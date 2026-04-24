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
  const opacity = useTransform(
    viewProgress,
    [(1 / 3) - 0.2, 1 / 3, 0.8, 1],
    opacityOutput,
  );

  const { scrollYProgress: panProgress } = useScroll({
    target: sectionRef,
    offset: ["start start", "end end"],
  });
  const y = useTransform(panProgress, [0, 1], ["-15%", "15%"]);

  return (
    <motion.div className="absolute inset-0 pointer-events-none" style={{ opacity }}>
      <motion.div
        className="absolute inset-x-0 top-[-25%] bottom-[-25%] will-change-transform"
        style={{ y }}
      >
        <Image
          src={biome.image}
          alt={biome.imageAlt}
          fill
          sizes="100vw"
          className="object-cover"
          priority={priority}
        />
      </motion.div>
      <div
        aria-hidden="true"
        className="absolute inset-0"
        style={{ background: F6_SCRIM }}
      />
    </motion.div>
  );
}

// Diagnostic: test-5 plus absolute inset-0 content layers met 2-viewport h-dvh structuur
// binnen sections (matcht production BiomeSection pattern). Functioneel equivalent aan
// production homepage (minus ScrollProgressDots, teasers, CTAs).
export default function Test6ContentAbsPage() {
  const sectionRefs = useRef<Array<RefObject<HTMLElement | null>>>(
    biomes.map(() => createRef<HTMLElement>()),
  );
  return (
    <>
      <div className="fixed top-2 right-2 bg-black/80 text-white font-mono text-xs p-2 z-50 rounded-sm pointer-events-none">
        test-6-content-abs
      </div>
      <div className="fixed inset-0 w-full h-dvh pointer-events-none z-0">
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
          className="relative w-full h-[200dvh]"
        >
          <div className="absolute inset-0 z-10">
            <div className="h-dvh flex items-center px-8 md:px-16">
              <div className="max-w-2xl">
                <h1 className="font-display text-warm-white text-5xl md:text-7xl leading-none tracking-tight">
                  {biome.title}
                </h1>
                <p className="mt-6 max-w-xl text-base md:text-lg text-warm-white/90 leading-relaxed">
                  {biome.tagline}
                </p>
              </div>
            </div>
            <div className="h-dvh" />
          </div>
        </section>
      ))}
    </>
  );
}
