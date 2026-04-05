# Phase 4 Checklist: Remove Redundant Delegation Methods
**Status:** Not Started

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

- [ ] Update `tests/unit/regressions/test_bug_regressions_2026_01.py:55` to call `ComponentStatsCalculator.apply_base_stats(c, stats, 100)` directly
- [ ] Remove `_reset_and_evaluate_base_formulas` (line 429-430)
- [ ] Remove `_calculate_modifier_stats` (lines 433-435)
- [ ] Remove `_apply_base_stats` (lines 437-439)
- [ ] Verify no other callers of these private methods exist (they're all internal to `recalculate_stats` which already delegates)
- [ ] Run tests: `pytest tests/unit/entities/test_components.py tests/unit/simulation/components/ tests/unit/regressions/ -v`
**Notes:**

## Task 4.2: Verify line count targets [Simple]
- [ ] Component class body should be ~280-300 lines (down from ~370)
- [ ] ModifierManager should be ~220-230 lines (up from 203 with state + `_load_initial_modifiers`)
- [ ] AbilityManager should be ~240-260 lines (up from 206 with index building + `has_ability_with_tag`)
- [ ] ComponentStatsCalculator should be ~270 lines (up from 247 with formula parsing)
- [ ] Module-level functions stay in component.py (~280 lines, not part of class)
- [ ] All 4 delegates follow same pattern: `__slots__`, `__init__(component)`, instance methods
- [ ] Document final line counts in Current State
**Notes:**
