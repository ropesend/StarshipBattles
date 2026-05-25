---
name: codex-ship-theme-creator
description: Create complete Starship Battles ship themes under assets/Images/ShipThemes. Use when the user wants a new faction/theme with generated top-down ship skins, off-axis space-view portraits, theme.json manifests, contact sheets, source preservation, and validation. This Codex-prefixed skill is repo-local and replaces the unprefixed user-level ship-theme-creator workflow for this project.
---

# Codex Ship Theme Creator

Create a new Starship Battles ship theme as a complete, game-ready asset folder. Use real image generation for art; do not substitute procedural line art except for temporary diagnostics explicitly requested by the user.

## Initial Questions

Ask these before generating, unless the user already answered them:

1. Theme name.
2. Primary coloration and glow color.
3. Visual motif/material language, for example crystalline, organic, naval, brutalist, ancient relic, biotech, solar, void.
4. Any avoid list, especially colors or shapes too close to existing themes.
5. Whether weapons should be visible. Default to **no visible turrets, cannon barrels, missile racks, or obvious external weapons**.
6. Whether any provided images are reference inputs, edit targets, or only mood examples. Default to reference inputs.

If the user gives a broad answer, make reasonable art-direction choices and proceed. Do not repeatedly stop for approval after the initial brief unless outputs are visibly wrong or the user asks for review checkpoints.

## Required Output

Create this folder shape:

```text
assets/Images/ShipThemes/<ThemeName>/
|-- theme.json
|-- Skins/
|-- Portraits/
`-- Production/
    |-- art_direction.md
    |-- skin_sources/
    |-- skin_alpha/           # optional, for chroma-key intermediates
    |-- portrait_sources/
    |-- contact_sheet_skins.png
    `-- contact_sheet_portraits.png
```

Do not modify existing themes unless the user explicitly asks.

## Reference Image Handling

- If the user provides or attaches a reference image, the model generating skin concepts or final skins MUST receive the actual image as an image input. Do not rely only on a text description of the image.
- Treat attached images as visual reference inputs by default, not edit targets. Use them to guide composition, massing, material language, lighting cues, or mood while still creating an original Starship Battles theme.
- If a reference image is visible only in the conversation context, use the built-in `image_gen` path that can see the attached image, or ask the user for a local file path before using a CLI/API path.
- If the reference image is available as a local file, use an image-input/edit-capable generation path such as `image_gen.py edit --image <reference-file>` for skin concepts and reference-driven skins.
- Do not use text-only `generate` or `generate-batch` for reference-driven skin concepts or final skins unless there is no actual reference image available to pass. `generate-batch` is acceptable only for no-reference text generation, or for a future tool path that explicitly supports per-job image inputs and actually passes them.
- Preserve local reference files under `Production/reference_sources/` when practical, so the theme's visual inputs remain auditable.
- In `Production/art_direction.md`, list every reference image used and state how it was used, for example "massing inspiration", "surface material reference", or "mood only".

## Class List

Generate exactly these 19 classes:

`Escort`, `Frigate`, `Destroyer`, `Light Cruiser`, `Cruiser`, `Heavy Cruiser`, `Battle Cruiser`, `Battleship`, `Dreadnought`, `Superdreadnought`, `Monitor`, `Fighter (Small)`, `Fighter (Medium)`, `Fighter (Large)`, `Fighter (Heavy)`, `Satellite (Small)`, `Satellite (Medium)`, `Satellite (Large)`, `Satellite (Heavy)`.

## Workflow

1. Inspect `assets/Images/ShipThemes` and `game/ui/assets/ship_theme_manager.py` if working in a Starship Battles repo you have not seen before.
2. Scaffold the new theme with `scripts/create_manifest.py`.
3. Write `Production/art_direction.md` with the theme brief, palette, motifs, avoid list, and prompt templates.
   - Define a **Theme Lock** block: exact palette, 3-5 repeated silhouette motifs, 3-5 repeated material details, glow placement rules, and weapon visibility rules.
   - Reuse the Theme Lock verbatim in every skin and portrait prompt. Vary only class scale/proportions and role-specific silhouette details.
   - If reference images are provided, document their file paths or attachment labels and how they influence the theme.
4. Generate skins with the image generation model:
   - Top-down orthographic.
   - Nose upward for ships.
   - Centered, single object, full object visible.
   - Flat `#00ff00` chroma-key background for removal.
   - No shadow, text, watermark, UI frame, or multiple ships.
   - No visible turrets, cannon barrels, missile racks, torpedo tubes, exposed gun pods, or obvious external weapons.
   - Weapon capability should be implied only by flush armor seams, recessed bay doors, sensor slits, hardpoint panel lines, or concealed ports integrated into the hull.
   - Generate and inspect a small early set of 3-5 classes before the full batch. If they do not clearly read as one fleet, revise the Theme Lock before continuing.
5. Copy generated skin originals into `Production/skin_sources/` using the expected skin filenames.
6. Run `scripts/process_theme_images.py --mode skins` to remove chroma-key, normalize to `2048x2048`, and create a skin contact sheet.
7. Generate portraits with the image generation model:
   - Three-quarter off-axis view from above/slightly in front.
   - Ship sailing through deep space.
   - Same palette and motif as skins.
   - No top-down orthographic view, green screen, text, watermark, UI frame, or multiple ships.
8. Copy generated portrait originals into `Production/portrait_sources/` using the expected skin filenames, then run `scripts/process_theme_images.py --mode portraits`.
9. Run `scripts/validate_theme.py`.
10. Report paths, validation results, and any art-quality caveats. Include contact sheet paths.

## Prompt Rules

Use the `imagegen` skill for all generated art.

For skins, start with:

```text
Use case: stylized-concept
Asset type: top-down 2D game ship sprite for Starship Battles
Primary request: Create a model-generated <THEME> <CLASS> starship.
Input image: if a reference image was provided, pass the actual image to the generation/edit call and use it as inspiration for massing, surface language, and mood. Do not merely describe the reference image in text.
Subject: <class-specific silhouette>.
Style/medium: polished sci-fi game asset, detailed hard-surface concept art, token-ready sprite.
Composition/framing: centered, top-down orthographic view, nose pointed upward, full object visible, generous padding, single object only.
Background: perfectly flat solid #00ff00 chroma-key background for background removal.
Constraints: no shadow, no text, no watermark, no UI frame, no multiple ships, do not use #00ff00 in the subject.
Weapon visibility: no visible turrets, cannon barrels, missile racks, torpedo tubes, exposed gun pods, or obvious external weapons. Weaponry must be implied by flush armor seams, recessed bay doors, sensor slits, hardpoint panel lines, or concealed ports integrated into the hull.
Theme consistency: include the same Theme Lock block in every class prompt. Reuse identical palette, materials, glow placement, panel language, and recurring silhouette motifs; vary only class size and role-specific proportions.
```

For portraits, start with:

```text
Use case: stylized-concept
Asset type: ship portrait for Starship Battles UI
Primary request: Create a <THEME> <CLASS> portrait.
Subject: A <CLASS> sailing through space, with the theme's palette and material language.
Composition/framing: three-quarter off-axis view from above and slightly in front, angled diagonally across the frame, full object visible, single object only.
Scene/backdrop: deep space with subtle stars and motif-colored nebula haze.
Constraints: no top-down orthographic view, no green screen, no text, no watermark, no UI frame, no multiple ships.
Weapon visibility: no visible turrets, cannon barrels, missile racks, torpedo tubes, exposed gun pods, or obvious external weapons. Weaponry must remain concealed or implied by hull seams and recessed bays.
Theme consistency: reuse the same Theme Lock block used for the skins so portraits preserve the fleet identity.
```

## Theme Consistency Rules

- Build every theme around one locked design system, not 19 independent ship prompts.
- The first lines after the class-specific subject must repeat the same Theme Lock: palette, hull material, trim material, glow color, recurring panel language, silhouette motifs, and weapon visibility rule.
- Use recurring details across all classes: matching engine glow placement, matching hull panel shapes, matching accent color locations, matching bridge/sensor language, and matching negative-space cutouts.
- Class variation should come from size, massing, wing span, number of engine clusters, and platform geometry. Do not change the underlying material language, color balance, trim style, or glow color from class to class.
- Reject or regenerate any source image that introduces a different faction identity, different palette, obvious external weapons, visible turrets, readable text, logos, or a silhouette that does not share the Theme Lock.

## Class Shape Guidance

- Escorts/frigates/destroyers: progressively larger fast warships.
- Cruisers: medium capital ships with clear faction identity.
- Heavy cruiser/battle cruiser: bulkier or more aggressive than cruiser.
- Battleship/dreadnought/superdreadnought: escalating size, armor, and reactor detail.
- Monitor: wide defensive vessel/platform, not a long cruiser.
- Fighters: small craft, increasing mass from small to heavy.
- Satellites: radial or platform-like objects, not ship-shaped.

## Scripts

- `scripts/create_manifest.py`: create directories and `theme.json`.
- `scripts/process_theme_images.py`: process named source images into game-ready skins or portraits and contact sheets.
- `scripts/validate_theme.py`: verify manifest references, image dimensions, alpha corners, and portrait coverage.

All scripts expect to run from any working directory and accept explicit paths. Prefer preserving model output originals under `Production/*_sources/`; never leave project-referenced assets only in `$CODEX_HOME/generated_images`.

`process_theme_images.py` and `validate_theme.py` require Pillow. On this Windows project, use the system Python 3.14 (`pip install -r requirements-dev.txt` installs Pillow).
