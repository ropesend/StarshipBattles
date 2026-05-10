# Phase 1: Add `unregister_ship()` and Wire into `remove_ship()`

**Status:** Complete

## Tasks

### Task 1.1: Write unit tests for `unregister_ship()` [Simple]
**Tests:** `tests/unit/simulation/combat/test_fleet_aura_unregister.py`
- [x] Test that `unregister_ship()` removes providers belonging to the ship from `_providers`
- [x] Test that `unregister_ship()` calls `_recalculate()` after removal
- [x] Test that teammates no longer receive bonuses from unregistered ship
- [x] Test that unregistering a ship with no aura abilities is a no-op (no crash)
- [x] Test that unregistering a ship from a different team doesn't affect that team's bonuses
- [x] Test round-trip: register then unregister returns to original state
**Notes:** 6 tests written following exact pattern from `test_fleet_aura_register.py`. All confirmed failing before implementation (AttributeError — method didn't exist).

### Task 1.2: Implement `unregister_ship()` on `FleetAuraManager` [Simple]
**Tests:** `tests/unit/simulation/combat/test_fleet_aura_unregister.py`
- [x] Add `unregister_ship(ship, all_ships)` method
- [x] Remove all `AuraProvider` entries where `provider.ship is ship`
- [x] Call `_recalculate(all_ships)` after removal
- [x] Mark aura cache dirty
**Notes:** Added after `register_ship()` at line ~137. Uses list comprehension to filter providers, sets `_providers_dirty = True`, then calls `_recalculate(all_ships)`.

### Task 1.3: Wire `unregister_ship()` into `BattleEngine.remove_ship()` [Simple]
**Tests:** `tests/unit/simulation/combat/test_fleet_aura_unregister.py`
- [x] Call `self.aura_manager.unregister_ship(ship, self.ships)` in `remove_ship()` after removal from `self.ships`
- [x] Verify integration: ship removal triggers aura cleanup
**Notes:** Added call after `self.ships.remove(ship)` and before AI controller cleanup. Passes `self.ships` (which no longer contains the removed ship). All 5 existing `remove_ship` tests still pass. Full suite: 14185 passed.
