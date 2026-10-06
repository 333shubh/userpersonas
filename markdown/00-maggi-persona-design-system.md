# Maggi Persona & Mascot Design System

| | |
|---|---|
| **Document** | `00-maggi-persona-design-system.md` (system file, brief Section 10.1) |
| **Gate** | 1 of 6 (brief Section 25): text and system only, no artwork |
| **Status** | Proposed. Nothing here is locked until Gate 1 approval. |
| **Source of truth** | `system/tokens/tokens.json`. Every number in the generated tables below is written by `tools/build-tokens.py` from that file. Do not edit tables between `generated` markers by hand. |
| **Brief** | `brief/maggi-persona-project-brief-v2.md`. Part II (Sections 16–28) overrides Part I. |
| **Validated by** | `python tools/run-all.py` (results: `stress-tests/qa/summary.md`) |

**What this file covers** (brief Section 15): 1 the seven-persona map, 2 shared brand DNA, 3 segmentation logic, 4 the design-token framework, 5 mascot construction rules, 6 colour and typography architecture, 7 accessibility rules, 8 the static illustration system, 9 the motion and sound system, 10 asset naming and file structure, 11 research insights and the competitor framework, 12 guardrails, 13 the Gate 1 decision log and handoff.

**Concept status.** Personas, mascots, pack mechanics, "felt time" lines and card scores are design concepts, not product or market claims (Section 22). This is not an official Nestlé or Maggi document. It uses no real logo, packaging artwork or slogan.

---

## 1. The seven-persona map

Seven globally adoptable, stylised archetypes. Each one owns exactly one **primary motivation** (the non-overlap rule, Section 3). Each one is separated from the others by **who buys, who eats and the gate they must pass** (Section 17), so three of them don't collapse into "cheap and convenient".

<!-- generated:persona-map:start -->
| # | Mascot | Persona | Primary motivation | Buyer | Eater | Decision gate | Day slot | Design constraint |
|---|---|---|---|---|---|---|---|---|
| 01 | **Cram** | Hostel Hungry | Lowest-effort filling meal | Self | Self | Price + zero cleanup | 3 · 13:00 | Strict black and white, one-colour print logic |
| 02 | **Riot** | Maximalist Foodie | Flavor experimentation | Self | Self + an audience | "Is this worth making and posting?" | 5 · 19:30 | Controlled clash: fixed rules for which colours may collide |
| 03 | **Nest** | Practical Parent | Kid-approved convenience | Parent | Child (and parent) | The child says yes | 4 · 16:15 | No sharp corners, large touch targets |
| 04 | **Sprig** | Conscious Upgrader | Health-compatible indulgence | Self | Self | "Does this fit my goals?" | 1 · 07:30 | Natural paper texture, low-ink look |
| 05 | **Lull** | Midnight Recharger | Emotional decompression | Self | Self | "Do I need comfort right now?" | 7 · 00:45 | Luminance-capped dark, no pure white |
| 06 | **Stack** | Value-Stocking Homemaker | Household value and reliability | Planner | Whole household | Price per serving + availability | 2 · 10:30 | Strict grid, stamp and price-tag logic |
| 07 | **Mise** | Premium Flavor Explorer | Premium taste adventure | Self | Self + guests | "Is it worth paying more?" | 6 · 21:00 | Duotone plus one foil accent |
<!-- generated:persona-map:end -->

**Day slot** is the panel order on the overview board (Section 18.5): the seven panels read as one day, from 07:30 to 00:45, each lit for its hour.

### Mascot card stats

The card radar (Section 18.7) uses seven stats, each scored as a whole number from 1 to 5. It doubles as the persona-map visualisation in the PDF.

<!-- generated:card-stats:start -->
| Mascot | Heat | Speed | Comfort | Chaos | Value | Fancy | Wellness |
|---|---|---|---|---|---|---|---|
| **Cram** | 2 | 5 | 3 | 2 | 5 | 1 | 1 |
| **Riot** | 5 | 3 | 2 | 5 | 3 | 2 | 1 |
| **Nest** | 1 | 4 | 5 | 2 | 4 | 1 | 3 |
| **Sprig** | 2 | 3 | 3 | 1 | 2 | 3 | 5 |
| **Lull** | 2 | 3 | 5 | 1 | 3 | 2 | 2 |
| **Stack** | 2 | 4 | 4 | 1 | 5 | 1 | 3 |
| **Mise** | 3 | 2 | 3 | 2 | 1 | 5 | 3 |

_Draft scores: design judgement from brief Section 18.7, to be validated against research._
<!-- generated:card-stats:end -->

Card radar rules (dataviz standard): one series per card, so there's no legend box and the card title names the series. The polygon stroke is 2px. The fill is `role.key` at 25% opacity. Stat labels and values use `role.text` and never the series colour. A table view of the same seven numbers is printed on the card back.

---

## 2. Shared Maggi brand DNA

These constants appear in all seven worlds. Personas re-render them through their own constraint but never redefine them.

| Constant | Specification | Token |
|---|---|---|
| Red and yellow energy | Red `#D42A1E`, yellow `#FFC20E`. Inspired by the brand's colour energy, not sampled from packaging. | `brand.color.red`, `brand.color.yellow` |
| Swiss heritage thread | A two-band rule (red above yellow), each band one persona stroke wide, used at most once per layout. Never a flag motif. | `brand.color.heritage-thread` |
| The sachet | 160 × 240 rig units, 8-unit corner radius, 12-unit crimps with 8-unit teeth. The diagonal split runs from the left edge at 70% height to the right edge at 30% height. A tear notch 16 wide and 12 deep sits 24 units below the top crimp. | `brand.sachet.*` |
| The "2" mark | Construction box 1:1.25. Stroke ≥ 12.5% of glyph height, open counter ≥ 25% of glyph width, so it reads as a 2 at 16px. It means *felt time*, never a cook-time claim. | `brand.two-mark.*` |
| Steam curl | Three wisps at 0.45W / 0.60W / 0.40W (W = rim width), bases 0.18W apart, each an S-curve with exactly two inflections. | `brand.steam-curl.*` |
| Seasoning-and-cube prop family | Secondary props (cube, seasoning bottle, sauce) for markets that know Maggi mainly as seasoning. These are switched on by the locale axis. | `locale.packs.*.secondaryProps` |
| Brand-lockup slot | Top-left inside the margin, 3 of 12 columns wide, height 0.5 × width, clear space 0.25 × height on every side. **Always left empty** for the brand team. | `brand.layout.lockup-slot` |
| Grid | 12 columns, 24px gutter, 48px margin, 8px baseline, and a 4px spacing unit (`0 4 8 12 16 24 32 48 64 96 128`). | `brand.grid`, `brand.space` |
| Noodle thread | One continuous line across all seven overview panels. It enters and exits at 62% of panel height, its stroke is 0.625% of panel height, and it runs horizontal for the first and last 4% of each panel. | `brand.noodle-thread` |

**The sachet rule** (Section 18.3) means every mascot carries or uses the sachet, and *what it does with it* is the personality. Each persona's `role.sachet-red` and `role.sachet-yellow` is how that world renders the brand's red and yellow. For Cram, the sachet is solid ink plus a 25% screen, because colour would break the B&W constraint.

| Mascot | Sachet behaviour (Section 18.3) | Noodle-thread form (18.4) | Felt two minutes (18.2) |
|---|---|---|---|
| Cram | Uses all of it, fast, no ceremony | zine underline | Counts it on a phone timer |
| Riot | Swaps, stacks, or replaces it with chili oil | flame hair | *Proposed:* two minutes of remix, the build-and-shoot window before it goes soggy |
| Nest | Measures it carefully, often "half for the little one" | yarn | Gets two quiet minutes |
| Sprig | Uses half, scored line, adds fresh ingredients | vine | *Proposed:* two minutes to chop the greens in |
| Lull | Tears it slowly; the tear is part of the ritual | steam | Stretches it into a ritual |
| Stack | Counts them: one sachet per serving, in rows | shelf rail | *Proposed:* two minutes per serving, counted in rows |
| Mise | Dissolves it into broth, finishes with a second oil sachet | chopstick-lifted ribbon | Treats it as mise en place |

---

## 3. Persona segmentation logic

### 3.1 Three separating axes

1. **Primary motivation** (Section 3). Exactly one per persona, all seven different. Shared *secondary* motivations are allowed.
2. **Decision spine** (Section 17). Buyer, eater, social unit, purchase rhythm, and the gate the product must pass.
3. **Hour of the day** (Section 18.5). A visual device, not a usage claim. It gives each world its own light and keeps the overview readable as one day.

A persona is valid only if it differs from every other persona on axis 1, *and* differs from every other persona on at least two of the five spine fields (checked by `check-tokens.py`).

### 3.2 Overlap resolutions (Section 17, binding)

| Risky pair | What separates them | Test |
|---|---|---|
| Cram vs Lull | Cram is economic and functional: eating cheaply, no kitchen. Lull is emotional, and the eater is as likely to be an adult, gamer or shift worker as a student. | Neither persona file may define its persona as "a student who eats late". |
| Nest vs Stack | Nest's problem is *the child's acceptance at this meal*. Stack's problem is *household planning across the week*. | Nest buys top-ups; Stack buys multipacks. Nest's gate is "the child says yes"; Stack's gate is price per serving plus availability. |
| Riot vs Mise | Riot is cheap ingredients, loud results, DIY chaos. Mise is curated, restaurant-style, and willing to pay. | Riot's competitors are internet hacks and street food. Mise's are Korean and café noodles. |

### 3.3 Positioning twists (Section 18.13)

- **Lull counter-programmes the gamer.** Competitors sell energy (caffeinated "gamer-friendly" cup noodles in Japan, High). Lull is a *wind-down* noodle that helps you land.
- **Sprig is additive, not punitive.** It *adds* greens, protein or lemon and never "subtracts". The "what's in your bowl" label component supports transparency.
- **Nostalgia with a date.** Stamp and postmark motifs for Nest and Mise refer to the 50-year postal stamp (Medium–High).
- **Voice continuity.** Riot extends the Maggi Spicy campaign's attitude of spice as Gen Z self-confidence (High). It doesn't compete with that campaign or quote it.

---

## 4. Design-token framework

### 4.1 Architecture

```
tokens.json  (the only hand-edited file; DTCG shape: $value / $type / $description; aliases {dot.path})
├── meta                 version, gate, status, precedence
├── brand                shared constants: colour, contrast, space, grid, type, sachet, two-mark, steam-curl, layout, density scale
├── motion               clock, frame-rate, 4 easing tokens, durations, layer order, UI timings, safety, export
├── sound                chord, tuning, synthesis, accessibility
├── locale               second axis: 5 starter packs, all "validate locally"
├── rivalries, card      cross-persona data
└── persona.{cram…mise}
    ├── identity         number, slug, name, persona, motivation, job, spine, day, felt time, sachet, thread, pack
    ├── constraint       Section 18.12 rule + machine checks
    ├── stats            card radar 1–5
    ├── color            TIER 1 primitives, named for the world (ink, paper, hot-pink, oxblood…)
    ├── role             TIER 2 semantics, identical keys in every persona → token switcher safe
    ├── contrast         target level, declared text pairs, declared "distinguish" pairs
    ├── type, shape, texture, elevation, iconography, density
    ├── mascot, motion, sound, glyph
```

**Two colour tiers.** Primitives (`persona.*.color.*`) carry each world's own vocabulary. Semantic roles (`persona.*.role.*`) have the **same ten keys in every persona**: `bg`, `surface`, `text`, `text-muted`, `accent`, `line`, `focus`, `key`, `sachet-red`, `sachet-yellow`. Components and pages consume roles only. That way the live-clock page (Section 18.14) can re-skin between personas by swapping one role set, and no component needs a per-persona branch.

**Generated files.** `tools/build-tokens.py` writes `system/tokens/personas/NN-<mascot>.tokens.json`: fully resolved (no aliases), with brand, motion, card, locale and that persona's rivalries merged in, plus an explicit px type scale. Claude Design reads one file per persona. `tools/check-tokens.py` fails if any generated file is stale.

**Persona axis × locale axis** (Section 18.9). The persona axis controls look (palette, type, shape, texture, motion rhythm). The locale axis controls props, flavour names, language lines and cultural cues. A locale pack may *add* props and lines. It may not change a persona token. All five starter packs are marked `validate locally`.

### 4.2 Rules

1. Neither tool invents a value. A value not in `tokens.json` doesn't exist. To add one, edit `tokens.json`, run `python tools/build-tokens.py`, then run `python tools/run-all.py`.
2. Token names are kebab-case. Motion easing names are fixed at four, and personas change only *timing and amplitude*.
3. Every colour pair used for text is declared in `contrast.pairs`, or covered by the automatic role pairs, and verified numerically.
4. Every colour pair that must stay tell-apart-able is declared in `contrast.distinguish` and verified under colour-vision simulation.
5. Version bump rules: patch for a value tweak that passes all checks; minor for a new token; major for a renamed or removed token, which needs a migration note in the commit.

### 4.3 Design constraints as machine checks (Section 18.12)

| Mascot | Constraint (brief) | How the validator enforces it |
|---|---|---|
| Cram | Strict black and white, one-colour print logic | Every primitive and role colour is achromatic (R = G = B). Greys are halftone screens of one ink. |
| Riot | Controlled clash: fixed rules for which colours may collide | Exactly four clash pairs (pink×acid-green, volt-blue×tangerine, ultraviolet×yolk, chili×cyan), with each colour in at most one pair. Any other meeting needs an ink keyline. At most 3 clash colours per region. Each clash pair stays ≥ 8 ΔE under every simulation. |
| Nest | No sharp corners, large touch targets | Every radius ≥ 12px, touch targets ≥ 56px (brand minimum 44px), round caps only. |
| Sprig | Natural paper texture, low-ink look | Every colour has HSV saturation ≤ 0.75, ink coverage ≤ 60% of the illustration bounding box, fills at 92% opacity, multiply. |
| Lull | Luminance-capped dark, no pure white | No colour above relative luminance 0.75; backgrounds ≤ 0.03. |
| Stack | Strict grid, stamp and price-tag logic | All spacing on the 8px grid, radius ≤ 4px, icon grid a multiple of 8, tabular numerals. |
| Mise | Duotone plus one foil accent | Every colour is oxblood, cream, a mix of the two (within 2/255), or the single foil. The foil is never placed on cream (2.03:1). |

---

## 5. Mascot construction rules

The full contract is in `system/rig-spec.md`, with machine rules in `system/rig-spec.json` and exact id lists in `system/rig-manifest.json`. This section is the summary.

### 5.1 Universe rules: one family, seven creatures

1. **All seven are food creatures or hybrid noodle/kitchen beings, never humans** (Section 5).
2. **Shared construction**: same canvas (1024 viewBox, ground at y = 896, centred on x = 512), same layer order, same face rig (two eyes with lids, two brows, one mouth with six states), same two arms and hands with grip anchors, and the same sachet and steam curl.
3. **Distinct silhouettes**: each mascot has its own base shape and one *silhouette hook* that survives at 32px when filled solid black. Hooks must never sit in a `__detail` group.
4. **Height = heightRatio × 768 rig units**. The range is 538 to 768 units, so the lineup reads by height before shape.

| Mascot | Height × width | Base shape | Silhouette hook | Eye Ø / spacing / height | Signature props |
|---|---|---|---|---|---|
| Cram | 630 × 360 | cylinder cup, rim ellipse ry 40 | headphone band (arc r 200, apex +60 above rim) + upright fork 220 tall in the left hand (sachet alone in the right) | 56 / 120 / 40% | headphones, backpack, fork, phone timer |
| Riot | 691 × 420 | teardrop, point up, widest at 35% | 3-point flame crown (160 / 220 / 140), leaning 12° right | 48 + 72 (deliberately mismatched) / 150 / 45% | flame hair, stickers, chili, chili-oil bottle, phone |
| Nest | 538 × 620 | dome, height:width 0.87 | apron-bow loops (2 × 120 wide) behind the dome, showing at both sides at 60% height (never on top) | 52 / 160 / 42% | apron, wooden spoon, kettle, small bowl |
| Sprig | 660 × 440 | shallow bowl 440 × 220 + head dome | leaf pair on a 120 stem, 280 above the head, leaves 140 × 70 at ±35° | 44 / 110 / 55% | sprout leaves, lemon wedge, greens, half-sachet |
| Lull | 568 × 480 | round bowl, head r 200 | crescent notch (0.6r circle centred 0.65r from the head centre, 45° up-right, biting the edge) + 3 steam stars Ø 36 | 60 / 140 / 48% | steam stars, blanket, mug-lamp |
| Stack | 730 × 420 | 3 stepped blocks 420 / 360 / 300 wide | stepped outline + price-tag flag 120 × 70 on a 60-unit string | 48 / 130 / 30% | multipack, calendar, rubber stamp, price tag |
| Mise | 768 × 300 | slim bowl on a 140-wide foot | crossed chopsticks 520 long at 30°, crossing 120 above the rim | 40 / 100 / 38% | chopsticks, finishing-oil sachet, garnish, napkin |

Design may deviate up to **8%** from any number in this table without approval. Larger changes come back to gate review.

### 5.2 Required per mascot

- **Turnaround**: front, three-quarter, side (facing screen-right). All three views use identical ids.
- **Eight expressions**, reached by state swaps only: neutral, happy, excited, focused, content, surprised, tired, sleepy (lid / brow / mouth combinations are in `rig-spec.json`).
- **At least three poses** (Section 7): idle stance, sachet moment (the Section 18.3 behaviour), and the reaction pose.
- **Colour and one-colour versions.** The one-colour version is `role.text` on `role.bg`, used for the stamp, enamel-pin outline and app-icon tests (Section 18.15).

### 5.3 Child-safety rule for Nest

Children never appear with faces. They appear as hands, silhouettes or toy-scale props only, with no child-directed claims (Section 22).

---

## 6. Colour and typography architecture

### 6.1 Palettes, roles and contrast

Contrast pairs are verified numerically (WCAG 2.2): body 4.5:1, large 3:1, non-text 3:1, and for Cram, AAA at body 7:1 and large 4.5:1. "Large" means at least 24px regular or 18.66px bold.

<!-- generated:palettes:start -->
#### Cram (Hostel Hungry), target WCAG AAA

| Token | Hex | WCAG luminance |
|---|---|---|
| `ink` | `#000000` | 0.000 |
| `paper` | `#FFFFFF` | 1.000 |
| `screen-75` | `#404040` | 0.051 |
| `screen-50` | `#808080` | 0.216 |
| `screen-25` | `#BFBFBF` | 0.521 |
| `screen-10` | `#E6E6E6` | 0.791 |

Semantic roles: `bg` = `paper`, `surface` = `screen-10`, `text` = `ink`, `text-muted` = `screen-75`, `accent` = `ink`, `line` = `ink`, `focus` = `ink`, `key` = `ink`, `sachet-red` = `ink`, `sachet-yellow` = `screen-25`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `ink` on `paper` | body | 21.00:1 | 7.0:1 | pass | all body copy |
| `paper` on `ink` | body | 21.00:1 | 7.0:1 | pass | reversed headers, timetable bars |
| `ink` on `screen-25` | body | 11.42:1 | 7.0:1 | pass | text on yellow-half of sachet |
| `ink` on `screen-10` | body | 16.83:1 | 7.0:1 | pass | text on tinted panels |
| `paper` on `screen-75` | body | 10.37:1 | 7.0:1 | pass | reversed text on dark screen |

#### Riot (Maximalist Foodie), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `ink` | `#14101F` | 0.006 |
| `paper` | `#FFF6E0` | 0.926 |
| `hot-pink` | `#FF2E88` | 0.250 |
| `acid-green` | `#B8F200` | 0.737 |
| `volt-blue` | `#2B3DFF` | 0.111 |
| `tangerine` | `#FF6A13` | 0.316 |
| `ultraviolet` | `#7A2BF5` | 0.125 |
| `yolk` | `#FFD000` | 0.664 |
| `chili` | `#E8231A` | 0.184 |
| `cyan` | `#00D7F0` | 0.549 |

Semantic roles: `bg` = `paper`, `surface` = `yolk`, `text` = `ink`, `text-muted` = `ultraviolet`, `accent` = `hot-pink`, `line` = `ink`, `focus` = `volt-blue`, `key` = `hot-pink`, `sachet-red` = `chili`, `sachet-yellow` = `yolk`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `ink` on `paper` | body | 17.36:1 | 4.5:1 | pass | captions, recipe steps |
| `ink` on `hot-pink` | body | 5.34:1 | 4.5:1 | pass | sticker text |
| `ink` on `acid-green` | body | 14.01:1 | 4.5:1 | pass | sticker text |
| `paper` on `volt-blue` | body | 6.07:1 | 4.5:1 | pass | sticker text |
| `ink` on `tangerine` | body | 6.52:1 | 4.5:1 | pass | sticker text |
| `paper` on `ultraviolet` | body | 5.59:1 | 4.5:1 | pass | sticker text |
| `ink` on `yolk` | body | 12.70:1 | 4.5:1 | pass | sticker text |
| `ink` on `cyan` | body | 10.66:1 | 4.5:1 | pass | sticker text |
| `ink` on `chili` | large | 4.17:1 | 3.0:1 | pass | display words only on chili |

#### Nest (Practical Parent), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `ink` | `#4A2A18` | 0.032 |
| `ink-muted` | `#7A5038` | 0.102 |
| `paper` | `#FFF3E0` | 0.907 |
| `surface` | `#FFE4BF` | 0.805 |
| `tomato` | `#BF3F2A` | 0.148 |
| `honey` | `#FFC94D` | 0.636 |
| `peach` | `#F6A58A` | 0.483 |
| `sky` | `#8CC7E6` | 0.521 |
| `sage` | `#9CBF8E` | 0.463 |

Semantic roles: `bg` = `paper`, `surface` = `surface`, `text` = `ink`, `text-muted` = `ink-muted`, `accent` = `tomato`, `line` = `ink`, `focus` = `tomato`, `key` = `honey`, `sachet-red` = `tomato`, `sachet-yellow` = `honey`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `ink` on `paper` | body | 11.71:1 | 4.5:1 | pass | body copy |
| `ink` on `surface` | body | 10.46:1 | 4.5:1 | pass | cards, recipe panels |
| `ink-muted` on `paper` | body | 6.32:1 | 4.5:1 | pass | secondary copy |
| `tomato` on `paper` | body | 4.84:1 | 4.5:1 | pass | headings |
| `paper` on `tomato` | body | 4.84:1 | 4.5:1 | pass | buttons |
| `ink` on `honey` | body | 8.38:1 | 4.5:1 | pass | label bands |
| `ink` on `sky` | body | 6.99:1 | 4.5:1 | pass | label bands |

#### Sprig (Conscious Upgrader), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `ink` | `#26321F` | 0.028 |
| `ink-muted` | `#55604A` | 0.108 |
| `paper` | `#F2EDE1` | 0.849 |
| `surface` | `#E6DFCD` | 0.740 |
| `leaf` | `#6F8F5E` | 0.238 |
| `olive` | `#55603A` | 0.106 |
| `wheat` | `#D4BC86` | 0.517 |
| `terracotta` | `#B0452F` | 0.137 |
| `mustard` | `#C99B3A` | 0.362 |

Semantic roles: `bg` = `paper`, `surface` = `surface`, `text` = `ink`, `text-muted` = `ink-muted`, `accent` = `terracotta`, `line` = `ink`, `focus` = `olive`, `key` = `olive`, `sachet-red` = `terracotta`, `sachet-yellow` = `mustard`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `ink` on `paper` | body | 11.53:1 | 4.5:1 | pass | body copy |
| `ink` on `surface` | body | 10.14:1 | 4.5:1 | pass | "what's in your bowl" label |
| `ink-muted` on `paper` | body | 5.69:1 | 4.5:1 | pass | secondary copy |
| `olive` on `paper` | body | 5.76:1 | 4.5:1 | pass | headings |
| `paper` on `olive` | body | 5.76:1 | 4.5:1 | pass | reversed bands |
| `terracotta` on `paper` | body | 4.81:1 | 4.5:1 | pass | accent words |
| `leaf` on `paper` | ui | 3.12:1 | 3.0:1 | pass | pictogram strip, leaf icons (non-text) |

#### Lull (Midnight Recharger), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `night` | `#121127` | 0.007 |
| `surface` | `#1D1B3A` | 0.014 |
| `raised` | `#2A2752` | 0.026 |
| `text` | `#E4DDF2` | 0.746 |
| `text-muted` | `#B3AACF` | 0.428 |
| `glow` | `#FFB866` | 0.565 |
| `star` | `#F0D58A` | 0.679 |
| `dusk-violet` | `#8C7BE0` | 0.251 |
| `ember` | `#E0663F` | 0.257 |

Semantic roles: `bg` = `night`, `surface` = `surface`, `text` = `text`, `text-muted` = `text-muted`, `accent` = `glow`, `line` = `text-muted`, `focus` = `glow`, `key` = `dusk-violet`, `sachet-red` = `ember`, `sachet-yellow` = `glow`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `text` on `night` | body | 14.03:1 | 4.5:1 | pass | body copy |
| `text` on `surface` | body | 12.54:1 | 4.5:1 | pass | cards |
| `text-muted` on `night` | body | 8.43:1 | 4.5:1 | pass | secondary copy |
| `text-muted` on `raised` | body | 6.33:1 | 4.5:1 | pass | secondary copy on raised |
| `glow` on `night` | body | 10.84:1 | 4.5:1 | pass | warm headings |
| `night` on `glow` | body | 10.84:1 | 4.5:1 | pass | buttons |
| `dusk-violet` on `night` | large | 5.31:1 | 3.0:1 | pass | display only |

#### Stack (Value-Stocking Homemaker), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `ink` | `#14213D` | 0.016 |
| `ink-muted` | `#3A4763` | 0.063 |
| `paper` | `#F5EBD7` | 0.837 |
| `label-white` | `#FFFDF7` | 0.982 |
| `kraft` | `#C4A27A` | 0.390 |
| `stamp` | `#B3122B` | 0.102 |
| `price-tag` | `#FFC72C` | 0.623 |
| `shelf-blue` | `#1C5D99` | 0.104 |

Semantic roles: `bg` = `paper`, `surface` = `kraft`, `text` = `ink`, `text-muted` = `ink-muted`, `accent` = `stamp`, `line` = `ink`, `focus` = `ink`, `key` = `shelf-blue`, `sachet-red` = `stamp`, `sachet-yellow` = `price-tag`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `ink` on `paper` | body | 13.50:1 | 4.5:1 | pass | body copy |
| `ink` on `kraft` | body | 6.69:1 | 4.5:1 | pass | text on cardboard |
| `ink` on `price-tag` | body | 10.24:1 | 4.5:1 | pass | price-per-serving tags |
| `ink-muted` on `paper` | body | 7.85:1 | 4.5:1 | pass | secondary copy |
| `label-white` on `stamp` | body | 6.80:1 | 4.5:1 | pass | stamp reversals |
| `stamp` on `paper` | body | 5.84:1 | 4.5:1 | pass | stamp text on paper |
| `label-white` on `shelf-blue` | body | 6.71:1 | 4.5:1 | pass | shelf strip labels |

#### Mise (Premium Flavor Explorer), target WCAG AA

| Token | Hex | WCAG luminance |
|---|---|---|
| `oxblood` | `#4A1416` | 0.020 |
| `cream` | `#F4EBDC` | 0.838 |
| `tint-80` | `#6C3F3E` | 0.071 |
| `tint-60` | `#8E6A65` | 0.170 |
| `tint-35` | `#B9A097` | 0.377 |
| `foil` | `#C9A24A` | 0.388 |

Semantic roles: `bg` = `oxblood`, `surface` = `tint-80`, `text` = `cream`, `text-muted` = `tint-35`, `accent` = `foil`, `line` = `tint-60`, `focus` = `foil`, `key` = `oxblood`, `sachet-red` = `oxblood`, `sachet-yellow` = `foil`.

| Pair | Use | Ratio | Needs | Result | Where |
|---|---|---|---|---|---|
| `cream` on `oxblood` | body | 12.66:1 | 4.5:1 | pass | body copy, dark editorial spreads |
| `oxblood` on `cream` | body | 12.66:1 | 4.5:1 | pass | body copy, light spreads |
| `foil` on `oxblood` | body | 6.24:1 | 4.5:1 | pass | foil headings |
| `cream` on `tint-80` | body | 7.35:1 | 4.5:1 | pass | captions on tinted panels |
| `oxblood` on `tint-35` | body | 6.09:1 | 4.5:1 | pass | captions on light tint |
| `tint-60` on `cream` | large | 4.04:1 | 3.0:1 | pass | pull quotes only |
<!-- generated:palettes:end -->

### 6.2 Cross-system key colours

Each persona has one `role.key` used to identify it in cross-persona views (overview strip, token switcher, quiz results, card backs). The seven keys were chosen by an exhaustive search over 384 combinations of candidate colours drawn from each palette, to maximise the worst-case separation of all 21 pairs. The result is a worst normal-vision ΔE of 16.0 (threshold 15) and a worst simulated ΔE of 7.7 (floor band 6–8). Because two pairs sit in the floor band (Riot vs Stack under protanopia, Sprig vs Stack under tritanopia), **a key colour never appears without the mascot silhouette and the persona name.**

### 6.3 Typography

All faces are on Google Fonts under the SIL Open Font License. Re-verify the licence before commercial release. Each display face has a fallback stack ending in a generic family (Section 21). Type scales come from base 16px × each persona's ratio; caption is clamped to the 14px web minimum.

<!-- generated:type-system:start -->
| Mascot | Display face + weight | Text face + weights | Line-height display / text | Tracking em display / text / label | Case display / text | Ratio | Scale px: caption / body / lead / h3 / h2 / h1 / display |
|---|---|---|---|---|---|---|---|
| **Cram** | Archivo Black 400 | IBM Plex Mono 400/600 | 0.95 / 1.5 | 0.02 / 0 / 0.08 | uppercase / none | 1.414 | 14 / 16 / 23 / 32 / 45 / 64 / 90 |
| **Riot** | Bungee 400 | Rubik 400/700 | 1.0 / 1.5 | 0.01 / 0 / 0.05 | uppercase / none | 1.5 | 14 / 16 / 24 / 36 / 54 / 81 / 122 |
| **Nest** | Baloo 2 700 | Nunito 400/800 | 1.15 / 1.6 | 0 / 0 / 0.02 | none / none | 1.25 | 14 / 16 / 20 / 25 / 31 / 39 / 49 |
| **Sprig** | Fraunces 600 | Karla 400/700 | 1.1 / 1.6 | -0.01 / 0 / 0.1 | none / none | 1.25 | 14 / 16 / 20 / 25 / 31 / 39 / 49 |
| **Lull** | Quicksand 600 | Atkinson Hyperlegible 400/700 | 1.2 / 1.65 | 0 / 0.01 / 0.04 | lowercase / none | 1.2 | 14 / 16 / 19 / 23 / 28 / 33 / 40 |
| **Stack** | Barlow Condensed 800 | Barlow 400/600 | 1.0 / 1.5 | 0.02 / 0 / 0.06 | uppercase / none | 1.333 | 14 / 16 / 21 / 28 / 38 / 51 / 67 |
| **Mise** | Playfair Display 400 | Libre Franklin 400/600 | 1.05 / 1.6 | -0.01 / 0 / 0.12 | none / none | 1.618 | 14 / 16 / 26 / 42 / 68 / 110 / 177 |
<!-- generated:type-system:end -->

**Minimum type sizes per medium** (`brand.type.min-size`): web body 16px, web caption 14px, app body 16px, print body 9pt, print caption 7pt, packaging copy 7pt (local labelling law may require more), motion text 48px at 1080p, sticker text 48px at 512px.

**Custom type kit** (Section 18.6). Each persona draws a "2", a wordmark and numerals 0–9 as SVG glyphs (not installable fonts), built from its mascot's geometry. The construction notes are in `persona.*.glyph`. Every "2" meets `brand.two-mark` minimums.

### 6.4 Shape, surface, texture and icons

<!-- generated:surface-system:start -->
| Mascot | Radius | Stroke (rig units) | Cap | Angles | Elevation | Icons | Density |
|---|---|---|---|---|---|---|---|
| **Cram** | 0px | 16px | square | rotation-max=2 | kind=none; note=Flat print. Separate layers with a 2px ink rule, never a shadow. | grid=24px; stroke=2px; cap=square; fill=none; note=margin-doodle line style | 2 |
| **Riot** | 0px, 12px, 999px | 20px | round | rotation-max=8 | kind=hard-offset; x=6px; y=6px; blur=0px; color=#14101F; opacity=1; note=Sticker drop: hard offset, no blur. | grid=24px; stroke=2px; cap=round; fill=solid; note=2px hard offset shadow in ink | 5 |
| **Nest** | 12px, 24px, 999px | 14px | round | rotation-max=4 | kind=soft; x=0px; y=6px; blur=16px; color=#4A2A18; opacity=0.18 | grid=24px; stroke=2px; cap=round; fill=two-tone: surface fill + ink line; note=no points; min corner radius 2px | 3 |
| **Sprig** | 6px, 16px | 8px | round | rotation-max=0; leaf-angle=35 | kind=none; note=Layers separate by surface colour only. | grid=24px; stroke=1.5px; cap=round; fill=single tint fill at 60% opacity | 2 |
| **Lull** | 20px, 999px | 0px | round | rotation-max=3 | kind=glow; x=0px; y=0px; blur=24px; color=#FFB866; opacity=0.35; note=Only the single warm-light element glows; everything else is flat. | grid=24px; stroke=0px; cap=round; fill=soft fill; note=4px glow halo at 35% opacity | 2 |
| **Stack** | 0px, 4px | 12px | butt | rotation-max=0; stamp-rotation=-6 | kind=edge; x=0px; y=4px; blur=0px; color=#14213D; opacity=1; note=Stacked-box edge: solid 4px drop, no blur. | grid=24px; stroke=2px; cap=butt; fill=stamp outline; note=drawn on an 8px sub-grid | 3 |
| **Mise** | 0px | 6px | butt | rotation-max=0; diagonal=30 | kind=none; note=Depth from light and shadow in the illustration, never UI shadows. | grid=24px; stroke=1px; cap=butt; fill=none; note=foil only on the single hero mark | 2 |

| Mascot | Texture parameters (SVG-filter ready; rig units at 1024) |
|---|---|
| **Cram** | halftone: lpi=65, angle=45, dot=round, threshold=1-bit: every pixel is ink or paper; grain: filter=feTurbulence fractalNoise, baseFrequency=0.9, octaves=1, opacity=0.08, blend=multiply; marks=max 2 staple marks per panel, 24 x 6 rig units |
| **Riot** | misregistration: dx=6px, dy=6px, plate=ink keyline plate offset from the fill plates; constant, never animated; overlap: blend=multiply, opacity=0.9, note=risograph overlap where two fills cross; gloss: color=#FFF6E0, opacity=0.6, shape=12-unit rounded bar at 35 degrees, top-left of each sticker |
| **Nest** | edge: filter=feTurbulence + feDisplacementMap, baseFrequency=0.04, octaves=2, displacement=3; grain: filter=feTurbulence fractalNoise, baseFrequency=0.7, octaves=1, opacity=0.05, blend=multiply |
| **Sprig** | paper-fibre: filter=feTurbulence fractalNoise, anisotropic, baseFrequency=0.012 0.4, octaves=3, opacity=0.06, blend=multiply; ink-coverage-max=0.6; fill-opacity=0.92 |
| **Lull** | grain: filter=feTurbulence fractalNoise, baseFrequency=0.8, octaves=1, opacity=0.05, blend=screen; bloom: stdDeviation=24px, opacity=0.4, color=#FFB866, rule=bloom on the single warm light only; one bloom source per frame |
| **Stack** | kraft: filter=feTurbulence fractalNoise, horizontal corrugation, baseFrequency=0.02 0.5, octaves=2, opacity=0.1, blend=multiply; stamp-ink: coverage=0.85, edge-displacement=2, baseFrequency=0.3 |
| **Mise** | paper: filter=feTurbulence fractalNoise, baseFrequency=0.6, octaves=2, opacity=0.04, blend=multiply; foil: gradient=linear, 30 degrees, stops=mix(foil, oxblood, 0.3) -> foil -> mix(foil, cream, 0.4), rule=one foil element per layout |
<!-- generated:surface-system:end -->

**Density scale** (`brand.density`): 1 means ≤ 3 props and ≥ 60% negative space; 2 means ≤ 5 and ≥ 50%; 3 means ≤ 8 and ≥ 40%; 4 means ≤ 12 and ≥ 30%; 5 means ≤ 20 and ≥ 15%. Negative space is the fraction of the frame left as plain `role.bg`.

---

## 7. Accessibility rules

| Area | Rule | Standard | Enforced by |
|---|---|---|---|
| Text contrast | Body ≥ 4.5:1, large ≥ 3:1 for every declared pair and every role pair; Cram ≥ 7:1 / 4.5:1 | WCAG 2.2 1.4.3, 1.4.6 | `check-contrast.py` |
| Non-text contrast | `focus`, `line` and UI marks ≥ 3:1 on `bg` and `surface` | 1.4.11, 2.4.11 | `check-contrast.py` |
| Focus | 3px outline, 2px offset, colour `role.focus`, following the element radius | 2.4.7, 2.4.11 | tokens `brand.focus` |
| Colour-blind | Every palette is simulated for protanopia, deuteranopia and tritanopia (Machado 2009, severity 1.0). Declared pairs need normal ΔE ≥ 15 and simulated ΔE ≥ 8; 6–8 is allowed only with a declared secondary cue. | Section 21 | `check-cvd.py` |
| Meaning | Colour is never the only carrier: stickers have shape and label, calendar days have a stamp tick, pictograms have shape, and personas carry silhouette and name. | 1.4.1 | review + `distinguish.secondaryCue` |
| Text spacing | Text line-height ≥ 1.5 in every persona | 1.4.12 | `check-tokens.py` |
| Targets | ≥ 44 × 44px everywhere; Nest ≥ 56px | 2.5.5 | `check-tokens.py` |
| Motion | Reduced-motion variant for every clip: a poster frame plus opacity crossfades only (500ms, ≤ 1 per bar), with no translate, scale, rotate, squash or parallax | 2.3.3 | Gate 4 loop check |
| Flashing | < 3 flashes per second, and a flash may change luminance by > 10% over at most 25% of the frame. Riot's flame pulse is fixed at 2 Hz (one per beat). | 2.3.1 | `check-tokens.py` (rates), Gate 4 frame analysis |
| Sound | No autoplay with sound. Every audio cue ships with a silent version plus captions (`.vtt`) or a visual equivalent. | 1.2.1, 1.4.2 | naming rule for `-silent` / `-captions` files |
| Alt text | Written for every illustration in the PDF and web pages: what the mascot is doing, plus its persona name | 1.1.1 | Gate 5 review |
| Zoom | Web pages reflow at 320 CSS px and at 200% zoom without loss | 1.4.10 | Gate 5 |
| Small sizes | Every mascot at 16, 32, 64 and 512px; recognition strokes ≥ 16 rig units (1px at 64px) | Section 18.15 | rig `lod` rule, Gate 6 stress tests |

---

## 8. Static illustration system

### 8.1 Per persona (Section 7), in `static/NN-slug/`

| Deliverable | File | Contents | Required tokens |
|---|---|---|---|
| Rig SVGs | `NN-mascot-rig-{front,three-quarter,side}.svg` | layered, named per `rig-spec` | colour, shape, rig |
| Character sheet | `NN-mascot-sheet-{turnaround,expressions,poses,props}.svg` | 3 views, 8 expressions, ≥ 3 poses, props, plus B&W/one-colour where relevant | all |
| Consumption scene | `NN-mascot-scene.svg` | prepare / eat / share / customise; lit for its Section 18.5 hour; product visible but not ad-like; density per token | texture, density, day |
| Visual-world board | `NN-mascot-board.svg` | palette swatches with roles, type specimen, shape language, pattern and texture, icons, layout example, one packaging / social / recipe-card application | everything |
| Overview panel | `NN-mascot-panel.svg` | mascot, name, core motivation, key consumption moment, world summary; noodle thread at 62% height | brand.noodle-thread |

### 8.2 Hero: seven ways to eat one packet (Section 18.1)

The same pack silhouette, sachet, "2" mark and steam curl appear at **identical position and scale** in all seven worlds. Constants are the pack silhouette, sachet, "2" and steam curl. Everything else varies. Used as the PDF cover, overview centrepiece and social teaser.

### 8.3 Scene light by hour (Section 18.5)

Order on the overview: Sprig 07:30 cool daylight → Stack 10:30 neutral busy → Cram 13:00 flat fluorescent with hard shadows → Nest 16:15 warm afternoon sun → Riot 19:30 coloured practicals with phone glow → Mise 21:00 low warm pendant with rich shadows → Lull 00:45 blue-violet dark with one warm glow.

### 8.4 Stress tests (Section 18.15, Gate 6)

Each mascot at 16 / 32 / 64 / 512px; as a one-colour stamp, enamel-pin outline and app icon; plus the 32px solid-black silhouette lineup. The silhouette test passes when a reviewer names all seven at a glance and no two silhouettes exceed 85% IoU after normalising to the same bounding-box height.

---

## 9. Motion and sound system

### 9.1 Grid and easing

<!-- generated:motion-grid:start -->
Clock **120 BPM**, beat 500ms, bar 2000ms, **24 fps** (12 frames per beat, 48 per bar). Flash ceiling 3 per second.

| Easing token | cubic-bezier | Use |
|---|---|---|
| `ease-in-soft` | 0.42, 0, 1, 1 | Anticipation and wind-up. |
| `ease-out-pop` | 0.34, 1.56, 0.64, 1 | Release with slight overshoot. |
| `ease-settle` | 0.22, 1, 0.36, 1 | Damped landing. Spring equivalent in motion.spring.ease-settle for engines that support springs. |
| `ease-linear-steam` | 0, 0, 1, 1 | Steam, drift, continuous rotation. |

| Mascot | Tempo feel | Idle loop | Amplitude | Squash/stretch | Anticipation (frames) | Accent beats | Pulse Hz |
|---|---|---|---|---|---|---|---|
| **Cram** | tired but quick | 2 s | 1.1 | 0.12 | 2 | 1, 3 | 0 |
| **Riot** | syncopated | 2 s | 1.4 | 0.18 | 3 | 1.5, 3.5 | 2 |
| **Nest** | smooth | 4 s | 0.9 | 0.06 | 6 | 1 | 0 |
| **Sprig** | balanced | 4 s | 0.7 | 0 | 6 | 1, 3 | 0 |
| **Lull** | slow breathing | 4 s | 0.6 | 0 | 12 | 1 | 0.25 |
| **Stack** | rhythmic and exact | 2 s | 0.8 | 0.04 | 4 | 1, 2, 3, 4 | 0 |
| **Mise** | cinematic and precise | 4 s | 0.6 | 0 | 8 | 1 | 0 |
<!-- generated:motion-grid:end -->

**Reading the table.** *Amplitude* multiplies every displacement in the shared motion library. *Squash/stretch* is the maximum scale deformation (0.12 = 12%). *Anticipation* is the wind-up in frames before a pop. *Accent beats* are positions in the 4-beat bar (1.5 = the "and" of beat 1). *Overshoot* and *stagger* are in `persona.*.motion` (`overshootPct`, `staggerFrames`).

**Clip lengths** (all whole bars): idle 2 s or 4 s, reaction 2 s, micro-animation 1–2 s, consumption scene 8 s (4 bars), sound signature 2 s.

**Layer order** (back to front): background → environment → body → face → limbs → props → noodles and steam → foreground type.

**Principles** (Section 20): anticipation before every pop; overlap on secondary parts (steam, hair, noodles) delayed by `staggerFrames`; squash and stretch only for the bouncy personas (Riot, Cram, with small amounts for Nest and Stack); zero squash and zero overshoot for the calm three (Sprig, Lull, Mise).

**Character motion vs UI motion.** Character clips use the bar grid. UI transitions on the web pages use `motion.ui`: 125ms (3 frames) for hover and press, 250ms (6 frames) for toggles and the persona switch, 500ms (one beat) for page-level reveals only, and 83ms (2 frames) between staggered items. Direct feedback never blocks input.

**Per-clip exports**: MP4 (H.264), WebM, GIF or APNG for stickers, and a poster PNG. Sizes are 1080×1080, 1920×1080 and 1080×1920, plus a silent version and a reduced-motion version. The first and last frames of every loop must match (checked at Gate 4).

### 9.2 Sound: seven signatures, one chord (Section 18.8)

<!-- generated:sound-chord:start -->
| Mascot | Pitch | Frequency | Role | Palette | ASMR layer |
|---|---|---|---|---|---|
| **Stack** | C2 | 65.41 Hz | root, dependable | box stacking thuds, calendar tick | no |
| **Nest** | G2 | 98.0 Hz | support (fifth) | kettle pour, wooden spoon on pot | no |
| **Lull** | E3 | 164.81 Hz | warm third | low hum, soft chime, whispered ASMR layer | yes |
| **Cram** | B3 | 246.94 Hz | tired seventh | kettle click, fork tap, phone timer blip | no |
| **Sprig** | D4 | 293.66 Hz | airy ninth | leaf rustle, glass chime | no |
| **Riot** | F#4 | 369.99 Hz | spicy sharp eleventh | sizzle, sticker pop, record-scratch accent | no |
| **Mise** | A4 | 440.0 Hz | refined thirteenth | sauce pour, chopstick tap, light string | no |
<!-- generated:sound-chord:end -->

The tuning is 12-TET at A4 = 440 Hz. Played together, the seven tones form a C lydian stack, the sonic logo. Audio is synthesised with Python and ffmpeg only, with no third-party samples. Every signature ships with a silent version and captions.

---

## 10. Asset naming and file structure

The rules are in `system/naming-rules.md` and enforced by `tools/check-names.py`. In summary: lowercase ASCII kebab-case; persona folders `NN-slug`; persona files `{NN}-{mascot}-{asset}[-qualifiers][-WxH].{ext}`; SVG ids `{mascot}__{slot}[__{part}[__{subpart}]][--{state}]`.

```text
.
├── brief/maggi-persona-project-brief-v2.md
├── CLAUDE.md (claude.md)
├── markdown/          00 system file (this) · 01–07 persona files at Gate 3
├── system/
│   ├── tokens/        tokens.json (source of truth) · tokens.schema.json · personas/NN-mascot.tokens.json (generated)
│   ├── rig-spec.md · rig-spec.json · rig-manifest.json (generated)
│   ├── naming-rules.md
│   └── claude-design-handoff.md
├── static/NN-slug/    rig, sheets, scene, board, panel                    Gate 2–3 · Claude Design
├── motion/NN-slug/    idle, reaction, micro, scene, poster                Gate 4 · Claude Code
├── glyphs/NN-slug/    "2", wordmark, numerals (SVG)                       Gate 1 tests → Gate 3 · Design
├── cards/NN-slug/     card fronts; cards/card-back.svg                    Gate 5 · Design
├── stickers/NN-slug/  512×512 reaction stickers                           Gate 5 · Design
├── packaging/NN-slug/ concept pack mockups                                Gate 6 · Design
├── hero/              seven-ways-to-eat-one-packet                        Gate 5 · Design
├── sound/             NN-mascot-signature(-silent|-captions), chord       Gate 4 · Code
├── locale/            india · malaysia-singapore · australia-new-zealand · west-africa · europe
├── merch/             pins, tote, kettle sticker                          Gate 6 · Design
├── stress-tests/      scale · silhouette · colour-blind · one-colour · qa (validator reports)
├── web/               live-clock · quiz                                   Gate 5 · Code
├── tools/             build-tokens, check-*, run-all (Python 3.10+, stdlib only)
├── maggi-persona-overview.png                                             Gate 5
└── maggi-persona-system.pdf                                               Gate 5
```

---

## 11. Research insights and competitor framework

### 11.1 Evidence rules

Only findings from the brief's research evidence log (Section 27) are used as market claims, and each keeps its confidence tag. **High** means a primary or reputable trade source. **Medium** means secondary or older. **Low** means a vendor estimate or weak source, so treat it as directional only. Anything not in the log is labelled **Hypothesis** and needs primary research (Nielsen, Kantar or first-party data) before any commercial use.

### 11.2 Research questions (Section 11)

| Question | What the evidence log supports | Confidence | Status |
|---|---|---|---|
| What jobs does Maggi do? | India is Nestlé's largest Maggi market, with over six billion servings in FY24. Food ASMR is an established sensory trend. | High · Medium | The seven jobs in section 1 are a design segmentation (**Hypothesis**) to validate. |
| When do people eat it? | No usage-occasion data in the log. | — | **Hypothesis.** The Section 18.5 day order is a visual device, not usage data. |
| Who buys vs who eats? | No buyer/eater data in the log. | — | **Hypothesis.** The Section 17 spine is the test framework. |
| Does customisation affect loyalty? | No direct data. The Maggi Spicy "Mujhe Mirch Nahi Lagti" Gen Z campaign (2026) frames spice as self-confidence. | High (campaign exists) | **Hypothesis** for the loyalty effect. |
| What role does nostalgia play? | Maggi marked 50 years in India (postal stamp, Feb 2026); noodles launched 1983. Malaysian two-minute noodles launched 1971 (curry, chicken). Maggi originated in Switzerland in 1884 and was acquired by Nestlé in 1947. | Medium–High · High · High | Nostalgia is used as a motif (stamps, postmarks). Its effect on purchase is a **Hypothesis**. |
| How do health concerns affect choices? | Critics flagged high sodium in atta and oats variants (label reads 2017–18; formulations may have changed). 2015 India ban, relaunch November 2015. Transparency is very important to 65% of consumers for sustainable food. | Medium · High · Medium | This drives the Sprig "additive" rule and the no-claims rule. Current labels must be re-checked. |
| Price, pack size, availability? | Price anchor around ₹14 per 70g; the ₹25–40 mid-premium band is thin; around 6 servings per capita per year. Nongshim launched Shin Ramyun Kimchi Stir Fry in India via quick commerce (May 2026). | Low (vendor) · High | Directional only. Supports Stack's price-per-serving cue and Mise's trade-up gap. |
| How does Maggi compete? | Korean noodles are a fast-growing premium segment, and Maggi's Korean variants are priced far above core packs. Maggi holds roughly 55–65% of India's instant-noodle market, but estimates vary widely. | Medium · Medium | Share figures are not used in any asset. |
| Gaps per persona? | Real cook time is longer than the "2-minute" name. | Medium | Basis for "felt time" (a concept, not a claim). Pack mechanics are concepts (Section 18.11). |
| What makes people recommend? | Characters improve brand linkage and recall (Ipsos, via trade press). Indomie (Nigeria) runs a school fan club with 3,000+ branches and 100,000+ members. Maggi's earned media value rose from $3M (2020) to $139.8M (2025), India about 24%. Pot Noodle used a 12-second slurp as a brand sound. | Medium · Medium · Low (vendor metric) · High | Supports mascots, the "collect all seven" cards, community mechanics and the sound signature. |

Other logged context: "Maggi Ready Family Jolly" Tamil Nadu regional campaign (May 2026, High); Maggi Hotspots kiosks at colleges and tourist spots (Medium); in West Africa and parts of Europe Maggi is known mainly as cubes, seasoning and sauce (High); Duolingo's custom typeface derived from its mascot (High), the model for Section 18.6; Cup Noodles' paper microwavable cup (High).

**Known data problems** (from Section 27). Market-share numbers conflict across sources and are mostly estimates. Some sources are vendor blogs or aggregator pages. Nutrition numbers come from older label reads. Evidence for markets outside India is thinner. No number here should drive a commercial decision without primary research.

### 11.3 Competitor framework

The structure is set by Section 12; the persona-specific anchors come from Section 17. Each cell is tagged with its basis: **[§17]** stated in the brief, **[E-High]/[E-Med]** from the evidence log, **[H]** hypothesis to test.

| Mascot | Direct competitors | Indirect competitors | Likely switching trigger | Likely return / recommend trigger |
|---|---|---|---|---|
| Cram | Other low-price instant noodles [H] | Biscuits, chips, campus canteen [H] | A cheaper pack or no kettle access [H] | Zero cleanup at the lowest price [§17] |
| Riot | Internet hacks and street food [§17] | Delivery food [H] | A more viral flavour trend [H] | Worth making *and* posting [§17] |
| Nest | Other kid-accepted instant noodles [H] | Pasta, sandwiches, homemade quick meals [H] | The child says no [§17] | The child says yes, again [§17] |
| Sprig | Millet, grain, protein or low-oil noodles [H] | Salads, ready-to-eat bowls [H] | Doesn't fit my goals [§17]; sodium concern [H] informed by E-Med label critiques | Transparent "what's in your bowl" plus fresh add-ins [H] informed by E-Med transparency finding |
| Lull | Instant soup, frozen meals [H] | Late-night delivery, snacks [H] | Effort or cleanup at night [H] | A comfort ritual that helps you land [§18.13] |
| Stack | Multipacks of other brands [H] | Rice, flatbread, pasta staples [H] | Price per serving or out of stock [§17] | Reliable availability and value [§17] |
| Mise | Korean and café noodles [§17] [E-Med] | Restaurant noodles, delivery [H] | A more authentic or premium alternative [H], made easier by Nongshim's quick-commerce launch [E-High] | Worth paying more [§17] |

---

## 12. Guardrails (Sections 14 and 22, binding)

- **Trademarks:** no real Maggi logo, packaging artwork or slogan. The brand-lockup slot stays empty.
- **Children:** no identifiable child faces; no child-directed claims; check local rules on advertising to children.
- **Health:** no nutrition, sodium or "healthy" claims. Anything near health is marked *needs Nestlé review*. Cook-time lines are "felt time" concepts only.
- **Reviews:** sample reviews in persona files are **synthesised composites, labelled as such**.
- **Real people:** no celebrities, creators or public figures.
- **Culture:** mascots are creatures. Locale packs avoid flag-colour stereotypes and accent jokes, and are reviewed by local collaborators before use.
- **Design:** no recolour-only mascots; the B&W persona must be full of personality; Riot's clashes follow the written grammar; motion is never decoration alone.

---

## 13. Gate 1 decision log and handoff

### 13.1 Decisions made at Gate 1 (review requested)

| # | Decision | Why | Alternative |
|---|---|---|---|
| D1 | The brief moved to `brief/maggi-persona-project-brief-v2.md` (was `reference file`) | CLAUDE.md points there; the old name broke the naming rules | Keep the old name and edit CLAUDE.md |
| D2 | The project lives at the repo root, not in a `maggi-persona-project/` subfolder | The repo *is* the project | Nest everything one level down |
| D3 | Cram's sachet is solid ink plus a 25% screen, with no spot colour | Section 18.12 strict B&W wins over the red/yellow sachet | A single red/yellow spot on the sachet only |
| D4 | Mise's default background is oxblood (dark) | The foil fails on cream (2.03:1); 21:00 pendant-light mood | A cream-first layout with no foil text |
| D5 | Felt-time lines for Riot, Sprig and Stack | The brief gives four and says "and so on" | Rewrite |
| D6 | Optional `limbs-back` slot added before `body` | Turnarounds need the far arm behind the torso without re-layering | Duplicate arms per view |
| D7 | All palette hexes, type faces, textures and construction metrics | Design judgement; the brief gives none | Any change, provided the validators still pass |
| D8 | Stack's focus ring is ink, not shelf-blue | Shelf-blue on kraft is 2.86:1 (< 3:1) | Lighter kraft, which then weakens price-tag separation |
| D9 | Stack's kraft darkened to `#C4A27A` | The price tag on kraft was ΔE 11 (< 15) for normal vision | A white price tag |
| D10 | Persona key colours chosen by a 384-combination search | Best worst-case separation of all 21 pairs | Hand-picked "signature" colours (e.g. Nest red) with weaker separation |

### 13.2 Still open in Gate 1 (Claude Design)

The **seven-mascot silhouette lineup** and the **"2" glyph tests** are artwork and are not in this commit. The brief is in `system/claude-design-handoff.md`. Gate 1 is complete when both are reviewed against the question *"Do the mascots feel like one universe yet seven distinct creatures?"*
