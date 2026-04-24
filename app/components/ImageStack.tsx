"use client";

import Image from "next/image";
import {
  motion,
  useInView,
  useReducedMotion,
  useScroll,
  useTransform,
} from "motion/react";
import type { RefObject } from "react";
import type { Biome } from "../data/biomes";
import { BiomeScrim } from "./BiomeScrim";

function BiomeLayer({
  biome,
  sectionRef,
  isFirst,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
  isFirst: boolean;
}) {
  const shouldDecode = useInView(sectionRef, {
    margin: "50% 0px",
    once: true,
  });
  const shouldReduceMotion = useReducedMotion();

  // Opacity tracks own section visibility in viewport (9a narrow-step, 9c widens).
  const { scrollYProgress: viewProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });
  const opacity = useTransform(
    viewProgress,
    [0, 0.333, 0.99, 1],
    [0, 1, 1, 0],
  );

  // Altitude-pan tracks own section scroll progress, -8% to +8% translateY.
  const { scrollYProgress: panProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });
  const y = useTransform(
    panProgress,
    [0, 1],
    shouldReduceMotion ? ["0%", "0%"] : ["-15%", "15%"],
  );

  const renderImage = isFirst || shouldDecode;

  return (
    <motion.div
      className="absolute inset-0 pointer-events-none"
      style={{ opacity }}
    >
      {renderImage ? (
        <>
          <motion.div
            className="absolute inset-x-0 top-[-20%] bottom-[-20%] will-change-transform"
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
        />
      ))}
    </div>
  );
}
