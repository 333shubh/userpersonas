# Image-generator prompts: the streetwear-creature toy series

For Midjourney (recommended) or ChatGPT's image tool. Built from `system/mascot-style-v3.md` and `tokens.json` (`brand.toy`, `persona.*.mascot.toy`). References are in `brief/references/inspo/mascots-v3/` (ref numbers below).

## Workflow

1. **Pilot first.** Generate **Cram** and **Riot** only (the two required extremes). Approve them before the other five, because they set the series look.
2. **Style reference.** Upload refs **10, 16 and 20** (series line-ups) as the *style reference* on every prompt. This is what makes seven figures look like one collection.
3. **Character references.** Also attach the per-mascot refs listed below as image prompts. Use them for material and attitude only, never to copy a specific toy.
4. **Lock each figure.** When a hero render is right, use it as the *character reference* (Midjourney's omni or character reference) for that mascot's turntable and poses, so the character stays the same.
5. **Real pack.** Generate the figure holding a **plain pack in the right colours**. AI tools garble logos and small print, so the real MAGGI pack image from `brief/references/packs/` is composited on afterwards with `tools/composite-packs.py` (measured pack corners per render, hands kept in front, relit from the render; output `NN-mascot-hero-with-pack.png`).
6. **Check.** Drop finished renders (2048 × 2048 PNG) in the repo; the silhouette, colour and naming checks run on them.

## The series prompt (prefix for every figure)

```
3D designer vinyl art toy, collectible blind-box figure, streetwear creature character: human-style body, pose and streetwear outfit with a non-human creature head and skin, head about 38% of figure height, 4-finger hands, chunky rounded sneakers, standing directly on the ground (no display base). Smooth sculpted vinyl, crisp clean edges, studio product render, three-quarter view 35 degrees off front, eye level at chest height, 85mm lens, large soft key light top-left, gentle fill from the right, rim light from behind, soft contact shadow, seamless background sweep, centred, full figure in frame, high detail, no text
```

**Avoid on every prompt** (Midjourney `--no`, or "do not include" in ChatGPT): `realistic human face, child, baby, food as a head, logo, brand name, readable text, watermark, extra fingers, cultural costume`.

**Midjourney settings:** square format (`--ar 1:1`), the style reference from step 2, and the avoid list above as `--no`.

## Per mascot

Add the line for each mascot after the series prompt.

| Mascot | Add to the prompt | Background sweep | Attach refs |
|---|---|---|---|
| **Cram** | `a sleepy cat-eared creature with half-closed eyes, cat ears poking through an oversized beanie, oversized grey hoodie printed with a timetable grid, black headphones, backpack, holding a fork upright and a plain noodle pack; entirely black and white: matte white vinyl with black screen-printed halftone graphics, monochrome, no colour at all` | white #FFFFFF | 18, 4, 13, 9 |
| **Riot** | `a mischievous red devil-imp with spiky flame-shaped hair in yellow and red, two small horns, a pointed tail, one big eye and one small eye, wide shouting grin, glossy chili-red skin covered in die-cut sticker decals, volt-blue puffer jacket with orange trim, holding a plain red noodle pack high and squeezing a chili sauce pouch, leaning back mid-shout` | warm cream #FFF6E0 | 15, 1, 3, 14 |
| **Nest** | `a calm grown-up pastel axolotl creature with soft feathery gill-frills at the sides of its head, kind eyes, soft-touch matte vinyl with an airbrushed cream-to-peach gradient, knit apron over a soft cardigan, rounded clogs, holding a wooden spoon and a plain yellow noodle pack, everything rounded with no sharp edges` | cream #FFF3E0 | 6, 17 |
| **Sprig** | `a calm frosted translucent sprite with a smooth rounded head and a small two-leaf sprout growing from the crown, muted leaf-green frosted resin with soft inner glow, relaxed linen overshirt in wheat colour, canvas shoes, holding fresh greens and a plain green noodle pack, balanced level pose, low saturation` | natural paper #F2EDE1 | 12, 20 |
| **Lull** | `a cozy round dark creature with a smooth blob head and glowing half-moon eyes, matte dusk-violet vinyl with glow-in-the-dark details, oversized hoodie with a blanket worn as a cape, soft slippers, cradling a plain noodle cup in both hands with glowing steam that turns into three small stars, lit only by one warm lamp in near-darkness` | deep blue-violet #121127 | 11 |
| **Stack** | `a sturdy box-head character whose head is a taped kraft cardboard carton with printed square eyes and a hanging price tag, navy vinyl body, navy work jacket with a blue stripe, boxy boots, holding a stack of plain yellow noodle packs, planted upright pose` | warm paper #F5EBD7 | 8, 10 |
| **Mise** | `a sleek long-limbed black-cat gentleman with tall pointed ears, long whiskers, calm half-lidded eyes and a thin tail, satin oxblood vinyl, tailored long oxblood coat, sleek boots, holding gold chopsticks that lift a long noodle ribbon and a plain dark red noodle pack, elegant pose, low warm pendant light with rich shadows` | oxblood #4A1416 | 1, 19, 9 |

**Colour note.** Image tools don't follow hex codes exactly. Keep the colour words above, then match final colours to the persona token file (`system/tokens/personas/NN-mascot.tokens.json`); the artwork check flags off-palette colours.

## After the hero render

Use the approved hero as the character reference, keep the series prompt and the mascot line, and swap the ending:

| Output | Replace "three-quarter view…" with |
|---|---|
| Turntable sheet | `character turnaround sheet, 8 views at 45-degree steps in a row, same character, same lighting, neutral pose` |
| Sachet moment | `tearing open a small red-and-yellow seasoning sachet over a noodle cup, focused expression` |
| Reaction | `big happy reaction pose after the first bite, arms up` |
| Series line-up | `all seven figures standing side by side on one shelf, same scale, same base height` (attach all seven heroes) |

## Guardrails

- No ordinary human faces, no child faces; Nest is a grown-up creature.
- No cultural costume or caricature.
- No health claims; packs carry no readable text until the real pack is composited, with its health badges made illegible.
- The references are for proportion, material and attitude only: don't copy any specific toy or artist.
