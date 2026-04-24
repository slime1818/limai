"""Substep 3 verification. Screenshot Apu hero + capture console logs.

Assumes dev server running on localhost:3000. Captures:
- HTTP status on /
- 1440x900 screenshot at docs/screenshots/fase-2/substep-3-post-lenis.png
- Any console messages to stdout (especially errors/warnings)
"""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path("docs/screenshots/fase-2")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    # HTTP prewarm
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    console_messages = []
    console_errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=1,
        )
        page = context.new_page()

        def on_console(msg):
            text = f"[{msg.type}] {msg.text}"
            console_messages.append(text)
            if msg.type in ("error", "warning"):
                console_errors.append(text)

        def on_pageerror(err):
            console_errors.append(f"[pageerror] {err}")

        page.on("console", on_console)
        page.on("pageerror", on_pageerror)

        page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector("h1", state="visible", timeout=20000)
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)",
            timeout=30000,
        )
        page.wait_for_timeout(2000)

        out = OUT_DIR / "substep-3-post-lenis.png"
        page.screenshot(path=str(out), full_page=False)
        print(f"[screenshot] 1440x900 -> {out} ({out.stat().st_size} bytes)")

        # Check for Lenis class on html
        lenis_class = page.evaluate("() => document.documentElement.className")
        print(f"[html className] {lenis_class}")

        # Check if window.lenis is set (Lenis v1 sets this global)
        lenis_version = page.evaluate("() => window.lenisVersion || 'not-set'")
        print(f"[lenisVersion] {lenis_version}")

        # Check for horizontal scroll
        has_h_scroll = page.evaluate(
            "() => document.documentElement.scrollWidth > document.documentElement.clientWidth"
        )
        print(f"[horizontal-scroll] {has_h_scroll}")

        # Check body + html heights
        dims = page.evaluate(
            "() => ({ htmlH: document.documentElement.scrollHeight, bodyH: document.body.scrollHeight, viewH: window.innerHeight })"
        )
        print(f"[dimensions] {dims}")

        browser.close()

    print(f"\n--- console messages ({len(console_messages)}) ---")
    for m in console_messages:
        print(m)

    print(f"\n--- console errors/warnings ({len(console_errors)}) ---")
    if console_errors:
        for m in console_errors:
            print(m)
    else:
        print("(none)")


if __name__ == "__main__":
    main()
