# Phase 1: Controller boundary fixes (T5.1 .. T5.4)

**Status:** Not Started
**Objective:** Restore controller-boundary discipline. Controllers do not touch pygame_gui widgets; Stage 1 of two-stage `__init__` is cheap-pure; dead methods are removed; test seams in production code are removed.

---

## Tasks

### Task 1.1: T5.1 — slider-read relocation [Medium]
**File:** `game/ui/screens/cargo_quick_dialog.py:300-306`, `cargo_quick_dialog_controller.py:69-79`
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog* -x`

- [ ] Read the controller's `issue_orders` (lines 69-79) — confirms `item['slider'].get_current_value()` calls.
- [ ] In `cargo_quick_dialog.py._issue_orders`, build a resolved values dict: `{cargo_key: int(slider.get_current_value()) for cargo_key, slider in ...}`.
- [ ] Update `controller.issue_orders` signature to take `Dict[str, int]` (or similar resolved type) instead of `cargo_items` (which contains widget refs).
- [ ] Update controller body to use the resolved dict directly.
- [ ] Add a characterization test: construct controller; pass it a resolved values dict; assert it never accesses any attribute named `slider`.
- [ ] Run.
- [ ] Commit: `fix(cargo-quick-dialog): move slider reads into dialog so controller stays widget-pure (PROJ-348 T5.1)`

**Notes:**

### Task 1.2: T5.2 — Stage 1 facade audit [Medium]
**File:** `game/ui/screens/cargo_quick_dialog.py:__init__`

- [ ] Read `__init__` to find every `self.scene.facade.*` access.
- [ ] Identify which accesses happen BEFORE the bypass guard (these violate Stage-1 purity).
- [ ] Move violating accesses into Stage 2 (after bypass guard).
- [ ] Add Stage-1 purity test: construct via `bypass_init`; assert NO `scene.facade.*` access.
- [ ] Commit: `fix(cargo-quick-dialog): keep Stage 1 facade-free under bypass (PROJ-348 T5.2)`

**Notes:**

### Task 1.3: T5.3 — `PlanetListController.navigate_to()` decision [Medium]
**File:** `game/ui/screens/planet_list_controller.py`, `planet_list_window.py`

- [ ] `git grep -n "navigate_to\|on_navigate_callback" game/` — list every caller.
- [ ] If `navigate_to` is truly dead (no production callers): delete the method. Commit: `refactor(planet-list-controller): remove dead navigate_to method (PROJ-348 T5.3)`.
- [ ] If the window SHOULD call `navigate_to` instead of `self.on_navigate_callback(loc)`: rewire. Commit: `refactor(planet-list-window): route navigation through controller.navigate_to (PROJ-348 T5.3)`.
- [ ] Document decision in [decisions.md](decisions.md).

**Notes:**

### Task 1.4: T5.4 — remove `__new__` test seam [Medium]
**File:** `game/ui/screens/planet_list_window.py:687-701`, `tests/unit/ui/screens/test_planet_list_window.py:38-50`

- [ ] Read `_resolve_demographic_view` lines 687-701 — confirm the `controller is None` fallback exists specifically to support `__new__`-bypass tests.
- [ ] In tests at lines 38-50: replace `PlanetListWindow.__new__(PlanetListWindow)` construction with `bypass_init` path (per `tests/fixtures/ui_widget_factory.py`).
- [ ] Remove the `controller is None` fallback in `_resolve_demographic_view`.
- [ ] Run tests; confirm still pass against the bypass path.
- [ ] Commit: `refactor(planet-list-window): remove __new__ test seam from _resolve_demographic_view (PROJ-348 T5.4)`

**Notes:**

### Task 1.5: Verification + index update
- [ ] `pytest tests/unit/ui/screens/ -x -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-348 → `Awaiting Verification`. Commit: `chore(PROJ-348): mark Sprint 6 awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked
- [ ] 4 fix commits + 1 chore commit landed
- [ ] plan.md phase row → `Complete`; Current State final
- [ ] Surface to user
