"""Substep 9a verification. Architectural refactor, ImageStack fixed-position layers.

Regression check: all 6 biomes render at their section-start with correct content + image.
Altitude-pan is intentionally off in 9a (returns in 9b).
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("apu", 0),
    ("puna", 1800),
    ("yungas", 3600),
    ("selva", 5400),
    ("paracas", 7200),
    ("pacifico", 9000),
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
        page.wait_for_timeout(2500)

        # Structure probe
        probe = page.evaluate(
            """() => ({
                sections: document.querySelectorAll('section').length,
                fixedStackChildren: document.querySelectorAll('.fixed.inset-0.pointer-events-none').length,
                imgCountInitial: document.images.length,
                htmlH: document.documentElement.scrollHeight,
                viewH: window.innerHeight,
            })"""
        )
        print(f"[structure probe] {probe}")

        for label, y in POSITIONS:
            # Scroll incrementally to progressively trigger useInView gates
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)
            # Ensure target-biome image has decoded
            page.wait_for_function(
                """() => {
                    const imgs = Array.from(document.images);
                    return imgs.length > 0 && imgs.every(i => !i.complete || i.naturalWidth > 0);
                }""",
                timeout=30000,
            )
            page.wait_for_timeout(800)

            img_count = page.evaluate("() => document.images.length")
            out = OUT_DIR / f"substep-9a-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            print(f"[{label} at y={y}] imgs={img_count} -> {out.name} ({out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
