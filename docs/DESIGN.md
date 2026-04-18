# LimAI — Design Reference

Single source of truth for Olivier. Captures all locked decisions from the 2026-04-18 design session. `.claude` memory holds machine-readable condensed copies; this document is the authoritative long-form reference.

---

## 1. Brand & content per biome

**LimAI is an agency brand.** Dutch market, VOF structure with Abdul as co-founder. Not a personal brand.

The 6-biome narrative descent mirrors a sales funnel: intro → trust → offer → proof → trust-deepen → action.

Paracas, originally planned as a pricing biome, is repurposed as the **Proces** biome. Pricing merges into Services (Yungas).

| # | Biome    | Role              | Title           | Tagline                                                                                 | CTA                    | Subpage     |
|---|----------|-------------------|-----------------|-----------------------------------------------------------------------------------------|------------------------|-------------|
| 1 | Apu      | Intro / Hero      | LimAI           | Sites voor merken met iets te zeggen. Een studio uit Amsterdam met wortels in de Andes. | subtle scroll indicator| —           |
| 2 | Puna     | About             | Wie we zijn     | Twee makers, één missie: digitale merken met karakter bouwen.                           | Lees ons verhaal →     | /over-ons   |
| 3 | Yungas   | Services + Pricing| Wat we doen     | Websites, brand identity en strategie. Transparante pakketten, geen verrassingen.       | Diensten & prijzen →   | /diensten   |
| 4 | Selva    | Portfolio         | Wat we maakten  | Een blik op recent werk voor merken die verschil willen maken.                          | Naar portfolio →       | /cases      |
| 5 | Paracas  | Proces            | Hoe we werken   | Helder proces, open communicatie, geen omwegen.                                         | Ons proces →           | /proces     |
| 6 | Pacífico | Contact           | Laten we praten | Klaar om je project te starten? Stuur ons een bericht.                                  | Start een project →    | /contact    |

---

## 2. Homepage skeleton

- **Navigation:** scroll-progress dots on the right side, clickable per biome, active-dot uses the per-biome accent color.
- **Scroll per biome:** 2+ viewports each, altitude-pan during scroll (longer/immersive variant).
  - **Viewport 1** = hero (title + tagline + CTA)
  - **Viewport 2** = content-teaser (not full agency content — previews only)
- **Transitions:**
  - **T1 (Apu → Puna), T2 (Puna → Yungas), T3 (Yungas → Selva):** seamless (crossfade + parallax), α uniform-driven.
  - **T4 (Selva → Paracas):** authored drama — camera-lift + leaves → golden-dust particle metamorphosis, β GSAP timeline.
  - **T5 (Paracas → Pacífico):** quiet finish, α uniform-driven.
- **Footer:** subtle after Pacífico; contains KvK, copyright, cookie link, privacy link, socials. Minimalist in LimAI palette.
- **Total:** ~13–14 viewports.

---

## 3. Visual language

### Typography

| Use                                    | Font     | Source                              |
|----------------------------------------|----------|-------------------------------------|
| Display (titles)                       | Fraunces | Google Fonts, `next/font` self-host |
| Body (taglines, paragraphs, subpages)  | Inter    | Google Fonts, `next/font` self-host |

### UI palette (consistent across site)

| Role           | Hex        | Use                                                          |
|----------------|------------|--------------------------------------------------------------|
| Warm White     | `#f5ede0`  | Primary text on dark backgrounds                             |
| Noche Andina   | `#1a1612`  | Primary text on light backgrounds; scrim; dark background    |
| Paper Cream    | `#f8f3ea`  | Subpage main background                                      |
| Andes Copper   | `#b87f4a`  | Primary accent: buttons, links                               |
| Mountain Slate | `#3d4247`  | Secondary accent: borders, secondary buttons                 |
| Ichu Gold      | `#c4a559`  | Success states, highlights                                   |

### Per-biome accents

Applied **only** to scroll-dots and subtle transitions. **Never** in buttons or body text.

| Biome    | Hex        | Name                                                          |
|----------|------------|---------------------------------------------------------------|
| Apu      | `#a8c8d4`  | Ice Rim                                                       |
| Puna     | `#b8a47a`  | Altiplano Khaki                                               |
| Yungas   | `#6b8e6b`  | Cloud Forest                                                  |
| Selva    | `#3a5f3a`  | Jungle Deep                                                   |
| Paracas  | `#b87f4a`  | Desert Bronze (matches primary UI accent — by design)         |
| Pacífico | `#5a8a94`  | Ocean Teal                                                    |

### Buttons

- **Homepage biome CTAs (A style):** minimalist underlined text + arrow.
- **Subpages (B style):** solid rectangular Andes Copper buttons.

### Forms

- Minimalist lines (underline only, no boxes).
- Labels above input fields.

---

## 4. Subpages — launch and post-launch

### Launch scope (Phase 5)

- Homepage (6 biomes, full)
- `/contact` — working form
- `/cases` — Coming soon vibe, live
- `/coming-soon` — placeholder for `/over-ons`, `/diensten`, `/proces`

### CTAs at launch

| Biome    | CTA                 | Target at launch                   |
|----------|---------------------|------------------------------------|
| Apu      | scroll indicator    | no link                            |
| Puna     | Lees ons verhaal →  | `/coming-soon`                     |
| Yungas   | Diensten & prijzen →| `/coming-soon`                     |
| Selva    | Naar portfolio →    | `/cases` (Coming soon styled)      |
| Paracas  | Ons proces →        | `/coming-soon`                     |
| Pacífico | Start een project → | `/contact` (working)               |

### Post-launch roadmap (Phase 6 priority order)

1. `/diensten` — highest priority. One long subpage with services + pricing.
2. `/over-ons`
3. `/cases` — upgrade to real portfolio as clients come in.
4. `/proces` — process already defined; content-write work.

---

## 5. Technical stack

| Layer             | Tool                                                            |
|-------------------|-----------------------------------------------------------------|
| Framework         | Next.js 14+ with App Router (currently 16.2.4)                  |
| Language          | TypeScript                                                      |
| Styling           | Tailwind CSS with custom palette config                         |
| Animation         | GSAP (ScrollTrigger + T4 authored timeline)                     |
| 3D / Particles    | React Three Fiber (R3F) + Three.js                              |
| Forms             | Formspree or Resend (no backend)                                |
| Hosting           | Vercel                                                          |
| Fonts             | `next/font` for Fraunces + Inter                                |
| Assets            | WebP composites + scrim from Python pipeline (platform-agnostic)|

### Team

- **Olivier** — primary dev
- **Claude Code** — co-pilot
- **Abdul** — outreach and social. Not implementation.

---

## 6. Implementation roadmap

### Phase 1 — Asset completion (~1 week, current phase)

- Puna Gate 8 fix (text-zone shift)
- Yungas v4 prompts (RIGHT framing per Pad C)
- Yungas runs + composite
- Selva / Paracas / Pacífico same cycle
- Cross-biome viewer final check across all 6 biomes

### Phase 2 — Next.js project setup (~1 week)

- Init, fonts, Tailwind config, routing skeleton
- Apu hero static on Vercel

### Phase 3 — Scroll architecture (~2 weeks, most complex)

- Biome component pattern
- GSAP scroll-triggers for altitude-pan
- Transitions T1–T5 (including authored T4)
- Scroll-progress dots

### Phase 4 — Particles and polish (~1.5 weeks)

R3F particle systems per biome:

| Biome    | Particles                                                    |
|----------|--------------------------------------------------------------|
| Apu      | Snowflakes (50–80, slow downward drift)                      |
| Puna     | Wind streaks + dust motes (lighter, more horizontal motion)  |
| Yungas   | Rain streaks + mist (denser near bottom of frame)            |
| Selva    | Falling leaves + god-rays (mid-density, occasional cross-text)|
| Paracas  | Baseline sand + **stochastic intensifications** (not timed)   |
| Pacífico | Sea spray + subtle mist above waves                          |

Accessibility pass included in this phase.

### Phase 5 — Launch prep (~1 week)

- `/contact` form, `/cases`, `/coming-soon`
- Footer, cookie banner, SEO, domain

### Phase 6 — Launch and iterate

- `/diensten` first, then `/over-ons`, `/cases` upgrade, `/proces`

**Total estimate:** ~6.5 weeks realistic with part-time availability.
