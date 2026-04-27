# PROJ-260: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Ship.py is 713 lines with 9 existing delegates already extracted. The remaining logic clusters
into two cohesive groups that can be extracted using the same facade/delegate pattern:

1. **Layer management** -- `_initialize_layers()`, `_equip_default_hull()`, layer radius
   recalculation, and the layer-related portion of `change_class()`.

2. **Resource management** -- The `resources` (ResourceRegistry) instance, initialization
   tracking (`_resources_initialized`, `_prev_max_resources`, `_prev_max_shields`), resource
   consumption attributes, and the `get_resource_stat()` accessor.

Both groups are self-contained: they read/write Ship attributes but have no dependencies on
each other or on the existing delegates (except that ShipStatsCalculator calls
`_initialize_resources()` which reads Ship resource state).

## Architecture

### ShipLayerManager

**File:** `game/simulation/entities/ship_layer_manager.py`

**Responsibilities (what moves OUT of Ship):**
- `_initialize_layers()` -- Build `self.layers` dict from vehicle class definition
- Layer radius recalculation (area-proportional to mass capacity)
- `_equip_default_hull()` -- Auto-equip the default hull component for a vehicle class
- Layer-related portion of `change_class()` -- Reinitialize layers after class change

**What stays on Ship:**
- `self.layers: Dict[LayerType, LayerData]` -- Remains a Ship attribute (too many direct readers)
- `self.ship_class: str` -- Identity attribute
- `self.max_mass_budget: float` -- Used by many subsystems

**Delegation pattern:**
```python
# Ship.__init__
self._layer_manager = None  # Lazy init

@property
def layer_manager(self):
    if self._layer_manager is None:
        from .ship_layer_manager import ShipLayerManager
        self._layer_manager = ShipLayerManager(self)
    return self._layer_manager

def _initialize_layers(self) -> None:
    self.layer_manager.initialize_layers()

def _equip_default_hull(self, class_def: dict) -> None:
    self.layer_manager.equip_default_hull(class_def)
```

**Constructor integration:**
Since `_initialize_layers()` and `_equip_default_hull()` are called during `__init__`, the
layer manager must be created eagerly (not lazily) or the methods must be called through the
property. Phase 1 analysis will determine the best approach -- likely eager initialization
since layers are always needed.

### ShipResourceManager

**File:** `game/simulation/entities/ship_resource_manager.py`

**Responsibilities (what moves OUT of Ship):**
- Owns `ResourceRegistry` instance (currently `ship.resources`)
- Owns initialization tracking: `_resources_initialized`, `_prev_max_resources`, `_prev_max_shields`
- `get_resource_stat()` accessor method
- Resource consumption attributes: `fuel_consumption`, `ammo_consumption`, `energy_consumption`,
  `potential_fuel_consumption`, `potential_ammo_consumption`, `potential_energy_consumption`
- `initialize_resources()` logic (currently in ShipStatsCalculator._initialize_resources)

**What stays on Ship:**
- `ship.resources` property -- Facade accessor that delegates to ShipResourceManager
- Resource-related combat stats set by ShipStatsCalculator: `max_shields`, `current_shields`,
  `shield_regen_rate`, `shield_regen_cost` (these are combat stats, not resource management)

**Delegation pattern:**
```python
# Ship.__init__
self._resource_manager = None  # Lazy init

@property
def resource_manager(self):
    if self._resource_manager is None:
        from .ship_resource_manager import ShipResourceManager
        self._resource_manager = ShipResourceManager(self)
    return self._resource_manager

@property
def resources(self) -> ResourceRegistry:
    return self.resource_manager.registry

def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
    return self.resource_manager.get_resource_stat(resource_name, stat_type)
```

**ShipStatsCalculator integration:**
`ShipStatsCalculator._initialize_resources()` currently reads and writes several Ship attributes
(`_prev_max_resources`, `_prev_max_shields`, `_resources_initialized`, `resources`, `current_shields`,
`max_shields`). After extraction, it will call `ship.resource_manager.initialize_resources()`
which encapsulates all that state.

### Integration with Existing Delegates

The new managers integrate cleanly because they follow the same pattern as all 9 existing delegates:

1. **ShipComponentManager** -- No changes. Accesses `ship.layers` directly (remains on Ship).
2. **ShipCombatManager** -- No changes. Calls `ship.resources.update()` which will now route
   through the facade property.
3. **ShipCombatEngine** -- No changes. Reads shield/resource values from Ship attributes.
4. **ShipStatsCalculator** -- Minor change: `_initialize_resources()` calls the resource
   manager instead of manipulating Ship attributes directly.
5. **ShipSerializer** -- No changes. Serializes `ship.layers` which remains on Ship.
6. **ShipStatQuerier** -- No changes.
7. **ShipValidatorHelper** -- No changes.
8. **ShipFormation** -- No changes.
9. **ShipPhysicsMixin** -- No changes.

### Line Count Projection

Current Ship.py: 713 lines

Estimated removals:
- `_initialize_layers()` body: ~58 lines (364-422)
- `_equip_default_hull()` body: ~17 lines (189-206)
- Resource instance variables and initialization: ~10 lines (119-123)
- Resource consumption attributes: ~8 lines (147-153)
- `get_resource_stat()` body: ~16 lines (595-611)
- `change_class()` can be simplified but stays on Ship (orchestrates multiple delegates)

Estimated additions (facade methods):
- Layer manager property + delegation: ~10 lines
- Resource manager property + delegation: ~15 lines

Net reduction: ~65-80 lines, bringing Ship to ~635-650 lines.

**Important note:** To reach the <500 line target, Phase 1 analysis must identify additional
methods/properties that can be moved. Candidates include:
- `change_class()` could move to ShipLayerManager (it's primarily layer reinit)
- `recalculate_stats()` orchestration could move to a dedicated method
- Some of the combat state attributes might move to ShipCombatManager
- The `mark_stats_dirty()` / `recalculate_stats_if_dirty()` pair
- The `cached_summary` property

Phase 1 will catalog every remaining method and determine the full extraction plan.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
