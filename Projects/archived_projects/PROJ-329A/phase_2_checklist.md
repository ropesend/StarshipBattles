# PROJ-329A Phase 2 — Fast-win retrofits

**Status:** In Progress
**Goal:** Apply the PROJ-328 Phase A recipe to the 3 in-scope fast-win classes (reduced from 5 after pre-flight per Decision D-008).

## Pre-flight findings (Decisions D-008 + D-009)

Two original 329A targets need no retrofit; 4 transitively-found classes deferred:

| Class | Reason | Disposition |
|---|---|---|
| `MoveChoiceWindow` | No `__init__`; widget construction in sibling `MoveChoiceDialog.show()` | **No-retrofit-needed** (`docs/known-issues.md`) |
| `PlanetTargetEditor` (base) | Base class with no `__init__` | **No-retrofit-needed** (`docs/known-issues.md`) |
| AtmosphereTargetEditor | Concrete subclass, no UI tests | **Deferred** (`docs/known-issues.md`) |
| GravityTargetEditor | Concrete subclass, no UI tests | **Deferred** (`docs/known-issues.md`) |
| WaterTargetEditor | Concrete subclass, no UI tests | **Deferred** (`docs/known-issues.md`) |
| RadiationShieldEditor | Concrete subclass, no UI tests | **Deferred** (`docs/known-issues.md`) |

## Tasks

### Task 2.1: Refactor `FoodAllocationEditor` [Medium]

**Production file:** `game/ui/screens/food_allocation_editor.py` (360 LOC)
**Test file:** `tests/unit/ui/screens/test_food_allocation_editor.py`
**Test infra (NEW):** `tests/fixtures/food_allocation_editor_ui_builder.py`

The class has its own `__init__` and an existing test file using `__new__` bypass. Apply the PROJ-328 Phase A recipe verbatim:
- Cheap state + delegates BEFORE the `super().__init__()` call (or moved out via `bypass_init` early-return).
- Bypass branch invokes explicit `ui_builder` if supplied.
- Production branch invokes `DefaultFoodAllocationUiBuilder()`.

- [ ] Read `__init__` end-to-end; identify cheap state (must run in both paths) vs heavy widget construction (only post-bypass).
- [ ] Extract widget construction into a new `FoodAllocationUiBuilder` (production) at `game/ui/screens/food_allocation_ui_builder.py` per Pattern §33 + Conventions §1.6.
- [ ] Create `tests/fixtures/food_allocation_editor_ui_builder.py` with `NullFoodAllocationEditorUiBuilder` + `MockFoodAllocationEditorUiBuilder`. Use `tests/fixtures/ui_builder_protocol.py:UiBuilder` as the structural type.
- [ ] Migrate `tests/unit/ui/screens/test_food_allocation_editor.py` from `__new__` bypass to `bypass_init` + `MockFoodAllocationEditorUiBuilder`. Outcome parity: same pass count + same assertions.
- [ ] Verify pre-existing test count holds; new bypass-construction smoke tests added if needed.
- [ ] Per-class commit: `feat(329A): retrofit FoodAllocationEditor to two-stage construction`.

### Task 2.2: Refactor `FleetSelectionWindow` (TDD-first) [Medium]

**Production file:** `game/ui/screens/fleet_selection_window.py` (123 LOC)
**Test files (NEW):** `tests/unit/ui/screens/test_fleet_selection_window.py` (characterization, FIRST), `tests/fixtures/fleet_selection_window_ui_builder.py`

No tests exist. Per Decision D-004, write characterization tests against the current `__new__` bypass first; verify they pass; then refactor.

- [ ] Write characterization tests covering the 4-widget construction (label, selection_list, btn_confirm, btn_cancel), the `update()` loop's button-press dispatch, the `_label_to_fleet` lookup, and the callback invocation. Use `__new__` bypass with manual widget mocking (the legacy pattern) so they work BEFORE the refactor.
- [ ] Verify the new tests PASS.
- [ ] Apply Phase A recipe: extract widget construction into `FleetSelectionUiBuilder`; rewire `__init__` for two-stage.
- [ ] Migrate the characterization tests from `__new__` bypass to `bypass_init` + `MockFleetSelectionUiBuilder`. Verify outcome parity (same assertions pass).
- [ ] Per-class commit: `feat(329A): retrofit FleetSelectionWindow to two-stage construction (TDD-first)`.

### Task 2.3: Refactor `PlanetSelectionWindow` (TDD-first) [Medium]

**Production file:** `game/ui/screens/planet_selection_window.py` (189 LOC)
**Test files (NEW):** `tests/unit/ui/screens/test_planet_selection_window.py`, `tests/fixtures/planet_selection_window_ui_builder.py`

Same TDD-first approach as Task 2.2.

- [ ] Write characterization tests covering: minimum-rect enforcement (950×650), label/selection_list/btn_select widget construction, planet_detail_panel = None initialization, callback wiring, "Any Planet" button conditional behavior.
- [ ] Verify the new tests PASS.
- [ ] Apply Phase A recipe: extract widget construction into `PlanetSelectionUiBuilder`; rewire for two-stage.
- [ ] Migrate characterization tests to `bypass_init` + `MockPlanetSelectionUiBuilder`. Verify outcome parity.
- [ ] Per-class commit: `feat(329A): retrofit PlanetSelectionWindow to two-stage construction (TDD-first)`.

## Verification

- After each task: `pytest tests/unit/ui/screens/test_<class>.py -x -q` passes.
- After all 3 tasks: `pytest tests/unit/ui/screens/ -x -q` matches baseline + new test count.
- `python Tools/lint_test_files.py` reports 0 violations.

## Phase Completion

- [ ] All Task 2.X complete.
- [ ] Per-class commits landed (3 expected).
