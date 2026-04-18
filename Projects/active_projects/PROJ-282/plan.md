# PROJ-282: FleetBattleSetupScreen MVVM Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-282` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-282 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit responsibilities of FleetBattleSetupScreen + study TestLab MVVM exemplar | Tasks Complete, User Review Pending | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Move `_complex_toggles` onto BattleSetupState (data model integrity) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract BattleSetupViewModel | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Extract BattleSetupRenderer (panel construction) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Extract BattleSetupInputHandler | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Extract BattleSetupController (mutation + launch) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Extract FleetHierarchyEditor (kills TF/SQ clone duplication) | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Slim FleetBattleSetupScreen to a thin scene shell | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Add line-budget convention to docs/03_CONVENTIONS.md | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Manual smoke (2-side, 3-side, 8-side, complex toggles, save/load) | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 5 Complete — ready for Phase 6 (extract `BattleSetupController`)
**Last Action:** Phases 1-5 complete in a single session. Phase 1 audit, Phase 2 state toggle fields + N-team bug fix, Phase 3 ViewModel extraction, Phase 4 Renderer + 3 panel builders, Phase 5 InputHandler. Screen: 1172 → 680 LOC (−492 total across phases 4 + 5). Structure now:
- `game/ui/screens/battle_setup/view_model.py` — pure dataclass selection/view state
- `game/ui/screens/battle_setup/renderer.py` — `BattleSetupRenderer.rebuild(screen)` orchestrator + bottom bar
- `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` — per-panel `build(screen, ...)` functions
- `game/ui/screens/battle_setup/input_handler.py` — pygame_gui event dispatch (26 tests)
- `game/ui/screens/battle_setup/spec_compiler.py` — pre-existing; unchanged

Screen still owns mutations (`_add_ship_from_design`, `_duplicate_task_force`, `_start_battle`, `_save_setup`, etc.), module-level option tables (`_SYSTEM_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`), and state references. InputHandler calls `screen._*` mutation methods — Phase 6 retargets these to a Controller.

Tests this session: 40+ new tests (9 state toggles + 2 sync regression + 4 shim-routing + 9 view_model + 5 renderer + 26 input_handler). 3470+ tests green.

**Next Action:** Phase 6 — extract `BattleSetupController` into `game/ui/screens/battle_setup/controller.py`. Owns mutations on `BattleSetupState`: add_ship_from_design, remove_ship, add_task_force, duplicate_task_force, delete_task_force, add_squadron, duplicate_squadron, delete_squadron, set_fleet_battle_role, set_ship_policy, set_selected_policy, save_setup, load_setup, start_battle. Also scan_designs and lifecycle start(). Phase 6 checklist: [phase_6_checklist.md](phase_6_checklist.md).

**Blockers:** None.

**Context for Next Agent (Phase 6):**
- Phases 1-5 are done. See [manifest.md](manifest.md) for the file-level accounting.
- Phase 6 extracts **mutation methods only**. The screen currently holds them; move them onto a new `BattleSetupController` class. Handler + renderer currently call `screen._*` — they need to be retargeted to `controller.*`.
- The Controller takes `state: BattleSetupState` and `view_model: BattleSetupViewModel` in its constructor. It mutates state and reads view_model selections to know where to apply mutations.
- Several mutation methods need `scene_callback` access (for `_start_battle` / return_to_menu). Pass `scene_callback` into the Controller constructor OR let the controller return a discriminated union that the screen translates into scene_callback calls. Recommend the former — simpler.
- Tkinter file dialogs (`_save_setup` / `_load_setup`) move into Controller. Keep the `tkinter.filedialog` import lazy inside those methods (as today).
- The currently-on-screen `_sync_complex_toggles_to_state` method should probably also move to Controller since `_start_battle` calls it. Alternative: inline it into `_start_battle` on the Controller, since the spec compiler could arguably consume toggle dicts directly (that's a Phase 7+ consideration).
- `_build_end_condition` is pure and reads screen's end-condition flag attributes — move to Controller after Phase 6's Task 2 move of those flags to state (per migration_plan.md the end-condition flags belong on BattleSetupState, but the plan opted to keep them on the screen for this project's scope).
- TF/SQ CRUD includes the duplicated ship-cloning block; Phase 7 extracts `FleetHierarchyEditor` after Phase 6 has the controller shell ready. Phase 6 can temporarily leave `_duplicate_task_force` / `_duplicate_squadron` bodies as-is on the Controller; Phase 7 refactors them.
- Testing pattern (from Phase 5): mock the state + view_model, call `controller.method(...)`, assert mutations. Pygame-free.
- [migration_plan.md](../../../.agent_reports/PROJ-282-audit/migration_plan.md) Phase 6 section has the full method-to-controller mapping.

## Overview
[FleetBattleSetupScreen](../../../game/ui/screens/battle_setup_screen.py) is a 1172-line monolithic UI coordinator that mixes panel construction, event dispatch, fleet/TF/squadron mutation, complex toggles, and battle launch. Decompose using the same MVVM pattern that [TestLabScreen](../../../game/ui/screens/test_lab/screen.py) uses (ViewModel + Renderer + InputHandler + Controller). Move `_complex_toggles` onto `BattleSetupState` so it's part of the data model. Extract a `FleetHierarchyEditor` helper to kill the existing TF/SQ clone duplication. Add anti-rebloat documentation: line-budget convention in [docs/03_CONVENTIONS.md](../../../docs/03_CONVENTIONS.md) so adding new behavior naturally lands in a delegate, not back on the screen.

## Goals
- `FleetBattleSetupScreen` becomes a thin scene shell (~150 lines) — lifecycle, layout, delegate wiring only
- ViewModel holds derived view state (e.g. selected fleet, expanded TF nodes, current panel layout)
- Renderer builds the 3 panels (each in its own file under `game/ui/screens/battle_setup/`)
- InputHandler dispatches button/dropdown events
- Controller mutates `BattleSetupState` (fleet/TF/squadron CRUD, complex toggles, save/load) and triggers battle launch
- `_complex_toggles` lives on `BattleSetupState` (it's data, not UI state)
- TF/SQ clone logic lives in one place (`FleetHierarchyEditor`)
- Documented line-budget convention prevents re-bloat
- N-team support (2-8 sides per PROJ-275) preserved through the decomposition

## Scope
**In:**
- New package structure under `game/ui/screens/battle_setup/`:
  - `screen.py` — thin scene shell (replaces current `battle_setup_screen.py`)
  - `view_model.py` — `BattleSetupViewModel`
  - `renderer.py` — `BattleSetupRenderer` + per-panel renderer files
  - `input_handler.py` — `BattleSetupInputHandler`
  - `controller.py` — `BattleSetupController`
  - `fleet_hierarchy_editor.py` — `FleetHierarchyEditor` (TF/SQ CRUD)
  - `panels/` subpackage with one file per panel (left/center/right)
- Move `_complex_toggles` onto `BattleSetupState` (or a `ComplexToggleSet` if it grows complex)
- Add `docs/03_CONVENTIONS.md` section: "UI screen line budget" (target: ≤300 lines for screens)
- Update [game/ui/screens/__init__.py](../../../game/ui/screens/__init__.py) to re-export from new location with the same `BattleSetupScreen` alias
- Migrate existing tests; add new tests for each extracted class
- Manual smoke checklist: 2-side / 3-side / 8-side / complex toggles / save+load

**Out:**
- Any change to `BattleSetupState`'s public API beyond the `_complex_toggles` move (no fleet/ship model changes)
- Any change to the [spec_compiler](../../../game/ui/screens/battle_setup/spec_compiler.py) (it's already well-structured)
- Any new gameplay features (no new toggles, no new fleet operations)
- Any change to `Game.start_battle` or `BattleController` integration points

## Key Files
| Component | File Path |
|-----------|-----------|
| Current god class | `game/ui/screens/battle_setup_screen.py` (1172 lines) |
| Current state model | `game/ui/screens/battle_setup_state.py` |
| Current spec compiler (UNCHANGED) | `game/ui/screens/battle_setup/spec_compiler.py` |
| MVVM exemplar to follow | `game/ui/screens/test_lab/screen.py` + sibling files |
| New screen shell | `game/ui/screens/battle_setup/screen.py` (NEW) |
| New view model | `game/ui/screens/battle_setup/view_model.py` (NEW) |
| New renderer | `game/ui/screens/battle_setup/renderer.py` (NEW) |
| New input handler | `game/ui/screens/battle_setup/input_handler.py` (NEW) |
| New controller | `game/ui/screens/battle_setup/controller.py` (NEW) |
| New hierarchy editor | `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` (NEW) |
| Panels subpackage | `game/ui/screens/battle_setup/panels/` (NEW) |
| Doc convention update | `docs/03_CONVENTIONS.md` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Approach: Full MVVM matching TestLab pattern | User chose "Full MVVM". Codebase consistency: TestLab already uses ViewModel+Renderer+InputHandler+Controller. Easier for future contributors who learn one pattern across the UI |
| 2026-04-17 | Move `_complex_toggles` onto BattleSetupState | It's part of the battle setup data, not UI presentation state. Its current placement on the screen is a code smell |
| 2026-04-17 | Extract `FleetHierarchyEditor` as a separate helper | TF/SQ clone duplication is a structural issue independent of the MVVM split. Solving it in the same project reinforces the anti-rebloat principle |
| 2026-04-17 | Anti-rebloat: line-budget convention in docs | Without documented limits, future contributors will pile UI logic back into the screen. Convention gives reviewers grounds to push back |
| 2026-04-17 | Sequencing: LAST in the 5-project arc | Largest project; benefits from momentum and learnings from earlier wins. Also: lets BattleScreen cleanup (PROJ-281) close before opening another UI front |
| 2026-04-17 | Preserve N-team support (PROJ-275) — 2 to 8 sides | Decomposition is structural; behavior must be unchanged |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Manual smoke: 2-side battle setup launches and runs to completion
- [ ] Manual smoke: 3-side and 8-side battle setups launch and run
- [ ] Manual smoke: system + sector complex toggles work
- [ ] Manual smoke: save and load preserve all state including complex toggles
- [ ] `wc -l game/ui/screens/battle_setup/screen.py` ≤ 300
- [ ] No file in `game/ui/screens/battle_setup/` exceeds the documented line budget
- [ ] User verified
