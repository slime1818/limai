"""Mobile visibility-pruning verify. Count visible layers per scroll-step on mobile + desktop."""

import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    req = urllib.request.Request("http://localhost:3000/")
    with urllib.request.urlopen(req, timeout=180) as resp:
        print(f"[http] GET / -> {resp.status}")
        resp.read()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def run_scroll_test(ctx_opts, label: str, expected_min_visible: int, expected_max_visible: int, viewport_height: int, total_height: int):
            print(f"\n--- {label} ---")
            ctx = browser.new_context(**ctx_opts)
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("h1", state="visible", timeout=20000)
            page.wait_for_timeout(2500)

            # Scroll the entire page in 300px steps, primes lazy-load and exercises opacity math
            max_scroll = total_height - viewport_height
            counts = []
            for y in range(0, max_scroll + 1, 300):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(120)  # allow opacity motion-value event to fire + setState
                visible = page.evaluate(
                    """() => {
                        const layers = document.querySelectorAll('.fixed.inset-0 > .absolute.inset-0');
                        return Array.from(layers).filter(l => window.getComputedStyle(l).visibility === 'visible').length;
                    }"""
                )
                counts.append((y, visible))

            max_vis = max(c[1] for c in counts)
            min_vis = min(c[1] for c in counts)
            avg_vis = sum(c[1] for c in counts) / len(counts)
            within = expected_min_visible <= min_vis and max_vis <= expected_max_visible

            print(f"steps={len(counts)} visible: min={min_vis} max={max_vis} avg={avg_vis:.2f}")
            print(f"expected: min >= {expected_min_visible}, max <= {expected_max_visible} -> {'PASS' if within else 'FAIL'}")
            # Print distribution
            from collections import Counter
            dist = Counter(c[1] for c in counts)
            print(f"distribution: {dict(sorted(dist.items()))}")

            ctx.close()
            return within, min_vis, max_vis, avg_vis

        # Desktop test: 1440x900, expect all 6 always visible
        desktop_total = 6 * 1800  # section-height on 900 viewport
        d_ok, d_min, d_max, d_avg = run_scroll_test(
            ctx_opts={"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
            label="DESKTOP 1440x900",
            expected_min_visible=6,
            expected_max_visible=6,
            viewport_height=900,
            total_height=desktop_total,
        )

        # Mobile test: 390x844, expect 1-2 visible
        mobile_total = 6 * 1688  # section-height on 844 viewport (200dvh)
        m_ok, m_min, m_max, m_avg = run_scroll_test(
            ctx_opts={
                "viewport": {"width": 390, "height": 844},
                "device_scale_factor": 1,
                "has_touch": True,
                "is_mobile": True,
            },
            label="MOBILE 390x844 (coarse pointer)",
            expected_min_visible=1,
            expected_max_visible=2,
            viewport_height=844,
            total_height=mobile_total,
        )

        browser.close()

    print("\n--- summary ---")
    print(f"Desktop: min={d_min} max={d_max} avg={d_avg:.2f} PASS={d_ok}")
    print(f"Mobile:  min={m_min} max={m_max} avg={m_avg:.2f} PASS={m_ok}")
    if m_max <= 2 and d_max == 6 and d_min == 6:
        print("\nCompositing-reductie bevestigd: mobile max 2 layers, desktop 6 layers altijd visible.")


if __name__ == "__main__":
    main()
