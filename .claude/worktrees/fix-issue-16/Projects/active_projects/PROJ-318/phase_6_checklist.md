# Phase 6: R4 — Migrate codex-ship-theme-creator skill to new schema

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate the two remaining sibling files in
`.agents/skills/codex-ship-theme-creator/scripts/` to the new
`assets:` schema. PROJ-314 updated `theme_common.py` but missed
`create_manifest.py` and `validate_theme.py`. Future themes
scaffolded by the skill must produce theme.json files compatible
with the new loader.

---

## Tasks

### Task 6.1: Read the canonical schema reference [Simple]
**File:** None (read-only research).
**Tests:** None.

- [x] Read `assets/ShipThemes/Federation/theme.json` to see the canonical post-migration shape
- [x] Read `.agents/skills/codex-ship-theme-creator/scripts/theme_common.py` (already migrated by PROJ-314 commit `0bbf9c36d`) for its `load_manifest()` and class structure
- [x] Read `Projects/active_projects/PROJ-314/decisions.md` for the locked schema decisions (display-form keys, 2048×2048 PNG, schema_version 1, optional portrait)

**Notes:**

### Task 6.2: Migrate `create_manifest.py` to write new `assets:` schema [Medium]
**File:** `.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py`
**Tests:** Manual run + smoke test in Task 6.5.

- [x] Identify the function that writes `theme.json` (currently writes `images: {class: "Skins/path"}`)
- [x] Rewrite to emit:
  ```json
  {
    "schema_version": 1,
    "name": "<theme_name>",
    "description": "<optional>",
    "image_sizes": {
      "skin": [2048, 2048],
      "portrait": [2048, 2048]
    },
    "assets": {
      "<DisplayFormKey>": {
        "skin": "Skins/<lowercase_underscored>.png",
        "portrait": "Portraits/<lowercase_underscored>.png"
      },
      ...
    }
  }
  ```
- [x] Use display-form keys (e.g. `"Battleship"`, `"Fighter (Medium)"`) — pull from `game.core.ship_classes::SHIP_CLASSES_WITH_VISUAL_THEMES`. Add a project-root bootstrap if necessary (mirror Phase 4 pattern).
- [x] If a portrait file isn't being scaffolded (e.g. user only generated skins), omit the `portrait` key (schema allows it)
- [x] Filename basenames in lowercase_with_underscores.png

**Notes:**

### Task 6.3: Migrate `validate_theme.py` to expect new `assets:` schema [Medium]
**File:** `.agents/skills/codex-ship-theme-creator/scripts/validate_theme.py`
**Tests:** Manual run on each existing theme.

- [x] Replace `manifest.get("images", {})` with `manifest.get("assets", {})`
- [x] Validate keys against `SHIP_CLASSES_WITH_VISUAL_THEMES` (import from `game.core.ship_classes`); flag extras and missing
- [x] Validate skin path exists and is PNG (not JPG)
- [x] Validate portrait path (when declared) exists and is PNG
- [x] Validate image dimensions are 2048×2048 (use PIL `Image.open(path).size`)
- [x] Print human-readable summary: per-theme schema-version, key count, skin coverage, portrait coverage, dimension conformance
- [x] Exit non-zero on any validation failure

**Notes:**

### Task 6.4: Add project-root bootstrap to both scripts [Simple]
**File:** Both files in 6.2 and 6.3.
**Tests:** Manual.

- [x] Add the standard project-root finder + sys.path insertion (mirror Phase 4 pattern) BEFORE any `from game.X import` lines
- [x] Verify both scripts can be invoked from any working directory:
  - `python .agents/skills/codex-ship-theme-creator/scripts/validate_theme.py <theme_name>`
  - `python -m .agents.skills.codex-ship-theme-creator.scripts.validate_theme <theme_name>` (if module form is supported)

**Notes:**

### Task 6.5: End-to-end smoke: scaffold + validate a fake theme [Medium]
**File:** None (manual smoke).
**Tests:** Manual end-to-end.

- [x] Use the codex-ship-theme-creator skill scripts to scaffold a fake theme (e.g. "TestTheme") with synthetic 2048×2048 PNG placeholders
- [x] Inspect the generated `theme.json` — confirm it matches the schema shape (use Federation's as the gold standard)
- [x] Run `validate_theme.py TestTheme` — confirm it passes
- [x] Run `python -c "from game.ui.assets.ship_theme_manager import ShipThemeManager; m = ShipThemeManager(); m.initialize(); print('TestTheme' in m.theme_data)"` — confirm the theme is discoverable
- [x] Delete the fake theme directory
- [x] If any step fails: iterate on Tasks 6.2 / 6.3

**Notes:**

### Task 6.6: Run existing theme validations [Simple]
**File:** None.
**Tests:** Manual.

- [x] Run `validate_theme.py` on each of the 9 existing themes (Aetherwake, Atlantians, Federation, Klingons, Ossivine, Prismsteel, Romulans, Thoraliens, Voidforged)
- [x] Record the result: Aetherwake passes schema validation; the other 8 themes fail on known portrait dimension debt surfaced by Phase 5
- [x] Do not broaden this phase into asset regeneration; the audit gate and smoke tests already track those asset gaps

**Notes:**

### Task 6.7: Run full test suite [Simple]
**File:** None.
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Confirm 15959 + delta passing, 0 failing
- [x] No regressions

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `create_manifest.py` produces theme.json files in the new schema
- [x] `validate_theme.py` accepts the new schema, rejects the old
- [x] Existing-theme validation sweep completed and known portrait-size failures recorded
- [x] End-to-end fake-theme scaffold + discovery succeeds
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `All 6 phases complete; project ready for archive.`
- [x] Commit: `feat(PROJ-318 Phase 6): migrate codex-ship-theme-creator skill to assets: schema`
- [x] Run `python Projects/scripts/validate_audit_ready.py PROJ-318` — expect exit 0
