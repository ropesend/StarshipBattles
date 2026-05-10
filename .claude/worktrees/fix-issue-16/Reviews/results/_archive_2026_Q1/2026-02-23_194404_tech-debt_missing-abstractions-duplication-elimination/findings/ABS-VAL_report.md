# ABS-VAL Report: Validation & Command Abstraction Design

## Summary
- **Total issues found:** 5
- **Critical:** 0 | **Major:** 3 | **Minor:** 2 | **Info:** 0
- **Scope:** ValidationResult construction patterns, command handler structure, validator base classes
- **Files analyzed:** 11 production files, ~1,800 lines of validation/command code

---

## Findings

### Finding 1

#### MAJOR: ValidationResult Factory Methods Missing
**ID:** ABS-VAL-001
**Location:** `game/core/validation.py:64-146`
**Issue:** The `ValidationResult` dataclass lacks factory methods, forcing every call site to use verbose constructor patterns. There are **83 total constructor calls** across 10 files, decomposing into:

| Pattern | Count | Files | Example |
|---------|-------|-------|---------|
| `ValidationResult(is_valid=False, errors=["msg"])` (single-line single-error) | 43 | 7 | `ValidationResult(is_valid=False, errors=["Fleet not found."])` |
| `ValidationResult(\n    is_valid=False,\n    errors=["msg"]\n)` (multi-line single-error) | 27 | 5 | Multi-line with `error_code=` kwarg |
| `ValidationResult()` (success, no args) | 27 | 8 | `return ValidationResult()` |
| `ValidationResult(True)` (success, positional) | 12 | 2 | `result = ValidationResult(True)` |
| `ValidationResult(is_valid=True)` (success, explicit) | 1 | 1 | `return ValidationResult(is_valid=True)` |

**Impact:** Every error-result construction requires 1-4 lines of boilerplate. The `is_valid=False, errors=[...]` pattern is the single most-repeated code pattern in the strategy layer. The inconsistency between `ValidationResult()`, `ValidationResult(True)`, and `ValidationResult(is_valid=True)` for success is also a readability issue.

**Proposed API:**
```python
@dataclass
class ValidationResult:
    # ... existing fields ...

    @staticmethod
    def success() -> 'ValidationResult':
        """Create a successful validation result."""
        return ValidationResult()

    @staticmethod
    def error(message: str, code: Optional[Union[str, ErrorCode]] = None) -> 'ValidationResult':
        """Create a failed validation result with a single error.

        Args:
            message: Error description.
            code: Optional error code for programmatic handling.

        Returns:
            ValidationResult with is_valid=False and the error message.
        """
        error_code_str = None
        if code is not None:
            error_code_str = code.value if isinstance(code, ErrorCode) else code
        return ValidationResult(
            is_valid=False,
            errors=[message],
            error_code=error_code_str
        )

    @staticmethod
    def errors(messages: List[str], code: Optional[Union[str, ErrorCode]] = None) -> 'ValidationResult':
        """Create a failed validation result with multiple errors.

        Args:
            messages: List of error descriptions.
            code: Optional error code for programmatic handling.

        Returns:
            ValidationResult with is_valid=False and all error messages.
        """
        error_code_str = None
        if code is not None:
            error_code_str = code.value if isinstance(code, ErrorCode) else code
        return ValidationResult(
            is_valid=False,
            errors=list(messages),
            error_code=error_code_str
        )
```

**Before/After:**

*Example 1 - Single error (command_handlers.py:94):*
```python
# BEFORE (1 line, 71 chars)
return ValidationResult(is_valid=False, errors=["Fleet not found."])

# AFTER (1 line, 47 chars)
return ValidationResult.error("Fleet not found.")
```

*Example 2 - Single error with error_code (transfer_validator.py:47):*
```python
# BEFORE (1 line, 93 chars)
return ValidationResult(is_valid=False, errors=["Fleet does not exist."], error_code="FLEET_NOT_FOUND")

# AFTER (1 line, 68 chars)
return ValidationResult.error("Fleet does not exist.", code="FLEET_NOT_FOUND")
```

*Example 3 - Multi-line error with error_code (transfer_validator.py:55-59):*
```python
# BEFORE (5 lines)
return ValidationResult(
    is_valid=False,
    errors=[f"Invalid direction '{direction}'. Must be 'load' or 'unload'."],
    error_code="INVALID_DIRECTION"
)

# AFTER (1 line)
return ValidationResult.error(f"Invalid direction '{direction}'. Must be 'load' or 'unload'.", code="INVALID_DIRECTION")
```

*Example 4 - Success (various):*
```python
# BEFORE (3 inconsistent patterns)
return ValidationResult()          # 27 sites
result = ValidationResult(True)    # 12 sites
return ValidationResult(is_valid=True)  # 1 site

# AFTER (1 consistent pattern)
return ValidationResult.success()
```

**Call Sites (error factory - 70 sites across 7 files):**

| File | Line Numbers | Count |
|------|-------------|-------|
| `game/strategy/engine/command_handlers.py` | 69, 94, 145, 154, 175, 193, 198, 218, 223, 249, 256, 276, 290, 306, 351, 375, 387, 393 | 18 |
| `game/strategy/engine/superweapon_command_handlers.py` | 35, 40, 64, 88, 116, 140, 164, 206, 230, 235, 258, 281, 308, 331 | 14 |
| `game/strategy/validation/superweapon_validator.py` | 55, 63, 92, 100, 107, 138, 146, 154, 162, 193, 201, 216, 245, 253, 260, 285, 295, 303 | 18 |
| `game/strategy/validation/transfer_validator.py` | 47, 51, 55, 63, 84, 90, 97, 103, 135, 145, 174, 183, 193, 217 | 14 |
| `game/strategy/validation/colonize_validator.py` | 80, 101, 123, 134, 141, 153, 169 | 7 |
| `game/strategy/facade/strategy_session_facade.py` | 443, 449, 469, 473 | 4 |
| `game/ui/screens/race_validator.py` | 53, 60, 67, 74, 81, 87, 106, 114 | 8 |

**Call Sites (success factory - 40 sites across 10 files):**

| File | Line Numbers | Count |
|------|-------------|-------|
| `game/strategy/engine/command_handlers.py` | 164, 180, 205, 234, 340, 358 | 6 |
| `game/strategy/engine/superweapon_command_handlers.py` | 219, 247, 270, 297, 320, 343 | 6 |
| `game/strategy/validation/superweapon_validator.py` | 68, 112, 167, 221, 265, 308 | 6 |
| `game/strategy/validation/transfer_validator.py` | 151, 200, 223 | 3 |
| `game/strategy/validation/colonize_validator.py` | 129, 175 | 2 |
| `game/strategy/facade/strategy_session_facade.py` | 475 | 1 |
| `game/strategy/data/race_config.py` | 288 | 1 |
| `game/ui/screens/race_validator.py` | 120 | 1 |
| `game/simulation/validation/ship_validator.py` | 58, 78, 96, 111, 146, 243, 289, 335, 409, 419 | 10 |
| `game/simulation/validation/base.py` | 30 (docstring), 58 | 2 |

**Lines Saved:** Multi-line error patterns (27 occurrences x 3 lines saved = ~81 lines). Single-line patterns save ~24 chars each but same line count. Success patterns gain consistency. **Net: ~81 lines saved + significant readability improvement.**

**Risk:** LOW. Factory methods are purely additive -- existing constructor still works. Can be migrated incrementally file-by-file. No behavioral change.

**Category:** Quick Win
**Recommendation:** Add factory methods to ValidationResult class, then migrate call sites file-by-file. Start with the highest-density files (command_handlers.py, superweapon_command_handlers.py).
**Effort:** Simple

---

### Finding 2

#### MAJOR: Command Handler Fleet/Planet Resolution Boilerplate
**ID:** ABS-VAL-002
**Location:** `game/strategy/engine/command_handlers.py:73-435`, `game/strategy/engine/superweapon_command_handlers.py:27-343`
**Issue:** 19 command handler classes all repeat identical fleet resolution (19/19), planet resolution (7/19), and "fleet not found" error return (19/19) boilerplate. The pattern is:

```python
fleet = session._get_fleet_by_id(cmd.fleet_id)
if not fleet:
    return ValidationResult(is_valid=False, errors=["Fleet not found."])
```

This 3-line block appears **19 times** verbatim. Planet resolution (`session._get_planet_by_id` + error check) appears **7 times**. Two handlers also iterate `session.empires` to find the owning empire (ColonizeCommandHandler, TransferCommandHandler).

**Handler Pattern Matrix:**

| Handler | Fleet Resolve | Planet Resolve | Target Fleet Resolve | Owner Resolve | Validator Call | Mission Move |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| ColonizeCommandHandler | Y (empire iter) | Y (optional) | - | Y | Y | - |
| MoveCommandHandler | Y | - | - | - | - | - |
| BuildShipCommandHandler | - | Y | - | - | - | - |
| InterceptCommandHandler | Y | - | Y | - | - | - |
| JoinCommandHandler | Y | - | Y | - | - | - |
| ColonizeMissionCommandHandler | Y | Y (optional) | - | - | Y (inline) | Y (inline) |
| ClearOrdersCommandHandler | Y | - | - | - | - | - |
| TransferCommandHandler | Y | Y | - | Y (empire iter) | Y | - |
| ImplodePlanetCommandHandler | Y | Y | - | - | Y | - |
| StellerateStarCommandHandler | Y | - | - | - | Y | - |
| OpenWarpPointCommandHandler | Y | - | - | - | Y | - |
| CloseWarpPointCommandHandler | Y | - | - | - | Y | - |
| CreateDysonSphereCommandHandler | Y | - | - | - | Y | - |
| SelfDestructCommandHandler | Y | - | - | - | Y | - |
| ImplodePlanetMissionHandler | Y | Y | - | - | - | Y |
| StellerateStarMissionHandler | Y | - | - | - | - | Y |
| OpenWarpPointMissionHandler | Y | - | - | - | - | Y |
| CloseWarpPointMissionHandler | Y | - | - | - | - | Y |
| CreateDysonSphereMissionHandler | Y | - | - | - | - | Y |

**Impact:** 57 lines of pure fleet-resolution boilerplate (19 x 3 lines). 21 lines of planet-resolution boilerplate (7 x 3 lines). The mission handlers share an additional pattern via the existing `_setup_mission_move()` helper (good partial consolidation already done).

**Proposed API:**
```python
class BaseCommandHandler:
    """Base class for command handlers with common resolution helpers."""

    def _resolve_fleet(
        self, session: 'GameSession', fleet_id: int
    ) -> Tuple[Optional[Any], Optional[ValidationResult]]:
        """Resolve a fleet by ID, returning error result if not found.

        Args:
            session: GameSession context.
            fleet_id: Fleet ID to look up.

        Returns:
            Tuple of (fleet, None) if found, or (None, ValidationResult) if not found.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if not fleet:
            return None, ValidationResult.error("Fleet not found.")
        return fleet, None

    def _resolve_planet(
        self, session: 'GameSession', planet_id: int
    ) -> Tuple[Optional[Any], Optional[ValidationResult]]:
        """Resolve a planet by ID, returning error result if not found.

        Args:
            session: GameSession context.
            planet_id: Planet ID to look up.

        Returns:
            Tuple of (planet, None) if found, or (None, ValidationResult) if not found.
        """
        planet = session._get_planet_by_id(planet_id)
        if not planet:
            return None, ValidationResult.error("Planet not found.")
        return planet, None

    def _resolve_target_fleet(
        self, session: 'GameSession', fleet_id: int
    ) -> Tuple[Optional[Any], Optional[ValidationResult]]:
        """Resolve a target fleet by ID, returning error result if not found.

        Args:
            session: GameSession context.
            fleet_id: Target fleet ID to look up.

        Returns:
            Tuple of (fleet, None) if found, or (None, ValidationResult) if not found.
        """
        fleet = session._get_fleet_by_id(fleet_id)
        if not fleet:
            return None, ValidationResult.error("Target fleet not found.")
        return fleet, None

    def _resolve_fleet_owner(
        self, session: 'GameSession', fleet: Any
    ) -> Tuple[Optional[Any], Optional[ValidationResult]]:
        """Find the empire that owns a fleet.

        Args:
            session: GameSession context.
            fleet: Fleet to find owner for.

        Returns:
            Tuple of (empire, None) if found, or (None, ValidationResult) if not found.
        """
        for emp in session.empires:
            if fleet in emp.fleets:
                return emp, None
        return None, ValidationResult.error("Fleet owner not found.")
```

**Before/After:**

*Example 1 - StellerateStarCommandHandler (superweapon_command_handlers.py:56-77):*
```python
# BEFORE (22 lines)
class StellerateStarCommandHandler:
    def execute(self, session, cmd):
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])
        result = SuperweaponValidator.validate_stellerate_star(session.galaxy, fleet)
        if result.is_valid:
            order = FleetOrder(OrderType.STELLERATE_STAR, target=None)
            fleet.add_order(order)
            log_info(f"GameSession: Issued STELLERATE_STAR order for Fleet {fleet.id}")
        return result

# AFTER (18 lines)
class StellerateStarCommandHandler(BaseCommandHandler):
    def execute(self, session, cmd):
        fleet, err = self._resolve_fleet(session, cmd.fleet_id)
        if err: return err
        result = SuperweaponValidator.validate_stellerate_star(session.galaxy, fleet)
        if result.is_valid:
            order = FleetOrder(OrderType.STELLERATE_STAR, target=None)
            fleet.add_order(order)
            log_info(f"GameSession: Issued STELLERATE_STAR order for Fleet {fleet.id}")
        return result
```

*Example 2 - InterceptCommandHandler (command_handlers.py:183-205):*
```python
# BEFORE (23 lines)
class InterceptCommandHandler:
    def execute(self, session, cmd):
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])
        target_fleet = session._get_fleet_by_id(cmd.target_fleet_id)
        if not target_fleet:
            return ValidationResult(is_valid=False, errors=["Target fleet not found."])
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)
        log_info(f"...")
        return ValidationResult()

# AFTER (19 lines)
class InterceptCommandHandler(BaseCommandHandler):
    def execute(self, session, cmd):
        fleet, err = self._resolve_fleet(session, cmd.fleet_id)
        if err: return err
        target_fleet, err = self._resolve_target_fleet(session, cmd.target_fleet_id)
        if err: return err
        order = FleetOrder(OrderType.MOVE_TO_FLEET, target=target_fleet)
        fleet.add_order(order)
        log_info(f"...")
        return ValidationResult.success()
```

*Example 3 - ImplodePlanetCommandHandler (superweapon_command_handlers.py:27-53):*
```python
# BEFORE (27 lines)
class ImplodePlanetCommandHandler:
    def execute(self, session, cmd):
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if not fleet:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])
        planet = session._get_planet_by_id(cmd.planet_id)
        if not planet:
            return ValidationResult(is_valid=False, errors=["Planet not found."])
        result = SuperweaponValidator.validate_implode_planet(session.galaxy, fleet, planet)
        if result.is_valid:
            order = FleetOrder(OrderType.IMPLODE_PLANET, target=planet)
            fleet.add_order(order)
            log_info(f"...")
        return result

# AFTER (23 lines)
class ImplodePlanetCommandHandler(BaseCommandHandler):
    def execute(self, session, cmd):
        fleet, err = self._resolve_fleet(session, cmd.fleet_id)
        if err: return err
        planet, err = self._resolve_planet(session, cmd.planet_id)
        if err: return err
        result = SuperweaponValidator.validate_implode_planet(session.galaxy, fleet, planet)
        if result.is_valid:
            order = FleetOrder(OrderType.IMPLODE_PLANET, target=planet)
            fleet.add_order(order)
            log_info(f"...")
        return result
```

**Handlers That Can Adopt BaseCommandHandler (17/19):**

| Handler | Adoption | Notes |
|---------|----------|-------|
| MoveCommandHandler | YES | Simple fleet resolve |
| BuildShipCommandHandler | YES | Planet resolve only |
| InterceptCommandHandler | YES | Fleet + target fleet |
| JoinCommandHandler | YES | Fleet + target fleet |
| ClearOrdersCommandHandler | YES | Simple fleet resolve |
| TransferCommandHandler | YES | Fleet + owner + planet |
| All 6 Superweapon Direct Handlers | YES | Fleet + optional planet |
| All 5 Superweapon Mission Handlers | YES | Fleet + optional planet |

**Handlers Requiring Special Treatment (2/19):**

| Handler | Issue | Solution |
|---------|-------|----------|
| ColonizeCommandHandler | Uses empire iteration for fleet lookup (not `_get_fleet_by_id`) | Could add `_resolve_fleet_with_owner` method, or refactor to use `_get_fleet_by_id` + `_resolve_fleet_owner` |
| ColonizeMissionCommandHandler | Complex inline validation + optional planet | Still benefits from `_resolve_fleet`, but planet logic is conditional |

**Lines Saved:** 19 fleet-resolve blocks x 1 line saved = 19 lines. 7 planet-resolve blocks x 1 line saved = 7 lines. Total: **~26 lines saved** + significant readability and consistency improvement.

**Risk:** LOW. The base class adds helper methods but does not change execution semantics. Each handler still controls its own flow. The ICommandHandler protocol is unchanged.

**Dependency Analysis:** No circular import risk. BaseCommandHandler would live in `game/strategy/engine/command_handlers.py` alongside the existing handlers. It depends only on `game.core.validation.ValidationResult` (already imported).

**Category:** Small Project
**Recommendation:** Create `BaseCommandHandler` in command_handlers.py. Migrate superweapon handlers first (most uniform), then core handlers. Combine with ABS-VAL-001 for maximum effect (use factory methods in helper returns).
**Effort:** Medium

---

### Finding 3

#### MAJOR: Strategy Validators Lack Shared Base Class
**ID:** ABS-VAL-003
**Location:** `game/strategy/validation/colonize_validator.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/validation/superweapon_validator.py`, `game/ui/screens/race_validator.py`
**Issue:** Four validator classes (ColonizeValidator, TransferValidator, SuperweaponValidator, RaceValidator) plus the existing simulation-layer validators (ValidationRule hierarchy in `game/simulation/validation/base.py`) have no shared strategy-layer base. The strategy validators repeat:

1. **Entity existence checks** - "Fleet does not exist", "Target does not exist", "Planet not found" (3 validators, 5+ sites)
2. **Early-return error pattern** - Every guard clause constructs a `ValidationResult(is_valid=False, ...)` and returns immediately
3. **Success return** - Every method ends with `return ValidationResult()` at the bottom

The simulation layer already has a good base class hierarchy (`ValidationRule` -> `DesignValidationRule` / `AdditionValidationRule`) that uses the template method pattern. The strategy validators are all static-method-based and don't fit this pattern.

**Validator Structure Comparison:**

| Validator | Style | Methods | Lines | Guard Clauses | Error Returns |
|-----------|-------|---------|-------|---------------|---------------|
| ColonizeValidator | Static methods | 4 public, 1 private | 247 | fleet exists, planet location, ownership | 7 |
| TransferValidator | Static methods | 4 public (1 main + 3 private) | 224 | fleet exists, target exists, direction, cargo type, location | 14 |
| SuperweaponValidator | Static methods | 7 public | 309 | ability checks, system checks, entity checks | 18 |
| RaceValidator | Instance method | 1 public | 121 | name, flag, portrait, theme, water, aptitudes, budget | 8 |
| ShipDesignValidator | Instance method (rule-based) | 2 public | 56 | Delegated to rules | Aggregated |

**Impact:** The lack of shared primitives means every validator independently reimplements entity-not-found checks. If error message format changes (e.g., adding error codes), every validator needs updating separately. The prior art report (DRY-STRAT-SYS CQ-003) identified this as a Critical finding.

**Proposed API:**

The strategy validators are fundamentally different from the simulation validators (static vs instance, different parameters, different domains). A forced common base would be over-engineering. Instead, the right abstraction is **shared validation primitives** combined with the **ValidationResult factory methods from ABS-VAL-001**:

```python
# In game/strategy/validation/primitives.py (NEW - ~30 lines)
"""Shared validation primitives for strategy-layer validators."""
from typing import Any, Optional, Tuple
from game.core.validation import ValidationResult


def require_entity(
    entity: Any,
    entity_name: str,
    error_code: Optional[str] = None
) -> Optional[ValidationResult]:
    """Return an error result if entity is None/falsy.

    Args:
        entity: The entity to check.
        entity_name: Human-readable name for error message (e.g., "Fleet", "Planet").
        error_code: Optional error code.

    Returns:
        ValidationResult.error(...) if entity is falsy, None if entity exists.

    Usage:
        if err := require_entity(fleet, "Fleet", "FLEET_NOT_FOUND"):
            return err
    """
    if not entity:
        return ValidationResult.error(
            f"{entity_name} does not exist.",
            code=error_code
        )
    return None


def require_at_system(
    galaxy: Any,
    fleet: Any,
    action_description: str
) -> Optional[ValidationResult]:
    """Return an error result if fleet is not at a star system.

    Args:
        galaxy: Galaxy object.
        fleet: Fleet to check.
        action_description: Description for error (e.g., "destroy a star").

    Returns:
        ValidationResult.error(...) if not at system, None otherwise.
    """
    system = galaxy.get_system_at_location(fleet.location)
    if system is None:
        return ValidationResult.error(
            f"Fleet must be at a star system to {action_description}."
        )
    return None


def require_system_has_stars(
    system: Any,
    action_description: str
) -> Optional[ValidationResult]:
    """Return an error result if system has no stars.

    Args:
        system: Star system to check.
        action_description: Description for error.

    Returns:
        ValidationResult.error(...) if no stars, None otherwise.
    """
    if not getattr(system, 'stars', []):
        return ValidationResult.error(
            f"System has no stars to {action_description}."
        )
    return None
```

**Before/After:**

*Example 1 - SuperweaponValidator.validate_stellerate_star (superweapon_validator.py:71-112):*
```python
# BEFORE (42 lines)
@staticmethod
def validate_stellerate_star(galaxy, fleet, component_registry=None):
    if component_registry is not None:
        ship = SuperweaponValidator.find_ship_with_ability(fleet, "DestroyStar", component_registry)
        if ship is None:
            return ValidationResult(
                is_valid=False,
                errors=["No ship in fleet has DestroyStar ability."]
            )
    system = galaxy.get_system_at_location(fleet.location)
    if system is None:
        return ValidationResult(
            is_valid=False,
            errors=["Fleet must be at a star system to destroy a star."]
        )
    if not getattr(system, 'stars', []):
        return ValidationResult(
            is_valid=False,
            errors=["System has no stars to destroy."]
        )
    return ValidationResult()

# AFTER (27 lines)
@staticmethod
def validate_stellerate_star(galaxy, fleet, component_registry=None):
    if component_registry is not None:
        ship = SuperweaponValidator.find_ship_with_ability(fleet, "DestroyStar", component_registry)
        if ship is None:
            return ValidationResult.error("No ship in fleet has DestroyStar ability.")

    if err := require_at_system(galaxy, fleet, "destroy a star"):
        return err

    system = galaxy.get_system_at_location(fleet.location)
    if err := require_system_has_stars(system, "destroy"):
        return err

    return ValidationResult.success()
```

*Example 2 - TransferValidator.validate (transfer_validator.py:20-116):*
```python
# BEFORE (first 10 lines of guards)
if not fleet:
    return ValidationResult(is_valid=False, errors=["Fleet does not exist."], error_code="FLEET_NOT_FOUND")
if not target:
    return ValidationResult(is_valid=False, errors=["Target does not exist."], error_code="TARGET_NOT_FOUND")

# AFTER
if err := require_entity(fleet, "Fleet", "FLEET_NOT_FOUND"):
    return err
if err := require_entity(target, "Target", "TARGET_NOT_FOUND"):
    return err
```

**Shared Primitives Usage Matrix:**

| Primitive | ColonizeValidator | TransferValidator | SuperweaponValidator | Count |
|-----------|:-:|:-:|:-:|:-:|
| `require_entity(fleet, "Fleet")` | 1 | 1 | - | 2 |
| `require_entity(target, "Target/Planet")` | - | 1 | 1 | 2 |
| `require_at_system(galaxy, fleet, ...)` | - | - | 4 | 4 |
| `require_system_has_stars(system, ...)` | - | - | 2 | 2 |

**Lines Saved:** Direct line savings from primitives: ~20-30 lines across validators. Combined with ABS-VAL-001 factory methods, the SuperweaponValidator alone shrinks from 309 lines to ~220 lines (~29% reduction).

**Risk:** LOW. Primitives are pure functions, no state, no inheritance. Validators adopt them incrementally.

**Category:** Quick Win (primitives) + Small Project (full adoption)
**Recommendation:** Create `game/strategy/validation/primitives.py` with shared guard-clause helpers. Combine rollout with ABS-VAL-001 factory methods for maximum impact. Do NOT force a common base class -- the validators are too structurally different. The walrus operator (`:=`) pattern keeps the guard-clause flow clean.
**Effort:** Simple

---

### Finding 4

#### MINOR: Superweapon Direct Handler Structural Duplication
**ID:** ABS-VAL-004
**Location:** `game/strategy/engine/superweapon_command_handlers.py:27-175`
**Issue:** The 6 direct superweapon command handlers (ImplodePlanet, StellerateStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct) all follow an identical 4-step pattern:

```
1. Resolve fleet (+ optional planet)
2. Call SuperweaponValidator.validate_X(...)
3. If valid, create FleetOrder(OrderType.X, target=...) and fleet.add_order(...)
4. Log and return result
```

The only differences between handlers are: (a) which validator method is called, (b) which OrderType is used, (c) what the order target is.

**Impact:** 6 classes x ~15 lines each = 90 lines. Could be replaced by a single generic `SuperweaponDirectHandler` class configured with validator method + order type + target extractor. However, the current code is already clear and each handler is short. The existing `_setup_mission_move()` helper for mission handlers is a good example of appropriate consolidation.

**Proposed API (data-driven alternative):**
```python
class SuperweaponDirectHandler(BaseCommandHandler):
    """Generic handler for direct superweapon commands."""

    def __init__(
        self,
        order_type: OrderType,
        validator_method: str,
        needs_planet: bool = False,
        target_builder: Optional[Callable] = None,
        log_label: Optional[str] = None
    ):
        self._order_type = order_type
        self._validator_method = validator_method
        self._needs_planet = needs_planet
        self._target_builder = target_builder or (lambda cmd, fleet, planet: planet)
        self._log_label = log_label or order_type.name

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        fleet, err = self._resolve_fleet(session, cmd.fleet_id)
        if err: return err

        planet = None
        if self._needs_planet:
            planet, err = self._resolve_planet(session, cmd.planet_id)
            if err: return err

        validator_fn = getattr(SuperweaponValidator, self._validator_method)
        # Build args dynamically based on validator signature
        result = validator_fn(session.galaxy, fleet, planet) if self._needs_planet \
            else validator_fn(session.galaxy, fleet)

        if result.is_valid:
            target = self._target_builder(cmd, fleet, planet)
            order = FleetOrder(self._order_type, target=target)
            fleet.add_order(order)
            log_info(f"GameSession: Issued {self._log_label} order for Fleet {fleet.id}")

        return result
```

**Registration:**
```python
# Instead of 6 classes, register configured instances:
registry.register('IssueImplodePlanetCommand', SuperweaponDirectHandler(
    order_type=OrderType.IMPLODE_PLANET,
    validator_method='validate_implode_planet',
    needs_planet=True
))
registry.register('IssueStellerateStarCommand', SuperweaponDirectHandler(
    order_type=OrderType.STELLERATE_STAR,
    validator_method='validate_stellerate_star',
    target_builder=lambda cmd, f, p: None
))
```

**Lines Saved:** 90 lines (6 classes) -> ~40 lines (1 class + 6 registrations) = **~50 lines saved**.

**Risk:** MEDIUM. The data-driven approach is less discoverable than individual classes. Debugger breakpoints become harder to set for specific handlers. The OpenWarpPoint and SelfDestruct handlers have non-trivial target builders.

**Category:** Small Project
**Recommendation:** Consider but do NOT prioritize. The current code is readable and each handler is only ~15 lines. The BaseCommandHandler from ABS-VAL-002 provides the main benefit (resolution helpers). Only pursue this if the superweapon handler count grows beyond 6.
**Effort:** Medium

---

### Finding 5

#### MINOR: Superweapon Mission Handler Structural Duplication
**ID:** ABS-VAL-005
**Location:** `game/strategy/engine/superweapon_command_handlers.py:222-343`
**Issue:** The 5 mission command handlers follow an identical pattern, already partially consolidated via the `_setup_mission_move()` helper:

```
1. Resolve fleet
2. (Optional) Resolve planet
3. Call _setup_mission_move(session, fleet, cmd.target_hex)
4. If move valid, queue action FleetOrder
5. Log and return success
```

The only differences are: (a) whether a planet is resolved, (b) which OrderType and target are used for the action order.

**Impact:** 5 classes x ~20 lines = 100 lines. The `_setup_mission_move()` helper already eliminates the worst duplication. A generic `SuperweaponMissionHandler` could reduce this further but faces the same readability tradeoffs as ABS-VAL-004.

**Proposed API (same data-driven pattern as ABS-VAL-004):**
```python
class SuperweaponMissionHandler(BaseCommandHandler):
    """Generic handler for superweapon mission commands (MOVE + action)."""

    def __init__(
        self,
        order_type: OrderType,
        needs_planet: bool = False,
        target_builder: Optional[Callable] = None,
        log_label: Optional[str] = None
    ):
        self._order_type = order_type
        self._needs_planet = needs_planet
        self._target_builder = target_builder or (lambda cmd, fleet, planet: planet)
        self._log_label = log_label or order_type.name

    def execute(self, session: 'GameSession', cmd: Any) -> ValidationResult:
        fleet, err = self._resolve_fleet(session, cmd.fleet_id)
        if err: return err

        planet = None
        if self._needs_planet:
            planet, err = self._resolve_planet(session, cmd.planet_id)
            if err: return err

        move_result = _setup_mission_move(session, fleet, cmd.target_hex)
        if not move_result.is_valid:
            return move_result

        target = self._target_builder(cmd, fleet, planet)
        action_order = FleetOrder(self._order_type, target=target)
        fleet.add_order(action_order)

        log_info(f"GameSession: Queued {self._log_label} mission for Fleet {fleet.id}")
        return ValidationResult.success()
```

**Lines Saved:** 100 lines (5 classes) -> ~35 lines (1 class + 5 registrations) = **~65 lines saved**.

**Risk:** MEDIUM (same readability tradeoffs as ABS-VAL-004).

**Category:** Small Project
**Recommendation:** Same as ABS-VAL-004 -- consider but don't prioritize. The handlers are already short thanks to `_setup_mission_move()`.
**Effort:** Medium

---

## Top 5 Priority Issues

| Priority | ID | Title | Category | Impact | Risk |
|----------|-----|-------|----------|--------|------|
| 1 | ABS-VAL-001 | ValidationResult Factory Methods | Quick Win | Eliminates 83 verbose constructor calls, ~81 lines saved, consistency across 10 files | LOW |
| 2 | ABS-VAL-003 | Validator Shared Primitives | Quick Win | Eliminates repeated guard clauses across 3 validators, ~25 lines saved | LOW |
| 3 | ABS-VAL-002 | BaseCommandHandler Resolution Helpers | Small Project | Eliminates 19 fleet-resolve blocks + 7 planet-resolve blocks, ~26 lines saved | LOW |
| 4 | ABS-VAL-004 | Superweapon Direct Handler Consolidation | Small Project | ~50 lines saved, but readability tradeoff | MEDIUM |
| 5 | ABS-VAL-005 | Superweapon Mission Handler Consolidation | Small Project | ~65 lines saved, but readability tradeoff | MEDIUM |

**Recommended Implementation Order:**
1. **ABS-VAL-001** first -- it's purely additive, zero regression risk, and every other finding benefits from it
2. **ABS-VAL-003** second -- the primitives depend on factory methods from ABS-VAL-001
3. **ABS-VAL-002** third -- BaseCommandHandler uses factory methods internally and can optionally use primitives
4. **ABS-VAL-004 + ABS-VAL-005** are optional follow-ups -- only if handler count grows

**Total Lines Saved (Priority 1-3):** ~132 lines + major consistency improvement across 10 files.

---

## Cross-References to Prior Art

| Prior Art ID | This Report | Relationship |
|-------------|-------------|-------------|
| DRY-STRAT-SYS CQ-013 | ABS-VAL-001 | Prior art identified 36 ValidationResult creations. Our count is 83 (more comprehensive -- includes success patterns and all files). |
| DRY-STRAT-SYS CQ-004 | ABS-VAL-002 | Prior art noted "Mission Command Handler Pattern (5+ handlers)". We expand to cover all 19 handlers with a unified BaseCommandHandler. |
| DRY-STRAT-SYS CQ-003 | ABS-VAL-003 | Prior art flagged "Validator common pattern (3 validators)". We propose primitives over forced inheritance. |
| DRY-STRAT-SYS CQ-008 | ABS-VAL-003 | Prior art noted "Validator entity resolution" duplication. Our `require_entity()` primitive addresses this. |

---
*Report generated: 2026-02-23*
*Agent: ABS-VAL (Validation & Command Abstraction Designer)*
