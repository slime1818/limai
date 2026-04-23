import { BiomeScroller } from "./components/BiomeScroller";
import { ScrollProgressDots } from "./components/ScrollProgressDots";
import { biomes } from "./data/biomes";

export default function Home() {
  return (
    <>
      <BiomeScroller biomes={biomes} />
      <ScrollProgressDots biomes={biomes} />
    </>
  );
}
