"""Chroma-key extraction + composite for Pacifico v1 layers (biome-6 FINAL).

4-layer composite: sky-subject -> plateau -> boats -> framing-waves

Architecture decisions (from diagnostic session):
- Boats offset (0, -60) shifts boats UP 60px to clear framing-waves crest.
- Framing-waves offset (0, +60) shifts waves DOWN 60px for boats clearance.
- Plateau top alpha-ramp 0.4 -> 1.0 over y=0..40px bridges the sky-subject
  exit (#6d7577) to plateau top (#cdbda4) palette seam (flagged in 2d0f5a0).
- Chroma tolerance 80 (Paracas precedent — clean painterly magenta).
- is_pinkish strict: r>180, g<110, b>120 (Apu+Puna precedent tightened per
  sampled magenta variance across the 4 Pacifico sources).
- Each layer auto-detects its own chroma color (per-image sample regions
  chosen to avoid pink-drift/content zones).

Composite lives at the biome root (public/Backdrops/pacifico/) not in
processed/ — consistent with user's git-add spec for the v1 commit.
Intermediate layer WebPs + scrim + heatmap go to processed/ as usual.

Expected sources (fal.ai flux-2-pro, JPG, 1024x768):
  public/Backdrops/pacifico/Raw/pacifico-sky-subject.jpg
  public/Backdrops/pacifico/Raw/pacifico-plateau.jpg
  public/Backdrops/pacifico/Raw/pacifico-boats.jpg
  public/Backdrops/pacifico/Raw/pacifico-framing-waves.jpg

Usage (from repo root):
  python scripts/process_pacifico.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


REPO = Path(r"C:\Users\odear\projects\limai")
RAW_DIR = REPO / "public" / "Backdrops" / "pacifico" / "Raw"
BIOME_DIR = REPO / "public" / "Backdrops" / "pacifico"  # composite lives here
PROCESSED_DIR = BIOME_DIR / "processed"  # intermediate artifacts

CANVAS = (1024, 768)
CHROMA_TOLERANCE = 80

# Offset corrections from Image 4 y-shift diagnostic.
# A3 strategy: boats UP 60, framing-waves DOWN 60, ~24px gap between layers.
SKY_OFFSET             = (0, 0)
PLATEAU_OFFSET         = (0, 0)
BOATS_OFFSET           = (0, -60)
FRAMING_WAVES_OFFSET   = (0, 60)

# Plateau top alpha-ramp. Bridges sky-subject exit (#6d7577) to plateau top
# (#cdbda4). At plateau y=0 alpha *= 0.4 so sky shows through at 60%; at
# y=40 alpha *= 1.0 so plateau fully opaque. 0..40 linear.
PLATEAU_ALPHA_START   = 0.4
PLATEAU_ALPHA_END_Y   = 40

# Text zone (legacy informational; F6 gradient is production scrim).
TEXT_ZONE = (180, 280, 630, 530)
TEXT_COLOR_LUM = 0.8423
SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)

SOURCES = {
    # sky-subject: magenta strip at BOTTOM (bottom 33% per diagnostic).
    "sky-subject":   (RAW_DIR / "pacifico-sky-subject.jpg",
                      (0.45, 0.90, 0.55, 0.99)),
    # plateau: opaque content y=0..641 (sky-mist top + ocean water), magenta
    # strip at BOTTOM y=642..767 only. Sample bottom-center magenta strip.
    "plateau":       (RAW_DIR / "pacifico-plateau.jpg",
                      (0.45, 0.92, 0.55, 0.98)),
    # boats: magenta everywhere except boats y=131..520 + pink drift y=0..99.
    # Sample bottom-center (safe magenta zone below boats cluster).
    "boats":         (RAW_DIR / "pacifico-boats.jpg",
                      (0.45, 0.75, 0.55, 0.85)),
    # framing-waves: magenta top ~55%. Sample top-center.
    "framing-waves": (RAW_DIR / "pacifico-framing-waves.jpg",
                      (0.45, 0.10, 0.55, 0.20)),
}


def detect_chroma(img_path, sample_region):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    x1, y1, x2, y2 = sample_region
    crop = img.crop((int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)))
    arr = np.array(crop)
    return (int(arr[..., 0].mean()),
            int(arr[..., 1].mean()),
            int(arr[..., 2].mean()))


def is_pinkish(color):
    # Strict Apu+Puna-style bounds for clean painterly magenta layers.
    r, g, b = color
    return r > 180 and g < 110 and b > 120


def remove_chroma(img_path, target, tolerance):
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)
    r = data[..., 0].astype(np.int32)
    g = data[..., 1].astype(np.int32)
    b = data[..., 2].astype(np.int32)
    tr, tg, tb = target
    dist = np.sqrt((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2)
    mask = (dist > tolerance).astype(np.uint8) * 255
    mask_img = Image.fromarray(mask, mode="L")
    mask_img = mask_img.filter(ImageFilter.MinFilter(3))
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(2))
    data[..., 3] = np.array(mask_img)
    return Image.fromarray(data.astype(np.uint8), mode="RGBA")


def process_layer(img_path, sample_region, name):
    detected = detect_chroma(img_path, sample_region)
    print(f"  {name}: sampled chroma RGB{detected}", end="")
    if is_pinkish(detected):
        layer = remove_chroma(img_path, detected, CHROMA_TOLERANCE)
        arr = np.array(layer)[..., 3]
        pct = 100 * (arr > 128).sum() / arr.size
        print(f"  -> chroma removed, {pct:.1f}% opaque")
    else:
        layer = Image.open(img_path).convert("RGBA")
        print(f"  -> no chroma detected (is_pinkish failed), fully opaque")
    if layer.size != CANVAS:
        print(f"    [info] layer size {layer.size} != canvas {CANVAS}, resizing")
        layer = layer.resize(CANVAS, Image.LANCZOS)
    return layer


def alpha_ramp_top(img, end_y, start_alpha=0.4, end_alpha=1.0, diagnostic=True):
    """Linear alpha multiplier on the top band of the layer.

    At y=0: alpha *= start_alpha.  At y>=end_y: alpha *= end_alpha.
    Between: linear interpolation. Used here to bridge the palette seam
    between sky-subject bottom and plateau top.
    """
    arr = np.array(img).astype(np.float64)
    h = arr.shape[0]
    ys = np.arange(h)
    gradient = np.full(h, end_alpha, dtype=np.float64)
    ramp_zone = ys < end_y
    gradient[ramp_zone] = start_alpha + (end_alpha - start_alpha) * (ys[ramp_zone] / max(end_y, 1))

    if diagnostic:
        print(f"    alpha-ramp: y=0 gradient={gradient[0]:.2f}"
              f"  y={end_y} gradient={gradient[min(end_y, h-1)]:.2f}"
              f"  ({end_y} rows attenuated)")

    arr[..., 3] = np.clip(arr[..., 3] * gradient[:, np.newaxis], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), mode="RGBA")


def place(layer, position):
    c = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    c.paste(layer, position, layer)
    return c


def composite_stack(layers):
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for layer in layers:
        out = Image.alpha_composite(out, layer)
    return out


def srgb_to_linear(c):
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb):
    lin = srgb_to_linear(rgb.astype(np.float64))
    return 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]


def contrast_vs_text(lum, text_lum=TEXT_COLOR_LUM):
    return np.where(lum > text_lum,
                    (lum + 0.05) / (text_lum + 0.05),
                    (text_lum + 0.05) / (lum + 0.05))


def apply_scrim_55(composite):
    scrim = Image.new("RGBA", CANVAS,
                      (*SCRIM_COLOR, int(SCRIM_OPACITY * 255)))
    return Image.alpha_composite(composite, scrim)


def measure_gate8(composite, text_zone):
    arr = np.array(composite)
    x1, y1, x2, y2 = text_zone
    region_rgb = arr[y1:y2, x1:x2, :3]
    region_alpha = arr[y1:y2, x1:x2, 3]
    mask = region_alpha > 240
    if not mask.any():
        return {"p95_lum": 0.0, "worst_lum": 0.0,
                "p95_contrast": 0.0, "worst_contrast": 0.0,
                "body_pass": False, "display_pass": False, "opaque_px": 0}
    lum = relative_luminance(region_rgb)
    lum_opaque = lum[mask]
    p95 = float(np.percentile(lum_opaque, 95))
    worst = float(lum_opaque.max())
    p95_contrast = float(contrast_vs_text(np.array([p95]))[0])
    worst_contrast = float(contrast_vs_text(np.array([worst]))[0])
    return {
        "p95_lum": p95,
        "worst_lum": worst,
        "p95_contrast": p95_contrast,
        "worst_contrast": worst_contrast,
        "body_pass": p95_contrast >= 4.5,
        "display_pass": p95_contrast >= 3.0,
        "opaque_px": int(mask.sum()),
    }


def build_heatmap(composite, out_path):
    arr = np.array(composite)
    rgb = arr[..., :3].astype(np.float64)
    lum = relative_luminance(rgb)
    cr = contrast_vs_text(lum)
    h, w = lum.shape
    heatmap = np.zeros((h, w, 3), dtype=np.uint8)
    heatmap[cr < 3.0] = [180, 40, 40]
    heatmap[(cr >= 3.0) & (cr < 4.5)] = [220, 150, 40]
    heatmap[cr >= 4.5] = [70, 170, 70]
    blended = (0.35 * heatmap + 0.65 * rgb).astype(np.uint8)
    Image.fromarray(blended).save(out_path, "PNG")


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    missing = [path for _, (path, _) in SOURCES.items() if not path.exists()]
    if missing:
        print("ERROR: missing Pacifico source layers:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        raise SystemExit(1)

    BIOME_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Pacifico 1024 pipeline (biome-6 FINAL, 4-layer composite)")
    print(f"Canvas:       {CANVAS[0]}x{CANVAS[1]}")
    print(f"Stack:        sky-subject -> plateau -> boats -> framing-waves")
    print(f"Offsets:      sky={SKY_OFFSET}  plateau={PLATEAU_OFFSET}")
    print(f"              boats={BOATS_OFFSET}  waves={FRAMING_WAVES_OFFSET}")
    print(f"Tolerance:    {CHROMA_TOLERANCE}  is_pinkish: r>180 g<110 b>120")
    print(f"Plateau ramp: alpha {PLATEAU_ALPHA_START} at y=0 -> 1.0 at y={PLATEAU_ALPHA_END_Y}")
    print("=" * 72)

    print("\nSTEP 1 - chroma extraction per layer")
    processed = {}
    for name, (path, sample) in SOURCES.items():
        layer = process_layer(path, sample, name)
        if name == "plateau":
            layer = alpha_ramp_top(layer, PLATEAU_ALPHA_END_Y,
                                   PLATEAU_ALPHA_START, 1.0)
        out_path = PROCESSED_DIR / f"pacifico-{name}.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        kb = out_path.stat().st_size / 1024
        print(f"    saved: {out_path.name}  {kb:.0f} KB")
        processed[name] = layer

    print(f"\nSTEP 2 - composite 4-layer stack with offsets")
    sky     = place(processed["sky-subject"],    SKY_OFFSET)
    plateau = place(processed["plateau"],        PLATEAU_OFFSET)
    boats   = place(processed["boats"],          BOATS_OFFSET)
    waves   = place(processed["framing-waves"],  FRAMING_WAVES_OFFSET)
    composite = composite_stack([sky, plateau, boats, waves])
    composite_path = BIOME_DIR / "pacifico-composite.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)
    composite_kb = composite_path.stat().st_size / 1024
    print(f"  saved: {composite_path.name}  {composite_kb:.0f} KB")

    print("\nSTEP 3 - 55% Noche Andina scrim (legacy preview)")
    scrim_composite = apply_scrim_55(composite)
    scrim_path = PROCESSED_DIR / "pacifico-composite-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)
    scrim_kb = scrim_path.stat().st_size / 1024
    print(f"  saved: {scrim_path.name}  {scrim_kb:.0f} KB")

    print("\nSTEP 4 - Gate 8 measurement (informational)")
    metrics = measure_gate8(scrim_composite, TEXT_ZONE)
    body_v = "PASS" if metrics["body_pass"] else "FAIL"
    disp_v = "PASS" if metrics["display_pass"] else "FAIL"
    print(f"  p95 luminance:    {metrics['p95_lum']:.4f}")
    print(f"  p95 contrast:     {metrics['p95_contrast']:.2f}:1  "
          f"(body {body_v}, display {disp_v})")
    print(f"  worst contrast:   {metrics['worst_contrast']:.2f}:1  (diagnostic)")

    print("\nSTEP 5 - Gate 8 heatmap (legacy)")
    heatmap_path = PROCESSED_DIR / "pacifico-composite-heatmap.png"
    build_heatmap(scrim_composite, heatmap_path)
    print(f"  saved: {heatmap_path.name}")

    print("\n" + "=" * 72)
    print("Cross-biome p95 contrast (F6 gradient is production scrim — info only):")
    print(f"  Apu:      5.35:1")
    print(f"  Puna:     3.58:1")
    print(f"  Yungas:   5.89:1")
    print(f"  Selva:    6.93:1")
    print(f"  Paracas:  4.77:1")
    print(f"  Pacifico: {metrics['p95_contrast']:.2f}:1  (biome 6 FINAL)")
    print("=" * 72)
    print(f"\n  composite: {composite_path}")
    print(f"  processed: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
