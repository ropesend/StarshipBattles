# Test Impact Analysis Report

## Summary

126 test assertions reference generic exception types:

| Exception Type | Total | MUST_UPDATE | KEEP_AS_IS | REVIEW |
|---------------|-------|-------------|------------|--------|
| ValueError | 43 | 26 | 17 | 0 |
| RuntimeError | 6 | 3 | 3 | 0 |
| TypeError | 72 | 51 | 21 | 0 |
| KeyError | 2 | 0 | 2 | 0 |
| Exception | 3 | 0 | 3 | 0 |
| **TOTAL** | **126** | **80** | **46** | **0** |

---

## ValueError Tests - MUST_UPDATE (26 tests)

| ID | Location | Test Method | Pattern | Target | Match | Effort |
|----|----------|-------------|---------|--------|-------|--------|
| EXC-T-001 | `tests/unit/assets/test_asset_manager_resolutions.py:59` | `test_invalid_size_raises_error()` | `pytest.raises(ValueError, match="Invalid planet image size: 999")` | Tests `game/assets/asset_manager.py` | ValidationException | Simple |
| EXC-T-002 | `tests/integration/test_strategic_abilities.py:268` | `test_warp_jump_rejects_non_self_scope()` | `pytest.raises(ValueError)` | Tests `game/simulation/components/abilities/propulsion.py` | ValidationException, match="does not support scope" | Simple |
| EXC-T-003 | `tests/unit/abilities/test_warp_jump.py:108` | `test_warp_jump_rejects_system_scope()` | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-004 | `tests/unit/abilities/test_strategic_movement.py:123` | `test_strategic_movement_invalid_scope_raises()` | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-005 | `tests/unit/abilities/test_colonize_planet.py:135` | `test_colonize_invalid_scope_raises()` | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-006 | `tests/unit/abilities/test_ability_layer_scope.py:174` | `test_invalid_scope_string_raises()` | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-007 | `tests/unit/modifiers/test_ability_stat_binding.py:80` | `test_invalid_operation_raises()` | `pytest.raises(ValueError, match="Invalid operation")` | ValidationException | Simple |
| EXC-T-011 | `tests/unit/simulation/components/abilities/test_stat_keys.py:90` | | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-012 | `tests/unit/simulation/components/abilities/test_ability_base.py:111` | | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-013 | `tests/unit/simulation/components/abilities/test_ability_base.py:225` | | `pytest.raises(ValueError, match="invalid scope")` | ValidationException | Simple |
| EXC-T-014 | `tests/unit/simulation/components/abilities/test_ability_base.py:231` | | `pytest.raises(ValueError, match="does not support scope")` | ValidationException | Simple |
| EXC-T-015 | `tests/unit/simulation/components/abilities/test_ability_base.py:706` | | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-016 | `tests/unit/simulation/components/abilities/test_ability_base.py:712` | | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-017 | `tests/unit/simulation/components/abilities/test_colonize_harvester.py:132` | | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-018 | `tests/unit/simulation/entities/test_projectile.py:199` | | `pytest.raises(ValueError, match="unknown_type")` | ValidationException | Simple |
| EXC-T-019 | `tests/unit/simulation/entities/test_ship_serialization.py:485` | | `pytest.raises(ValueError, match="Component entry must be dict")` | ValidationException | Simple |
| EXC-T-020 | `tests/unit/simulation/managers/test_battle_state_manager.py:143` | | `pytest.raises(ValueError, match="Invalid")` | ValidationException or StateException | Simple |
| EXC-T-021 | `tests/unit/simulation/systems/test_battle_engine_tick.py:988` | | `pytest.raises(ValueError, match="ai_factory")` | ValidationException | Simple |
| EXC-T-022 | `tests/unit/strategy/generation/density/test_density_map.py:24` | | `pytest.raises(ValueError, match="empty DensityMap")` | ValidationException | Simple |
| EXC-T-023 | `tests/unit/strategy/generation/density/test_density_map.py:173` | | `pytest.raises(ValueError, match="Unknown primitive type")` | ValidationException | Simple |
| EXC-T-024 | `tests/unit/strategy/generation/density/test_density_map.py:179` | | `pytest.raises(ValueError, match="must contain")` | ValidationException | Simple |
| EXC-T-025 | `tests/unit/strategy/generation/density/test_density_map.py:189` | | `pytest.raises(ValueError, match="must have a 'type'")` | ValidationException | Simple |
| EXC-T-026 | `tests/unit/strategy/generation/density/test_layout_loader.py:42` | | `pytest.raises(ValueError, match="Unknown layout type")` | ValidationException | Simple |
| EXC-T-027-029 | `tests/unit/strategy/test_game_config.py:127,134,219` | game_config tests | `pytest.raises(ValueError)` | ValidationException | Simple |
| EXC-T-030 | `tests/unit/ui/services/test_vehicle_class_service.py:17` | | `pytest.raises(ValueError, match="registry_provider is required")` | ValidationException | Simple |
| EXC-T-031-032 | `tests/unit/ui/test_new_game_setup.py:215,222` | build_game_config tests | `pytest.raises(ValueError)` | ValidationException | Simple |

---

## RuntimeError Tests - MUST_UPDATE (3 tests)

| ID | Location | Pattern | Target | Effort |
|----|----------|---------|--------|--------|
| EXC-T-034 | `tests/unit/simulation/entities/test_ship_loader.py:121` | `pytest.raises(RuntimeError, match="Critical Error")` | MissingResourceException | Medium |
| EXC-T-035 | `tests/unit/simulation/entities/test_ship_loader.py:353` | `pytest.raises(RuntimeError, match="Critical Error")` | MissingResourceException | Medium |
| EXC-T-036 | `tests/unit/simulation/factories/test_ai_factory.py:65` | `pytest.raises(RuntimeError, match="set_grid")` | StateException | Simple |
| EXC-T-037 | `tests/unit/simulation/managers/test_battle_state_manager.py:53` | `pytest.raises(RuntimeError, match="No engine")` | StateException | Simple |

---

## TypeError Tests - MUST_UPDATE (51 tests)

All follow the DI validation pattern: `pytest.raises(TypeError, match="X is required")`

| Test File | Count | Target | Effort |
|-----------|-------|--------|--------|
| `tests/unit/builder/test_ship_validator_di.py` | 2 | ValidationException | Simple |
| `tests/unit/entities/test_ship_di.py` | 2 | ValidationException | Simple |
| `tests/unit/entities/test_component_di.py` | 4 | ValidationException | Simple |
| `tests/unit/core/test_service_injection.py` | 2 | ValidationException | Simple |
| `tests/unit/simulation/validation/test_ship_validator_rules.py` | 2 | ValidationException | Simple |
| `tests/unit/simulation/entities/test_ship_serialization.py` | 1 | ValidationException | Simple |
| `tests/unit/simulation/services/test_vehicle_design_service.py` | 1 | ValidationException | Simple |
| `tests/unit/simulation/services/test_modifier_service.py` | 1 | ValidationException | Simple |
| `tests/unit/strategy/ship_stats/test_edge_cases.py` | 1 | ValidationException | Simple |
| `tests/unit/systems/test_event_bus.py` | 3 | ValidationException | Simple |
| `tests/unit/simulation/components/test_component_health_manager.py` | 3 | ValidationException | Simple |
| `tests/unit/simulation/combat/test_battle_mode_handlers.py` | 1 | ValidationException | Simple |
| `tests/unit/strategy/engine/test_resupply_engine.py` | 1 | ValidationException | Simple |
| `tests/unit/strategy/interfaces/test_engine_interfaces.py` | 6 | ValidationException | Simple |
| `tests/unit/strategy/interfaces/test_battle_resolver.py` | 2 | ValidationException | Simple |
| `tests/unit/strategy/resource_management_engine/test_initialization.py` | 1 | ValidationException | Simple |

All are bulk pattern changes: `TypeError` to `ValidationException`.

---

## KEEP_AS_IS Tests (46 tests)

These tests correctly use generic exceptions because they test stdlib or language-level behavior:

| Category | Count | Rationale |
|----------|-------|-----------|
| `ValueError` from `int()`/`float()`/`datetime` stdlib | 17 | Standard library raises these |
| `TypeError` from abstract class instantiation | 6 | Python ABC mechanism |
| `TypeError` from HexCoord math operations | 10 | Operator overloading type checks |
| `TypeError` from other stdlib | 5 | Standard library raises these |
| `KeyError` from dict/enum access | 2 | Standard Python behavior |
| `Exception` from attrs frozen | 3 | attrs library behavior |
| `RuntimeError`/`ValueError` from decorator propagation | 3 | Decorator mechanism |

---

## Summary Table

| Exception Type | Total | MUST_UPDATE | KEEP_AS_IS | REVIEW |
|---------------|-------|-------------|------------|--------|
| ValueError | 43 | 26 | 17 | 0 |
| RuntimeError | 6 | 3 | 3 | 0 |
| TypeError | 72 | 51 | 21 | 0 |
| KeyError | 2 | 0 | 2 | 0 |
| Exception | 3 | 0 | 3 | 0 |
| **TOTAL** | **126** | **80** | **46** | **0** |

---

## Migration Effort Estimate

| Category | Count | Estimated Time |
|----------|-------|---------------|
| Simple updates (change exception type + match pattern) | 77 | ~2-3 hours |
| Medium updates (choose exception type) | 3 | ~30 min |
| **Total** | **80** | **~3-4 hours** |

**IMPORTANT:** You MUST update tests in the same commit/phase as the corresponding source code changes to keep tests green throughout the migration.
