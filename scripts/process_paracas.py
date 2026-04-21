"""Chroma-key extraction + composite for Paracas v1 layers (1024 UI pipeline).

BOTTOM framing geometry — NOVEL in project (first BOTTOM framing, after
Apu/Puna LEFT, Yungas RIGHT, Selva TOP). Composite stack:
  sky-subject (back) → plateau (mid) → framing-dune (front)

Framing-dune source has opaque dune content at image BOTTOM and magenta
at TOP (inverse of Selva canopy's structure). Feather on framing-dune is
'top' edge: opaque at dune body (high y), fading UP to transparent at the
curved crest and above (low y). This is the inverse direction of Selva
canopy, which faded DOWN.

Paracas palette is warm-bronze dominant with cool lavender shadow
threading (from user prompt analysis). Chroma tolerance 80 (clean warm
palette, Apu+Puna precedent — tighter than Selva/Yungas 130). Strict
is_pinkish bounds (r>180, b>120, g<110) match Apu because Paracas
magenta strips render clean.

Luminance clamps start disabled per user spec — diagnose first run, add
only if hot-spots actually appear.

Expected sources (fal.ai UI output, JPG, 1024x768):
  public/Backdrops/paracas/Raw/paracas-sky-subject.jpg
  public/Backdrops/paracas/Raw/paracas-plateau.jpg
  public/Backdrops/paracas/Raw/paracas-framing-dune.jpg

Usage (from repo root):
  python scripts/process_paracas.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


REPO = Path(r"C:\Users\odear\projects\limai")
RAW_DIR = REPO / "public" / "Backdrops" / "paracas" / "Raw"
OUT_DIR = REPO / "public" / "Backdrops" / "paracas" / "processed"

CANVAS = (1024, 768)
CHROMA_TOLERANCE = 80  # Apu+Puna precedent for clean warm-bronze palette

# BOTTOM framing geometry.
# Framing-dune source: opaque dune at bottom, magenta at top.
# (0, 0) offset keeps image aligned; dune lands canvas-y=540..768 approx.
FRAMING_OFFSET = (0, 0)
# Plateau: bottom-aligned sand band. (0, 0) = source y=0..768 → canvas y=0..768.
# Plateau v1 Image 5 content spans y~442..767 per diagnostic; magenta top
# extracted to transparent. Adjust after visual check if plateau sits wrong.
PLATEAU_OFFSET = (0, 0)

# Framing-dune TOP-edge alpha feather — fades UP from opaque dune body to
# transparent above the curved crest, softening the framing-to-plateau seam.
# User-semantic naming (canvas-y-space):
#   START_Y = top of fade band (transparent target — at/above curved crest)
#   END_Y   = bottom of fade band (opaque target — dune body begins here)
# feather_edge('top') convention requires fade_start > fade_end, so we pass
# END_Y as fade_start and START_Y as fade_end at the call site.
FRAMING_FEATHER_START_Y = 250  # top of fade (transparent)
FRAMING_FEATHER_END_Y   = 400  # bottom of fade (opaque)

# Luminance clamps — disabled on first run per user spec. Diagnose, then
# enable if hot-spot counts exceed ~100 in diagnostic zones.
PLATEAU_LUM_CLAMP = None
FRAMING_LUM_CLAMP = None

# Text zone (legacy informational; F6 gradient is production scrim)
TEXT_ZONE = (180, 280, 630, 530)
TEXT_COLOR_LUM = 0.8423
SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)

SOURCES = {
    # sky-subject: magenta strip at BOTTOM 8-12% → sample bottom-center
    "sky-subject":  (RAW_DIR / "paracas-sky-subject.jpg",
                     (0.45, 0.93, 0.55, 0.99)),
    # plateau: magenta at TOP ~82-85% → sample top-center
    "plateau":      (RAW_DIR / "paracas-plateau.jpg",
                     (0.45, 0.05, 0.55, 0.15)),
    # framing-dune: magenta at TOP ~70-75% → sample top-center
    "framing-dune": (RAW_DIR / "paracas-framing-dune.jpg",
                     (0.45, 0.05, 0.55, 0.15)),
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
    r, g, b = color
    return r > 180 and b > 120 and g < 110


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


def clamp_luminance(img, max_lum, diagnostic_zone=None):
    arr = np.array(img).astype(np.float64)
    rgb = arr[..., :3]
    lum = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    lum_norm = lum / 255.0
    pre_count = None
    if diagnostic_zone is not None:
        y1, y2, x1, x2 = diagnostic_zone
        pre_count = int((lum_norm[y1:y2, x1:x2] > max_lum).sum())
        print(f"    pre-clamp zone y=[{y1}..{y2}), x=[{x1}..{x2}): "
              f"{pre_count} pixels lum>{max_lum:.2f}")
    scale = np.where(lum_norm > max_lum,
                     (max_lum * 255.0) / np.maximum(lum, 1.0), 1.0)
    arr[..., :3] = np.clip(rgb * scale[..., np.newaxis], 0, 255)
    if diagnostic_zone is not None:
        new_rgb = arr[..., :3]
        new_lum = (0.2126 * new_rgb[..., 0] + 0.7152 * new_rgb[..., 1]
                   + 0.0722 * new_rgb[..., 2]) / 255.0
        post_count = int((new_lum[y1:y2, x1:x2] > max_lum).sum())
        print(f"    post-clamp zone: {post_count} pixels lum>{max_lum:.2f} "
              f"(reduced by {pre_count - post_count}, cap = {max_lum:.2f})")
    return Image.fromarray(arr.astype(np.uint8), mode="RGBA")


def feather_edge(img, edge, fade_start, fade_end, diagnostic=True):
    """Vertical alpha gradient. See process_selva.py for full docs.

    edge='bottom': opaque above fade_start, fade 1→0 through fade_end.
    edge='top':    opaque below fade_start, fade 1→0 reversed to fade_end.
    """
    arr = np.array(img).astype(np.float64)
    h = arr.shape[0]
    ys = np.arange(h)
    gradient = np.ones(h, dtype=np.float64)
    if edge == 'bottom':
        assert fade_end > fade_start, \
            f"bottom edge needs fade_end > fade_start (got {fade_start}, {fade_end})"
        fade_mask = (ys >= fade_start) & (ys < fade_end)
        gradient[fade_mask] = 1.0 - (ys[fade_mask] - fade_start) / (fade_end - fade_start)
        gradient[ys >= fade_end] = 0.0
        bands = [(0, fade_start, "above fade (opaque target)"),
                 (fade_start, fade_end, "fade zone"),
                 (fade_end, h, "below fade (transparent target)")]
    elif edge == 'top':
        assert fade_start > fade_end, \
            f"top edge needs fade_start > fade_end (got {fade_start}, {fade_end})"
        fade_mask = (ys >= fade_end) & (ys < fade_start)
        gradient[fade_mask] = (ys[fade_mask] - fade_end) / (fade_start - fade_end)
        gradient[ys < fade_end] = 0.0
        bands = [(0, fade_end, "above fade (transparent target)"),
                 (fade_end, fade_start, "fade zone"),
                 (fade_start, h, "below fade (opaque target)")]
    else:
        raise ValueError(f"edge must be 'bottom' or 'top', got {edge!r}")
    if diagnostic:
        pre_alpha = arr[..., 3].copy()
        print(f"    pre-feather ({edge}, fade {fade_start}->{fade_end}) alpha opaque% per band:")
        for y1, y2, label in bands:
            zone = pre_alpha[y1:y2]
            pct = (zone > 240).sum() * 100.0 / max(zone.size, 1)
            print(f"      y=[{y1}..{y2}) {label}: {pct:.1f}%")
    arr[..., 3] = np.clip(arr[..., 3] * gradient[:, np.newaxis], 0, 255)
    if diagnostic:
        post_alpha = arr[..., 3]
        affected = int(((pre_alpha - post_alpha) > 1).sum())
        print(f"    post-feather: {affected:,} pixels had alpha reduced")
        print("    post-feather alpha opaque% per band:")
        for y1, y2, label in bands:
            zone = post_alpha[y1:y2]
            pct = (zone > 240).sum() * 100.0 / max(zone.size, 1)
            print(f"      y=[{y1}..{y2}) {label}: {pct:.1f}%")
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


def hot_spot_diagnostic(img, name, zone=None, threshold=0.70):
    """Pre-composite hot-spot count at luminance threshold (pre-clamp visibility)."""
    arr = np.array(img).astype(np.float64)
    rgb = arr[..., :3]
    alpha = arr[..., 3]
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]) / 255.0
    opaque_mask = alpha > 240
    if zone is not None:
        y1, y2, x1, x2 = zone
        region_lum = lum[y1:y2, x1:x2]
        region_opaque = opaque_mask[y1:y2, x1:x2]
        count = int(((region_lum > threshold) & region_opaque).sum())
        print(f"    [{name}] hot-spot diagnostic zone y=[{y1}..{y2}), x=[{x1}..{x2}): "
              f"{count} opaque pixels lum>{threshold:.2f}")
    else:
        count = int(((lum > threshold) & opaque_mask).sum())
        print(f"    [{name}] hot-spot diagnostic full-layer: "
              f"{count} opaque pixels lum>{threshold:.2f}")
    return count


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    missing = [path for _, (path, _) in SOURCES.items() if not path.exists()]
    if missing:
        print("ERROR: missing Paracas source layers:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        raise SystemExit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Paracas 1024 pipeline (biome-5, first BOTTOM framing in project)")
    print(f"Canvas:       {CANVAS[0]}x{CANVAS[1]}")
    print(f"Framing:      framing-dune @ offset {FRAMING_OFFSET} (BOTTOM)")
    print(f"Plateau:      offset {PLATEAU_OFFSET}")
    print(f"Tolerance:    {CHROMA_TOLERANCE}  (Apu+Puna precedent)")
    print(f"is_pinkish:   strict (r>180, b>120, g<110)")
    print(f"Clamps:       plateau={PLATEAU_LUM_CLAMP}  framing={FRAMING_LUM_CLAMP}")
    print(f"Feather:      framing-dune TOP edge y=[{FRAMING_FEATHER_START_Y}..{FRAMING_FEATHER_END_Y}]")
    print("=" * 72)

    print("\nSTEP 1 - chroma extraction per layer")
    processed = {}
    for name, (path, sample) in SOURCES.items():
        layer = process_layer(path, sample, name)
        # Hot-spot diagnostic (pre-clamp visibility on every layer)
        hot_spot_diagnostic(layer, name, zone=None, threshold=0.70)
        if name == "framing-dune":
            if FRAMING_LUM_CLAMP is not None:
                layer = clamp_luminance(layer, FRAMING_LUM_CLAMP,
                                        diagnostic_zone=(540, 768, 0, 1024))
            # TOP-edge feather: dune body opaque at bottom, fades UP through
            # curved crest to transparent above. feather_edge('top') wants
            # fade_start > fade_end → pass END_Y first, START_Y second.
            layer = feather_edge(layer, 'top',
                                 fade_start=FRAMING_FEATHER_END_Y,
                                 fade_end=FRAMING_FEATHER_START_Y)
        elif name == "plateau":
            if PLATEAU_LUM_CLAMP is not None:
                layer = clamp_luminance(layer, PLATEAU_LUM_CLAMP,
                                        diagnostic_zone=(440, 600, 300, 700))
        out_path = OUT_DIR / f"paracas-{name}.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        kb = out_path.stat().st_size / 1024
        print(f"    saved: {out_path.name}  {kb:.0f} KB")
        processed[name] = layer

    print(f"\nSTEP 2 - composite BOTTOM-framing "
          f"(sky back, plateau mid, framing-dune front)")
    sky = place(processed["sky-subject"], (0, 0))
    plateau = place(processed["plateau"], PLATEAU_OFFSET)
    framing = place(processed["framing-dune"], FRAMING_OFFSET)
    composite = composite_stack([sky, plateau, framing])
    composite_path = OUT_DIR / "paracas-composite.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)
    composite_kb = composite_path.stat().st_size / 1024
    print(f"  saved: {composite_path.name}  {composite_kb:.0f} KB")

    print("\nSTEP 3 - apply 55% Noche Andina scrim (legacy preview)")
    scrim_composite = apply_scrim_55(composite)
    scrim_path = OUT_DIR / "paracas-composite-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)
    scrim_kb = scrim_path.stat().st_size / 1024
    print(f"  saved: {scrim_path.name}  {scrim_kb:.0f} KB")

    print("\nSTEP 4 - Gate 8 measurement (informational)")
    paracas_metrics = measure_gate8(scrim_composite, TEXT_ZONE)
    body_v = "PASS" if paracas_metrics["body_pass"] else "FAIL"
    disp_v = "PASS" if paracas_metrics["display_pass"] else "FAIL"
    print(f"  p95 luminance:    {paracas_metrics['p95_lum']:.4f}")
    print(f"  p95 contrast:     {paracas_metrics['p95_contrast']:.2f}:1  "
          f"(body {body_v}, display {disp_v})")
    print(f"  worst contrast:   {paracas_metrics['worst_contrast']:.2f}:1  (diagnostic)")
    print(f"  opaque px in zone: {paracas_metrics['opaque_px']:,}")

    print("\nSTEP 5 - Gate 8 heatmap (legacy)")
    heatmap_path = OUT_DIR / "paracas-composite-heatmap.png"
    build_heatmap(scrim_composite, heatmap_path)
    print(f"  saved: {heatmap_path.name}")

    print("\n" + "=" * 72)
    print("Cross-biome p95 contrast (F6 gradient is production scrim — informational):")
    print(f"  Apu:     5.35:1")
    print(f"  Puna:    3.58:1")
    print(f"  Yungas:  5.89:1")
    print(f"  Selva:   6.93:1")
    print(f"  Paracas: {paracas_metrics['p95_contrast']:.2f}:1  (biome 5 first run)")
    print("=" * 72)
    print(f"\n  outputs: {OUT_DIR}")


if __name__ == "__main__":
    main()
