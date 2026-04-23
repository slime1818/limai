export type Biome = {
  id: string;
  accentColor: string;
  image: string;
  imageAlt: string;
  title: string;
  tagline: string;
  ctaLabel: string | null;
  ctaHref: string | null;
  subpage: string;
};

export const biomes: Biome[] = [
  {
    id: "apu",
    accentColor: "var(--color-apu)",
    image: "/biomes/apu.webp",
    imageAlt:
      "Andes-bergwand met ijzige top bij dageraad, rotspartij links op de voorgrond",
    title: "LimAI",
    tagline:
      "Sites voor merken met iets te zeggen. Een studio uit Amsterdam met wortels in de Andes.",
    ctaLabel: null,
    ctaHref: null,
    subpage: "-",
  },
  {
    id: "puna",
    accentColor: "var(--color-puna)",
    image: "/biomes/puna.webp",
    imageAlt:
      "Andes-hoogland met besneeuwde toppen, droge grassen op de vlakte, rotsen links",
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
      "Nevelwoud-vallei met zonnestralen door de mist, hangende lianen aan de rechterzijde",
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
      "Dicht regenwoud met hangende lianen en een bladerdak van takken bovenin",
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
      "Woestijnlandschap met zandduinen en rotsbogen in warme bronstinten",
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
      "Schemer-oceaan met verspreide vissersboten op goudbruine golven",
    title: "Laten we praten",
    tagline: "Klaar om je project te starten? Stuur ons een bericht.",
    ctaLabel: "Start een project →",
    ctaHref: "/contact",
    subpage: "/contact",
  },
];
