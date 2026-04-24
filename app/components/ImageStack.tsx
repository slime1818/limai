"use client";

import Image from "next/image";
import {
  motion,
  useInView,
  useMotionValueEvent,
  useReducedMotion,
  useScroll,
  useTransform,
} from "motion/react";
import { useEffect, useState, type RefObject } from "react";
import type { Biome } from "../data/biomes";
import { useIsCoarsePointer } from "../hooks/useIsCoarsePointer";
import { debugCounters } from "../lib/debug-counters";
import { BiomeScrim } from "./BiomeScrim";

function BiomeLayer({
  biome,
  sectionRef,
  isFirst,
  isLast,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
  isFirst: boolean;
  isLast: boolean;
}) {
  const isCoarsePointer = useIsCoarsePointer();
  const shouldDecode = useInView(sectionRef, {
    // Strictere lazy-load op mobile (pas bij in-view decode) om GPU-memory druk te beperken.
    // Desktop houdt 50% pre-roll voor smoother first-paint tijdens fade-in.
    margin: isCoarsePointer ? "0% 0px" : "50% 0px",
    once: true,
  });
  const shouldReduceMotion = useReducedMotion();

  // Opacity crossfade via widened thresholds: fade-in 0-0.3, plateau 0.3-0.7, fade-out 0.7-1.
  // isFirst (Apu) skips fade-in so pageload shows full opacity immediately.
  // isLast (Pacifico) skips fade-out so section-end doesn't reveal empty background.
  const { scrollYProgress: viewProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });
  const opacityOutput: [number, number, number, number] =
    isFirst && isLast
      ? [1, 1, 1, 1]
      : isFirst
        ? [1, 1, 1, 0]
        : isLast
          ? [0, 1, 1, 1]
          : [0, 1, 1, 0];
  // Fade-in begins 540px before section-top (1/3 - 0.2), reaches plateau at section-top (1/3), fade-out begins at 0.8 for 540px symmetrical zone.
  const opacity = useTransform(
    viewProgress,
    [(1 / 3) - 0.2, 1 / 3, 0.8, 1],
    opacityOutput,
  );

  // Mobile GPU-compositing reductie via visibility-pruning. Layers met opacity < 0.01
  // krijgen visibility:hidden zodat de compositor ze kan skippen. Typisch 1 layer visible
  // tijdens plateau-zones, 2 tijdens crossfade-zones. Desktop (fine pointer) blijft altijd
  // visible voor smooth render gedurende full page-scroll.
  const [isMobileVisible, setIsMobileVisible] = useState(true);
  useMotionValueEvent(opacity, "change", (v) => {
    debugCounters.motionEvents++;
    if (!isCoarsePointer) return;
    const nowVisible = v > 0.01;
    setIsMobileVisible((prev) => (prev !== nowVisible ? nowVisible : prev));
  });
  // Initial-sync: useMotionValueEvent fires alleen op CHANGE, niet op mount. Layers wiens
  // opacity nooit van default-waarde verandert (zoals Puna op pageload, opacity 0 static)
  // zouden isMobileVisible=true houden. Deze effect syncs bij coarse-pointer activation.
  useEffect(() => {
    if (!isCoarsePointer) return;
    const nowVisible = opacity.get() > 0.01;
    setIsMobileVisible((prev) => (prev !== nowVisible ? nowVisible : prev));
  }, [isCoarsePointer, opacity]);
  const computedVisibility =
    !isCoarsePointer || isMobileVisible ? "visible" : "hidden";

  // Altitude-pan tracks own section scroll progress, -8% to +8% translateY.
  const { scrollYProgress: panProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });
  // Altitude-pan uit op coarse pointer (touch devices) voor mobile GPU-compositing
  // reductie. 6 fixed-position layers plus parallel transforms stapelen op mobile GPU,
  // zichtbaar als progressieve scroll-stuttering vanaf biome 4+ op iPhone. Desktop
  // (fine pointer) behoudt volle -15% tot +15% range.
  const y = useTransform(
    panProgress,
    [0, 1],
    shouldReduceMotion || isCoarsePointer ? ["0%", "0%"] : ["-15%", "15%"],
  );

  const renderImage = isFirst || shouldDecode;

  return (
    <motion.div
      className="absolute inset-0 pointer-events-none"
      style={{ opacity, visibility: computedVisibility }}
    >
      {renderImage ? (
        <>
          <motion.div
            className="absolute inset-x-0 top-[-25%] bottom-[-25%] will-change-transform"
            style={{ y }}
          >
            <Image
              src={biome.image}
              alt={biome.imageAlt}
              fill
              priority={isFirst}
              sizes="100vw"
              className="object-cover"
            />
          </motion.div>
          <BiomeScrim biome={biome} />
        </>
      ) : null}
    </motion.div>
  );
}

export function ImageStack({
  biomes,
  sectionRefs,
}: {
  biomes: Biome[];
  sectionRefs: Array<RefObject<HTMLElement | null>>;
}) {
  return (
    <div className="fixed inset-0 w-full h-dvh pointer-events-none z-0">
      {biomes.map((biome, i) => (
        <BiomeLayer
          key={biome.id}
          biome={biome}
          sectionRef={sectionRefs[i]}
          isFirst={i === 0}
          isLast={i === biomes.length - 1}
        />
      ))}
    </div>
  );
}
