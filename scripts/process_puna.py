"""Chroma-key extraction + composite for Puna v4 layers (1024 UI pipeline).

Mirrors process_apu.py pattern: 1024x768 canvas, variant-B framing-rock
placement at x=-200, chroma-key extraction per layer using sample regions,
composite output + scrim-55 + Gate 8 heatmap + p95-contrast measurement.

Uses STRICT is_pinkish thresholds (same as process_apu.py). The relaxed
bounds from process_apu_2048.py are for the abandoned 2048-track pipeline;
at 1024 UI preset flux-2-pro renders cleaner chroma that passes the strict
check (per Apu baseline evidence: framing-rock 251/5/184, plateau 218/57/150).

Text zone slightly LEFT-shifted vs Apu per project_limai memory
(Puna text-safe zone = "left", Apu was "central-left").

Expected sources (fal.ai UI outputs, JPG, 1024x768):
  public/Backdrops/puna/Raw/puna-sky-subject.jpg
  public/Backdrops/puna/Raw/puna-plateau.jpg
  public/Backdrops/puna/Raw/puna-framing-rock.jpg

Usage (from repo root, after all 3 layers downloaded):
  python scripts/process_puna.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


REPO = Path(r"C:\Users\odear\projects\limai")
RAW_DIR = REPO / "public" / "Backdrops" / "puna" / "Raw"
OUT_DIR = REPO / "public" / "Backdrops" / "puna" / "processed"

CANVAS = (1024, 768)
CHROMA_TOLERANCE = 55
FRAMING_OFFSET = (-200, 0)

# Text zone left-shifted vs Apu (250,280,700,530) per biome text-safe spec
TEXT_ZONE = (180, 280, 630, 530)
TEXT_COLOR_LUM = 0.8423

SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)  # Noche Andina

SOURCES = {
    # sky-subject sample narrowed to 0.96-1.00 to hit the actual chroma strip
    # (Puna sky-subject rendered chroma ~5-8% of frame, not 10% as in spec).
    "sky-subject":  (RAW_DIR / "puna-sky-subject.jpg",  (0.45, 0.96, 0.55, 1.00)),
    "plateau":      (RAW_DIR / "puna-plateau.jpg",      (0.45, 0.10, 0.55, 0.20)),
    "framing-rock": (RAW_DIR / "puna-framing-rock.jpg", (0.80, 0.40, 0.95, 0.60)),
}


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
    # Relaxed bounds vs process_apu.py 1024-strict. Puna empirical evidence
    # (plateau RGB 217/0/113 fails strict b>120; sky-subject chroma strip is
    # narrower than spec so averaging muddies the sample). Relaxed bounds
    # match process_apu_2048.py and catch Puna plateau; sky-subject uses a
    # narrower sample region below instead of further relaxation.
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
    mask_img = mask_img.filter(ImageFilter.MinFilter(3))
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(2))
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
    if layer.size != CANVAS:
        print(f"    [info] layer size {layer.size} != canvas {CANVAS}, resizing")
        layer = layer.resize(CANVAS, Image.LANCZOS)
    return layer


def place(layer: Image.Image, position) -> Image.Image:
    c = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    c.paste(layer, position, layer)
    return c


def composite_stack(layers) -> Image.Image:
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


def apply_scrim_55(composite: Image.Image) -> Image.Image:
    scrim = Image.new("RGBA", CANVAS,
                      (*SCRIM_COLOR, int(SCRIM_OPACITY * 255)))
    return Image.alpha_composite(composite, scrim)


def measure_gate8(composite: Image.Image, text_zone):
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


CROSS_BIOME_VIEWER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cross-biome style cohesion &mdash; Apu vs Puna</title>
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
  p.note { font-size: 0.82rem; opacity: 0.7; max-width: 90ch; line-height: 1.5; }
</style>
</head>
<body>
<h1>Cross-biome style cohesion &mdash; Apu (biome 1) vs Puna (biome 2)</h1>
<div class="toolbar">
  <span>View:</span>
  <button data-view="raw" class="active">Raw composite</button>
  <button data-view="scrim55">+55% scrim</button>
  <button data-view="heatmap">Gate 8 heatmap</button>
  <label>Zoom:
    <input type="range" id="zoom" min="0.25" max="2" step="0.05" value="0.8">
    <span id="zoom-val">80%</span>
  </label>
  <span style="opacity:0.6">Pan/scroll one pane to sync the other</span>
</div>

<div class="pair">
  <div class="pane">
    <span class="pane-label">Apu &middot; biome 1 &middot; LEFT framing cliff</span>
    <div class="scroll-wrap" id="scroll-a">
      <img id="img-a"
           data-raw="apu/processed/apu-composite-alt.webp"
           data-scrim55="apu/processed/apu-composite-scrim-55.webp"
           data-heatmap="apu/processed/apu-composite-scrim-55-heatmap.png"
           src="apu/processed/apu-composite-alt.webp"
           alt="Apu composite">
    </div>
  </div>
  <div class="pane">
    <span class="pane-label">Puna &middot; biome 2 &middot; LEFT framing outcrop (Pad C locked)</span>
    <div class="scroll-wrap" id="scroll-b">
      <img id="img-b"
           data-raw="puna/processed/puna-composite.webp"
           data-scrim55="puna/processed/puna-composite-scrim55.webp"
           data-heatmap="puna/processed/puna-composite-heatmap.png"
           src="puna/processed/puna-composite.webp"
           alt="Puna composite">
    </div>
  </div>
</div>

<h2>Metrics (Gate 8 on +55% scrim composite, per-biome text-zone)</h2>
<table>
<tr><th>Metric</th><th>Apu (biome 1)</th><th>Puna (biome 2)</th><th>Delta</th></tr>
<tr>
  <td>p95 contrast (body AA &ge; 4.5:1)</td>
  <td class="num">{{apu_p95}}:1 {{apu_body_verdict}}</td>
  <td class="num">{{puna_p95}}:1 {{puna_body_verdict}}</td>
  <td class="num">{{delta_p95}}</td>
</tr>
<tr>
  <td>Worst-pixel contrast (diagnostic)</td>
  <td class="num">{{apu_worst}}:1</td>
  <td class="num">{{puna_worst}}:1</td>
  <td class="num">{{delta_worst}}</td>
</tr>
<tr>
  <td>Composite file size (WebP q90)</td>
  <td class="num">{{apu_comp_kb}} KB</td>
  <td class="num">{{puna_comp_kb}} KB</td>
  <td class="num">{{delta_comp_kb}}%</td>
</tr>
<tr>
  <td>Composite+scrim file size (WebP q90)</td>
  <td class="num">{{apu_scrim_kb}} KB</td>
  <td class="num">{{puna_scrim_kb}} KB</td>
  <td class="num">{{delta_scrim_kb}}%</td>
</tr>
<tr>
  <td>Text-zone opaque pixels (diagnostic)</td>
  <td class="num">{{apu_opaque}}</td>
  <td class="num">{{puna_opaque}}</td>
  <td class="num">&mdash;</td>
</tr>
</table>

<h2>Reference</h2>
<p class="note">
  Both biomes at 1024&times;768 native (fal.ai UI flux-2-pro). Scrim: 55% Noche Andina (#1a1612) full-viewport, working default for biomes 1-4 until calibration-pass after biome 6. Framing: Pad C locks Apu+Puna at LEFT (cliff + rock outcrop respectively); Yungas/Selva/Paracas/Pac&iacute;fico positions TBD per user-approval at prompt-authoring time. Text-zones: Apu (250..700, 280..530) central-left; Puna (180..630, 280..530) left-shifted per biome text-safe spec. Puna sky-subject layer carries cross-biome overlap zones (top 15% Apu-handoff with distant snow-topped peaks; lower-middle 15% Yungas-hint with cloud-forest mist wisps).
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


def build_cross_biome_viewer(apu_metrics: dict, puna_metrics: dict,
                              out_path: Path) -> None:
    def pct_ratio(a, b):
        if a <= 0:
            return "n/a"
        return f"{(b / a - 1) * 100:+.0f}"

    replacements = {
        "apu_p95":          f"{apu_metrics['p95_contrast']:.2f}",
        "puna_p95":         f"{puna_metrics['p95_contrast']:.2f}",
        "apu_body_verdict": _verdict_span(apu_metrics["body_pass"]),
        "puna_body_verdict": _verdict_span(puna_metrics["body_pass"]),
        "delta_p95":        f"{puna_metrics['p95_contrast'] - apu_metrics['p95_contrast']:+.2f}",
        "apu_worst":        f"{apu_metrics['worst_contrast']:.2f}",
        "puna_worst":       f"{puna_metrics['worst_contrast']:.2f}",
        "delta_worst":      f"{puna_metrics['worst_contrast'] - apu_metrics['worst_contrast']:+.2f}",
        "apu_comp_kb":      f"{apu_metrics['composite_kb']:.0f}",
        "puna_comp_kb":     f"{puna_metrics['composite_kb']:.0f}",
        "delta_comp_kb":    pct_ratio(apu_metrics["composite_kb"], puna_metrics["composite_kb"]),
        "apu_scrim_kb":     f"{apu_metrics['scrim_kb']:.0f}",
        "puna_scrim_kb":    f"{puna_metrics['scrim_kb']:.0f}",
        "delta_scrim_kb":   pct_ratio(apu_metrics["scrim_kb"], puna_metrics["scrim_kb"]),
        "apu_opaque":       f"{apu_metrics['opaque_px']:,}",
        "puna_opaque":      f"{puna_metrics['opaque_px']:,}",
    }
    html = CROSS_BIOME_VIEWER_TEMPLATE
    for k, v in replacements.items():
        html = html.replace("{{" + k + "}}", v)
    out_path.write_text(html, encoding="utf-8")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    missing = [path for _, (path, _) in SOURCES.items() if not path.exists()]
    if missing:
        print("ERROR: missing Puna source layers:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        print("Download all 3 layers from fal.ai UI before running.",
              file=sys.stderr)
        raise SystemExit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Puna 1024 pipeline")
    print(f"Canvas:       {CANVAS[0]}x{CANVAS[1]}")
    print(f"Framing:      variant B, rock @ x={FRAMING_OFFSET[0]}")
    print(f"Scrim:        55% Noche Andina (working default)")
    print(f"Text zone:    {TEXT_ZONE}  (left-shifted vs Apu central-left)")
    print("=" * 72)

    print("\nSTEP 1 - chroma extraction per layer")
    processed = {}
    for name, (path, sample) in SOURCES.items():
        layer = process_layer(path, sample, name)
        out_path = OUT_DIR / f"puna-{name}.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        kb = out_path.stat().st_size / 1024
        print(f"    saved: {out_path.name}  {kb:.0f} KB")
        processed[name] = layer

    print("\nSTEP 2 - composite variant B")
    sky = place(processed["sky-subject"], (0, 0))
    plateau = place(processed["plateau"], (0, 0))
    framing = place(processed["framing-rock"], FRAMING_OFFSET)
    composite = composite_stack([sky, plateau, framing])
    composite_path = OUT_DIR / "puna-composite.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)
    composite_kb = composite_path.stat().st_size / 1024
    print(f"  saved: {composite_path.name}  {composite_kb:.0f} KB")

    print("\nSTEP 3 - apply 55% Noche Andina scrim")
    scrim_composite = apply_scrim_55(composite)
    scrim_path = OUT_DIR / "puna-composite-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)
    scrim_kb = scrim_path.stat().st_size / 1024
    print(f"  saved: {scrim_path.name}  {scrim_kb:.0f} KB")

    print("\nSTEP 4 - Gate 8 measurement")
    metrics = measure_gate8(scrim_composite, TEXT_ZONE)
    body_v = "PASS" if metrics["body_pass"] else "FAIL"
    disp_v = "PASS" if metrics["display_pass"] else "FAIL"
    print(f"  p95 luminance:    {metrics['p95_lum']:.4f}")
    print(f"  p95 contrast:     {metrics['p95_contrast']:.2f}:1  "
          f"(body {body_v}, display {disp_v})")
    print(f"  worst contrast:   {metrics['worst_contrast']:.2f}:1  (diagnostic)")
    print(f"  opaque px in zone: {metrics['opaque_px']:,}")

    print("\nSTEP 5 - Gate 8 heatmap")
    heatmap_path = OUT_DIR / "puna-composite-heatmap.png"
    build_heatmap(scrim_composite, heatmap_path)
    print(f"  saved: {heatmap_path.name}")

    metrics["composite_kb"] = composite_kb
    metrics["scrim_kb"] = scrim_kb

    print("\nSTEP 6 - load Apu 1024 baseline metrics for cross-biome viewer")
    apu_processed = REPO / "public" / "Backdrops" / "apu" / "processed"
    apu_composite_path = apu_processed / "apu-composite-alt.webp"
    apu_scrim_path = apu_processed / "apu-composite-scrim-55.webp"
    apu_scrim_heatmap = apu_processed / "apu-composite-scrim-55-heatmap.png"

    if not apu_scrim_path.exists():
        print(f"  [ERROR] Apu scrim composite missing: {apu_scrim_path}",
              file=sys.stderr)
        raise SystemExit(1)

    # Generate Apu scrim-heatmap if missing (matched methodology with Puna)
    if not apu_scrim_heatmap.exists():
        print(f"  generating missing Apu scrim heatmap: {apu_scrim_heatmap.name}")
        apu_scrim_img_for_hmap = Image.open(apu_scrim_path).convert("RGBA")
        build_heatmap(apu_scrim_img_for_hmap, apu_scrim_heatmap)
    else:
        print(f"  Apu scrim heatmap already exists: {apu_scrim_heatmap.name}")

    # Apu uses its own text-zone (central-left, (250,280,700,530))
    apu_text_zone = (250, 280, 700, 530)
    apu_scrim_img = Image.open(apu_scrim_path).convert("RGBA")
    apu_metrics = measure_gate8(apu_scrim_img, apu_text_zone)
    apu_metrics["composite_kb"] = apu_composite_path.stat().st_size / 1024
    apu_metrics["scrim_kb"] = apu_scrim_path.stat().st_size / 1024

    print(f"  Apu p95 contrast:   {apu_metrics['p95_contrast']:.2f}:1")
    print(f"  Puna p95 contrast:  {metrics['p95_contrast']:.2f}:1")
    print(f"  delta:              "
          f"{metrics['p95_contrast'] - apu_metrics['p95_contrast']:+.2f}")

    print("\nSTEP 7 - build cross-biome viewer HTML")
    viewer_path = REPO / "public" / "Backdrops" / "cross-biome-viewer.html"
    build_cross_biome_viewer(apu_metrics, metrics, viewer_path)
    print(f"  saved: {viewer_path}")

    print("\n" + "=" * 72)
    print("OK - Puna 1024 pipeline complete")
    print(f"  outputs: {OUT_DIR}")
    print(f"  viewer:  file:///{viewer_path.as_posix()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
