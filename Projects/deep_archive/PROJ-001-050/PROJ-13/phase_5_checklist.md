# PROJ-13 Phase 5: Remaining Code Quality

## Phase Overview
Address remaining minor code quality issues.

## Tasks

### CQ-007: Fix Copy-Paste Targeting Code
- [x] Open `game/ai/controller.py`
- [x] Compare find_target() and find_secondary_targets()
- [x] Extract common logic to helper methods:
  - [x] `_find_enemies_in_radius()`
  - [x] `_score_and_sort_enemies()`
- [x] Update both methods to use helpers
- [x] Run tests

**Notes:** Extracted two helper methods to eliminate ~40 lines of duplicate code. Both `find_target()` and `find_secondary_targets()` now use the shared helpers. Added 7 new tests in `TestTargetingHelpers` class. All 189 AI tests pass.

### SIM-08: Fix Duplicate Ability Aggregation
- [x] Open `game/simulation/entities/ability_aggregator.py`
- [x] Compare calculate_ability_totals() and calculate_ability_totals_for_layer()
- [x] Extract common aggregation logic
- [x] Update both methods
- [x] Run tests

**Notes:** Extracted `_aggregate_ability_groups()` helper function to eliminate ~30 lines of duplicate aggregation logic. Both main functions now use the shared helper. Added 5 new tests in `TestAggregateAbilityGroups` class. All 17 ability aggregator tests pass.

### CQ-004: Audit getattr Usage
- [x] Find all getattr() with fallback values
- [x] For each, determine if attribute should be guaranteed
- [x] Add type hints and __init__ declarations where missing
- [x] Document remaining intentional getattr usage

**Notes:** Substantially addressed in Phase 4 (UI-004). Found 178 getattr uses across 41 files. Most are intentional for:
- Optional attributes (`is_derelict`, `max_targets`, `crew_*`)
- Polymorphic access (different object types)
- Backward compatibility with older object versions
Documentation added to PATTERNS.md "Type-Safe Data Access" section with key UI data contracts table.

### CQ-014: Naming Convention Cleanup
- [x] Document naming conventions
- [x] Review private method naming (_method vs no prefix)
- [x] Review property naming (current_, max_, base_)
- [x] Fix most egregious violations (optional)

**Notes:** Added comprehensive "Naming Conventions" section to PATTERNS.md covering:
- Methods (`_method`, `get_*`, `calculate_*`, `is_*`, `on_*`, `find_*`)
- Properties/Attributes (`current_*`, `max_*`, `base_*`, `total_*`)
- Classes (`*Manager`, `*Service`, `*Mixin`, `*Panel`, `*Screen`)
- Constants (SCREAMING_SNAKE_CASE)
- Files (snake_case.py)
No egregious violations found requiring immediate fixes.

### CQ-020: Replace Debug Print Statements
- [x] Find all print() statements in production code
- [x] Replace with appropriate log_debug() calls
- [x] Verify no debug output in normal operation

**Notes:** Found 3 debug print statements in `game/app.py` and `game/ui/screens/workshop_screen.py`. Replaced all with `log_debug()` calls. No more print statements in production code.

### SIM-06: Modifier System Extensibility (Documentation)
- [x] Document current stat key system
- [x] Document how to add new stats
- [x] Note: Full dynamic system is future work

**Notes:** Documentation already exists:
- `docs/modifier_system.md` - Full architecture overview with data flow, ModifierEffect, STAT_BINDINGS
- `docs/adding_modifiers.md` - Step-by-step guide including stat key table, formula syntax, restrictions
No additional documentation needed.

### SIM-11: Validation Calculated Stats (Documentation)
- [x] Document validation system limitations
- [x] Note: Design validator only sees base stats
- [x] Document workarounds
- [x] Note: Full fix is future work

**Notes:** Added "Validation System Limitations" section to PATTERNS.md documenting:
- Design-time vs runtime stats limitation
- Why modifier-adjusted stats aren't available at validation time
- Workarounds (use base stat requirements, runtime validation, warnings)
- Example showing crew requirements pattern
- Future work notes

### SIM-13: Make sync_data() Consistent
- [x] Review ability sync_data() pattern
- [x] Add default implementation to Ability base class
- [x] Update abilities that override
- [x] Run tests

**Notes:** The base class already has sync_data(). Added sync_data() overrides to propulsion abilities:
- CombatPropulsion, ManeuveringThruster, StrategicMovement now sync their base values when data changes
- Added 3 new tests in TestPropulsionSyncData class
- All 14 propulsion ability tests pass

### STRAT-001: Fleet Order Serialization
- [x] Review fleet.from_dict() method
- [x] Implement order restoration
- [x] Handle cross-fleet references (two-phase)
- [x] Test save/load cycle with orders
- [x] Run tests

**Notes:** Implemented order restoration in Fleet.from_dict():
- MOVE orders restored with HexCoord targets
- COLONIZE and other orders restored with appropriate targets
- Fleet references stored as `{'_fleet_ref': id}` for later resolution
- Added 3 new tests in TestFleetSerialization class
- All 76 fleet tests pass

### Final Cleanup
- [x] Run linter on modified files
- [x] Address any new warnings
- [x] Review all changes
- [x] Run full test suite

**Notes:** Full test suite: 4561 passed, 1 failed (pre-existing flaky test), 1 skipped, 189 warnings. No new regressions.

## Verification
- [x] DRY violations addressed
- [x] Naming more consistent
- [x] Debug prints removed
- [x] Fleet orders persist across save/load
- [x] All tests pass (except pre-existing flaky test)

## Notes
- Phase 5 complete - all tasks finished
- Pre-existing flaky test: `test_intercept_integration` (fails in parallel, passes isolated)
