# Handoff spec: Claude Design, rest of Gate 1, then Gate 2

Status: ready once the Gate 1 system (this commit) is approved. Owner: Claude Design. Reviewer: project lead.

## Read in this order

1. `CLAUDE.md`, then `brief/maggi-persona-project-brief-v2.md` Sections 5, 6, 7, 18.1, 18.6, 18.12, 18.15, 19, 22, 24, 25 (Part II wins on conflict).
2. `markdown/00-maggi-persona-design-system.md`: sections 1, 2, 5 and 6.
3. `system/rig-spec.md`: the drawing contract. Construction targets are in section 7.
4. `system/tokens/personas/NN-mascot.tokens.json`: one resolved file per mascot. **Use only these hex values, faces, strokes and radii.**
5. `system/naming-rules.md`: file names.
6. `system/rig-manifest.json`: exact ids, needed from Gate 2.

---

## A. Gate 1 deliverable 1: seven-mascot silhouette lineup

### Overview
Prove the seven mascots read as **one universe yet seven distinct creatures** (the Gate 1 question) before any detailed character work. This is shape only: no faces, no colour.

### Layout
| Property | Value |
|---|---|
| Canvas | 7168 × 1024 (seven 1024 × 1024 cells, side by side) |
| Cell order | Section 18.5 day order: Sprig, Stack, Cram, Nest, Riot, Mise, Lull |
| Per cell | rig canvas rules: ground y = 896, centre x = 512 of the cell, height = heightRatio × 768 |
| Fill | `#000000` solid, no strokes, no interior detail |
| Background | `#FFFFFF` |
| Labels | none on the artwork (labels would help the reviewer cheat). A separate key file maps cell number to mascot. |

### What each silhouette must contain
Base shape + silhouette hook + arms + the sachet in `grip-r`, using the construction targets (±8%) in `rig-spec.md` §7.

| Mascot | Must be visible in pure black at 32px |
|---|---|
| Cram | headphone arc above the cup rim; upright fork |
| Riot | three flame points, the tallest in the middle-right |
| Nest | wide low dome with two bow loops behind |
| Sprig | single leaf pair rising high above the head |
| Lull | crescent bite out of the round head; three small star points above |
| Stack | three-step outline; price-tag flag on its string |
| Mise | crossed chopsticks forming an X above a slim footed bowl |

### Files
| File | Purpose |
|---|---|
| `stress-tests/silhouette/silhouette-lineup.svg` | master; each cell is a group `<g id="{mascot}">` |
| `stress-tests/silhouette/silhouette-lineup-224x32.png` | 32px-per-mascot render (the test) |
| `stress-tests/silhouette/silhouette-lineup-3584x512.png` | 512px-per-mascot render (review) |
| `stress-tests/silhouette/silhouette-lineup-key.md` | cell → mascot mapping |

### Acceptance tests
1. A reviewer who hasn't seen the key names all seven correctly from the 32px render within 10 seconds.
2. No two silhouettes exceed 85% IoU when scaled to the same bounding-box height (Claude Code computes this).
3. **Cram vs Stack** (aspect 0.57 vs 0.58) are clearly different at 32px. This is the known risk.
4. All seven share the family traits: the same ground line, the same arm construction and the same sachet silhouette.

### Edge cases
- If a hook disappears at 32px, enlarge the hook within the 8% tolerance. If that isn't enough, propose a new hook in a note rather than adding detail.
- No human silhouettes. Nest shows no child, not even as a silhouette, in this lineup.

---

## B. Gate 1 deliverable 2: "2" glyph tests

### Overview
Each persona's own "2" (Section 18.6), built from its mascot geometry, which must read as a 2 at 16px.

### Construction (tokens `brand.two-mark` + `persona.*.glyph`)
| Property | Value |
|---|---|
| Box | width : height = 1 : 1.25, baseline at the box bottom |
| Cap height | 80% of box height |
| Minimum stroke | 12.5% of glyph height (= 2px at 16px) |
| Minimum open counter | 25% of glyph width |
| Colour | `role.text` on `role.bg` of the persona; also a pure `#000000` version |

| Mascot | Construction idea (tokens) |
|---|---|
| Cram | cut from the cup cylinder with a fork-tine terminal; monoline, square terminals |
| Riot | built from a flame curl with a sticker die-cut outline; offset misregistration shadow 6 units |
| Nest | one continuous yarn-noodle loop, round terminals |
| Sprig | grown as a stem with a leaf at the hook |
| Lull | a crescent-moon arc with a steam tail, filled (no stroke) |
| Stack | three stacked blocks on the 8px grid, stencil-cut |
| Mise | high-contrast didone with a chopstick-straight base stroke |

### Files
| File | Purpose |
|---|---|
| `glyphs/NN-slug/NN-mascot-two.svg` | the glyph, outlined, `viewBox` = construction box |
| `stress-tests/scale/two-glyph-scale-test.svg` | all seven at 16, 32, 64 and 512px, colour and black |

### Acceptance tests
1. At 16px, each glyph is read as "2" by a reviewer with no context.
2. Measured stroke ≥ 12.5% of height and counter ≥ 25% of width (Claude Code measures the SVG).
3. In colour, contrast passes the persona's level (Cram AAA, others AA) when used as text.
4. No glyph resembles the real brand's lettering or logo.

---

## C. Gate 2 preview: pilot pair (Cram + Riot)

Not to start until A and B are approved. Per mascot:

| Deliverable | File | Notes |
|---|---|---|
| Rig, 3 views | `static/NN-slug/NN-mascot-rig-{front,three-quarter,side}.svg` | every id in `rig-manifest.json`; `tools/check-rig.py` must pass |
| Character sheet | `NN-mascot-sheet-turnaround.svg`, `-expressions.svg`, `-poses.svg`, `-props.svg` | 8 expressions by state swap only; ≥ 3 poses |
| Scene | `NN-mascot-scene.svg` | Cram 13:00 flat fluorescent; Riot 19:30 coloured practicals and phone glow |
| Board | `NN-mascot-board.svg` | palette with roles, type specimen, shape, texture, icons, one application |
| Idle loop | Claude Code builds it from the rig (`motion/`) | Cram 2 s, Riot 2 s; Riot's pulse at 2 Hz |

Riot's clash grammar applies to every Riot file: only the four listed clash pairs may touch without an ink keyline; at most 3 clash colours per region; text never crosses a clash seam. Cram is strictly achromatic: halftone screens of one ink only, and the sachet is ink plus a 25% screen.

## D. Never

- The real Maggi logo, packaging artwork or slogans. The lockup slot stays empty.
- Identifiable child faces.
- Health, nutrition or cook-time claims.
- Colours, fonts, radii or strokes that aren't in the persona token file. If you need a new value, ask for a token change first.
- Raster images, `<text>` or baked rotate/scale transforms in rig SVGs.
