# Puna viewport 2 content draft

**Layout:** Optie B, elke founder krijgt een eigen viewport binnen de Puna-sectie.

**Status:** draft, klaar voor Abdul's batch-review aan het einde van substep 1.

---

## Layout wireframe

### Viewport 1: Olivier

```
┌─────────────────────────────────────────────────────┐
│  ─ 02 · Wie we zijn · 1 / 2                         │
│                                                     │
│  Olivier                (Fraunces, XL)              │
│  Founder & lead architect   (Inter mono, copper)    │
│                                            ┌─────┐  │
│  body ~~~~~~~~~~~~~~~~~~~                  │     │  │
│  ~~~~~~~~~~~~~~~~~~~~~~~~                  │foto │  │
│  ~~~~~~~~~~~                               │     │  │
│                                            │     │  │
│  18 · Amsterdam · feit                     └─────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Viewport 2: Abdul

```
┌─────────────────────────────────────────────────────┐
│  ─ 02 · Wie we zijn · 2 / 2                         │
│                                                     │
│  Abdul                  (Fraunces, XL)              │
│  Founder & production lead  (Inter mono, copper)    │
│                                            ┌─────┐  │
│  body ~~~~~~~~~~~~~~~~~~~                  │     │  │
│  ~~~~~~~~~~~~~~~~~~~~~~~~                  │foto │  │
│  ~~~~~~~~~~~                               │     │  │
│                                            │     │  │
│  19 · Amsterdam · designer                 └─────┘  │
│                                                     │
│  Lees ons verhaal →                                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Positie-specs

**Beide viewports gebruiken dezelfde structuur, met alleen de content en het portret verschillend:**

- **Eyebrow:** top-left, Inter monospace 11-12px, copper (#b87f4a), met korte streep ervoor (letter-spacing 0.08em)
- **Naam:** groot, Fraunces display (60-80px op desktop), onder eyebrow. Initieel hidden, wordt onthuld via signature-reveal animatie bij scroll-in
- **Rol:** direct onder naam, Inter monospace klein (13-14px), copper
- **Body:** Inter 16-18px, 3-4 regels, links uitgelijnd binnen de F6 scrim zone
- **Meta-strip:** onderaan content-kolom, Inter monospace klein (11-12px), copper-secondary met middle-dot separators
- **CTA** (alleen VP2): onder meta-strip, Inter 14px met pijl-arrow, hover-underline in copper
- **Foto:** rechterhelft van de viewport, buiten F6 scrim maar met rand die deels in de scrim overlapt. Grootte ongeveer 280 x 380px op desktop. Card-borders 0.5px copper met subtle 3D tilt-on-hover (max 7 graden rotatie)

---

## Viewport 1: Olivier

- **Eyebrow:** 02 · Wie we zijn · 1 / 2
- **Naam** (Fraunces, display): Olivier
- **Rol** (Inter monospace, klein, copper): Founder & lead architect
- **Body** (Inter, body size):

  Strategie, AI en het meeste klantcontact. Als je LimAI mailt, kom je meestal bij mij uit. Ik bedenk waar AI écht verschil maakt voor je bedrijf, en zorg dat het daarna ook wordt gebouwd in plaats van in een rapport te belanden.

- **Meta-strip** (Inter monospace, copper, subtiel): 18 · Amsterdam · bouwt sinds zijn tienerjaren

## Viewport 2: Abdul

- **Eyebrow:** 02 · Wie we zijn · 2 / 2
- **Naam** (Fraunces, display): Abdul
- **Rol** (Inter monospace, klein, copper): Founder & production lead
- **Body** (Inter, body size):

  Zet ontwerpen om naar werkende sites en haalt de trekker over bij release. Werkt in Elementor en Framer. Ook eerste aanspreekpunt voor launch, hosting en dagelijks beheer.

- **Meta-strip** (Inter monospace, copper, subtiel): 19 · Amsterdam · designer
- **CTA:** Lees ons verhaal →

---

## SEO-structuur

```html<section id="puna" aria-labelledby="puna-heading">
  <h2 id="puna-heading" class="sr-only">Wie we zijn</h2>  <article>
    <p class="eyebrow">02 · Wie we zijn · 1 / 2</p>
    <h3>Olivier, Founder & lead architect</h3>
    <p>Strategie, AI en het meeste klantcontact ...</p>
  </article>  <article>
    <p class="eyebrow">02 · Wie we zijn · 2 / 2</p>
    <h3>Abdul, Founder & production lead</h3>
    <p>Zet ontwerpen om naar werkende sites ...</p>
    <a href="/over-ons">Lees ons verhaal</a>
  </article>
</section>
````
Hiërarchie-principes:

één visible H1 op de homepage, in de Apu hero sectie
Puna-sectie krijgt H2 "Wie we zijn", als sr-only of als subtiele eyebrow boven beide viewports
elke founder-viewport krijgt H3 met naam en rol bij elkaar, voor Google en voor LLM-crawlers


Interactie en animatie
Tilt-on-hover (card)

max 6 tot 8 graden rotatie in x en y
ease-out op mouseleave, ongeveer 0.45s
alleen op pointer devices, via @media (hover: hover) and (pointer: fine)
lichte implementatie: vanilla JS met requestAnimationFrame, of react-parallax-tilt

Signature reveal (naam)

SVG path-animation met stroke-dasharray en stroke-dashoffset
getriggerd door IntersectionObserver bij eerste keer in view
duur ongeveer 1.4s, ease-in-out
handgeschreven versie zelf tekenen en exporteren als SVG (Procreate, Figma vector of Illustrator)

Coordinaten (subtiel)

monospace, copper kleur, 11px
bottom-left of bottom-right van de card
waarden:

Amsterdam: 52°22'N  4°53'E
Lima: 12°03'S  77°02'W


context: Amsterdam is waar we zitten, Lima is letterlijk de L in LimAI. Peru zit er dus in als naamverwijzing, niet als herkomstverhaal.


Mobile

dezelfde tekstuele content als desktop, voor content-parity onder mobile-first indexing
layout: gestapeld, portret boven de tekst per founder
tilt-on-hover uit
signature reveal blijft
coordinaten blijven


Open items

foto-treatment: Olivier maakt zelf een versie met en zonder duotone, vergelijking volgt later
Abdul's derde feit: nu "creatief" als placeholder, vervangen na Abdul's review
Olivier's derde feit: nu "bouwt sinds zijn tienerjaren" als gok, bevestigen of vervangen
/over-ons pagina: aparte werksessie, valt buiten substep 1
- /over-ons placeholder pagina wordt meegebouwd in substep 2 (lege page met alleen een minimale heading, inhoud komt later)


Changelog

2026-04-24: eerste draft, chat-sessie Olivier en Claude
