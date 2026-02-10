# PROJ-87: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### ShipInstance (922 lines, 49 methods)
- **47 importers** across strategy layer and tests
- 13 resource methods (~166 lines) duplicate simulation-layer Ship's ResourceRegistry behavior
- Methods like `get_current_fuel()`, `consume_fuel()`, `get_current_energy()`, `consume_energy()` re-implement what Ship already provides via `ship.resources.get_value(name)` and `ship.resources.consume(name, amount)`
- 5 display methods (`get_status_text()`, `get_hp_display()`, etc.) are UI concerns in the data layer
- 5 cargo methods (`load_cargo()`, `unload_cargo()`, etc.) are self-contained
- Serialization (to_dict/from_dict, to_ship/from_ship) is core identity and stays

### Fleet (833 lines, 48 methods across Fleet + FleetOrder + OrderType)
- **100 importers** (high blast radius — facade pattern critical)
- 12 resource aggregation methods (~211 lines) follow identical loop-over-ships patterns:
  ```python
  def get_X_costs(self):
      total = {}
      for ship in self.get_combat_capable_ships():
          costs = ship.get_X_costs()
          # aggregate to total
      return total
  ```
- 5 capability methods are self-contained
- 3 battle adapter methods bridge strategy↔simulation layers

### GameSession (834 lines, 24 methods)
- **23 importers** (moderate blast radius)
- TurnEngine delegation works well (PROJ-12 decomposition successful)
- 8 command handler methods dispatched via if/elif chain in `handle_command()` (lines ~372-403)
- 130-line initialization in `__init__` entangles galaxy generation, empire creation, race setup
- `_get_fleet_by_id()` iterates all empires O(n) — Galaxy already has O(1) `get_planet_by_id()`

## Swarm Findings Summary

### Architecture

**Cross-Layer Resource Duplication (Critical):**
```
Ship (simulation)              ShipInstance (strategy)
├─ resources: ResourceRegistry   ├─ resource_levels: Dict
│   ├─ fuel (current/max)        │   ├─ fuel value
│   ├─ energy (current/max)      │   ├─ energy value
│   └─ ammo (current/max)        │   └─ ammo value
└─ get_value(name)               └─ get_current_fuel()
└─ consume(name, amt)            └─ consume_fuel()
```
Result: 2 resource systems that must stay in sync. ~360 lines of duplicate logic.

**Fleet Aggregation Pattern (Repetitive):**
All 12 Fleet resource methods follow the same iteration pattern. Can be consolidated to 3 parameterized methods (get_costs, has_resources, consume_resources) with a movement_type parameter.

**GameSession Command Dispatch (Growing):**
```python
def handle_command(self, command_type, data):
    if command_type == 'build_ship': self._handle_build_ship_command(data)
    elif command_type == 'move': self._handle_move_command(data)
    elif command_type == 'transfer': self._handle_transfer_command(data)
    # ... 5 more elif branches
```
This grows with every new command type. Registry pattern eliminates the chain.

### Key Patterns to Reuse
- **Facade delegation**: `self.resources = ShipResourceManager(self)` — used successfully in prior projects
- **Registry dispatch**: `CommandHandlerRegistry.register(name, handler)` — standard pattern
- **Loop aggregation**: `FleetResourceAggregator` parameterizes the identical loop pattern

### Dependencies & Risks
1. **Fleet↔ShipInstance junction in production_engine.py** — imports both Fleet and ShipInstance. Facade pattern means no import changes needed.
2. **100 Fleet importers** — any API change ripples widely. Facade keeps existing method signatures as thin wrappers.
3. **Display methods in data layer** — extract to separate formatter in strategy layer (not UI) to avoid circular dependencies.
4. **Serialization must be preserved** — `to_dict()`/`from_dict()` on ShipInstance and Fleet must continue to work identically.

### Opportunities Discovered
- FleetResourceAggregator could consolidate 12 methods into 3 parameterized methods, further reducing code
- Galaxy.get_fleet_by_id() O(1) lookup is a quick performance win
- ShipResourceManager could eventually delegate to Ship's ResourceRegistry instead of reimplementing

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
