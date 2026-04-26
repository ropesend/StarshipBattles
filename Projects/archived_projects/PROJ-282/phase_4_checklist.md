# Phase 4: Extract BattleSetupRenderer (panel construction)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-282 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract the three `_build_*_panel` methods (~447 lines of panel construction) into focused per-panel renderer modules under `game/ui/screens/battle_setup/panels/` plus a top-level `BattleSetupRenderer` orchestrator.

**Prerequisite:** Phase 3 complete — ViewModel exists; panels can read view-state from it.

---

## Tasks

### Task 4.1: Create `battle_setup/panels/` package [Simple]
**Files:** `game/ui/screens/battle_setup/panels/__init__.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/` — imports still work

- [x] Created `panels/__init__.py` with package docstring
- [x] `battle_setup/__init__.py` unchanged (no re-exports needed — callers use full module paths)
- [x] `battle_setup/spec_compiler.py` untouched (Phase 1 scope decision preserved)

**Notes:** Package created at [game/ui/screens/battle_setup/panels/](../../../game/ui/screens/battle_setup/panels/). Tests for individual panel builders are structural (via `test_renderer.py`) rather than per-file — pygame_gui widget instantiation requires a running UIManager which makes isolated panel testing heavy for low marginal value. Integration coverage comes from Phase 10 manual smoke.

### Task 4.2: Extract `left_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/left_panel.py` (NEW)
**Tests:** Covered structurally in [test_renderer.py](../../../tests/unit/ui/screens/battle_setup/test_renderer.py)

- [x] Read `FleetBattleSetupScreen._build_left_panel` end-to-end (131 LOC)
- [x] Implemented as module-level `build(screen, width, height)` function that mutates `screen` with pygame_gui handles. Reads state via `screen.state`, view state via `screen.view_model` (through property shims), and complex toggles via `screen._get_toggle(...)`. Imports the `_SYSTEM_SCOPE_COMPLEXES` / `_SECTOR_SCOPE_COMPLEXES` tables from the screen module (still where they live in Phase 4 — relocation is Phase 8 cleanup).
- [x] Port of left panel build logic is verbatim — 131 LOC of panel-build code moved out of the screen.
- [x] Smoke tested via `test_panel_modules_expose_build_callable` in test_renderer.py.

**Notes:** Chose the **function-based** extraction style (module-level `build(screen, ...)` mutating screen handles) over a class-based `LeftPanelRenderer` — matches the "smallest-diff, preserve behavior" scope discipline. See [decisions.md 2026-04-18](decisions.md) "Phase 4 panel extraction style".

### Task 4.3: Extract `center_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/center_panel.py` (NEW)
**Tests:** Covered structurally in test_renderer.py

- [x] Same pattern as Task 4.2 for the center panel (fleet hierarchy tree, policies, ship list)
- [x] Port includes the 199 LOC `_build_center_panel` body AND the 62 LOC `_build_policy_controls` helper (kept as a module-private `_build_policy_controls(screen, panel, y, width, fleet)` in the same file — inseparable from center panel)

**Notes:** Largest single panel file (~260 LOC). Imports `_TARGETING_OPTIONS`, `_MOVEMENT_OPTIONS`, `_BATTLE_ROLE_OPTIONS` from the screen module. `_build_policy_controls` stays co-located per the Phase 1 delegate_map plan.

### Task 4.4: Extract `right_panel.py` [Medium]
**File:** `game/ui/screens/battle_setup/panels/right_panel.py` (NEW)
**Tests:** Covered structurally in test_renderer.py

- [x] Same pattern — smallest panel, ~35 LOC
- [x] Port of `_build_right_panel` logic
- [x] Named `right_panel.py` here; collision with `game/ui/screens/builder/right_panel.py` is a namespace-level (different package), not an import-time collision

**Notes:** Tiny — 35 LOC including docstring.

### Task 4.5: Create `BattleSetupRenderer` orchestrator [Medium]
**File:** `game/ui/screens/battle_setup/renderer.py` (NEW)
**Tests:** [test_renderer.py](../../../tests/unit/ui/screens/battle_setup/test_renderer.py) (5 tests)

- [x] `BattleSetupRenderer` class with a single `rebuild(screen)` method
- [x] Owns layout calculation (panel widths: left=250, right=280, bottom=60, center=remaining — same numbers as the current screen)
- [x] Also owns `_build_bottom_bar(screen, width, height, bar_height)` — the bottom-bar builder was small enough to inline on the renderer rather than splitting into `panels/bottom_bar.py`
- [x] 5 smoke tests: module imports, panel build callables, renderer is stateless, screen holds a renderer instance, `_rebuild_ui` delegates to `renderer.rebuild(self)`

**Notes:** Renderer is deliberately stateless (`renderer.__dict__ == {}` on a fresh instance, enforced by `test_renderer_is_stateless_between_calls`). All pygame_gui element handles still live on `screen` — Phase 8 will consolidate them on a `RendererHandles` dataclass when the screen becomes a thin shell.

### Task 4.6: Migrate screen to use BattleSetupRenderer [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/`

- [x] `__init__` now creates `self.renderer = BattleSetupRenderer()`
- [x] `_rebuild_ui` is now a single-line delegation: `self.renderer.rebuild(self)`
- [x] Deleted `_build_left_panel`, `_build_center_panel`, `_build_policy_controls`, `_build_right_panel`, `_build_bottom_bar` from the screen
- [x] Screen line count dropped from **1172 → 801** (−371 LOC). Not quite the "~450 fewer lines" plan target because module-level constants (`_SYSTEM_SCOPE_COMPLEXES` etc.) still live on the screen (imported by panel builders) — they're small and relocation is Phase 8 work.
- [x] Cleaned up now-unused imports (`UIPanel`, `UIButton`, `UILabel`, `UIDropDownMenu`, `UITextEntryLine` — the screen no longer constructs pygame_gui widgets directly)
- [x] Regression: 3470 tests pass (UI + integration UI scope)

**Notes:** Took the pragmatic route: panel builders are functions that mutate `screen` directly (`screen._side_dropdown = ...`), rather than introducing a `RendererHandles` dataclass. The invariant the Phase preserves: **panel construction code lives in per-panel modules**. The handle storage move is Phase 8 cleanup.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ui/screens/battle_setup/panels/{left,center,right}_panel.py` each exist
- [x] `game/ui/screens/battle_setup/renderer.py` orchestrates them
- [x] Screen's `_build_*_panel` methods DELETED (5 methods total: left, center, policy_controls, right, bottom_bar)
- [x] `wc -l game/ui/screens/battle_setup_screen.py` = 801 (was 1172 at Phase 1 start; −371 LOC). Less than the "~450 fewer lines" plan target because module-level option tables (`_SYSTEM_SCOPE_COMPLEXES`, `_TARGETING_OPTIONS`, etc.) still live on the screen and are imported by panel builders — relocating them to a shared module is a small Phase 8 follow-up.
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5 (extract InputHandler)
