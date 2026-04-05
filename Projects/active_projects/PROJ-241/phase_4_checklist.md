# Phase 4 Checklist: Remove Redundant Delegation Methods
**Status:** Complete

**Objective:** Remove private delegation methods that just forward to ComponentStatsCalculator
**Estimated effort:** Simple (delete + redirect)
**Risk:** One test directly calls `_apply_base_stats` -- needs update

## Task 4.1: Remove thin private delegation wrappers [Simple]
**File:** `game/simulation/components/component.py`

These three methods (lines 429-439) are one-line forwarders to ComponentStatsCalculator:
```python
def _reset_and_evaluate_base_formulas(self, context=None):     # L429
    ComponentStatsCalculator.reset_and_evaluate_formulas(self, context)

def _calculate_modifier_stats(self):                            # L433
    return ComponentStatsCalculator.calculate_modifier_stats(self.modifiers, self)

def _apply_base_stats(self, stats, old_max_hp):                # L437
    ComponentStatsCalculator.apply_base_stats(self, stats, old_max_hp)
```

External caller: `tests/unit/regressions/test_bug_regressions_2026_01.py:55` calls `c._apply_base_stats(stats, 100)` directly.

- [x] Update `tests/unit/regressions/test_bug_regressions_2026_01.py:55` to call `ComponentStatsCalculator.apply_base_stats(c, stats, 100)` directly
- [x] Remove `_reset_and_evaluate_base_formulas`
- [x] Remove `_calculate_modifier_stats`
- [x] Remove `_apply_base_stats`
- [x] Verify no other callers of these private methods exist (confirmed via grep)
- [x] Run tests: 1096 passed
**Notes:**

## Task 4.2: Verify line count targets [Simple]
- [x] Component class body: 301 lines (down from ~370) -- target was ~280-300
- [x] ModifierManager: 330 lines (includes deprecated static methods with `_static` suffix)
- [x] AbilityManager: 339 lines (includes deprecated static methods with `_static` suffix)
- [x] ComponentStatsCalculator: 292 lines (up from 247 with FORMULA_DEFAULTS + parse_formulas + apply_formula_defaults)
- [x] Module-level functions stay in component.py (lines 382-668, ~286 lines)
- [x] All 4 delegates follow same pattern: `__slots__`, `__init__(component)`, instance methods
- [x] Final line counts documented
**Notes:** Line counts for ModifierManager and AbilityManager are higher than estimated due to deprecated `_static` suffix methods being retained. These can be removed in a future cleanup pass when all callers are confirmed migrated.
