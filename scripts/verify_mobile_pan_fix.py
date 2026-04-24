"""Mobile pan-fix verify. Desktop pan actief vs mobile pan-uit via coarse-pointer check."""

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

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # --- Desktop context: fine pointer, pan should be active ---
        print("\n--- desktop 1440x900 (fine pointer, pan expected active) ---")
        ctx_desktop = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = ctx_desktop.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_timeout(2500)

        matches_coarse = page.evaluate(
            "() => window.matchMedia('(pointer: coarse)').matches"
        )
        print(f"[desktop] matchMedia('(pointer: coarse)').matches = {matches_coarse}")

        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(800)
        transform_desktop_y0 = page.evaluate(
            """() => {
                const w = document.querySelector('.will-change-transform');
                return w ? window.getComputedStyle(w).transform : 'none';
            }"""
        )
        print(f"[desktop y=0] first-layer transform = {transform_desktop_y0}")

        out = OUT_DIR / "mobile-fix-desktop-y0.png"
        page.screenshot(path=str(out), full_page=False)
        ctx_desktop.close()

        # --- Mobile context: coarse pointer via hasTouch+isMobile, pan should be 0 ---
        print("\n--- mobile 390x844 (coarse pointer, pan expected 0) ---")
        ctx_mobile = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            has_touch=True,
            is_mobile=True,
        )
        page = ctx_mobile.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_timeout(2500)

        matches_coarse_mob = page.evaluate(
            "() => window.matchMedia('(pointer: coarse)').matches"
        )
        print(f"[mobile] matchMedia('(pointer: coarse)').matches = {matches_coarse_mob}")

        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(800)
        transform_mobile_y0 = page.evaluate(
            """() => {
                const w = document.querySelector('.will-change-transform');
                return w ? window.getComputedStyle(w).transform : 'none';
            }"""
        )
        print(f"[mobile y=0] first-layer transform = {transform_mobile_y0}")

        # Also scroll into Puna section to check its transform at mobile
        page.evaluate("window.scrollTo(0, 2000)")
        page.wait_for_timeout(1200)
        transforms_mobile_puna = page.evaluate(
            """() => {
                const ws = document.querySelectorAll('.will-change-transform');
                return Array.from(ws).map(w => window.getComputedStyle(w).transform);
            }"""
        )
        print(f"[mobile y=2000] all-layer transforms = {transforms_mobile_puna}")

        out_mob = OUT_DIR / "mobile-fix-mobile-y0.png"
        page.screenshot(path=str(out_mob), full_page=False)
        ctx_mobile.close()
        browser.close()

    print("\n--- summary ---")
    print(f"Desktop coarse: {matches_coarse} (expected False)")
    print(f"Desktop y=0 transform: {transform_desktop_y0} (expected non-identity, ~-86.4)")
    print(f"Mobile coarse: {matches_coarse_mob} (expected True)")
    print(f"Mobile y=0 transform: {transform_mobile_y0} (expected 'none' or identity)")
    print(f"Mobile y=2000 all transforms: {transforms_mobile_puna}")


if __name__ == "__main__":
    main()
