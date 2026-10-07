# Mascot style v3: the designer-toy series

Status: **current, 2026-10-07.** Supersedes `mascot-style-v2.md` (2D illustration). Decided by the project lead after reviewing 20 art-toy references in `brief/references/inspo/mascots-v3/`. Machine values live in `system/tokens/tokens.json` (`brand.toy` and `persona.*.mascot.toy`); each persona file shows its figure's spec in section 11.

## 1. Stance

**Seven figures, one shelf.** The mascots are a 3D designer vinyl art-toy series, like a collectible blind-box line. One shared toy body makes them one universe; each head, material and set of props makes them seven worlds.

- **Keywords:** collectible, tactile, characterful.
- **Anti-keywords:** generic shiny 3D, human faces, costume stereotype.
- **The key idea:** in designer toys, the material is the design language. Each persona's colour constraint becomes a toy finish.

## 2. Persona constraint becomes material

| Mascot | Persona rule (Section 18.12) | Toy material and finish | References |
|---|---|---|---|
| Cram | Strict black and white, one-colour print | Matte white vinyl with black screen-printed halftone; no coloured light | 13, 9, 2, 16 |
| Riot | Controlled clash | High-gloss chili-red vinyl covered in sticker decals; clash pairs only | 15, 4, 3, 14 |
| Nest | No sharp corners, kid-near | Soft-touch matte vinyl, airbrushed cream-to-peach gradient | 6, 17, 18 |
| Sprig | Natural, low-ink | Frosted translucent resin in muted leaf green | 12, 20 |
| Lull | Luminance-capped dark | Matte dusk-violet vinyl with glow-in-the-dark details | 11 |
| Stack | Strict grid, stamp, price tag | Kraft cardboard carton head with tape and a printed price tag | 8, 10 |
| Mise | Duotone plus one foil | Satin oxblood vinyl with exactly one gold-foil detail | 1, 19, 9 |

## 3. The shared body (one universe)

- **Head:** the food object itself (cup, chili, nest, sprout bowl, moon bowl, carton, footed bowl), 45% of figure height. Eyes and mouth are printed or sculpted on it. **No human faces.**
- **Body:** compact torso, short limbs with soft elbow and knee bends, 4-finger mitten hands sized to hold a real MAGGI pack, chunky rounded shoes, an 8 mm round display base.
- **Outfit:** contemporary streetwear chosen per persona. Never cultural or national dress.
- **Pack:** each figure holds its real MAGGI pack at 1:6 scale as a separate prop; health badges are printed illegible. Cram's pack is a one-ink print.
- **Scale:** a 15 cm figure equivalent. All seven stand on the same base height; differences come from heads and hair.

## 4. Render rules

| | |
|---|---|
| Hero camera | Three-quarter view, 35° off front, eye level at chest height, 85 mm lens look |
| Turntable | 8 views at 45° steps |
| Studio light | Large key 45° top-left, fill at 30% from the right, rim light from behind, soft contact shadow on the base |
| Scene light | Each persona's hour (section 10 of its file); Lull and Mise always use scene light |
| Background | Seamless sweep in the persona's `role.bg`, plus a transparent PNG |
| Colour | Token colours only for the figure and set; the real pack keeps its own print |
| Output | 2048 × 2048 PNG with alpha |

## 5. Deliverables per mascot

1. Hero render holding the pack.
2. 8-view turntable sheet.
3. Three poses: hero with pack, sachet moment, reaction.
4. Material callout sheet: head, body, outfit and prop finishes with token colours.
5. For the series: a lineup of all seven on one shelf, and the 32 px silhouette lineup.

## 6. Production path

Claude Design cannot model or render 3D. It produces **model sheets** (front, side, back orthographic views plus material callouts). The 3D figures are then made in Blender or Spline, or generated from the model sheets with an image tool and checked for consistency. Rendered PNGs flow into the existing pipeline: silhouette, colour and naming checks, cards, stickers, the overview and the PDF.

## 7. Guardrails

- No human or child faces; Nest's children appear only as toy-scale hands.
- No cultural costume or caricature.
- No health claims; real pack badges stay illegible.
- Learn from the references' principles (proportion, material, finish), never copy a specific toy or artist.
