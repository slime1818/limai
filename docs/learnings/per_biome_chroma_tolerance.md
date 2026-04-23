# Per-biome chroma tolerance

## Lesson
Chroma-extraction tolerance is NIET architecturaal cross-biome gedeeld. Elke biome's painterly palette bepaalt z'n eigen veilige tolerance — forceren van cross-biome consistency breekt extraction op biomes wiens natural dark-pixel range overlapt met strict is_pinkish bounds.

## Validation
- Attempted tolerance 130 + relaxed is_pinkish cross-biome voor Yungas parity: Apu mountain kreeg zwarte chunks (rock shadows weggesneden), Puna bushes kregen zwarte gaten (donkere foliage weggesneden). Reverted.
- Production matrix:
  - Apu (cool rock + snow + warm bronze plateau): tolerance 55, strict is_pinkish (R>180, B>120, G<90)
  - Puna (altiplano bronze + ichu tussocks): tolerance 55, strict
  - Yungas (warm jungle greens + wet cloud-forest): tolerance 130, relaxed is_pinkish
  - Selva (deep saturated warm greens + humid browns): tolerance 130, relaxed
  - Paracas (warm bronze desert): tolerance 80
  - Pacifico (muted cool-grey ocean): tolerance 80, strict

## Pattern
Nieuwe biome krijgt tolerance bepaald door dominant palette karakter:

- Cool/muted (grey, rock, water, snow): tolerance 55-80 + strict is_pinkish — ruime marge tussen dark-pixels en chroma space
- Warm/saturated (jungle greens, wet browns): tolerance 130 + relaxed — dark-pixels in de painting zitten closer bij chroma space
- Bronze/warm earth (desert): tolerance 80 + strict

Als compositing shows black holes in opaque zones → tolerance te hoog of is_pinkish te relaxed. Als magenta bleed visible in composite → tolerance te laag.

## Bug to watch for
Sample locations matter. Pacifico plateau v2 had een eerste chroma-sample bug: top-center sample hit mist-exit warm tan, niet magenta. Fix was sample relocation to bottom-center (guaranteed magenta strip zone). Voor sky-subject met 45-50% magenta strip: sample from lower-center, niet upper-center.
