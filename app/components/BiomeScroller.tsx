"use client";

import { createRef, useRef, type RefObject } from "react";
import type { Biome } from "../data/biomes";
import { useActiveBiomeIndex } from "../hooks/useActiveBiomeIndex";
import { useIsCoarsePointer } from "../hooks/useIsCoarsePointer";
import { BiomeSection } from "./BiomeSection";
import { ImageStack } from "./ImageStack";

export function BiomeScroller({ biomes }: { biomes: Biome[] }) {
  const sectionRefs = useRef<Array<RefObject<HTMLElement | null>>>(
    biomes.map(() => createRef<HTMLElement>()),
  );
  const activeIndex = useActiveBiomeIndex(biomes.length);
  const isCoarsePointer = useIsCoarsePointer();

  return (
    <>
      <ImageStack biomes={biomes} sectionRefs={sectionRefs.current} />
      {biomes.map((biome, i) => {
        // Mobile content-pruning: alleen active biome's content-layer rendert op coarse
        // pointer. Andere sections behouden section-height via de lege ref-wrapper voor
        // scroll-progress tracking. Voorkomt iOS Safari text-repaint load tijdens scroll.
        const renderContent = !isCoarsePointer || i === activeIndex;
        return (
          <BiomeSection
            key={biome.id}
            biome={biome}
            sectionRef={sectionRefs.current[i]}
            renderContent={renderContent}
          />
        );
      })}
    </>
  );
}
