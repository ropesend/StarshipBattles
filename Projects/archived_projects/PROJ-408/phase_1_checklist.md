# Phase 1: Add direct unit coverage for C-01, C-02, C-04

**Status:** Complete
**Objective:** Land 3 new direct unit tests covering the introspection/UI-only gaps in PROJ-381 and PROJ-397.

---

## Tasks

### Task 1.1: C-01 — Replace introspection-only `EmpireBuildQueueWindow` test [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`

- [x] Read PROJ-397's existing F-05 test that verifies the constructor signature only via introspection.
- [x] Read `game/ui/screens/empire_build_queue_window.py` to see the actual class — what dependencies does the constructor take, and what should a real instance be able to do?
- [x] Write a new test (or augment the existing one) that:
  - Constructs `EmpireBuildQueueWindow` with realistic dependencies (use existing fixtures if any — check the module for facade/registry patterns).
  - Exercises at least one method that proves the threading is correct (e.g., a method that uses `self._facade.handle_command(...)`).
- [x] If the introspection-only test was a `test_constructor_signature_*` pattern, **delete it** after the real-construction test lands — it's bug-shaped (asserts shape, not behavior).
- [x] Run focused tests — pass.

**Notes:**
- The pre-PROJ-408 test was `test_constructor_requires_facade` (introspected `inspect.signature(EmpireBuildQueueWindow.__init__)`). Replaced with `test_add_item_to_source_routes_command_through_facade` which constructs the window via the suite's `_make_window` helper and exercises `_add_item_to_source` — the production path PROJ-393 Task 2.5 narrowed to facade-only dispatch. Asserts the facade received an `AddToConstructionQueueCommand` carrying the threaded design_id, category, queue_id, entity_id, and entity_type. A regression that re-introduced the deleted no-facade in-place mutation fallback would fail because `handle_command` would not be called.
- Commit: `049193339`.

### Task 1.2: C-02 — Facade conversion `EnginePhaseError` → `TurnFailedError` [Medium]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py` (or wherever the facade is unit-tested — check; if no module exists, create one)
**Tests:** `pytest tests/unit/strategy/facade/ -v`

- [x] Read `game/strategy/facade/strategy_session_facade.py:194-201` to understand the conversion path.
- [x] Identify the facade method that catches `EnginePhaseError` and re-raises as `TurnFailedError` with context.
- [x] Write a focused unit test that:
  - Patches the underlying engine call (or constructs a session with a stub engine) so it raises `EnginePhaseError`.
  - Asserts the facade method raises `TurnFailedError`.
  - Asserts the wrapped error carries the expected context (turn_number, save_path, etc. — see PROJ-381 Phase 3 verification).
- [x] Run the test against current production — should PASS (the conversion exists; this is just adding test coverage that was missing).
- [x] Run the broader facade test module to confirm no breakage.

**Notes:**
- Added `TestProcessTurnErrorConversion` class with 5 tests in `tests/unit/strategy/facade/test_strategy_session_facade.py`:
  1. `test_engine_phase_error_is_re_raised_as_turn_failed_error` — class identity check (`type(exc) is TurnFailedError`).
  2. `test_turn_failed_error_preserves_message_code_and_context` — message, code, full context dict, and PROJ-395 properties (phase_name/tick/turn_number/save_path).
  3. `test_turn_failed_error_chains_from_engine_phase_error` — `__cause__` preservation.
  4. `test_invalidate_all_is_not_called_on_engine_phase_error` — error path skips per-turn cache invalidation.
  5. `test_non_engine_phase_error_propagates_unchanged` — only `EnginePhaseError` is converted (e.g., `RuntimeError` propagates raw).
- Full facade module: 324 passed (was 319 before; +5 new).
- Commit: `1add34b20`.

### Task 1.3: C-04 — `PlanetSelectionWindow` facade threading direct unit coverage [Medium]
**File:** `tests/unit/ui/screens/test_planet_selection_window.py` (or wherever — confirm via Glob)
**Tests:** `pytest tests/unit/ui/screens/ -k planet_selection -v`

- [x] Read `PlanetSelectionWindow` to see the facade-threading the PROJ-397 review flagged.
- [x] Find or create the test module.
- [x] Write a unit test that:
  - Constructs `PlanetSelectionWindow` with a real (or stub) facade.
  - Calls a method that exercises facade threading (e.g., one that uses `self._facade` to fetch data or dispatch).
  - Asserts the facade is invoked with the expected arguments (use `unittest.mock.MagicMock` if needed).
- [x] Run the test — pass.

**Notes:**
- Existing test module `tests/unit/ui/screens/test_planet_selection_window.py` had no facade tests. Added `TestFacadeThreading` class with 5 tests pinning PROJ-397 Phase 3 Task 3.2:
  1. `test_facade_stored_on_construction` — Stage-1 cheap-state assignment.
  2. `test_facade_default_is_none_when_omitted` — legacy fixtures continue to work.
  3. `test_update_fetches_demographic_view_for_colonized_planet` — `update()` calls `facade.get_colony_demographic_view(planet.id)` and threads the returned `ColonyDemographicView` into `PlanetReportPanel(view=...)`.
  4. `test_update_skips_facade_for_uncolonized_planet` — short-circuit before facade is consulted.
  5. `test_update_passes_view_none_when_facade_is_none` — legacy callers get `view=None` without legacy fallback rendering.
- Patches `PlanetReportPanel` + `get_default_asset_manager` + `pygame_gui.elements.UIWindow.update` so the panel-creation branch runs without a real pygame display. Sets `window._rect` after `bypass_init` (production reads `self.rect.width/.height`). Also extended the suite-local `_make_window` helper to thread the `facade` kwarg.
- Commit: `b9b622eee`.

### Task 1.4: Run focused suites to confirm no breakage [Simple]
**Tests:**
- `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`
- `pytest tests/unit/strategy/facade/ -v`
- `pytest tests/unit/ui/screens/ -k planet_selection -v`

- [x] All pass.

**Notes:**
- `tests/unit/ui/screens/test_empire_build_queue_window.py`: 118 passed.
- `tests/unit/strategy/facade/`: 324 passed.
- `tests/unit/ui/screens/test_planet_selection_window.py`: 23 passed.
- Cross-check Wave 1 (C-05/C-06) coverage tests still pass:
  - `tests/unit/strategy/validation/ -k missing_species_id`: 1 passed.
  - `tests/unit/strategy/ship_instance/ -k missing_components`: 1 passed.

### Task 1.5: Closeout
- [x] Phase 1 status `Complete`
- [x] Plan.md updated
- [x] `Projects/projects_index.md` row for PROJ-408 set to `Complete`
- [x] Validators PASS
- [x] Commit (one or more): per-task commits `049193339`, `1add34b20`, `b9b622eee` plus closeout commit.
- [x] Verification report at `findings/verification_report.md`

**Notes:**

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] Focused suites pass
- [x] `python Projects/scripts/validate_phase.py PROJ-408 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-408` PASSED
