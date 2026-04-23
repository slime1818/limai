# Future work, pre-launch polish

Low-prioriteit items buiten de huidige fase-scope. Adresseer wanneer content-pass, launch prep (Fase 5), of budget-ruimte ontstaat. Geen blockers.

## Apu widescreen composite-variant

Huidige Apu composite is 4:3 (1024x768). Op wider-dan-4:3 viewports wordt full-width + bottom-crop gedaan (per commit cbdc650). Dit werkt visueel maar verliest framing-rock in de crop op ultrawide monitors. Een wider-aspect variant (16:9 of 21:9) zou banden boven en onder mogelijk maken met framing-rock zichtbaar. Re-render kost Flux-budget plus 3-5 uur iteratie, visuele ROI beperkt tot ultrawide gebruikers.

## Paracas composite re-render overwegen

Intake Fase 2 substep 1 bevestigde dat Paracas de zwakste van de 6 composites is qua framing-anchor. Het framing-dune-element rechts onderaan is te klein om de frame te dragen, compositie leest als wide-pan landschap ipv immersive-descent. Scrim plus tekst werken functioneel. Re-render overwegen voor stronger framing-anchor, **prioriteit laag**. Pragmatic_acceptance learning gold bij intake, deze flag is voor toekomstige polish-pass als de content-quality op andere biomes hoger ligt.
