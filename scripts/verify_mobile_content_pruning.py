"""Mobile content-pruning verify. Count h1s in DOM per scroll-step on mobile + desktop."""

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

        def run_scroll_test(ctx_opts, label: str, expected_h1_min: int, expected_h1_max: int, viewport_height: int, total_height: int):
            print(f"\n--- {label} ---")
            ctx = browser.new_context(**ctx_opts)
            page = ctx.new_page()
            page.goto("http://localhost:3000/", wait_until="domcontentloaded", timeout=60000)
            page.wait_for_selector("h1", state="visible", timeout=20000)
            page.wait_for_timeout(2500)

            max_scroll = total_height - viewport_height
            counts: list[tuple[int, int, list[str]]] = []
            for y in range(0, max_scroll + 1, 300):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(150)
                result = page.evaluate(
                    """() => {
                        const h1s = Array.from(document.querySelectorAll('section h1'));
                        return { count: h1s.length, titles: h1s.map(h => h.textContent) };
                    }"""
                )
                counts.append((y, result['count'], result['titles']))

            max_h1 = max(c[1] for c in counts)
            min_h1 = min(c[1] for c in counts)
            avg_h1 = sum(c[1] for c in counts) / len(counts)
            within = expected_h1_min <= min_h1 and max_h1 <= expected_h1_max

            print(f"steps={len(counts)} h1s: min={min_h1} max={max_h1} avg={avg_h1:.2f}")
            print(f"expected: {expected_h1_min} to {expected_h1_max} -> {'PASS' if within else 'FAIL'}")

            # Distribution
            from collections import Counter
            dist = Counter(c[1] for c in counts)
            print(f"distribution: {dict(sorted(dist.items()))}")

            # Spot-check which title is rendered at key positions
            for y, count, titles in counts[:5] + counts[-3:]:
                print(f"  y={y:<5} count={count} titles={titles}")

            ctx.close()
            return within, min_h1, max_h1, avg_h1

        # Desktop: 1440x900, expect 6 h1s always
        desktop_total = 6 * 1800
        d_ok, *_ = run_scroll_test(
            ctx_opts={"viewport": {"width": 1440, "height": 900}, "device_scale_factor": 1},
            label="DESKTOP 1440x900",
            expected_h1_min=6,
            expected_h1_max=6,
            viewport_height=900,
            total_height=desktop_total,
        )

        # Mobile: 390x844, expect 1 h1 always (active biome only)
        mobile_total = 6 * 1688
        m_ok, *_ = run_scroll_test(
            ctx_opts={
                "viewport": {"width": 390, "height": 844},
                "device_scale_factor": 1,
                "has_touch": True,
                "is_mobile": True,
            },
            label="MOBILE 390x844 (coarse pointer)",
            expected_h1_min=1,
            expected_h1_max=1,
            viewport_height=844,
            total_height=mobile_total,
        )

        browser.close()

    print(f"\nDesktop PASS={d_ok}, Mobile PASS={m_ok}")


if __name__ == "__main__":
    main()
