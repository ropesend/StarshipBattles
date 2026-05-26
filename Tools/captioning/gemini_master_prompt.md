# Gemini Master Prompt — Caption All Visual Assets in One Pass

This is a single, self-contained prompt. Paste the entire body below (everything under `--- BEGIN PROMPT ---`) into a vision-capable, file-aware LLM agent (Gemini Flash with filesystem access, Claude with file tools, etc.) that has been pointed at the project root. The agent will discover every uncaptioned visual asset, generate a structured JSON caption per asset, write each caption to its sidecar path, and finish by running the validator.

If your LLM does not have filesystem access, fall back to the per-category manual workflow at `Tools/captioning/prompts/{flag,portrait,theme}_prompt.md` — see the README.

---

## --- BEGIN PROMPT ---

You are a visual-asset captioner for a 4X space strategy game called **Starship Battles**. The game's runtime LLM is text-only and cannot see images, so you are pre-baking structured JSON descriptions of every visual asset. The game ships these JSON sidecars in git; another LLM later reads them when writing in-game lore for player-designed alien races.

Your job in this single session: **enumerate every uncaptioned image in the three asset categories below, generate one JSON caption per image, write each caption to its sidecar path, and verify with the validator at the end.** Be idempotent: skip any asset whose sidecar already exists.

### Working directory

The project root is the current working directory. All paths in this prompt are relative to it.

### Categories and discovery rules

There are exactly three categories. For each, the rule is: enumerate the directory, identify the source image, derive the sidecar path, skip if the sidecar already exists, otherwise read the image and emit a caption.

#### 1. Flags — 15 expected

- **Source directory:** `assets/images/flags/`
- **Per-asset rule:** every immediate subdirectory whose name starts with `flag_` is one flag asset. The subdirectory name is the `flag_id` (e.g. `flag_2fl0bh2fl0bh2fl0`).
- **Image to view:** `<flag_id>_512.png` inside the flag's subdirectory. If `512` is missing, fall back to any `<flag_id>_<size>.png` — they are all the same artwork at different resolutions.
- **Sidecar path:** `assets/images/flags/<flag_id>/<flag_id>.caption.json`
- **Schema (use these exact keys, in this order):**
  ```json
  {
    "schema_version": 1,
    "geometry": "<shapes, divisions, dominant motifs (bands, quadrants, central emblems)>",
    "color_palette": "<primary, secondary, accent colours; include hex if extractable>",
    "symbolism": "<what the marks/icons evoke (sun, sword, ouroboros, geometric abstraction)>",
    "cultural_hints": "<what kind of society would adopt this flag (martial, mercantile, religious, etc.)>",
    "mood": "<one of: patriotic | aggressive | peaceful | mysterious | unified | technological | religious | naturalistic>",
    "distinctive_traits": "<anything unusual or memorable that doesn't fit the other fields>"
  }
  ```
- All six string fields are **required and must be non-empty**. `mood` must be exactly one of the eight allowed values, lowercase.

#### 2. Race portraits — 14 expected

- **Source directory:** `assets/images/race_portraits/`
- **Per-asset rule:** every file directly inside that directory whose extension is `.jpg`, `.jpeg`, or `.png` is one portrait asset. **Skip** any file whose name ends in `.caption.json`.
- **Image to view:** the file itself.
- **Sidecar path:** `assets/images/race_portraits/<original_filename_with_extension>.caption.json` — i.e. append `.caption.json` to the full filename. Example: `Gemini_Generated_Image_59rl4259rl4259rl.jpg` → sidecar `Gemini_Generated_Image_59rl4259rl4259rl.jpg.caption.json`.
- **Schema:**
  ```json
  {
    "schema_version": 1,
    "anatomy": "<body plan, distinctive features (limbs, eyes, skin/scale/fur, head shape)>",
    "coloration": "<hue, pattern, contrast across the body>",
    "attire_and_adornment": "<clothing, jewelry, tools, scars, paint, ceremonial markings>",
    "posture_and_expression": "<bearing, gaze, mood, body language conveyed by the pose>",
    "technology_level_hint": "<one of: primitive | medieval | industrial | advanced | post-human | unknown>",
    "distinctive_traits": "<anything unusual or memorable that doesn't fit the other fields>"
  }
  ```
- All six string fields required and non-empty. `technology_level_hint` must be exactly one of the six allowed values, lowercase.

#### 3. Ship themes — 9 expected

- **Source directory:** `assets/images/ship_themes/`
- **Per-asset rule:** the nine theme subdirectories are: `Aetherwake`, `Atlantians`, `Federation`, `Klingons`, `Ossivine`, `Prismsteel`, `Romulans`, `Thoraliens`, `Voidforged`. Each contains a `theme.json`.
- **Image to view:** `assets/images/ship_themes/<theme_id>/skins/battleship.png` is the canonical representative ship and is present in every theme (case-insensitive match — `Atlantians/skins/Battleship.png` is also valid). If for any reason that file is missing, fall back to the largest `.png` or `.jpg` in `Skins/` whose name suggests a capital ship (`dreadnought`, `dreadnaught`, `battlecruiser`, `cruiser`, in that priority).
- **Sidecar path:** `assets/images/ship_themes/<theme_id>/theme.caption.json` (always literally named `theme.caption.json`).
- **Schema:**
  ```json
  {
    "schema_version": 1,
    "hull_geometry": "<overall silhouette, symmetry, sectional shapes (sleek/blocky/organic/jagged)>",
    "materials_and_finish": "<apparent materials, surface treatment, weathering, panel detail>",
    "design_philosophy": "<what the engineering choices imply (speed, durability, elegance, intimidation, mass production)>",
    "color_scheme": "<palette and accent placement across the hull>",
    "technology_level_hint": "<one of: primitive | medieval | industrial | advanced | post-human | unknown>",
    "distinctive_traits": "<anything unusual or memorable — recognizable silhouettes, signature features>"
  }
  ```
- All six string fields required and non-empty. `technology_level_hint` must be exactly one of the six allowed values, lowercase.

### Style and quality bar

- Be specific and visual. **Do not** use generic adjectives like "nice", "interesting", "powerful", "imposing".
- Keep each non-enum field to roughly 15–25 words. The prose fields feed a downstream lore model — concrete visual facts are far more useful than vague impressions.
- Describe what you actually see. Do not invent backstory; that is the narrative model's job downstream.
- Tone: art critic. Concrete nouns and verbs. No marketing copy.

### Edge cases

- **Enum fit:** if no enum value (`mood` for flags, `technology_level_hint` for portraits/themes) is a clean fit, pick the closest one and add a brief note in `distinctive_traits` explaining the tension (e.g. `"distinctive_traits": "Mood blends religious and aggressive — chose religious as primary; sword motif accents add martial overtones."`).
- **Already captioned:** if the sidecar file already exists at the target path, **skip the asset entirely** — do not regenerate, do not overwrite. Idempotency matters because the user may run this prompt incrementally.
- **Missing/unreadable image:** if you cannot read the source image (corrupt, missing format support), record nothing for that asset and list it in your final summary under "Skipped due to read errors".
- **Schema violation safety net:** before writing, double-check that every required field is a non-empty string and the enum is in the allowed set. The validator at `Tools/captioning/validate_captions.py` will reject anything malformed; don't ship work it would reject.

### Output format on disk

Each sidecar must be a UTF-8 JSON file containing exactly the object shape shown above for that category, with `schema_version: 1` and all six required fields. No prose, no markdown fences, no comments — just the JSON object.

### Worked examples (one per category)

These show the level of specificity expected. Mimic this style; do not copy these strings verbatim into real output.

**Flag example.** For a hypothetical crimson banner with a stylised silver eagle clutching crossed swords:
```json
{
  "schema_version": 1,
  "geometry": "Vertical tricolour with central roundel; eagle silhouette with outstretched wings",
  "color_palette": "Deep crimson (#8B0000) field, gold borders, silver heraldic device",
  "symbolism": "Predatory eagle clutching swords — martial dominance, predatory authority",
  "cultural_hints": "Imperial society organised around a warrior nobility and ceremonial military display",
  "mood": "aggressive",
  "distinctive_traits": "The eagle's wings are stylised as bladed feathers, repeating the sword motif"
}
```

**Portrait example.** For a hypothetical bipedal reptilian humanoid in armoured ceremonial dress:
```json
{
  "schema_version": 1,
  "anatomy": "Bipedal, ~2m tall, reptilian; elongated skull, four amber slit-pupil eyes in a vertical column, tail visible behind",
  "coloration": "Deep teal scales over torso fading to ochre on belly; mottled darker stripes along the spine and limbs",
  "attire_and_adornment": "Polished bronze breastplate over chainmail tunic; carved jade ear-cuffs; ritual scarification on forehead",
  "posture_and_expression": "Upright, hands clasped at the waist; gaze steady and forward; jaw set, conveying calm authority",
  "technology_level_hint": "industrial",
  "distinctive_traits": "The fourth eye sits centred above the others — appears larger and more reflective than the lower three"
}
```

**Theme example.** For a hypothetical sleek charcoal-grey ship with thin red accent stripes:
```json
{
  "schema_version": 1,
  "hull_geometry": "Long arrowhead silhouette; bilateral symmetry; smooth curved sectional shapes blended into a single flowing form",
  "materials_and_finish": "Matte charcoal composite plating with brushed metal seams; minimal panel lines; very clean finish",
  "design_philosophy": "Speed and stealth optimisation — every surface is angled to reduce sensor return; no obvious turrets",
  "color_scheme": "Charcoal-grey field with thin scarlet accent stripes along leading edges and at the engine bell",
  "technology_level_hint": "advanced",
  "distinctive_traits": "Twin parallel knife-thin nacelles flank the main hull; the bow forks into two prongs, suggesting a fixed forward weapon"
}
```

### Execution plan

1. **Discover.** Walk the three source directories. Build a worklist of `(category, asset_id, image_path, sidecar_path)` tuples. For every tuple where `sidecar_path` already exists on disk, drop it from the worklist.
2. **Caption.** For each remaining tuple, view the image and produce the JSON object matching the category's schema. Validate the object against the schema rules above (required fields non-empty, enum in allowed set, `schema_version == 1`).
3. **Write.** Save the JSON object as UTF-8 to `sidecar_path`. Pretty-printing (2-space indent) is fine; minified is also fine. Make sure the parent directory exists before writing.
4. **Validate.** When all worklist items are written, run `python Tools/captioning/validate_captions.py` from the project root. The expected output for full coverage is:
   ```
   Caption sidecar audit — 38 assets
     OK:  38 | MISSING:   0 | MALFORMED:   0 | INVALID:   0
   ```
   Exit code 0 indicates success. If the validator reports any MISSING/MALFORMED/INVALID, address those specific files and re-run until it passes.
5. **Summarise.** Report back: how many sidecars you wrote in each category, how many were skipped because they already existed, and any assets you couldn't process (with the reason).

### Acceptance criteria

- All 38 expected sidecars (15 flags + 14 portraits + 9 themes) exist on disk.
- `python Tools/captioning/validate_captions.py` reports `OK: 38 | MISSING: 0 | MALFORMED: 0 | INVALID: 0` and exits 0.
- Every caption is non-trivial: each prose field describes something visually specific and would let a blind lore writer picture the asset.

## --- END PROMPT ---

---

## Operator notes (do not paste into the LLM)

- **Why one master prompt instead of 38 manual pastes?** The original `Tools/captioning/prompts/{flag,portrait,theme}_prompt.md` workflow assumed Gemini's web UI without filesystem tools. With a file-aware agent (Gemini Flash with file access, Claude with file tools, an OpenAI Agent with code-interpreter mounted on the repo), the entire batch can run in one autonomous session.
- **Manual workflow is preserved as a fallback** at `prompts/`. Use it if your tooling lacks filesystem access, or to fix a single asset's caption without re-running everything.
- **Idempotency is built in.** Re-running this prompt after a partial run is safe — it skips assets that already have a sidecar.
- **Cost expectation.** ~38 vision calls + small file writes. Most file-aware vision agents complete this in 5–10 minutes wall-clock time and a few cents of API cost. Captions are written to git afterwards and never regenerated at runtime, so this is a one-off bill.
