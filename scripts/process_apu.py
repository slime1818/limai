"""Chroma-key extraction + composite for Apu v4 layers.

Flux doesn't produce exact #FF00FF despite the prompt - the actual chroma
color varies per image (framing-rock ≈ RGB(251,5,184), plateau ≈ RGB(218,57,150)).
So we sample the background per image, use the detected color as the target,
and remove within a tight tolerance. Mountain-face has no chroma and is
treated as fully opaque.
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

RAW_DIR = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\Raw")
OUT_DIR = Path(r"C:\Users\odear\projects\limai\public\Backdrops\apu\processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CANVAS = (1024, 768)
CHROMA_TOLERANCE = 55  # Euclidean RGB distance from DETECTED chroma color


def detect_chroma(img_path: Path, sample_region: tuple) -> tuple[int, int, int]:
    """Return mean RGB of a normalized sub-region (x1, y1, x2, y2 in 0-1)."""
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    x1, y1, x2, y2 = sample_region
    crop = img.crop((int(x1 * w), int(y1 * h), int(x2 * w), int(y2 * h)))
    arr = np.array(crop)
    return (int(arr[..., 0].mean()), int(arr[..., 1].mean()), int(arr[..., 2].mean()))


def is_pinkish(color: tuple[int, int, int]) -> bool:
    r, g, b = color
    return r > 180 and b > 120 and g < 90


def remove_chroma(img_path: Path, target: tuple[int, int, int], tolerance: int) -> Image.Image:
    img = Image.open(img_path).convert("RGBA")
    data = np.array(img)
    r = data[..., 0].astype(np.int32)
    g = data[..., 1].astype(np.int32)
    b = data[..., 2].astype(np.int32)
    tr, tg, tb = target
    dist = np.sqrt((r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2)
    mask = (dist > tolerance).astype(np.uint8) * 255

    mask_img = Image.fromarray(mask, mode="L")
    mask_img = mask_img.filter(ImageFilter.MinFilter(3))    # contract 1px
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(2)) # feather 2px

    data[..., 3] = np.array(mask_img)
    return Image.fromarray(data.astype(np.uint8), mode="RGBA")


def as_opaque(img_path: Path) -> Image.Image:
    return Image.open(img_path).convert("RGBA")


def process_layer(img_path: Path, chroma_sample_region: tuple, name: str) -> Image.Image:
    detected = detect_chroma(img_path, chroma_sample_region)
    print(f"  {name}: sampled chroma region -> RGB{detected}", end="")
    if is_pinkish(detected):
        layer = remove_chroma(img_path, detected, CHROMA_TOLERANCE)
        arr = np.array(layer)[..., 3]
        pct = 100 * (arr > 128).sum() / arr.size
        print(f"  (chroma detected -> removed, {pct:.1f}% opaque)")
    else:
        layer = as_opaque(img_path)
        print(f"  (no chroma -> fully opaque)")
    return layer


def place(layer: Image.Image, position: tuple) -> Image.Image:
    c = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    c.paste(layer, position, layer)
    return c


def composite_stack(layers: list[Image.Image]) -> Image.Image:
    out = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    for layer in layers:
        out = Image.alpha_composite(out, layer)
    return out


def main() -> None:
    sources = {
        "mountain-face": (RAW_DIR / "apu-mountain-face.jpg", (0.45, 0.92, 0.55, 0.98)),  # bottom-center (spec'd chroma strip)
        "plateau":       (RAW_DIR / "apu-plateau.jpg",       (0.45, 0.10, 0.55, 0.20)),  # top-center
        "framing-rock":  (RAW_DIR / "apu-framing-rock.jpg",  (0.80, 0.40, 0.95, 0.60)),  # right-middle
    }

    print("STEP 1 - adaptive chroma-key extraction + alpha WebP export")
    processed: dict[str, Image.Image] = {}
    for name, (path, sample) in sources.items():
        if not path.exists():
            print(f"  MISSING: {path}")
            return
        layer = process_layer(path, sample, name)
        out_path = OUT_DIR / f"apu-{name}.webp"
        layer.save(out_path, "WebP", quality=82, method=6)
        processed[name] = layer

    print("\nSTEP 2 - composite")
    mountain = place(processed["mountain-face"], (0, 0))
    plateau  = place(processed["plateau"],       (0, 0))

    rock_spec = place(processed["framing-rock"], (-512, 0))
    comp_spec = composite_stack([mountain, plateau, rock_spec])
    comp_spec.save(OUT_DIR / "apu-composite.webp", "WebP", quality=90, method=6)

    rock_alt = place(processed["framing-rock"], (-200, 0))
    comp_alt = composite_stack([mountain, plateau, rock_alt])
    comp_alt.save(OUT_DIR / "apu-composite-alt.webp", "WebP", quality=90, method=6)

    rock_0 = place(processed["framing-rock"], (0, 0))
    comp_0 = composite_stack([mountain, plateau, rock_0])
    comp_0.save(OUT_DIR / "apu-composite-x0.webp", "WebP", quality=90, method=6)

    print(f"  rock @ x=-512 on-canvas opaque px: {int((np.array(rock_spec)[...,3]>128).sum()):,}")
    print(f"  rock @ x=-200 on-canvas opaque px: {int((np.array(rock_alt)[...,3] >128).sum()):,}")
    print(f"  rock @ x=0    on-canvas opaque px: {int((np.array(rock_0)[...,3]  >128).sum()):,}")

    print("\nSTEP 3 - file sizes")
    for p in sorted(OUT_DIR.glob("*.webp")):
        kb = p.stat().st_size / 1024
        print(f"  {p.name}: {kb:.1f} KB")


if __name__ == "__main__":
    main()
