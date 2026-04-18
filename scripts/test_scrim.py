"""Test: add a scrim behind the text zone + re-check Gate 8 contrast.

Builds a vertical linear-gradient scrim (dark, feathered top/bottom) over
the text zone in variant B, composites it above the painting layers,
and re-runs the WCAG worst-case-pixel check.

Tests 3 scrim opacities (40, 55, 70%) and saves each as a separate composite
so user can visually compare aesthetic vs contrast trade-off.
"""
from pathlib import Path
from PIL import Image
import numpy as np

OUT_DIR = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\processed")
COMPOSITE_IN = OUT_DIR / "apu-composite-alt.webp"

TEXT_COLOR_LUM = 0.8423  # #f4ecd9
TEXT_ZONE = (250, 280, 700, 530)

# Scrim shape (vertical band): transparent at top, peak in middle, transparent at bottom
SCRIM_TOP = 230        # scrim starts fading in here
SCRIM_PEAK_TOP = 290   # max opacity starts
SCRIM_PEAK_BOT = 520   # max opacity ends
SCRIM_BOT = 580        # scrim fully transparent here
SCRIM_COLOR = (26, 22, 18)  # Noche Andina

# Also fade horizontally at left/right so the scrim doesn't look like a rectangle
SCRIM_LEFT = 130
SCRIM_LEFT_PEAK = 210
SCRIM_RIGHT_PEAK = 760
SCRIM_RIGHT = 870


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    lin = srgb_to_linear(rgb.astype(np.float64))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast_vs_text(lum):
    return np.where(lum > TEXT_COLOR_LUM,
                    (lum + 0.05) / (TEXT_COLOR_LUM + 0.05),
                    (TEXT_COLOR_LUM + 0.05) / (lum + 0.05))


def make_scrim(w, h, max_opacity):
    """Linear gradient scrim with feathered top/bottom/left/right."""
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    arr[..., 0] = SCRIM_COLOR[0]
    arr[..., 1] = SCRIM_COLOR[1]
    arr[..., 2] = SCRIM_COLOR[2]

    # Vertical opacity falloff
    y_alpha = np.zeros(h, dtype=np.float64)
    for y in range(h):
        if y < SCRIM_TOP or y > SCRIM_BOT:
            y_alpha[y] = 0
        elif y < SCRIM_PEAK_TOP:
            y_alpha[y] = (y - SCRIM_TOP) / (SCRIM_PEAK_TOP - SCRIM_TOP)
        elif y <= SCRIM_PEAK_BOT:
            y_alpha[y] = 1.0
        else:
            y_alpha[y] = (SCRIM_BOT - y) / (SCRIM_BOT - SCRIM_PEAK_BOT)

    # Horizontal opacity falloff
    x_alpha = np.zeros(w, dtype=np.float64)
    for x in range(w):
        if x < SCRIM_LEFT or x > SCRIM_RIGHT:
            x_alpha[x] = 0
        elif x < SCRIM_LEFT_PEAK:
            x_alpha[x] = (x - SCRIM_LEFT) / (SCRIM_LEFT_PEAK - SCRIM_LEFT)
        elif x <= SCRIM_RIGHT_PEAK:
            x_alpha[x] = 1.0
        else:
            x_alpha[x] = (SCRIM_RIGHT - x) / (SCRIM_RIGHT - SCRIM_RIGHT_PEAK)

    # Combine: final alpha = y_alpha * x_alpha * max_opacity
    combined = np.outer(y_alpha, x_alpha) * max_opacity
    arr[..., 3] = (combined * 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGBA")


def analyze_zone(arr):
    """Return worst-case contrast ratio across opaque pixels in TEXT_ZONE."""
    x1, y1, x2, y2 = TEXT_ZONE
    region = arr[y1:y2, x1:x2, :3]
    alpha = arr[y1:y2, x1:x2, 3]
    mask = alpha > 240
    lum = relative_luminance(region)
    lum_opaque = lum[mask]
    p95 = float(np.percentile(lum_opaque, 95))
    p100 = float(np.percentile(lum_opaque, 100))
    return {
        "p95_lum": p95,
        "max_lum": p100,
        "p95_contrast": float(contrast_vs_text(np.array([p95]))[0]),
        "max_contrast": float(contrast_vs_text(np.array([p100]))[0]),
    }


def main():
    base = Image.open(COMPOSITE_IN).convert("RGBA")
    w, h = base.size

    print(f"Base composite: {COMPOSITE_IN.name} ({w}x{h})")
    print(f"Text zone: {TEXT_ZONE}")
    print(f"Scrim: linear vertical gradient, feathered, color rgb{SCRIM_COLOR}")
    print()

    base_arr = np.array(base)
    pre = analyze_zone(base_arr)
    print(f"BEFORE scrim:")
    print(f"  p95 luminance {pre['p95_lum']:.4f}, max {pre['max_lum']:.4f}")
    print(f"  p95 contrast  {pre['p95_contrast']:.2f}:1, worst {pre['max_contrast']:.2f}:1")
    print()

    print(f"{'Scrim opacity':>15} {'p95 lum':>10} {'max lum':>10} {'p95 ctr':>10} {'worst ctr':>10} {'body(4.5)':>10} {'disp(3.0)':>10}")
    print("-" * 90)
    for opacity in [0.40, 0.55, 0.70, 0.85]:
        scrim = make_scrim(w, h, opacity)
        result = Image.alpha_composite(base, scrim)
        result_arr = np.array(result)
        stats = analyze_zone(result_arr)
        body_verdict = "PASS" if stats["p95_contrast"] >= 4.5 else "FAIL"
        disp_verdict = "PASS" if stats["p95_contrast"] >= 3.0 else "FAIL"
        print(f"{opacity*100:>13.0f}% "
              f"{stats['p95_lum']:>10.4f} "
              f"{stats['max_lum']:>10.4f} "
              f"{stats['p95_contrast']:>10.2f} "
              f"{stats['max_contrast']:>10.2f} "
              f"{body_verdict:>10} {disp_verdict:>10}")

        out_path = OUT_DIR / f"apu-composite-scrim-{int(opacity*100)}.webp"
        result.save(out_path, "WebP", quality=90, method=6)


if __name__ == "__main__":
    main()
