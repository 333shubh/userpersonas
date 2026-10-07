# Mascot style v2: direction brief

Status: **superseded by `mascot-style-v3.md` (3D designer-toy series), 2026-10-07.** Kept for history. Replaces the look of the v1 mascots (geometric, code-built). It keeps everything else: palettes, persona constraints, rig ids and anchors, motion grid, sound and naming. Claude Design proposes, the project lead approves, then Claude Code locks the approved proportions into `rig-spec.json` (v0.2).

## 1. Stance

**"Snack-sized heroes":** chunky, cheeky noodle creatures drawn with a character designer's discipline. Each one owns a real MAGGI pack like a trophy.

- **Tension resolved:** a precise, rule-bound system vs hand-drawn joy. The rules decide colour and timing; the drawing gets the attitude.
- **Keywords:** chunky, cheeky, appetising.
- **Anti-keywords:** stiff geometry, generic chibi, costume stereotype.

## 2. What we borrow from the three references (principles, never surface)

Reference images are local only: `brief/references/inspo/` (git-ignored). Learn the principles; do not copy any brand illustration or the living artist's surface style.

| Reference | Borrow | Never take |
|---|---|---|
| 1. Maggi kids campaign art | Chunky, faceted "paper-cut" construction; oversized heads; flat, bold fills; joyful, open poses | Child characters; human kids |
| 2. Flame poster | Exaggerated emotion (tears, flame-for-spice); food flying into frame; confident outlines; one-idea compositions | Its layout |
| 3. Character illustration (Sarah-Lisa Hleb) | Strong silhouette; a clear S/C line of action; big-small-medium shape rhythm; attitude in hands and eyes; 2-tone shading with one highlight | Qipao, hair chopsticks, fan or any cultural costume; her rendering surface |

## 3. Construction rules (all seven)

| Rule | Value |
|---|---|
| Species | Hybrid noodle beings. Noodles, steam, bowl, cup or sachet are part of the **anatomy** (hair, limbs, body), not stuck-on props. Never human, never child-like (no baby proportions with human faces). |
| Proportion | Head : body = 1 : 1.5 to 1 : 2 (head is the biggest single shape). Hands oversized (1.3x a realistic ratio) for gesture. |
| Line of action | Every pose is built on one visible S or C curve from head to grounded foot/base. Weight on one side. No symmetric "standing to attention" poses. |
| Shape rhythm | Every mascot has one big, one medium, one small dominant shape; no two of equal size. |
| Eyes | Large, readable at 64 px: eye height ≥ 9% of mascot height; pupils with a single highlight. Expressions carry the persona (brief Section 5 personalities). |
| Outline | Confident outer contour; interior lines thinner (about 60% of the contour). Persona stroke tokens still set the contour weight. |
| Shading | 2-tone cel shading: base + one shadow tone + one highlight, all from the persona palette. No gradients except where tokens allow (Lull bloom, Mise foil). Cram shades with halftone screens of its one ink. |
| Silhouette hook | Keep each v1 hook idea (headphones, flame crown, nest dome, sprout, crescent, stepped blocks, crossed chopsticks), but redrawn with appeal. It must survive the 32 px solid-black test. |
| Rig compatibility | Same rig ids, slots, anchors and states as `system/rig-manifest.json`; groups named, translate() only. The pack lives in `{mascot}__props__pack` (new, see section 5). |

## 4. Per-mascot concept (redraw targets)

| Mascot | Body idea | Pose / attitude | Signature moment |
|---|---|---|---|
| **Cram** (Hostel Hungry) | A noodle-cup creature, cup as body, noodle fringe falling over tired eyes, oversized headphones | Slouched C-curve, fork raised like a pen, pack clamped under the arm | Phone timer glowing on the desk: "counts it on a phone timer" |
| **Riot** (Maximalist Foodie) | A chili-noodle firecracker: noodle flame hair, sticker-patched skin, mismatched eyes | Leaning back mid-shout, pack held high, sauce squeezed in a jet | Flame hair erupting with tears of joy (borrowed from ref 2's emotion) |
| **Nest** (Practical Parent) | A round noodle-nest homebody, apron-bow tied at the back, rounded everything | Calm S-curve, one hand steady on a kettle, the other offering a small bowl to a toy-scale hand | "Half for the little one": the sachet split with care |
| **Sprig** (Conscious Upgrader) | A bowl creature with a sprout growing from the head, leafy hands | Balanced contrapposto, dropping fresh greens in from above | Greens falling into the bowl: additive, never punitive |
| **Lull** (Midnight Recharger) | A sleepy moon-bowl, crescent bite in the head, blanket-cape | Sinking C-curve, cup cradled in both hands at chest height | Steam leaving the cup becomes stars |
| **Stack** (Value-Stocking Homemaker) | A sturdy stack-of-packs being, stepped blocky body, price-tag flag | Planted, exact, one hand counting packs on fingers | Multipack wrap with the tear-off Mon-Sun calendar |
| **Mise** (Premium Flavor Explorer) | A slim, poised bowl-on-a-foot with chopstick arms and a noodle ribbon | Elegant S-curve, chopsticks lifting a single ribbon | The lifted ribbon catching the one foil highlight |

Global flavour for Mise comes from food and props only, never from clothing.

## 5. The packs (real Nestlé MAGGI packaging)

Private project decision (2026-10-07): real MAGGI logo and packs are allowed. The assignments are in `tokens.json` (`persona.*.product`). Images are in `brief/references/packs/` (local only, never committed).

| Mascot | Pack | Format | Image |
|---|---|---|---|
| Cram | MAGGI 2-Minute Noodles Masala | 70 g pouch | `masala-single.png`, redrawn in Cram's one ink (photocopy look) |
| Riot | MAGGI Special Masala ("Spicy. Yummy.") + Hot & Sweet Extra Hot sauce | 70 g pouch + sauce pouch | `special-masala.png`, `extra-hot-sauce.png` (swap to the 2026 Spicy range if a photo is supplied) |
| Nest | MAGGI 2-Minute Noodles Veggie Masala | single pouch | `veggie-masala.png` |
| Sprig | MAGGI Nutri-licious Veg Atta (2025 pack) | 72.5 g pouch | `veg-atta-2025.png` (alt `spinach-atta.png`). Needs Nestlé review. |
| Lull | MAGGI Masala Cuppa | cup | `masala-cuppa.png` |
| Stack | MAGGI 2-Minute Noodles Masala 12-pack | 840 g multipack | built from `masala-single.png` |
| Mise | MAGGI Korean BBQ Chicken | pouch | `korean-bbq-chicken.jpg` (alts: Korean BBQ Veg, Cuppa Korean Spicy Cheesy) |
| Locale prop | MAGGI Magic Cubes (Extra Chicken) | cube pack | `magic-cubes-chicken.png` (West Africa and Europe packs) |

Pack rules:
1. Render style is free per mascot (illustrated or near-photoreal), but the pack must read as the real product: logo cushion, flavour name, pack colours, hero bowl.
2. The pack sits in its own group `{mascot}__props__pack`. Only inside that group may colours fall outside the persona palette, and a raster `<image>` (embedded, not linked) is allowed. Everything else keeps token colours only.
3. Nutrition or health badges printed on real packs (e.g. "With Goodness of Iron", fibre messages) are drawn as illegible texture. No health claims anywhere (brief Section 22).
4. Cram's pack is the one exception to full colour: it is redrawn in one ink, so Cram stays strictly black and white.

## 6. Stress tests before approval

- 32 px solid-black silhouette lineup: all seven named at a glance; pairwise IoU ≤ 0.85.
- 64 px colour: eyes and the pack still read.
- Cram in one ink; Lull below the luminance cap; Mise duotone + one foil.
- "Does this look like generic AI chibi?" If yes, push the hybrid anatomy further.
