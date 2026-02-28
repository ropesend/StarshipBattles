# PROJ-75: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Resource Systems
- **Ship Resources** (combat layer): fuel, energy, ammo - fully functional with `ResourceRegistry` pattern in `game/simulation/systems/resource_manager.py`
- **Planetary Resources**: Metals, Organics, Vapors, Radioactives, Exotics - stored on planets with quantity/quality but NOT used
- **Build Queues**: Currently instant (1 turn), free (no costs), no resource consumption
- **Empire System**: No global resource pool exists

### Key Findings
1. `Empire.resource_pool` is completely missing - needs to be created
2. `ProductionEngine` has NO resource deduction - builds are free
3. Turn order undefined for harvesting/maintenance phases
4. `Component.resource_cost` already exists in JSON but is unused
5. `ResourceHarvesterAbility` exists in `harvester.py` but isn't integrated into turn loop

## Swarm Findings Summary

### Architecture
- Empire needs new `empire_resources` dict for global resource pool
- Create new `EmpireHarvesterAbility` and `EmpireStorageAbility` following existing patterns
- ProductionEngine needs per-tick resource consumption
- Create new `MaintenanceEngine` for facility/ship upkeep
- Components already have `resource_cost` field in JSON - just needs to be used

### Key Patterns to Reuse
- **ResourceConsumption pattern**: `game/simulation/components/abilities/resources.py:8-229` - update() per-tick, recalculate() for modifiers
- **ResourceManagementEngine pattern**: `game/strategy/engine/resource_management_engine.py:57-98` - spreads per-turn costs over 100 ticks
- **PopulationEngine pattern**: `game/strategy/engine/population_engine.py:35-120` - nested iteration for per-turn calculations
- **Ability aggregation**: Scan `design_data['abilities']` for facility abilities

### Dependencies & Risks
1. **Empire serialization** (12+ files) - Safe: to_dict/from_dict pattern handles new fields
2. **ProductionEngine** (9+ files depend) - Medium risk: must maintain backwards compatibility
3. **Planet.resources** - Safe: read-only from harvesting perspective
4. **Turn order** - Critical: must define phase ordering carefully

### Opportunities Discovered
- `Component.resource_cost` already parsed - no loader changes needed
- `ResourceHarvesterAbility` already defined - just needs integration
- TurnEngine dependency injection pattern makes adding new engines clean

## Design Decisions

### Turn Phase Order (NEW)
```
TURN START:
  1. HarvestingEngine.recalculate_storage()
  2. HarvestingEngine.process_harvesting()
  3. MaintenanceEngine.process_maintenance()

SUBTURN LOOP (100 ticks):
  4. ResourceManagementEngine (ship consumption - existing)
  5. ProductionEngine.process_construction_tick() - NEW
  6. FleetOrderProcessor (existing)
  7. FleetMovementEngine (existing)
  8. ConflictResolutionEngine (existing)

TURN END:
  9. ProductionEngine.process_production() - completion only
  10. PopulationEngine (existing)
```

### Data Flow

**Harvesting Flow:**
```
Planet.resources[X].quantity (source)
    │
    ├─ HarvestingEngine scans facilities
    │  └─ Find EmpireHarvesterAbility instances
    │
    ├─ Calculate: harvest = base_rate * quality
    │
    ├─ Deduct from planet: max(0, quantity - harvest)
    │
    └─ Add to empire: resource_pool[X] += harvest
       └─ Respect max_storage[X] limit
```

**Production Flow:**
```
Empire.resource_pool[X] (source)
    │
    ├─ Queue item added with total_cost calculated
    │  └─ cost_per_tick = total_cost / turns / 100
    │
    ├─ Each tick: consume cost_per_tick from pool
    │  └─ If insufficient: pause (don't decrement turns)
    │
    └─ When complete: spawn ship/complex
```

**Maintenance Flow:**
```
Empire.resource_pool[X] (source)
    │
    ├─ Calculate: maintenance = 5% of build_cost per turn
    │
    ├─ Check: has_resources(maintenance)?
    │  ├─ Yes: consume and continue
    │  └─ No: mark for scuttling
    │
    └─ Execute scuttles (one-pass, no cascade)
```

### Component JSON Structure

**Harvester Component:**
```json
{
    "id": "metals_harvester",
    "name": "Metals Extractor",
    "type": "Harvester",
    "mass": 500,
    "hp": 1000,
    "allowed_vehicle_types": ["Planetary Complex"],
    "abilities": {
        "EmpireHarvesterAbility": {
            "resource_type": "Metals",
            "base_rate": 100.0
        }
    },
    "major_classification": "Infrastructure",
    "resource_cost": {
        "Metals": 1000,
        "Radioactives": 200
    }
}
```

**Storage Component:**
```json
{
    "id": "resource_vault_metals",
    "name": "Metals Vault",
    "type": "Storage",
    "mass": 300,
    "hp": 500,
    "allowed_vehicle_types": ["Planetary Complex"],
    "abilities": {
        "EmpireStorageAbility": {
            "resource_type": "Metals",
            "capacity": 10000
        }
    },
    "major_classification": "Infrastructure",
    "resource_cost": {
        "Metals": 500,
        "Organics": 100
    }
}
```

### Risk Mitigations

| Risk | Approach |
|------|----------|
| Negative planet resources | Clamp: `max(0, quantity - harvest)` |
| Storage overflow | Return overflow amount, log excess |
| Build pause/resume | Track `is_paused` flag, check each tick |
| Rounding errors | Use float, reconcile at turn end |
| Old save compatibility | Safe defaults in from_dict() |
| Scuttle cascade | One-pass: collect all failures, then execute |
| Empty empire | Define defeat condition when no colonies and no fleets |

See [decisions.md](decisions.md) for the full log with rationale.
