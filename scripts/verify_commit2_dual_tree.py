"""Verify dual-tree content layout: desktop sees 2-viewport tree, mobile sees single-viewport tree."""

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

        # Desktop: expect desktop-tree visible, mobile-tree hidden
        print("\n--- DESKTOP 1440x900 ---")
        ctx = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = ctx.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("section", timeout=20000)
        page.wait_for_timeout(2500)

        trees = page.evaluate(
            """() => {
                const desktops = Array.from(document.querySelectorAll('.hidden.pointer-fine\\\\:block'));
                const mobiles = Array.from(document.querySelectorAll('.pointer-fine\\\\:hidden'));
                return {
                    desktop_tree_count: desktops.length,
                    desktop_visible: desktops.filter(d => window.getComputedStyle(d).display !== 'none').length,
                    mobile_tree_count: mobiles.length,
                    mobile_visible: mobiles.filter(m => window.getComputedStyle(m).display !== 'none').length,
                };
            }"""
        )
        print(f"trees: {trees}")

        page.screenshot(path=str(OUT_DIR / "commit2-desktop-apu.png"), full_page=False)
        page.evaluate("window.scrollTo(0, 900)")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT_DIR / "commit2-desktop-apu-v2.png"), full_page=False)
        ctx.close()

        # Mobile: expect mobile-tree visible, desktop-tree hidden
        print("\n--- MOBILE 390x844 (coarse pointer) ---")
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
            has_touch=True,
            is_mobile=True,
        )
        page = ctx.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("section", timeout=20000)
        page.wait_for_timeout(2500)

        trees = page.evaluate(
            """() => {
                const desktops = Array.from(document.querySelectorAll('.hidden.pointer-fine\\\\:block'));
                const mobiles = Array.from(document.querySelectorAll('.pointer-fine\\\\:hidden'));
                return {
                    desktop_tree_count: desktops.length,
                    desktop_visible: desktops.filter(d => window.getComputedStyle(d).display !== 'none').length,
                    mobile_tree_count: mobiles.length,
                    mobile_visible: mobiles.filter(m => window.getComputedStyle(m).display !== 'none').length,
                };
            }"""
        )
        print(f"trees: {trees}")

        # Screenshot Apu (null teaser/CTA - should show only hero block)
        page.screenshot(path=str(OUT_DIR / "commit2-mobile-apu.png"), full_page=False)

        # Scroll to Puna section (has teaser + CTA)
        page.evaluate("window.scrollTo(0, 844)")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT_DIR / "commit2-mobile-puna.png"), full_page=False)

        # Scroll to Pacifico (last biome, has teaser + CTA)
        page.evaluate("window.scrollTo(0, 844 * 5)")
        page.wait_for_timeout(800)
        page.screenshot(path=str(OUT_DIR / "commit2-mobile-pacifico.png"), full_page=False)

        ctx.close()
        browser.close()


if __name__ == "__main__":
    main()
