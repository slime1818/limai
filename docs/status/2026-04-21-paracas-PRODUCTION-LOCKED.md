# Paracas biome-5 PRODUCTION-LOCKED — 2026-04-21

## Status
5 of 6 biomes production-locked: Apu · Puna · Yungas · Selva · Paracas. Only Pacifico remaining.

## Paracas session summary
Single-session production (much faster than Selva's multi-day iteration). Palette-match strategy + Selva v7 learnings enabled quick convergence. BOTTOM framing architecture validated on first attempt.

## Key learnings codified
1. BOTTOM framing works with 3-layer stack (sky → plateau → framing) if curved arc foreground-dune + warm-to-warm boundary with plateau.
2. Novel framing architecture does NOT require novel pipeline — process_paracas.py is structurally same as process_selva.py, just different feather zones.
3. Flux "warm X + cool Y" palette prompts drift cooler than intended. Future lesson: explicit ratio "70% warm 30% cool shadow" in palette block.
4. Chroma tolerance per biome depends on palette complexity, not painterly/photorealistic distinction. Paracas tol=80 same as Apu+Puna despite painterly style, because warm-bronze palette is less green-adjacent than Selva's dark-jungle palette.

## Budget
- Paracas session spend: $0.24 sky + $0.12 plateau + $0.24 framing = $0.60 total (on-budget with estimate)
- Remaining: ~$1.75-2.15 for Pacifico
- Pacifico estimate: $0.48-0.60 (similar 3-layer pattern assumed)

## Next session entry
Paste in next chat:
"LimAI continuation — Paracas biome-5 production-locked. Starting Pacifico biome-6 prompt-authoring. Final biome. Read docs/DESIGN.md for Pacifico spec (Contact page, Ocean Teal #5a8a94 accent, TBD framing — options RIGHT or open landscape)."
