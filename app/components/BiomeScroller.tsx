"use client";

import { createRef, useRef, type RefObject } from "react";
import type { Biome } from "../data/biomes";
import { BiomeSection } from "./BiomeSection";
import { ImageStack } from "./ImageStack";

export function BiomeScroller({ biomes }: { biomes: Biome[] }) {
  const sectionRefs = useRef<Array<RefObject<HTMLElement | null>>>(
    biomes.map(() => createRef<HTMLElement>()),
  );

  return (
    <>
      <ImageStack biomes={biomes} sectionRefs={sectionRefs.current} />
      {biomes.map((biome, i) => (
        <BiomeSection
          key={biome.id}
          biome={biome}
          sectionRef={sectionRefs.current[i]}
        />
      ))}
    </>
  );
}
