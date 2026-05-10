# PROJ-354 Test Impact Analysis

## 1. Existing tests for superweapon_order_processor

**Unit tests:**
- **`tests/unit/strategy/engine/test_superweapon_order_processor.py`** (~1,232 lines) — per-weapon test classes:
  - `TestProcessImplodePlanet`: planet_removed, ship_not_consumed, event_logged
  - `TestProcessStellerateStar`: stars/planets/all_fleets_destroyed
  - `TestProcessOpenWarpPoint`: bidirectional warp_points, ship_not_consumed
  - `TestProcessCloseWarpPoint`: both_ends_removed, rejects_wrong_sector
  - `TestProcessCreateDysonSphere`: star_removed, planets_removed, sphere_created
  - `TestProcessSelfDestruct`: specified_ships_removed, event_logged
  - `TestNoShipFallback`: cancellation when no ability ship
  - `TestEnemyColonyCleanup`: cross-empire colony list updates
- **`test_superweapon_edge_cases.py`** — error paths, missing targets.
- **`test_superweapon_order_processor_gaps.py`** — stabilizer-blocking (OBS-004/005/006), empty-fleet cleanup for SELF_DESTRUCT.

**Integration:**
- **`tests/integration/strategy/test_superweapon_integration.py`** (~622 lines) — full flows for all 6 order types + serialization round-trip.

## 2. Coverage by superweapon

| Type | Happy Path | Stabilizer Block | Missing Ship | Notes |
|------|-----------|------------------|--------------|-------|
| IMPLODE_PLANET | ✓ | ✓ | ✓ | Enemy colony cleanup |
| STELLERATE_STAR | ✓ | ✓ | ✓ | Suicide consumption |
| OPEN_WARP_POINT | ✓ | ✓ | ✓ | Direction math |
| CLOSE_WARP_POINT | ✓ | ✓ | ✓ | Legacy back-compat |
| CREATE_DYSON_SPHERE | ✓ | ✓ | ✓ | radius_hexes=6, race fallback |
| SELF_DESTRUCT | ✓ | N/A | ✓ | Selected ships only |

## 3. SuperweaponValidator tests
**File:** `tests/unit/strategy/validation/test_superweapon_validator.py` (~651 lines) — TestFindShipWithAbility + per-type Validate* classes; happy + ability-missing + state-check coverage.

## 4. Stabilizer registry pattern tests
- **`tests/unit/strategy/services/test_stabilizer_registry.py`** (~150+ lines) — early-return paths, positive matches, iteration order.
- **`tests/integration/strategy/test_stabilizer_blocks_superweapon.py`** — real facility designs, end-to-end registry+scanner integration.

These are the patterns PROJ-354 should mirror for SuperweaponSpec contract tests.

## 5. Coverage gaps

1. **Order pop semantics not unified:** per-superweapon tests for success/failure/missing-ship outcomes lack a unified matrix. Need `TestOrderPopSemantics` class (6 weapons × 3 outcomes).
2. **Event payload contents:** only IMPLODE_PLANET and SELF_DESTRUCT validate event payload structure. Missing: STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE.
3. **Component-ability contract:** no integration test asserts `SuperweaponSpec.ability_name` matches an actual component registry entry.

## 6. Recommended new contract test
```python
class TestSuperweaponSpecContract:
    def test_all_specs_have_matching_component(self, component_registry): ...
    def test_all_specs_have_valid_event_type(self): ...        # Asserts spec.event_type ∈ EventType
    def test_all_specs_have_valid_stabilizer_scope(self): ...   # Scopes ∈ {system, sector, empire}
```
File path: `tests/unit/strategy/services/test_superweapon_registry_contract.py`.

## 7. Reusable fixtures

| Fixture | Path |
|---------|------|
| Fleet with ability ship | `test_superweapon_order_processor.py:65-75` |
| Real Galaxy/StarSystem | `test_superweapon_integration.py:96-120` |
| Component registry | `test_superweapon_validator.py:62-86` |
| Stabilizer registry pattern | `test_stabilizer_registry.py` |

## Summary
Coverage is mature on happy paths; the order-pop matrix and event-payload assertions are the gaps PROJ-354 should fill before refactoring. The stabilizer_registry contract tests are the model for the new SuperweaponSpec contract test.
