"""Chroma-key extraction + composite for Selva v4 layers (1024 UI pipeline).

TOP framing geometry (Pad C second variation, vertical-mirror analogue of
Yungas RIGHT-mirror). Canopy source renders opaque at image top with
magenta bottom; composite at offset (0, 0) places canopy on canvas top.
Empirically adjust to (0, -50) or (0, -100) if first run shows canopy
drifting below the frame-top.

Chroma tolerance bumped to 130 following Yungas precedent — painterly
pastel-pink chroma rendered by flux-2-pro at 1024 UI needs looser bounds
to catch fern/leaf silhouette transition pixels without removing legit
painted content.

Selva sky-subject is the B-fixed variant with a jungle river through the
middle-ground. Chroma-strip compliance at 12.5% required front-loaded
instruction in the prompt; single accepted variant committed to repo.

Owns the 4-pane cross-biome viewer HTML (supersedes the 3-pane from
process_yungas.py). Loads Apu + Puna + Yungas baselines for comparison.

Expected sources (fal.ai UI output, JPG, 1024x768):
  public/Backdrops/selva/Raw/selva-sky-subject.jpg
  public/Backdrops/selva/Raw/selva-plateau.jpg
  public/Backdrops/selva/Raw/selva-framing-canopy.jpg

Usage (from repo root, after all 3 layers downloaded):
  python scripts/process_selva.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np


REPO = Path(r"C:\Users\odear\projects\limai")
RAW_DIR = REPO / "public" / "Backdrops" / "selva" / "Raw"
OUT_DIR = REPO / "public" / "Backdrops" / "selva" / "processed"

CANVAS = (1024, 768)
CHROMA_TOLERANCE = 130  # Yungas precedent for painterly pastel-pink chroma
# TOP framing geometry: canopy source is already top-dominant at image top.
# (0, 0) keeps image at original position, canopy lands on canvas-y=0..
# Adjust to (0, -50) or (0, -100) if canopy drifts too far below top edge.
FRAMING_OFFSET = (0, 0)

# Text zone kept same as Yungas (legacy reference only; F6 gradient handles
# contrast architecturally, Gate 8 is informational).
TEXT_ZONE = (180, 280, 630, 530)
TEXT_COLOR_LUM = 0.8423

SCRIM_OPACITY = 0.55
SCRIM_COLOR = (26, 22, 18)

SOURCES = {
    # Sky-subject: bottom 10% magenta strip (B-fixed front-loaded compliance)
    "sky-subject":    (RAW_DIR / "selva-sky-subject.jpg",
                       (0.45, 0.93, 0.55, 0.99)),
    # Plateau: opaque BOTTOM 12-15%, magenta TOP 85-88% (standard plateau
    # structure — same as Apu/Puna/Yungas). Sample top-center for chroma.
    "plateau":        (RAW_DIR / "selva-plateau.jpg",
                       (0.45, 0.05, 0.55, 0.15)),
    # Framing-canopy: TOP 20-30% opaque canopy, BOTTOM 70-80% magenta.
    # NEW structure (first TOP framing in project). Sample bottom-center.
    "framing-canopy": (RAW_DIR / "selva-framing-canopy.jpg",
                       (0.40, 0.80, 0.60, 0.95)),
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
    # Relaxed bounds matching process_puna.py / process_yungas.py
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


# =============================================================================
# 4-pane cross-biome viewer (Apu + Puna + Yungas + Selva)
# =============================================================================

CROSS_BIOME_VIEWER_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Cross-biome style cohesion &mdash; Apu vs Puna vs Yungas vs Selva (F6 scrim)</title>
<style>
  :root {
    --f6-gradient: linear-gradient(90deg,
      rgba(26,22,18,0.68) 0%,
      rgba(26,22,18,0.45) 30%,
      rgba(26,22,18,0.08) 55%,
      rgba(26,22,18,0.0) 72%);
  }
  * { box-sizing: border-box; }
  body { font-family: 'Segoe UI', system-ui, sans-serif; background: #1a1612;
         color: #f4ecd9; margin: 0; padding: 16px; line-height: 1.4; }
  h1 { font-size: 1.15rem; margin: 0 0 12px; }
  h2 { font-size: 0.9rem; color: #c8a26b; margin: 20px 0 8px;
       text-transform: uppercase; letter-spacing: 0.05em; }
  .toolbar { display: flex; gap: 16px; align-items: center; padding: 10px 12px;
             background: rgba(255,255,255,0.03); border: 1px solid #3a2f26;
             margin-bottom: 12px; font-size: 0.85rem; flex-wrap: wrap; }
  .toolbar label { display: flex; gap: 6px; align-items: center; }
  button { background: #2a1f15; color: #f4ecd9; border: 1px solid #3a2f26;
           padding: 4px 10px; cursor: pointer; font-size: 0.82rem; }
  button.active { background: #c8a26b; color: #1a1612; }
  button.new { border-color: #c8a26b; }
  button.legacy { opacity: 0.7; }
  .quartet { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 6px; }
  @media (max-width: 1400px) { .quartet { grid-template-columns: 1fr 1fr; } }
  @media (max-width: 720px)  { .quartet { grid-template-columns: 1fr; } }
  .pane { position: relative; min-width: 0; }
  .pane-label { position: absolute; top: 6px; left: 6px;
                background: rgba(26,22,18,0.9); padding: 3px 8px;
                font-size: 0.68rem; border: 1px solid #3a2f26; z-index: 10; }
  .scroll-wrap { overflow: auto; height: 62vh; border: 1px solid #3a2f26;
                 background: #0d0a08; position: relative; }
  .scroll-wrap img { display: block; transform-origin: top left;
                     image-rendering: pixelated; }
  .gradient-overlay { position: absolute; top: 0; left: 0; right: 0;
                      height: 62vh; pointer-events: none; display: none;
                      z-index: 5; background: var(--f6-gradient); }
  .pane.show-f6 .gradient-overlay { display: block; }
  table { border-collapse: collapse; width: 100%; font-size: 0.85rem;
          margin-top: 6px; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #3a2f26; }
  th { color: #c8a26b; font-weight: 500; text-transform: uppercase;
       font-size: 0.72rem; letter-spacing: 0.05em; }
  td.num { font-variant-numeric: tabular-nums; text-align: right; }
  td.info { opacity: 0.72; }
  p.note { font-size: 0.82rem; opacity: 0.75; max-width: 100ch; line-height: 1.55; }
  p.caveat { font-size: 0.85rem; line-height: 1.55; max-width: 100ch;
             padding: 10px 14px; margin: 10px 0 0;
             background: rgba(200,162,107,0.08); border-left: 3px solid #c8a26b; }
  p.caveat strong { color: #c8a26b; }
  code { background: rgba(255,255,255,0.05); padding: 1px 5px; font-size: 0.8rem; }
</style>
</head>
<body>
<h1>Cross-biome style cohesion &mdash; Apu (1) &middot; Puna (2) &middot; Yungas (3) &middot; Selva (4) &middot; F6 scrim</h1>
<div class="toolbar">
  <span>View:</span>
  <button data-view="f6" class="active new">F6 gradient (production)</button>
  <button data-view="raw">Raw composite</button>
  <button data-view="scrim55" class="legacy">+55% scrim (legacy)</button>
  <button data-view="heatmap" class="legacy">Gate 8 heatmap (legacy)</button>
  <label>Zoom:
    <input type="range" id="zoom" min="0.25" max="2" step="0.05" value="0.6">
    <span id="zoom-val">60%</span>
  </label>
  <span style="opacity:0.6">Scroll one pane to sync the others</span>
</div>

<div class="quartet">
  <div class="pane show-f6">
    <span class="pane-label">Apu &middot; 1 &middot; LEFT cliff</span>
    <div class="scroll-wrap" id="scroll-a">
      <img id="img-a"
           data-raw="apu/processed/apu-composite-alt.webp"
           data-scrim55="apu/processed/apu-composite-scrim-55.webp"
           data-heatmap="apu/processed/apu-composite-scrim-55-heatmap.png"
           data-f6="apu/processed/apu-composite-alt.webp"
           src="apu/processed/apu-composite-alt.webp"
           alt="Apu composite">
    </div>
    <div class="gradient-overlay"></div>
  </div>
  <div class="pane show-f6">
    <span class="pane-label">Puna &middot; 2 &middot; LEFT outcrop</span>
    <div class="scroll-wrap" id="scroll-b">
      <img id="img-b"
           data-raw="puna/processed/puna-composite.webp"
           data-scrim55="puna/processed/puna-composite-scrim55.webp"
           data-heatmap="puna/processed/puna-composite-heatmap.png"
           data-f6="puna/processed/puna-composite.webp"
           src="puna/processed/puna-composite.webp"
           alt="Puna composite">
    </div>
    <div class="gradient-overlay"></div>
  </div>
  <div class="pane show-f6">
    <span class="pane-label">Yungas &middot; 3 &middot; RIGHT trunk (Pad C 1st)</span>
    <div class="scroll-wrap" id="scroll-c">
      <img id="img-c"
           data-raw="yungas/processed/yungas-composite.webp"
           data-scrim55="yungas/processed/yungas-composite-scrim55.webp"
           data-heatmap="yungas/processed/yungas-composite-heatmap.png"
           data-f6="yungas/processed/yungas-composite.webp"
           src="yungas/processed/yungas-composite.webp"
           alt="Yungas composite">
    </div>
    <div class="gradient-overlay"></div>
  </div>
  <div class="pane show-f6">
    <span class="pane-label">Selva &middot; 4 &middot; TOP canopy (Pad C 2nd)</span>
    <div class="scroll-wrap" id="scroll-d">
      <img id="img-d"
           data-raw="selva/processed/selva-composite.webp"
           data-scrim55="selva/processed/selva-composite-scrim55.webp"
           data-heatmap="selva/processed/selva-composite-heatmap.png"
           data-f6="selva/processed/selva-composite.webp"
           src="selva/processed/selva-composite.webp"
           alt="Selva composite">
    </div>
    <div class="gradient-overlay"></div>
  </div>
</div>

<h2>Metrics &mdash; informational only, F6 gradient is the production scrim</h2>
<table>
<tr><th>Metric</th><th>Apu (1)</th><th>Puna (2)</th><th>Yungas (3)</th><th>Selva (4)</th></tr>
<tr>
  <td class="info">p95 contrast on +55% scrim composite (legacy)</td>
  <td class="num info">{{apu_p95}}:1</td>
  <td class="num info">{{puna_p95}}:1</td>
  <td class="num info">{{yungas_p95}}:1</td>
  <td class="num info">{{selva_p95}}:1</td>
</tr>
<tr>
  <td class="info">Worst-pixel contrast on +55% scrim (legacy)</td>
  <td class="num info">{{apu_worst}}:1</td>
  <td class="num info">{{puna_worst}}:1</td>
  <td class="num info">{{yungas_worst}}:1</td>
  <td class="num info">{{selva_worst}}:1</td>
</tr>
<tr>
  <td>Production composite size (raw WebP q90)</td>
  <td class="num">{{apu_comp_kb}} KB</td>
  <td class="num">{{puna_comp_kb}} KB</td>
  <td class="num">{{yungas_comp_kb}} KB</td>
  <td class="num">{{selva_comp_kb}} KB</td>
</tr>
<tr>
  <td class="info">+55% scrim composite size (legacy preview)</td>
  <td class="num info">{{apu_scrim_kb}} KB</td>
  <td class="num info">{{puna_scrim_kb}} KB</td>
  <td class="num info">{{yungas_scrim_kb}} KB</td>
  <td class="num info">{{selva_scrim_kb}} KB</td>
</tr>
</table>

<p class="caveat">
  <strong>Scrim architecture:</strong> F6 left-gradient (CSS layer at runtime in Next.js build, not baked). Gate 8 metrics above are informational continuity data only. All 4 biomes production-accepted on painterly cohesion evaluation. Selva is the first biome with TOP framing (Pad C second variation, vertical-mirror of Yungas RIGHT); framing-canopy compliance drifted to 30% (spec 20-25%) and pragmatic-accepted per the creative-direction-over-compliance precedent.
</p>

<h2>F6 gradient spec</h2>
<p class="note">
  <code>background: linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%);</code>
  <br>Left ~55% viewport = natural text-contrast. Right ~45% viewport = painting fully visible. Text-content cross-biome lives in the left 50% viewport.
</p>

<h2>Reference</h2>
<p class="note">
  All four biomes at 1024&times;768 native (fal.ai UI flux-2-pro). Pad C framing positions: Apu+Puna LEFT (cliff/outcrop), Yungas RIGHT (tree trunk, 1st mirror variation), Selva TOP (canopy, 2nd variation &mdash; first TOP framing in project). Selva sky-subject is the B-variant with a murky warm-brown jungle river flowing through the middle-ground (differentiates from Pacific Ocean teal). No wildlife cross-project. Production composite = raw painterly WebP q90; F6 gradient applied at runtime by the Next.js frontend layer in Phase 2+.
</p>

<script>
  const panes = [
    { scroll: document.getElementById('scroll-a'), img: document.getElementById('img-a') },
    { scroll: document.getElementById('scroll-b'), img: document.getElementById('img-b') },
    { scroll: document.getElementById('scroll-c'), img: document.getElementById('img-c') },
    { scroll: document.getElementById('scroll-d'), img: document.getElementById('img-d') },
  ];
  const allPanes = document.querySelectorAll('.pane');
  let syncing = false;
  function sync(src) {
    if (syncing) return;
    syncing = true;
    const srcMaxX = src.scrollWidth - src.clientWidth;
    const srcMaxY = src.scrollHeight - src.clientHeight;
    panes.forEach(p => {
      if (p.scroll === src) return;
      const dstMaxX = p.scroll.scrollWidth - p.scroll.clientWidth;
      const dstMaxY = p.scroll.scrollHeight - p.scroll.clientHeight;
      p.scroll.scrollLeft = srcMaxX > 0 ? (src.scrollLeft / srcMaxX) * dstMaxX : 0;
      p.scroll.scrollTop = srcMaxY > 0 ? (src.scrollTop / srcMaxY) * dstMaxY : 0;
    });
    requestAnimationFrame(() => { syncing = false; });
  }
  panes.forEach(p => p.scroll.addEventListener('scroll', () => sync(p.scroll)));

  const zoom = document.getElementById('zoom');
  const zoomVal = document.getElementById('zoom-val');
  function applyZoom() {
    const z = zoom.value;
    panes.forEach(p => p.img.style.transform = 'scale(' + z + ')');
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
      panes.forEach(p => { p.img.src = p.img.dataset[view]; });
      allPanes.forEach(p => {
        if (view === 'f6') p.classList.add('show-f6');
        else p.classList.remove('show-f6');
      });
    });
  });
</script>
</body>
</html>
"""


def build_cross_biome_viewer(apu_metrics: dict, puna_metrics: dict,
                             yungas_metrics: dict, selva_metrics: dict,
                             out_path: Path) -> None:
    replacements = {
        "apu_p95":         f"{apu_metrics['p95_contrast']:.2f}",
        "puna_p95":        f"{puna_metrics['p95_contrast']:.2f}",
        "yungas_p95":      f"{yungas_metrics['p95_contrast']:.2f}",
        "selva_p95":       f"{selva_metrics['p95_contrast']:.2f}",
        "apu_worst":       f"{apu_metrics['worst_contrast']:.2f}",
        "puna_worst":      f"{puna_metrics['worst_contrast']:.2f}",
        "yungas_worst":    f"{yungas_metrics['worst_contrast']:.2f}",
        "selva_worst":     f"{selva_metrics['worst_contrast']:.2f}",
        "apu_comp_kb":     f"{apu_metrics['composite_kb']:.0f}",
        "puna_comp_kb":    f"{puna_metrics['composite_kb']:.0f}",
        "yungas_comp_kb":  f"{yungas_metrics['composite_kb']:.0f}",
        "selva_comp_kb":   f"{selva_metrics['composite_kb']:.0f}",
        "apu_scrim_kb":    f"{apu_metrics['scrim_kb']:.0f}",
        "puna_scrim_kb":   f"{puna_metrics['scrim_kb']:.0f}",
        "yungas_scrim_kb": f"{yungas_metrics['scrim_kb']:.0f}",
        "selva_scrim_kb":  f"{selva_metrics['scrim_kb']:.0f}",
    }
    html = CROSS_BIOME_VIEWER_TEMPLATE
    for k, v in replacements.items():
        html = html.replace("{{" + k + "}}", v)
    out_path.write_text(html, encoding="utf-8")


def _load_biome_metrics(scrim_path: Path, composite_path: Path, text_zone) -> dict:
    scrim_img = Image.open(scrim_path).convert("RGBA")
    m = measure_gate8(scrim_img, text_zone)
    m["composite_kb"] = composite_path.stat().st_size / 1024
    m["scrim_kb"] = scrim_path.stat().st_size / 1024
    return m


# =============================================================================
# Orchestrator
# =============================================================================

def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    missing = [path for _, (path, _) in SOURCES.items() if not path.exists()]
    if missing:
        print("ERROR: missing Selva source layers:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        raise SystemExit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Selva 1024 pipeline (Pad C TOP-framing, vertical mirror)")
    print(f"Canvas:       {CANVAS[0]}x{CANVAS[1]}")
    print(f"Framing:      canopy @ offset {FRAMING_OFFSET} (TOP-dominant source)")
    print(f"Tolerance:    {CHROMA_TOLERANCE} (Yungas precedent)")
    print(f"Scrim:        55% Noche Andina (legacy preview, F6 is production)")
    print(f"Text zone:    {TEXT_ZONE}  (legacy reference only)")
    print("=" * 72)

    print("\nSTEP 1 - chroma extraction per layer")
    processed = {}
    for name, (path, sample) in SOURCES.items():
        layer = process_layer(path, sample, name)
        out_path = OUT_DIR / f"selva-{name}.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        kb = out_path.stat().st_size / 1024
        print(f"    saved: {out_path.name}  {kb:.0f} KB")
        processed[name] = layer

    print(f"\nSTEP 2 - composite TOP-framing (canopy @ offset {FRAMING_OFFSET})")
    sky = place(processed["sky-subject"], (0, 0))
    plateau = place(processed["plateau"], (0, 0))
    canopy = place(processed["framing-canopy"], FRAMING_OFFSET)
    composite = composite_stack([sky, plateau, canopy])
    composite_path = OUT_DIR / "selva-composite.webp"
    composite.save(composite_path, "WebP", quality=90, method=6)
    composite_kb = composite_path.stat().st_size / 1024
    print(f"  saved: {composite_path.name}  {composite_kb:.0f} KB")

    print("\nSTEP 3 - apply 55% Noche Andina scrim (legacy preview)")
    scrim_composite = apply_scrim_55(composite)
    scrim_path = OUT_DIR / "selva-composite-scrim55.webp"
    scrim_composite.save(scrim_path, "WebP", quality=90, method=6)
    scrim_kb = scrim_path.stat().st_size / 1024
    print(f"  saved: {scrim_path.name}  {scrim_kb:.0f} KB")

    print("\nSTEP 4 - Gate 8 measurement (informational)")
    selva_metrics = measure_gate8(scrim_composite, TEXT_ZONE)
    selva_metrics["composite_kb"] = composite_kb
    selva_metrics["scrim_kb"] = scrim_kb
    body_v = "PASS" if selva_metrics["body_pass"] else "FAIL"
    disp_v = "PASS" if selva_metrics["display_pass"] else "FAIL"
    print(f"  p95 luminance:    {selva_metrics['p95_lum']:.4f}")
    print(f"  p95 contrast:     {selva_metrics['p95_contrast']:.2f}:1  "
          f"(body {body_v}, display {disp_v})")
    print(f"  worst contrast:   {selva_metrics['worst_contrast']:.2f}:1  (diagnostic)")
    print(f"  opaque px in zone: {selva_metrics['opaque_px']:,}")

    print("\nSTEP 5 - Gate 8 heatmap (legacy)")
    heatmap_path = OUT_DIR / "selva-composite-heatmap.png"
    build_heatmap(scrim_composite, heatmap_path)
    print(f"  saved: {heatmap_path.name}")

    print("\nSTEP 6 - load Apu + Puna + Yungas baselines for 4-biome viewer")
    apu_processed = REPO / "public" / "Backdrops" / "apu" / "processed"
    apu_scrim = apu_processed / "apu-composite-scrim-55.webp"
    apu_composite_p = apu_processed / "apu-composite-alt.webp"
    apu_text_zone = (250, 280, 700, 530)

    puna_processed = REPO / "public" / "Backdrops" / "puna" / "processed"
    puna_scrim = puna_processed / "puna-composite-scrim55.webp"
    puna_composite_p = puna_processed / "puna-composite.webp"
    puna_text_zone = (180, 280, 630, 530)

    yungas_processed = REPO / "public" / "Backdrops" / "yungas" / "processed"
    yungas_scrim = yungas_processed / "yungas-composite-scrim55.webp"
    yungas_composite_p = yungas_processed / "yungas-composite.webp"
    yungas_text_zone = (180, 280, 630, 530)

    for req in (apu_scrim, apu_composite_p, puna_scrim, puna_composite_p,
                yungas_scrim, yungas_composite_p):
        if not req.exists():
            print(f"  [ERROR] required baseline composite missing: {req}",
                  file=sys.stderr)
            raise SystemExit(1)

    apu_metrics = _load_biome_metrics(apu_scrim, apu_composite_p, apu_text_zone)
    puna_metrics = _load_biome_metrics(puna_scrim, puna_composite_p, puna_text_zone)
    yungas_metrics = _load_biome_metrics(yungas_scrim, yungas_composite_p, yungas_text_zone)

    print(f"  Apu p95 contrast:    {apu_metrics['p95_contrast']:.2f}:1")
    print(f"  Puna p95 contrast:   {puna_metrics['p95_contrast']:.2f}:1")
    print(f"  Yungas p95 contrast: {yungas_metrics['p95_contrast']:.2f}:1")
    print(f"  Selva p95 contrast:  {selva_metrics['p95_contrast']:.2f}:1")

    print("\nSTEP 7 - build 4-biome cross-biome viewer HTML")
    viewer_path = REPO / "public" / "Backdrops" / "cross-biome-viewer.html"
    build_cross_biome_viewer(apu_metrics, puna_metrics, yungas_metrics,
                             selva_metrics, viewer_path)
    print(f"  saved: {viewer_path}")

    print("\n" + "=" * 72)
    print("OK - Selva 1024 pipeline complete (4-biome viewer updated)")
    print(f"  outputs: {OUT_DIR}")
    print(f"  viewer:  file:///{viewer_path.as_posix()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
