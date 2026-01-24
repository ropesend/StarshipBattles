# PROJ-13 Phase 5: Remaining Code Quality

## Phase Overview
Address remaining minor code quality issues.

## Tasks

### CQ-007: Fix Copy-Paste Targeting Code
- [ ] Open `game/ai/controller.py`
- [ ] Compare find_target() and find_secondary_targets()
- [ ] Extract common logic to helper methods:
  - [ ] `_find_enemies_in_radius()`
  - [ ] `_score_and_sort_enemies()`
- [ ] Update both methods to use helpers
- [ ] Run tests

### SIM-08: Fix Duplicate Ability Aggregation
- [ ] Open `game/simulation/entities/ability_aggregator.py`
- [ ] Compare calculate_ability_totals() and calculate_ability_totals_for_layer()
- [ ] Extract common aggregation logic
- [ ] Update both methods
- [ ] Run tests

### CQ-004: Audit getattr Usage
- [ ] Find all getattr() with fallback values
- [ ] For each, determine if attribute should be guaranteed
- [ ] Add type hints and __init__ declarations where missing
- [ ] Document remaining intentional getattr usage

### CQ-014: Naming Convention Cleanup
- [ ] Document naming conventions
- [ ] Review private method naming (_method vs no prefix)
- [ ] Review property naming (current_, max_, base_)
- [ ] Fix most egregious violations (optional)

### CQ-020: Replace Debug Print Statements
- [ ] Find all print() statements in production code
- [ ] Replace with appropriate log_debug() calls
- [ ] Verify no debug output in normal operation

### SIM-06: Modifier System Extensibility (Documentation)
- [ ] Document current stat key system
- [ ] Document how to add new stats
- [ ] Note: Full dynamic system is future work

### SIM-11: Validation Calculated Stats (Documentation)
- [ ] Document validation system limitations
- [ ] Note: Design validator only sees base stats
- [ ] Document workarounds
- [ ] Note: Full fix is future work

### SIM-13: Make sync_data() Consistent
- [ ] Review ability sync_data() pattern
- [ ] Add default implementation to Ability base class
- [ ] Update abilities that override
- [ ] Run tests

### STRAT-001: Fleet Order Serialization
- [ ] Review fleet.from_dict() method
- [ ] Implement order restoration
- [ ] Handle cross-fleet references (two-phase)
- [ ] Test save/load cycle with orders
- [ ] Run tests

### Final Cleanup
- [ ] Run linter on modified files
- [ ] Address any new warnings
- [ ] Review all changes
- [ ] Run full test suite

## Verification
- [ ] DRY violations addressed
- [ ] Naming more consistent
- [ ] Debug prints removed
- [ ] Fleet orders persist across save/load
- [ ] All tests pass
