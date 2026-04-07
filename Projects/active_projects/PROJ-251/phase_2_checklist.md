# Phase 2: Strict Deserialization

**Objective:** Remove all `except Exception` blocks from the save/load serialization chain. Corrupt data fails the entire load with a clear error, rather than silently dropping entries.

**Key Principle:** Since saves are disposable (pre-production), it is better to fail loudly with "Save corrupted at Fleet X, Ship Y" than to load 95% of an empire's assets and silently lose the rest.

**Depends On:** Phase 1 (new exception types available)

---

## Checklist

### Tests First (TDD)

#### Fleet.from_dict() Strictness
- [x] Rewrite `test_bad_ship_skipped_fleet_loads` → `test_bad_ship_raises_persistence_exception`
- [x] Verify PersistenceException context includes `fleet_id` and `ship_index`
- [x] Existing valid-data tests still pass (regression guard)

#### Empire.from_dict() Strictness
- [x] Rewrite `test_bad_fleet_skipped_empire_loads` → `test_bad_fleet_raises_persistence_exception`
- [x] Verify PersistenceException context includes `empire_id` and `fleet_index`
- [x] Existing valid-data tests still pass (regression guard)

#### OrderSerializer Strictness
- [x] Rewrite `test_corrupt_order_skipped_with_warning` → `test_corrupt_order_raises_persistence_exception`
- [x] Rewrite `test_unknown_order_type_skipped` → `test_unknown_order_type_raises_persistence_exception`
- [x] Verify PersistenceException context includes `fleet_id` and `order_index`

#### Galaxy.from_dict() Tightening
- [x] Rewrite `test_system_missing_coord_skipped` → `test_system_missing_coord_raises`
- [x] Rewrite `test_system_missing_system_key_skipped` → `test_system_missing_system_key_raises`
- [x] Rewrite `test_bad_system_data_skipped_galaxy_loads` → `test_bad_system_data_raises`

#### StarSystem.from_dict() Strictness (via deserialize_list strict=True)
- [x] Rewrite `test_bad_star_skipped_system_loads` → `test_bad_star_raises_persistence_exception`
- [x] Rewrite `test_bad_planet_skipped_system_loads` → `test_bad_planet_raises_persistence_exception`
- [x] Rewrite `test_bad_warp_point_skipped_system_loads` → `test_bad_warp_point_raises_persistence_exception`

#### Planet.from_dict() Strictness (via deserialize_list strict=True)
- [x] Rewrite `test_bad_facility_skipped_with_warning` → `test_bad_facility_raises_persistence_exception`
- [x] Rewrite `test_bad_population_skipped_with_warning` → `test_bad_population_raises_persistence_exception`

- [x] Run all new tests — confirm they fail before implementation

### Implementation

#### Fleet.from_dict()
- [x] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [x] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [x] Add context: fleet_id, ship_index, original error

#### Empire.from_dict()
- [x] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [x] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [x] Add context: empire_id, fleet_index, original error

#### OrderSerializer.deserialize_orders()
- [x] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [x] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [x] Add context: fleet_id, order_index, original error

#### Galaxy.from_dict()
- [x] Change from skip-and-continue to raise with context
- [x] Add context: system_index, original error

### Collateral: `deserialize_list()` in json_utils.py
- [x] Add `strict=False` parameter to `deserialize_list()`
- [x] Write tests for `strict=True` raising on first error (4 tests in `TestDeserializeListStrict`)
- [x] Implement `strict` parameter
- [x] Update strategy-layer callers to pass `strict=True`:
  - [x] `StarSystem.from_dict()` — stars, warp_points, planets, storms
  - [x] `Planet.from_dict()` — facilities, populations

### Collateral: Pre-existing bug fix
- [x] Fixed syntax error in `strategy_session_facade.py:554,570` (escaped `\"\"\"` → `"""`)

### Verification
- [x] Run full test suite — 14615/14616 passed (1 flaky pre-existing test ordering issue in `test_pursuers_registered_after_load` — passes in isolation, fails in specific shard ordering)
- [x] Valid save/load round-trip still works (303 save_load tests pass)

**Notes:** Changed 6 files in `game/` (fleet.py, empire.py, order_serializer.py, galaxy.py, planet.py, json_utils.py) and 6 test files. Total: 12 old "skip" tests rewritten to expect `PersistenceException`, 4 new strict deserialize_list tests added. Also fixed pre-existing syntax error in `strategy_session_facade.py` that was blocking all strategy test imports.
