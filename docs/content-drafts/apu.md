# Apu viewport draft (design + content)

**Layout:** Twee viewports. VP1 is de hero van de hele homepage met LimAI-titel, eyebrow, tagline, metrics-regel en scroll-indicator. VP2 toont de zes-biome route als preview van de cinematic reis die komt.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

**Opmerking:** Apu is de hero-biome (biome 1) en de drager van de enige visible `<h1>` op de homepage ("LimAI"). VP2 contrasteert bewust met VP1 qua compositie: VP1 is tekst-content links-uitgelijnd, VP2 is structureel anders met een horizontale route die over de volle breedte loopt en gecentreerd-italic copy eronder. Dat ritmeverschil voorkomt dat de twee viewports als kopieën aanvoelen.

---

## Layout wireframe

### Viewport 1: hero met metrics-regel

```
┌───────────────────────────────────────────────────────────┐
│  ─ 01 · Studio uit Amsterdam                              │
│                                                           │
│                                                           │
│                                                           │
│  LimAI               (Fraunces italic, XXL ~84-96px)      │
│                                                           │
│  Websites met karakter.                                   │
│  ────────────────                                         │
│  6 BIOMES · 2 MAKERS · AMSTERDAM                          │
│                                                           │
│                                                           │
│                  ↓  scroll              52°22'N · 12°03'S │
└───────────────────────────────────────────────────────────┘
```

### Viewport 2: zes-biome route preview

```
┌───────────────────────────────────────────────────────────┐
│                                                           │
│                                                           │
│                                                           │
│   ●━━━━━━━○━━━━━━━○━━━━━━━○━━━━━━━○━━━━━━━○              │
│  APU     PUNA   YUNGAS  SELVA  PARACAS PACÍFICO           │
│                                                           │
│              Zes taferelen.                               │
│              Scroll om ze te ontmoeten.                   │
│                                                           │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### Positie-specs

**Viewport 1:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), letter-spacing 0.08em, met korte copper-streep ervoor (16-20px lang, 1.2px stroke)
- **LimAI titel:** Fraunces italic, XXL (84-96px op desktop, 64-72px tablet), warm-white (#f4e8db), gecentreerd verticaal in viewport
- **Tagline:** onder titel, Inter regular 16-18px, secondary warm (#e8e0d6), max 1 regel
- **Divider:** korte horizontale lijn onder tagline, kleur rgba(184,127,74,0.4), lengte ongeveer 240px, hoogte 0.5px
- **Metrics-regel:** onder divider, Inter monospace, 11-12px, copper, letter-spacing 0.1em, uppercase, één regel: `6 BIOMES · 2 MAKERS · AMSTERDAM`
- **Scroll-indicator:** gecentreerd onderaan VP1 (horizontaal midden), Inter monospace 11-12px, copper, letter-spacing 0.1em, met chevron `↓` voor het woord `scroll`. Subtle pulse-animatie (zie animatie-sectie)
- **Coordinates:** rechtsonder, Inter monospace 11px, copper, letter-spacing 0.05em, format: `52°22'N · 12°03'S` (Amsterdam latitude · Lima latitude, subtiele Peru-hint via getallen, niet via woorden)

**Viewport 2:**

- **Geen eyebrow:** bewust weggelaten zodat het manifest vrij ademt tegen de biome
- **Connector-lijn:** copper rgba(184,127,74,0.35), 0.5px stroke, horizontaal gecentreerd verticaal in upper-half van viewport, breedte ongeveer 75% van viewport-width
- **Zes dots:** gepositioneerd op gelijke afstand op de connector-lijn
  - **Apu (eerste, actief):** SVG-circle radius 11-12, fill vol copper (#b87f4a)
  - **Andere vijf (Puna, Yungas, Selva, Paracas, Pacífico):** radius 5-6, fill rgba(184,127,74,0.3)
- **Labels onder dots:** Inter monospace, 10-11px, letter-spacing 0.1-0.12em, uppercase
  - Apu-label: vol copper
  - Andere labels: rgba(184,127,74,0.45) (gedimd)
- **Caption (italic):** Fraunces italic, 36-44px, warm-white, gecentreerd onder de route, regel 1: `Zes taferelen.`
- **Sub-caption:** Inter regular, 15-17px, secondary warm, gecentreerd onder caption, regel 2: `Scroll om ze te ontmoeten.`

---

## Viewport 1: Hero (content)

- **Eyebrow:** 01 · Studio uit Amsterdam
- **H1 (Fraunces italic, XXL):** LimAI
- **Tagline (Inter regular):** Websites met karakter.
- **Divider:** subtle copper line, decoratief
- **Metrics-regel (Inter monospace, uppercase):** 6 BIOMES · 2 MAKERS · AMSTERDAM
- **Scroll-indicator (Inter monospace):** ↓  scroll
- **Coordinates (Inter monospace):** 52°22'N · 12°03'S

---

## Viewport 2: Zes-biome route (content)

- **Geen eyebrow**
- **6 route-dots met labels** (van links naar rechts):
  1. APU (actief, vol copper)
  2. PUNA (gedimd)
  3. YUNGAS (gedimd)
  4. SELVA (gedimd)
  5. PARACAS (gedimd)
  6. PACÍFICO (gedimd)
- **Caption (Fraunces italic, gecentreerd):** Zes taferelen.
- **Sub-caption (Inter regular, gecentreerd):** Scroll om ze te ontmoeten.

---

## SEO-structuur

```html
<section id="apu" aria-labelledby="apu-heading">
  <h2 id="apu-heading" class="sr-only">LimAI, studio uit Amsterdam</h2>

  <article aria-labelledby="hero-heading">
    <p class="eyebrow">01 · Studio uit Amsterdam</p>
    <h1 id="hero-heading">LimAI</h1>
    <p class="tagline">Websites met karakter.</p>
    <hr class="divider" aria-hidden="true" />
    <p class="metrics">6 biomes · 2 makers · Amsterdam</p>
    <p class="scroll-indicator" aria-hidden="true">↓ scroll</p>
    <p class="coordinates" aria-hidden="true">52°22'N · 12°03'S</p>
  </article>

  <article aria-labelledby="route-heading">
    <h3 id="route-heading" class="sr-only">De reis door zes biomes</h3>

    <ol class="biome-route" aria-label="Zes biomes op de homepage">
      <li class="active">
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Apu</span>
      </li>
      <li>
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Puna</span>
      </li>
      <li>
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Yungas</span>
      </li>
      <li>
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Selva</span>
      </li>
      <li>
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Paracas</span>
      </li>
      <li>
        <span class="dot" aria-hidden="true"></span>
        <span class="label">Pacífico</span>
      </li>
    </ol>

    <p class="route-caption">Zes taferelen.</p>
    <p class="route-sub">Scroll om ze te ontmoeten.</p>
  </article>
</section>
```

**Hiërarchie-principes:**

- Apu draagt de **enige visible H1** op de homepage: `LimAI`
- Apu-sectie krijgt H2 "LimAI, studio uit Amsterdam" als sr-only voor screen-readers en LLM's (extra context die SEO-relevant is zonder visueel gewicht)
- Eyebrow, tagline, metrics zijn `<p>` elementen, niet headings
- VP2 route is een `<ol>` (geordende lijst) want de volgorde is betekenisvol (de scroll-volgorde van de site)
- Coordinates en scroll-indicator zijn `aria-hidden="true"` want puur decoratief
- Page-level metadata in `app/page.tsx` of `app/layout.tsx`:
  - `<title>LimAI, studio uit Amsterdam voor websites met karakter</title>`
  - `<meta name="description" content="LimAI is een tweekoppige studio uit Amsterdam die websites bouwt met karakter. Van landing pages tot volledige sites met AI-integratie." />`
  - Open Graph tags voor sociale shares (titel, beschrijving, og:image met Apu backdrop)
  - JSON-LD `Organization` schema met naam, founders, locatie

---

## Interactie en animatie

### VP1 cinematic intro (eenmalig bij page-load)

**Timeline:**

| Element | Delay | Duration | Animation |
| --- | --- | --- | --- |
| Eyebrow | 200ms | 400ms | opacity 0 → 1, translateX -8px → 0 |
| LimAI titel | 500ms | letter-per-letter | per-letter fade-in, 60ms stagger, opacity 0 → 1 |
| Tagline | 1000ms | 500ms | opacity 0 → 1, translateY 6px → 0 |
| Divider | 1200ms | 400ms | scaleX 0 → 1 (links-uit-rechts uitvouw), origin left |
| Metrics-regel | 1300ms | 500ms | opacity 0 → 1 |
| Scroll-indicator | 1500ms | 500ms | opacity 0 → 1 |
| Coordinates | 1500ms | 500ms | opacity 0 → 1 |

**Easing:** `cubic-bezier(0.23, 1, 0.32, 1)` (soepel ease-out) voor alle elementen.

**Reduce-motion fallback:**

- Bij `prefers-reduced-motion: reduce`: alle elementen direct zichtbaar, geen staggers of fades

### VP1 scroll-indicator pulse (continue)

- Zachte op-en-neer beweging: translateY 0 → 4px → 0
- Duur: 1.6s per cyclus
- Easing: ease-in-out
- Stopt zodra bezoeker begint met scrollen

### VP2 entrance bij scroll-in

**Connector-lijn:**

- bij scroll-in van VP2: lijn tekent zichzelf van links naar rechts
- techniek: SVG path met `stroke-dasharray` en `stroke-dashoffset`, animeer offset van path-length naar 0
- duur 600ms, ease-out

**Dots:**

- na connector-line is klaar: dots verschijnen sequentieel, 80ms stagger
- Apu (eerste): pulse-effect bij verschijnen (scale 1 → 1.3 → 1 in 300ms)
- Andere vijf: gewoon fade-in (opacity 0 → 0.3, scale 0.6 → 1)

**Labels:**

- na dots: labels faden in onder elke dot, 60ms stagger, 300ms duration

**Caption en sub-caption:**

- na alle dots/labels: caption fade-in (opacity 0 → 1, translateY 8px → 0, 500ms)
- 200ms later: sub-caption fade-in (zelfde animatie)

**Single-shot, niet continuous:**

- Animatie speelt eenmalig bij eerste scroll-in van VP2
- Niet scroll-sync zoals Paracas connector (Paracas is langer en continuer; Apu VP2 is een kort moment dat moet "klikken")

**Reduce-motion fallback:**

- bij `prefers-reduced-motion: reduce`: alle elementen direct zichtbaar, geen tekenanimatie of pulse

---

## Mobile

- **parkeren voor aparte mobile-pass sessie**, na alle 6 biome desktop-drafts klaar
- Mobile-strategie: apart dual-tree fork, 100vh per biome, eigen content-keuze
- Voor Apu mobile waarschijnlijk:
  - VP1 + VP2 samen in één 100vh-viewport (geen scroll binnen Apu op mobile)
  - LimAI titel iets kleiner (48-56px), eyebrow boven, tagline + metrics onder
  - Coordinates en route-preview kunnen ofwel weggelaten of gecomprimeerd (alleen 6 kleine dots zonder labels)
  - Cinematic intro behouden maar versneld (totaal binnen 1.2s)

---

## Open items

- **Scroll-indicator copy:** nu `↓ scroll`. Alternatieven: `Scroll mee`, `Begin de reis`, of alleen `↓` zonder woord. Laat staan voor nu, A/B-test later
- **Caption VP2 finalize:** `Zes taferelen.` is redelijk, maar `Zes biomes.` is functioneler (matcht met metrics-regel "6 BIOMES"). Subjectief, definitief beslissen voor launch
- **Coordinates: enkel of dubbel?** Nu `52°22'N · 12°03'S` (Amsterdam · Lima), subtiele Peru-hint. Alternatief: alleen Amsterdam (`AMS 52°22'N · 4°53'E`), zonder Peru-verwijzing. Beslissing afhankelijk van of we de Peru-link willen tonen of bewust verbergen voor non-LimAI-context
- **JSON-LD Organization schema:** moet ingebouwd worden voor SEO. Inhoud:
  - `@type: Organization`
  - `name: LimAI`
  - `url: https://limai.nl` (of definitief domein)
  - `founder: [{name: "Olivier de Armenteras"}, {name: "Abdul ..."}]`
  - `address: {locality: "Amsterdam", country: "NL"}`
  - `description: "Studio voor websites met karakter."`
- **OG-image:** Apu backdrop met LimAI-titel-overlay als 1200x630 PNG voor sociale shares. Genereren met Playwright na Apu in productie staat
- **mobile-pass:** volgt na alle 6 desktop-drafts klaar

---

## Changelog

- 2026-04-24: eerste draft met variant C hero (metrics-regel) en zes-biome route VP2 in landscape-verhouding
