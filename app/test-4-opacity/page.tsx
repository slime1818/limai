"use client";

import Image from "next/image";
import { motion, useScroll, useTransform } from "motion/react";
import { createRef, useRef, type RefObject } from "react";
import { biomes, type Biome } from "../data/biomes";

const F6_SCRIM =
  "linear-gradient(90deg, rgba(26,22,18,0.68) 0%, rgba(26,22,18,0.45) 30%, rgba(26,22,18,0.08) 55%, rgba(26,22,18,0.0) 72%)";

function FixedLayer({
  biome,
  sectionRef,
  isFirst,
  isLast,
  priority,
}: {
  biome: Biome;
  sectionRef: RefObject<HTMLElement | null>;
  isFirst: boolean;
  isLast: boolean;
  priority: boolean;
}) {
  const { scrollYProgress } = useScroll({
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
  const opacity = useTransform(
    scrollYProgress,
    [(1 / 3) - 0.2, 1 / 3, 0.8, 1],
    opacityOutput,
  );
  return (
    <motion.div className="absolute inset-0 pointer-events-none" style={{ opacity }}>
      <div className="relative h-full w-full overflow-hidden">
        <Image
          src={biome.image}
          alt={biome.imageAlt}
          fill
          sizes="100vw"
          className="object-cover"
          priority={priority}
        />
        <div
          aria-hidden="true"
          className="absolute inset-0"
          style={{ background: F6_SCRIM }}
        />
      </div>
    </motion.div>
  );
}

// Diagnostic: test-3 plus motion useScroll + useTransform opacity-crossfade per fixed layer.
// Geen altitude-pan nog. Test of motion scroll-listener churn tijdens scroll de reversal
// triggert.
export default function Test4OpacityPage() {
  const sectionRefs = useRef<Array<RefObject<HTMLElement | null>>>(
    biomes.map(() => createRef<HTMLElement>()),
  );
  return (
    <>
      <div className="fixed top-2 right-2 bg-black/80 text-white font-mono text-xs p-2 z-50 rounded-sm pointer-events-none">
        test-4-opacity
      </div>
      <div className="fixed inset-0 w-full h-screen pointer-events-none z-0">
        {biomes.map((biome, i) => (
          <FixedLayer
            key={biome.id}
            biome={biome}
            sectionRef={sectionRefs.current[i]}
            isFirst={i === 0}
            isLast={i === biomes.length - 1}
            priority={i === 0}
          />
        ))}
      </div>
      {biomes.map((biome, i) => (
        <section
          key={biome.id}
          ref={sectionRefs.current[i]}
          className="relative w-full h-[200vh]"
        >
          <div className="h-screen flex items-center px-8 md:px-16">
            <div className="max-w-2xl relative z-10">
              <h1 className="font-display text-warm-white text-5xl md:text-7xl leading-none tracking-tight">
                {biome.title}
              </h1>
              <p className="mt-6 max-w-xl text-base md:text-lg text-warm-white/90 leading-relaxed">
                {biome.tagline}
              </p>
            </div>
          </div>
        </section>
      ))}
    </>
  );
}
