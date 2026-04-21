# Pacifico biome-6 start — 2026-04-21

## Paracas recap
Biome-5 production-locked 2026-04-21. 5 of 6 biomes done. Paracas validated BOTTOM framing + palette-match chain in single-day session. Pacifico is final biome.

## Pacifico user decisions
- Framing: NO FRAMING (open horizon) — distinct from all 5 other biomes. First no-framing biome in project.
- Architecture: 2-layer (sky-subject + plateau-waves). Simpler than Paracas's 3-layer, simpler than Selva's 3-layer.
- Character: calm Pacific sunset + 2-4 fishing boat silhouettes on horizon (Lima/Callao heritage)
- Plateau: gentle ocean swells with sunset-reflections (NOT breaking waves)
- Palette: Paracas-handoff warm bronze top → golden-amber sunset mid → Ocean Teal #5a8a94 lower
- T5 from Paracas: quiet finish (α uniform crossfade, no authored drama)

## Why no-framing works for biome-6
1. Conceptually matches Contact CTA ("open invitation, laten we praten")
2. T5 quiet finish — no framing = no visual dominance, quiet
3. Distinct from all 5 other biomes (visual narrative closure)
4. Simpler pipeline = lower risk on final biome
5. F6 gradient scrim (CSS) handles text contrast, no framing needed for compositional anchor

## Budget plan
- Sky-subject: $0.24 (8x batch — complex: sunset + boats + horizon)
- Plateau-waves: $0.12 (4x batch)
- No framing layer: $0.00 saved
- Total: $0.36 of ~$1.75 remaining
- Project complete budget: ~$1.40 safety margin

## Open questions
- Boat silhouette compliance: Flux historically over-details boats. Watch for cartoony rendering in batch. Fallback: best-of-8 even if boats are suboptimal — we can mask-remove close-up boats if needed in process_pacifico.py, but not mask-add missing ones.
- Sunset warmth vs teal-dominance balance: we want TEAL DOMINANT with warm ACCENTS, not warm-dominant. If batch comes out too warm (Paracas-like), iterate once.
