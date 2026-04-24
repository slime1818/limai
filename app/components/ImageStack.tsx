"use client";

import Image from "next/image";
import {
  motion,
  useInView,
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
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });
  // 9a narrow-step opacity: 1 during own section in viewport, 0 otherwise.
  // 9c will widen transition zones for proper crossfade.
  const opacity = useTransform(
    scrollYProgress,
    [0, 0.333, 0.99, 1],
    [0, 1, 1, 0],
  );

  const renderImage = isFirst || shouldDecode;

  return (
    <motion.div
      className="absolute inset-0 pointer-events-none"
      style={{ opacity }}
    >
      {renderImage ? (
        <>
          <Image
            src={biome.image}
            alt={biome.imageAlt}
            fill
            priority={isFirst}
            sizes="100vw"
            className="object-cover"
          />
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
