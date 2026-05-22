# Phase 1: Re-inventory tooling imports against post-474/475/477 live code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-476 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Confirm PROJ-474/475/477 have landed, then derive the EXACT
post-gate tooling-exemption residue set from live code (the 2026-05-22 snapshot
in plan.md is provisional). Produce the authoritative triple list Phase 2 will
encode. No code/guard edits in this phase.

---

## Tasks

### Task 1.1: Confirm the gate is cleared [Simple]
**Files:** `Projects/active_projects/PROJ-474/plan.md`, `PROJ-475/plan.md`, `PROJ-477/plan.md`
**Tests:** n/a (verification only)

- [x] Confirm PROJ-474 is COMPLETE: `_UISAFE_SYMBOLS` exists in
      `tests/static_guards/test_facade_read_path_imports_guard.py` and the pure
      symbols (`RaceConfig`, `RacePointBudget`, `FieldStatus`, `PlanetType`,
      `BattleRole`, `CombatPolicy`, `VALID_GALAXY_TYPES`, `StrategicKind`,
      `abilities_with_kind_tag`, `SUPERWEAPONS`) are no longer in the tooling
      files' `TAIL` lines.
- [x] Confirm PROJ-475 + PROJ-477 are COMPLETE (live `.session` readers + render
      pass-throughs migrated; their guard allowlist entries removed).
- [x] If any of 474/475/477 is NOT complete: STOP. PROJ-476 is gated; do not
      proceed.
- [x] Verify: gate-clearance state recorded in Notes below.

### Task 1.2: Re-grep for session reads in the tooling dirs [Simple]
**Files:** `game/ui/screens/{battle_setup,galaxy_test,race_setup,builder}/`, `battle_setup_state.py`, `design_selector_window.py`, `workshop_event_router.py`
**Tests:** grep (no test change)

- [x] Grep `\.session\b|\._session\b|facade_state\.session` across all in-scope
      tooling files. EXPECT zero matches (confirmed 2026-05-22).
- [x] If any match appears (a regression introduced by 475/477 or new code):
      STOP and reclassify — that file may belong to PROJ-475/477, not 476.
- [x] Verify: confirm PROJ-476 remains import-guard-only.

### Task 1.3: Re-inventory the tooling `game.strategy.*` imports [Medium]
**Files:** in-scope tooling files (see plan.md "Key Files")
**Tests:** grep / AST (no test change)

- [x] Grep `from game.strategy|import game.strategy` across each tooling file;
      list every runtime (non-`TYPE_CHECKING`) `(file, module, member)` import.
- [x] For each, classify: UISAFE (already moved by 474 → DROP from 476) |
      tooling-exemption (KEEP) | live-defer (should already be gone via 475/477;
      if present, flag).
- [x] Cross-check the residual `TAIL` block of the import guard: every remaining
      tooling-file triple must be a genuine tooling exemption.
- [x] Re-confirm the screens-root boundary: `battle_setup_state.py` IN;
      `design_selector_window.py` + `workshop_event_router.py` IN
      (`design-editor`); `build_queue_panel_factory.py` OUT.
- [x] Verify: produce the authoritative `_TOOLING_EXEMPTIONS` triple set (with
      tag + reason per entry) in Notes — this is Phase 2's input.

**Notes (execution 2026-05-22):**

**Gate state — CLEARED.** PROJ-474 (commit `11439ea71`), PROJ-475
(`83ba24ea1`, `e2af24373`), PROJ-477 (`95a07ea83`) all committed and present
in the live guard. `_UISAFE_SYMBOLS` exists (guard lines 90-135); the pure
symbols (`PlanetType`, `BattleRole`, `CombatPolicy`, `VALID_GALAXY_TYPES`,
`RaceConfig`, `RacePointBudget`, `FieldStatus`, `StrategicKind`,
`abilities_with_kind_tag`, `SUPERWEAPONS`) are all in `_UISAFE_SYMBOLS` and
absent from any tooling triple in `_IMPORT_ALLOWLIST`.

**Session-read grep — ZERO matches** across `battle_setup/`, `galaxy_test/`,
`race_setup/`, `builder/`, and the three screens-root files
(`battle_setup_state.py`, `design_selector_window.py`,
`workshop_event_router.py`). PROJ-476 remains import-guard-only.

**Re-inventory vs 2026-05-22 snapshot — NO DRIFT.** All 30 tooling triples in
the snapshot are present and live in the guard's `TAIL` block; every one
verified against current source line numbers. Pure symbols at the same call
sites (`fleet_hierarchy_editor.py:17` CombatPolicy, `constants.py` BattleRole/
PlanetType, `galaxy_mode.py:20` VALID_GALAXY_TYPES, `race_config` RaceConfig,
`controller.py:129/311/342` RacePointBudget, `llm_dialog_service.py:63/105`
FieldStatus) are UISAFE-allowed and correctly NOT in the tooling set.
`race_setup/screen.py:28` RaceRandomizer test-seam (noqa F401) is STILL present
→ KEEP its triple. `llm_dialog_service.py:21` is `TYPE_CHECKING` (ignored);
its runtime FieldStatus imports are UISAFE → no new triple.

**Authoritative `_TOOLING_EXEMPTIONS` triple set (30) for Phase 2:**

`prebattle-editor` (5):
- battle_setup/fleet_hierarchy_editor.py · game.strategy.data.ship_instance · ShipInstance
- battle_setup/fleet_hierarchy_editor.py · game.strategy.data.squadron · Squadron
- battle_setup/fleet_hierarchy_editor.py · game.strategy.data.task_force · TaskForce
- battle_setup_state.py · game.strategy.data.fleet · Fleet
- battle_setup_state.py · game.strategy.data.ship_instance · ShipInstance

`sandbox-harness` (15):
- galaxy_test/galaxy_mode.py · game.strategy.data.galaxy · Galaxy
- galaxy_test/galaxy_mode.py · game.strategy.generation.density.density_map · DensityMap
- galaxy_test/galaxy_mode.py · game.strategy.generation.loaders.galaxy_layouts_loader · GalaxyLayoutsLoader
- galaxy_test/galaxy_mode.py · game.strategy.generation.placement_strategies · DensityBasedPlacementStrategy
- galaxy_test/galaxy_mode.py · game.strategy.generation.placement_strategies · RandomPlacementStrategy
- galaxy_test/system_mode.py · game.strategy.data.planet · Planet
- galaxy_test/system_mode.py · game.strategy.data.planet_gen · PlanetGenerator
- galaxy_test/system_mode.py · game.strategy.data.planet_physics · MASS_EARTH
- galaxy_test/system_mode.py · game.strategy.data.planet_physics · calculate_escape_velocity
- galaxy_test/system_mode.py · game.strategy.data.planet_physics · calculate_surface_gravity
- galaxy_test/system_mode.py · game.strategy.data.star_system · StarSystem
- galaxy_test/system_mode.py · game.strategy.data.stars · Star
- galaxy_test/system_mode.py · game.strategy.data.stars · StarGenerator
- galaxy_test/system_mode.py · game.strategy.generation.loaders.system_blueprints_loader · SystemBlueprintsLoader
- galaxy_test/system_mode.py · game.strategy.generation.planet_image_registry · PlanetImageRegistry

`race-authoring` (6):
- race_setup/controller.py · game.strategy.systems.race_library · RaceLibrary
- race_setup/controller.py · game.strategy.systems.race_randomizer · RaceRandomizer
- race_setup/panel_factory.py · game.strategy.data.race_caption_loader · RaceCaptionLoader
- race_setup/panel_factory.py · game.strategy.services.race_description_llm_controller · RaceDescriptionLLMController
- race_setup/screen.py · game.strategy.systems.race_library · RaceLibrary
- race_setup/screen.py · game.strategy.systems.race_randomizer · RaceRandomizer

`design-editor` (4):
- builder/right_panel.py · game.strategy.data.design_role_registry · get_default_design_role_registry
- design_selector_window.py · game.strategy.data.design_role_registry · get_default_design_role_registry
- design_selector_window.py · game.strategy.systems.design_catalog · DesignCatalog
- workshop_event_router.py · game.strategy.data.design_role_registry · get_default_design_role_registry

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] The authoritative post-gate triple set is recorded in Notes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
