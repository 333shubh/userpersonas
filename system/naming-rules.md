# Naming rules

Status: **Gate 1 proposal**. Enforced by `tools/check-names.py`, which reads the JSON block at the end of this file. Edit the block and this prose together; the block is the machine source.

## 1. Universal rules

| # | Rule | Example (pass) | Example (fail) |
|---|---|---|---|
| U1 | ASCII only, lowercase, no spaces. | `01-cram-scene.svg` | `Cram Scene.svg` |
| U2 | Words are joined with single hyphens (kebab-case). No underscores in file or folder names. Double underscores appear only inside SVG ids (section 5). | `value-stocking-homemaker` | `value_stocking_homemaker` |
| U3 | Every file has an extension from the allowed list (section 6). Compound extensions are allowed only where listed (`.tokens.json`, `.schema.json`). | `01-cram.tokens.json` | `01-cram.tokens` |
| U4 | Numbers that order things are zero-padded to two digits. | `03-practical-parent` | `3-practical-parent` |
| U5 | Pixel sizes are written `{width}x{height}` with a lowercase `x`, last before the extension. | `01-cram-idle-1080x1080.mp4` | `01-cram-idle-1080X1080.mp4` |
| U6 | Exempt names (tooling and repo conventions): `README.md`, `CLAUDE.md`, `claude.md`, `LICENSE`, `.gitkeep`, `.gitignore`, `.gitattributes`, `.editorconfig`. | | |
| U7 | Ignored paths: `.git/`, `.claude/`, `__pycache__/`. | | |

## 2. Persona identifiers

| Number | Persona slug (folders, Markdown) | Mascot id (files, SVG ids, tokens) |
|---|---|---|
| 01 | `01-hostel-hungry` | `cram` |
| 02 | `02-maximalist-foodie` | `riot` |
| 03 | `03-practical-parent` | `nest` |
| 04 | `04-conscious-upgrader` | `sprig` |
| 05 | `05-midnight-recharger` | `lull` |
| 06 | `06-value-stocking-homemaker` | `stack` |
| 07 | `07-premium-flavor-explorer` | `mise` |

Slugs are fixed by brief Section 10 (US spelling "flavor" is kept because the brief uses it in the file name). Mascot ids are the Section 19 working names, lowercased. If a working name changes after language validation, the mascot id changes everywhere in one commit and the token check confirms it.

## 3. Persona asset files

Inside any persona folder (`static/`, `motion/`, `glyphs/`, `cards/`, `stickers/`, `packaging/` → `NN-slug/`):

```
{NN}-{mascot}-{asset}[-{qualifier}...][-{W}x{H}].{ext}
```

- `{NN}-{mascot}` must match the folder it sits in (`01-cram-…` only inside `01-hostel-hungry/`).
- `{asset}` must come from that folder's vocabulary (section 4).
- Qualifiers are kebab words from the qualifier list, in this order when combined: view → expression/pose → variant → delivery. Example: `01-cram-sheet-expressions-bw.svg`, `02-riot-idle-reduced-1080x1920.mp4`.

## 4. Asset vocabulary per folder

| Folder | Allowed `{asset}` values | Typical files |
|---|---|---|
| `static/NN-slug/` | `rig`, `sheet`, `scene`, `board`, `panel`, `silhouette` | `01-cram-rig-front.svg`, `01-cram-sheet-turnaround.svg`, `01-cram-scene.svg`, `01-cram-board.png` |
| `motion/NN-slug/` | `idle`, `reaction`, `micro`, `scene`, `poster` | `01-cram-idle-1080x1080.mp4`, `01-cram-idle-silent-1080x1080.webm`, `01-cram-idle-reduced-1080x1080.mp4`, `01-cram-idle-poster-1080x1080.png` |
| `glyphs/NN-slug/` | `two`, `wordmark`, `numerals`, `numeral` | `01-cram-two.svg`, `01-cram-wordmark.svg`, `01-cram-numeral-7.svg` |
| `cards/NN-slug/` | `card` | `01-cram-card-front.svg`, `01-cram-card-front-750x1050.png` |
| `stickers/NN-slug/` | `sticker` | `02-riot-sticker-shock-512x512.png` |
| `packaging/NN-slug/` | `pack` | `06-stack-pack-concept.png` |

Qualifiers (enforced, except in `stickers/` where the reaction word is free kebab-case): `front`, `side`, `three-quarter`, `back`, `turnaround`, `expressions`, `poses`, `props`, `bw`, `colour`, `one-colour`, `concept`, `silent`, `reduced`, `poster`, `captions`, plus any expression name from `system/rig-spec.json` and numerals `0`–`9`. Sticker reactions use any kebab word.

## 5. SVG ids

Defined in `system/rig-spec.md`. Grammar: `{mascot}__{slot}[__{part}[__{subpart}]][--{state}]`, for example `riot__body__flame-hair__flame-2`, `lull__face__lid-l--half`. Full required lists: `system/rig-manifest.json`.

## 6. Shared folders and reserved names

| Path | Allowed names |
|---|---|
| repo root | `maggi-persona-overview.png`, `maggi-persona-system.pdf` (Gate 5) |
| `markdown/` | exactly `00-maggi-persona-design-system.md` and the seven `NN-slug.md` files |
| `hero/` | `seven-ways-to-eat-one-packet.png`, `seven-ways-to-eat-one-packet.pdf` |
| `cards/` (root) | `card-back.svg`, `card-back.png` |
| `sound/` | `{NN}-{mascot}-signature[-silent].{wav\|mp3}`, `{NN}-{mascot}-signature-captions.vtt`, `chord.{wav\|mp3}`, `sound-spec.md` |
| `locale/` | folders: `india`, `malaysia-singapore`, `australia-new-zealand`, `west-africa`, `europe`; files kebab-case |
| `stress-tests/` | folders: `scale`, `silhouette`, `colour-blind`, `one-colour`, `qa`; files kebab-case |

Allowed extensions: `md`, `json`, `py`, `svg`, `png`, `pdf`, `mp4`, `webm`, `gif`, `apng`, `wav`, `mp3`, `vtt`, `html`, `css`, `js`, `txt`.

## 7. Machine rules

```json naming-rules
{
  "exempt": ["README.md", "CLAUDE.md", "claude.md", "LICENSE", ".gitkeep", ".gitignore", ".gitattributes", ".editorconfig"],
  "ignoreDirs": [".git", ".claude", "__pycache__"],
  "extensions": ["md", "json", "py", "svg", "png", "pdf", "mp4", "webm", "gif", "apng", "wav", "mp3", "vtt", "html", "css", "js", "txt"],
  "compoundExtensions": ["tokens.json", "schema.json"],
  "segment": "^[a-z0-9]+(-[a-z0-9]+)*$",
  "personas": {
    "01-hostel-hungry": "cram",
    "02-maximalist-foodie": "riot",
    "03-practical-parent": "nest",
    "04-conscious-upgrader": "sprig",
    "05-midnight-recharger": "lull",
    "06-value-stocking-homemaker": "stack",
    "07-premium-flavor-explorer": "mise"
  },
  "personaFolders": {
    "static": ["rig", "sheet", "scene", "board", "panel", "silhouette"],
    "motion": ["idle", "reaction", "micro", "scene", "poster"],
    "glyphs": ["two", "wordmark", "numerals", "numeral"],
    "cards": ["card"],
    "stickers": ["sticker"],
    "packaging": ["pack"]
  },
  "qualifiers": ["front", "side", "three-quarter", "back", "turnaround", "expressions", "poses", "props", "bw", "colour", "one-colour", "concept", "silent", "reduced", "poster", "captions", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
  "qualifiersFromRigExpressions": true,
  "freeQualifierFolders": ["stickers"],
  "reserved": {
    "": ["maggi-persona-overview.png", "maggi-persona-system.pdf"],
    "markdown": ["00-maggi-persona-design-system.md", "01-hostel-hungry.md", "02-maximalist-foodie.md", "03-practical-parent.md", "04-conscious-upgrader.md", "05-midnight-recharger.md", "06-value-stocking-homemaker.md", "07-premium-flavor-explorer.md"],
    "hero": ["seven-ways-to-eat-one-packet.png", "seven-ways-to-eat-one-packet.pdf"]
  },
  "fixedSubfolders": {
    "locale": ["india", "malaysia-singapore", "australia-new-zealand", "west-africa", "europe"],
    "stress-tests": ["scale", "silhouette", "colour-blind", "one-colour", "qa"],
    "web": ["live-clock", "quiz"]
  },
  "soundFile": "^(0[1-7])-([a-z]+)-signature(-silent|-captions)?\\.(wav|mp3|vtt)$|^chord\\.(wav|mp3)$|^sound-spec\\.md$",
  "requiredFolders": ["markdown", "system", "system/tokens", "system/tokens/personas", "static", "motion", "hero", "cards", "glyphs", "sound", "locale", "packaging", "stickers", "merch", "stress-tests", "web", "tools", "brief"]
}
```
