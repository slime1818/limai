"""Find the best text-landing zone in the Apu composite.

Scans the composite with a sliding window, computes worst-case contrast
(using 95th-percentile brightness in each window as the "worst light pixel"),
and reports candidate zones ranked by body/display PASS.

Saves a heatmap PNG showing contrast quality across the canvas so we can see
visually where text can land.
"""
from pathlib import Path
from PIL import Image
import numpy as np

COMPOSITE_PATH = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\processed\apu-composite-alt.webp")
HEATMAP_PATH = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\processed\contrast-heatmap.png")
TEXT_COLOR = np.array([0xF4, 0xEC, 0xD9], dtype=np.float64)


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    lin = srgb_to_linear(rgb.astype(np.float64))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast_vs_text(l_bg):
    text_l = 0.8423
    return np.where(l_bg > text_l,
                    (l_bg + 0.05) / (text_l + 0.05),
                    (text_l + 0.05) / (l_bg + 0.05))


def score_zone(arr, x1, y1, x2, y2):
    region = arr[y1:y2, x1:x2, :3]
    alpha = arr[y1:y2, x1:x2, 3]
    mask = alpha > 240
    if not mask.any():
        return None
    lum = relative_luminance(region)
    lum_opaque = lum[mask]
    p50 = float(np.percentile(lum_opaque, 50))
    p95 = float(np.percentile(lum_opaque, 95))
    p100 = float(np.percentile(lum_opaque, 100))
    worst_ratio = float(contrast_vs_text(np.array([p95]))[0])
    absolute_worst = float(contrast_vs_text(np.array([p100]))[0])
    return {
        "zone": (x1, y1, x2, y2),
        "median_lum": p50,
        "p95_lum": p95,
        "max_lum": p100,
        "worst_ratio_p95": worst_ratio,
        "worst_ratio_absolute": absolute_worst,
    }


def main():
    img = Image.open(COMPOSITE_PATH).convert("RGBA")
    arr = np.array(img)
    h, w = arr.shape[:2]

    # Named candidate zones to evaluate (x1, y1, x2, y2)
    candidates = {
        "Center-left (original)": (250, 280, 700, 530),
        "Lower center-left (mountain base)": (220, 440, 650, 620),
        "Upper center-left (near peak)": (250, 200, 700, 400),
        "Left band (shadow side)": (230, 250, 480, 600),
        "Mid-right (alternative)": (500, 280, 900, 530),
        "Plateau (bottom strip)": (240, 600, 800, 700),
    }

    print(f"Composite: {COMPOSITE_PATH.name} ({w}x{h})")
    print(f"Text color: #f4ecd9 (luminance 0.8423)")
    print(f"Body AA threshold: 4.5:1  |  Display AA threshold: 3:1")
    print()
    print(f"{'Zone':<42} {'median':>8} {'p95':>8} {'max':>8} {'p95 contrast':>14} {'verdict':>10}")
    print("-" * 96)
    scored = []
    for name, (x1, y1, x2, y2) in candidates.items():
        s = score_zone(arr, x1, y1, x2, y2)
        if s is None:
            continue
        if s["worst_ratio_p95"] >= 4.5:
            verdict = "BODY PASS"
        elif s["worst_ratio_p95"] >= 3.0:
            verdict = "DISP ONLY"
        else:
            verdict = "FAIL"
        print(f"{name:<42} {s['median_lum']:>8.4f} {s['p95_lum']:>8.4f} {s['max_lum']:>8.4f} "
              f"{s['worst_ratio_p95']:>14.2f} {verdict:>10}")
        scored.append((name, s, verdict))

    # Heatmap: per-pixel luminance colored by contrast tier
    print("\nGenerating per-pixel contrast heatmap...")
    rgb_arr = arr[..., :3].astype(np.float64)
    lum = relative_luminance(rgb_arr)
    cr = contrast_vs_text(lum)

    # Red = fail (<3), Orange = display-only (3-4.5), Green = body pass (>4.5)
    heatmap = np.zeros((h, w, 3), dtype=np.uint8)
    heatmap[cr < 3.0] = [180, 40, 40]
    heatmap[(cr >= 3.0) & (cr < 4.5)] = [220, 150, 40]
    heatmap[cr >= 4.5] = [70, 170, 70]
    # Blend with 35% opacity over original so we can see what's underneath
    blended = (0.35 * heatmap + 0.65 * rgb_arr).astype(np.uint8)
    Image.fromarray(blended).save(HEATMAP_PATH, "PNG")
    print(f"Saved heatmap: {HEATMAP_PATH.name}")
    print("Legend: green=body PASS (>=4.5:1) | orange=display-only (3-4.5) | red=FAIL (<3)")


if __name__ == "__main__":
    main()
