"use client";

import { createRef, useState, type RefObject } from "react";
import type { Biome } from "../data/biomes";
import { ApuSection } from "./ApuSection";
import { BiomeSection } from "./BiomeSection";
import { ImageStack } from "./ImageStack";

export function BiomeScroller({ biomes }: { biomes: Biome[] }) {
  // useState lazy initializer ipv useRef of useMemo: garandeert stable identity
  // van de createRef-array over alle renders heen, zonder .current access tijdens
  // render (react-hooks/refs lint clean). Setter wordt nooit aangeroepen.
  const sectionRefs = useState<Array<RefObject<HTMLElement | null>>>(
    () => biomes.map(() => createRef<HTMLElement>()),
  )[0];

  return (
    <>
      <ImageStack biomes={biomes} sectionRefs={sectionRefs} />
      {biomes.map((biome, i) =>
        biome.id === "apu" ? (
          <ApuSection
            key={biome.id}
            biome={biome}
            sectionRef={sectionRefs[i]}
          />
        ) : (
          <BiomeSection
            key={biome.id}
            biome={biome}
            sectionRef={sectionRefs[i]}
          />
        ),
      )}
    </>
  );
}
