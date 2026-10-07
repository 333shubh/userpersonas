# Mascot style v3: the designer-toy series

Status: **current (v3.1, streetwear creatures), 2026-10-07.** Supersedes `mascot-style-v2.md` (2D illustration). Decided by the project lead after reviewing 20 art-toy references in `brief/references/inspo/mascots-v3/`. Machine values live in `system/tokens/tokens.json` (`brand.toy` and `persona.*.mascot.toy`); each persona file shows its figure's spec in section 11.

## 1. Stance

**Seven figures, one shelf.** The mascots are a 3D designer vinyl art-toy series, like a collectible blind-box line, in one style rule: **streetwear creatures**. Human-style bodies, poses and streetwear, with creature heads and skin (cat, devil-imp, axolotl, sprite, glow-creature, box-head, black cat). One shared body makes them one universe; each creature, material and set of props makes them seven worlds.

- **Keywords:** collectible, tactile, characterful.
- **Anti-keywords:** generic shiny 3D, food objects as heads, ordinary human faces, costume stereotype.
- **The key idea:** in designer toys, the material is the design language. Each persona's colour constraint becomes a toy finish.

## 2. Persona constraint becomes material

| Mascot | Creature | Persona rule (Section 18.12) | Toy material and finish | References |
|---|---|---|---|---|
| Cram | Sleepy cat-eared creature in a beanie and hoodie | Strict black and white, one-colour print | Matte white vinyl with black screen-printed halftone; no coloured light | 18, 4, 13, 9 |
| Riot | Red devil-imp, spiky flame hair, horns | Controlled clash | High-gloss chili-red vinyl covered in sticker decals; clash pairs only | 15, 1, 3, 14 |
| Nest | Grown-up pastel axolotl in an apron | No sharp corners, kid-near | Soft-touch matte vinyl, airbrushed cream-to-peach gradient | 6, 17 |
| Sprig | Frosted sprite with a sprout | Natural, low-ink | Frosted translucent resin in muted leaf green | 12, 20 |
| Lull | Round dark glow-creature | Luminance-capped dark | Matte dusk-violet vinyl with glow-in-the-dark details | 11 |
| Stack | Box-head figure with a price tag | Strict grid, stamp, price tag | Kraft cardboard carton head on a navy body | 8, 10 |
| Mise | Sleek black-cat gentleman | Duotone plus one foil | Satin oxblood vinyl with exactly one gold-foil detail | 1, 19, 9 |

## 3. The shared body (one universe)

- **Head:** a creature head (ears, horns, gill-frills, glow eyes, carton), about 38% of figure height, with non-human skin colours. **Never a food object, never an ordinary human face, never a child face.**
- **Body:** human-style torso and limbs with relaxed streetwear posture, 4-finger hands sized to hold a real MAGGI pack, chunky rounded shoes, an 8 mm round display base.
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

- No ordinary human faces and no child faces; Nest is a grown-up creature and children appear only as toy-scale hands.
- No cultural costume or caricature.
- No health claims; real pack badges stay illegible.
- Learn from the references' principles (proportion, material, finish), never copy a specific toy or artist.
