# Phase 2: CAT-5 Fixture Bloat

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rescope or share the 20 verified CAT-5 expensive fixtures to module/session scope where safe.

---

## Tasks

### Task 2.1: Module-scope builder UI-sync setup_ui [Medium]
**File:** `tests/integration/builder/test_builder_ui_sync.py`
**Tests:** `pytest tests/integration/builder/test_builder_ui_sync.py`

- [ ] S03-CAT5-001: promote `setup_ui` autouse fixture (lines 18-85) to module scope, or split heavy setup (pygame.display init, UIManager construction, file I/O, real BuilderRightPanel) from per-test state. 3 tests share it.
- [ ] Verify: `pytest tests/integration/builder/test_builder_ui_sync.py` passes; LOC delta approximately -45 (savings via reduced repeat work)

---

### Task 2.2: Module-scope dialog-size pygame display [Simple]
**File:** `tests/repro_issues/test_bug_11_dialog_size.py`
**Tests:** `pytest tests/repro_issues/test_bug_11_dialog_size.py`

- [ ] S06-CAT5-001: promote the `pygame.display.set_mode()` autouse fixture (lines 19-66) to module scope; keep the test as a smoke regression.
- [ ] Verify: `pytest tests/repro_issues/test_bug_11_dialog_size.py` passes; LOC delta approximately -30 (cycle-time)

---

### Task 2.3: Memoize / module-scope workshop view-model registries [Simple]
**File:** `tests/unit/builder/test_workshop_viewmodel.py`
**Tests:** `pytest tests/unit/builder/test_workshop_viewmodel.py`

- [ ] S12-CAT5-002: promote `mock_registries` (currently function-scoped, calls `load_components_data` per function) and `viewmodel_setup` (lines 37-87) to module/class scope, or memoize the disk load.
- [ ] Verify: `pytest tests/unit/builder/test_workshop_viewmodel.py` passes; LOC delta approximately -20

---

### Task 2.4: Rescope reset_registry autouse [Simple]
**File:** `tests/unit/core/test_pure_loaders.py`
**Tests:** `pytest tests/unit/core/test_pure_loaders.py`

- [ ] S04-CAT5-001: rescope `reset_registry` autouse fixture (lines 23-28) from function -> module/session; tests only read.
- [ ] Verify: `pytest tests/unit/core/test_pure_loaders.py` passes; LOC delta approximately -5

---

### Task 2.5: Share BattleEngine and boundaries across exit-policy tests [Medium]
**File:** `tests/unit/simulation/combat/test_exit_policy.py`
**Tests:** `pytest tests/unit/simulation/combat/test_exit_policy.py`

- [ ] S11-CAT5-002: hoist `RectBoundary` to module-level constants and share `BattleEngine`/2-ship fixture for the 7 tests at lines 42-93.
- [ ] Verify: `pytest tests/unit/simulation/combat/test_exit_policy.py` passes; LOC delta approximately -30

---

### Task 2.6: Rescope component-resource-manager fixtures [Medium]
**File:** `tests/unit/simulation/components/test_component_resource_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_component_resource_manager.py`

- [ ] S08-CAT5-001: rescope the 3 function-scoped MagicMock-tree fixtures (lines 23-52) to class or module scope; ~24 test methods across 9 classes use them.
- [ ] Verify: `pytest tests/unit/simulation/components/test_component_resource_manager.py` passes; LOC delta approximately -20

---

### Task 2.7: Rescope full_registry to class scope [Medium]
**File:** `tests/unit/simulation/services/test_modifier_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_modifier_service.py`

- [ ] S10-CAT5-002: rescope `full_registry` (currently function-scoped, lines 226-253; creates 11 mock Modifier objects per test) to class scope after verifying no test mutates state. 20+ tests share it.
- [ ] Verify: `pytest tests/unit/simulation/services/test_modifier_service.py` passes; LOC delta approximately -28 (cycle-time)

---

### Task 2.8: Consolidate resupply-engine helper functions into shared fixtures [Complex]
**File:** `tests/unit/strategy/engine/test_resupply_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_resupply_engine.py`

- [ ] S08-CAT5-002: consolidate the 10 helper functions (lines 20-101 and 306-379: `_make_mock_registries`, `_make_*_facility`, `_make_colony`, `_make_empire`, `_make_mock_ship/fleet/galaxy`, `_make_planet_with_fuel`) into shared fixtures under `tests/fixtures/`. Coordinate with HLP-001/HLP-003/HLP-004/DUP-003 in Phase 6.
- [ ] Verify: `pytest tests/unit/strategy/engine/test_resupply_engine.py` passes; LOC delta approximately -120 (overlaps with Phase 6 cluster work)

---

### Task 2.9: Shared mock-fleet/empire factories for strategy-session-facade [Complex]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade.py`

- [ ] S10-CAT5-003: collapse the 7 `_make_mock_*` helpers across 4 classes (lines 19-39, 168-181, 252-261, 333-363, 484-520) into shared kwargs-override factories in conftest.py / `tests/fixtures/`. Coordinate with HLP-001 in Phase 6.
- [ ] Verify: `pytest tests/unit/strategy/facade/test_strategy_session_facade.py` passes; LOC delta approximately -55

---

### Task 2.10: Module-scope astrophysics loader fixtures [Simple]
**File:** `tests/unit/strategy/generation/test_astrophysics.py`
**Tests:** `pytest tests/unit/strategy/generation/test_astrophysics.py`

- [ ] S04-CAT5-002: collapse the 5 identical `AstrophysicsLoader()` per-class fixtures (lines 97-107, 134-138, 167-171, 192-196, 224-228) into a single module-scoped fixture; the file load currently runs 5x.
- [ ] Verify: `pytest tests/unit/strategy/generation/test_astrophysics.py` passes; LOC delta approximately -20

---

### Task 2.11: Module-scope empire-treasury panel fixtures (adjusted) [Medium]
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

_(Plan-review M-002 (2026-05-03): mutable MagicMock objects accumulate assert state — either keep per-test or add reset_mock() autouse fixture.)_

- [ ] S05-CAT5-001 (NEEDS_REWORK): rescope `mock_ui_manager` and `mock_resource_icons` (immutable inputs) to module scope. Keep `sample_snapshot` and `mock_panel` at function scope — they accumulate `assert_called_*` state which must be per-test. Actual test count is 17 methods (not 12 as originally claimed). _(verification adjusted from review's "Module-scope the fixtures (claim: 13 test methods)" - see verification_report.md)_
- [ ] **Alternative approach:** rescope ALL four fixtures to module scope BUT add a `conftest.py` autouse fixture that calls `reset_mock()` on the shared mocks between tests. Document in this task body which approach was chosen and why before marking complete.
- [ ] Verify: `pytest tests/unit/ui/panels/test_empire_treasury_panel.py` passes; LOC delta approximately -10

---

### Task 2.12: Rescope modifier-editor-panel fixture [Simple]
**File:** `tests/unit/ui/panels/test_modifier_editor_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_modifier_editor_panel.py`

- [ ] S10-CAT5-001: rescope `modifier_panel` (function-scoped, lines 10-44; 5 MagicMocks + real ModifierEditorPanel) to class scope, or merge the 3 tests into one parametrized test.
- [ ] Verify: `pytest tests/unit/ui/panels/test_modifier_editor_panel.py` passes; LOC delta approximately -25

---

### Task 2.13: Module-scope battle-setup-logic autouse [Simple]
**File:** `tests/unit/ui/screens/test_battle_setup_logic.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_logic.py`

- [ ] S04-CAT5-003: rescope `setup_game_data` autouse fixture (lines 17-31, calls pygame.init / `initialize_ship_data` / `load_components` / policy load) to module scope; only 3 tests run.
- [ ] Verify: `pytest tests/unit/ui/screens/test_battle_setup_logic.py` passes; LOC delta approximately -10

---

### Task 2.14: Convert build-queue-screen helper to class-scoped fixture [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen.py`

- [ ] S12-CAT5-001: convert the 88-LOC `_make_build_queue_screen` plain function (lines 37-125; ~50 mock attrs) into a `scope='class'` pytest fixture; expose a thin per-test override path. Coordinate with APC-001-F15 in Phase 5.
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_screen.py` passes; LOC delta approximately -50

---

### Task 2.15: Extract make_mock_ship to shared fixture [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py`

- [ ] S08-CAT5-003: extract the 63-LOC `make_mock_ship` helper (lines 12-75; 20+ params, called 80+ times across 15 classes) to shared `tests/fixtures/test_entities.py` with kwargs overrides. Coordinate with HLP-001 in Phase 6.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_filters.py` passes; LOC delta approximately -50

---

### Task 2.16: Rescope queue-selector build_queue_screen fixture [Medium]
**File:** `tests/unit/ui/screens/test_queue_selector.py`
**Tests:** `pytest tests/unit/ui/screens/test_queue_selector.py`

- [ ] S03-CAT5-002: rescope `build_queue_screen` (function-scoped, lines 50-123; real BuildQueueScreen + pygame_gui UIManager + Planet + Empire) to class or module scope; 7 tests share it.
- [ ] Verify: `pytest tests/unit/ui/screens/test_queue_selector.py` passes; LOC delta approximately -50 (cycle-time)

---

### Task 2.17: Class-scope or rebuild race-setup-screen helper [Medium]
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [ ] S07-CAT5-001: factor the 118-LOC `_make_race_setup_screen` heavy bypass-init helper (lines 31-148; ~50 mock objects) into a class-scoped fixture; preferred fix - construct the real screen with mocked pygame_gui. Coordinate with APC-001-F11 in Phase 5.
- [ ] Verify: `pytest tests/unit/ui/screens/test_race_setup_screen.py` passes; LOC delta approximately -90

---

### Task 2.18: Module-level setup_tmpdir for save-selection [Simple]
**File:** `tests/unit/ui/screens/test_save_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_save_selection.py`

- [ ] S09-CAT5-001: collapse the 3 byte-identical autouse `setup_tmpdir` fixtures (lines 47-55, 148-156, 217-225) into a single module-level fixture or conftest helper.
- [ ] Verify: `pytest tests/unit/ui/screens/test_save_selection.py` passes; LOC delta approximately -20

---

### Task 2.19: Rescope ship_io Ship fixtures [Simple]
**File:** `tests/unit/ui/services/test_ship_io.py`
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py`

- [ ] S02-CAT5-002: rescope `mock_ship`, `mock_ship_with_special_chars`, `minimal_ship` (function-scoped, lines 27-55) to class or module scope; 14 classes consume them.
- [ ] Verify: `pytest tests/unit/ui/services/test_ship_io.py` passes; LOC delta approximately -20

---

### Task 2.20: Single module-scoped pygame.init fixture for camera tests [Medium]
**File:** `tests/unit/ui/test_camera.py`
**Tests:** `pytest tests/unit/ui/test_camera.py`

- [ ] S02-CAT5-001: collapse the 8 per-class pygame.init autouse fixtures (lines 22-26, 48-51, 115-118, 164-167, 237-240, 259-262, 305-308, 355-361) into a single module-scoped fixture; SDL_VIDEODRIVER is already set by the repo conftest.
- [ ] Verify: `pytest tests/unit/ui/test_camera.py` passes; LOC delta approximately -45

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
