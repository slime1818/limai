"""Substep 9b verification. Altitude-pan in ImageStack per layer.

Six scroll-positioned screenshots: 4 Apu pan-progress + 2 Puna pan-progress.
Validates altitude-pan now runs on fixed-position ImageStack layers.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

POSITIONS = [
    ("apu-pan-progress-0", 0),
    ("apu-pan-progress-25", 450),
    ("apu-pan-progress-50", 900),
    ("apu-pan-progress-75", 1350),
    ("puna-pan-progress-0", 1800),
    ("puna-pan-progress-50", 2700),
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

        for label, y in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)

            # Measure active layer transform
            info = page.evaluate(
                """() => {
                    const panWrappers = document.querySelectorAll('.will-change-transform');
                    const results = [];
                    panWrappers.forEach((w, i) => {
                        const style = window.getComputedStyle(w);
                        const parent = w.parentElement;
                        const parentOpacity = parent ? window.getComputedStyle(parent).opacity : 'n/a';
                        results.push({
                            idx: i,
                            transform: style.transform,
                            parentOpacity: parentOpacity,
                        });
                    });
                    return results;
                }"""
            )
            out = OUT_DIR / f"substep-9b-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            visible_layers = [r for r in info if float(r['parentOpacity']) > 0.01]
            print(f"[{label} at y={y}] visible={len(visible_layers)} transforms={[l['transform'] for l in visible_layers]} -> {out.name} ({out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
