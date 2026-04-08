# PROJ-246 Phase 1: Switch Data-Loading Call Sites to Strict Mode

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run tests: `pytest tests/unit/simulation/ -x && python -m simulation_tests.run_tests --fast --no-history`

## Objective
Replace `safe_evaluate()` with `evaluate()` at data-loading call sites so malformed JSON formulas crash at boot instead of silently returning 0.

## Status: Complete

---

### Task 1.1: Component Stats Calculator — Strict Evaluate [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [x] Line 197: Replace `FormulaEvaluator.safe_evaluate(formula, eval_context)` with `FormulaEvaluator.evaluate(formula, eval_context)`
- [x] Line 223: Same replacement for resource cost formula evaluation
- [x] Line 244: **NOT CHANGED** — `evaluate_recursive()` in `_evaluate_formulas_in_abilities` must keep `safe_evaluate()` because ability formulas may contain runtime variables (e.g. `range_to_target`) that are not available at load time. See decision log.
- [x] Add try/except around the calling scope that catches `FormulaException` and re-raises with component ID and formula string for clear error messages
- [x] Run tests: `pytest tests/unit/simulation/components/ -x` — 1065 passed

**Notes:** The `_evaluate_formulas_in_abilities` path processes a mix of data-loading formulas and runtime formulas. Runtime formulas (like weapon damage formulas using `range_to_target`) are intentionally evaluated with `safe_evaluate` so they degrade to 0 at load time; the weapon ability re-parses the raw formula string from `component.data` and evaluates it at runtime via `get_damage()`.

---

### Task 1.2: Weapon Init Parsing — Strict Evaluate [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [x] Line 33 in `_parse_formula_field()`: Replace `FormulaEvaluator.safe_evaluate(formula_str, formula_context)` with `FormulaEvaluator.evaluate(formula_str, formula_context)`
- [x] **DID NOT** change line 207 (`get_damage()` runtime path) — kept `safe_evaluate()`
- [x] Fixed `sync_data()` to pass default `formula_context={'range_to_target': 0}` (pre-existing bug where `sync_data` called `_parse_formula_field` without context, hidden by `safe_evaluate`)
- [x] Run tests: `pytest tests/unit/simulation/components/ -x` — 1065 passed

**Notes:** The runtime `get_damage()` method uses `safe_evaluate()` because `range_to_target` context may vary each tick and runtime crashes are unacceptable.

---

### Task 1.3: Verify No Regressions [Simple]
**Tests:** Full simulation test suite

- [x] Run `pytest tests/unit/simulation/ -x` — 2942 passed
- [x] Run `python -m simulation_tests.run_tests --fast --no-history` — 162 passed, 0 failed

**Notes:**
