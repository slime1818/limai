"""Substep 5 verification. Dots desktop + mobile hidden + per-biome readability.

Assumes dev server running on localhost:3000.
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# biome scrollY positions (biome-top). Each biome section is 1080px tall at 1440 viewport.
BIOME_SCROLLS = [
    ("apu", 0),
    ("puna", 1080),
    ("yungas", 2160),
    ("selva", 3240),
    ("paracas", 4320),
    ("pacifico", 5400),
]


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_errors: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Desktop
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.on("console", lambda m: console_errors.append(f"[{m.type}] {m.text}") if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: console_errors.append(f"[pageerror] {e}"))

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        # Check dots container exists and is visible on desktop
        dots_info = page.evaluate(
            """() => {
                const dots = document.querySelectorAll('[aria-hidden="true"].fixed div.rounded-full');
                const container = dots.length > 0 ? dots[0].parentElement : null;
                if (!container) return { found: false };
                const style = window.getComputedStyle(container);
                const rect = container.getBoundingClientRect();
                return {
                    found: true,
                    count: dots.length,
                    display: style.display,
                    position: style.position,
                    top: rect.top,
                    right: window.innerWidth - rect.right,
                    visible: rect.width > 0 && rect.height > 0,
                };
            }"""
        )
        print(f"[desktop dots] {dots_info}")

        # Per-biome readability: scroll incrementally (also triggers lazy-load) and screenshot
        for biome_id, y in BIOME_SCROLLS:
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(600)
            # Ensure current-biome image is loaded
            page.wait_for_function(
                "() => { const imgs = Array.from(document.images); return imgs.every(i => !i.getBoundingClientRect().top || Math.abs(i.getBoundingClientRect().top) > 2000 || (i.complete && i.naturalWidth > 0)); }",
                timeout=30000,
            )
            page.wait_for_timeout(800)
            out = OUT_DIR / f"substep-5-dots-at-{biome_id}.png"
            page.screenshot(path=str(out), full_page=False)
            print(f"[{biome_id} at y={y}] {out.name} ({out.stat().st_size} bytes)")

        # The Apu-top screenshot is also the spec'd "desktop" screenshot, save a copy with spec filename
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)
        desktop_out = OUT_DIR / "substep-5-dots-desktop.png"
        page.screenshot(path=str(desktop_out), full_page=False)
        print(f"[desktop-spec] {desktop_out.name} ({desktop_out.stat().st_size} bytes)")

        context.close()

        # Mobile
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=1,
        )
        page = context.new_page()
        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "() => { const imgs = document.images; return imgs.length > 0 && imgs[0].complete && imgs[0].naturalWidth > 0; }",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        mobile_info = page.evaluate(
            """() => {
                const dots = document.querySelectorAll('[aria-hidden="true"].fixed div.rounded-full');
                const container = dots.length > 0 ? dots[0].parentElement : null;
                if (!container) return { found: false };
                const style = window.getComputedStyle(container);
                const rect = container.getBoundingClientRect();
                return {
                    found: true,
                    count: dots.length,
                    display: style.display,
                    hidden: style.display === 'none' || rect.width === 0,
                };
            }"""
        )
        print(f"[mobile dots] {mobile_info}")

        mobile_out = OUT_DIR / "substep-5-dots-mobile.png"
        page.screenshot(path=str(mobile_out), full_page=False)
        print(f"[mobile-spec] {mobile_out.name} ({mobile_out.stat().st_size} bytes)")

        browser.close()

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
