# PROJ-260 File Manifest

> Generated during project planning. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

### Production Code (Modified)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/entities/ship.py` | Production | Remove implementation logic, add facade methods to new delegates |
| `game/simulation/entities/ship_stats.py` | Production | `_initialize_resources()` calls resource manager instead of Ship attrs |

### Production Code (New)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/entities/ship_layer_manager.py` | Production | New delegate: layer init, hull equip, radius calc |
| `game/simulation/entities/ship_resource_manager.py` | Production | New delegate: ResourceRegistry owner, resource init, consumption attrs |

### Test Code (New)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/simulation/entities/test_ship_layer_manager.py` | Test | Tests for ShipLayerManager delegate |
| `tests/unit/simulation/entities/test_ship_resource_manager.py` | Test | Tests for ShipResourceManager delegate |

### Test Code (Potentially Modified)

| File | Type | Notes |
|------|------|-------|
| `tests/unit/entities/test_ship.py` | Test | May need updates if Ship init changes |
| `tests/unit/simulation/entities/test_ship_resource_stat.py` | Test | May need updates if get_resource_stat() interface changes |
| `tests/unit/simulation/systems/test_ship_stats_calculator_phases.py` | Test | May need updates for _initialize_resources() change |

### Documentation (Potentially Modified)

| File | Type | Notes |
|------|------|-------|
| `docs/01_ARCHITECTURE.md` | Docs | Update if Ship decomposition section exists |
| `docs/02_PATTERNS.md` | Docs | Update Facade/Delegate pattern with new delegates |

### Read-Only Reference (Not Modified)

| File | Type | Notes |
|------|------|-------|
| `game/simulation/entities/layer_data.py` | Production | LayerData dataclass -- used by ShipLayerManager |
| `game/simulation/systems/resource_manager.py` | Production | ResourceRegistry/ResourceState -- used by ShipResourceManager |
| `game/simulation/entities/ship_component_manager.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_combat_manager.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_combat_engine.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_stat_querier.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_validator_helper.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_formation.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_physics.py` | Production | Existing delegate pattern reference |
| `game/simulation/entities/ship_serialization.py` | Production | Existing delegate pattern reference |

## Conflict Zones

Files with HIGH conflict risk if other projects modify them simultaneously:

| File | Risk | Reason |
|------|------|--------|
| `game/simulation/entities/ship.py` | HIGH | Primary target -- every Ship PROJ touches this |
| `game/simulation/entities/ship_stats.py` | MEDIUM | `_initialize_resources()` changes |
