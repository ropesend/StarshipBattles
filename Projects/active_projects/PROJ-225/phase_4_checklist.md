# Phase 4: Cross-Cutting + Minor Cleanup
**Status:** Complete

## Task 4.1: Consolidate Firing Arc Check [Simple]
**Finding:** DUP-XL-001
**Tests:** tests/unit/ai/test_combat_utils.py, tests/unit/test_targeting_rules.py
- [x] Write tests verifying `is_in_pdc_arc` produces same results when delegating to WeaponAbility
- [x] Update `game/ai/combat_utils.py::is_in_pdc_arc` to delegate to `WeaponAbility.check_firing_solution()`
- [x] Preserve same-position guard (distance=0 returns False)
- [x] Update test mocks to bind real check_firing_solution method
- [x] Run tests, verify all pass
**Notes:** weapon_firing_system.py seeker arc check NOT consolidated (different semantics - determines launch direction, not accept/reject). See DEC-004 in decisions.md. Removed unused `math` import from combat_utils.py.

## Task 4.2: Migrate ComponentCacheManager to SingletonMeta [Simple]
**Finding:** DUP-XL-010
**Tests:** tests/unit/entities/test_component_cache.py
- [x] Verify existing tests cover singleton behavior
- [x] Refactor `ComponentCacheManager` to use `metaclass=SingletonMeta`
- [x] Remove manual `_instance`/`_lock` pattern
- [x] Verify reset() works via SingletonMeta.reset()
- [x] Run tests, verify all pass
**Notes:** Updated test_cache_manager_has_lock to test_cache_manager_uses_singleton_meta. Removed threading import.

## Task 4.3: Remove Redundant cached_summary from ShipStatQuerier [Simple]
**Finding:** DUP-SIM-007
**Tests:** tests/unit/entities/test_ship_stat_querier.py
- [x] Verify no external callers use `ShipStatQuerier.cached_summary`
- [x] Remove `cached_summary` property from `ShipStatQuerier`
- [x] Remove associated tests
- [x] Run tests, verify all pass
**Notes:** Only 2 test methods referenced the property. Ship.cached_summary is the canonical accessor.

## Task 4.4: Assess and Clean Up Ship.layers_dict [Simple]
**Finding:** DUP-SIM-010
**Tests:** tests/unit/entities/test_ship.py
- [x] Find all callers of `Ship.layers_dict`
- [x] layers_dict is unused - removed entirely
- [x] Run tests, verify all pass
**Notes:** Property had zero callers in production or test code. Removed 16 lines of dead code.

## Completion Checklist
- [x] All Phase 4 tests pass
- [x] Full test suite passes (`pytest tests/ -n 12`): 13471 passed, 2 skipped
