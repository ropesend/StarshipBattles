# PROJ-159: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Root Cause of Test Failures

The current unit tests in `test_transfer_validator.py` use `MagicMock(spec=Planet)` to create test planets. However, the `TransferValidator` uses protocol-based type checking:

```python
# transfer_validator.py line 70-72
from game.core.protocols import is_planet, is_fleet

if is_planet(target):  # isinstance(target, IPlanet)
    # Planet-specific validation
```

The `is_planet()` function (`game/core/protocols.py:326-328`) performs:
```python
def is_planet(obj: Any) -> TypeGuard[IPlanet]:
    return isinstance(obj, IPlanet)
```

`MagicMock` objects do NOT implement the `IPlanet` protocol, so `isinstance()` returns `False`, causing the validator to skip planet-specific validation logic entirely.

### Why Mocks Can't Be Fixed

The `@runtime_checkable` Protocol decorator enables duck-type checking, but `MagicMock` objects don't actually define the protocol methods - they create mock objects that respond to attribute access. The `isinstance()` check against a Protocol uses `_get_protocol_attrs()` to scan for required methods, which fails on mocks.

**Options considered:**
1. ~~Make `is_planet()` duck-type friendly~~ - Invasive change to core protocols
2. ~~Create Mock subclass implementing IPlanet~~ - Complex, fragile maintenance
3. **Use real Planet objects** - Clean, maintainable, follows existing patterns

## Swarm Findings Summary

### Architecture (Planet Class)

**Location:** `game/strategy/data/planet.py:138-201`

Planet is a `@dataclass` with 13 mandatory fields (physical properties) and 11 optional fields:

**Mandatory (no defaults):**
- `name`, `location`, `orbit_distance`
- `mass`, `radius`, `surface_area`, `density`
- `surface_gravity`, `surface_pressure`, `surface_temperature`
- `surface_water`, `tectonic_activity`, `magnetic_field`

**Used by TransferValidator (only 5):**
- `name` - Error messages
- `owner_id` - Colonization check
- `location` - System location
- `total_population` - Population check (computed property)
- `populations` - Species-specific checks

**Solution:** Create factory function with Earth-like defaults for physical properties.

### Fleet Cargo System

**How cargo capacity works:**
1. `Fleet.get_fleet_cargo_capacity()` → `FleetResourceAggregator`
2. Aggregator sums `ship.get_cargo_capacity()` for all ships
3. Ship capacity from `CargoStorage` ability in design layers

**How to create transport ships:**
```python
design = {
    "layers": {
        "internal": [{
            "id": "cargo_hold",
            "abilities": {"CargoStorage": {"cargo_type": "passengers", "capacity": 500}}
        }]
    }
}
ship = ShipInstance.create(design, owner_id=0, name="Transport")
```

### Key Patterns to Reuse

- **MockGalaxy**: `tests/integration/strategy/test_colonize_logic.py:32-43`
  - Simple dict-based system storage
  - Implements `get_planets_at_global_hex()`
  - Copy and add `get_system_at_location()` for transfer tests

- **Ship with cargo**: `tests/unit/strategy/engine/test_colonize_population.py:41-67`
  - `_make_ship_with_cargo()` pattern
  - Uses `CargoStorage` ability in layers

- **Colony ship factory**: `tests/conftest.py:272-305`
  - `make_colony_ship_for_planet()` - centralized, reusable

### Dependencies & Risks

1. **Physical property requirements** - Planet constructor requires 13 mandatory fields
   - *Mitigation:* Create factory function with Earth-like defaults

2. **Protocol satisfaction** - Real Planet must pass `is_planet()` check
   - *Mitigation:* Real Planet class implements IPlanet by design

3. **Galaxy system structure** - Validator expects galaxy with system containment
   - *Mitigation:* Use MockGalaxy/MockSystem pattern from colonize_logic.py

### Opportunities Discovered

- **Consolidate tests**: Current 30 tests include implementation-detail tests (validation order, constant existence) that don't add value. Reduce to ~12 core behavioral tests.

- **Reuse existing fixtures**: MockGalaxy pattern already proven in integration tests.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key decisions:**
1. Use real Planet/Fleet objects instead of MagicMock
2. Move tests from `unit/` to `integration/`
3. Consolidate to ~12 core tests (from 30)
4. Follow MockGalaxy pattern from test_colonize_logic.py
