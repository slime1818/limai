"use client";

import { useState } from "react";
import { useMotionValueEvent, useScroll } from "motion/react";

// Crossover-based active-biome detection. Switch-moment ligt op het visuele
// zwaartepunt van de ImageStack crossfade, niet op de section-boundary.
// For section N, switch fires bij scrollY = N * sectionHeight - crossfadeHalf
// (zie ImageStack thresholds [1/3 - 0.2, 1/3, 0.8, 1]: 0.15 = half van
// 0.3 fade-ratio = half-crossfade-width).
export function useActiveBiomeIndex(sectionCount: number): number {
  const [activeIndex, setActiveIndex] = useState(0);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (v) => {
    const sectionHeight = window.innerHeight * 2;
    const crossfadeHalf = sectionHeight * 0.15;
    const newIndex = Math.min(
      sectionCount - 1,
      Math.max(0, Math.floor((v + crossfadeHalf) / sectionHeight)),
    );
    setActiveIndex((prev) => (prev !== newIndex ? newIndex : prev));
  });

  return activeIndex;
}
