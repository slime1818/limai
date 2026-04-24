"""Verify section-height CSS-only conditional via pointer-coarse variant.

Desktop (fine pointer): h-[200dvh] = 2x viewport-height sections.
Mobile (coarse pointer): h-[100dvh] = 1x viewport-height sections.
"""

import urllib.request
from playwright.sync_api import sync_playwright


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def probe(ctx_opts, label: str, vh: int, expected_factor: int):
            print(f"\n--- {label} ---")
            ctx = browser.new_context(**ctx_opts)
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("h1", state="visible", timeout=20000)
            page.wait_for_timeout(2500)

            probe = page.evaluate(
                """() => {
                    const sections = Array.from(document.querySelectorAll('section'));
                    return {
                        coarse: window.matchMedia('(pointer: coarse)').matches,
                        viewH: window.innerHeight,
                        htmlH: document.documentElement.scrollHeight,
                        sectionCount: sections.length,
                        firstSectionH: sections[0] ? Math.round(sections[0].getBoundingClientRect().height) : null,
                    };
                }"""
            )
            expected_section_h = vh * expected_factor
            expected_total_h = expected_section_h * 6
            section_ok = probe['firstSectionH'] == expected_section_h
            total_ok = probe['htmlH'] == expected_total_h
            print(f"coarse: {probe['coarse']}")
            print(f"viewH: {probe['viewH']}")
            print(f"section[0] height: {probe['firstSectionH']} (expected {expected_section_h}) {'OK' if section_ok else 'FAIL'}")
            print(f"page total height: {probe['htmlH']} (expected {expected_total_h}) {'OK' if total_ok else 'FAIL'}")
            ctx.close()
            return section_ok and total_ok

        desktop_ok = probe(
            ctx_opts={"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
            label="DESKTOP 1440x900 (expect 200dvh sections = 1800px each)",
            vh=900,
            expected_factor=2,
        )
        mobile_ok = probe(
            ctx_opts={
                "viewport": {"width": 390, "height": 844},
                "device_scale_factor": 1,
                "has_touch": True,
                "is_mobile": True,
            },
            label="MOBILE 390x844 (expect 100dvh sections = 844px each)",
            vh=844,
            expected_factor=1,
        )

        browser.close()

    print(f"\nDesktop PASS={desktop_ok}, Mobile PASS={mobile_ok}")


if __name__ == "__main__":
    main()
