"use client";

import Image from "next/image";
import {
  useCallback,
  useEffect,
  useRef,
  useState,
  type CSSProperties,
  type RefObject,
} from "react";
import {
  motion,
  useInView,
  useMotionValue,
  useReducedMotion,
  useSpring,
  useTransform,
  type Variants,
} from "motion/react";

import type { Biome } from "../data/biomes";

// Tabular-nums voor eyebrow-counters en meta-strip-leeftijden, identiek aan Apu.
const MONO_STYLE: CSSProperties = {
  fontFeatureSettings: "'tnum'",
};

// Twee-laagse text-shadow zoals Apu: scherpe korte shadow voor letterrand-definitie
// plus zachte verre shadow voor cinematic depth op warm-white tekst.
const TEXT_SHADOW_STYLE: CSSProperties = {
  textShadow:
    "0 1px 2px rgba(26, 22, 18, 0.85), 0 2px 12px rgba(26, 22, 18, 0.5)",
};

const MONO_SHADOW_STYLE: CSSProperties = {
  ...MONO_STYLE,
  ...TEXT_SHADOW_STYLE,
};

// Olivier foto-treatment systeem. Pass 2.1 koerst op B-natural als productie-
// default na pass 2.0 vergelijking. De varianten via ?olivier=... query-param
// blijven beschikbaar als dev-flag voor latere verkenning (duotone, warmtint).
type OlivierTreatment = "natural" | "duotone" | "warmtint";

type OlivierVariant = {
  src: string;
  treatment: OlivierTreatment;
};

const OLIVIER_DEFAULT: OlivierVariant = {
  src: "/team/olivier-b.webp",
  treatment: "natural",
};

const OLIVIER_VARIANTS: Readonly<Record<string, OlivierVariant>> = {
  "a-natural": { src: "/team/olivier-a.webp", treatment: "natural" },
  "b-natural": OLIVIER_DEFAULT,
  "a-duotone": { src: "/team/olivier-a.webp", treatment: "duotone" },
  "b-duotone": { src: "/team/olivier-b.webp", treatment: "duotone" },
  "b-warmtint": { src: "/team/olivier-b.webp", treatment: "warmtint" },
};

function useOlivierVariant(): OlivierVariant {
  const [variant, setVariant] = useState<OlivierVariant>(OLIVIER_DEFAULT);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const key = params.get("olivier");
    if (key === null) return;
    const found = OLIVIER_VARIANTS[key];
    if (found === undefined) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setVariant(found);
  }, []);
  return variant;
}

// Pass 2.4 lockt Allura als productie-default na pass 2.3 vergelijking. Optie
// B (Fraunces plus kleine Allura) en C (asymmetrisch) zijn weggehaald. De
// originele Fraunces blijft beschikbaar als dev-flag via ?nameStyle=fraunces.
type NameStyle = "allura" | "fraunces";

const SIGNATURES = {
  // aspectRatio matcht viewBox dimensies uit generate_signatures.py output.
  olivier: { src: "/team/signatures/olivier.svg", aspectRatio: "2440 / 755" },
  abdul: { src: "/team/signatures/abdul.svg", aspectRatio: "2544 / 795" },
} as const;

function useNameStyle(): NameStyle {
  const [style, setStyle] = useState<NameStyle>("allura");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("nameStyle") !== "fraunces") return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStyle("fraunces");
  }, []);
  return style;
}

function SignatureMask({
  founderId,
  height,
  className,
  style: extraStyle,
}: {
  founderId: "olivier" | "abdul";
  height: number;
  className?: string;
  // Optional override-style voor speciale plaatsing zoals frame=typographic
  // overlay (absolute positioning, mix-blend-mode, eigen kleur).
  style?: CSSProperties;
}) {
  const sig = SIGNATURES[founderId];
  return (
    <div
      aria-hidden="true"
      className={className}
      style={{
        height: `${height}px`,
        aspectRatio: sig.aspectRatio,
        backgroundColor: "currentColor",
        color: "var(--color-andes-copper-bright)",
        maskImage: `url('${sig.src}')`,
        maskSize: "contain",
        maskRepeat: "no-repeat",
        maskPosition: "left center",
        WebkitMaskImage: `url('${sig.src}')`,
        WebkitMaskSize: "contain",
        WebkitMaskRepeat: "no-repeat",
        WebkitMaskPosition: "left center",
        ...extraStyle,
      }}
    />
  );
}

// Pass 2.4 vergelijkings-scaffolding: skills-row als tekst-rij of als pills.
// Default productie-staat = pills.
type SkillsStyle = "text" | "pills";

function useSkillsStyle(): SkillsStyle {
  const [style, setStyle] = useState<SkillsStyle>("pills");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("skills") !== "text") return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStyle("text");
  }, []);
  return style;
}

function SkillsRow({
  skills,
  style,
}: {
  skills: ReadonlyArray<string>;
  style: SkillsStyle;
}) {
  if (style === "text") {
    return (
      <p
        className="copper-glow-soft text-[var(--color-andes-copper-bright)] text-[12px] tracking-[0.08em] mt-4"
        style={MONO_STYLE}
      >
        {skills.join(" · ")}
      </p>
    );
  }
  return (
    <ul className="flex flex-wrap gap-2 mt-4 list-none p-0 m-0">
      {skills.map((skill) => (
        <li
          key={skill}
          className="px-3 py-1 rounded-full bg-noche-andina/40 backdrop-blur-sm text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.08em] transition-[transform,border-color] duration-200 hover:scale-[1.02] hover:border-[var(--color-andes-copper-bright)]"
          style={{ ...MONO_STYLE, border: "0.5px solid #b87f4a" }}
        >
          {skill}
        </li>
      ))}
    </ul>
  );
}

// Foto-frame systeem. Default productie-staat = magazine. Pass 2.5 breidt
// uit met zes radicaal andere richtingen (fullbleed, atmospheric, duotone,
// asymcrop, kinetic, typographic) plus behoud van pass 2.4 frames als backup-
// vergelijking. Alle non-default opties zijn alleen via ?frame=... bereikbaar.
type FrameStyle =
  | "magazine"
  | "polaroid"
  | "layered"
  | "fullbleed"
  | "fullbleed-cutout-clean"
  | "fullbleed-cutout-rim"
  | "atmospheric"
  | "duotone"
  | "asymcrop"
  | "kinetic"
  | "typographic";

const VALID_FRAMES: ReadonlySet<FrameStyle> = new Set<FrameStyle>([
  "magazine",
  "polaroid",
  "layered",
  "fullbleed",
  "fullbleed-cutout-clean",
  "fullbleed-cutout-rim",
  "atmospheric",
  "duotone",
  "asymcrop",
  "kinetic",
  "typographic",
]);

// Cutout-sources: alpha-PNG/WebP per founder zonder background. Pass 2.7 lockt
// fullbleed-cutout-clean als productie-default voor beide founders.
// Olivier: Photoroom-export 900x1600, figuur ~66% van source-hoogte.
// Abdul: remove.bg-export 433x577, figuur ~39% van source-hoogte. Klein figure-
// fraction binnen source vraagt om per-founder scale-tuning voor pariteit.
const OLIVIER_CUTOUT_SRC = "/team/olivier-b-Photoroom.webp";
// TODO: vervang abdul-cutout-removebg-preview.png met betere kwaliteit cutout
// zodra Abdul nieuwe foto levert. Huidige foto heeft remove.bg artefacten in het
// gezicht (donker haar tegen donkere bg). Pose met camera voor gezicht werkt
// visueel niet als cutout zonder context. Zie pass 2.7 evaluatie.
const ABDUL_CUTOUT_SRC = "/team/abdul-cutout-removebg-preview.png";

const PHOTO_W = 380;
const PHOTO_H = 520;

function useFrameStyle(): FrameStyle {
  // Pass 2.7 lockt fullbleed-cutout-clean als productie-default. Alle pass 2.4
  // en 2.5 dev-flag varianten blijven via expliciet ?frame=... bereikbaar voor
  // backup-vergelijking en toekomstige verkenning. Magazine (oude default) is
  // nog steeds beschikbaar als ?frame=magazine.
  const [style, setStyle] = useState<FrameStyle>("fullbleed-cutout-clean");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const v = params.get("frame");
    if (v === null || !VALID_FRAMES.has(v as FrameStyle)) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStyle(v as FrameStyle);
  }, []);
  return style;
}

// Pass 3.0 cinematic animatie-systeem: drie onafhankelijke dimensies als
// query-param toggles. Productie-default = intro=A, hover=none, sig=clippath.
// Alle dev-flag opties via expliciet ?intro=... ?hover=... ?sig=...
type IntroStyle = "A" | "B";
type HoverEffect = "none" | "parallax" | "scale";
type SigReveal = "clippath" | "fade";

function useIntroStyle(): IntroStyle {
  const [style, setStyle] = useState<IntroStyle>("A");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("intro") !== "B") return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setStyle("B");
  }, []);
  return style;
}

function useHoverEffect(): HoverEffect {
  const [effect, setEffect] = useState<HoverEffect>("none");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const v = params.get("hover");
    if (v !== "parallax" && v !== "scale") return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setEffect(v);
  }, []);
  return effect;
}

function useSigReveal(): SigReveal {
  const [reveal, setReveal] = useState<SigReveal>("clippath");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("sig") !== "fade") return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setReveal("fade");
  }, []);
  return reveal;
}

// Stagger-spacing per intro. A: 80ms tussen elementen (totaal ~800ms voor 8
// elementen met duration 240ms). B: 60ms tussen elementen, langere durations
// per element met cubic-bezier voor cinematic deceleration (totaal ~1.2-1.4s).
const STAGGER_A = 0.08;
const STAGGER_B = 0.06;
const EASE_B: [number, number, number, number] = [0.22, 1, 0.36, 1];

function getStagger(intro: IntroStyle): number {
  return intro === "A" ? STAGGER_A : STAGGER_B;
}

type ElementKind = "eyebrow" | "text" | "photo";

function getIntroVariants(
  intro: IntroStyle,
  kind: ElementKind,
  delay: number,
): Variants {
  if (intro === "A") {
    return {
      hidden: { opacity: 0, y: 20 },
      visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.24, ease: "easeOut", delay },
      },
    };
  }
  if (kind === "eyebrow") {
    return {
      hidden: { opacity: 0, x: -20 },
      visible: {
        opacity: 1,
        x: 0,
        transition: { duration: 0.6, ease: EASE_B, delay },
      },
    };
  }
  if (kind === "photo") {
    return {
      hidden: { opacity: 0, scale: 1.05 },
      visible: {
        opacity: 1,
        scale: 1,
        transition: { duration: 1.0, ease: EASE_B, delay },
      },
    };
  }
  return {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.7, ease: EASE_B, delay },
    },
  };
}

function getSigVariants(reveal: SigReveal, delay: number): Variants {
  if (reveal === "clippath") {
    return {
      hidden: { clipPath: "inset(0 100% 0 0)" },
      visible: {
        clipPath: "inset(0 0 0 0)",
        transition: { duration: 1.4, ease: "easeInOut", delay },
      },
    };
  }
  return {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: { duration: 0.8, ease: "easeOut", delay },
    },
  };
}

// Inline-SVG grain texture voor frame=duotone. fractalNoise base 0.9 plus
// numOctaves 2 geeft fijne film-grain. Werkt cross-browser zonder PNG asset.
const GRAIN_SVG =
  '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">' +
  '<filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2"/></filter>' +
  '<rect width="100%" height="100%" filter="url(#n)" opacity="0.4"/>' +
  "</svg>";
const GRAIN_DATA_URL = `data:image/svg+xml,${encodeURIComponent(GRAIN_SVG)}`;

function PhotoTreatmentOverlays({
  treatment,
}: {
  treatment: OlivierTreatment;
}) {
  if (treatment === "duotone") {
    return (
      <>
        <div
          aria-hidden="true"
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundColor: "#b87f4a",
            mixBlendMode: "multiply",
            opacity: 0.55,
          }}
        />
        <div
          aria-hidden="true"
          className="absolute inset-0 pointer-events-none"
          style={{
            backgroundColor: "#f5ede0",
            mixBlendMode: "screen",
            opacity: 0.5,
          }}
        />
      </>
    );
  }
  if (treatment === "warmtint") {
    return (
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundColor: "#b87f4a",
          mixBlendMode: "soft-light",
          opacity: 0.08,
        }}
      />
    );
  }
  return null;
}

function PhotoFrame({
  frame,
  founderId,
  photoSrc,
  alt,
  treatment,
  coords,
}: {
  frame: FrameStyle;
  founderId: "olivier" | "abdul";
  photoSrc: string;
  alt: string;
  treatment: OlivierTreatment;
  coords: string;
}) {
  const isolation: CSSProperties =
    treatment !== "natural" ? { isolation: "isolate" } : {};
  const photoClass =
    treatment === "duotone"
      ? "object-cover grayscale brightness-90 contrast-110"
      : "object-cover";

  if (frame === "magazine") {
    return (
      <div className="justify-self-end self-end">
        <div
          className="relative overflow-hidden"
          style={{
            width: PHOTO_W,
            height: PHOTO_H,
            border: "2px solid var(--color-andes-copper-bright)",
            boxShadow: "0 0 40px rgba(184, 127, 74, 0.15)",
            ...isolation,
          }}
        >
          <Image
            src={photoSrc}
            alt={alt}
            fill
            sizes={`${PHOTO_W}px`}
            className={photoClass}
          />
          <PhotoTreatmentOverlays treatment={treatment} />
        </div>
        <p
          aria-hidden="true"
          className="text-right mt-2 text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em]"
          style={MONO_STYLE}
        >
          {coords}
        </p>
      </div>
    );
  }

  if (frame === "polaroid") {
    return (
      <div className="justify-self-end self-end">
        <div
          className="bg-paper-cream"
          style={{
            padding: "14px 14px 40px 14px",
            boxShadow: "0 8px 24px rgba(0, 0, 0, 0.4)",
          }}
        >
          <div
            className="relative overflow-hidden"
            style={{
              width: PHOTO_W,
              height: PHOTO_H,
              ...isolation,
            }}
          >
            <Image
              src={photoSrc}
              alt={alt}
              fill
              sizes={`${PHOTO_W}px`}
              className={photoClass}
            />
            <PhotoTreatmentOverlays treatment={treatment} />
          </div>
          <p
            aria-hidden="true"
            className="text-noche-andina text-[11px] tracking-[0.05em] mt-3 text-center"
            style={MONO_STYLE}
          >
            {coords}
          </p>
        </div>
      </div>
    );
  }

  if (frame === "layered") {
    // Layered: photo plus offset copper-tinted bg, plus floating coord-card naast.
    return (
      <div className="justify-self-end self-end flex items-start gap-4">
        <div className="relative">
          <div
            aria-hidden="true"
            className="absolute pointer-events-none"
            style={{
              width: PHOTO_W,
              height: PHOTO_H,
              top: 0,
              left: 0,
              transform: "translate(12px, 12px)",
              backgroundColor: "rgba(184, 127, 74, 0.25)",
            }}
          />
          <div
            className="relative overflow-hidden"
            style={{
              width: PHOTO_W,
              height: PHOTO_H,
              border: "1px solid var(--color-andes-copper-bright)",
              ...isolation,
            }}
          >
            <Image
              src={photoSrc}
              alt={alt}
              fill
              sizes={`${PHOTO_W}px`}
              className={photoClass}
            />
            <PhotoTreatmentOverlays treatment={treatment} />
          </div>
        </div>
        <div
          aria-hidden="true"
          className="self-center px-3 py-1 bg-noche-andina/60 backdrop-blur-sm rounded-sm"
          style={{ border: "0.5px solid var(--color-andes-copper-bright)" }}
        >
          <span
            className="text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em] whitespace-nowrap"
            style={MONO_STYLE}
          >
            {coords}
          </span>
        </div>
      </div>
    );
  }

  if (frame === "atmospheric") {
    // Foto met radial-gradient mask aan alle randen. Geen border. Coords als
    // floating mini-card rechtsonder, gedeeltelijk overlappend met de fade-zone.
    return (
      <div className="justify-self-end self-end relative">
        <div
          className="relative"
          style={{
            width: PHOTO_W,
            height: PHOTO_H,
            maskImage:
              "radial-gradient(ellipse 75% 80% at center, black 50%, transparent 100%)",
            WebkitMaskImage:
              "radial-gradient(ellipse 75% 80% at center, black 50%, transparent 100%)",
            ...isolation,
          }}
        >
          <Image
            src={photoSrc}
            alt={alt}
            fill
            sizes={`${PHOTO_W}px`}
            className={photoClass}
          />
          <PhotoTreatmentOverlays treatment={treatment} />
        </div>
        <div
          aria-hidden="true"
          className="absolute -bottom-2 -right-2 px-3 py-1 bg-noche-andina/60 backdrop-blur-sm rounded-sm"
          style={{ border: "0.5px solid var(--color-andes-copper-bright)" }}
        >
          <span
            className="text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em] whitespace-nowrap"
            style={MONO_STYLE}
          >
            {coords}
          </span>
        </div>
      </div>
    );
  }

  if (frame === "duotone") {
    // Filter chain plus copper multiply plus cream screen plus film grain. Pass
    // 2.0 leerde dat multiply 1.0 te donker was; hier starten we conservatief
    // (multiply 0.5, screen 0.25) gecombineerd met de filter-pipeline op de
    // image. Tune indien Olivier's gezicht niet leesbaar is.
    return (
      <div className="justify-self-end self-end">
        <div
          className="relative overflow-hidden"
          style={{
            width: PHOTO_W,
            height: PHOTO_H,
            isolation: "isolate",
            border: "0.5px solid var(--color-andes-copper-bright)",
          }}
        >
          <Image
            src={photoSrc}
            alt={alt}
            fill
            sizes={`${PHOTO_W}px`}
            className="object-cover"
            style={{
              filter:
                "grayscale(1) brightness(0.95) contrast(1.15) sepia(0.6) hue-rotate(-15deg) saturate(1.4)",
            }}
          />
          <div
            aria-hidden="true"
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundColor: "#b87f4a",
              mixBlendMode: "multiply",
              opacity: 0.5,
            }}
          />
          <div
            aria-hidden="true"
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundColor: "#f5e6d0",
              mixBlendMode: "screen",
              opacity: 0.25,
            }}
          />
          <div
            aria-hidden="true"
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: `url("${GRAIN_DATA_URL}")`,
              backgroundRepeat: "repeat",
              mixBlendMode: "overlay",
              opacity: 0.3,
            }}
          />
        </div>
        <p
          aria-hidden="true"
          className="text-right mt-2 text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em]"
          style={MONO_STYLE}
        >
          {coords}
        </p>
      </div>
    );
  }

  if (frame === "asymcrop") {
    // 9:16 crop met editorial-zine zijbalk. Coordinaten en location-codes
    // verticaal gestapeld in een 40px brede kolom rechts naast de foto.
    const coordParts = coords.trim().split(/\s+/);
    return (
      <div className="justify-self-end self-end flex items-stretch gap-3">
        <div
          className="relative overflow-hidden"
          style={{
            width: 240,
            height: PHOTO_H,
            border: "0.5px solid var(--color-andes-copper-bright)",
            ...isolation,
          }}
        >
          <Image
            src={photoSrc}
            alt={alt}
            fill
            sizes="240px"
            className={`${photoClass} object-center`}
          />
          <PhotoTreatmentOverlays treatment={treatment} />
        </div>
        <div
          aria-hidden="true"
          className="w-10 flex flex-col items-center justify-between py-2"
          style={MONO_STYLE}
        >
          <div className="flex flex-col items-center gap-1 text-[var(--color-andes-copper-bright)] text-[10px] tracking-[0.1em]">
            {coordParts.map((part) => (
              <span key={part}>{part}</span>
            ))}
          </div>
          <div className="w-px flex-1 my-3 bg-[var(--color-andes-copper-bright)]/40" />
          <div className="flex flex-col items-center gap-1 text-[var(--color-andes-copper-bright)] text-[10px] tracking-[0.2em] uppercase">
            <span>AMS</span>
            <span>LIM</span>
          </div>
        </div>
      </div>
    );
  }

  if (frame === "kinetic") {
    // Drie horizontale stroken van 380x173 met 4px gap. Alleen static stack,
    // geen animatie (komt in pass 3 via IntersectionObserver). Elke strook
    // toont een verticale slice via translate van een full-size image binnen
    // een overflow-hidden container.
    const STRIPE_H = (PHOTO_H - 4 * 2) / 3; // 4px gap × 2 = 8, height per strook ≈ 170.66
    return (
      <div
        className="justify-self-end self-end flex flex-col gap-1"
        style={{ width: PHOTO_W }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="relative overflow-hidden"
            style={{
              width: PHOTO_W,
              height: STRIPE_H,
              border: "0.5px solid var(--color-andes-copper-bright)",
              ...isolation,
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -i * STRIPE_H,
                left: 0,
                width: PHOTO_W,
                height: PHOTO_H,
              }}
            >
              <Image
                src={photoSrc}
                alt={i === 0 ? alt : ""}
                width={PHOTO_W}
                height={PHOTO_H}
                sizes={`${PHOTO_W}px`}
                className={photoClass}
                style={{
                  display: "block",
                  width: `${PHOTO_W}px`,
                  height: `${PHOTO_H}px`,
                }}
              />
              <PhotoTreatmentOverlays treatment={treatment} />
            </div>
          </div>
        ))}
        <p
          aria-hidden="true"
          className="text-right mt-1 text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em]"
          style={MONO_STYLE}
        >
          {coords}
        </p>
      </div>
    );
  }

  if (frame === "typographic") {
    // Foto zonder border, Allura naam-overlay schaal 80px hoog absolute
    // gepositioneerd over linker rand. mix-blend-mode difference inverteert de
    // mask tegen wat eronder ligt voor maximale contrast op warm-bronze bg.
    return (
      <div className="justify-self-end self-end relative">
        <div
          className="relative overflow-hidden"
          style={{
            width: PHOTO_W,
            height: PHOTO_H,
            ...isolation,
          }}
        >
          <Image
            src={photoSrc}
            alt={alt}
            fill
            sizes={`${PHOTO_W}px`}
            className={photoClass}
          />
          <PhotoTreatmentOverlays treatment={treatment} />
        </div>
        <SignatureMask
          founderId={founderId}
          height={80}
          style={{
            position: "absolute",
            left: "-40px",
            top: "50%",
            transform: "translateY(-50%)",
            mixBlendMode: "difference",
            color: "white",
            pointerEvents: "none",
          }}
        />
        <div
          aria-hidden="true"
          className="absolute -bottom-3 -left-3 px-3 py-1 bg-noche-andina/60 backdrop-blur-sm rounded-sm"
          style={{ border: "0.5px solid var(--color-andes-copper-bright)" }}
        >
          <span
            className="text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em] whitespace-nowrap"
            style={MONO_STYLE}
          >
            {coords}
          </span>
        </div>
      </div>
    );
  }

  // Fullbleed wordt in FounderViewport buiten PhotoFrame om afgehandeld omdat
  // het een afwijkende article-layout vereist (foto absoluut, content single-
  // column). Komen we hier tegen frame=fullbleed dan rendert PhotoFrame niets.
  return null;
}

type Founder = {
  id: "olivier" | "abdul";
  index: string;
  name: string;
  role: string;
  body: string;
  body2: string;
  skills: ReadonlyArray<string>;
  meta: string;
  coords: string;
  photo: {
    src: string;
    alt: string;
    cutoutSrc: string;
    // Optional CSS transform: scale toe te passen op de cutout zodat figuren
    // op vergelijkbare schaal staan ondanks verschillende source-formats.
    // Default 1.0 als undefined.
    cutoutScale?: number;
  };
  cta: { href: string; label: string } | null;
};

const FOUNDERS: ReadonlyArray<Founder> = [
  {
    id: "olivier",
    index: "1 / 2",
    name: "Olivier",
    role: "Founder & lead architect",
    body:
      "Strategie, AI en het meeste klantcontact. Als je LimAI mailt, kom je meestal bij mij uit. Ik bedenk waar AI écht verschil maakt voor je bedrijf, en zorg dat het daarna ook wordt gebouwd in plaats van in een rapport te belanden.",
    body2:
      "Ik werk met de nieuwste tools maar begin altijd bij wat je echt wilt bereiken. Welke route brengt je daar het snelst, en waar kan AI het zware werk overnemen. Veel websites worden beter door minder, niet door meer.",
    skills: ["AI integratie", "Next.js", "TypeScript", "Python", "HTML/CSS", "SEO"],
    meta: "18 · Amsterdam · bouwt sinds zijn tienerjaren",
    coords: "52°22'N  4°53'E",
    photo: {
      src: "/team/olivier-b.webp",
      alt: "Olivier, founder & lead architect, portret",
      cutoutSrc: OLIVIER_CUTOUT_SRC,
    },
    cta: null,
  },
  {
    id: "abdul",
    index: "2 / 2",
    name: "Abdul",
    role: "Founder & production lead",
    body:
      "Zet ontwerpen om naar werkende sites en haalt de trekker over bij release. Werkt in Elementor en Framer. Ook eerste aanspreekpunt voor launch, hosting en dagelijks beheer.",
    body2:
      "Van Figma-mockup naar live in dagen, niet in weken. Werkt met Elementor en Framer voor snelheid, en bouwt waar nodig zelf de back-end. Vragen die na launch komen, los ik op voordat de week om is.",
    skills: ["Figma", "Framer", "Elementor", "Laravel", "C#", "HTML/CSS"],
    meta: "19 · Amsterdam · designer",
    coords: "12°03'S  77°02'W",
    photo: {
      src: "/team/abdul.webp",
      alt: "Abdul, founder & production lead, portret",
      cutoutSrc: ABDUL_CUTOUT_SRC,
      // Abdul's cutout source heeft figuur op slechts 39% van bbox-hoogte
      // (vs Olivier 66%); cover-fit zou hem ~50% kleiner laten ogen. Scale
      // 1.7 brengt zijn hoofd/torso schaal in de buurt van Olivier.
      cutoutScale: 1.7,
    },
    cta: { href: "/coming-soon", label: "Lees ons verhaal" },
  },
];

export function PunaSection({
  sectionRef,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
}) {
  const olivierVariant = useOlivierVariant();
  const nameStyle = useNameStyle();
  const skillsStyle = useSkillsStyle();
  const frameStyle = useFrameStyle();
  return (
    <section
      ref={sectionRef}
      id="puna"
      aria-labelledby="puna-heading"
      className="relative w-full h-[200vh]"
    >
      <h2 id="puna-heading" className="sr-only">
        Wie we zijn
      </h2>

      {/* Apu-warmte mode C, drie lagen, op section-niveau zodat ze beide VPs
          overspannen zonder zichtbare lijn op de VP1-VP2 overgang. F6 left-
          gradient bar komt globaal uit BiomeScrim (Puna staat niet in de
          opt-out lijst), dus geen lokale F6 hier. */}
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[3]"
        style={{
          background:
            "linear-gradient(90deg, rgba(74, 45, 30, 0.15) 0%, rgba(74, 45, 30, 0.08) 30%, transparent 55%)",
        }}
      />
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[4]"
        style={{
          background: "rgba(255, 220, 180, 0.08)",
          mixBlendMode: "soft-light",
        }}
      />
      <div
        aria-hidden="true"
        className="absolute inset-0 pointer-events-none z-[5]"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 70% 35%, rgba(212, 154, 106, 0.18) 0%, rgba(212, 154, 106, 0.08) 40%, transparent 75%)",
        }}
      />

      <div className="absolute inset-0 z-10">
        {FOUNDERS.map((founder) => (
          <FounderViewport
            key={founder.id}
            founder={founder}
            olivierVariant={founder.id === "olivier" ? olivierVariant : null}
            nameStyle={nameStyle}
            skillsStyle={skillsStyle}
            frameStyle={frameStyle}
          />
        ))}
      </div>
    </section>
  );
}

function FounderViewport({
  founder,
  olivierVariant,
  nameStyle,
  skillsStyle,
  frameStyle,
}: {
  founder: Founder;
  olivierVariant: OlivierVariant | null;
  nameStyle: NameStyle;
  skillsStyle: SkillsStyle;
  frameStyle: FrameStyle;
}) {
  const photoSrc = olivierVariant?.src ?? founder.photo.src;
  const treatment: OlivierTreatment = olivierVariant?.treatment ?? "natural";
  const useAllura = nameStyle === "allura";
  // Typographic verplaatst de Allura signature naar een overlay over de foto.
  // De content-kolom toont dan geen aparte naam-display.
  const showNameInContent = frameStyle !== "typographic";

  if (
    frameStyle === "fullbleed" ||
    frameStyle === "fullbleed-cutout-clean" ||
    frameStyle === "fullbleed-cutout-rim"
  ) {
    return (
      <FullbleedFounderLayout
        frame={frameStyle}
        founder={founder}
        photoSrc={photoSrc}
        treatment={treatment}
        useAllura={useAllura}
        skillsStyle={skillsStyle}
      />
    );
  }

  return (
    <article
      aria-labelledby={`puna-${founder.id}-heading`}
      className="relative h-screen grid grid-rows-[auto_1fr] px-8 md:px-16 lg:px-24 py-8 md:py-12"
    >
      {/* Eyebrow top-left, copper-streep prefix zoals Apu hero. Eyebrow valt in
          de bovenste F6-zone met voldoende contrast, dus copper-glow (text-
          shadow only) volstaat zonder pseudo-backdrop. */}
      <p
        className="copper-glow self-start flex items-center gap-3 text-[var(--color-andes-copper-bright)] text-[12px] md:text-[13px] tracking-[0.08em]"
        style={MONO_SHADOW_STYLE}
      >
        <span
          aria-hidden="true"
          className="block w-4 h-px bg-[var(--color-andes-copper-bright)]"
        />
        02 · Wie we zijn · {founder.index}
      </p>

      <div className="self-end grid grid-cols-1 md:grid-cols-2 items-end gap-10 md:gap-16 pb-6 md:pb-8 w-full">
        <div className="flex flex-col max-w-xl">
          {showNameInContent ? (
            useAllura ? (
              <>
                <h3 id={`puna-${founder.id}-heading`} className="sr-only">
                  {founder.name}, {founder.role}
                </h3>
                <SignatureMask
                  founderId={founder.id}
                  height={88}
                  className="-ml-2 md:-ml-4"
                />
              </>
            ) : (
              <h3
                id={`puna-${founder.id}-heading`}
                className="font-display italic text-warm-white text-[60px] md:text-[72px] lg:text-[80px] leading-[1.05] tracking-tight -ml-1 md:-ml-2"
                style={TEXT_SHADOW_STYLE}
              >
                {founder.name}
              </h3>
            )
          ) : (
            // Typographic: Allura komt als overlay op de foto, alleen sr-only
            // h3 voor SEO/a11y heading-hierarchie.
            <h3 id={`puna-${founder.id}-heading`} className="sr-only">
              {founder.name}, {founder.role}
            </h3>
          )}

          {/* Secondary copper tekst krijgt copper-glow-soft (pseudo-backdrop)
              ipv copper-glow (text-shadow only). Role + meta + CTA vallen
              regelmatig in de F6-fade zone bij midden van VP, waar text-shadow
              alleen niet genoeg contrast geeft tegen de painterly grass-tonen. */}
          <p
            className="copper-glow-soft text-[var(--color-andes-copper-bright)] text-[13px] md:text-[14px] tracking-[0.08em] mt-3"
            style={MONO_STYLE}
          >
            {founder.role}
          </p>

          <p
            className="copper-glow font-sans text-warm-white text-[16px] md:text-[18px] leading-[1.6] mt-6"
            style={TEXT_SHADOW_STYLE}
          >
            {founder.body}
          </p>

          <p
            className="copper-glow font-sans text-warm-white text-[16px] md:text-[18px] leading-[1.6] mt-3"
            style={TEXT_SHADOW_STYLE}
          >
            {founder.body2}
          </p>

          <SkillsRow skills={founder.skills} style={skillsStyle} />

          <p
            className="copper-glow-soft text-[var(--color-andes-copper-bright)]/85 text-[11px] md:text-[12px] tracking-[0.05em] mt-6"
            style={MONO_STYLE}
          >
            {founder.meta}
          </p>

          {founder.cta !== null ? (
            <a
              href={founder.cta.href}
              className="copper-glow-soft inline-flex items-center gap-2 text-[var(--color-andes-copper-bright)] text-[14px] mt-8 underline-offset-4 hover:underline w-fit"
            >
              {founder.cta.label}
              <span aria-hidden="true">→</span>
            </a>
          ) : null}
        </div>

        <PhotoFrame
          frame={frameStyle}
          founderId={founder.id}
          photoSrc={photoSrc}
          alt={founder.photo.alt}
          treatment={treatment}
          coords={founder.coords}
        />
      </div>
    </article>
  );
}

// Fullbleed: foto absoluut over de rechterhelft van het viewport, met linker-
// edge gradient mask die in de F6-zone vervaagt. Tekst-kolom blijft single-
// column links binnen de F6-zone.
function FullbleedFounderLayout({
  frame,
  founder,
  photoSrc,
  treatment,
  useAllura,
  skillsStyle,
}: {
  frame: "fullbleed" | "fullbleed-cutout-clean" | "fullbleed-cutout-rim";
  founder: Founder;
  photoSrc: string;
  treatment: OlivierTreatment;
  useAllura: boolean;
  skillsStyle: SkillsStyle;
}) {
  const isCutout = frame !== "fullbleed";
  const useRim = frame === "fullbleed-cutout-rim";
  const photoSourceUrl = isCutout ? founder.photo.cutoutSrc : photoSrc;
  const cutoutScale = founder.photo.cutoutScale;

  const photoClassName = isCutout
    ? "object-cover"
    : treatment === "duotone"
      ? "object-cover grayscale brightness-90 contrast-110"
      : "object-cover";

  const photoIsolation: CSSProperties =
    treatment !== "natural" && !isCutout ? { isolation: "isolate" } : {};

  const maskStyle: CSSProperties = isCutout
    ? {}
    : {
        maskImage:
          "linear-gradient(to right, transparent 0%, black 200px)",
        WebkitMaskImage:
          "linear-gradient(to right, transparent 0%, black 200px)",
      };

  const imageInlineStyle: CSSProperties = {
    ...(isCutout ? { objectPosition: "center" } : {}),
    ...(useRim
      ? {
          filter:
            "drop-shadow(0 20px 30px rgba(26, 22, 18, 0.6)) drop-shadow(2px -1px 0 rgba(184, 127, 74, 0.4))",
        }
      : {}),
    ...(isCutout && cutoutScale !== undefined && cutoutScale !== 1
      ? {
          transform: `scale(${cutoutScale})`,
          transformOrigin: "center",
        }
      : {}),
  };

  // Pass 3.0 animatie-systeem.
  const introStyle = useIntroStyle();
  const hoverEffect = useHoverEffect();
  const sigReveal = useSigReveal();
  const shouldReduceMotion = useReducedMotion();

  // Per-viewport in-view trigger zodat scrollen-vanaf-Apu niet beide founders
  // tegelijk anim'd voordat ze zichtbaar zijn. Margin -25% op bottom triggered
  // de animatie wanneer 75% van VP in beeld is.
  const articleRef = useRef<HTMLElement | null>(null);
  const isInView = useInView(articleRef, {
    once: true,
    margin: "0% 0% -25% 0%",
  });

  // Stagger-config en delays per element-index in de cinematic volgorde:
  // eyebrow=0, signature=1, role=2, body1=3, body2=4, skills=5, meta=6,
  // cta=6.5 (compact bij meta), photo=7.
  const stagger = getStagger(introStyle);
  const eyebrowDelay = 0;
  const sigDelay = stagger * 1;
  const roleDelay = stagger * 2;
  const body1Delay = stagger * 3;
  const body2Delay = stagger * 4;
  const skillsDelay = stagger * 5;
  const metaDelay = stagger * 6;
  const ctaDelay = stagger * 6.5;
  const photoDelay = stagger * 7;

  const initialState = shouldReduceMotion ? "visible" : "hidden";
  const animateState = shouldReduceMotion || isInView ? "visible" : "hidden";

  // Hover-state voor section-scope hover (effect=scale).
  const [sectionHover, setSectionHover] = useState(false);

  // Parallax: motionvalues + spring damping voor smooth follow op mousemove.
  // Range -1..1 mapped naar -8..8 px translate, max 8px per spec.
  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const parallaxX = useSpring(useTransform(mouseX, [-1, 1], [-8, 8]), {
    damping: 25,
    stiffness: 200,
  });
  const parallaxY = useSpring(useTransform(mouseY, [-1, 1], [-8, 8]), {
    damping: 25,
    stiffness: 200,
  });

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      if (hoverEffect !== "parallax") return;
      const article = articleRef.current;
      if (article === null) return;
      const rect = article.getBoundingClientRect();
      const cx = (e.clientX - rect.left) / rect.width - 0.5;
      const cy = (e.clientY - rect.top) / rect.height - 0.5;
      mouseX.set(cx * 2);
      mouseY.set(cy * 2);
    },
    [hoverEffect, mouseX, mouseY],
  );

  // Photo hover-wrapper transforms: parallax via x/y motion-values, scale via
  // animate prop op section-hover. Twee gescheiden wrappers vermijden conflict
  // met intro-variant scale (1.05->1) op de inner photo-wrapper.
  const hoverWrapperStyle: CSSProperties = {
    width: "55vw",
    ...maskStyle,
    ...photoIsolation,
    ...(hoverEffect === "parallax"
      ? ({ x: parallaxX, y: parallaxY } as unknown as CSSProperties)
      : {}),
  };
  const hoverAnimate =
    hoverEffect === "scale"
      ? { scale: sectionHover ? 1.02 : 1 }
      : undefined;
  const hoverTransition =
    hoverEffect === "scale"
      ? { duration: 0.6, ease: "easeOut" as const }
      : undefined;

  const eyebrowVariants = getIntroVariants(
    introStyle,
    "eyebrow",
    eyebrowDelay,
  );
  const photoVariants = getIntroVariants(introStyle, "photo", photoDelay);
  const sigVariants = getSigVariants(sigReveal, sigDelay);
  const fraunceNameVariants = getIntroVariants(introStyle, "text", sigDelay);
  const roleVariants = getIntroVariants(introStyle, "text", roleDelay);
  const body1Variants = getIntroVariants(introStyle, "text", body1Delay);
  const body2Variants = getIntroVariants(introStyle, "text", body2Delay);
  const skillsVariants = getIntroVariants(introStyle, "text", skillsDelay);
  const metaVariants = getIntroVariants(introStyle, "text", metaDelay);
  const ctaVariants = getIntroVariants(introStyle, "text", ctaDelay);

  return (
    <article
      ref={articleRef}
      aria-labelledby={`puna-${founder.id}-heading`}
      className="relative h-screen grid grid-rows-[auto_1fr] px-8 md:px-16 lg:px-24 py-8 md:py-12 overflow-hidden"
      style={{ isolation: "isolate" }}
      onMouseMove={
        hoverEffect === "parallax" ? handleMouseMove : undefined
      }
      onMouseEnter={
        hoverEffect === "scale" ? () => setSectionHover(true) : undefined
      }
      onMouseLeave={
        hoverEffect === "scale" ? () => setSectionHover(false) : undefined
      }
    >
      {/* Outer hover-wrapper: parallax (x/y) of scale animatie. Inner intro-
          wrapper: opacity/scale/y voor cinematic intro. Twee niveaus zodat
          hover-transformaties niet met intro-variant transformaties botsen. */}
      <motion.div
        className="absolute right-0 top-0 bottom-0 z-[1] pointer-events-none"
        style={hoverWrapperStyle}
        animate={hoverAnimate}
        transition={hoverTransition}
      >
        <motion.div
          className="absolute inset-0"
          initial={initialState}
          animate={animateState}
          variants={photoVariants}
        >
          <Image
            src={photoSourceUrl}
            alt={founder.photo.alt}
            fill
            sizes="55vw"
            className={photoClassName}
            style={imageInlineStyle}
          />
          {!isCutout ? (
            <PhotoTreatmentOverlays treatment={treatment} />
          ) : null}
        </motion.div>
      </motion.div>

      {/* Coords blijven static, geen intro-animatie. */}
      <p
        aria-hidden="true"
        className="absolute z-[2] text-[var(--color-andes-copper-bright)] text-[11px] tracking-[0.05em]"
        style={{
          ...MONO_SHADOW_STYLE,
          right: "24px",
          bottom: "24px",
        }}
      >
        {founder.coords}
      </p>

      <motion.p
        className="copper-glow self-start flex items-center gap-3 text-[var(--color-andes-copper-bright)] text-[12px] md:text-[13px] tracking-[0.08em] z-[3]"
        style={MONO_SHADOW_STYLE}
        initial={initialState}
        animate={animateState}
        variants={eyebrowVariants}
      >
        <span
          aria-hidden="true"
          className="block w-4 h-px bg-[var(--color-andes-copper-bright)]"
        />
        02 · Wie we zijn · {founder.index}
      </motion.p>

      <div className="self-end max-w-xl pb-6 md:pb-8 z-[3] flex flex-col">
        {useAllura ? (
          <>
            <h3 id={`puna-${founder.id}-heading`} className="sr-only">
              {founder.name}, {founder.role}
            </h3>
            <motion.div
              className="-ml-2 md:-ml-4"
              initial={initialState}
              animate={animateState}
              variants={sigVariants}
            >
              <SignatureMask founderId={founder.id} height={88} />
            </motion.div>
          </>
        ) : (
          <motion.h3
            id={`puna-${founder.id}-heading`}
            className="font-display italic text-warm-white text-[60px] md:text-[72px] lg:text-[80px] leading-[1.05] tracking-tight -ml-1 md:-ml-2"
            style={TEXT_SHADOW_STYLE}
            initial={initialState}
            animate={animateState}
            variants={fraunceNameVariants}
          >
            {founder.name}
          </motion.h3>
        )}

        <motion.p
          className="copper-glow-soft text-[var(--color-andes-copper-bright)] text-[13px] md:text-[14px] tracking-[0.08em] mt-3"
          style={MONO_STYLE}
          initial={initialState}
          animate={animateState}
          variants={roleVariants}
        >
          {founder.role}
        </motion.p>

        <motion.p
          className="copper-glow font-sans text-warm-white text-[16px] md:text-[18px] leading-[1.6] mt-6"
          style={TEXT_SHADOW_STYLE}
          initial={initialState}
          animate={animateState}
          variants={body1Variants}
        >
          {founder.body}
        </motion.p>

        <motion.p
          className="copper-glow font-sans text-warm-white text-[16px] md:text-[18px] leading-[1.6] mt-3"
          style={TEXT_SHADOW_STYLE}
          initial={initialState}
          animate={animateState}
          variants={body2Variants}
        >
          {founder.body2}
        </motion.p>

        <motion.div
          initial={initialState}
          animate={animateState}
          variants={skillsVariants}
        >
          <SkillsRow skills={founder.skills} style={skillsStyle} />
        </motion.div>

        <motion.p
          className="copper-glow-soft text-[var(--color-andes-copper-bright)]/85 text-[11px] md:text-[12px] tracking-[0.05em] mt-6"
          style={MONO_STYLE}
          initial={initialState}
          animate={animateState}
          variants={metaVariants}
        >
          {founder.meta}
        </motion.p>

        {founder.cta !== null ? (
          <motion.a
            href={founder.cta.href}
            className="copper-glow-soft inline-flex items-center gap-2 text-[var(--color-andes-copper-bright)] text-[14px] mt-8 underline-offset-4 hover:underline w-fit"
            initial={initialState}
            animate={animateState}
            variants={ctaVariants}
          >
            {founder.cta.label}
            <span aria-hidden="true">→</span>
          </motion.a>
        ) : null}
      </div>
    </article>
  );
}
