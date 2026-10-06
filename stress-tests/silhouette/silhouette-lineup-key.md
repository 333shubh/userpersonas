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
- Arms: 40-unit capsule from the shoulder, 32-radius hand.
- Sachet: brand geometry 160 × 240, 8-unit crimp teeth top and bottom, 16 × 12 tear notch 24 below the top crimp, held alone in `grip-r` (screen-left in front view).

## Rig spec v0.1.1 changes applied
- **Cram:** fork (220 tall, upright) moved to `grip-l`, hand raised to (800, 600) so the fork clears the earcup. The sachet hangs alone from `grip-r`.
- **Nest:** dome h:w 0.87 (538 × 620). The 120-wide bow loops sit behind the dome and show at both sides at 60% height (y 573), with punched counters. Nothing sits on top. The sachet is raised to clear the left loop.
- **Lull:** unchanged (notch 0.6r centred 0.65r at 45° up-right, now in the spec).

## Remaining notes
1. **Cram headphone arc r 190** (−5%, within tolerance).
2. **Sprig head dome rx 180 / ry 200, stem 125.** Needed to reach 660 with the §7 leaf numbers.
3. **Lull stars** Ø39 (+8%) with fat 4-point cores.
4. **Mise chopsticks** cross 30% up each stick; the tops reach y 141.
5. **Cram vs Stack:** Stack's steps are 60 units. At 32px the price-tag flag carries most of the difference, and Cram's fork now sits on the opposite side to Stack's tag.
6. **Nest at 32px:** the side loops read as small ears on the dome. If they get lost in the test, the +8% allowance takes them to 130 wide.
