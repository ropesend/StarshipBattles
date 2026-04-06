# Phase 2: Strict Deserialization

**Objective:** Remove all `except Exception` blocks from the save/load serialization chain. Corrupt data fails the entire load with a clear error, rather than silently dropping entries.

**Key Principle:** Since saves are disposable (pre-production), it is better to fail loudly with "Save corrupted at Fleet X, Ship Y" than to load 95% of an empire's assets and silently lose the rest.

**Depends On:** Phase 1 (new exception types available)

---

## Problem Statement

Three `except Exception` blocks in the serialization chain silently skip corrupt data:

1. **`Empire.from_dict()`** ([empire.py:324](game/strategy/data/empire.py#L324)) — skips corrupt fleets
2. **`Fleet.from_dict()`** ([fleet.py:394](game/strategy/data/fleet.py#L394)) — skips corrupt ships
3. **`FleetOrderSerializer.deserialize_orders()`** ([order_serializer.py:57](game/strategy/data/order_serializer.py#L57)) — skips corrupt orders

Additionally, `Galaxy.from_dict()` ([galaxy.py:637](game/strategy/data/galaxy.py#L637)) catches `(PersistenceException, KeyError, TypeError, ValueError)` per-system. This is more targeted but still drops entire star systems silently.

## Design

### Strategy: Let Exceptions Propagate

For each broad catch site:
1. **Remove** the `except Exception` (or broad tuple) block
2. **Let exceptions propagate** to `GameSession.from_dict()`, which already has `except KeyError as e: raise PersistenceException(...) from e` patterns
3. **Add a top-level catch** in `GameSession.from_dict()` that wraps unexpected exceptions in `PersistenceException` with full context (which empire, fleet, ship index failed)

### What Exceptions Can `ShipInstance.from_dict()` Actually Raise?

From the research:
- `PersistenceException` — from `require_keys()`, `validate_non_negative()`
- `KeyError` — from missing dict keys not covered by `require_keys()`
- `TypeError` — from wrong types passed to constructors
- `ValueError` — from invalid enum values, numeric conversions

These should all propagate. The caller (`Fleet.from_dict`) should add context ("while loading ship[3] in fleet 'Alpha Fleet'") and re-raise as `PersistenceException`.

### Enhanced Error Context Pattern

```python
# BEFORE (silent drop):
for i, ship_data in enumerate(data.get('ships', [])):
    try:
        ship = ShipInstance.from_dict(ship_data, registries=registries)
        fleet.ships.append(ship)
    except Exception as e:
        logger.warning(f"Fleet {data['id']}: skipping corrupt ship[{i}]: {e}")

# AFTER (propagate with context):
for i, ship_data in enumerate(data.get('ships', [])):
    try:
        ship = ShipInstance.from_dict(ship_data, registries=registries)
        fleet.ships.append(ship)
    except (PersistenceException, KeyError, TypeError, ValueError) as e:
        raise PersistenceException(
            f"Corrupt ship data at index {i} in fleet '{data.get('id', '?')}'",
            code=ErrorCode.CORRUPT_DATA.value,
            context={"fleet_id": data.get('id'), "ship_index": i, "original_error": str(e)}
        ) from e
```

This pattern:
- Catches only expected deserialization exceptions (not `RuntimeError`, `AttributeError` from bugs)
- Adds context about WHERE in the data the corruption is
- Preserves the original exception chain via `from e`
- Lets truly unexpected exceptions (`RuntimeError`, etc.) propagate unmodified

---

## Checklist

### Tests First (TDD)

#### Fleet.from_dict() Strictness
- [ ] Write test: `Fleet.from_dict()` with one corrupt ship dict raises `PersistenceException` (not silently skips)
- [ ] Write test: `PersistenceException` context includes `fleet_id` and `ship_index`
- [ ] Write test: `PersistenceException` chains to original cause (`__cause__` is set)
- [ ] Write test: `Fleet.from_dict()` with valid data still works (regression guard)
- [ ] Write test: `Fleet.from_dict()` with ship missing required keys raises with clear message

#### Empire.from_dict() Strictness
- [ ] Write test: `Empire.from_dict()` with one corrupt fleet dict raises `PersistenceException`
- [ ] Write test: `PersistenceException` context includes `empire_id` and `fleet_index`
- [ ] Write test: `Empire.from_dict()` with valid data still works (regression guard)

#### OrderSerializer Strictness
- [ ] Write test: `deserialize_orders()` with one corrupt order dict raises `PersistenceException`
- [ ] Write test: `PersistenceException` context includes `fleet_id` and `order_index`
- [ ] Write test: `deserialize_orders()` with valid data still works (regression guard)

#### Galaxy.from_dict() Tightening
- [ ] Write test: `Galaxy.from_dict()` with one corrupt system raises `PersistenceException`
- [ ] Write test: `PersistenceException` context includes `system_index` or `system_id`
- [ ] Write test: `Galaxy.from_dict()` with valid data still works (regression guard)

#### GameSession.from_dict() Top-Level
- [ ] Write test: `GameSession.from_dict()` with corrupt fleet data raises `PersistenceException` with full path (empire → fleet → ship)
- [ ] Write test: error message is human-readable and identifies the corrupt location

- [ ] Run all new tests — confirm they fail

### Implementation

#### Fleet.from_dict()
- [ ] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [ ] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [ ] Add context: fleet_id, ship_index, original error

#### Empire.from_dict()
- [ ] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [ ] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [ ] Add context: empire_id, fleet_index, original error

#### OrderSerializer.deserialize_orders()
- [ ] Replace `except Exception as e:` with `except (PersistenceException, KeyError, TypeError, ValueError) as e:`
- [ ] Change handler from `logger.warning(skip)` to `raise PersistenceException(...) from e`
- [ ] Add context: fleet_id, order_index, original error

#### Galaxy.from_dict()
- [ ] Change from skip-and-continue to raise with context
- [ ] Add context: system_index, system_id if available, original error

- [ ] Run new tests — confirm they pass

### Existing Test Updates
- [ ] Find and update tests that previously expected silent skip behavior
- [ ] Update `test_roundtrip_fleet.py` if any tests relied on graceful degradation
- [ ] Update any save/load integration tests that injected corrupt data expecting partial loads

### Collateral: `deserialize_list()` in json_utils.py
- [ ] Review whether `deserialize_list()` (used by `StarSystem.from_dict()`) should also become strict
- [ ] Decision: YES for strategy data (fleets, ships, orders), keep resilient for cosmetic data (star names, portraits). If `StarSystem.from_dict()` uses `deserialize_list()` for planets, that needs to propagate. Add a `strict=False` parameter to `deserialize_list()` and set `strict=True` at strategy-layer call sites.
- [ ] Write tests for `deserialize_list(strict=True)` raising on first error
- [ ] Implement `strict` parameter
- [ ] Update strategy-layer callers to pass `strict=True`

### Verification
- [ ] Run full test suite — no regressions
- [ ] Manually verify that a round-trip (save → load) still works for a valid game
- [ ] Verify that loading a hand-corrupted save file produces a clear `PersistenceException`
