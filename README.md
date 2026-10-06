# userpersonas: Maggi persona and mascot design system

Seven stylised Maggi consumer personas, each with its own mascot and visual world, built gate by gate (brief Section 25).

- Brief: `brief/maggi-persona-project-brief-v2.md` (Part II wins on conflict)
- Working rules for Claude: `claude.md`
- System file: `markdown/00-maggi-persona-design-system.md`
- Source of truth: `system/tokens/tokens.json` (rig: `system/rig-spec.md`, names: `system/naming-rules.md`)
- Next for Claude Design: `system/claude-design-handoff.md`

## Validate

Python 3.10+, standard library only.

```sh
python tools/build-tokens.py   # regenerate persona token files + doc tables after editing tokens.json
python tools/run-all.py        # tokens, contrast, colour-blind, naming, rig -> stress-tests/qa/
```

Concept work only: no real Maggi logo, packaging or slogans; no health claims; no identifiable child faces.
