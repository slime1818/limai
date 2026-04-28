"""Capture Puna pass 2.1 productie-staat: VP1 (Olivier B natural) en VP2 (Abdul).

Loopt tegen een lopende Next.js dev-server op localhost:3000 en schrijft naar
docs/screenshots/fase-2/.
"""

import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORT_W, VIEWPORT_H = 1440, 900


def prewarm(timeout: float = 120.0) -> None:
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        resp.read()
        print(f"[prewarm] HTTP {resp.status} on /")


def capture_puna() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
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

        # VP1: scrollIntoView op #puna start.
        page.evaluate(
            "document.getElementById('puna').scrollIntoView({behavior: 'instant', block: 'start'});"
        )
        page.wait_for_timeout(800)
        out_vp1 = OUT_DIR / "puna-vp1-olivier-pass2-1.png"
        page.screenshot(path=str(out_vp1), full_page=False)
        print(f"[VP1] {VIEWPORT_W}x{VIEWPORT_H} -> {out_vp1} ({out_vp1.stat().st_size} bytes)")

        # VP2: een viewport verder.
        page.evaluate("window.scrollBy(0, window.innerHeight);")
        page.wait_for_timeout(800)
        out_vp2 = OUT_DIR / "puna-vp2-abdul-pass2-1.png"
        page.screenshot(path=str(out_vp2), full_page=False)
        print(f"[VP2] {VIEWPORT_W}x{VIEWPORT_H} -> {out_vp2} ({out_vp2.stat().st_size} bytes)")

        browser.close()


if __name__ == "__main__":
    prewarm()
    capture_puna()
