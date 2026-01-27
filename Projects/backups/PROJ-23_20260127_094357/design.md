# PROJ-23: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Bug Discovery
CRU_1 design cannot use warp drive while CRU_2 can, despite both being Cruiser-class ships with identical warp drive components.

**CRU_1**: 1 battery at size 20.0 (expected: 40,000 energy)
**CRU_2**: 10 batteries at size 1.0 (expected: 20,000 energy)

### Root Cause
`ShipStatsService.calculate_stats()` reads component ability values from the **registry** (base component definition) without applying the **modifiers** specified in the design's component entry.

**Bug Location**: `game/strategy/services/ship_stats_service.py:110-135`

```python
# Current code reads from registry only - ignores design modifiers
abilities = getattr(comp_def, 'abilities', {}) or {}

# comp_entry contains modifiers that are NEVER applied:
# {'id': 'battery', 'modifiers': [{'id': 'simple_size_mount', 'value': 20.0}]}
```

### Impact Calculation
| Design | Configuration | Expected Capacity | Calculated Capacity |
|--------|---------------|-------------------|---------------------|
| CRU_1 | 1 battery × size 20 | 40,000 energy | **2,000** (base only) |
| CRU_2 | 10 batteries × size 1 | 20,000 energy | **20,000** (correct) |

Warp drive energy cost for Cruiser (16,000t hull): `5 * (16000 ** (2/3))` ≈ **3,175 energy**

- CRU_1: 2,000 < 3,175 → `has_warp_capability()` returns **False** (BUG)
- CRU_2: 20,000 ≥ 3,175 → `has_warp_capability()` returns **True** (correct)

---

## Swarm Findings Summary

### Architecture Analysis

#### Modifier System Structure
The modifier system uses a **formula-based V2 format**:

```json
{
  "id": "modifier_id",
  "name": "Display Name",
  "param": {"name": "Scale", "type": "linear", "min": 1, "max": 1024},
  "effects": [
    {"stat": "mass_mult", "formula": "param"},
    {"stat": "hp_mult", "formula": "param"},
    {"stat": "capacity_mult", "formula": "param"}
  ]
}
```

#### Stats Dictionary Structure (from Component._calculate_modifier_stats)
```python
stats = {
    # Multiplicative stats (defaults = 1.0)
    'mass_mult': 1.0, 'hp_mult': 1.0, 'damage_mult': 1.0,
    'range_mult': 1.0, 'cost_mult': 1.0, 'thrust_mult': 1.0,
    'turn_mult': 1.0, 'strategic_mult': 1.0, 'energy_gen_mult': 1.0,
    'capacity_mult': 1.0, 'crew_capacity_mult': 1.0,
    'life_support_capacity_mult': 1.0, 'consumption_mult': 1.0,
    'reload_mult': 1.0, 'endurance_mult': 1.0,
    'projectile_hp_mult': 1.0, 'projectile_damage_mult': 1.0,
    'crew_req_mult': 1.0,

    # Additive stats (defaults = 0.0)
    'mass_add': 0.0, 'arc_add': 0.0, 'accuracy_add': 0.0,
    'projectile_stealth_level': 0.0,

    # Set stats (defaults = None)
    'arc_set': None,

    # Properties dict
    'properties': {}
}
```

### Key Patterns to Reuse

- **Stats Dict Template**: `component.py:548-574` - exact template used by Component
- **Modifier Loading**: `component.py:125-137` - loading modifiers from data
- **Modifier Application**: `component.py:576-577` - `apply_modifier_effects(m.definition, m.value, stats)`
- **Multiplier Application**: `component.py:588-591` - `mass = (base_mass + mass_add) * mass_mult`

### Dependencies & Risks

1. **Output format must be preserved** - ShipStatsService returns 8 dictionary keys with exact types
   - `max_hp`: int
   - `mass`: float
   - `resource_storage`: Dict[str, float]
   - `resource_consumption_per_hex`: Dict[str, float]
   - `resource_consumption_per_turn`: Dict[str, float]
   - `warp_resource_costs`: Dict[str, float]
   - `strategic_movement`: float
   - `warp_max_tonnage`: int

2. **71 existing tests** in `test_ship_stats_service.py` - must all pass

3. **6 downstream consumers** depend on output format:
   - `ShipInstance.get_calculated_stats()` - primary consumer
   - `ShipInstance.get_hp_percentage()` - uses max_hp
   - `ShipInstance.get_resource_percentage()` - uses resource_storage
   - `Fleet.filter_by_warp_capable()` - uses warp_max_tonnage
   - `ShipStatsService.has_warp_capability()` - multi-field validation
   - `TurnEngine._disable_resource_consumers()` - accesses design structure

4. **No circular import risks** - `get_modifier_registry` from core.registry is safe

### Opportunities Discovered

- `apply_modifier_effects()` already exists in `modifiers.py` - can reuse directly
- Pattern is already proven in `modifier_service.py` and `component.py`
- Core registry has no upstream imports (terminal dependency)

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Selected Approach: Option C (Shared Modifier Logic)

Extract modifier calculation into pure functions used by both Component and ShipStatsService.

**Why not Option A (Duplicate in ShipStatsService)?**
- Creates tech debt - must maintain two implementations
- Adding new modifiers requires changes in two places
- Risk of drift between Component and ShipStatsService behavior

**Why not Option B (Instantiate Components)?**
- Performance overhead for large fleets (20,000 Component instantiations for 1000 ships)
- Memory usage concerns
- Component lifecycle complexity

**Why Option C?**
- Single source of truth - one implementation
- Best performance (pure functions, no object instantiation)
- Best maintainability (new modifiers "just work")
- Testable (pure functions are easy to unit test)

### Architecture

```
game/simulation/components/modifiers.py
├── apply_modifier_effects()          # EXISTING
├── get_default_stat_multipliers()    # NEW - returns default stats dict
└── calculate_stat_multipliers()      # NEW - pure function for modifier math

Component._calculate_modifier_stats()
└── calls calculate_stat_multipliers()

ShipStatsService.calculate_stats()
└── calls calculate_stat_multipliers()
```
