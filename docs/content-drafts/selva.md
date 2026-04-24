# Selva viewport draft (design + content)

**Layout:** Twee viewports. VP1 toont de LimAI-site zelf als "eerste case" via een code-gebouwde scrub-preview binnen een browser-frame. VP2 toont drie lege atmospheric placeholder-cards die toekomstig portfolio-werk aankondigen.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

**Opmerking:** Selva is nu in coming-soon-fase omdat er nog geen opgeleverde klantcases zijn. Zodra die er zijn, wordt VP1 vervangen door een featured case en vult VP2 zich met echte portfolio-thumbnails.

---

## Layout wireframe

### Viewport 1: site-als-case scrub-preview

```
┌─────────────────────────────────────────────────────┐
│  ─ 04 · Werk                                        │
│                                                     │
│  Deze site. Onze eigen case.    (Fraunces, XL)      │
│                                                     │
│                 ┌─────────────────┐                 │
│                 │ ● ● ●  limai.nl │                 │
│                 ├─────────────────┤                 │
│                 │                 │                 │
│                 │  mini site      │                 │
│                 │  scrubt mee     │                 │
│                 │  met scroll     │                 │
│                 │                 │                 │
│                 │                 │                 │
│                 └─────────────────┘                 │
│                                                     │
│  Body: één regel over stack en aanpak               │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Viewport 2: toekomstig werk

```
┌─────────────────────────────────────────────────────┐
│  ─ 04 · Selva groeit                                │
│                                                     │
│                                                     │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│   │          │   │          │   │          │       │
│   │    01    │   │    02    │   │    03    │       │
│   │          │   │          │   │          │       │
│   │          │   │          │   │          │       │
│   └──────────┘   └──────────┘   └──────────┘       │
│                                                     │
│  Selva groeit. Onze eerste cases landen hier        │
│  zodra ze live zijn.                                │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Positie-specs

**Viewport 1:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), met korte streep ervoor (letter-spacing 0.08em)
- **Headline:** onder eyebrow, Fraunces display, groot (40-56px op desktop), `Deze site. Onze eigen case.`
- **Preview-frame:** gecentreerd onder de headline, max-width ongeveer 560px op desktop, hoogte 360px
  - Browser-chrome: dark bg (#1a1612), 3 "dots" (rgba copper), URL-bar met monospace tekst `limai.nl`, border-radius 10px
  - Inner viewport: overflow hidden, hoogte 320px (na chrome), bevat de miniatuur-site-stack
- **Body:** onder preview, Inter 14-16px, secondary, één zin over de stack (Next.js, GSAP, painterly biomes)

**Viewport 2:**

- **Eyebrow en headline:** zelfde styling als VP1
- **3 empty cards:** gelijke breedte, horizontaal naast elkaar
  - Card border: 0.5px rgba(184,127,74,0.3), border-radius 10px
  - Baseline achtergrond: transparant
  - Padding: 2rem intern
  - Alleen inhoud: groot nummer gecentreerd (Fraunces XXL, rgba(184,127,74,0.5), uitzicht als "nog-leeg")
  - Bewust niet interactief: geen cursor pointer, geen hover-effect. Lege kaders mogen niet misleidend als klikbaar overkomen
- **Body-regel:** onder de cards, Inter body, gecentreerd, secondary kleur

---

## Viewport 1: Site als eerste case (content)

- **Eyebrow:** 04 · Werk
- **Headline** (Fraunces, display): Deze site. Onze eigen case.
- **Body** (Inter, body size, onder preview): Next.js, GSAP, painterly biomes en een cinematic scroll die beweegt zoals een goede film.
- **Preview:** code-gebouwde miniatuur-site, scrolt gesynced met Selva VP1 scroll-progress

### Techniek voor de preview

De preview is een React-component (bijv. `<SitePreview>`) die een mini-versie van de eigen site rendert. Geen afbeeldingen, geen assets, puur code.

**Opbouw:**

- Browser-chrome container (`<div>`) met:
  - header: 3 cirkel-dots (`<div>`s in rij), URL-bar met `limai.nl`
  - border-radius 10px, dark background matching site (#1a1612)
  - border: 0.5px rgba(184,127,74,0.3)
- Inner viewport: `overflow: hidden`, vaste hoogte (bijv. 320px)
- Inner stack: 4 verticaal gestapelde sectie-blokken, elk 320px hoog:
  - blok 1: Apu hero (dark navy bg + Fraunces headline "Ontdek wat we bouwen")
  - blok 2: Puna (copper-brown bg + "Wie we zijn" + zweem van 2 portret-silhouetten)
  - blok 3: Yungas (warm amber bg + 3 mini pricing-card rectangles)
  - blok 4: Selva (green bg + "Werk" headline), meta-knipoog
- Totale hoogte inner stack: 4 × 320 = 1280px
- Elk blok gebruikt dezelfde kleurvariabelen en Fraunces/Inter stack als de echte site

**Scroll-sync:**

- Gebruik motion-library `useScroll` op de Selva-VP1 section
- `offset: ["start end", "end start"]` zodat mapping begint wanneer section in view scrolt en eindigt wanneer ie weer uit beeld is
- Output progress 0-1 mapping naar `translateY(0)` tot `translateY(-(stackHeight - viewportHeight))` op de inner stack
- Easing: `useTransform` met cubic-bezier of gewoon linear mapping
- tip: inner stack krijgt `will-change: transform` voor smooth GPU acceleration

**Fallback wanneer echte cases beschikbaar komen:**

- `<SitePreview>` component blijft bruikbaar, maar wordt vervangen of aangevuld met `<CasePreview slug="..." />` die dan de echte case toont
- structuur is gelijk: browser-chrome plus scrubable inhoud, alleen de inhoud wordt ingeruild

---

## Viewport 2: Toekomstig werk (content)

- **Eyebrow:** 04 · Selva groeit
- **3 empty cards:** alleen nummering `01`, `02`, `03` (Fraunces XXL, rgba(184,127,74,0.5))
- **Body** (Inter, body size, onder cards, gecentreerd):

  Selva groeit. Onze eerste cases landen hier zodra ze live zijn.

- **Geen CTA:** er is niks om op te klikken. Bezoeker gaat gewoon door naar Paracas.

---

## SEO-structuur

```html
<section id="selva" aria-labelledby="selva-heading">
  <h2 id="selva-heading" class="sr-only">Werk</h2>

  <article aria-labelledby="case-preview-heading">
    <p class="eyebrow">04 · Werk</p>
    <h3 id="case-preview-heading">Deze site. Onze eigen case.</h3>
    <p>Next.js, GSAP, painterly biomes en een cinematic scroll ...</p>
    <div class="site-preview" aria-label="Preview van de LimAI homepage">
      <!-- scrubable preview component, purely decorative -->
    </div>
  </article>

  <article aria-labelledby="selva-grows-heading">
    <p class="eyebrow">04 · Selva groeit</p>
    <h3 id="selva-grows-heading">Selva groeit</h3>
    <p>Onze eerste cases landen hier zodra ze live zijn.</p>

    <ul class="upcoming-cases" aria-label="Plekken voor toekomstige cases">
      <li aria-label="Plek voor case 1">01</li>
      <li aria-label="Plek voor case 2">02</li>
      <li aria-label="Plek voor case 3">03</li>
    </ul>
  </article>
</section>
```

**Hiërarchie-principes:**

- één visible H1 op de homepage, in de Apu hero sectie
- Selva-sectie krijgt H2 "Werk", als sr-only boven beide viewports
- VP1 en VP2 krijgen elk een H3 (de viewport-headline)
- preview-component gemarkeerd als `aria-label` zodat screenreaders begrijpen dat het decoratief is
- empty cards gemarkeerd als `<ul>` met `<li>` items en aria-labels die duidelijk maken dat het lege plekken zijn

---

## Interactie en animatie

### VP1 scrub-preview

- `useScroll` hook met `target` op Selva section ref, `offset: ["start end", "end start"]`
- output 0-1 mapping naar `translateY` op inner stack
- easing: linear mapping werkt prima, easing in/out kan ook maar dan subtle
- reduce-motion fallback: bij `prefers-reduced-motion: reduce` stop de scroll-sync, toon de preview statisch op positie 0

### VP2 empty cards entrance

- subtle stagger fade-in bij scroll-in (IntersectionObserver)
- elk card: opacity 0 naar 1, translateY 10px naar 0, stagger 80ms tussen cards
- duur 600ms, ease-out
- géén hover-state: lege cards moeten niet interactief overkomen

### Geen extra animaties

- geen tilt, geen glow, geen pijl-reveal in Selva
- bewust minimalistisch omdat de scrub-preview zelf al visueel complex genoeg is
- Selva onderscheidt zich via de preview-interactie, niet via stapeling van micro-effecten

---

## Mobile

- **parkeren voor aparte mobile-pass sessie**, na alle 6 biome desktop-drafts klaar
- mobile-strategie: apart dual-tree fork, 100vh per biome, geen sticky/fixed/motion, andere content-keuze dan desktop
- voor Selva mobile waarschijnlijk: heel compacte variant zonder scrub-preview (scroll-sync werkt niet lekker op iOS Safari), mogelijk één statische "coming soon" card met icoon en korte regel

---

## Open items

- **echte cases invoegen** zodra opgeleverd:
  - VP1 wordt ingeruild voor een featured klantcase (met scrub-preview van dié site in plaats van LimAI)
  - VP2 grid krijgt 3 thumbnails met live-links naar externe sites
  - empty-state copy ("Selva groeit") gaat weg
- **hover-sync interactie VP2 → VP1:** zodra er grid-items zijn, hoveren op een item in VP2 moet de preview in VP1 wijzigen naar dat project. Technisch: shared state (Zustand of Context) met hovered-case-slug, preview rendert aangepast
- **links per case:** externe live-links met `rel="noopener noreferrer"`, plus analytics click-tracking via Vercel Analytics of Plausible
- **Webarctic case:** mag NIET als case gebruikt worden (niet uitleggen op de site, alleen opslaan in deze open-items-lijst)
- **mobile-pass:** volgt na alle 6 desktop-drafts klaar

---

## Changelog

- 2026-04-24: eerste draft met code-gebouwde scrub-preview (geen assets), lege atmospheric grid-cards voor VP2, chat-sessie Olivier en Claude
