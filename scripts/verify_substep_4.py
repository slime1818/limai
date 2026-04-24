"""Substep 4 verification. Apu regression + full 6-biome stacked screenshot.

Assumes dev server running on localhost:3000.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_messages: list[str] = []
    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        def on_console(msg):
            text = f"[{msg.type}] {msg.text}"
            console_messages.append(text)
            if msg.type in ("error", "warning"):
                console_errors.append(text)

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)

        # Wait for the first image (Apu, priority=true) to be loaded
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        apu_out = OUT_DIR / "substep-4-apu-regression.png"
        page.screenshot(path=str(apu_out), full_page=False)
        print(f"[apu-regression] {apu_out} ({apu_out.stat().st_size} bytes)")

        h1_count = page.evaluate("() => document.querySelectorAll('h1').length")
        h1_texts = page.evaluate(
            "() => Array.from(document.querySelectorAll('h1')).map(h => h.textContent)"
        )
        img_count = page.evaluate("() => document.querySelectorAll('img').length")
        anchor_count = page.evaluate(
            "() => document.querySelectorAll('section a[href]').length"
        )
        dims = page.evaluate(
            "() => ({ htmlH: document.documentElement.scrollHeight, viewH: window.innerHeight })"
        )
        print(f"[h1 count] {h1_count}")
        print(f"[h1 texts] {h1_texts}")
        print(f"[img count] {img_count}")
        print(f"[anchor count] {anchor_count}")
        print(f"[dimensions] {dims}")

        # Scroll incrementally to trigger lazy-load of biomes 2-6
        total_h = dims["htmlH"]
        step = 800
        y = 0
        while y < total_h:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(400)
            y += step
        page.evaluate("() => window.scrollTo(0, document.documentElement.scrollHeight)")
        page.wait_for_timeout(1000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=60000,
        )
        page.wait_for_timeout(1500)
        page.evaluate("() => window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)

        stacked_out = OUT_DIR / "substep-4-stacked.png"
        page.screenshot(path=str(stacked_out), full_page=True)
        print(f"[stacked-full-page] {stacked_out} ({stacked_out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
