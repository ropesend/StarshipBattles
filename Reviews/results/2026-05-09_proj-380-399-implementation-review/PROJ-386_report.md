# PROJ-386 Implementation Review

**Project:** PROJ-386 - Legacy removal: Save-format migration eradication  
**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **Not audit-clean.** The four explicitly planned deletions were implemented, but the project did not actually eradicate save-format compatibility from the touched surfaces. At least two remaining old-save tolerance paths exist in the same production files, and the checklist overstates verification evidence.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-386`:

- **PASSED**
- Warning: `Projects/projects_index.md` still lists PROJ-386 as `Planning`.

`python Projects/scripts/validate_phase.py PROJ-386 1`:

- **PASSED**
- 5 warnings: Tasks 1.1 through 1.5 are complete but have empty Notes.

## Tests Run

- `python -B -m pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py tests/integration/save_load/test_roundtrip_ships.py tests/integration/resource_system/test_resource_pipeline.py tests/unit/ui/screens/test_battle_setup_state.py tests/unit/ui/screens/battle_setup/test_controller.py tests/integration/ui/test_battle_setup_three_sides.py tests/unit/strategy/engine/test_component_activation_engine.py tests/unit/strategy/data/test_planet_active_abilities.py -q -p no:cacheprovider`
  - **119 passed**
- Cheap behavioral probes:
  - `ShipInstanceSerializer.from_dict()` loads a dict containing both `components` and legacy `component_damage`; the legacy key is ignored.
  - `ShipInstanceSerializer.from_dict()` raises raw `KeyError: 'components'` when `components` is missing.
  - `ShipInstanceSerializer.from_dict()` still loads old `resource_levels` into `consumable_levels`.

## Plan Goals vs Actual Implementation

| Goal | Result | Evidence |
|---|---|---|
| Delete `_complex_toggles` load migration in `battle_setup/controller.py` | Met | `_load_from_path()` now only loads JSON and delegates to `BattleSetupState.from_dict()`; no top-level `_complex_toggles` migration remains (`game/ui/screens/battle_setup/controller.py:536-552`). |
| Delete `{'active': bool}` old activation-state branch | Met | `ComponentActivationState.from_dict()` now requires `data['phase']` directly (`game/strategy/data/component_activation_state.py:135-144`). |
| Delete `component_damage` explicit ignore + missing-`components` graceful degrade | Partially met | The explicit branch is gone and missing `components` now fails at `data['components']` (`game/strategy/data/ship_instance_serializer.py:124-130`), but the legacy key is still not rejected when mixed into otherwise new-format data. |
| Delete `side_0`/`side_1` legacy emit + read from battle setup save format | Met for top-level save format | `BattleSetupState.to_dict()` emits only `sides`, and `from_dict()` reads only `data["sides"]` (`game/ui/screens/battle_setup_state.py:256-277`). |

## Literal Checklist Execution

- Phase 1 checkboxes are all marked complete, and validator agrees the phase metadata is complete.
- The implementation did not leave the four named legacy blocks in place.
- The final checklist claim that `grep -rn -E "(_complex_toggles|side_0|side_1|component_damage)" game/` shows no remaining legacy-format handling is too broad to be true literally. `side_0`/`side_1` compatibility properties remain in production (`game/ui/screens/battle_setup_state.py:141-181`), and `component_damage` remains as accepted extra input when `components` is present.
- The checklist's Task 1.3 verification says deserialization raises if missing/legacy, but the current tests only assert new saves do not emit `component_damage`; they do not assert that legacy input containing `component_damage` is rejected (`tests/unit/strategy/ship_instance/test_ship_instance_serializer.py:66-69`).

## Plan Gaps / Missed Assumptions

- The plan treated the source audit's four items as exhaustive for save-format migration in the touched files. They were not exhaustive.
- The plan did not account for `BattleSetupSide.from_dict()` still explicitly tolerating pre-PROJ-282 save payloads that lack `system_complex_toggles` and `sector_complex_toggles`.
- The plan did not account for `ShipInstanceSerializer.from_dict()` still accepting the old `resource_levels` field as a fallback for `consumable_levels`.
- The plan did not require negative tests for legacy input rejection, so several "raises if legacy" claims remain unpinned by tests.

## Findings

### Major: Save-format compatibility remains in touched files

`game/ui/screens/battle_setup_state.py:117-130` explicitly says `BattleSetupSide.from_dict()` tolerates legacy saves lacking `*_complex_toggles` fields and defaults them to `{}`. The corresponding test preserves that behavior at `tests/unit/ui/screens/test_battle_setup_state.py:223-235`, including a docstring that says "Legacy saves ... Don't crash." This is the same class of old-save compatibility PROJ-386 was supposed to eradicate under the no-migration rule.

`game/strategy/data/ship_instance_serializer.py:106` also still accepts `resource_levels` as a fallback for missing `consumable_levels`. That is a field-rename shim for old save data in one of the project's key files. The implementation removed the four named audit findings, but the plan missed these adjacent compatibility paths.

### Minor: Task 1.3 verification is weaker than claimed

The checklist says `ShipInstanceSerializer.from_dict()` should raise if the input is missing/legacy (`Projects/active_projects/PROJ-386/phase_1_checklist.md:33-35`). In practice, missing `components` raises a raw `KeyError`, not the documented `PersistenceException`, because `components` is not included in `require_keys()` and is accessed later via `data['components']` (`game/strategy/data/ship_instance_serializer.py:87,126`). A payload with both `components` and legacy `component_damage` loads successfully because unknown keys are ignored. This is not the original graceful-degrade behavior, but it means the literal checklist verification is not covered or fully true.

### Minor: Project index still reports Planning

Audit-readiness passed, but it warned that the index status is stale. `Projects/projects_index.md:20` lists PROJ-386 as `Planning` even though `plan.md` marks the project complete and awaiting user verification (`Projects/active_projects/PROJ-386/plan.md:20-23`).

## Residual Risks

- Focused tests pass, but there is no dedicated negative coverage proving old save shapes are rejected for the remaining compatibility paths above.
- I did not run the full sharded suite during this review. The project checklist claims a prior full sharded/focused regression pass, and I ran a focused 119-test subset covering the affected areas.
- The broader codebase likely has additional old-save tolerance patterns because PROJ-386 was seeded from a non-exhaustive audit path; this review only confirmed surviving issues in the PROJ-386 touched files.
