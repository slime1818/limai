import { BiomeScroller } from "./components/BiomeScroller";
import { biomes } from "./data/biomes";

export default function Home() {
  return <BiomeScroller biomes={biomes} />;
}
