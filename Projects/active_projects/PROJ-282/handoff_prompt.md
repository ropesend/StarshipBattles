# Handoff: PROJ-282 — Phase 6 (extract `BattleSetupController`)

Resume **PROJ-282** at **Phase 6**. The previous session ended at ~27%
context after completing Phases 1–5 (audit + state toggles + ViewModel +
Renderer + InputHandler). Phase 6 is the densest remaining phase —
~15 mutation methods and ~400 LOC to move off the screen AND retarget
the InputHandler's call sites in lockstep. Start fresh so you have full
context budget for the coordinated refactor.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. The plan assumes
you understand the MVVM pattern already wired through Phases 3–5. If you
read the plan cold, you'll make decisions that contradict choices the
previous session locked in. Load extra context first — it's cheap.

### 1. Foundation docs (always)

- `docs/README.md` — doc index
- `docs/01_ARCHITECTURE.md` — layer structure (UI is top layer; Controller should not import pygame unless it needs tkinter for file dialogs)
- `docs/02_PATTERNS.md` — MVVM pattern, ApplicationContext DI, Facade
- `docs/03_CONVENTIONS.md` — line budgets, naming, test conventions
- `CLAUDE.md` at the project root — Rule 1 TDD, Rule 3 clean-sheet design, System Migration Policy ("saves are disposable")

### 2. Task-specific docs

- `docs/systems/combat_simulation.md` §"Battle Orchestration" and §"Spec Compiler" — the `build_manual_battle_spec` function is called by `_start_battle` and is out-of-scope for PROJ-282 (stays unchanged; Controller wraps the call)

### 3. Related code — READ IN FULL

**Project-owned extractions from Phases 2–5 (read the public contracts):**
- `game/ui/screens/battle_setup_state.py` — 288 LOC — `BattleSetupState` + `BattleSetupSide`. Phase 2 added `system_complex_toggles` + `sector_complex_toggles` dicts.
- `game/ui/screens/battle_setup/view_model.py` — `BattleSetupViewModel` dataclass; 6 selection attrs + 3 helpers; no pygame imports.
- `game/ui/screens/battle_setup/renderer.py` — `BattleSetupRenderer.rebuild(screen)` orchestrator.
- `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` — `build(screen, ...)` functions that mutate `screen.*` handles.
- `game/ui/screens/battle_setup/input_handler.py` — `BattleSetupInputHandler.handle_event(event)`. **IMPORTANT: this currently calls `self._screen._add_ship_from_design(...)`, `self._screen._duplicate_task_force(...)`, etc. Phase 6 retargets these to `controller.*` calls.**
- `game/ui/screens/battle_setup_screen.py` — 680 LOC — still owns the ~15 mutation methods Phase 6 extracts.

**Pre-existing (unchanged in PROJ-282):**
- `game/ui/screens/battle_setup/spec_compiler.py` — `build_manual_battle_spec(state, registries, ...)`. Controller's `start_battle` calls this.
- `game/app.py:37` imports `FleetBattleSetupScreen as BattleSetupScreen`. **Do not rename the class until Phase 8.**

**Exemplar (read for Controller shape reference):**
- `combat_lab/services/test_lab_controller.py` — an *external-package* controller style. PROJ-282's Controller lives inside the `battle_setup` package (co-located, not a separate service).

### 4. Related tests

- `tests/unit/ui/screens/test_battle_setup_state.py` — 28 tests; includes `TestSyncComplexTogglesToStateIsNTeamSafe` (2 tests that exercise the screen's `_sync_complex_toggles_to_state`; if you move that method to Controller, update these tests' call path).
- `tests/unit/ui/screens/battle_setup/test_view_model.py` — 9 tests.
- `tests/unit/ui/screens/battle_setup/test_renderer.py` — 5 tests (structural).
- `tests/unit/ui/screens/battle_setup/test_input_handler.py` — 26 tests. **IMPORTANT: these tests mock `screen` as a MagicMock and assert `screen._add_ship_from_design.assert_called_once_with(7)` etc. After Phase 6 retargets the handler to call `controller.*`, these tests need updating — the assertions become `controller.add_ship_from_design.assert_called_once_with(7)` on a mocked controller.**
- `tests/integration/ui/test_battle_setup_three_sides.py` — 4 integration tests hitting `BattleSetupState → build_manual_battle_spec`. Don't touch; Controller's start_battle should not break these.

## Only now: read the project files

1. `Projects/active_projects/PROJ-282/design.md` — architecture rationale
2. `Projects/active_projects/PROJ-282/decisions.md` — 10 decisions logged from the previous session, including the 3 pragmatic shortcuts (data-on-state via supplement, property shims on screen, InputHandler takes `screen`). Phase 6 gets to revisit the last one.
3. `Projects/active_projects/PROJ-282/plan.md` § Current State — authoritative status
4. `Projects/active_projects/PROJ-282/phase_6_checklist.md` — task list for Phase 6
5. `Projects/active_projects/PROJ-282/manifest.md` — every file touched this project
6. `.agent_reports/PROJ-282-audit/` — 6 Phase 1 reports:
   - `delegate_map.md` — method → target delegate
   - `migration_plan.md` — the authoritative plan document; **re-read Phase 6 section before writing code**
   - `testlab_pattern.md` — MVVM conventions
   - `test_coverage.md`, `save_load.md`, `n_team_paths.md`

## First action

From `phase_6_checklist.md` — start with Task 6.1:

> Write tests for `BattleSetupController` in
> `tests/unit/ui/screens/battle_setup/test_controller.py`. Test each
> mutation method (add_fleet, remove_fleet, add_ship_from_design,
> add_task_force, duplicate_task_force, delete_task_force, add_squadron,
> duplicate_squadron, delete_squadron, set_fleet_battle_role,
> set_ship_policy, set_selected_policy, save_setup, load_setup,
> start_battle). Mock state + view_model; call the method; assert state
> mutations. Strict TDD — all tests fail before implementation.

## Watchouts (from the previous session)

- **The InputHandler still calls `self._screen.*` for mutations.** When you move a method to the Controller (e.g. `_add_ship_from_design` → `controller.add_ship_from_design`), you must simultaneously update `input_handler.py` to call `self._controller.add_ship_from_design(...)`. You also need to update `test_input_handler.py`'s 26 tests — they mock the screen and assert on `screen._add_ship_from_design.assert_called_once_with(7)`. Rewrite to a mocked controller.
- **Recommended Controller constructor:** `BattleSetupController(state, view_model, scene_callback=None)`. Scene callback is used by `_start_battle` ("start_battle" / "start_headless") and `_return_to_menu`. Pass it in; keep the controller pygame-free.
- **`_save_setup` / `_load_setup` use tkinter.filedialog.** Keep the import lazy inside those methods. It's fine for the Controller to touch tkinter — it's already screen-side today.
- **`_start_battle` does a "both sides have ships" guard check → `_sync_complex_toggles_to_state` → `_build_end_condition` → `build_manual_battle_spec` → `scene_callback(action, spec=...)`.** All of this moves to `Controller.start_battle(headless: bool)`. The sync + build_end_condition helpers also migrate as private controller methods.
- **`_sync_complex_toggles_to_state` is currently tested by `TestSyncComplexTogglesToStateIsNTeamSafe` in `test_battle_setup_state.py`** with the bypass-init pattern. After moving to Controller, the test either (a) follows — updates to construct `BattleSetupController` directly (no bypass-init needed, controller is lightweight), or (b) tests the Controller instead. Option (a) is cleaner.
- **`_get_active_fleet`** is read by several mutation methods. Move it to Controller too.
- **`_scan_designs` + `start(preserve_teams)` lifecycle** — these move to Controller. Screen's `start(preserve_teams)` becomes `self.controller.start(preserve_teams)`. The Controller populates `view_model.available_designs`.
- **`_sync_complex_toggles_to_state` iterates `for side in state.sides`** (fixed the N-team bug in Phase 2). Do NOT reintroduce a 2-side hardcoding when porting.
- **Module-level constant tables** (`_SYSTEM_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`, `_MOVEMENT_OPTIONS`, `_BATTLE_ROLE_OPTIONS`) live on the screen module. Panel builders + now Controller + now InputHandler (for `_ship_targeting_dropdown` dispatch) all import from there. Relocating to `battle_setup/constants.py` is Phase 8 cleanup — don't move them in Phase 6 unless a Controller-side import becomes ugly.
- **Property shims from Phase 3** (`self.active_side` → `self.view_model.active_side`) still route to view_model. Controller should read `self._view_model.active_side` directly (no shim layer).
- **Screen should end Phase 6 at ~300 LOC** per [migration_plan.md](../../../.agent_reports/PROJ-282-audit/migration_plan.md). Target delete: ~380 LOC of mutation methods.
- **Regression baseline:** 3470+ tests pass at end of Phase 5. After Phase 6, same count (or +8-15 new Controller tests).

## Protocol

Follow `Projects/protocols/03a_continue_working.md`. Check context at
natural handoff points via `python Tools/check_context/check_context.py`.
Phase 6 is large — consider pausing at the halfway point (after ~8
methods moved) if context starts climbing, and handing off before
input_handler retargeting gets interrupted. Remember: splitting Phase 6
into "methods moved" + "handler retargeted" halves across two sessions
is safer than stopping mid-retargeting.
