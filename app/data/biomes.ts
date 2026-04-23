export type Biome = {
  id: string;
  accentColor: string;
  image: string;
  imageAlt: string;
  title: string;
  tagline: string;
  ctaLabel: string;
  ctaHref: string;
  subpage: string;
};

export const biomes: Biome[] = [
  {
    id: "apu",
    accentColor: "var(--color-apu)",
    image: "/biomes/apu.webp",
    imageAlt:
      "Apu schilderij: Andes bergwand met ijzige kroon bij dageraad, rotspartij links als framing",
    title: "LimAI",
    tagline:
      "Sites voor merken met iets te zeggen. Een studio uit Amsterdam met wortels in de Andes.",
    ctaLabel: "subtle scroll indicator",
    ctaHref: "/coming-soon",
    subpage: "-",
  },
  {
    id: "puna",
    accentColor: "var(--color-puna)",
    image: "/biomes/puna.webp",
    imageAlt:
      "Puna schilderij: altiplano met besneeuwde Andes-toppen, ichu-graspollen op de vlakte, rotspartij links als framing",
    title: "Wie we zijn",
    tagline:
      "Twee makers, één missie: digitale merken met karakter bouwen.",
    ctaLabel: "Lees ons verhaal →",
    ctaHref: "/coming-soon",
    subpage: "/over-ons",
  },
  {
    id: "yungas",
    accentColor: "var(--color-yungas)",
    image: "/biomes/yungas.webp",
    imageAlt:
      "Yungas schilderij: cloud forest vallei met lichtstralen door de mist, hangende lianen rechts als framing",
    title: "Wat we doen",
    tagline:
      "Websites, brand identity en strategie. Transparante pakketten, geen verrassingen.",
    ctaLabel: "Diensten & prijzen →",
    ctaHref: "/coming-soon",
    subpage: "/diensten",
  },
  {
    id: "selva",
    accentColor: "var(--color-selva)",
    image: "/biomes/selva.webp",
    imageAlt:
      "Selva schilderij: diep regenwoud met canopy van takken en lianen als TOP-framing, dichte begroeiing rondom een rivier",
    title: "Wat we maakten",
    tagline:
      "Een blik op recent werk voor merken die verschil willen maken.",
    ctaLabel: "Naar portfolio →",
    ctaHref: "/cases",
    subpage: "/cases",
  },
  {
    id: "paracas",
    accentColor: "var(--color-paracas)",
    image: "/biomes/paracas.webp",
    imageAlt:
      "Paracas schilderij: woestijnlandschap met zandduinen en rotsbogen in de verte, warme bronstinten",
    title: "Hoe we werken",
    tagline: "Helder proces, open communicatie, geen omwegen.",
    ctaLabel: "Ons proces →",
    ctaHref: "/coming-soon",
    subpage: "/proces",
  },
  {
    id: "pacifico",
    accentColor: "var(--color-pacifico)",
    image: "/biomes/pacifico.webp",
    imageAlt:
      "Pacifico schilderij: schemering-oceaan met verspreide vissersboten op warme goudbruine golven",
    title: "Laten we praten",
    tagline: "Klaar om je project te starten? Stuur ons een bericht.",
    ctaLabel: "Start een project →",
    ctaHref: "/contact",
    subpage: "/contact",
  },
];
