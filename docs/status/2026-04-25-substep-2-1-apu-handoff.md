# Substep 2.1 Apu desktop handoff

## Eindstand desktop
VP1 commercial hero met:
- Eyebrow "Studio uit Amsterdam" top-left (copper-glow text-shadow)
- H1 "Website laten maken." Fraunces italic met -ml-2 md:-ml-4 voor optische uitlijning
- LIMAI brand-mark in midblock (copper-glow text-shadow)
- Propositie-paragraph met €400 one-pager tot €1000+ maatwerk plus Amsterdam-keyword
- Drie CTAs hover-swap met Lenis smooth-scroll naar #selva, #yungas, #pacifico
- Conditional copper-glow-soft op secondary CTAs voor leesbaarheid
- LIMA-pill rechtsboven (copper-glow text-shadow)
- Coordinates rechtsonder (copper-glow-soft pseudo-backdrop)
- Scroll-indicator met pulse-stop-on-scroll
- Bottom-aligned content via pb-6 md:pb-8

VP2 zes plus-punten (Variant A cards):
- 3-koloms grid met 2 rijen, max-w-6xl gap-6 md:gap-8
- Per card: nummer 01-06 (copper-glow-soft), label uppercase font-semibold (copper-glow-soft), description warm-white
- 3D hover-tilt 6 graden uniform met spring-easing damping 30 stiffness 200 mass 0.5
- copper border /40, donkere bg /40 backdrop-blur-sm
- Hover: border vol, bg /60, scale 1.03, glow shadow

Apu warmte mode C:
- z-3 warm scrim shift (linear-gradient bruin-warm)
- z-4 blend-mode soft-light (cream tint)
- z-5 warm radial gold gloed upper-right
- F6 site-breed scrim uitgesloten via BiomeScrim.tsx (voor Apu en Selva)

Cinematic intro snel (~0.7s totaal) zodat snelle scrollers content niet missen.

## Locked design-keuzes
- Cards (variant A) gekozen na A/B/C/D test
- Commerciële koers na ouders-feedback (poëtisch -> functioneel)
- Variant B nummers in dots eerder gekozen, vervangen door cards
- Warmte mode C alle 3 routes gestapeld
- Hover-swap CTAs met primary-migratie en dynamische scrim
- Bottom-aligned content
- Tilt uniform 6 graden alle cards
- F6 scrim per-biome opt-out
- copper-glow utility gesplitst in copper-glow (text-shadow only) en copper-glow-soft (pseudo-backdrop) voor verschillende contexten
- Cinematic intro versneld naar 0.7s totaal
- Donkere kolom in Apu-painting links geaccepteerd

## Open items
- Apu mobile (substep 2.1.5 als volgende sessie)
- Andere 5 biomes nog h1 in BiomeSection.tsx (TODO refactor naar h2)
- Fraunces echte italic glyphs in app/layout.tsx (synthetic italic nu)
- lucide-react eventueel installeren als meer iconen nodig
- Drie pre-existing lint suppressions met TODOs voor useSyncExternalStore
- VoiceOver/NVDA screen-reader test voor launch
- Eventuele Apu-painting re-generation via fal.ai

## Sessie-context
Werkmap C:\Users\odear\projects\limai
Stack Next.js 16.2.4 TS Tailwind v4 motion 12.38.0 Lenis
Schrijfstijl Nederlands geen em-dashes
Tools Claude Code --dangerously-skip-permissions --model claude-opus-4-7

## Iteratie-leerpunten
- 25+ iteraties op één biome te veel, voor Puna t/m Pacifico max 5-6
- Eerste-bezoeker test telt zwaarder dan brand-feel
- A/B/C/D feature-flag patroon werkt
- F6 scrim per-biome opt-out beter dan site-breed compensatie
- Copper-glow utility splitsing voor verschillende contexten essentieel
- Counter-overlays op painting-darkness werken niet betrouwbaar
- Cinematic intro 0.7s ipv 1.7s veel beter voor snelle scrollers

## Roadmap-update

Strategische beslissing: alle 6 biomes desktop content first, mobile pas
daarna, backdrop-richting (painterly behouden of switchen naar minimal)
beslissen wanneer alle desktop content evalueerbaar is.

Reden: minimal backdrop variant ontdekt tijdens substep 2.1, voelt mogelijk
mooier dan painterly. Maar beslissing alleen na holistische beoordeling van
alle 6 biomes met content. Mobile-implementaties uitstellen voorkomt
dubbel werk: zonder painting vervallen height-restrictions en wordt mobile
drastisch eenvoudiger.

Nieuwe volgorde:
- Substep 2.1 Apu desktop: KLAAR (live op productie via 87bdf2c, 903e268)
- Substep 2.2 Puna desktop
- Substep 2.3 Yungas desktop
- Substep 2.4 Selva desktop
- Substep 2.5 Paracas desktop
- Substep 2.6 Pacifico desktop
- BESLISMOMENT: painterly behouden of switchen naar minimal
- Substep 3.1-3.6 Mobile per biome met gekozen backdrop-richting
- Substep 4 Contact-form Resend integration plus deployment finalisatie

## Alternatieve design-richting (in overweging)

Tijdens substep 2.1 evaluatie ontdekte Olivier dat een minimale warm-bruine
background (noche-andina body-bg plus drie warmte-overlays zonder painting
Image) visueel rustiger en commerciëler voelt dan painterly composities.
Geparkeerd voor beoordeling na alle 6 desktop biomes.

Mogelijke vervolgstappen na substep 2.6:
- Side-by-side test op separate routes voor objectieve vergelijking
- Test op alle 6 biomes om te zien of minimal universeel werkt of per-biome
  differentiation nodig is
- Beslissing voor LimAI brand-richting: painterly behouden, minimal switchen,
  of hybride
