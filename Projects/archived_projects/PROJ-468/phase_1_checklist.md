# Phase 1: Critical content-accuracy errors

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-468 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Correct the 7 verified CRITICAL content-accuracy errors in systems/guides docs against current code — deleted `component_inspector.py` and `effect_ability_metadata.py` references — identified by audit `2026-05-20_073330_docs-audit`. Both files are confirmed absent; replacements are `component_abilities.py` + `component_layers.py` and `ability_metadata.py`.

---

## Tasks

### Task 1.1: 04_SERVICES.md component_inspector shim claim [Medium]
**File:** `docs/04_SERVICES.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Remove the directory-map entry (line 58) listing `component_inspector.py` as a "thin re-export shim"
- [x] Rewrite lines 480-482: drop the false claim that `component_inspector.py` "is preserved as a thin re-export shim"; state the shim was removed (PROJ-454) and `component_abilities.py` + `component_layers.py` are the only import paths
- [x] Verify: `grep -n "component_inspector" docs/04_SERVICES.md` returns nothing presenting it as a live/importable path
- [x] Verify: code claim now matches repo (`component_inspector.py` absent; `component_abilities.py` + `component_layers.py` present)


**Notes:** docs/04_SERVICES.md: removed shim entry (line 58) + rewrote shim claim (removed PROJ-454); also fixed in-scope effect_ability_metadata refs to ability_metadata.py. Stamp bumped.

### Task 1.2: ability_reference.md component_inspector + effect_ability_metadata [Medium]
**File:** `docs/systems/ability_reference.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Replace `component_inspector.py` (lines 19, 489) with `component_abilities.py` / `component_layers.py`; verify the functions listed at lines 493-502 (`get_component_abilities`, `extract_abilities_from_component`, `iterate_design_components`, etc.) resolve in the replacement modules
- [x] Replace `effect_ability_metadata.py` (lines 18, 184) with `ability_metadata.py` (the `AbilityMetadataRegistry`)
- [x] Verify: `grep -n "component_inspector\|effect_ability_metadata" docs/systems/ability_reference.md` returns nothing as a live path


**Notes:** docs/systems/ability_reference.md: lines 18/19/184/318/489 updated to component_abilities/component_layers + ability_metadata. Functions verified present in component_abilities.py.

### Task 1.3: strategy_layer.md effect_ability_metadata "remains importable" claim [Simple]
**File:** `docs/systems/strategy_layer.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Rewrite line 692: remove the false claim that `effect_ability_metadata.py` "remains importable"; point consumers to `ability_metadata.py`
- [x] Verify: code claim now matches repo (`effect_ability_metadata.py` absent; `ability_metadata.py` present)


**Notes:** docs/systems/strategy_layer.md line 692: removed false "remains importable" shim claim; points to ability_metadata.py.

### Task 1.4: adding_abilities.md component_inspector + effect_ability_metadata [Medium]
**File:** `docs/guides/adding_abilities.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Replace `component_inspector.py` (line 55) with `component_abilities.py` / `component_layers.py`; fix example `import` snippets so they no longer import from the dead module
- [x] Rewrite line 422 + remove File Map entry (line 495): `effect_ability_metadata.py` is fully removed, not "now a shim"; reference `ability_metadata.py`
- [x] Verify: `grep -n "component_inspector\|effect_ability_metadata" docs/guides/adding_abilities.md` returns nothing as a live path


**Notes:** docs/guides/adding_abilities.md: lines 55/422/424/495 fixed; EffectAbilityMetadata->EffectFacet of AbilityMetadata.

### Task 1.5: component_system.md component_inspector [Medium]
**File:** `docs/guides/component_system.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Replace `component_inspector.py` (lines 23, 130-133) with `component_abilities.py` / `component_layers.py`; correct the "Both are re-exported by the legacy `component_inspector` import path" claim (no such shim exists)
- [x] Verify: example `import` snippets resolve against current modules


**Notes:** docs/guides/component_system.md: lines 23/130-133/152(import)/316 fixed; corrected false re-export claim.

### Task 1.6: qs_complex_design.md component_inspector [Simple]
**File:** `docs/guides/qs_complex_design.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Replace `component_inspector.py` (line 32, Source Files table) with `component_abilities.py` / `component_layers.py`
- [x] Verify: `grep -n "component_inspector" docs/guides/qs_complex_design.md` returns nothing as a live path


**Notes:** docs/guides/qs_complex_design.md: line 32 + line 338 component_inspector refs fixed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
