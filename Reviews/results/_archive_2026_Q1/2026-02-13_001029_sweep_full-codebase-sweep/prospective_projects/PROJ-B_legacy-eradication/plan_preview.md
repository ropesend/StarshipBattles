# PROJ-B: Legacy System Eradication

## Project Overview

**Goal:** Remove all backward compatibility shims, deprecated code paths, and legacy API holdovers per the System Migration Policy.

**Context:** The policy states "When a new system replaces an old one, ERADICATE the old system completely." This project addresses 37 findings where legacy code remains.

## Current State

- String-to-Enum migration code still active in BattleEngine
- Backward compatibility aliases in RacePortraitGallery
- Legacy BuilderScreen parallel to WorkshopScreen
- V1 modifier format detection code
- Numerous hasattr checks for always-present attributes
- Multiple dual-format support patterns

## Target State

- All migration support code removed
- Single authoritative API for each system
- No hasattr checks for standard attributes
- No "backward compatibility" comments in code
- Clean, single-path code without fallbacks

## Phases

### Phase 1: Simple Removals
**Estimated Duration:** 2 days

#### 1.1 Unused Code Removal
- [ ] Remove unused exception classes from `game/core/exceptions.py`
- [ ] Remove dead code `draw_hud` and `draw_bar` from renderer
- [ ] Remove unused `create_ai_for_ship` method
- [ ] Remove unused `capture_step` method
- [ ] Remove unused `AbilityStatBinding.describe()` method

#### 1.2 Alias and Shim Removal
- [ ] Remove backward compatibility aliases from `race_portrait_gallery.py`
- [ ] Update tests to use canonical attribute names
- [ ] Remove legacy API comment from FleetReportWindow (or actual method if legacy)
- [ ] Remove DEBUG_SCREENSHOTS hardcoded True

#### 1.3 Hasattr Cleanup
- [ ] Remove hasattr check for `just_fired_projectiles` (always present)
- [ ] Add `retreat_status` as formal Ship attribute
- [ ] Remove hasattr checks for retreat_status
- [ ] Convert hasattr fallbacks to direct attribute access

### Phase 2: Format Consolidation
**Estimated Duration:** 2 days

#### 2.1 Enum Migration
- [ ] Find all callers passing string attack types
- [ ] Update callers to use `AttackType` enum
- [ ] Remove string-to-enum migration code from battle_engine.py
- [ ] Remove V1 modifier format detection (or convert to exception)

#### 2.2 Data Format Migration
- [ ] Find callers using `(layer, idx, comp)` tuple format
- [ ] Migrate to `ComponentRef` typed reference
- [ ] Remove tuple format support from detail_panel.py
- [ ] Update WorkshopEventRouter to single format

#### 2.3 Backward Compatibility Wrappers
- [ ] Audit `load_resources` wrapper usage
- [ ] Remove or migrate callers
- [ ] Remove wrapper from resources.py

### Phase 3: Complex Removals
**Estimated Duration:** 3 days

#### 3.1 Legacy BuilderScreen Evaluation
- [ ] Audit test dependencies on BuilderScreen
- [ ] Audit any production usage
- [ ] If unused: remove entire builder/main.py
- [ ] If used: document why and remove "legacy" label

#### 3.2 Selection System Cleanup
- [ ] Audit callers of `selected_index` / `selected_source`
- [ ] Migrate to multi-selection API (`selected_indices`)
- [ ] Remove legacy single-selection fields

#### 3.3 Fallback Mode Removal
- [ ] Audit BuildQueueController fallback mode usage
- [ ] Make queue source selection mandatory
- [ ] Remove `_add_to_fallback` method

#### 3.4 Deprecated Properties
- [ ] Complete facade migration in StrategyScreen
- [ ] Remove deprecated property notes
- [ ] Or remove misleading deprecation comments

### Phase 4: Cleanup
**Estimated Duration:** 1 day

- [ ] Search for remaining "backward compatibility" comments
- [ ] Search for remaining "legacy" comments
- [ ] Search for remaining "migration" comments
- [ ] Remove or justify each instance
- [ ] Run full test suite

## Validation

### During Development
- Run `pytest tests/ --testmon` after each removal
- Verify no runtime errors with manual testing
- Check for import errors after removing code

### Completion Criteria
- [ ] All Critical findings resolved (2/2)
- [ ] All Major findings resolved (14/14)
- [ ] All Minor findings addressed (19/19)
- [ ] No "backward compatibility" code paths remain
- [ ] Full test suite passes: `pytest tests/ -n 12`

## Notes

- Coordinate with PROJ-58 if it becomes active
- Some "legacy" comments may be stale - verify before removing code
- Document any code that must be kept and why
