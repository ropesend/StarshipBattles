# PROJ-139: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Baseline
- **11,906 tests passing**, 2 warnings, 0 failures (2026-02-13)

### Current State
- **Stars** have `diameter_hexes` (0.5 to 11.0) but occupy a single hex for selection/interaction
- **Dyson Spheres** created as single `Planet` at `HexCoord(0, 0)` with `PlanetType.DYSON_SPHERE`
- **No objects span multiple hexes** for selection, interaction, or spatial queries
- Dyson creation clears planets within `dyson_radius = 9` hexes (to be aligned to 5)
- Dyson conditions are hardcoded (288K, 1g, 0.3 water) instead of matching creator species

### Key Classes
| Class | File | Role |
|-------|------|------|
| `Star` | `game/strategy/data/stars.py:77` | Star data with `diameter_hexes`, `location` |
| `Planet` | `game/strategy/data/planet.py:137` | Planet data including DYSON_SPHERE type |
| `StarSystem` | `game/strategy/data/galaxy.py:43` | Container for stars, planets, warp points |
| `Galaxy` | `game/strategy/data/galaxy.py:95` | Spatial registries: `_global_hex_planets`, `_planet_to_system` |
| `HexCoord` | `game/core/hex_math.py:25` | Axial hex coordinate (q, r, s=-q-r) |
| `ColonizeValidator` | `game/strategy/validation/colonize_validator.py:50` | Checks fleet at planet's hex |
| `StrategyInputHandler` | `game/ui/screens/strategy_input_handler.py:719` | `_handle_picking()` click->object |
| `StrategyRenderer` | `game/ui/screens/strategy_renderer.py:332` | Star/planet rendering |
| `RaceConfig` | `game/strategy/data/race_config.py:104` | Species environmental preferences |

## Swarm Findings Summary

### Architecture
- **Two-Level Coordinates**: Galaxy-global vs system-local hex coords
- **Spatial Registries**: `_global_hex_planets` (HexCoord -> List[Planet]) for O(1) lookups
- **Selection Pipeline**: screen -> world -> hex -> `_handle_picking()` -> priority list
- **Existing pattern**: `get_all_fleets_in_system()` (line 315) already builds `Set[HexCoord]` from system objects - this is exactly the zone pattern we need
- **`hex_ring()`** exists but **no `hex_circle_filled()`** - need to add

### Key Patterns to Reuse
- **Set[HexCoord] for system bounds**: `galaxy.py:329-342`
- **Protocol system**: `game/core/protocols.py` - runtime_checkable protocols
- **Spatial registry pattern**: `_global_hex_planets` dict
- **Star diameter_hexes**: computed by `_map_radius_to_hexes()` in `stars.py:262`
- **Planet orbital avoidance**: `planet_gen.py` uses `safe_start = int(diameter_hexes / 2) + 2`

### Dependencies & Risks
1. **`get_system_at_location()` O(n)** (galaxy.py:277) - iterates all systems. Zone registry provides O(1) alternative
2. **Binary star overlap** - companions placed by hex_ring, no zone collision check
3. **Warp point placement** - `create_vars_link()` doesn't check zone boundaries
4. **Save compat** - old saves rejected per policy. Increment save version.
5. **Performance** - ~3000-6000 zone registry entries for 100-200 systems. Acceptable.

### Opportunities
- Pre-compute system hex sets instead of rebuilding per call
- Zone infrastructure enables future nebulae, asteroid fields, territory claims

## Core Design: IZoneOccupant Protocol + Galaxy Zone Registry

### IZoneOccupant Protocol
New protocol in `game/core/protocols.py`:
```python
@runtime_checkable
class IZoneOccupant(Protocol):
    @property
    def occupied_hexes(self) -> FrozenSet[Any]:
        """Set of LOCAL hex coords this object occupies."""
        ...
```

### Zone Data on Objects
- `Star.occupied_hexes`: computed from `diameter_hexes` as filled circle
- `Planet.occupied_hexes`: defaults to `frozenset({self.location})` for normal planets
- Dyson Sphere `Planet`: large circular zone + `diameter_hexes` field for rendering

### Galaxy Zone Registry
New dict in Galaxy.__init__:
```python
self._global_hex_zones = {}  # HexCoord -> List[object]  (stars, dyson spheres, etc.)
```
- `register_zone(system, obj)` / `unregister_zone(system, obj)` methods
- Rebuilt during `from_dict()` like `_global_hex_planets`
- Queried by `get_zones_at_global_hex(hex)` for O(1) lookup

### Selection & Interaction
- Clicking any hex in a zone returns the zone-owning object
- Fleet at any hex in a Dyson Sphere's zone can colonize it
- Star zones are passable (fleets can enter/stop)
- Selection priority unchanged: fleets > planets > warp points > stars/zones > environment

### Dyson Sphere Conditions
Set from creator empire's `race_config`:
- `surface_gravity = race_config.gravity_ideal * 9.81`
- `surface_temperature = race_config.temperature_ideal`
- `surface_water = race_config.water_ideal`
- Atmosphere from preferred gases at ideal pressures
- Clearing radius aligned to zone radius (5 hexes, not 9)

### Image Rendering
- Dyson Sphere rendered with `Sphereworld_Portrait.png` at 11-hex diameter
- Uses same rendering pattern as stars: scale image to `diameter_hexes * hex_size * zoom`
- Planet `diameter_hexes` field added for Dyson Sphere (normal planets don't need it)
