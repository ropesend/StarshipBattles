# PROJ-282 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated as implementation discovers additional files.

## Files touched or planned

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `.agent_reports/PROJ-282-audit/delegate_map.md` | Audit (Phase 1) | 1 | NEW — method → delegate mapping + line budgets |
| `.agent_reports/PROJ-282-audit/testlab_pattern.md` | Audit (Phase 1) | 1 | NEW — TestLab MVVM conventions to adopt |
| `.agent_reports/PROJ-282-audit/test_coverage.md` | Audit (Phase 1) | 1 | NEW — existing test coverage analysis |
| `.agent_reports/PROJ-282-audit/save_load.md` | Audit (Phase 1) | 1 | NEW — current save/load shape + migration plan |
| `.agent_reports/PROJ-282-audit/n_team_paths.md` | Audit (Phase 1) | 1 | NEW — N-team support gap analysis |
| `.agent_reports/PROJ-282-audit/migration_plan.md` | Audit (Phase 1) | 1 | NEW — synthesized plan + escalations |
| `Projects/active_projects/PROJ-282/phase_1_checklist.md` | Project doc | 1 | Updated — all tasks checked, status Complete |
| `Projects/active_projects/PROJ-282/plan.md` | Project doc | 1 | Updated — Quick Status + Current State |
| `Projects/active_projects/PROJ-282/manifest.md` | Project doc | 1 | This file |
| `Projects/active_projects/PROJ-282/decisions.md` | Project doc | 2 | Added 3 Phase-2 decisions (toggle shape supplement, save/load legacy compat, N-team bug fix) |
| `Projects/active_projects/PROJ-282/phase_2_checklist.md` | Project doc | 2 | All Phase 2 tasks checked; status Complete |
| `game/ui/screens/battle_setup_state.py` | Production | 2 | Added `system_complex_toggles` + `sector_complex_toggles` dicts on `BattleSetupSide`; updated `to_dict`/`from_dict`. Spec-compiler interface (`*_complexes: List[Dict]`) unchanged |
| `game/ui/screens/battle_setup_screen.py` | Production | 2 | Removed screen-level `_complex_toggles` dict; added `_get_toggle`/`_set_toggle`/`_toggle_dict_for` accessors on state; rewrote `_sync_complex_toggles_to_state` to iterate all `state.sides` (fixes N-team bug); updated `_save_setup`/`_load_setup` to persist via state + migrate legacy `_complex_toggles` key |
| `tests/unit/ui/screens/test_battle_setup_state.py` | Test | 2, 3 | Added `TestBattleSetupSideComplexToggles` (7 cases) + `TestSyncComplexTogglesToStateIsNTeamSafe` (2 cases) in Phase 2; added `TestScreenDelegatesViewStateToViewModel` (4 cases) in Phase 3. 22 tests total |
| `game/ui/screens/battle_setup/view_model.py` | Production (NEW) | 3 | `BattleSetupViewModel` dataclass — pure data, no pygame. 6 attrs + 3 helpers |
| `tests/unit/ui/screens/battle_setup/test_view_model.py` | Test (NEW) | 3 | 9 tests: defaults, mutation, helpers, pygame-import absence |
| `Projects/active_projects/PROJ-282/phase_3_checklist.md` | Project doc | 3 | All Phase 3 tasks checked; status Complete |
| `game/ui/screens/battle_setup_screen.py` | Production | 3, 4 | Phase 3: `self.view_model` + property shims. Phase 4: `self.renderer` + delegation in `_rebuild_ui`; deleted `_build_{left,center,right}_panel` + `_build_policy_controls` + `_build_bottom_bar` (−371 LOC, 1172 → 801) |
| `Projects/active_projects/PROJ-282/phase_4_checklist.md` | Project doc | 4 | All Phase 4 tasks checked; status Complete |
| `game/ui/screens/battle_setup/panels/__init__.py` | Production (NEW) | 4 | Panels subpackage marker + docstring |
| `game/ui/screens/battle_setup/panels/left_panel.py` | Production (NEW) | 4 | `build(screen, width, height)` — lifted from `_build_left_panel` (~131 LOC) |
| `game/ui/screens/battle_setup/panels/center_panel.py` | Production (NEW) | 4 | `build(screen, x, width, height)` + `_build_policy_controls(screen, panel, y, width, fleet)` — lifted from `_build_center_panel` + `_build_policy_controls` (~260 LOC — largest) |
| `game/ui/screens/battle_setup/panels/right_panel.py` | Production (NEW) | 4 | `build(screen, x, width, height)` — lifted from `_build_right_panel` (~35 LOC — smallest) |
| `game/ui/screens/battle_setup/renderer.py` | Production (NEW) | 4 | `BattleSetupRenderer.rebuild(screen)` orchestrator + `_build_bottom_bar(screen, ...)` helper |
| `tests/unit/ui/screens/battle_setup/test_renderer.py` | Test (NEW) | 4 | 5 structural tests: renderer imports, panel build callables, renderer is stateless, screen holds renderer, `_rebuild_ui` delegates |
| `Projects/active_projects/PROJ-282/phase_5_checklist.md` | Project doc | 5 | All Phase 5 tasks checked; status Complete |
| `game/ui/screens/battle_setup/input_handler.py` | Production (NEW) | 5 | `BattleSetupInputHandler.handle_event(event)` — pygame_gui dispatch. Tag-based button dispatch + named-button dispatch + dropdown dispatch. ~175 LOC |
| `tests/unit/ui/screens/battle_setup/test_input_handler.py` | Test (NEW) | 5 | 26 tests covering every event family (fleet/ship/design/TF/SQ/complex/named-button/dropdown/unknown-noop) |
| `game/ui/screens/battle_setup_screen.py` (cont.) | Production | 5 | Added `self.input_handler`; `handle_event` trimmed to 3 lines; deleted `_handle_button` (105 LOC) + `_handle_dropdown` (17 LOC) + `import pygame_gui`. Screen 801 → 680 LOC |
| `Projects/active_projects/PROJ-282/phase_6_checklist.md` | Project doc | 6 | All Phase 6 tasks checked; status Complete |
| `game/ui/screens/battle_setup/controller.py` | Production (NEW) | 6 | `BattleSetupController` — 458 LOC. Owns all state mutations, complex toggles, end-condition settings, save/load, battle launch, lifecycle. Pygame-free. |
| `tests/unit/ui/screens/battle_setup/test_controller.py` | Test (NEW) | 6 | 31 tests covering defaults, lifecycle, CRUD, toggles, end-condition, save/load migration, start_battle guard + callback |
| `game/ui/screens/battle_setup/input_handler.py` (cont.) | Production | 6 | Retargeted from `screen._*` to `screen.controller.*` for every mutation dispatch. Added `_push_tick_limit_to_controller()` helper. Selection-only view_model writes unchanged. |
| `tests/unit/ui/screens/battle_setup/test_input_handler.py` (cont.) | Test | 6 | Mock `screen.controller = MagicMock()`; assertions retargeted from `screen._*` to `screen.controller.*`. Added 4 new tests for add_fleet, remove_fleet, add_tf, add_sq, end_derelict, end_mass. 26 → 30 tests. |
| `game/ui/screens/battle_setup_screen.py` (cont.) | Production | 6 | Instantiated `self.controller`; added 5 property shims (end-condition fields) + `_get_toggle` shim; deleted 15 mutation methods; `start()` is a one-line delegate; deleted `import os`. **Fixed latent Phase 3 bug** (end-condition fields inside `@available_designs.setter`). Screen 680 → 287 LOC. |
| `tests/unit/ui/screens/test_battle_setup_state.py` (cont.) | Test | 6 | Deleted `TestSyncComplexTogglesToStateIsNTeamSafe` (2 tests) — duplicated by `test_controller.py::TestSyncComplexTogglesIsNTeamSafe` with real controller. |
| `Projects/active_projects/PROJ-282/phase_7_checklist.md` | Project doc | 7 | All Phase 7 tasks checked; status Complete |
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | Production (NEW) | 7 | `FleetHierarchyEditor` — stateless static-method helper for Fleet/TF/SQ CRUD + `_clone_ship`. ~180 LOC. Kills the Phase 6 inline clone duplication. |
| `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` | Test (NEW) | 7 | 11 tests: create_tf/sq, duplicate_tf/sq (policy + battle_role + spatial_behavior preservation), delete_tf/sq, clone_ship, stateless |
| `game/ui/screens/battle_setup/controller.py` (cont.) | Production | 7 | TF/SQ mutation methods became one-line delegations to `FleetHierarchyEditor.*`. Deleted inline clone logic + `_clone_ship` staticmethod + unused `TaskForce`/`Squadron`/`CombatPolicy` imports. |
| `Projects/active_projects/PROJ-282/phase_8_checklist.md` | Project doc | 8 | All Phase 8 tasks checked; status Complete |
| `game/ui/screens/battle_setup/screen.py` | Production (NEW) | 8 | **Terminal PROJ-282 home for the screen.** `FleetBattleSetupScreen` thin shell — 184 LOC (IScene + delegate wiring + property shims). |
| `game/ui/screens/battle_setup/constants.py` | Production (NEW) | 8 | 5 module-level option tables relocated from the old `battle_setup_screen.py`: `_SYSTEM_SCOPE_COMPLEXES`, `_SECTOR_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`, `_MOVEMENT_OPTIONS`, `_BATTLE_ROLE_OPTIONS`. 54 LOC. |
| `game/ui/screens/battle_setup/__init__.py` | Production | 8 | Added full package-structure docstring; re-exports `FleetBattleSetupScreen`. |
| `game/ui/screens/battle_setup_screen.py` | Production (DELETED) | 8 | **Old screen file DELETED.** All functionality migrated to the `battle_setup/` package. |
| `game/app.py` | Production | 8 | Import updated: `from game.ui.screens.battle_setup.screen import FleetBattleSetupScreen as BattleSetupScreen`. |
| `game/ui/screens/battle_setup/panels/{left,center}_panel.py` | Production | 8 | Imports updated from `battle_setup_screen` → `battle_setup.constants`. |
| `game/ui/screens/battle_setup/input_handler.py` (cont.) | Production | 8 | Imports updated from `battle_setup_screen` → `battle_setup.constants`. |
| `game/ui/screens/battle_setup/controller.py` (cont.) | Production | 8 | Imports updated from `battle_setup_screen` → `battle_setup.constants`. |
| `tests/unit/ui/screens/battle_setup/test_controller.py` (cont.) | Test | 8 | Imports updated from `battle_setup_screen` → `battle_setup.constants`. |
| `tests/unit/ui/screens/battle_setup/test_renderer.py` (cont.) | Test | 8 | Imports updated from `battle_setup_screen` → `battle_setup.screen`. |
| `tests/unit/ui/screens/test_battle_setup_state.py` (cont.) | Test | 8 | Imports updated from `battle_setup_screen` → `battle_setup.screen`. |
| `Projects/active_projects/PROJ-282/phase_9_checklist.md` | Project doc | 9 | All Phase 9 tasks checked; status Complete |
| `docs/03_CONVENTIONS.md` | Doc | 9 | **Added § 2.4 UI Screen Line Budget (PROJ-282)** — documents the ≤300 LOC target as a review signal, not a blocker. Names `TestLabScreen` + `FleetBattleSetupScreen` as exemplars. |
| `game/ui/screens/battle_setup/screen.py` (cont.) | Production | 9 | Added module-docstring paragraph cross-referencing the convention + naming TestLabScreen as sibling exemplar. Dropped unused `import pygame`. |
| `game/ui/screens/test_lab/screen.py` | Production | 9 | Added the symmetric module-docstring paragraph naming FleetBattleSetupScreen as sibling exemplar. |
| `Projects/active_projects/PROJ-282/phase_11_checklist.md` | Project doc (NEW) | 11 | N-Side UI phase added post-hoc + completed; status Complete |
| `game/ui/screens/battle_setup/controller.py` (cont.) | Production | 11 | `add_side()` + `remove_side(index)` methods with MIN/MAX bounds handling + view-model reconciliation (clamp on active-side removal, index-shift on before-active removal) + selection clearing |
| `game/ui/screens/battle_setup/panels/left_panel.py` (cont.) | Production | 11 | Side dropdown populates dynamically from `len(state.sides)` (drops hardcoded 2 entries + "(Left)"/"(Right)" suffixes). Added `_add_side_btn` + `_remove_side_btn` with MIN/MAX auto-disable + informative labels. Also fixed stale `battle_setup_screen` → `battle_setup.constants` import miss from Phase 8. |
| `game/ui/screens/battle_setup/input_handler.py` (cont.) | Production | 11 | Added 2 named-button branches (`_add_side_btn` → `controller.add_side()`, `_remove_side_btn` → `controller.remove_side(view_model.active_side)`). Updated side-dropdown parser to handle `"Side N"` format with malformed-text fallback. |
| `tests/unit/ui/screens/battle_setup/test_controller.py` (cont.) | Test | 11 | New `TestAddRemoveSide` class (11 tests) + `TestNTeamBattleLaunch` class (1 N-team integration launch test). |
| `tests/unit/ui/screens/battle_setup/test_input_handler.py` (cont.) | Test | 11 | Added 4 new tests (add_side button, remove_side button, N>2 dropdown parse, malformed-dropdown fallback). Updated 2 existing side-dropdown tests to the new `"Side N"` format. Added 2 new button sentinels to `_make_handler_with_mock_screen()`. |

## Planned for Phases 3-8

See [migration_plan.md](../../../.agent_reports/PROJ-282-audit/migration_plan.md) §"Per-phase deliverables + file targets" for the detailed file plan. Summary:

- **Phase 3:** NEW `game/ui/screens/battle_setup/view_model.py` + `tests/unit/ui/screens/battle_setup/test_view_model.py`
- **Phase 4:** NEW `game/ui/screens/battle_setup/renderer.py` + `panels/{__init__.py,left_panel.py,center_panel.py,right_panel.py}` + tests
- **Phase 5:** NEW `game/ui/screens/battle_setup/input_handler.py` + `tests/.../test_input_handler.py`
- **Phase 6:** NEW `game/ui/screens/battle_setup/controller.py` + `tests/.../test_controller.py`
- **Phase 7:** NEW `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` + `tests/.../test_fleet_hierarchy_editor.py`
- **Phase 8:** NEW `game/ui/screens/battle_setup/screen.py` + `__init__.py` re-export; DELETE `game/ui/screens/battle_setup_screen.py`; update `game/app.py` import; NEW `tests/.../test_screen.py`
- **Phase 9:** `docs/03_CONVENTIONS.md` — add UI line budget section
- **Phase 10:** No file changes (manual smoke)
