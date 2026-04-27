---
name: codex-starship-design-assets
description: Validate and maintain Starship Battles designs, data files, and visual asset tooling. Use for Tools/validate_designs, QS complex design data, component visuals, galaxy screenshots, asset processors, image tools, design JSON validation, and docs/guides/qs_complex_design.md or Tools/README.md workflows.
---

# Codex Starship Design Assets

Use this skill for design-data validation and asset/tool workflows that are not full ship theme creation.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `Tools/README.md`.
3. Read task-specific tool README files before running tools.
4. For design JSON or QS complexes, read `docs/guides/qs_complex_design.md`, `docs/guides/component_system.md`, and relevant system docs.

## Design Validation

- Use `python Tools/validate_designs/validate_designs.py <directory>` for design validation.
- Report validation categories and affected files before fixing design data.
- Do not automatically fix designs unless the user requested fixes.
- If fixes require code changes, use strict TDD.
- If fixes change data conventions, update the relevant docs.

## Asset Tooling

- Use the tool-specific README under `Tools/` for command syntax and expected outputs.
- Keep generated preview/output artifacts out of version control unless the tool docs or user explicitly say they are source assets.
- For UI-visible assets, verify actual rendered output when practical.
- For image-processing tools, preserve source inputs and document generated outputs.

## Common References

- `Tools/validate_designs/README.md`
- `Tools/component_visuals_manager/README.md`
- `Tools/component_transparency_viewer/README.md`
- `Tools/galaxy_screenshot/README.md`
- `Tools/inspect_galaxy/README.md`
- `docs/guides/qs_complex_design.md`
