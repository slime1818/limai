"""WCAG AA contrast check on Apu composite variant B.

Samples the text-landing zone (center-left mountain face where Fraunces
"Apu" display and Satoshi manifesto land). Reports darkest + lightest
pixel, contrast ratio against text color #f4ecd9, and pass/fail for
body (4.5:1) and display (3:1) thresholds.
"""
from pathlib import Path
from PIL import Image
import numpy as np

COMPOSITE_PATH = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\processed\apu-composite-alt.webp")
TEXT_COLOR = np.array([0xF4, 0xEC, 0xD9], dtype=np.float64)  # #f4ecd9

# Text-landing zone coordinates on 1024x768 canvas
# Approx where the Fraunces "Apu" display + Satoshi manifesto block falls in variant B,
# BEYOND the rock framing (~x=210) and ABOVE the plateau band (~y=538)
TEXT_ZONE = (250, 280, 700, 530)  # x1, y1, x2, y2


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb: np.ndarray) -> np.ndarray:
    """Compute WCAG relative luminance. rgb is array of shape (..., 3)."""
    lin = srgb_to_linear(rgb.astype(np.float64))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast_ratio(l1: float, l2: float) -> float:
    light = max(l1, l2)
    dark = min(l1, l2)
    return (light + 0.05) / (dark + 0.05)


def hex_of(px: np.ndarray) -> str:
    r, g, b = int(px[0]), int(px[1]), int(px[2])
    return f"#{r:02x}{g:02x}{b:02x}"


def main():
    img = Image.open(COMPOSITE_PATH).convert("RGBA")
    arr = np.array(img)

    x1, y1, x2, y2 = TEXT_ZONE
    region_rgb = arr[y1:y2, x1:x2, :3]
    region_alpha = arr[y1:y2, x1:x2, 3]

    # Consider only fully opaque pixels (the composite is mostly opaque, but be safe)
    mask = region_alpha > 240
    if not mask.any():
        print("No opaque pixels in text zone — something is wrong with composite or coords.")
        return

    # Luminance map
    lum = relative_luminance(region_rgb)

    # Find darkest and lightest opaque pixel
    lum_masked_for_min = np.where(mask, lum, np.inf)
    lum_masked_for_max = np.where(mask, lum, -np.inf)
    min_idx = np.unravel_index(np.argmin(lum_masked_for_min), lum.shape)
    max_idx = np.unravel_index(np.argmax(lum_masked_for_max), lum.shape)

    darkest_px = region_rgb[min_idx]
    lightest_px = region_rgb[max_idx]
    darkest_lum = float(lum[min_idx])
    lightest_lum = float(lum[max_idx])

    text_lum = float(relative_luminance(TEXT_COLOR.reshape(1, 3))[0])

    ratio_dark = contrast_ratio(text_lum, darkest_lum)
    ratio_light = contrast_ratio(text_lum, lightest_lum)

    print(f"Composite: {COMPOSITE_PATH.name}")
    print(f"Text color: #f4ecd9 (luminance {text_lum:.4f})")
    print(f"Text zone: x=[{x1},{x2}) y=[{y1},{y2}) on 1024x768 canvas")
    print(f"  zone size: {x2-x1}x{y2-y1} = {(x2-x1)*(y2-y1):,} px")
    print(f"  opaque px: {int(mask.sum()):,} / {int(mask.size):,}")
    print()
    print("=== Pixel-level contrast analysis ===")
    print(f"Darkest opaque pixel:  {hex_of(darkest_px)}  RGB{tuple(int(v) for v in darkest_px)}  luminance={darkest_lum:.4f}")
    print(f"  position in canvas:  ({x1 + min_idx[1]}, {y1 + min_idx[0]})")
    print(f"  contrast vs text:    {ratio_dark:.2f}:1")
    print()
    print(f"Lightest opaque pixel: {hex_of(lightest_px)}  RGB{tuple(int(v) for v in lightest_px)}  luminance={lightest_lum:.4f}")
    print(f"  position in canvas:  ({x1 + max_idx[1]}, {y1 + max_idx[0]})")
    print(f"  contrast vs text:    {ratio_light:.2f}:1")
    print()
    print("=== WCAG AA worst-case-pixel verdict ===")
    print(f"Body text (Satoshi 15-17px, threshold 4.5:1):")
    body_worst = min(ratio_dark, ratio_light)
    print(f"  worst-case ratio: {body_worst:.2f}:1 - {'PASS' if body_worst >= 4.5 else 'FAIL'}")
    print(f"Display text (Fraunces 48-96px, threshold 3:1):")
    disp_worst = min(ratio_dark, ratio_light)
    print(f"  worst-case ratio: {disp_worst:.2f}:1 - {'PASS' if disp_worst >= 3.0 else 'FAIL'}")

    # Additional diagnostic: histogram of luminance in zone
    print()
    print("=== Luminance distribution in zone (opaque only) ===")
    opaque_lum = lum[mask]
    percentiles = [0, 1, 5, 25, 50, 75, 95, 99, 100]
    for p in percentiles:
        v = float(np.percentile(opaque_lum, p))
        cr = contrast_ratio(text_lum, v)
        print(f"  {p:3d}th percentile luminance: {v:.4f}  (contrast {cr:.2f}:1)")


if __name__ == "__main__":
    main()
