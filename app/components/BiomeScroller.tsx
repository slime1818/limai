import type { Biome } from "../data/biomes";
import { BiomeSection } from "./BiomeSection";

export function BiomeScroller({ biomes }: { biomes: Biome[] }) {
  return (
    <>
      {biomes.map((biome, index) => (
        <BiomeSection key={biome.id} biome={biome} priority={index === 0} />
      ))}
    </>
  );
}
