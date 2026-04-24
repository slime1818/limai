"""Pas 5 verify. Lenis active on desktop, not initialized on mobile (coarse pointer)."""

import urllib.request
from playwright.sync_api import sync_playwright


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def probe(ctx_opts, label: str):
            print(f"\n--- {label} ---")
            ctx = browser.new_context(**ctx_opts)
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("h1", state="visible", timeout=20000)
            page.wait_for_timeout(2500)

            probe = page.evaluate(
                """() => ({
                    coarse: window.matchMedia('(pointer: coarse)').matches,
                    lenisVersion: window.lenisVersion || null,
                    htmlClass: document.documentElement.className,
                    hasLenisClass: document.documentElement.classList.contains('lenis'),
                })"""
            )
            print(f"coarse: {probe['coarse']}")
            print(f"lenisVersion: {probe['lenisVersion']}")
            print(f"hasLenisClass: {probe['hasLenisClass']}")
            print(f"htmlClass: {probe['htmlClass']}")
            ctx.close()
            return probe

        desktop = probe(
            ctx_opts={"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
            label="DESKTOP 1440x900 (expect Lenis active)",
        )
        mobile = probe(
            ctx_opts={
                "viewport": {"width": 390, "height": 844},
                "device_scale_factor": 1,
                "has_touch": True,
                "is_mobile": True,
            },
            label="MOBILE 390x844 (expect Lenis NOT active)",
        )

        browser.close()

    print("\n--- summary ---")
    desktop_ok = desktop['lenisVersion'] is not None and desktop['hasLenisClass']
    mobile_ok = mobile['lenisVersion'] is None and not mobile['hasLenisClass']
    print(f"Desktop Lenis active: {desktop_ok}")
    print(f"Mobile Lenis inactive: {mobile_ok}")
    print(f"Overall: {'PASS' if desktop_ok and mobile_ok else 'FAIL'}")


if __name__ == "__main__":
    main()
