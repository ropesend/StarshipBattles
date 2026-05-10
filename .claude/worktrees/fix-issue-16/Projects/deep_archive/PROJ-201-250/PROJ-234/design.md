# PROJ-234: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

ShipInstance (`game/strategy/data/ship_instance.py`, 756 lines) is a `@dataclass` with 44 public methods in 9 responsibility clusters. Three delegates already exist and work well:
- `ShipResourceManager` — 7 methods for resource tracking
- `ShipCargoManager` — 5 methods for cargo management
- `ShipDisplayFormatter` — 5 methods for display formatting

The remaining clusters that are candidates for extraction:
1. **Simulation Bridge** (~160L): `to_ship()`, `from_ship()` (dead), `update_from_ship()`, `_capture_resource_levels()`
2. **Serialization** (~120L): `to_dict()`, `from_dict()`, `to_json()`, `from_json()`, `clone()`
3. **Stats/Damage** (~110L): `get_calculated_stats()` (already a thin cache wrapper over ShipStatsCalculator), `repair()`, `get_hp_percentage()`

## Swarm Findings Summary

### Architecture (6 agents)
- ShipInstance is well-structured but accumulates too many responsibilities
- `from_ship()` classmethod has zero callers — dead code since `update_from_ship()` replaced it
- All 4 data flows (battle entry/exit, save/load) are cleanly bounded
- `_registries` is the only tricky state: not serialized, must be injected via parameter

### Key Patterns to Reuse
- **Delegate init**: `ship_instance.py:81-89` — `field(default=None, repr=False, init=False)` + `__post_init__`
- **Static serializer**: `fleet_order_serializer.py` — static methods, late-imports parent class
- **Late import**: `ship_instance.py:216,538` — `from game.simulation.entities.ship_serialization import ShipSerializer`
- **TYPE_CHECKING guards**: All existing delegates use `TYPE_CHECKING` for ShipInstance import

### Dependencies & Risks
1. **Save game compatibility (MEDIUM)** — `from_dict()` must call dataclass constructor normally so `__post_init__` runs. Mitigation: keep serializer logic identical to current implementation.
2. **Circular imports (LOW)** — Bridge imported eagerly (same pattern as existing delegates). Serializer uses late imports for ShipInstance (same pattern as FleetOrderSerializer).
3. **Cache invalidation (LOW)** — `update_from_ship()` calls `invalidate_stats_cache()` at end. When moved to bridge, calls `self._ship.invalidate_stats_cache()`. No timing sensitivity.

### Opportunities Discovered
- Coverage gap: No integration test for actual `to_ship()` → Ship with damage applied. New bridge tests should fill this.

## Design Decisions

### ShipInstanceBridge — Eager Delegate Pattern

Matches existing ShipInstance delegates (ShipResourceManager, ShipCargoManager, ShipDisplayFormatter):
- Constructor takes `ship_instance`, stores as `self._ship`
- Instantiated in `__post_init__`, stored as `field(default=None, repr=False, init=False)`
- Imports `IPostBattleShip` from `game.core.protocols`
- Late-imports `ShipSerializer` in `to_ship()` method body
- TYPE_CHECKING import for `ShipInstance`, `Ship`, `GameRegistries`

**Why delegate, not static?** The bridge mutates parent state in `update_from_ship()` (sets `current_hp`, `is_alive`, `component_damage`, etc.). Needs parent reference.

### ShipInstanceSerializer — Static Utility Pattern

Matches FleetOrderSerializer:
- All static methods, no instance state
- Late-imports `ShipInstance` inside `from_dict()` and `clone()` to avoid circular deps
- Takes `ship: ShipInstance` as first parameter (read-only access)

**Why static, not delegate?** Serialization is stateless. `from_dict()` and `from_json()` are constructors — they don't need an existing instance.

### Facade Preservation

ShipInstance keeps 1-2 line facade methods for all extracted functionality:
```python
def to_dict(self) -> Dict[str, Any]:
    from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
    return ShipInstanceSerializer.to_dict(self)
```

**Why facades?** 126+ existing tests call methods on ShipInstance. Facade methods preserve exact signatures. Zero test changes. Zero call-site changes.

See [decisions.md](decisions.md) for the full log with rationale.
