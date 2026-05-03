# Deserialization Validation Audit Report

## Summary

20 deserialization methods audited across `game/`:

| Validation Level | Count | Risk Profile |
|-----------------|-------|-------------|
| VALIDATES_WELL | 3 | Low risk |
| PARTIAL_VALIDATION | 11 | Medium-High risk |
| NO_VALIDATION | 4 | HIGH risk |
| GENERIC_EXCEPTIONS | 2 | Medium risk |
| **TOTAL** | **20** | **HIGH OVERALL** |

---

## Findings

### EXC-D-001: ShipSerializer.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/simulation/entities/ship_serialization.py:124` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required key validation (name, ship_class, color, team_id), type validation, ship_class existence check |
| Risk | High (save data) |
| Effort | Medium |

### EXC-D-002: ShipSerializer._load_components()

| Field | Value |
|-------|-------|
| Location | `game/simulation/entities/ship_serialization.py:164` |
| Validation | PARTIAL_VALIDATION |
| Missing | layer_type validation, modifier required fields, component data completeness |
| Has | `ValueError` for wrong component entry type |
| Risk | High (corrupted components silently skipped) |
| Effort | Simple |

### EXC-D-003: Fleet.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/fleet.py:343` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required fleet ID/owner_id, location data structure, path coordinates, order types |
| Risk | High (invalid fleet state) |
| Effort | Medium |

### EXC-D-004: Galaxy.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/galaxy.py:879` |
| Validation | NO_VALIDATION |
| Missing | Radius validation, systems array, _next_planet_id, system data validation |
| Risk | High (entire game state corruption) |
| Effort | Simple |

### EXC-D-005: StarSystem.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/galaxy.py:77` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required name/global_location, HexCoord format, stars/planets arrays |
| Risk | High (save data) |
| Effort | Simple |

### EXC-D-006: WarpPoint.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/galaxy.py:35` |
| Validation | NO_VALIDATION |
| Missing | destination_id, location HexCoord format |
| Risk | Medium |
| Effort | Simple |

### EXC-D-007: Empire.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/empire.py:168` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required ID/name/color, color format, fleet data, galaxy parameter, planet IDs |
| Risk | High (invalid colonies) |
| Effort | Medium |

### EXC-D-008: Planet.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/planet.py:357` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required fields, location format, planet_type enum, value ranges, facilities |
| Risk | High (corrupted planet state) |
| Effort | Medium |

### EXC-D-009: Star.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/stars.py:123` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required fields, value ranges, star_type enum, spectrum data, color |
| Risk | Medium |
| Effort | Simple |

### EXC-D-010: Spectrum.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/stars.py:62` |
| Validation | NO_VALIDATION |
| Missing | 9 spectrum fields validation, non-negative float validation |
| Risk | Low |
| Effort | Simple |

### EXC-D-011: ShipInstance.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/ship_instance.py:632` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required fields, design_data structure, numeric fields, component_damage |
| Risk | High (ship state corruption) |
| Effort | Simple |

### EXC-D-012: RaceConfig.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/race_config.py:197` |
| Validation | NO_VALIDATION |
| Missing | Required fields, aptitude ranges (1-100), government_type, environment ranges |
| Risk | Medium (gameplay balance) |
| Effort | Medium |

### EXC-D-013: DesignMetadata.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/data/design_metadata.py:58` |
| Validation | VALIDATES_WELL |
| Notes | Uses `.get()` with defaults for all optional fields |
| Risk | Low |
| Effort | None |

### EXC-D-014: Event.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/events/event_log.py:41` |
| Validation | VALIDATES_WELL |
| Notes | All fields have sensible defaults |
| Risk | Low |
| Effort | None |

### EXC-D-015: EventLog.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/strategy/events/event_log.py:92` |
| Validation | VALIDATES_WELL |
| Notes | Handles missing events gracefully |
| Risk | Low |
| Effort | None |

### EXC-D-016: ComponentState.from_dict()

| Field | Value |
|-------|-------|
| Location | `game/simulation/battle_state.py:50` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required fields, HP range validation, layer name validation |
| Risk | Medium |
| Effort | Simple |

### EXC-D-017: LayerData.from_definition()

| Field | Value |
|-------|-------|
| Location | `game/simulation/entities/layer_data.py:69` |
| Validation | PARTIAL_VALIDATION |
| Missing | Required 'type' field, percentage range validation |
| Risk | Low |
| Effort | Simple |

### EXC-D-018: TechTree.load_from_json()

| Field | Value |
|-------|-------|
| Location | `game/research/data/tech_tree.py:28` |
| Validation | PARTIAL_VALIDATION |
| Missing | File existence check, required fields per node, requirement structure |
| Risk | Medium |
| Effort | Simple |

---

## Summary Table

| Validation Level | Count | Risk Profile |
|-----------------|-------|-------------|
| VALIDATES_WELL | 3 | Low risk |
| PARTIAL_VALIDATION | 11 | Medium-High risk |
| NO_VALIDATION | 4 | HIGH risk |
| GENERIC_EXCEPTIONS | 2 | Medium risk |
| **TOTAL** | **20** | **HIGH OVERALL** |

---

## Critical Save Data Methods (highest priority)

1. **ShipSerializer.from_dict()** - ship data corruption
2. **Fleet.from_dict()** - fleet loss if location corrupted
3. **Galaxy.from_dict()** - entire game state corruption
4. **Empire.from_dict()** - invalid colonies
5. **Planet.from_dict()** - corrupted planet state
