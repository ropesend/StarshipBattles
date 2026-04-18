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
| 6. Extract BattleSetupController (mutation + launch) | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Extract FleetHierarchyEditor (kills TF/SQ clone duplication) | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. Slim FleetBattleSetupScreen to a thin scene shell | Complete | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Add line-budget convention to docs/03_CONVENTIONS.md | Complete | [phase_9_checklist.md](phase_9_checklist.md) |
| 10. Manual smoke (2-side, 3-side, 8-side, complex toggles, save/load) | Not Started | [phase_10_checklist.md](phase_10_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 9 Complete — ready for Phase 10 (manual smoke; user-gated)
**Last Action:** Phases 1-9 complete in a single session — **all PROJ-282 code + docs work is DONE.** Only Phase 10 (user-led manual smoke) remains; that's not something I can do. Structure now:
- `game/ui/screens/battle_setup/view_model.py` — pure dataclass selection/view state
- `game/ui/screens/battle_setup/renderer.py` — `BattleSetupRenderer.rebuild(screen)` orchestrator + bottom bar
- `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` — per-panel `build(screen, ...)` functions
- `game/ui/screens/battle_setup/screen.py` — **184 LOC** thin shell: IScene + delegate wiring + property shims
- `game/ui/screens/battle_setup/view_model.py` — pure dataclass (60 LOC, no pygame)
- `game/ui/screens/battle_setup/renderer.py` — orchestrator (85 LOC)
- `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` — per-panel builders
- `game/ui/screens/battle_setup/input_handler.py` — pygame_gui dispatch (178 LOC, 30 tests)
- `game/ui/screens/battle_setup/controller.py` — ALL state mutations (523 LOC, 31 tests, pygame-free except for tkinter filedialog)
- `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` — stateless TF/SQ CRUD + ship cloning (191 LOC, 11 tests)
- `game/ui/screens/battle_setup/constants.py` — shared option tables (54 LOC)
- `game/ui/screens/battle_setup/spec_compiler.py` — pre-existing, unchanged
- `game/ui/screens/battle_setup/__init__.py` — package docstring + `FleetBattleSetupScreen` re-export
- `docs/03_CONVENTIONS.md § 2.4 UI Screen Line Budget (PROJ-282)` — documented convention

**Old `game/ui/screens/battle_setup_screen.py` DELETED.** Old screen's monolith went from **1172 LOC** → decomposed across 10 package files totaling ~1765 LOC (overhead = per-module docstrings + imports ≈ 150 LOC). The TF/SQ ship-cloning duplication is GONE — `FleetHierarchyEditor._clone_ship` lives in exactly one place. The latent Phase 3 bug (end-condition settings inside `@available_designs.setter`, resetting on every design scan) is FIXED as a side effect of moving those fields to the controller.

Tests this session: **79+ new tests** across state (9 toggles + 2 sync + 4 shim-routing), view_model (9), renderer (5), input_handler (30 — 26 original + 4 added in Phase 6), controller (31), fleet_hierarchy_editor (11). 2 duplicate state-level sync tests deleted after Phase 6 moved the method to the controller. **3545 tests green** in PROJ-282 scope (tests/unit/ui/ + tests/integration/ui/). Full repo regression has 4 pre-existing failures/errors outside PROJ-282 scope (test_ai_protocols ImportError, test_quickstart_builder theme assertion) — verified not caused by this project.

**Next Action:** Phase 10 — **user-led manual smoke** [phase_10_checklist.md](phase_10_checklist.md). I cannot click through the UI; the user needs to:
  1. Launch the game → Battle Setup, verify panels render
  2. Fleet/TF/SQ CRUD (create, duplicate, delete)
  3. 3-side setup compile + launch (if the "Add Side" UI exists — see Blocker below)
  4. 8-side max-cap behavior
  5. Complex toggles + spec modifier flow
  6. Save/load roundtrip
  7. Edge cases (empty side launch guard, large setup, rapid interactions)

**Blockers:** Phase 10 tasks 10.3 + 10.4 assume "Add Side" / "Remove Side" UI buttons exist. **They don't** — the current left panel only has a hardcoded 2-entry side dropdown. The Phase 1 audit flagged this in [n_team_paths.md](../../../.agent_reports/PROJ-282-audit/n_team_paths.md) as UI work that PROJ-282 *should* add, but the per-phase checklists never scheduled it as a concrete task. State + spec-compiler N-team support is solid (tested in `test_battle_setup_three_sides.py`); the UI surface to drive it into N>2 battles is the gap. User should decide: (a) accept current 2-side UI + rely on `BattleSetupState.add_side()` at state level (e.g. via save-file editing), (b) file a follow-up project for N-team UI (Add/Remove Side buttons in `panels/left_panel.py` + `Controller.add_side/remove_side` methods), or (c) block Phase 10 until the UI ships.

**Context for Next Agent / User Verification:**
- All production code + docs work is DONE. No code-level follow-ups known other than the N-team UI surface.
- See [manifest.md](manifest.md) for the file-level accounting of every change this session.
- Phase 6 property shims on the screen (`tick_limit`, `end_all_destroyed`, etc. routing to controller; `active_side`, `selected_tf_index`, etc. routing to view_model; `_get_toggle` routing to controller) are legitimate thin-shell wiring. Dropping them requires updating ~10 read sites in `panels/left_panel.py` + `panels/center_panel.py` to go through `screen.controller.*` / `screen.view_model.*` directly. Small, safe follow-up — not a blocker.
- `controller.py` at 523 LOC exceeds the newly-added ≤300 convention; the convention explicitly treats this as a review signal, not a blocker. If the user wants to split it: save/load + battle-launch into a `LaunchController` sub-service is the natural cut (~100 LOC saved).

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
