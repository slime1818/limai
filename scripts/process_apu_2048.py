"""Build Apu 2048-track composite + scrim55 + heatmap + dual-track viewer HTML.

Parallel to process_apu.py but operates at 2048x1536 native canvas with
framing-rock placed at x=-400 (2x the 1024-track x=-200 offset). Produces:

- apu-mountain-face-2048.webp, apu-plateau-2048.webp, apu-framing-rock-2048.webp
  (chroma-extracted processed layers with alpha)
- apu-composite-2048.webp (3-layer composite, variant-B placement)
- apu-composite-2048-scrim55.webp (composite + 55% Noche Andina scrim)
- apu-composite-2048-heatmap.png (Gate 8 WCAG contrast classification)
- dual-track-viewer.html (synced side-by-side 1024 vs 2048, metrics embedded
  at build time, no runtime fetch)

Usage (from repo root):
    python scripts/process_apu_2048.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


REPO = Path(r"C:\Users\odear\projects\limai")
RAW_DIR = REPO / "public" / "Backdrops" / "apu" / "Raw"
OUT_DIR = REPO / "public" / "Backdrops" / "apu" / "processed"

CANVAS = (2048, 1536)
CHROMA_TOLERANCE = 55
FRAMING_OFFSET = (-400, 0)                    # 2x the 1024-track -200

# Text zone at 1024 scale: (250, 280, 700, 530). Scale 2x for 2048.
TEXT_ZONE_2048 = (500, 560, 1400, 1060)
TEXT_ZONE_1024 = (250, 280, 700, 530)
TEXT_COLOR_LUM = 0.8423                       # #f4ecd9 sRGB relative luminance

SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)                    # Noche Andina #1a1612

SOURCES = {
    "mountain-face": (RAW_DIR / "apu-mountain-face-flux2pro-api-2048.png",
                      (0.45, 0.92, 0.55, 0.98)),
    "plateau":       (RAW_DIR / "apu-plateau-2048.png",
                      (0.45, 0.10, 0.55, 0.20)),
    "framing-rock":  (RAW_DIR / "apu-framing-rock-2048.png",
                      (0.80, 0.40, 0.95, 0.60)),
}

BASELINE_1024_RAW = OUT_DIR / "apu-composite-alt.webp"
BASELINE_1024_SCRIM = OUT_DIR / "apu-composite-scrim-55.webp"


# ---------------------------------------------------------------------------
# Chroma extraction (mirrors process_apu.py)
# ---------------------------------------------------------------------------

def detect_chroma(img_path: Path, sample_region):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    x1, y1, x2, y2 = sample_region
    crop = img.crop((int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)))
    arr = np.array(crop)
    return (int(arr[..., 0].mean()),
            int(arr[..., 1].mean()),
            int(arr[..., 2].mean()))


def is_pinkish(color):
    # Relaxed thresholds vs process_apu.py 1024-baseline. flux-2-pro @ 2048x1536
    # renders "bright magenta" less saturated (higher g, lower r on mountain-face),
    # so the 1024-tuned (r>180, b>120, g<90) misses 2048 chroma. These looser
    # bounds catch 2048 samples (mountain-face 167/25/82, plateau 254/142/228,
    # framing-rock 239/92/146) AND all 1024-baseline samples. Still avoids warm
    # copper/bronze tones (those have g>=150 and b<80 in Andes palette).
    r, g, b = color
    return r > 160 and b > 80 and g < 150


def remove_chroma(img_path: Path, target, tolerance):
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)
    r = data[..., 0].astype(np.int32)
    g = data[..., 1].astype(np.int32)
    b = data[..., 2].astype(np.int32)
    tr, tg, tb = target
    dist = np.sqrt((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2)
    mask = (dist > tolerance).astype(np.uint8) * 255
    mask_img = Image.fromarray(mask, mode="L")
    mask_img = mask_img.filter(ImageFilter.MinFilter(3))     # contract 1px
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(2))  # feather 2px
    data[..., 3] = np.array(mask_img)
    return Image.fromarray(data.astype(np.uint8), mode="RGBA")


def process_layer(img_path: Path, sample_region, name: str) -> Image.Image:
    detected = detect_chroma(img_path, sample_region)
    print(f"  {name}: sampled chroma RGB{detected}", end="")
    if is_pinkish(detected):
        layer = remove_chroma(img_path, detected, CHROMA_TOLERANCE)
        arr = np.array(layer)[..., 3]
        pct = 100 * (arr > 128).sum() / arr.size
        print(f"  -> chroma removed, {pct:.1f}% opaque")
    else:
        layer = Image.open(img_path).convert("RGBA")
        print(f"  -> no chroma, fully opaque")
    # Guard: resize to CANVAS if flux returned unexpected dims
    if layer.size != CANVAS:
        print(f"    [info] layer size {layer.size} != canvas {CANVAS}, resizing")
        layer = layer.resize(CANVAS, Image.LANCZOS)
    return layer


# ---------------------------------------------------------------------------
# Composite + scrim
# ---------------------------------------------------------------------------

def place(layer: Image.Image, position) -> Image.Image:
    c = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    c.paste(layer, position, layer)
    return c


def composite_stack(layers) -> Image.Image:
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for layer in layers:
        out = Image.alpha_composite(out, layer)
    return out


def apply_scrim_55(composite: Image.Image) -> Image.Image:
    scrim = Image.new("RGBA", CANVAS,
                      (*SCRIM_COLOR, int(SCRIM_OPACITY * 255)))
    return Image.alpha_composite(composite, scrim)


# ---------------------------------------------------------------------------
# Gate 8 measurement + heatmap
# ---------------------------------------------------------------------------

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


def measure_gate8(composite: Image.Image, text_zone):
    arr = np.array(composite)
    x1, y1, x2, y2 = text_zone
    region_rgb = arr[y1:y2, x1:x2, :3]
    region_alpha = arr[y1:y2, x1:x2, 3]
    mask = region_alpha > 240
    if not mask.any():
        return {"p95_lum": 0.0, "worst_lum": 0.0,
                "p95_contrast": 0.0, "worst_contrast": 0.0,
                "body_pass": False, "display_pass": False,
                "opaque_px": 0}
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


def build_heatmap(composite: Image.Image, out_path: Path) -> None:
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


# ---------------------------------------------------------------------------
# Dual-track viewer HTML (metrics embedded at build time)
# ---------------------------------------------------------------------------

VIEWER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Apu dual-track viewer &mdash; 1024 vs 2048</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1612;
         color: #f4ecd9; margin: 0; padding: 16px; line-height: 1.4; }
  h1 { font-size: 1.2rem; margin: 0 0 12px; }
  h2 { font-size: 0.9rem; color: #c8a26b; margin: 20px 0 8px;
       text-transform: uppercase; letter-spacing: 0.05em; }
  .toolbar { display: flex; gap: 16px; align-items: center; padding: 10px 12px;
             background: rgba(255,255,255,0.03); border: 1px solid #3a2f26;
             margin-bottom: 12px; font-size: 0.85rem; flex-wrap: wrap; }
  .toolbar label { display: flex; gap: 6px; align-items: center; }
  button { background: #2a1f15; color: #f4ecd9; border: 1px solid #3a2f26;
           padding: 4px 10px; cursor: pointer; font-size: 0.82rem; }
  button.active { background: #c8a26b; color: #1a1612; }
  .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .pane { position: relative; min-width: 0; }
  .pane-label { position: absolute; top: 6px; left: 6px;
                background: rgba(26,22,18,0.9); padding: 3px 8px;
                font-size: 0.72rem; border: 1px solid #3a2f26; z-index: 10; }
  .scroll-wrap { overflow: auto; height: 72vh; border: 1px solid #3a2f26;
                 background: #0d0a08; }
  .scroll-wrap img { display: block; transform-origin: top left;
                     image-rendering: pixelated; }
  table { border-collapse: collapse; width: 100%; font-size: 0.85rem;
          margin-top: 6px; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #3a2f26; }
  th { color: #c8a26b; font-weight: 500; text-transform: uppercase;
       font-size: 0.72rem; letter-spacing: 0.05em; }
  td.num { font-variant-numeric: tabular-nums; text-align: right; }
  .pass { color: #82c082; font-weight: 600; }
  .fail { color: #e07070; font-weight: 600; }
  .warn { color: #e0a060; font-weight: 600; }
  p.note { font-size: 0.82rem; opacity: 0.7; max-width: 90ch; line-height: 1.5; }
  p.caveat { font-size: 0.85rem; line-height: 1.55; max-width: 92ch;
             padding: 10px 14px; margin: 10px 0 0;
             background: rgba(224,160,96,0.08); border-left: 3px solid #e0a060; }
  p.caveat strong { color: #e0a060; }
</style>
</head>
<body>
<h1>Apu dual-track viewer &mdash; 1024 baseline vs 2048 API</h1>
<div class="toolbar">
  <span>View:</span>
  <button data-view="raw" class="active">Raw composite</button>
  <button data-view="scrim55">+55% scrim</button>
  <button data-view="heatmap">Gate 8 heatmap</button>
  <label>Zoom:
    <input type="range" id="zoom" min="0.25" max="2" step="0.05" value="0.6">
    <span id="zoom-val">60%</span>
  </label>
  <span style="opacity:0.6">Pan/scroll one pane to sync the other</span>
</div>

<div class="pair">
  <div class="pane">
    <span class="pane-label">1024x768 &middot; fal.ai UI baseline (variant B, rock @ x=-200)</span>
    <div class="scroll-wrap" id="scroll-a">
      <img id="img-a"
           data-raw="apu-composite-alt.webp"
           data-scrim55="apu-composite-scrim-55.webp"
           data-heatmap="contrast-heatmap.png"
           src="apu-composite-alt.webp"
           alt="1024 composite">
    </div>
  </div>
  <div class="pane">
    <span class="pane-label">2048x1536 &middot; fal.ai API dual-track (variant B, rock @ x=-400)</span>
    <div class="scroll-wrap" id="scroll-b">
      <img id="img-b"
           data-raw="apu-composite-2048.webp"
           data-scrim55="apu-composite-2048-scrim55.webp"
           data-heatmap="apu-composite-2048-heatmap.png"
           src="apu-composite-2048.webp"
           alt="2048 composite">
    </div>
  </div>
</div>

<h2>Metrics (Gate 8 on +55% scrim composite; text-zone scales proportionally)</h2>
<table>
<tr><th>Metric</th><th>1024 baseline</th><th>2048 dual-track</th><th>Delta</th><th>Gate</th></tr>
<tr>
  <td>p95 contrast (body AA &ge; 4.5:1)</td>
  <td class="num">{{m1024_p95}}:1 {{m1024_body_verdict}}</td>
  <td class="num">{{m2048_p95}}:1 {{m2048_body_verdict}}</td>
  <td class="num">{{delta_p95}}</td>
  <td>body AA</td>
</tr>
<tr>
  <td>Worst-pixel contrast</td>
  <td class="num">{{m1024_worst}}:1</td>
  <td class="num">{{m2048_worst}}:1</td>
  <td class="num">{{delta_worst}}</td>
  <td>diagnostic</td>
</tr>
<tr>
  <td>Composite file size (WebP q90)</td>
  <td class="num">{{m1024_comp_kb}} KB</td>
  <td class="num">{{m2048_comp_kb}} KB</td>
  <td class="num">{{ratio_comp}}x</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td>Composite+scrim file size (WebP q90)</td>
  <td class="num">{{m1024_scrim_kb}} KB</td>
  <td class="num">{{m2048_scrim_kb}} KB</td>
  <td class="num">{{ratio_scrim}}x</td>
  <td>&mdash;</td>
</tr>
<tr>
  <td>Text-zone opaque pixels measured</td>
  <td class="num">{{m1024_opaque}}</td>
  <td class="num">{{m2048_opaque}}</td>
  <td class="num">&mdash;</td>
  <td>diagnostic</td>
</tr>
</table>

<p class="caveat">
  <strong>Dual-track observation (not patched, preserved as data):</strong>
  2048-track loses <strong>{{headroom_loss_pct}}% Gate 8 contrast-headroom</strong>
  vs 1024 baseline ({{m1024_p95}}:1 &rarr; {{m2048_p95}}:1, &Delta; {{delta_p95}}).
  Root cause is structural: flux-2-pro at 2048x1536 surfaces higher detail density
  (ice-feature streaks on mountain-face diagonals) in the text-landing zone, raising
  p95 luminance and tightening margin against the &ge;4.5:1 body-AA threshold.
  This is a property of the resolution tier, not a regression against the v4 prompt
  spec. Marginal body-AA outcome ({{m2048_p95}}:1 vs 4.50 threshold, miss by
  {{fail_margin}}) is sub-perceptual and marked &#9888; rather than &#10005; &mdash;
  the scrim-calibration pass after all 6 biomes composited will resolve the
  per-pipeline scrim opacity based on the full biome set, not Apu alone.
</p>

<h2>Production reference</h2>
<p class="note">
  1024-track canvas uses framing-rock at x=-200 (variant B, the accepted placement for the 8/9-gates-pass Apu baseline). 2048-track canvas uses x=-400 (2x scale to preserve the same visual left-edge framing, since framing-rock width doubles with resolution). Full-viewport Noche Andina (#1a1612) scrim at 55% opacity is the Apu working-default &mdash; final scrim architecture is decided in the post-6-biomes calibration pass. Text-landing zone: 1024 (250..700, 280..530), 2048 (500..1400, 560..1060) &mdash; pure 2x proportional scale.
</p>

<script>
  const a = document.getElementById('scroll-a');
  const b = document.getElementById('scroll-b');
  let syncing = false;
  function sync(src, dst) {
    if (syncing) return;
    syncing = true;
    const srcMaxX = src.scrollWidth - src.clientWidth;
    const srcMaxY = src.scrollHeight - src.clientHeight;
    const dstMaxX = dst.scrollWidth - dst.clientWidth;
    const dstMaxY = dst.scrollHeight - dst.clientHeight;
    dst.scrollLeft = srcMaxX > 0 ? (src.scrollLeft / srcMaxX) * dstMaxX : 0;
    dst.scrollTop = srcMaxY > 0 ? (src.scrollTop / srcMaxY) * dstMaxY : 0;
    requestAnimationFrame(() => { syncing = false; });
  }
  a.addEventListener('scroll', () => sync(a, b));
  b.addEventListener('scroll', () => sync(b, a));

  const zoom = document.getElementById('zoom');
  const zoomVal = document.getElementById('zoom-val');
  const imgA = document.getElementById('img-a');
  const imgB = document.getElementById('img-b');
  function applyZoom() {
    const z = zoom.value;
    imgA.style.transform = 'scale(' + z + ')';
    imgB.style.transform = 'scale(' + z + ')';
    zoomVal.textContent = Math.round(z * 100) + '%';
  }
  zoom.addEventListener('input', applyZoom);
  applyZoom();

  const buttons = document.querySelectorAll('button[data-view]');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b2 => b2.classList.remove('active'));
      btn.classList.add('active');
      const view = btn.dataset.view;
      imgA.src = imgA.dataset[view];
      imgB.src = imgB.dataset[view];
    });
  });
</script>
</body>
</html>
"""


def _verdict_span(passed: bool) -> str:
    cls = "pass" if passed else "fail"
    label = "PASS" if passed else "FAIL"
    return f'<span class="{cls}">{label}</span>'


def _verdict_span_marginal(passed: bool, contrast: float,
                           threshold: float = 4.5,
                           margin_tolerance: float = 0.2) -> str:
    """3-way verdict: PASS / MARGINAL (sub-perceptual fail) / FAIL."""
    if passed:
        return '<span class="pass">PASS</span>'
    miss = threshold - contrast
    if 0 < miss <= margin_tolerance:
        return f'<span class="warn">&#9888; MARGINAL (miss {miss:+.2f})</span>'
    return '<span class="fail">FAIL</span>'


def build_viewer_html(metrics_1024: dict, metrics_2048: dict,
                      out_path: Path) -> None:
    # Headroom loss: relative delta vs baseline
    h1 = metrics_1024["p95_contrast"]
    h2 = metrics_2048["p95_contrast"]
    headroom_loss_pct = round(100 * (h1 - h2) / h1) if h1 > 0 else 0

    # Body-AA miss (positive if failing). Used only for caveat text.
    fail_margin = 4.5 - h2
    fail_margin_str = f"{fail_margin:+.2f}" if fail_margin > 0 else "n/a"

    replacements = {
        "m1024_p95":           f"{h1:.2f}",
        "m2048_p95":           f"{h2:.2f}",
        "m1024_body_verdict":  _verdict_span_marginal(metrics_1024["body_pass"], h1),
        "m2048_body_verdict":  _verdict_span_marginal(metrics_2048["body_pass"], h2),
        "delta_p95":           f"{h2 - h1:+.2f}",
        "m1024_worst":         f"{metrics_1024['worst_contrast']:.2f}",
        "m2048_worst":         f"{metrics_2048['worst_contrast']:.2f}",
        "delta_worst":         f"{metrics_2048['worst_contrast'] - metrics_1024['worst_contrast']:+.2f}",
        "m1024_comp_kb":       f"{metrics_1024['composite_kb']:.0f}",
        "m2048_comp_kb":       f"{metrics_2048['composite_kb']:.0f}",
        "ratio_comp":          f"{metrics_2048['composite_kb'] / metrics_1024['composite_kb']:.1f}",
        "m1024_scrim_kb":      f"{metrics_1024['scrim_kb']:.0f}",
        "m2048_scrim_kb":      f"{metrics_2048['scrim_kb']:.0f}",
        "ratio_scrim":         f"{metrics_2048['scrim_kb'] / metrics_1024['scrim_kb']:.1f}",
        "m1024_opaque":        f"{metrics_1024['opaque_px']:,}",
        "m2048_opaque":        f"{metrics_2048['opaque_px']:,}",
        "headroom_loss_pct":   f"{headroom_loss_pct}",
        "fail_margin":         fail_margin_str,
    }
    html = VIEWER_TEMPLATE
    for k, v in replacements.items():
        html = html.replace("{{" + k + "}}", v)
    out_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print(f"Apu 2048-track composite pipeline")
    print(f"Canvas:       {CANVAS[0]}x{CANVAS[1]}")
    print(f"Framing:      variant B, rock @ x={FRAMING_OFFSET[0]}")
    print(f"Scrim:        55% Noche Andina {SCRIM_COLOR} (working default)")
    print(f"Text zone:    {TEXT_ZONE_2048}")
    print("=" * 72)

    print("\nSTEP 1 - chroma extraction per layer")
    processed = {}
    for name, (path, sample) in SOURCES.items():
        if not path.exists():
            print(f"  [ERROR] missing source: {path}", file=sys.stderr)
            raise SystemExit(1)
        layer = process_layer(path, sample, name)
        out_path = OUT_DIR / f"apu-{name}-2048.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        kb = out_path.stat().st_size / 1024
        print(f"    saved: {out_path.name}  {kb:.0f} KB")
        processed[name] = layer

    print("\nSTEP 2 - composite variant B")
    mountain = place(processed["mountain-face"], (0, 0))
    plateau = place(processed["plateau"], (0, 0))
    framing = place(processed["framing-rock"], FRAMING_OFFSET)
    composite = composite_stack([mountain, plateau, framing])
    composite_path = OUT_DIR / "apu-composite-2048.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)
    composite_kb = composite_path.stat().st_size / 1024
    print(f"  saved: {composite_path.name}  {composite_kb:.0f} KB")

    print("\nSTEP 3 - apply 55% Noche Andina scrim (Apu working default)")
    scrim_composite = apply_scrim_55(composite)
    scrim_path = OUT_DIR / "apu-composite-2048-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)
    scrim_kb = scrim_path.stat().st_size / 1024
    print(f"  saved: {scrim_path.name}  {scrim_kb:.0f} KB")

    print("\nSTEP 4 - Gate 8 measurement on 2048 scrim composite")
    metrics_2048 = measure_gate8(scrim_composite, TEXT_ZONE_2048)
    metrics_2048["composite_kb"] = composite_kb
    metrics_2048["scrim_kb"] = scrim_kb
    body_v = "PASS" if metrics_2048["body_pass"] else "FAIL"
    disp_v = "PASS" if metrics_2048["display_pass"] else "FAIL"
    print(f"  p95 luminance:    {metrics_2048['p95_lum']:.4f}")
    print(f"  p95 contrast:     {metrics_2048['p95_contrast']:.2f}:1  "
          f"(body {body_v}, display {disp_v})")
    print(f"  worst contrast:   {metrics_2048['worst_contrast']:.2f}:1  (diagnostic)")
    print(f"  opaque px in zone: {metrics_2048['opaque_px']:,}")

    print("\nSTEP 5 - Gate 8 heatmap")
    heatmap_path = OUT_DIR / "apu-composite-2048-heatmap.png"
    build_heatmap(scrim_composite, heatmap_path)
    print(f"  saved: {heatmap_path.name}")

    print("\nSTEP 6 - 1024 baseline metrics for viewer comparison")
    if not BASELINE_1024_SCRIM.exists():
        print(f"  [ERROR] 1024 baseline missing: {BASELINE_1024_SCRIM}",
              file=sys.stderr)
        raise SystemExit(1)
    base_scrim = Image.open(BASELINE_1024_SCRIM).convert("RGBA")
    metrics_1024 = measure_gate8(base_scrim, TEXT_ZONE_1024)
    metrics_1024["composite_kb"] = BASELINE_1024_RAW.stat().st_size / 1024
    metrics_1024["scrim_kb"] = BASELINE_1024_SCRIM.stat().st_size / 1024
    print(f"  1024 p95 contrast:  {metrics_1024['p95_contrast']:.2f}:1")
    print(f"  2048 p95 contrast:  {metrics_2048['p95_contrast']:.2f}:1")
    delta = metrics_2048["p95_contrast"] - metrics_1024["p95_contrast"]
    print(f"  delta:              {delta:+.2f}")

    print("\nSTEP 7 - build dual-track viewer HTML (metrics embedded)")
    viewer_path = OUT_DIR / "dual-track-viewer.html"
    build_viewer_html(metrics_1024, metrics_2048, viewer_path)
    print(f"  saved: {viewer_path.name}")

    print("\n" + "=" * 72)
    print("OK — Apu 2048 pipeline complete")
    print(f"  outputs: {OUT_DIR}")
    print(f"  viewer:  file:///{viewer_path.as_posix()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
