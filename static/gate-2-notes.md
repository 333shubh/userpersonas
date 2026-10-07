# Gate 2 pilot: notes for QA

Scope: 01 Cram and 02 Riot only. No animation.

## Checked before handoff
- Rigs (6): every Cram/Riot id in `system/rig-manifest.json` is present, with no extras or duplicates. Slots are direct children of `<svg>` in spec order. 15 anchors per view, all `r="0"` circles in `__rig`. Every group transform is `translate()` only.
- No `<text>`, `<image>`, `<script>` or `<foreignObject>` in any file. All lettering is outlined from Archivo Black, IBM Plex Mono, Bungee and Rubik (OFL; the TTFs are in `tools-design/fonts/`).
- Every hex value in every file is from that persona's token file (6 for Cram, 10 for Riot).
- Strokes stay strokes: Cram 16 with square caps, Riot 20 with round caps.

## Decisions to review
1. **Sheets, scenes and boards place characters with `translate() scale()` on unnamed wrapper groups.** Ids are stripped inside them, so nothing animatable is scaled. Rigs use translate only.
2. **Cram's halftone** uses token screen greys on rigs, and a 1-bit ink-dot `<pattern>` (rotated 45°) for scene shadows and board texture. I skipped the grain filter: feTurbulence makes non-token colours.
3. **Riot clash regions:**
   - Body: chili, yolk, cyan.
   - Wall: ultraviolet, yolk, cyan.
   - Neon (on an ink board): hot-pink, acid-green.
   - Counter top (separated by an ink edge): yolk, chili.
   - Counter front: volt-blue, tangerine.

   Non-pair contacts carry the 20-unit ink keyline, offset +6/+6 as the misregistration plate. Text sits only on paper stickers, ink, or one flat colour.
4. **Riot's 3 flames:** flames 1 and 3 are chili and flame 2 is yolk, to stay at 3 clash colours in the body region. Riot's noodles hang from the mouth, and steam rises off the flame tip. Steam-origin is at (566, 192).
5. **Gloss and overlap texture tokens** use paper at opacity 0.6 and multiply at 0.9. These are the only blended colours, and both are token-defined.
6. **Poses:**
   - Sachet moment: tear-strip `translate(-28 -64)`.
   - Reaction: every top-level part `translate(0 -48)`, with the ground left in place.
   - Cram's reaction also uses `phone-timer--ringing`.
7. **Density:**
   - Cram's scene has 5 props: sachet, fork, backpack, timer and kettle. More than 50% of the frame is empty.
   - Riot's scene has 11 props.
8. **Scenes:**
   - Cram (13:00): one overhead tube light, so shadows fall straight down and hard.
   - Riot (19:30): a yolk pendant lamp, pink/green neon and a cyan phone glow.

## Rebuild
Run `tools-design/gate2-build.js`. It uses `gate2-lib.js` (rigs), `gate2-sheets.js` (sheets, scenes, boards) and `ttf-outline.js`.
