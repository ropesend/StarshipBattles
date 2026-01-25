# Phase 6: Type Safety via Protocols

**Project:** Legacy Code Cleanup
**Phase:** 6 of 8
**Risk Level:** High
**Dependencies:** Phase 5 complete

---

## High-Level Project Context

This phase is part of a comprehensive 8-phase legacy code cleanup effort:

| Phase | Name | Status |
|-------|------|--------|
| 1 | Delete Dead Code | Complete |
| 2 | Remove Shims & Aliases | Complete |
| 3 | Consolidate Re-exports | Complete |
| 4 | Enforce Layer Boundaries | Complete |
| 5 | Standardize Registry Access | Complete |
| **6** | **Type Safety via Protocols** | **THIS PHASE** |
| 7 | Standardize Data Formats | Pending |
| 8 | Clean Up Tests & Patterns | Pending |

**Overall Goal:** Clean up legacy code, enforce architectural boundaries, and standardize patterns across the Starship Battles codebase.

---

## Phase 6 Objectives

1. Define core Protocol classes for strategy entities
2. Replace duck typing clusters (hasattr patterns) with isinstance checks
3. Create type guard utility functions
4. Address optional property patterns
5. Significantly reduce the 500+ hasattr/getattr defensive patterns

---

## Background: Current Problem

The codebase has 500+ instances of hasattr/getattr patterns in 4 categories:

| Category | Count | Description |
|----------|-------|-------------|
| Duck Typing | 100+ | Type discrimination: `if hasattr(obj, 'ships')` → Fleet |
| Optional Properties | 250+ | `getattr(ship, 'is_derelict', False)` |
| Backward Compat | 40+ | Checking for new vs old attributes |
| Defensive Coding | 110+ | Protecting against None/incomplete objects |

**Worst offenders:**
- `game/ui/screens/strategy_screen.py` - 30+ hasattr for type discrimination
- `game/ai/behaviors.py` - 8+ getattr for optional ship properties
- `game/ai/controller.py` - 12+ getattr for defensive access

---

## Detailed Tasks

### 6.1 Define Core Protocols

Create new file: `game/core/protocols.py`

```python
"""
Type Protocols for Starship Battles

These protocols define contracts for cross-layer type safety.
Use isinstance() checks with @runtime_checkable protocols.
"""
from typing import Protocol, runtime_checkable, Optional, List, Tuple, Dict, Any, TypeVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance
    from game.strategy.data.fleet_order import FleetOrder


# ============================================================
# STRATEGY ENTITY PROTOCOLS
# ============================================================

@runtime_checkable
class ILocatable(Protocol):
    """Entity with a location on the strategy map."""
    @property
    def location(self) -> Tuple[int, int]: ...


@runtime_checkable
class INamed(Protocol):
    """Entity with a name."""
    @property
    def name(self) -> str: ...


@runtime_checkable
class IOwnable(Protocol):
    """Entity that can be owned by an empire."""
    @property
    def owner_id(self) -> Optional[int]: ...


@runtime_checkable
class IStrategyEntity(ILocatable, INamed, Protocol):
    """Base protocol for strategy map entities."""
    pass


@runtime_checkable
class IFleet(IStrategyEntity, IOwnable, Protocol):
    """Protocol for Fleet entities."""
    @property
    def ships(self) -> List['ShipInstance']: ...

    @property
    def orders(self) -> List['FleetOrder']: ...


@runtime_checkable
class IPlanet(IStrategyEntity, IOwnable, Protocol):
    """Protocol for Planet entities."""
    @property
    def planet_type(self) -> str: ...

    @property
    def resources(self) -> Dict[str, int]: ...


@runtime_checkable
class IStarSystem(ILocatable, INamed, Protocol):
    """Protocol for StarSystem entities."""
    @property
    def stars(self) -> List[Any]: ...

    @property
    def planets(self) -> List['IPlanet']: ...


@runtime_checkable
class IStar(Protocol):
    """Protocol for Star entities."""
    @property
    def color(self) -> Tuple[int, int, int]: ...

    @property
    def mass(self) -> float: ...


@runtime_checkable
class IWarpPoint(ILocatable, Protocol):
    """Protocol for WarpPoint entities."""
    @property
    def destination_id(self) -> int: ...


# ============================================================
# COMBAT ENTITY PROTOCOLS
# ============================================================

@runtime_checkable
class ICombatant(Protocol):
    """Protocol for combat-capable entities."""
    @property
    def team_id(self) -> int: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def position(self) -> Tuple[float, float]: ...


@runtime_checkable
class IDamageable(Protocol):
    """Protocol for entities that can take damage."""
    @property
    def current_hp(self) -> float: ...

    @property
    def max_hp(self) -> float: ...

    @property
    def is_derelict(self) -> bool: ...
```

### 6.2 Create Type Guard Utilities

Add to `game/core/protocols.py`:

```python
from typing import TypeGuard

# ============================================================
# TYPE GUARDS
# ============================================================

def is_fleet(obj: Any) -> TypeGuard[IFleet]:
    """Check if object is a Fleet."""
    return isinstance(obj, IFleet)


def is_planet(obj: Any) -> TypeGuard[IPlanet]:
    """Check if object is a Planet."""
    return isinstance(obj, IPlanet)


def is_star_system(obj: Any) -> TypeGuard[IStarSystem]:
    """Check if object is a StarSystem."""
    return isinstance(obj, IStarSystem)


def is_star(obj: Any) -> TypeGuard[IStar]:
    """Check if object is a Star."""
    return isinstance(obj, IStar)


def is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]:
    """Check if object is a WarpPoint."""
    return isinstance(obj, IWarpPoint)


def is_combatant(obj: Any) -> TypeGuard[ICombatant]:
    """Check if object is a combat-capable entity."""
    return isinstance(obj, ICombatant)
```

### 6.3 Replace Duck Typing Clusters

#### 6.3.1 Strategy Screen Type Discrimination

**File:** `game/ui/screens/strategy_screen.py` (Lines 446-544)

**Before (30+ lines of duck typing):**
```python
if hasattr(obj, 'stars'):  # StarSystem
    # ... StarSystem handling
elif hasattr(obj, 'color') and hasattr(obj, 'mass'):  # Star
    # ... Star handling
elif hasattr(obj, 'planet_type'):  # Planet
    # ... Planet handling
elif hasattr(obj, 'ships'):  # Fleet
    # ... Fleet handling
elif hasattr(obj, 'destination_id'):  # WarpPoint
    # ... WarpPoint handling
```

**After (clean isinstance checks):**
```python
from game.core.protocols import (
    is_star_system, is_star, is_planet, is_fleet, is_warp_point
)

if is_star_system(obj):
    # ... StarSystem handling - obj is typed as IStarSystem
elif is_star(obj):
    # ... Star handling - obj is typed as IStar
elif is_planet(obj):
    # ... Planet handling - obj is typed as IPlanet
elif is_fleet(obj):
    # ... Fleet handling - obj is typed as IFleet
elif is_warp_point(obj):
    # ... WarpPoint handling - obj is typed as IWarpPoint
```

#### 6.3.2 Strategy Scene Entity Rendering

**File:** `game/ui/screens/strategy_scene.py`

Apply same pattern - replace hasattr chains with protocol checks.

#### 6.3.3 Strategy Detail Formatting

**File:** `game/ui/screens/strategy_detail_fmt.py`

Apply same pattern for entity type discrimination.

### 6.4 Address Optional Property Patterns

For `getattr(obj, 'property', default)` patterns, there are two approaches:

#### Approach A: Explicit Optional in Protocol

If the property is genuinely optional on the type:

```python
@runtime_checkable
class IShipState(Protocol):
    @property
    def is_derelict(self) -> bool: ...  # Required, defaults handled in implementation

    @property
    def current_target(self) -> Optional['ITarget']: ...  # Can be None
```

#### Approach B: Protocol Inheritance for Subtypes

If property exists on some subtypes:

```python
@runtime_checkable
class IBasicShip(Protocol):
    @property
    def position(self) -> Tuple[float, float]: ...

@runtime_checkable
class IFormationShip(IBasicShip, Protocol):
    @property
    def formation_master(self) -> Optional['IFormationShip']: ...

    @property
    def formation_rotation_mode(self) -> str: ...
```

### 6.5 Update AI Layer

#### 6.5.1 Behaviors Module

**File:** `game/ai/behaviors.py`

Replace patterns like:
```python
getattr(master, 'is_derelict', False)
getattr(ship, 'formation_rotation_mode', 'relative')
getattr(ship, 'turn_throttle', 1.0)
```

With proper protocol checks and typed access.

#### 6.5.2 Controller Module

**File:** `game/ai/controller.py`

Replace defensive patterns:
```python
if hasattr(obj, 'team_id') and obj.team_id == self.enemy_team_id
```

With:
```python
if is_combatant(obj) and obj.team_id == self.enemy_team_id
```

### 6.6 Update Simulation Layer

#### 6.6.1 Battle State

**File:** `game/simulation/battle_state.py`

Replace patterns like:
```python
if hasattr(ship, 'resources') and ship.resources:
if hasattr(ship, 'current_target') and ship.current_target:
```

With typed protocol checks.

---

## Implementation Priority

1. **First:** Create `game/core/protocols.py` with all protocols
2. **Second:** Update strategy_screen.py (biggest cluster)
3. **Third:** Update AI layer (behaviors.py, controller.py)
4. **Fourth:** Update remaining files

---

## Verification Checklist

After completing all tasks:

- [ ] `game/core/protocols.py` created with all protocols
- [ ] Type guards created and working
- [ ] Strategy screen type discrimination updated
- [ ] AI behaviors updated
- [ ] AI controller updated
- [ ] Battle state updated
- [ ] hasattr count significantly reduced (target: <100 remaining)
- [ ] mypy type checking passes (if configured)
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Application launches and runs correctly

---

## Files Created

- `game/core/protocols.py` (new file with all protocols)

## Files Modified

- `game/ui/screens/strategy_screen.py` (replace duck typing)
- `game/ui/screens/strategy_scene.py` (replace duck typing)
- `game/ui/screens/strategy_detail_fmt.py` (replace duck typing)
- `game/ai/behaviors.py` (replace getattr patterns)
- `game/ai/controller.py` (replace hasattr patterns)
- `game/simulation/battle_state.py` (replace hasattr patterns)
- Other files with duck typing patterns

---

## Measuring Success

**Before Phase 6:**
```bash
# Count hasattr usages
grep -r "hasattr(" --include="*.py" game/ | wc -l
# Expected: 300+

# Count getattr usages
grep -r "getattr(" --include="*.py" game/ | wc -l
# Expected: 200+
```

**After Phase 6:**
```bash
# Target: <100 hasattr remaining (mostly legitimate uses)
# Target: <50 getattr remaining (mostly legitimate defaults)
```

---

## Notes for Next Phase

Phase 7 (Standardize Data Formats) will:
- Remove dual-format support (string ships, list queues)
- Standardize on single format for all data structures
- Update test fixtures to use new formats
- Remove legacy format handling code

Ensure type safety is in place before proceeding to Phase 7.

---

*End of Phase 6 Plan*
