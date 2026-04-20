# Selva biome-4 handoff — 2026-04-20

## Project state
LimAI agency site, biome 4 of 6 in progress.

## Biome status
- ✅ Apu (biome 1) production-locked
- ✅ Puna (biome 2) production-locked
- ✅ Yungas (biome 3) production-locked
- 🟡 Selva (biome 4) — 2/3 layers done:
  - ✅ plateau: V7 variant (massive fallen emergent with buttress roots, palms + philodendron, warm-dark wet earth)
  - ✅ sky-subject: B-winner (wide flowing jungle river, warm-brown water, partial closed-canopy, dense understory)
  - ⏳ framing-canopy: NOT YET RUN — next step
  - ⏳ composite + process_selva.py: pending after framing done

## Key Selva decisions (locked)
- Palette C: ondergedompeld dichte canopy, minimal direct light, humid warm
- TOP framing: chosen experimenteel, untested on Flux, fallback ready (v4-alt = LEFT emergent-trunk with buttress roots)
- River: CHOSEN for Selva sky-subject (differentiates from Pacífico: murky warm-brown vs ocean blue)
- Amazon elements: emergent trees, buttress roots, hanging lianas, bromeliads, palm species, strangler figs, dense understory
- NO wildlife (cross-project policy: no jaguars, tapirs, monkeys, birds — brand clean agency identity over wildlife-site drift)
- Sunbeams acceptable in Selva (precedent set by user's V4 Yungas pick with god-rays)

## Cross-biome framing positions
| Biome | Framing | Status |
|-------|---------|--------|
| Apu | LEFT cliff | Production |
| Puna | LEFT outcrop | Production |
| Yungas | RIGHT trunk (Pad C first variation) | Production |
| Selva | TOP canopy (Pad C second variation, experimental) | PENDING TEST |
| Paracas | TBD | Future |
| Pacífico | TBD | Future |

## Next steps (new chat should do)

### Immediate: Framing-canopy TOP test
1. Run prompts/selva-framing-canopy-v4.txt ($0.24, 8x batch)
2. Verify fal.ai UI: aspect ratio = landscape_4_3 / 4:3 (NOT 1:1)
3. User posts 8-variant grid to Claude
4. Claude evaluates stop-rule:
   - If 1+ correct (TOPMOST 20-25% canopy + bottom 75% magenta + lianas trailing down): pick best, download
   - If all 8 fail (full-height scene, center-bias, or horizontal spread): pivot to v4-alt (+$0.24)
5. Download best as selva-framing-canopy.jpg

### Then: Composite
6. Claude Code writes scripts/process_selva.py:
   - Analogous to process_yungas.py but with TOP framing geometry
   - TOP framing composite offset: start at (0, 0), adjust empirically if canopy doesn't land at top
   - Chroma tolerance: start 55, escalate toward 130 (Yungas precedent)
   - 1024x768 canvas, F6 gradient CSS-only
7. Run script, verify composite
8. Update cross-biome-viewer.html to 4-pane (Apu + Puna + Yungas + Selva)

### Visual verify
9. User opens viewer in Chrome
10. Check F6 gradient on Selva, cross-biome cohesion with 3 earlier biomes, TOP framing visual-success
11. Commit "Selva biome-4 production-locked"

## Budget
- Spent so far on fal.ai (running total): ~$3
- Remaining: ~$2.85 from original ~$5.85 budget
- Estimated for framing-canopy + eventual pivot: $0.24-0.48
- Estimated remaining for Paracas + Pacífico: $1.50-2.00

## Technical reminders / learnings

### Selva sky-subject compliance issue
- A batch (original prompt): 2/8 = 25% strip compliance
- B-fixed (frontload): 1/8 = 12.5%
- **Frontload did NOT improve compliance**
- Hypothesis: Flux interprets "Selva natural rainforest scene" priors too strongly; magenta strip treated as alien compositional element regardless of prompt position
- Workaround: generate more variants ($0.24 per batch), pick compliant ones
- Future biomes: if sky-subject shows similar compliance issues, consider restructuring prompt to lead with "technical composition with magenta chroma strip" instead of "natural scene description"

### fal.ai UI pitfalls experienced this session
- **Aspect ratio slip**: at some point UI reset to 1:1 (square) instead of 4:3. ALWAYS verify landscape_4_3 / 1024x768 before run.
- **num_images=8**: user's explicit choice (not accident). Each batch = $0.24 (8 images × $0.03)

### process_selva.py geometry (to be written)
Claude Code noted in commit 320df1a memory that y-offset sign for TOP framing must be determined empirically:
- PIL screen coords: y-positive = down
- Canopy should appear at TOP of canvas
- Possible offsets to try: (0, 0), (0, -200), or Flux's natural positioning may work without offset
- Chroma-layout: opaque TOP 20-25%, magenta bottom 75-80%

### User preferences / style
- Dutch communication
- Critical visual eye (catches issues across batches)
- Accepts creative direction over strict prompt compliance (picked Yungas V4 with god-rays despite "no direct sun" prompt)
- Pragmatic about cost (explicitly OK with extra batches for better variants)
- Works in fal.ai UI (not via API)
- Location: Amsterdam, NL
- Co-founder: Abdul (handles design/outreach in LimAI agency)

## File manifest for new chat context
- Git log: use `git log --oneline -15` to see recent commits
- Prompts: /prompts/selva-*.txt (6 files: a, b, b-fixed, c, plateau, framing-canopy + alt)
- Downloaded assets: /public/Backdrops/selva/Raw/
  - selva-plateau.jpg (V7 variant)
  - selva-sky-subject.jpg (B-winner with river)
- Viewer: /public/Backdrops/cross-biome-viewer.html (currently 3-pane, update to 4 after Selva composite)
- Design spec: /docs/DESIGN.md (994-line canonical spec)

## How to resume in new chat
New chat Claude should:
1. Read this handoff file first (docs/status/2026-04-20-selva-handoff.md)
2. Run `git log --oneline -15` to see commit history
3. Check working tree clean: `git status`
4. Optionally: view existing biome composites in viewer for visual context of where we are
5. Begin with framing-canopy TOP batch as described in "Next steps" above

## How user starts new chat
Paste this in new chat:
"Project continuation LimAI. Read docs/status/2026-04-20-selva-handoff.md for context. Then we run selva-framing-canopy-v4.txt on fal.ai."
