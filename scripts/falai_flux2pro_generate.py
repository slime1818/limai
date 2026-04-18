"""Generic fal.ai flux-2-pro generator for biome-layer production.

Single-shot API call at 2048x1536 (c1 production path). Designed to be
reused across all biome layers without code edits — prompt + output path
come from CLI args.

Security properties (identical to falai_flux2pro_test.py):
- FAL_KEY read from env only; never interpolated in print/log/file output.
- Exactly one fal_client.subscribe() call per invocation. No retry loop.
- On error: diagnose + exit. No automatic retry = no surprise cost stacking.
- Refuses to overwrite an existing output unless --force is passed
  (defense against accidentally spending on the same file twice).

Requires:
  - env var FAL_KEY
  - pip install fal-client requests

Usage (from repo root):
  # literal prompt
  python scripts/falai_flux2pro_generate.py \\
      --prompt "extreme low-angle view..." \\
      --output public/Backdrops/apu/Raw/apu-plateau-2048.png

  # prompt from file (recommended for long prompts)
  python scripts/falai_flux2pro_generate.py \\
      --prompt-file prompts/apu-plateau.txt \\
      --output public/Backdrops/apu/Raw/apu-plateau-2048.png \\
      --seed 42

  # overwrite safeguard
  python scripts/falai_flux2pro_generate.py ... --force   # re-run on existing path

Cost: ~$0.075 per call at 2048x1536 (rounds to 4 MP pricing tier).

Exit codes:
  0  success
  1  missing dependency
  2  missing FAL_KEY / invalid args
  3  API error
  4  unexpected response shape
  5  image download failed
  6  output exists and --force not given
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import fal_client  # type: ignore
except ImportError:
    print("ERROR: fal-client not installed.", file=sys.stderr)
    print("  pip install fal-client", file=sys.stderr)
    raise SystemExit(1)

try:
    import requests
except ImportError:
    print("ERROR: requests not installed.", file=sys.stderr)
    print("  pip install requests", file=sys.stderr)
    raise SystemExit(1)


MODEL_ID = "fal-ai/flux-2-pro"
TARGET_WIDTH = 2048
TARGET_HEIGHT = 1536


def _diagnose_api_error(exc: Exception) -> None:
    msg = str(exc).lower()
    name = type(exc).__name__
    print(f"  exception: {name}: {exc}", file=sys.stderr)

    if "401" in msg or "unauthorized" in msg or ("invalid" in msg and "key" in msg):
        print("\nAuth error (401). Verify FAL_KEY is correct and active on "
              "https://fal.ai/dashboard/keys", file=sys.stderr)
        return
    if "403" in msg or "forbidden" in msg:
        print("\nForbidden (403). Account may lack access to flux-2-pro.",
              file=sys.stderr)
        return
    if "422" in msg or "400" in msg or "validation" in msg or "invalid" in msg:
        print("\nAPI rejected the request (422/400). Likely prompt-content "
              "or argument shape issue.", file=sys.stderr)
        return
    if "429" in msg or "rate" in msg:
        print("\nRate-limited (429). Wait 60s and retry.", file=sys.stderr)
        return
    if "timeout" in msg or "timed out" in msg:
        print("\nTimeout. flux-2-pro usually finishes in <30s. Retry.",
              file=sys.stderr)
        return
    if "network" in msg or "connection" in msg:
        print("\nNetwork error. Check internet connectivity.", file=sys.stderr)
        return
    print("\nUnrecognized error. Full exception above.", file=sys.stderr)


def _load_prompt(args) -> str:
    if args.prompt and args.prompt_file:
        print("ERROR: pass either --prompt or --prompt-file, not both.",
              file=sys.stderr)
        raise SystemExit(2)
    if args.prompt:
        return args.prompt
    if args.prompt_file:
        pf = Path(args.prompt_file)
        if not pf.exists():
            print(f"ERROR: prompt file not found: {pf}", file=sys.stderr)
            raise SystemExit(2)
        text = pf.read_text(encoding="utf-8").strip()
        if not text:
            print(f"ERROR: prompt file is empty: {pf}", file=sys.stderr)
            raise SystemExit(2)
        return text
    print("ERROR: must pass --prompt or --prompt-file.", file=sys.stderr)
    raise SystemExit(2)


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description=f"Generic fal.ai {MODEL_ID} generator @ "
                    f"{TARGET_WIDTH}x{TARGET_HEIGHT}",
    )
    parser.add_argument("--prompt", type=str,
                        help="Literal prompt text (XOR with --prompt-file)")
    parser.add_argument("--prompt-file", type=str,
                        help="Path to UTF-8 text file containing the prompt")
    parser.add_argument("--output", type=str, required=True,
                        help="Output image path (PNG recommended)")
    parser.add_argument("--seed", type=int, default=None,
                        help="Fixed seed for reproducibility (default: random)")
    parser.add_argument("--output-format", choices=["png", "jpeg"], default="png",
                        help="Output format (default: png)")
    parser.add_argument("--num-images", type=int, choices=[1, 2, 3, 4], default=1,
                        help="Number of variants per run (1-4, default 1 for "
                             "backward-compat). N>=2 produces {stem}-v1, -v2, ... "
                             "suffixed outputs and requires --yes.")
    parser.add_argument("--yes", action="store_true",
                        help="Required for --num-images >= 2 (cost-safety "
                             "double-check).")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing output path(s) (default: refuse).")
    args = parser.parse_args()

    if not os.environ.get("FAL_KEY"):
        print("ERROR: FAL_KEY env var not set.", file=sys.stderr)
        print("  PowerShell (persistent):   setx FAL_KEY 'your-key-here'",
              file=sys.stderr)
        print("  PowerShell (session):      $env:FAL_KEY = 'your-key-here'",
              file=sys.stderr)
        raise SystemExit(2)

    prompt_text = _load_prompt(args)

    # Build output paths (single or variant-suffixed)
    output_base = Path(args.output)
    if args.num_images == 1:
        output_paths = [output_base]
    else:
        stem = output_base.stem
        ext = output_base.suffix
        parent = output_base.parent
        output_paths = [parent / f"{stem}-v{i+1}{ext}"
                        for i in range(args.num_images)]

    # Cost-safety — multi-image run requires explicit --yes confirmation
    if args.num_images > 1 and not args.yes:
        total_cost = args.num_images * 0.075
        print(f"ERROR: --num-images {args.num_images} will cost "
              f"{args.num_images} x $0.075 = ${total_cost:.3f}.",
              file=sys.stderr)
        print("  Pass --yes to confirm multi-image run.", file=sys.stderr)
        raise SystemExit(2)

    # Existence safety — refuse if ANY target path exists without --force
    existing = [p for p in output_paths if p.exists()]
    if existing and not args.force:
        print(f"ERROR: {len(existing)} output path(s) already exist:",
              file=sys.stderr)
        for p in existing:
            print(f"  {p}", file=sys.stderr)
        print("  Pass --force to overwrite. Refusing to avoid duplicate charges.",
              file=sys.stderr)
        raise SystemExit(6)

    output_base.parent.mkdir(parents=True, exist_ok=True)

    arguments = {
        "prompt": prompt_text,
        "image_size": {"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
        "output_format": args.output_format,
        "num_images": args.num_images,
        "enable_safety_checker": True,
    }
    if args.seed is not None:
        arguments["seed"] = args.seed

    print("=" * 72)
    print(f"fal.ai layer generation  ~  {MODEL_ID}")
    print(f"Requested size:  {TARGET_WIDTH}x{TARGET_HEIGHT}")
    print(f"Output format:   {args.output_format}")
    if args.num_images == 1:
        print(f"Num images:      1")
        print(f"Output path:     {output_paths[0]}")
    else:
        total_cost = args.num_images * 0.075
        print(f"Num images:      {args.num_images}  (total ~${total_cost:.3f})")
        print(f"Output paths:    {args.num_images} variants:")
        for p in output_paths:
            print(f"                 {p}")
    print(f"Seed:            "
          f"{'random (fal assigns)' if args.seed is None else args.seed}")
    print(f"Prompt tokens:   ~{len(prompt_text.split())} words, "
          f"{len(prompt_text)} chars")
    if args.force and any(p.exists() for p in output_paths):
        print("  [--force] will overwrite existing output(s)")
    print("=" * 72)

    start_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.monotonic()

    def _on_queue_update(update) -> None:
        logs = getattr(update, "logs", None)
        if not logs:
            return
        for log in logs:
            if isinstance(log, dict):
                msg = log.get("message") or json.dumps(log)[:200]
            else:
                msg = str(log)[:200]
            print(f"  [fal] {msg}")

    try:
        result = fal_client.subscribe(
            MODEL_ID,
            arguments=arguments,
            with_logs=True,
            on_queue_update=_on_queue_update,
        )
    except Exception as e:
        elapsed = time.monotonic() - t0
        print(f"\n[ERROR] generation failed after {elapsed:.1f}s", file=sys.stderr)
        _diagnose_api_error(e)
        raise SystemExit(3)

    elapsed = time.monotonic() - t0

    if not isinstance(result, dict) or not result.get("images"):
        print("\n[ERROR] unexpected response shape from fal.ai:", file=sys.stderr)
        print(json.dumps(result, indent=2, default=str)[:2000], file=sys.stderr)
        raise SystemExit(4)

    images = result.get("images", [])
    if len(images) != args.num_images:
        print(f"[WARN] requested {args.num_images} image(s), got {len(images)}",
              file=sys.stderr)

    top_seed = result.get("seed")
    print(f"\n[{elapsed:.1f}s] generation complete "
          f"({len(images)} image(s))")

    for idx, (image_info, output_path) in enumerate(
        zip(images, output_paths), start=1
    ):
        image_url = image_info.get("url")
        returned_w = image_info.get("width")
        returned_h = image_info.get("height")
        per_image_seed = image_info.get("seed", top_seed)
        content_type = image_info.get("content_type")

        print(f"\n  [image {idx}/{len(images)}]")
        print(f"    returned dims:  {returned_w}x{returned_h} "
              f"(requested {TARGET_WIDTH}x{TARGET_HEIGHT})")
        print(f"    returned seed:  {per_image_seed}")
        print(f"    content-type:   {content_type}")
        print(f"    image URL:      {image_url}")

        if not image_url:
            print(f"[ERROR] no image URL in image {idx}", file=sys.stderr)
            raise SystemExit(4)

        dim_match = (returned_w == TARGET_WIDTH and returned_h == TARGET_HEIGHT)
        if not dim_match:
            print(f"    [WARN] dim mismatch "
                  f"({returned_w}x{returned_h} vs "
                  f"{TARGET_WIDTH}x{TARGET_HEIGHT})", file=sys.stderr)

        print(f"    downloading to {output_path}")
        try:
            resp = requests.get(image_url, timeout=60)
            resp.raise_for_status()
            output_path.write_bytes(resp.content)
        except Exception as e:
            print(f"[ERROR] download {idx} failed: {e}", file=sys.stderr)
            raise SystemExit(5)

        file_bytes = output_path.stat().st_size
        file_mb = file_bytes / (1024 * 1024)
        print(f"    saved: {file_bytes:,} bytes ({file_mb:.2f} MB)")

        meta_path = output_path.with_suffix(".meta.json")
        metadata = {
            "model_id": MODEL_ID,
            "image_index": idx,
            "num_images_requested": args.num_images,
            "requested_size": {"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
            "returned_size": {"width": returned_w, "height": returned_h},
            "dimension_match": dim_match,
            "seed": per_image_seed,
            "prompt": prompt_text,
            "prompt_source": "file" if args.prompt_file else "cli",
            "prompt_file": args.prompt_file,
            "output_format_requested": args.output_format,
            "content_type_returned": content_type,
            "output_path": str(output_path),
            "file_size_bytes": file_bytes,
            "file_size_mb": round(file_mb, 3),
            "start_utc": start_iso,
            "elapsed_seconds": round(elapsed, 2),
            "image_info": image_info,
        }
        meta_path.write_text(
            json.dumps(metadata, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"    metadata: {meta_path}")

    total_cost = args.num_images * 0.075
    print("\n" + "=" * 72)
    print(f"OK — {len(images)} image(s) saved. Cost: ~${total_cost:.3f}.")
    print("=" * 72)


if __name__ == "__main__":
    main()
