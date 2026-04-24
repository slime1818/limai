"""Substep 6 verification. 2-viewport BiomeSection with sticky image pinning.

Four scroll-positioned screenshots: Apu v1, Apu v2, Puna v1, Puna v2.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("apu-section-v1", 0),
    ("apu-section-v2", 900),
    ("puna-section-v1", 1800),
    ("puna-section-v2", 2700),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        def on_console(msg):
            if msg.type in ("error", "warning"):
                console_errors.append(f"[{msg.type}] {msg.text}")

        page.on("console", on_console)
        page.on("pageerror", lambda err: console_errors.append(f"[pageerror] {err}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        dims = page.evaluate(
            "() => ({ htmlH: document.documentElement.scrollHeight, viewH: window.innerHeight, sections: document.querySelectorAll('section').length })"
        )
        print(f"[dimensions] {dims}")

        # Scroll incrementally through the page to trigger lazy loads up to Puna viewport 2
        for y in range(0, 3000, 500):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(400)
        page.wait_for_function(
            "() => { const imgs = Array.from(document.images).slice(0, 2); return imgs.every(i => i.complete && i.naturalWidth > 0); }",
            timeout=30000,
        )
        page.wait_for_timeout(1500)

        for label, y in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1000)
            out = OUT_DIR / f"substep-6-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            print(f"[{label} at y={y}] {out.name} ({out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
