# Phase 4: CAT-11 Fragile Assertion

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~12 verified CAT-11 fragile-assertion findings from review `2026-05-20_210550_test-review`. Each test pins exact list/dict/pixel-coordinate values that break on formatting / layout changes without behavioral regression. Replace with relaxed matchers, property assertions, or assertions against named constants.

---

## Tasks

### Task 4.1: test_persistence_adapter.py — 50-line literal dict equality
**File:** `tests/unit/strategy/persistence/test_persistence_adapter.py`
**Tests:** `pytest tests/unit/strategy/persistence/test_persistence_adapter.py`

- [ ] Replace exact dict equality (line 150) vs 50-line literal (lines 113-147) with key-by-key validation on the stable subset.
- [ ] Verify: passes; LOC delta ≈ -20.

### Task 4.2: test_caption_schemas_validate.py — 3 exact set equality tests
**File:** `tests/unit/strategy/data/test_caption_schemas_validate.py`
**Tests:** `pytest tests/unit/strategy/data/test_caption_schemas_validate.py`

- [ ] Replace exact set equality (lines 59, 74, 90) for Flag / Portrait / Theme schemas with `issuperset()` so new fields don't break the test.
- [ ] Verify: passes; LOC delta ≈ 0.

### Task 4.3: test_join_fleet_handler.py — exact 7-key dict equality
**File:** `tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_join_fleet_handler.py`

- [ ] Replace exact dict equality (lines 217-242) on FLEET_JOINED payload with `assert all(key in payload for key in ["category", "empire_id", ...])`.
- [ ] Verify: passes; LOC delta ≈ +3.

### Task 4.4: test_design_selector_window.py — call_args[1] kwargs access
**File:** `tests/unit/ui/screens/test_design_selector_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_design_selector_window.py`

- [ ] Replace ~4 `call_args[1]` positional kwargs accesses (lines 189, 202, 215, 813-814) with `call_args.kwargs` (~130 LOC across file).
- [ ] Verify: passes; LOC delta ≈ 0 (style only).

### Task 4.5: test_design_report_panel.py — magic number 750
**File:** `tests/unit/ui/panels/test_design_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_design_report_panel.py`

- [ ] Replace `assert width == 750` (lines 267-273) with assertion against named constant (`DEFAULT_PANEL_WIDTH`) or property (`0 < width < 2000`).
- [ ] Verify: passes; LOC delta ≈ +1.

### Task 4.6: test_workshop_event_router_select_component.py — formula duplication
**File:** `tests/unit/ui/screens/test_workshop_event_router_select_component.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_event_router_select_component.py`

- [ ] Replace formula `50 * sqrt(2000/1000)` duplication (lines 79-91) with property assertions (`mass > 50`, `mass / expected_base in [0.9, 1.1]`).
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 4.7: test_test_run_card.py — exact format substrings
**File:** `tests/unit/ui/screens/test_lab/test_test_run_card.py`
**Tests:** `pytest tests/unit/ui/screens/test_lab/test_test_run_card.py`

- [ ] Replace exact-substring asserts `"Failed Metric:"` / `"1P 1F 0W"` (lines 148, 150) with regex or contains-key assertions.
- [ ] Verify: passes; LOC delta ≈ 0.

### Task 4.8: test_weapons_renderer.py — 9 hardcoded format strings
**File:** `tests/unit/ui/screens/builder/test_weapons_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_weapons_renderer.py`

- [ ] Replace exact ordered list assertion (lines 107-118) with structural assertions (each string contains expected key-value pair) rather than exact strings.
- [ ] Verify: passes; LOC delta ≈ +5.

### Task 4.9: test_list_windows.py — exact pixel coords
**File:** `tests/unit/ui/screens/strategy_windows/test_list_windows.py`
**Tests:** `pytest tests/unit/ui/screens/strategy_windows/test_list_windows.py`

- [ ] Replace `rect.topleft == (50, 40)` / `rect.size == (900, 720)` (lines 55-57) with assertions against named layout constants or shape (`topleft[0] > 0`).
- [ ] Verify: passes; LOC delta ≈ 0.

### Task 4.10: test_order_processor_colonize.py — exact resource dict
**File:** `tests/unit/strategy/engine/test_order_processor_colonize.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor_colonize.py`

- [ ] Replace `assert add_calls == {"metals": 50.0, "organics": 25.0}` exact dict (lines 247-248) with `assert add_calls.get("metals") == 50.0 and add_calls.get("organics") == 25.0`.
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 4.11: test_bug_regressions_2026_01.py — opaque formula result
**File:** `tests/unit/regression/test_bug_regressions_2026_01.py`
**Tests:** `pytest tests/unit/regression/test_bug_regressions_2026_01.py`

- [ ] Replace `assert ab.amount == 25` (lines 45-60) with intermediate `expected = 10 * math.sqrt(stats.mass_mult) * stats.crew_req_mult`; assert on `expected`. Document formula clearly.
- [ ] Verify: passes; LOC delta ≈ +3.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 5 — CAT-12 Logic-Heavy)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
