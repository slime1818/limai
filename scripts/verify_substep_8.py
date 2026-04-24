"""Substep 8 verification. Altitude-pan screenshots across Apu section scroll range.

Four positions y=0, 450, 900, 1350 to capture translateY progress from -8% to +8%.
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

        # Verify prefers-reduced-motion not active (default)
        prefers = page.evaluate(
            "() => window.matchMedia('(prefers-reduced-motion: reduce)').matches"
        )
        print(f"[prefers-reduced-motion] {prefers}")

        # Verify motion.div is in DOM (uses will-change-transform)
        motion_check = page.evaluate(
            """() => {
                const section = document.querySelector('section');
                if (!section) return { found: false };
                const motionDiv = section.querySelector('.will-change-transform');
                if (!motionDiv) return { found: false };
                const style = window.getComputedStyle(motionDiv);
                return {
                    found: true,
                    transform: style.transform,
                    willChange: style.willChange,
                    top: style.top,
                    bottom: style.bottom,
                };
            }"""
        )
        print(f"[motion element] {motion_check}")

        # Scroll container style probe (for motion warning diagnosis)
        scroll_probe = page.evaluate(
            """() => {
                const html = document.documentElement;
                const body = document.body;
                return {
                    html_position: window.getComputedStyle(html).position,
                    body_position: window.getComputedStyle(body).position,
                    scrolling_element_tag: document.scrollingElement ? document.scrollingElement.tagName : 'none',
                };
            }"""
        )
        print(f"[scroll root probe] {scroll_probe}")

        for label, y in POSITIONS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(1500)
            # Capture transform at this scroll position
            transform = page.evaluate(
                """() => {
                    const motionDiv = document.querySelector('section .will-change-transform');
                    return motionDiv ? window.getComputedStyle(motionDiv).transform : 'none';
                }"""
            )
            out = OUT_DIR / f"substep-8-{label}.png"
            page.screenshot(path=str(out), full_page=False)
            print(f"[{label} at y={y}] transform={transform} -> {out.name} ({out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
