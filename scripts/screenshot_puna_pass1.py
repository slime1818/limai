"""Capture Puna desktop pass 1 screenshots: VP1 (Olivier) and VP2 (Abdul).

Runs against an already-running Next.js dev server on localhost:3000. Writes
PNGs to docs/screenshots/fase-2/.
"""

import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture_puna(width: int, height: int) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=2,
        )
        page = context.new_page()
        page.goto(
            "http://localhost:3000/",
            wait_until="domcontentloaded",
            timeout=60000,
        )
        page.wait_for_selector("h1", state="visible", timeout=15000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(1500)

        # VP1: jump to top of #puna section.
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
        )
        page.wait_for_timeout(800)
        out_vp1 = OUT_DIR / "puna-vp1-olivier-desktop.png"
        page.screenshot(path=str(out_vp1), full_page=False)
        print(f"[VP1] {width}x{height} -> {out_vp1} ({out_vp1.stat().st_size} bytes)")

        # VP2: scroll one viewport further (Puna section is h-[200vh], so VP2
        # starts at section-top + viewport-height).
        page.evaluate(
            "window.scrollBy(0, window.innerHeight);"
        )
        page.wait_for_timeout(800)
        out_vp2 = OUT_DIR / "puna-vp2-abdul-desktop.png"
        page.screenshot(path=str(out_vp2), full_page=False)
        print(f"[VP2] {width}x{height} -> {out_vp2} ({out_vp2.stat().st_size} bytes)")

        # Bonus: capture the seam between VP1 and VP2 to verify scrim continuity.
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
            "window.scrollBy(0, window.innerHeight / 2);"
        )
        page.wait_for_timeout(800)
        out_seam = OUT_DIR / "puna-seam-desktop.png"
        page.screenshot(path=str(out_seam), full_page=False)
        print(f"[seam] {width}x{height} -> {out_seam} ({out_seam.stat().st_size} bytes)")

        browser.close()


if __name__ == "__main__":
    prewarm()
    capture_puna(1440, 900)
