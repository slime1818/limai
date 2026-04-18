"""Gate 9 validation harness for flux-2-max Apu mountain-face output.

Runs 5 checks:
1. File-size: raw PNG + WebP q82 @ native 2560x1920, target ≤ 1.7 MB
2. Chroma-strip: bottom-band magenta integrity + coverage
3. Subject-dominance: painted silhouette (non-chroma dark-mass via Otsu)
4. Composite + Gate 8 contrast: build composite with existing plateau/framing-rock
   layers, apply 55% working-default scrim, measure p95 contrast in text zone
5. Side-by-side comparison vs flux-2-pro v4.2 baseline (HTML with metrics +
   luminance histograms + crop strips)

Default input:    public/Backdrops/apu/Raw/apu-mountain-face-flux2max-v1.png
Default baseline: public/Backdrops/apu/Raw/apu-mountain-face.jpg

Usage:
    python scripts/validate_flux2max.py
    python scripts/validate_flux2max.py --input <path> --baseline <path>

Exit code 0 = PASS all gates, 2 = one or more FAIL, 1 = IO / config error.
"""
from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

REPO = Path(r"C:\Users\odear\projects\limai")
RAW = REPO / "public" / "Backdrops" / "apu" / "Raw"
PROC = REPO / "public" / "Backdrops" / "apu" / "processed"
OUT = PROC / "flux2max-validation"

DEFAULT_INPUT = RAW / "apu-mountain-face-flux2max-v1.png"
DEFAULT_BASELINE = RAW / "apu-mountain-face.jpg"

PLATEAU_LAYER = PROC / "apu-plateau.webp"
FRAMING_LAYER = PROC / "apu-framing-rock.webp"

# Constants — match process_apu.py / contrast_check.py / test_scrim.py
CANVAS_SIZE = (1024, 768)
CHROMA_SAMPLE = (0.45, 0.92, 0.55, 0.98)   # bottom-center of frame
CHROMA_TOLERANCE = 55
TEXT_ZONE = (250, 280, 700, 530)           # x1, y1, x2, y2 on 1024x768
TEXT_COLOR_LUM = 0.8423                    # #f4ecd9 relative luminance
SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)                 # Noche Andina #1a1612
FRAMING_OFFSET = (-200, 0)                 # variant B placement

# Thresholds
MAX_WEBP_MB = 1.7
CHROMA_BAND_MIN_PCT = 80                   # ≥80% of bottom 15% band is chroma
CHROMA_CENTROID_MIN = 0.80                 # vertical centroid ≥ 0.80 (bottom-heavy)
SUBJECT_ABS_MIN = 65                       # absolute range
SUBJECT_ABS_MAX = 80
SUBJECT_REL_TOLERANCE = 5.0                # ±5% vs baseline
BODY_AA = 4.5
DISPLAY_AA = 3.0


# ============================================================================
# Helpers — luminance, contrast, chroma detection
# ============================================================================

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


def is_pinkish(c):
    r, g, b = c
    return r > 180 and b > 120 and g < 90


def detect_chroma(arr_rgb, region=CHROMA_SAMPLE):
    h, w = arr_rgb.shape[:2]
    x1, y1, x2, y2 = region
    crop = arr_rgb[int(y1 * h):int(y2 * h), int(x1 * w):int(x2 * w)]
    return (int(crop[..., 0].mean()),
            int(crop[..., 1].mean()),
            int(crop[..., 2].mean()))


def chroma_mask(arr_rgb, target, tolerance=CHROMA_TOLERANCE):
    r = arr_rgb[..., 0].astype(np.int32)
    g = arr_rgb[..., 1].astype(np.int32)
    b = arr_rgb[..., 2].astype(np.int32)
    tr, tg, tb = target
    dist = np.sqrt((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2)
    return dist <= tolerance


def extract_rgba(img_path: Path) -> Image.Image:
    """Load, detect+remove chroma, return RGBA with feathered alpha."""
    img = Image.open(img_path).convert("RGBA")
    arr = np.array(img)
    rgb = arr[..., :3]
    target = detect_chroma(rgb)
    if not is_pinkish(target):
        return img  # no chroma, fully opaque
    cmask = chroma_mask(rgb, target)
    alpha = np.where(cmask, 0, 255).astype(np.uint8)
    a_img = Image.fromarray(alpha, mode="L")
    a_img = a_img.filter(ImageFilter.MinFilter(3))     # contract 1px
    a_img = a_img.filter(ImageFilter.GaussianBlur(2))  # feather 2px
    arr[..., 3] = np.array(a_img)
    return Image.fromarray(arr, mode="RGBA")


def _resolve_input(path: Path) -> Path:
    """If path doesn't exist, try common image extensions for the same stem."""
    if path.exists():
        return path
    base = path.with_suffix("")
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        alt = base.with_suffix(ext)
        if alt.exists():
            return alt
    return path


def otsu_threshold(values_01):
    """Pure-numpy Otsu threshold on 1D array of floats in [0, 1]."""
    hist, _ = np.histogram(values_01, bins=256, range=(0.0, 1.0))
    total = hist.sum()
    if total == 0:
        return 0.5
    sum_total = (hist * np.arange(256)).sum()
    sum_b, weight_b, max_var, threshold_idx = 0.0, 0, 0.0, 0
    for i in range(256):
        weight_b += int(hist[i])
        if weight_b == 0:
            continue
        weight_f = int(total) - weight_b
        if weight_f == 0:
            break
        sum_b += i * int(hist[i])
        mean_b = sum_b / weight_b
        mean_f = (sum_total - sum_b) / weight_f
        var_between = weight_b * weight_f * (mean_b - mean_f) ** 2
        if var_between > max_var:
            max_var = var_between
            threshold_idx = i
    return threshold_idx / 255.0


# ============================================================================
# Check 1 — File size
# ============================================================================

@dataclass
class FileSizeResult:
    source_dimensions: str
    raw_bytes: int
    raw_mb: float
    webp_bytes: int
    webp_mb: float
    webp_path: str
    pass_: bool
    detail: str


def check_file_size(input_path: Path, out_dir: Path) -> FileSizeResult:
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    raw_bytes = input_path.stat().st_size
    webp_path = out_dir / f"{input_path.stem}@2x.webp"
    img.save(webp_path, "WebP", quality=82, method=6)
    webp_bytes = webp_path.stat().st_size
    raw_mb = raw_bytes / (1024 * 1024)
    webp_mb = webp_bytes / (1024 * 1024)
    passed = webp_mb <= MAX_WEBP_MB
    detail = (f"source {w}x{h}, raw PNG {raw_mb:.2f} MB, WebP q82 {webp_mb:.2f} MB "
              f"(target ≤ {MAX_WEBP_MB} MB)")
    return FileSizeResult(
        source_dimensions=f"{w}x{h}",
        raw_bytes=raw_bytes,
        raw_mb=raw_mb,
        webp_bytes=webp_bytes,
        webp_mb=webp_mb,
        webp_path=str(webp_path),
        pass_=passed,
        detail=detail,
    )


# ============================================================================
# Check 2 — Chroma-strip integrity
# ============================================================================

@dataclass
class ChromaResult:
    sampled_rgb: tuple
    is_pinkish: bool
    total_chroma_pct: float
    bottom_band_coverage_pct: float
    vertical_centroid_normalized: float
    pass_: bool
    detail: str


def check_chroma_strip(input_path: Path) -> ChromaResult:
    img = Image.open(input_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    target = detect_chroma(arr)
    pink = is_pinkish(target)
    mask = chroma_mask(arr, target) if pink else np.zeros((h, w), dtype=bool)
    total_chroma = int(mask.sum())
    total_pct = 100 * total_chroma / mask.size if mask.size else 0.0

    band_start = int(h * 0.85)  # bottom 15%
    band_mask = mask[band_start:, :]
    band_pct = 100 * band_mask.sum() / band_mask.size if band_mask.size else 0.0

    if total_chroma > 0:
        ys, _ = np.where(mask)
        y_centroid = float(ys.mean() / h)
    else:
        y_centroid = 0.0

    passed = pink and band_pct >= CHROMA_BAND_MIN_PCT and y_centroid >= CHROMA_CENTROID_MIN
    detail = (f"sampled chroma RGB{target}, pinkish={pink}. "
              f"bottom 15% band coverage {band_pct:.1f}% (≥{CHROMA_BAND_MIN_PCT}%). "
              f"total chroma {total_pct:.1f}%. "
              f"vertical centroid y={y_centroid:.2f} (≥{CHROMA_CENTROID_MIN} = bottom-heavy)")
    return ChromaResult(
        sampled_rgb=target,
        is_pinkish=pink,
        total_chroma_pct=total_pct,
        bottom_band_coverage_pct=band_pct,
        vertical_centroid_normalized=y_centroid,
        pass_=passed,
        detail=detail,
    )


# ============================================================================
# Check 3 — Subject-dominance (Otsu on non-chroma luminance, abs+rel)
# ============================================================================

@dataclass
class SubjectResult:
    method: str
    otsu_threshold: float
    subject_dominance_pct: float
    painted_coverage_pct: float
    baseline_subject_dominance_pct: float
    delta_vs_baseline: float
    abs_pass: bool
    rel_pass: bool
    target_band_hit: bool
    pass_: bool
    mask_path: str
    detail: str


def _measure_subject(img_path: Path):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    h, w = arr.shape[:2]
    total = h * w
    target = detect_chroma(arr)
    if is_pinkish(target):
        cmask = chroma_mask(arr, target)
        non_chroma = ~cmask
    else:
        cmask = np.zeros((h, w), dtype=bool)
        non_chroma = np.ones((h, w), dtype=bool)
    lum = relative_luminance(arr)
    lum_nc = lum[non_chroma]
    if lum_nc.size == 0:
        return arr, cmask, non_chroma, np.zeros_like(non_chroma), 0.0, 0.0, 0.0
    thresh = otsu_threshold(lum_nc)
    subject_mask = non_chroma & (lum < thresh)
    subject_pct = 100 * subject_mask.sum() / total
    painted_pct = 100 * non_chroma.sum() / total
    return arr, cmask, non_chroma, subject_mask, thresh, subject_pct, painted_pct


def check_subject_dominance(input_path: Path, baseline_path: Path,
                            out_dir: Path) -> SubjectResult:
    arr, cmask, non_chroma, subject_mask, thresh, subject_pct, painted_pct = \
        _measure_subject(input_path)
    _, _, _, _, _, base_subject_pct, _ = _measure_subject(baseline_path)

    delta = subject_pct - base_subject_pct

    # Save mask visualization
    h, w = arr.shape[:2]
    vis = np.zeros((h, w, 3), dtype=np.uint8)
    vis[subject_mask] = [70, 170, 70]                            # green = subject
    vis[non_chroma & ~subject_mask] = [200, 200, 80]             # yellow = sky/light
    vis[cmask] = [200, 40, 160]                                  # magenta = chroma
    blended = (0.5 * vis + 0.5 * arr).astype(np.uint8)
    mask_path = out_dir / f"{input_path.stem}-subject-mask.png"
    Image.fromarray(blended).save(mask_path, "PNG")

    abs_pass = SUBJECT_ABS_MIN <= subject_pct <= SUBJECT_ABS_MAX
    rel_pass = abs(delta) <= SUBJECT_REL_TOLERANCE
    target_hit = 70 <= subject_pct <= 75
    # Pass criterion = relative consistency vs baseline only. The Otsu-on-non-chroma
    # method cannot reliably reproduce the user's visual "70-75%" assessment
    # (Otsu captures deep-shadow vs everything-else, not mountain-silhouette vs sky).
    # Absolute range reported as informational; visual 70-75% verification happens
    # in the side-by-side HTML.
    passed = rel_pass

    detail = (f"Otsu on non-chroma luminance, threshold L={thresh:.4f}. "
              f"new {subject_pct:.1f}%, baseline {base_subject_pct:.1f}%, Δ {delta:+.1f}pp. "
              f"rel ±{SUBJECT_REL_TOLERANCE}pp (binding): {rel_pass}. "
              f"abs {SUBJECT_ABS_MIN}-{SUBJECT_ABS_MAX}% (informational): {abs_pass}. "
              f"target 70-75% hit (informational): {target_hit}. "
              f"painted coverage {painted_pct:.1f}%. "
              f"visual 70-75% confirmation via side-by-side HTML, not this metric. "
              f"mask visualization: {mask_path.name}")
    return SubjectResult(
        method="otsu-luminance-on-non-chroma",
        otsu_threshold=thresh,
        subject_dominance_pct=subject_pct,
        painted_coverage_pct=painted_pct,
        baseline_subject_dominance_pct=base_subject_pct,
        delta_vs_baseline=delta,
        abs_pass=abs_pass,
        rel_pass=rel_pass,
        target_band_hit=target_hit,
        pass_=passed,
        mask_path=str(mask_path),
        detail=detail,
    )


# ============================================================================
# Check 4 — Composite + Gate 8 contrast (55% scrim)
# ============================================================================

@dataclass
class ContrastResult:
    composite_path: str
    scrim_composite_path: str
    heatmap_path: str
    p95_lum: float
    max_lum: float
    p95_contrast: float
    worst_contrast: float
    body_pass: bool
    display_pass: bool
    pass_: bool
    detail: str


def _place(layer: Image.Image, position=(0, 0)) -> Image.Image:
    c = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    c.paste(layer, position, layer)
    return c


def check_contrast(input_path: Path, out_dir: Path) -> ContrastResult:
    if not PLATEAU_LAYER.exists():
        raise FileNotFoundError(f"Expected existing plateau layer at {PLATEAU_LAYER}")
    if not FRAMING_LAYER.exists():
        raise FileNotFoundError(f"Expected existing framing-rock layer at {FRAMING_LAYER}")

    # New mountain — chroma extract + downscale to canvas
    mtn = extract_rgba(input_path)
    if mtn.size != CANVAS_SIZE:
        mtn = mtn.resize(CANVAS_SIZE, Image.LANCZOS)

    plateau = Image.open(PLATEAU_LAYER).convert("RGBA")
    if plateau.size != CANVAS_SIZE:
        plateau = plateau.resize(CANVAS_SIZE, Image.LANCZOS)
    framing = Image.open(FRAMING_LAYER).convert("RGBA")
    if framing.size != CANVAS_SIZE:
        framing = framing.resize(CANVAS_SIZE, Image.LANCZOS)

    mtn_p = _place(mtn, (0, 0))
    plt_p = _place(plateau, (0, 0))
    frm_p = _place(framing, FRAMING_OFFSET)
    composite = Image.alpha_composite(Image.alpha_composite(mtn_p, plt_p), frm_p)

    composite_path = out_dir / f"{input_path.stem}-composite.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)

    scrim = Image.new("RGBA", CANVAS_SIZE, (*SCRIM_COLOR, int(SCRIM_OPACITY * 255)))
    scrim_composite = Image.alpha_composite(composite, scrim)
    scrim_path = out_dir / f"{input_path.stem}-composite-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)

    # Gate 8 measurement — p95 luminance in text zone
    arr = np.array(scrim_composite)
    x1, y1, x2, y2 = TEXT_ZONE
    region_rgb = arr[y1:y2, x1:x2, :3]
    region_alpha = arr[y1:y2, x1:x2, 3]
    opaque = region_alpha > 240
    lum = relative_luminance(region_rgb)
    lum_opaque = lum[opaque]
    if lum_opaque.size == 0:
        p95_lum = max_lum = 0.0
        p95_contrast = worst_contrast = 0.0
    else:
        p95_lum = float(np.percentile(lum_opaque, 95))
        max_lum = float(lum_opaque.max())
        p95_contrast = float(contrast_vs_text(np.array([p95_lum]))[0])
        worst_contrast = float(contrast_vs_text(np.array([max_lum]))[0])

    body_pass = p95_contrast >= BODY_AA
    display_pass = p95_contrast >= DISPLAY_AA
    passed = body_pass  # Gate 8 body threshold is binding

    # Heatmap of scrim composite
    heatmap_path = _generate_heatmap(
        scrim_composite, out_dir / f"{input_path.stem}-composite-heatmap.png"
    )

    detail = (f"composite 1024x768 (new flux-2-max mountain + existing plateau/framing @ x=-200). "
              f"55% full-viewport scrim applied. text-zone p95 luminance {p95_lum:.4f}, "
              f"worst {max_lum:.4f}. p95 contrast {p95_contrast:.2f}:1 (body {BODY_AA}:1 "
              f"{'PASS' if body_pass else 'FAIL'}, display {DISPLAY_AA}:1 "
              f"{'PASS' if display_pass else 'FAIL'}). worst-px contrast {worst_contrast:.2f}:1 "
              f"(diagnostic, not binding)")
    return ContrastResult(
        composite_path=str(composite_path),
        scrim_composite_path=str(scrim_path),
        heatmap_path=str(heatmap_path),
        p95_lum=p95_lum,
        max_lum=max_lum,
        p95_contrast=p95_contrast,
        worst_contrast=worst_contrast,
        body_pass=body_pass,
        display_pass=display_pass,
        pass_=passed,
        detail=detail,
    )


def _generate_heatmap(composite: Image.Image, out_path: Path) -> Path:
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
    return out_path


# ============================================================================
# Check 5 — Side-by-side HTML comparison
# ============================================================================

CROP_REGIONS = [
    ("Peak / sunrise apex (top-center)", (0.30, 0.00, 0.70, 0.35)),
    ("Text-landing zone (center-left)",  (0.15, 0.30, 0.70, 0.70)),
    ("Mountain mid-face detail",         (0.30, 0.40, 0.70, 0.75)),
    ("Chroma-strip band (bottom)",       (0.00, 0.85, 1.00, 1.00)),
]


def _crop_normalized(img: Image.Image, region):
    x1, y1, x2, y2 = region
    w, h = img.size
    return img.crop((int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)))


def _lum_histogram(img: Image.Image, bins=50):
    arr = np.array(img.convert("RGB"))
    lum = (relative_luminance(arr) * 100).astype(np.int32)
    hist, _ = np.histogram(lum, bins=bins, range=(0, 100))
    return hist


def build_comparison_html(input_path: Path, baseline_path: Path, out_dir: Path,
                          fs: FileSizeResult, ch: ChromaResult,
                          sd: SubjectResult, ct: ContrastResult,
                          overall_pass: bool) -> Path:
    target = (1024, 768)
    base = Image.open(baseline_path).convert("RGB").resize(target, Image.LANCZOS)
    new = Image.open(input_path).convert("RGB").resize(target, Image.LANCZOS)
    base_path = out_dir / "baseline-display.jpg"
    new_path = out_dir / "new-display.jpg"
    base.save(base_path, "JPEG", quality=85)
    new.save(new_path, "JPEG", quality=85)

    # Crop strips at display size
    crops_html = ""
    for name, region in CROP_REGIONS:
        b_crop = _crop_normalized(base, region)
        n_crop = _crop_normalized(new, region)
        b_name = f"crop-base-{name.split()[0].lower()}.jpg"
        n_name = f"crop-new-{name.split()[0].lower()}.jpg"
        b_crop.save(out_dir / b_name, "JPEG", quality=85)
        n_crop.save(out_dir / n_name, "JPEG", quality=85)
        crops_html += (
            f'<div class="crop-row"><div class="crop-label">{name}</div>'
            f'<div class="crop-pair">'
            f'<div class="pane"><img src="{b_name}"></div>'
            f'<div class="pane"><img src="{n_name}"></div>'
            f'</div></div>\n'
        )

    base_hist = _lum_histogram(base)
    new_hist = _lum_histogram(new)
    max_count = max(int(base_hist.max()), int(new_hist.max()), 1)
    base_bars = "".join(
        f'<div class="bar" style="height:{int(h)/max_count*100:.1f}%"></div>'
        for h in base_hist
    )
    new_bars = "".join(
        f'<div class="bar" style="height:{int(h)/max_count*100:.1f}%"></div>'
        for h in new_hist
    )

    def verdict(v):
        return f'<span class="{"pass" if v else "fail"}">{"PASS" if v else "FAIL"}</span>'

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Flux-2-max v1 — Gate 9 validation</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1612; color: #f4ecd9;
         margin: 0; padding: 24px; line-height: 1.4; }}
  h1 {{ font-size: 1.4rem; margin-top: 0; }}
  h2 {{ font-size: 1rem; color: #c8a26b; margin: 28px 0 10px; text-transform: uppercase;
        letter-spacing: 0.05em; }}
  p {{ max-width: 72ch; opacity: 0.75; font-size: 0.9rem; }}
  .pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .pane {{ position: relative; }}
  .pane img {{ width: 100%; display: block; border: 1px solid #3a2f26; }}
  .pane .label {{ position: absolute; top: 8px; left: 8px; background: rgba(26,22,18,0.85);
                  padding: 4px 10px; font-size: 0.75rem; border: 1px solid #3a2f26; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.88rem; margin-bottom: 16px; }}
  th, td {{ text-align: left; padding: 8px 10px; border-bottom: 1px solid #3a2f26; }}
  th {{ color: #c8a26b; font-weight: 500; text-transform: uppercase; font-size: 0.75rem;
        letter-spacing: 0.06em; }}
  td.num {{ font-variant-numeric: tabular-nums; }}
  .pass {{ color: #82c082; font-weight: 600; }}
  .fail {{ color: #e07070; font-weight: 600; }}
  .hist {{ display: flex; align-items: flex-end; gap: 1px; height: 100px;
           background: rgba(255,255,255,0.03); padding: 8px; border: 1px solid #3a2f26; }}
  .hist .bar {{ flex: 1; min-height: 1px; }}
  .hist.base .bar {{ background: #8a9fb3; }}
  .hist.new .bar {{ background: #c8a26b; }}
  .legend {{ font-size: 0.8rem; opacity: 0.7; margin-top: 6px; }}
  .crop-row {{ margin-bottom: 16px; }}
  .crop-label {{ font-size: 0.85rem; color: #c8a26b; margin-bottom: 6px; }}
  .crop-pair {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .verdict-banner {{ padding: 12px 16px; margin: 16px 0 24px; border: 1px solid;
                     font-size: 1rem; letter-spacing: 0.05em; }}
  .verdict-banner.pass {{ border-color: #82c082; color: #82c082;
                          background: rgba(130,192,130,0.08); }}
  .verdict-banner.fail {{ border-color: #e07070; color: #e07070;
                          background: rgba(224,112,112,0.08); }}
</style>
</head>
<body>
<h1>Flux-2-max v1 — Gate 9 validation</h1>
<p>Baseline: flux-2-pro v4.2 (<code>{baseline_path.name}</code>). New: flux-2-max v1
(<code>{input_path.name}</code>). Side-by-side voor painterly kwaliteit, subject rendering,
chroma-strip integriteit, detail density in text-landing zone. Metrics below.</p>

<div class="verdict-banner {'pass' if overall_pass else 'fail'}">
  OVERALL: {'PASS — all gates green' if overall_pass else 'FAIL — one or more gates failed'}
</div>

<h2>Metrics</h2>
<table>
<tr><th>Criterion</th><th>Target</th><th>Measured</th><th>Verdict</th></tr>
<tr><td>WebP q82 @2x file size</td><td>≤ {MAX_WEBP_MB} MB</td>
    <td class="num">{fs.webp_mb:.2f} MB</td><td>{verdict(fs.pass_)}</td></tr>
<tr><td>Raw PNG (informational)</td><td>—</td>
    <td class="num">{fs.raw_mb:.2f} MB @ {fs.source_dimensions}</td><td>—</td></tr>
<tr><td>Chroma bottom-band coverage <span style="opacity:0.7">(informational — not binding)</span></td>
    <td>≥ {CHROMA_BAND_MIN_PCT}% = "clean" signal</td>
    <td class="num">{ch.bottom_band_coverage_pct:.1f}% (centroid y={ch.vertical_centroid_normalized:.2f}, sampled RGB{ch.sampled_rgb})</td>
    <td><span style="opacity:0.8">{('CLEAN' if ch.pass_ else 'MUTED')}</span></td></tr>
<tr><td>Subject-mass consistency vs baseline (Otsu)</td>
    <td>Δ within ±{SUBJECT_REL_TOLERANCE}pp</td>
    <td class="num">new {sd.subject_dominance_pct:.1f}%, baseline {sd.baseline_subject_dominance_pct:.1f}%, Δ {sd.delta_vs_baseline:+.1f}pp</td>
    <td>{verdict(sd.pass_)}</td></tr>
<tr><td style="opacity:0.7">↳ Visual 70–75% target (informational)</td>
    <td style="opacity:0.7">abs 65–80% range</td>
    <td class="num" style="opacity:0.7">{sd.subject_dominance_pct:.1f}% (Otsu method proxy; verify via full-frame comparison)</td>
    <td style="opacity:0.7">{'within' if sd.abs_pass else 'outside'} Otsu-proxy range</td></tr>
<tr><td>Composite + 55% scrim, p95 contrast (Gate 8)</td>
    <td>body ≥ {BODY_AA}:1</td>
    <td class="num">{ct.p95_contrast:.2f}:1 (worst-px {ct.worst_contrast:.2f}:1)</td>
    <td>{verdict(ct.body_pass)}</td></tr>
</table>

<h2>Full-frame side-by-side</h2>
<div class="pair">
  <div class="pane"><span class="label">Baseline · flux-2-pro v4.2</span><img src="{base_path.name}"></div>
  <div class="pane"><span class="label">New · flux-2-max v1</span><img src="{new_path.name}"></div>
</div>

<h2>Region crops</h2>
{crops_html}

<h2>Luminance distribution (non-weighted, full frame)</h2>
<div class="pair">
  <div>
    <div style="font-size:0.85rem;opacity:0.75;margin-bottom:6px">Baseline · flux-2-pro v4.2</div>
    <div class="hist base">{base_bars}</div>
  </div>
  <div>
    <div style="font-size:0.85rem;opacity:0.75;margin-bottom:6px">New · flux-2-max v1</div>
    <div class="hist new">{new_bars}</div>
  </div>
</div>
<div class="legend">50 bins, luminance 0 (dark) → 100 (light). Similar shapes = similar tonal palette.
Significant shift (e.g. new distribution pushed brighter) can indicate palette regression or loss
of shadow depth.</div>

<h2>Artifacts</h2>
<ul>
  <li>Subject-mask visualization: <a href="{Path(sd.mask_path).name}">{Path(sd.mask_path).name}</a></li>
  <li>Composite (pre-scrim): <a href="{Path(ct.composite_path).name}">{Path(ct.composite_path).name}</a></li>
  <li>Composite + 55% scrim: <a href="{Path(ct.scrim_composite_path).name}">{Path(ct.scrim_composite_path).name}</a></li>
  <li>Contrast heatmap: <a href="{Path(ct.heatmap_path).name}">{Path(ct.heatmap_path).name}</a></li>
  <li>WebP @2x: <a href="{Path(fs.webp_path).name}">{Path(fs.webp_path).name}</a></li>
</ul>

</body>
</html>"""
    html_path = out_dir / "flux2max-comparison.html"
    html_path.write_text(html, encoding="utf-8")
    return html_path


# ============================================================================
# Orchestrator
# ============================================================================

@dataclass
class FullReport:
    input_path: str
    baseline_path: str
    file_size: FileSizeResult
    chroma: ChromaResult
    subject: SubjectResult
    contrast: ContrastResult
    comparison_html: str
    overall_pass: bool

    def to_dict(self):
        return asdict(self)


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    p = argparse.ArgumentParser(description="Gate 9 validation harness for flux-2-max Apu output")
    p.add_argument("--input", default=str(DEFAULT_INPUT),
                   help=f"New flux-2-max mountain-face PNG (default: {DEFAULT_INPUT})")
    p.add_argument("--baseline", default=str(DEFAULT_BASELINE),
                   help=f"Baseline flux-2-pro v4.2 reference (default: {DEFAULT_BASELINE})")
    args = p.parse_args()

    input_path = _resolve_input(Path(args.input))
    baseline_path = _resolve_input(Path(args.baseline))

    if not input_path.exists():
        print(f"ERROR: input file not found: {args.input}")
        print(f"Tried .png/.jpg/.jpeg/.webp for stem '{Path(args.input).stem}'.")
        print(f"Place the flux-2-max output (any image format) at: {DEFAULT_INPUT.with_suffix('.{png|jpg}')}")
        raise SystemExit(1)
    if not baseline_path.exists():
        print(f"ERROR: baseline file not found: {args.baseline}")
        raise SystemExit(1)
    if not PLATEAU_LAYER.exists() or not FRAMING_LAYER.exists():
        print(f"ERROR: existing plateau/framing layers missing; run scripts/process_apu.py first")
        raise SystemExit(1)

    OUT.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Gate 9 validation — flux-2-max v1")
    print(f"Input:    {input_path}")
    print(f"Baseline: {baseline_path}")
    print(f"Output:   {OUT}")
    print("=" * 70)

    print("\n[1/5] File-size check (raw PNG + WebP q82 @2x)")
    fs = check_file_size(input_path, OUT)
    print(f"   {fs.detail}")
    print(f"   Verdict: {'PASS' if fs.pass_ else 'FAIL'}")

    print("\n[2/5] Chroma-strip integrity")
    ch = check_chroma_strip(input_path)
    print(f"   {ch.detail}")
    print(f"   Verdict: {'PASS' if ch.pass_ else 'FAIL'}")

    print("\n[3/5] Subject-dominance (Otsu non-chroma, abs + rel vs baseline)")
    sd = check_subject_dominance(input_path, baseline_path, OUT)
    print(f"   {sd.detail}")
    print(f"   Verdict: {'PASS' if sd.pass_ else 'FAIL'}")

    print("\n[4/5] Composite + Gate 8 p95 contrast on 55% scrim")
    ct = check_contrast(input_path, OUT)
    print(f"   {ct.detail}")
    print(f"   Verdict: {'PASS' if ct.pass_ else 'FAIL'}")

    print("\n[5/5] Side-by-side HTML comparison")
    # Chroma is informational, not binding (v4.2 baseline was accepted without clean chroma).
    # Binding gates: file-size (production-critical), subject-mass consistency, Gate 8 contrast.
    overall = fs.pass_ and sd.pass_ and ct.pass_
    html_path = build_comparison_html(input_path, baseline_path, OUT,
                                       fs, ch, sd, ct, overall)
    print(f"   {html_path}")

    report = FullReport(
        input_path=str(input_path),
        baseline_path=str(baseline_path),
        file_size=fs,
        chroma=ch,
        subject=sd,
        contrast=ct,
        comparison_html=str(html_path),
        overall_pass=overall,
    )
    report_json = OUT / "flux2max-report.json"
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, default=str)

    print()
    print("=" * 70)
    print(f"OVERALL: {'PASS — all gates green' if overall else 'FAIL — one or more gates failed'}")
    print(f"  1. File size        : {'PASS' if fs.pass_ else 'FAIL'}    (binding)         {fs.webp_mb:.2f} MB WebP q82")
    print(f"  2. Chroma strip     : {'CLEAN' if ch.pass_ else 'MUTED'}  (informational)   {ch.bottom_band_coverage_pct:.1f}% band")
    print(f"  3. Subject-mass rel : {'PASS' if sd.pass_ else 'FAIL'}    (binding)         {sd.subject_dominance_pct:.1f}%, Δ {sd.delta_vs_baseline:+.1f}pp vs baseline")
    print(f"  4. Gate 8 contrast  : {'PASS' if ct.pass_ else 'FAIL'}    (binding)         {ct.p95_contrast:.2f}:1 p95")
    print("=" * 70)
    print(f"Report JSON:      {report_json}")
    print(f"Comparison HTML:  {html_path}")
    print(f"All artefacts in: {OUT}")
    raise SystemExit(0 if overall else 2)


if __name__ == "__main__":
    main()
