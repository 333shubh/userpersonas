# Silhouette lineup key

Reviewer: name all seven from `silhouette-lineup-224x32.png` **before** opening this file.

| Cell | x range (px, master) | Mascot | SVG group |
|---|---|---|---|
| 1 | 0–1023 | Sprig | `<g id="sprig">` |
| 2 | 1024–2047 | Stack | `<g id="stack">` |
| 3 | 2048–3071 | Cram | `<g id="cram">` |
| 4 | 3072–4095 | Nest | `<g id="nest">` |
| 5 | 4096–5119 | Riot | `<g id="riot">` |
| 6 | 5120–6143 | Mise | `<g id="mise">` |
| 7 | 6144–7167 | Lull | `<g id="lull">` |

Order = Section 18.5 day order. Fill `#000000`, background `#FFFFFF`, no strokes. Each cell: ground y 896, centre x 512, height = heightRatio × 768.

## Shared family traits (all seven)
- Ground line y 896, every base sits on it.
- Arms: 40-unit capsule from shoulder, 32-radius hand. Mascot-left arm always drops 85/85 units down-out.
- Sachet: brand geometry 160 × 240, 8-unit crimp teeth top and bottom, 16 × 12 tear notch 24 below the top crimp, held in `grip-r` (screen-left in front view).

## Interpretations to confirm (spec conflicts or gaps)
1. **Cram, fork + sachet both in grip-r.** rig-spec §7 puts the fork in grip-r and the handoff puts the sachet there too. Here the hand holds the sachet by its top crimp, with the fork rising 220 above the hand. If you want the fork in grip-l, it would read more clearly. Needs a decision.
2. **Cram headphone arc r 190** (−5%, within tolerance). This keeps a gap between the earcup and the fork head at 32px.
3. **Sprig head dome rx 180 / ry 200, stem 125.** Bowl 220 + stem 120 + 35° leaves (140 × 70) only adds up to 660 if the dome is this tall.
4. **Nest bows above the dome.** A dome with h:w 0.65 (403 tall) plus loops 120 wide only reaches 538 if the loops rise above the dome top. The loops have punched counters.
5. **Lull crescent notch:** circle 0.6r (120), centre 0.65r (130) from the head centre at 45° up-right. Read literally as a 0.35r offset, the notch circle would sit fully inside the head and become a hole, not a bite. Stars are Ø39 (+8%, the edge-case allowance) with fat 4-point cores so they survive at 32px.
6. **Mise chopsticks** are 520 long at 30° from vertical and cross 120 above the rim, 30% of the way up each stick. The tops reach y 141 (height 755, −2%).
7. **Stack**'s steps are only 60 units each (fixed by the block widths). At 32px the price-tag flag carries most of the difference from Cram, and the steps are second. This is the pair to test first.
