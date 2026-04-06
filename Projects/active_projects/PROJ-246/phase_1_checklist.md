# PROJ-246 Phase 1: Switch Data-Loading Call Sites to Strict Mode

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run tests: `pytest tests/unit/simulation/ -x && python -m simulation_tests.run_tests --fast --no-history`

## Objective
Replace `safe_evaluate()` with `evaluate()` at 4 data-loading call sites so malformed JSON formulas crash at boot instead of silently returning 0.

## Status: Not Started

---

### Task 1.1: Component Stats Calculator — Strict Evaluate [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [ ] Line 197: Replace `FormulaEvaluator.safe_evaluate(formula, eval_context)` with `FormulaEvaluator.evaluate(formula, eval_context)`
- [ ] Line 223: Same replacement for resource cost formula evaluation
- [ ] Line 244: Same replacement in `evaluate_recursive()` helper
- [ ] Add try/except around the calling scope that catches `FormulaException` and re-raises with component ID and formula string for clear error messages:
  ```python
  except FormulaException as e:
      raise FormulaException(
          f"Component '{component.id}' has invalid formula "
          f"in field '{attr}': {e}"
      ) from e
  ```
- [ ] Run tests: `pytest tests/unit/simulation/components/ -x`

**Notes:**

---

### Task 1.2: Weapon Init Parsing — Strict Evaluate [Simple]
**File:** `game/simulation/components/abilities/weapons.py`
**Tests:** `pytest tests/unit/simulation/components/ -x`

- [ ] Line 33 in `_parse_formula_field()`: Replace `FormulaEvaluator.safe_evaluate(formula_str, formula_context)` with `FormulaEvaluator.evaluate(formula_str, formula_context)`
- [ ] **DO NOT** change line 207 (`get_damage()` runtime path) — this MUST keep `safe_evaluate()`
- [ ] Run tests: `pytest tests/unit/simulation/components/ -x`

**Notes:** The runtime `get_damage()` method uses `safe_evaluate()` because `range_to_target` context may vary each tick and runtime crashes are unacceptable.

---

### Task 1.3: Verify No Regressions [Simple]
**Tests:** Full simulation test suite

- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] Run `python -m simulation_tests.run_tests --fast --no-history` — all simulation tests pass
- [ ] Boot the game with `python main.py` — verify no crashes on load

**Notes:**
