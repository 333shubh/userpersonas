# ChatGPT prompts: turntables and poses

**Extra, for after the task outputs** (project lead's call, 2026-10-07). The task's own illustrations are the eating scenes in `system/scene-prompts.md`; make those and the overview PNG/PDF first.

Version 1.0, 2026-10-07. These follow the seven approved hero renders (`static/NN-slug/NN-mascot-hero.png`) and `system/mascot-style-v3.md`. Every value here comes from `tokens.json`: background colours are `persona.*.role.bg`, and pose size is scaled by `persona.*.motion.amplitude`.

## Workflow

1. **Use the hero's own chat.** Open the ChatGPT chat where each hero was made, so it remembers the character. In a new chat, attach the approved `NN-mascot-hero.png` first (the version without the pack, not `-with-pack`).
2. **Four images per mascot**, one prompt each, in this order:

   | # | Output | Format | Save as |
   |---|---|---|---|
   | 1 | Turnaround, views 0° to 135° | landscape 3:2 | `static/NN-slug/NN-mascot-sheet-turnaround-1.png` |
   | 2 | Turnaround, views 180° to 315° | landscape 3:2 | `static/NN-slug/NN-mascot-sheet-turnaround-2.png` |
   | 3 | Sachet moment | square 1:1 | `static/NN-slug/NN-mascot-pose-sachet.png` |
   | 4 | Reaction after the first bite | square 1:1 | `static/NN-slug/NN-mascot-pose-reaction.png` |

   Two sheets of 4 views are more reliable than one row of 8. Claude Code joins them into the 8-view turntable.
3. **Redo a view when it drifts.** If any part of the "Keep identical" line changes (colour, outfit, head shape, number of fingers), reply: `View N changed the [part]. Redraw only that view exactly like the attached hero.`
4. **No packs in these images.** Hands are empty in the turntables. Where a pack or cup shows in a pose, it is plain, and Claude Code composites the real MAGGI pack on afterwards, as for the heroes.
5. **Avoid on every prompt** (already included at the end of each block): realistic human face, child, food as a head, display base, readable text, logos, watermark, extra fingers, cultural costume.

## Pose size by persona

Motion amplitude (`persona.*.motion.amplitude`) sets how big each reaction is:

| Mascot | Amplitude | Reaction size |
|---|---|---|
| Riot | 1.4 | Biggest: arms fully up, one foot off the ground |
| Cram | 1.1 | Pop: eyes snap open, small hop |
| Nest | 0.9 | Warm: hand to cheek, shoulders lift |
| Stack | 0.8 | Firm: one thumbs-up, feet stay planted |
| Sprig | 0.7 | Calm: hand on chest, level posture |
| Lull | 0.6 | Smallest: sinks into the blanket |
| Mise | 0.6 | Smallest: eyes close, chopsticks rise |

---

## 01 Cram

Keep identical: `sleepy cat-eared creature, cat ears through a grey knit beanie with black star patches, half-closed eyes, black headphones, oversized grey hoodie with a timetable-grid print, black backpack, grey camo cargo pants, chunky black-and-white sneakers; strictly black, white and grey, no colour at all`

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet hip-width apart, arms relaxed slightly away from the body, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Large soft key light from top-left, gentle fill from the right, rim light from behind, identical in every view. Seamless pure white background (#FFFFFF), soft contact shadow under each figure. Keep identical: sleepy cat-eared creature, cat ears through a grey knit beanie with black star patches, half-closed eyes, black headphones, oversized grey hoodie with a timetable-grid print, black backpack, grey camo cargo pants, chunky black-and-white sneakers; strictly black, white and grey, no colour at all. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lighting, same white background (#FFFFFF), soft contact shadows. Keep identical: sleepy cat-eared creature, grey beanie with black star patches, half-closed eyes, black headphones, grey timetable-grid hoodie, black backpack, grey camo cargo pants, black-and-white sneakers; strictly black, white and grey. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit, strictly black, white and grey. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: holding a small steel saucepan of cooked noodles at waist height in one hand and tearing a small plain white seasoning sachet with a black band open with its teeth; grey seasoning specks drift into the pan; a fork stands upright in the hoodie pocket; eyes half-closed, shoulders slumped, still hungry. Large soft key light from top-left, fill from the right, rim light from behind. Seamless pure white background (#FFFFFF), soft contact shadow. No display base, no text, no logos, no colour at all, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same black-and-white render setup, square 1:1, three-quarter view, full figure. Pose: right after the first bite. One hand raises the fork like a trophy with noodles hanging from it, the other holds the steel saucepan; the sleepy eyes snap fully open and sparkle for the first time; cat ears perk straight up through the beanie; a small hop with both sneakers just off the ground and the contact shadow below. Strictly black, white and grey. Seamless pure white background (#FFFFFF). No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## 02 Riot

Keep identical: `glossy chili-red devil-imp, spiky flame hair in yellow and red, two small horns, mismatched eyes, wide fanged grin, sticker decals on the skin, volt-blue puffer jacket with orange trim and white patches, black cargo pants, white sneakers with orange and black panels, red pointed tail with an arrow tip`

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet hip-width apart, arms relaxed slightly away from the body, hands empty, mouth in its usual grin. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Large soft key light from top-left, gentle fill from the right, rim light from behind, identical in every view. Seamless warm cream background (#FFF6E0), soft contact shadow under each figure. Keep identical: glossy chili-red devil-imp, spiky flame hair in yellow and red, two small horns, mismatched eyes, wide fanged grin, sticker decals on the skin, volt-blue puffer jacket with orange trim and white patches, black cargo pants, white sneakers with orange and black panels, red pointed tail with an arrow tip. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lighting, same warm cream background (#FFF6E0), soft contact shadows. The back views must show the tail and the back of the puffer clearly. Keep identical: glossy chili-red devil-imp, yellow-and-red flame hair, two small horns, sticker decals, volt-blue puffer with orange trim and white patches, black cargo pants, white-orange-black sneakers, red arrow-tip tail. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit and colours. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: leaning back with one knee raised, holding a bowl of noodles low in one hand and ripping a small plain red seasoning sachet with a yellow band open with the other hand and its teeth; a red-orange cloud of seasoning bursts out over the bowl; flame hair flaring, mismatched eyes wide, grinning. Large soft key light from top-left, fill from the right, rim light from behind. Seamless warm cream background (#FFF6E0), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same render setup, square 1:1, three-quarter view, full figure. Pose: right after the first bite, at full volume. Both arms flung high, the bowl in one hand and a fork in the other, noodles flying in an arc; flame hair flaring taller than before; mouth wide open shouting with the tongue out; one foot off the ground; the tail whipping up; two small sweat drops from the spice. Seamless warm cream background (#FFF6E0), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## 03 Nest

Keep identical: `grown-up axolotl creature with a soft cream-to-peach head, pink feathery gill-frills, small blush cheeks, kind calm eyes, sage-green cardigan, cream knit apron with a small pink heart patch, cream trousers with pink patches, rounded pink clogs; rounded everywhere, no sharp edges`

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet hip-width apart, arms relaxed slightly away from the body, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Large soft warm key light from top-left, gentle fill from the right, rim light from behind, identical in every view. Seamless cream background (#FFF3E0), soft contact shadow under each figure. Keep identical: grown-up axolotl creature with a soft cream-to-peach head, pink feathery gill-frills, small blush cheeks, kind calm eyes, sage-green cardigan, cream knit apron with a small pink heart patch, cream trousers with pink patches, rounded pink clogs; rounded everywhere, no sharp edges. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, no child, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lighting, same cream background (#FFF3E0), soft contact shadows. The back views must show the apron ties and the back of the gill-frills. Keep identical: cream-to-peach axolotl head, pink gill-frills, sage-green cardigan, cream apron with a pink heart patch, cream trousers, pink clogs; rounded everywhere. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit and colours. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: one hand cradles a small rounded bowl of noodles against the apron; the other hand gently shakes an opened small plain red seasoning sachet with a yellow band over it; a wooden spoon is tucked in the apron pocket; calm, focused eyes, a slight forward lean. Everything rounded. Large soft warm key light from top-left, fill from the right, rim light from behind. Seamless cream background (#FFF3E0), soft contact shadow. No display base, no text, no logos, no realistic human face, no child, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same render setup, square 1:1, three-quarter view, full figure. Pose: right after the first spoonful. Eyes closed in a warm smile, one hand pressed to its cheek, the other holding the rounded bowl close to the apron with the wooden spoon resting in it; gill-frills lifted; shoulders up in gentle delight; both clogs on the ground. Seamless cream background (#FFF3E0), soft contact shadow. No display base, no text, no logos, no realistic human face, no child, 4 fingers per hand.
```

---

## 04 Sprig

Keep identical: `calm frosted translucent pale-green sprite with a smooth rounded head and a two-leaf sprout on the crown, large dark eyes, wheat linen overshirt over a white tee, olive crossbody bag, olive cargo trousers, canvas sneakers; low saturation`

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet hip-width apart, arms relaxed slightly away from the body, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Large soft key light from top-left, gentle fill from the right, rim light from behind, identical in every view, so the frosted head keeps its soft inner glow. Seamless natural paper background (#F2EDE1), soft contact shadow under each figure. Keep identical: calm frosted translucent pale-green sprite with a smooth rounded head and a two-leaf sprout on the crown, large dark eyes, wheat linen overshirt over a white tee, olive crossbody bag, olive cargo trousers, canvas sneakers; low saturation. Do not redesign anything. No falling leaves in the turnaround. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lighting, same paper background (#F2EDE1), soft contact shadows. Keep identical: frosted translucent pale-green head with a two-leaf sprout, wheat linen overshirt, white tee, olive crossbody bag, olive cargo trousers, canvas sneakers; low saturation. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer toy, same outfit and colours, low saturation. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: holding a bowl of noodles topped with fresh greens and a lemon wedge level at chest height in one hand; the other hand has torn a small plain red seasoning sachet with a yellow band only halfway and sprinkles about half of it over the bowl; upright, level posture; calm eyes on the bowl. Large soft key light from top-left, fill from the right, rim light from behind. Seamless natural paper background (#F2EDE1), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same render setup, square 1:1, three-quarter view, full figure. Pose: right after the first bite. Calm eyes closed, a small content smile, one hand resting on its chest, the other holding the bowl level at chest height; a third small leaf unfurls on the sprout; three leaves drift down slowly; balanced, level posture, both feet planted. Seamless natural paper background (#F2EDE1), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## 05 Lull

Keep identical: `round dark glow-creature with a smooth dusk-violet blob head, glowing half-moon eyes, a glowing crescent mark on the forehead, small smile, dark purple oversized hoodie, lilac sherpa blanket with a star-and-moon pattern worn as a cape, dark cargo trousers, lilac fluffy slippers`

Lull always uses scene light (`mascot-style-v3.md` section 4), including in the turntable.

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet together, arms relaxed, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Near-darkness: one warm lamp glow from the front-left and a soft violet rim light from behind so the outline reads in every view; eyes and crescent glowing warm; identical in every view. Seamless deep blue-violet background (#121127), soft contact shadow under each figure. Keep identical: round dark glow-creature with a smooth dusk-violet blob head, glowing half-moon eyes, a glowing crescent mark on the forehead, small smile, dark purple oversized hoodie, lilac sherpa blanket with a star-and-moon pattern worn as a cape, dark cargo trousers, lilac fluffy slippers. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lamp-and-rim lighting, same deep blue-violet background (#121127), soft contact shadows. The back views must show the blanket cape's star-and-moon pattern. Keep identical: dusk-violet blob head, glowing half-moon eyes, glowing crescent mark, dark purple hoodie, lilac star-and-moon blanket cape, dark cargo trousers, lilac slippers. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit and colours. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: holding a plain cream paper noodle cup (no print) close to the chest in one hand; the other hand tears a small plain red seasoning sachet with a yellow band over the cup; steam rises and turns into three small glowing stars; sleepy, content eyes. Lit only by one warm lamp glow from the front-left, soft violet rim light from behind. Seamless deep blue-violet background (#121127), soft contact shadow. Nothing brighter than the glowing eyes. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same scene lighting, square 1:1, three-quarter view, full figure. Pose: right after the first sip. Sinking slightly into the blanket cape, glowing eyes turned into happy upturned crescents, the plain cream noodle cup hugged to the chest with both hands, a small cluster of five glowing stars rising from the cup. Seamless deep blue-violet background (#121127), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## 06 Stack

Keep identical: `closed taped kraft cardboard carton head with printed dark half-round eyes and a small smile, yellow price tag hanging from the top-right corner, navy work jacket with a light-blue sleeve stripe over a cream tee, black cargo trousers, tan work boots, navy mitten hands`

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet hip-width apart and parallel, arms relaxed straight at the sides, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Large soft key light from top-left, gentle fill from the right, rim light from behind, identical in every view. Seamless warm paper background (#F5EBD7), soft contact shadow under each figure. Keep identical: closed taped kraft cardboard carton head with printed dark half-round eyes and a small smile, yellow price tag hanging from the top-right corner, navy work jacket with a light-blue sleeve stripe over a cream tee, black cargo trousers, tan work boots, navy mitten hands. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same lighting, same warm paper background (#F5EBD7), soft contact shadows. The back views show the plain back of the carton with its tape strips and no face. Keep identical: closed taped kraft carton head, yellow price tag, navy work jacket with a light-blue sleeve stripe, cream tee, black cargo trousers, tan work boots, navy mitten hands. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit and colours. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: a small square navy pot of noodles held level at chest height in one mitten; the other mitten tears a small plain red seasoning sachet with a yellow band along a perfectly straight line at its notch, seasoning falling in a neat stream into the pot; price tag swinging; upright planted stance, feet parallel. Large soft key light from top-left, fill from the right, rim light from behind. Seamless warm paper background (#F5EBD7), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same render setup, square 1:1, three-quarter view, full figure. Pose: right after the first bite. One mitten gives a firm thumbs-up; the other holds the square pot level; the printed eyes turn into happy arcs; the price tag flips forward; upright planted stance, feet parallel, nothing tilted. Seamless warm paper background (#F5EBD7), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## 07 Mise

Keep identical: `sleek satin oxblood cat gentleman with tall pointed ears, long whiskers, calm half-lidded eyes, long oxblood coat with cream lining and lapels over a cream shirt, dark trousers, polished dark boots, thin cat tail; gold chopsticks are the only gold item`

Mise always uses scene light (`mascot-style-v3.md` section 4), including in the turntable.

**1. Turnaround, sheet 1**
```
Using the attached figure as the exact character reference, make a character turnaround sheet of this same 3D designer vinyl toy. Landscape 3:2. Four full-body views in one row, left to right, the figure turning clockwise in 45-degree steps: front (0°), front three-quarter (45°), side profile (90°), back three-quarter (135°). Same neutral standing pose in every view: feet together, arms relaxed at the sides, hands empty. Same height and same ground line for all four, evenly spaced, no overlap. Orthographic look, camera at chest height. Low warm pendant light from above-front, cream rim light from behind so the outline reads, rich shadows, identical in every view. Seamless deep oxblood background (#4A1416), soft contact shadow under each figure. Keep identical: sleek satin oxblood cat gentleman with tall pointed ears, long whiskers, calm half-lidded eyes, long oxblood coat with cream lining and lapels over a cream shirt, dark trousers, polished dark boots, thin cat tail. No gold anywhere in the turnaround. Do not redesign anything. No display base, no text, no labels, no logos, no watermark, no realistic human face, 4 fingers per hand.
```

**2. Turnaround, sheet 2**
```
Same character, same sheet setup as before. Landscape 3:2. Four full-body views in one row, left to right, continuing clockwise in 45-degree steps: back (180°), back three-quarter (225°), other side profile (270°), other front three-quarter (315°). Same neutral pose, same height, same ground line, same pendant-and-rim lighting, same oxblood background (#4A1416), soft contact shadows. The back views must show the coat's back and the tail clearly. Keep identical: satin oxblood cat head, tall ears, long whiskers, long oxblood coat with cream lining, cream shirt, dark trousers, polished dark boots, thin cat tail. No display base, no text, no labels, no logos, 4 fingers per hand.
```

**3. Sachet moment**
```
Using the attached figure as the exact character reference, same 3D designer vinyl toy, same outfit and colours. Square 1:1. Three-quarter view 35 degrees off front, camera at chest height, full figure in frame. Pose: holding a small dark ceramic bowl of noodles topped with spring onion and sesame at chest height in one paw; the other paw drizzles a small plain dark-red seasoning-oil sachet from about one bowl-width above in a thin glossy stream; gold chopsticks rest across the bowl and are the only gold item; eyes half-closed, tail curled at the tip. Low warm pendant light from above-front, cream rim light from behind, rich shadows. Seamless deep oxblood background (#4A1416), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

**4. Reaction**
```
Same character, same scene lighting, square 1:1, three-quarter view, full figure. Pose: right after the first bite. Eyes closed, savouring; chin slightly lifted; one paw raises the gold chopsticks elegantly with a single noodle ribbon; the other paw holds the dark bowl; the tail curls into a loose spiral; whiskers relaxed; composed, elegant posture, feet together. Gold chopsticks are the only gold item. Seamless deep oxblood background (#4A1416), soft contact shadow. No display base, no text, no logos, no realistic human face, 4 fingers per hand.
```

---

## What Claude Code checks when the images are in the repo

- **Names:** every file follows `system/naming-rules.md` (`check-names`).
- **Turntable:** both sheets are cut into 8 figures; every figure stands on the same ground line, and heights differ by 4% or less between views. They are joined into `NN-mascot-sheet-turnaround.png`.
- **Consistency:** each view's main colours stay close to the hero's (same check family as `check-heroes`); Cram stays achromatic.
- **Real pack:** plain packs and cups that show in poses get the real MAGGI pack composited with `tools/composite-packs.py`.
