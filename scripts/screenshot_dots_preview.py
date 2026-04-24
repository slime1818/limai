"""Preview-task screenshots of /dots-preview route, Apu-active + cycled.

Assumes dev server running on localhost:3000.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2/research")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    req = urllib.request.Request("http://localhost:3000/dots-preview")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET /dots-preview -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        page.goto(
            "http://localhost:3000/dots-preview",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2500)

        # View 1: Apu-active comparison (top viewport)
        out1 = OUT_DIR / "dots-active-state-preview.png"
        page.screenshot(path=str(out1), full_page=False)
        print(f"[view-1 apu-active] {out1.name} ({out1.stat().st_size} bytes)")

        # Full page captures both sections for the cycled view without cutoff
        full = OUT_DIR / "dots-active-state-full.png"
        page.screenshot(path=str(full), full_page=True)
        print(f"[full-page] {full.name} ({full.stat().st_size} bytes)")

        browser.close()


if __name__ == "__main__":
    main()
