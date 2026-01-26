# PROJ-19: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Current Metrics:**
- 254 hasattr() calls in game/ directory across 63 files
- 190 getattr() calls in game/ directory across 46 files
- 0 Protocol definitions exist (game/core/protocols.py does not exist)

**Major Duck Typing Clusters Identified:**
1. `game/ui/screens/strategy_screen.py` lines 446-544: 6-type cascade checking for StarSystem, Star, Planet, SectorEnvironment, Fleet, WarpPoint
2. `game/ui/screens/strategy_detail_fmt.py` lines 222-244: Duplicate type discrimination in get_label_for_object()
3. `game/ai/controller.py` lines 109, 349: `hasattr(obj, 'team_id')` for combat entity filtering

**Existing Interface Patterns:**
- `game/ai/interfaces/controllable.py` - IControllable ABC with 15 abstract methods and ShipControllableAdapter
- `ui/builder/drop_target.py` - Uses @runtime_checkable Protocol correctly (existing pattern to follow)

## Swarm Findings Summary

### Architecture
- Strategy entities defined in `game/strategy/data/`: Fleet, Planet (dataclass), StarSystem, Star, WarpPoint
- Galaxy class maintains spatial indexes for O(1) lookups
- Planet and ShipInstance use @dataclass; others use regular classes
- All entity classes already have the properties needed for Protocol compatibility

### Key Patterns to Reuse
- **TYPE_CHECKING guards**: `game/strategy/data/fleet.py:4-7` shows correct pattern to avoid circular imports
- **ABC Interface style**: `game/ai/interfaces/controllable.py` provides consistent interface design
- **@runtime_checkable Protocol**: `ui/builder/drop_target.py` shows existing usage in codebase

### Dependencies & Risks
1. **Circular imports** - protocols.py importing from strategy/data; mitigation: TYPE_CHECKING guards
2. **Mock objects in tests** - MagicMock passes Protocol checks; mitigation: use spec=ClassName
3. **Performance** - isinstance with Protocol is O(N) checks; mitigation: keep Protocols minimal (3-4 attributes)
4. **Optional vs required confusion** - Some getattr patterns are genuinely optional; mitigation: document which to keep

### Opportunities Discovered
- TypeGuard functions provide IDE type narrowing, improving developer experience
- Protocol-based approach doesn't require modifying existing entity classes
- Can incrementally migrate files without breaking changes

## Protocol Design

### Strategy Entity Protocols

```python
@runtime_checkable
class IStarSystem(Protocol):
    """Protocol for StarSystem entities."""
    @property
    def stars(self) -> List[Any]: ...
    @property
    def planets(self) -> List[Any]: ...
    @property
    def warp_points(self) -> List[Any]: ...
    @property
    def global_location(self) -> Any: ...  # HexCoord
    @property
    def name(self) -> str: ...

@runtime_checkable
class IStar(Protocol):
    """Protocol for Star entities."""
    @property
    def color(self) -> Tuple[int, int, int]: ...
    @property
    def mass(self) -> float: ...
    @property
    def temperature(self) -> float: ...
    @property
    def star_type(self) -> Any: ...  # Enum
    @property
    def name(self) -> str: ...

@runtime_checkable
class IPlanet(Protocol):
    """Protocol for Planet entities."""
    @property
    def planet_type(self) -> Any: ...  # PlanetType enum
    @property
    def resources(self) -> Dict[str, Any]: ...
    @property
    def owner_id(self) -> Optional[int]: ...
    @property
    def name(self) -> str: ...

@runtime_checkable
class IFleet(Protocol):
    """Protocol for Fleet entities."""
    @property
    def ships(self) -> List[Any]: ...
    @property
    def orders(self) -> List[Any]: ...
    @property
    def location(self) -> Any: ...  # HexCoord
    @property
    def owner_id(self) -> int: ...
    @property
    def id(self) -> int: ...

@runtime_checkable
class IWarpPoint(Protocol):
    """Protocol for WarpPoint entities."""
    @property
    def destination_id(self) -> str: ...
    @property
    def location(self) -> Any: ...  # HexCoord

@runtime_checkable
class ISectorEnvironment(Protocol):
    """Protocol for SectorEnvironment entities."""
    @property
    def local_hex(self) -> Any: ...
    @property
    def system(self) -> Any: ...
    def calculate_radiation(self) -> Any: ...
```

### Combat Entity Protocols

```python
@runtime_checkable
class ICombatant(Protocol):
    """Protocol for combat-capable entities with team affiliation."""
    @property
    def team_id(self) -> int: ...
    @property
    def is_alive(self) -> bool: ...
    @property
    def position(self) -> Any: ...  # Vector2
```

### TypeGuard Functions

```python
def is_star_system(obj: Any) -> TypeGuard[IStarSystem]:
    return isinstance(obj, IStarSystem)

def is_star(obj: Any) -> TypeGuard[IStar]:
    return isinstance(obj, IStar)

def is_planet(obj: Any) -> TypeGuard[IPlanet]:
    return isinstance(obj, IPlanet)

def is_fleet(obj: Any) -> TypeGuard[IFleet]:
    return isinstance(obj, IFleet)

def is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]:
    return isinstance(obj, IWarpPoint)

def is_sector_environment(obj: Any) -> TypeGuard[ISectorEnvironment]:
    return isinstance(obj, ISectorEnvironment)

def is_combatant(obj: Any) -> TypeGuard[ICombatant]:
    return isinstance(obj, ICombatant)
```

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Migration Pattern

**Before (duck typing):**
```python
if hasattr(obj, 'stars'):  # StarSystem
    primary = obj.primary_star
elif hasattr(obj, 'ships'):  # Fleet
    ship_count = len(obj.ships)
```

**After (Protocol-based):**
```python
from game.core.protocols import is_star_system, is_fleet

if is_star_system(obj):
    primary = obj.primary_star  # Type narrowed to IStarSystem
elif is_fleet(obj):
    ship_count = len(obj.ships)  # Type narrowed to IFleet
```
