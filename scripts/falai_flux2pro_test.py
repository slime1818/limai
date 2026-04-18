"""fal.ai flux-2-pro empirical c1-path test @ 2048x1536.

Single-shot generator that asks fal.ai's REST API to produce a flux-2-pro
output at a custom image_size beyond the UI preset range, using the
cleaned v4.2 mountain-face prompt verbatim.

Purpose: answer the c1 question — does fal-ai/flux-2-pro accept custom
image_size (e.g. 2048x1536) via API? If yes and the painterly quality
matches the 1024x768 UI baseline, the c1 path is viable as the production
generator for all 6 biomes.

Expected cost: ~$0.075 per run at 3.15 MP (rounds to 4 MP pricing tier).

Requires:
  - env var FAL_KEY (generated via https://fal.ai/dashboard/keys)
  - pip install fal-client requests

Usage (from repo root):
  python scripts/falai_flux2pro_test.py
  python scripts/falai_flux2pro_test.py --seed 42
  python scripts/falai_flux2pro_test.py --output path/to/other.png

Exit codes:
  0  success (API accepted, image downloaded)
  1  missing dependency
  2  missing/invalid FAL_KEY
  3  API error (422/400/401/429/timeout/etc.) — diagnostic printed
  4  unexpected response shape from fal.ai
  5  image download failed
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


REPO = Path(r"C:\Users\odear\projects\limai")
DEFAULT_OUTPUT = (
    REPO / "public" / "Backdrops" / "apu" / "Raw"
    / "apu-mountain-face-flux2pro-api-2048.png"
)

MODEL_ID = "fal-ai/flux-2-pro"
TARGET_WIDTH = 2048
TARGET_HEIGHT = 1536

PROMPT = (
    "extreme low-angle view of a massive mountain face, painterly digital "
    "illustration with soft gradient brushwork and subtle color transitions, "
    "avoiding hard flat shading or cartoon style, camera at ground level "
    "looking straight up at a towering Andean peak, the sheer mountain face "
    "fills 75 percent of the frame from bottom to top, peak apex at the "
    "very top edge of frame, narrow strip of pre-dawn sky visible only at "
    "top above the peak silhouette, no distant horizon, no other mountains, "
    "no establishing shot, close intimate view of one dominant peak, cold "
    "icy white and ice-blue mountain palette with warm rock undertones, "
    "consistent snow coverage across both sides of the mountain face, "
    "symmetrical snow patches on upper half and clean rock on lower half, "
    "golden dawn rim-light only on peak tip catching first sun, calm "
    "uniform tonal region at center-left of mountain face reserved for "
    "text overlay, narrow flat solid bright magenta color strip along "
    "bottom 10 percent of frame below mountain base for alpha extraction, "
    "dramatic close-up composition like a rock climber at the base of a "
    "cliff looking up, no humans, no text, no logos, no photorealism"
)


def _diagnose_api_error(exc: Exception) -> None:
    """Print a targeted diagnostic for common fal.ai API failure modes."""
    msg = str(exc).lower()
    name = type(exc).__name__
    print(f"  exception: {name}: {exc}", file=sys.stderr)

    if "401" in msg or "unauthorized" in msg or ("invalid" in msg and "key" in msg):
        print(
            "\nAuth error (401). Verify FAL_KEY is correct and active on "
            "https://fal.ai/dashboard/keys",
            file=sys.stderr,
        )
        return
    if "403" in msg or "forbidden" in msg:
        print("\nForbidden (403). Account may lack access to flux-2-pro.", file=sys.stderr)
        return
    if "422" in msg or "400" in msg or "validation" in msg or "invalid" in msg:
        print(
            "\nAPI rejected the request (422/400).",
            file=sys.stderr,
        )
        print(
            "CRITICAL c1 SIGNAL: custom image_size may not be accepted at "
            f"{TARGET_WIDTH}x{TARGET_HEIGHT}.",
            file=sys.stderr,
        )
        print(
            "  Retry with UI preset like 'landscape_4_3' by swapping image_size to "
            "{'width':1024,'height':768} to isolate whether the issue is dimension vs other param.",
            file=sys.stderr,
        )
        print(
            "  If only custom size fails: c1 is NOT viable via API. Fall back to option (a) 1024x768 native.",
            file=sys.stderr,
        )
        return
    if "429" in msg or "rate" in msg:
        print(
            "\nRate-limited (429). Wait 60s and retry. "
            "fal.ai free tier has per-minute limits.",
            file=sys.stderr,
        )
        return
    if "timeout" in msg or "timed out" in msg:
        print(
            "\nTimeout. flux-2-pro usually finishes in <30s. "
            "Transient issue — retry in a minute.",
            file=sys.stderr,
        )
        return
    if "network" in msg or "connection" in msg:
        print(
            "\nNetwork error. Check internet connectivity.",
            file=sys.stderr,
        )
        return
    print(
        "\nUnrecognized error. Full exception above. "
        "Inspect fal.ai docs or retry.",
        file=sys.stderr,
    )


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    parser = argparse.ArgumentParser(
        description=f"fal.ai {MODEL_ID} empirical c1 test @ {TARGET_WIDTH}x{TARGET_HEIGHT}",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output PNG path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Fixed seed for reproducibility (default: random, fal.ai assigns)",
    )
    parser.add_argument(
        "--output-format",
        choices=["png", "jpeg"],
        default="png",
        help="Output format request (default: png — cleaner for chroma-strip)",
    )
    args = parser.parse_args()

    fal_key = os.environ.get("FAL_KEY")
    if not fal_key:
        print("ERROR: FAL_KEY env var not set.", file=sys.stderr)
        print(
            "PowerShell (session only):  $env:FAL_KEY = 'your-key-here'",
            file=sys.stderr,
        )
        print(
            "PowerShell (persistent):    setx FAL_KEY 'your-key-here'",
            file=sys.stderr,
        )
        print(
            "  Then CLOSE + REOPEN PowerShell so the persistent var becomes visible.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = output_path.with_suffix(".meta.json")

    arguments = {
        "prompt": PROMPT,
        "image_size": {"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
        "output_format": args.output_format,
        "num_images": 1,
        "enable_safety_checker": True,
    }
    if args.seed is not None:
        arguments["seed"] = args.seed

    print("=" * 72)
    print(f"fal.ai c1 empirical test  ~  {MODEL_ID}")
    print(f"Requested size:  {TARGET_WIDTH}x{TARGET_HEIGHT} (custom, not UI preset)")
    print(f"Output format:   {args.output_format}")
    print(f"Seed:            {'random (fal assigns)' if args.seed is None else args.seed}")
    print(f"Output path:     {output_path}")
    print(f"Prompt tokens:   ~{len(PROMPT.split())} words, {len(PROMPT)} chars")
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

    image_info = result["images"][0]
    image_url = image_info.get("url")
    returned_w = image_info.get("width")
    returned_h = image_info.get("height")
    returned_seed = result.get("seed")
    content_type = image_info.get("content_type")

    print(f"\n[{elapsed:.1f}s] generation complete")
    print(f"  returned dims:  {returned_w}x{returned_h} "
          f"(requested {TARGET_WIDTH}x{TARGET_HEIGHT})")
    print(f"  returned seed:  {returned_seed}")
    print(f"  content-type:   {content_type}")
    print(f"  image URL:      {image_url}")

    if not image_url:
        print("[ERROR] no image URL in response", file=sys.stderr)
        raise SystemExit(4)

    dim_match = (returned_w == TARGET_WIDTH and returned_h == TARGET_HEIGHT)
    if not dim_match:
        print("\n[WARN] returned dimensions differ from request!", file=sys.stderr)
        print(f"  requested: {TARGET_WIDTH}x{TARGET_HEIGHT}", file=sys.stderr)
        print(f"  returned:  {returned_w}x{returned_h}", file=sys.stderr)
        print("  API accepted request but silently resized. Log this — c1 is",
              file=sys.stderr)
        print(f"  viable only up to {returned_w}x{returned_h} on this endpoint.",
              file=sys.stderr)

    print(f"\nDownloading to {output_path} ...")
    try:
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        output_path.write_bytes(resp.content)
    except Exception as e:
        print(f"[ERROR] download failed: {e}", file=sys.stderr)
        raise SystemExit(5)

    file_bytes = output_path.stat().st_size
    file_mb = file_bytes / (1024 * 1024)
    print(f"  saved: {file_bytes:,} bytes ({file_mb:.2f} MB)")

    metadata = {
        "model_id": MODEL_ID,
        "requested_size": {"width": TARGET_WIDTH, "height": TARGET_HEIGHT},
        "returned_size": {"width": returned_w, "height": returned_h},
        "dimension_match": dim_match,
        "seed": returned_seed,
        "prompt": PROMPT,
        "output_format_requested": args.output_format,
        "content_type_returned": content_type,
        "output_path": str(output_path),
        "file_size_bytes": file_bytes,
        "file_size_mb": round(file_mb, 3),
        "start_utc": start_iso,
        "elapsed_seconds": round(elapsed, 2),
        "raw_response": result,
    }
    meta_path.write_text(
        json.dumps(metadata, indent=2, default=str),
        encoding="utf-8",
    )
    print(f"  metadata: {meta_path}")

    print("\n" + "=" * 72)
    if dim_match:
        print("c1 DIMENSION GATE: PASS — API accepts 2048x1536 custom image_size.")
    else:
        print(f"c1 DIMENSION GATE: PARTIAL — API accepted but resized to "
              f"{returned_w}x{returned_h}.")
    print()
    print("Next step — run Gate 9 validator on this output:")
    print(f"  python scripts/validate_flux2max.py --input {output_path}")
    print("=" * 72)


if __name__ == "__main__":
    main()
