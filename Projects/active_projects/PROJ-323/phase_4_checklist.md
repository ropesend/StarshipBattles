# Phase 4: CAT-11 Fragile Assertion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-323 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace fragile assertions in the 15 verified CAT-11 cases with semantic comparisons or documented boundary references.

---

## Tasks

### Task 4.1: test_portrait_load_success.py [Simple]
**File:** `tests/integration/data/test_portrait_load_success.py`
**Tests:** `pytest tests/integration/data/test_portrait_load_success.py`

- [ ] [S11-CAT11-003] `test_portrait_load_success_no_warning` (lines 87-88): Assert zero WARNING-level records from the logger instead.

- [ ] Verify: `pytest tests/integration/data/test_portrait_load_success.py` passes; LOC delta ≈ 2

**Notes:** _(none yet)_

---

### Task 4.2: test_deprecated_code_removed.py [Simple]
**File:** `tests/regression/test_deprecated_code_removed.py`
**Tests:** `pytest tests/regression/test_deprecated_code_removed.py`

- [ ] [S02-CAT11-001] `EXPECTED_GAME_COUNT magic numbers` (lines 152-199): Remove the count-based tests or make them advisory-only. The hasattr checks already guard against reintroduced code.

- [ ] Verify: `pytest tests/regression/test_deprecated_code_removed.py` passes; LOC delta ≈ 48

**Notes:** _(none yet)_

---

### Task 4.3: test_combat_types.py [Simple]
**File:** `tests/unit/core/test_combat_types.py`
**Tests:** `pytest tests/unit/core/test_combat_types.py`

- [ ] [S06-CAT11-001] `test_slots` (lines 29-31): Remove or merge.

- [ ] Verify: `pytest tests/unit/core/test_combat_types.py` passes; LOC delta ≈ 3

**Notes:** _(none yet)_

---

### Task 4.4: test_formation_files_have_professional_names.py [Simple]
**File:** `tests/unit/qa/test_formation_files_have_professional_names.py`
**Tests:** `pytest tests/unit/qa/test_formation_files_have_professional_names.py`

- [ ] [S11-CAT11-002] `Profanity regex test` (lines 24-48): Move to pre-commit hook.

- [ ] Verify: `pytest tests/unit/qa/test_formation_files_have_professional_names.py` passes; LOC delta ≈ 25

**Notes:** _(none yet)_

---

### Task 4.5: test_battle_state_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_battle_state_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_battle_state_validation.py`

- [ ] [S08-CAT11-002] `Substring matching on exception messages` (lines 39-101): Assert exception type and structured field; not message text.

- [ ] Verify: `pytest tests/unit/strategy/data/test_battle_state_validation.py` passes; LOC delta ≈ 63

**Notes:** _(none yet)_

---

### Task 4.6: test_event_validation.py [Simple]
**File:** `tests/unit/strategy/data/test_event_validation.py`
**Tests:** `pytest tests/unit/strategy/data/test_event_validation.py`

- [ ] [S08-CAT11-001] `Exact event_type/message strings` (lines 26-33): Assert structural shape and field types instead of exact strings.

- [ ] Verify: `pytest tests/unit/strategy/data/test_event_validation.py` passes; LOC delta ≈ 8

**Notes:** _(none yet)_

---

### Task 4.7: test_race_loader.py [Simple]
**File:** `tests/unit/strategy/data/test_race_loader.py`
**Tests:** `pytest tests/unit/strategy/data/test_race_loader.py`

- [ ] [S11-CAT11-001] `test_race_has_valid_theme` (lines 84-88): Load valid themes from registry.

- [ ] Verify: `pytest tests/unit/strategy/data/test_race_loader.py` passes; LOC delta ≈ 5

**Notes:** _(none yet)_

---

### Task 4.8: test_superweapon_orders.py [Simple]
**File:** `tests/unit/strategy/data/test_superweapon_orders.py`
**Tests:** `pytest tests/unit/strategy/data/test_superweapon_orders.py`

- [ ] [S08-CAT11-003] `Exact dict-structure assertions` (lines 62-123): Assert structural invariants; consider schema validation.

- [ ] Verify: `pytest tests/unit/strategy/data/test_superweapon_orders.py` passes; LOC delta ≈ 62

**Notes:** _(none yet)_

---

### Task 4.9: test_colonize_mission_handler.py [Simple]
**File:** `tests/unit/strategy/engine/test_colonize_mission_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py`

- [ ] [S01-CAT11-001] `make_component_registry duplicate key` (lines 107-123): Remove the duplicate 'colony_pod' entry (lines 113-117).

- [ ] Verify: `pytest tests/unit/strategy/engine/test_colonize_mission_handler.py` passes; LOC delta ≈ 6

**Notes:** _(none yet)_

---

### Task 4.10: test_facade_dispatch.py [Simple]
**File:** `tests/unit/strategy/facade/test_facade_dispatch.py`
**Tests:** `pytest tests/unit/strategy/facade/test_facade_dispatch.py`

- [ ] [S08-CAT11-004] `DISPATCH_CASES with 31 hardcoded entries` (lines 36-68): Generate from dispatch registry rather than hardcode names.

- [ ] Verify: `pytest tests/unit/strategy/facade/test_facade_dispatch.py` passes; LOC delta ≈ 33

**Notes:** _(none yet)_

---

### Task 4.11: test_strategy_menu_panel.py [Simple]
**File:** `tests/unit/ui/panels/test_strategy_menu_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_strategy_menu_panel.py`

- [ ] [S08-CAT11-005] `Exact menu label/option-id assertions` (lines 48-78): Assert membership/structure rather than exact ordering.

- [ ] Verify: `pytest tests/unit/ui/panels/test_strategy_menu_panel.py` passes; LOC delta ≈ 31

**Notes:** _(none yet)_

---

### Task 4.12: test_renderer.py [Simple]
**File:** `tests/unit/ui/screens/battle_setup/test_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_renderer.py`

- [ ] [S07-CAT11-001] `test_renderer_is_stateless_between_calls` (lines 29-38): Replace with behavioral assertion on stateless behavior.

- [ ] Verify: `pytest tests/unit/ui/screens/battle_setup/test_renderer.py` passes; LOC delta ≈ 10

**Notes:** _(none yet)_

---

### Task 4.13: test_empire_build_queue_window.py [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] [S05-CAT11-001] `Hardcoded 18-column set` (lines 388-402): Replace with a behavioral assertion on column purpose, not literal IDs.

- [ ] Verify: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

### Task 4.14: test_new_game_setup.py [Simple]
**File:** `tests/unit/ui/test_new_game_setup.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`

- [ ] [S09-CAT11-001] `test_build_game_config_signature_default_matches_dataclass` (lines 103-117): Replace with a behavioral default-construction test.

- [ ] Verify: `pytest tests/unit/ui/test_new_game_setup.py` passes; LOC delta ≈ 15

**Notes:** _(none yet)_

---

### Task 4.15: test_unified_entry_guard.py [Simple]
**File:** `tests/unit/ui/test_unified_entry_guard.py`
**Tests:** `pytest tests/unit/ui/test_unified_entry_guard.py`

- [ ] [S07-CAT11-002] `test_whitelist_size_locked` (lines 70-78): Keep as gate but use a constant defined alongside the whitelist.

- [ ] Verify: `pytest tests/unit/ui/test_unified_entry_guard.py` passes; LOC delta ≈ 9

**Notes:** _(none yet)_

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
