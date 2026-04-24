export type Biome = {
  id: string;
  accentColor: string;
  image: string;
  imageAlt: string;
  title: string;
  tagline: string;
  viewport2Teaser: string | null;
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
    viewport2Teaser: null,
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
    viewport2Teaser:
      "Achter LimAI staan twee makers met verschillende paden naar hetzelfde vak. Waarom we geloven dat digitale merken karakter mogen dragen, en hoe Amsterdam en de Andes dat bij ons hebben gevormd, vertellen we je graag.",
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
    viewport2Teaser:
      "Website en brand identity vormen de kern, strategie maakt ze samenhangend. Wat je krijgt en wat het kost, leggen we vooraf vast, zodat jij weet waar je aan toe bent.",
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
    viewport2Teaser:
      "Onze cases-pagina staat in de steigers. In plaats van alles te tonen wat we ooit maakten, selecteren we hier projecten waar verhaal en uitvoering samenkomen. De eerste landen binnenkort.",
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
    viewport2Teaser:
      "Van kennismaking tot lancering werken we in duidelijke fases, met vaste momenten voor feedback en besluit. Je weet waar we staan, wat er volgt, en op welke momenten we iets van jou nodig hebben.",
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
    viewport2Teaser:
      "Een mail hoeft geen dichtgetimmerde briefing te zijn. Schrijf in de vorm die past, van vage richting tot uitgewerkt plan. We lezen mee en reageren persoonlijk.",
    ctaLabel: "Start een project →",
    ctaHref: "/contact",
    subpage: "/contact",
  },
];
