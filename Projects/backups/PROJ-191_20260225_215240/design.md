# PROJ-191: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Duck Typing Landscape in game/strategy/
The strategy layer has ~105 `hasattr()`/`getattr()` instances across 20+ files. Analysis categorized them into:

| Category | Count | Treatment |
|----------|-------|-----------|
| A: Empire access (`getattr(empire, 'colonies', [])`) | ~21 | Replace with direct access |
| B: Colony/Facility access (`getattr(colony, 'facilities', [])`) | ~22 | Replace with direct access |
| C: Fleet/Ship access (`getattr(fleet, 'ships', [])`) | ~10 | Replace with direct access |
| D: Type discrimination (`hasattr(obj, 'planet_type')`) | ~25 | Replace with isinstance |
| E: comp_def dual-format (dict or Component) | ~12 | Keep & document |
| F: Command handler defensive chaining | ~3 | Replace with direct access |
| G: Miscellaneous (DTOs, game session, etc.) | ~12 | Mixed treatment |

### Why getattr Is Unnecessary for Domain Objects
All strategy domain objects (Empire, Planet, Fleet, PlanetaryFacility, ShipInstance) are either `@dataclass` classes or plain classes with well-defined `__init__` methods. Their attributes **always exist** after construction:

- `Empire.__init__` always sets: `colonies=[]`, `fleets=[]`, `resource_pool={}`, `max_storage={}`, `race_config`
- `Planet` is a `@dataclass` with: `facilities` (default_factory=list), `populations` (default_factory=list), `resources` (default_factory=dict), `diameter_hexes` (default=0.0)
- `Fleet.__init__` always sets: `ships=[]`, `orders=[]`, `location`, `speed`
- `PlanetaryFacility` is a `@dataclass` with: `is_operational` (default=True), `design_data`, `resource_levels`

The `getattr` defaults are therefore **never actually used** in production. They only protect against test mocks that lack the attribute — which is itself a testing anti-pattern.

### Existing Protocol Infrastructure
`game/core/protocols.py` already defines 15+ protocols with `@runtime_checkable` decorator and TypeGuard functions. The naming convention is `I`-prefix (IFleet, IPlanet, ILocatable, etc.). However, these protocols are designed for **cross-layer boundaries** (e.g., `IPostBattleShip` between strategy and simulation) and are **not used** within the strategy layer's own internal code.

## Swarm Findings Summary
Combined analysis from 6 parallel agents examining architecture, dependencies, tests, patterns, risks, and data flow.

### Architecture
- Strategy layer follows **delegate pattern**: Fleet, Galaxy, ShipInstance delegate to extracted helpers
- Engines are **stateless processors** that accept domain objects as parameters
- **Facade/DTO pattern** isolates UI from domain objects (FleetInfo, PlanetInfo DTOs)
- Two-phase save/load: Galaxy first (assigns IDs), then Empires (resolve IDs via galaxy)

### Key Patterns to Reuse
- **TYPE_CHECKING import pattern**: `game/strategy/data/fleet.py:15` — uses `if TYPE_CHECKING:` block to avoid circular imports
- **Protocol + TypeGuard pattern**: `game/core/protocols.py:344-361` — every protocol has a matching `is_*()` function
- **is_zone_occupant()**: `game/core/protocols.py:379-381` — already exists, can replace `hasattr(obj, 'occupied_hexes')` in galaxy registry

### Dependencies & Risks
1. **FleetOrder.to_dict() serialization** — Changing hasattr to isinstance could affect save format if the type checks don't match exactly. **Mitigation:** The serialization output format doesn't change, only the branching logic. Test thoroughly with save/load round-trip.
2. **Bare Mock() test breakage** — ~60% of strategy test mocks use `Mock()` without spec. After removing getattr, accessing `mock.colonies` on an unspec'd Mock will return a MagicMock object instead of a list, potentially causing subtle test failures. **Mitigation:** Update mocks in Phase 3 immediately after Phase 2.
3. **Component definition dual-format** — `comp_def` objects can be dict (from JSON) or Component (from simulation layer). Both formats need `abilities` access. **Mitigation:** Keep getattr for these, document the pattern.

### Opportunities Discovered
- `cargo_transfer_service.get_inventory_items()` can be cleanly typed with `Union[FleetInfo, PlanetInfo]` and isinstance checks
- `galaxy_entity_registry.py` already imports `IZoneOccupant` conceptually — just needs to use `is_zone_occupant()` from protocols
- `population_engine.py` already uses real Empire/Planet objects in tests — gold standard for other test files

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
