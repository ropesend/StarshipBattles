# PROJ-246: Silent Formula Evaluation Failure

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-246` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
`FormulaEvaluator.safe_evaluate()` catches `FormulaException` and silently returns 0 on error, hiding data file bugs. A typo in a component JSON formula (e.g., `"=2 ^ parm"`) makes the weapon deal zero damage with only a log warning. Data loading should crash fast; runtime fallbacks are acceptable.

## Goals
- Data-loading formulas raise FormulaException (catch corruption at boot, not in combat)
- Runtime formulas continue to use safe fallback with WARNING log
- Clear separation between strict (data) and lenient (runtime) evaluation paths

## Scope
**In Scope:**
- Replace `safe_evaluate()` with `evaluate()` at 4 data-loading call sites
- Keep `safe_evaluate()` for 3 runtime call sites
- Add tests for strict data-loading behavior
- Add tests verifying runtime path still degrades gracefully

**Out of Scope:**
- Changing the FormulaEvaluator class API itself
- Changing the formula language or eval() security sandbox
- Modifying modifier_effects.py (already delegates to FormulaEvaluator)

## Current State
**Last Updated:** 2026-04-06 23:30
**Current Phase:** Planning Complete
**Last Agent Action:** Plan written with verified line numbers from deep code review
**Next Action:** Implementation via Continue Project prompt
**Blockers:** None
**Context for Next Agent:** safe_evaluate is used at 7 call sites. 4 are data-loading (should crash), 3 are runtime (should keep safe fallback). The FormulaEvaluator class itself doesn't change — only which method callers use.

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| safe_evaluate def | `game/simulation/formula_system.py:235-261` | `FormulaEvaluator.safe_evaluate()` |
| evaluate def | `game/simulation/formula_system.py:100-170` | `FormulaEvaluator.evaluate()` |
| Comp base formulas (DATA) | `game/simulation/components/component_stats_calculator.py:197` | `reset_and_evaluate_formulas()` |
| Comp resource costs (DATA) | `game/simulation/components/component_stats_calculator.py:223` | `reset_and_evaluate_formulas()` |
| Ability formula recursion (DATA) | `game/simulation/components/component_stats_calculator.py:244` | `evaluate_recursive()` |
| Weapon init parsing (DATA) | `game/simulation/components/abilities/weapons.py:33` | `_parse_formula_field()` |
| Weapon runtime damage (RUNTIME) | `game/simulation/components/abilities/weapons.py:207` | `get_damage()` |
| Strategy stats calc (RUNTIME) | `game/strategy/services/ship_stats_calculator.py:659` | `_evaluate_value()` |
| Resource cost mgr (RUNTIME) | `game/simulation/components/component_resource_manager.py:112` | `get_applied_costs()` |
| Existing tests | `tests/unit/simulation/test_formula_evaluator.py:351-374` | `TestFormulaEvaluatorSafeEvaluate` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Crash with exception at data load | Developer must fix JSON before game runs. Fastest path to finding data bugs. |
| 2026-04-06 | Keep WARNING level for runtime safe_evaluate | Current behavior is acceptable. Noisy if formula broken, but visible for debugging. |
| 2026-04-06 | Don't modify FormulaEvaluator class | Both evaluate() and safe_evaluate() already exist. Just change which one callers use. |

## Initial Analysis

### Call Site Classification
**DATA LOADING (should use strict `evaluate()`):**
1. `component_stats_calculator.py:197` — base attribute formulas (mass, HP)
2. `component_stats_calculator.py:223` — resource cost formulas
3. `component_stats_calculator.py:244` — ability formula recursion
4. `weapons.py:33` — weapon init parsing (damage, range, reload)

**RUNTIME (keep lenient `safe_evaluate()`):**
5. `weapons.py:207` — `get_damage()` with range_to_target context
6. `ship_stats_calculator.py:659` — strategy layer stat evaluation
7. `component_resource_manager.py:112` — runtime resource cost multiplier

### Risk Assessment
- **Low risk:** Data-loading sites already work with valid formulas. Switching to strict just means invalid formulas crash instead of silently returning 0.
- **Test impact:** Existing tests that test safe_evaluate behavior still pass (runtime path unchanged). Need new tests for strict data-loading path.
- **No save file impact:** Formulas are in JSON data files, not save files.

---

## Phases

### Phase 1: Switch Data-Loading Call Sites to Strict Mode [Simple]
**Objective:** Replace safe_evaluate() with evaluate() at 4 data-loading call sites
**Status:** Not Started

See `phase_1_checklist.md` for detailed tasks.

### Phase 2: Add Tests [Simple]
**Objective:** Verify strict mode catches bad formulas, runtime mode degrades gracefully
**Status:** Not Started

See `phase_2_checklist.md` for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `pytest tests/` — all tests pass

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] `python -m simulation_tests.run_tests --fast` — all simulation tests pass

### Final Verification
- [ ] Game boots with valid data files — no crashes
- [ ] Introduce deliberate formula typo in test components.json — verify it raises at load
- [ ] Run full test suite: `pytest tests/` — all pass
- [ ] Verify changes are consistent with `docs/` — update docs if needed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] User verified
