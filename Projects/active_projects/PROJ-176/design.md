# PROJ-176: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/)
- **Type:** Technical Debt Review
- **Date:** 2026-02-23
- **Report:** [View Full Report](../../Reviews/results/2026-02-23_194404_tech-debt_missing-abstractions-duplication-elimination/report.md)
- **Agents:** ABS-SIM, ABS-VAL, ABS-UI, ABS-LOAD, CENSUS, DESIGN, PRIORITY

## Architecture

### Layer Boundaries
All proposed abstractions respect the existing layer hierarchy:
- `game/core/` — ValidationResult factory methods (no new dependencies)
- `game/simulation/components/abilities/` — SimpleMultiplierAbility, SuperweaponMarker (simulation layer only)
- `game/strategy/validation/` — Validator primitives (strategy layer)
- `game/strategy/engine/` — BaseCommandHandler mixin (strategy layer)

### Migration Policy
Per CLAUDE.md: **ALL-AT-ONCE per abstraction, phased across abstractions.**
When introducing an abstraction:
1. Implement the abstraction + tests
2. Migrate ALL consumers in a single phase
3. Delete the old pattern completely
4. Never leave partial migrations

---

## API Designs

### Cluster 5: ValidationResult Factory Methods
**File:** `game/core/validation.py`
**Mechanism:** Static factory methods (additive — no breaking changes)

```python
@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)

    @staticmethod
    def success() -> 'ValidationResult':
        """Create a successful validation result."""
        return ValidationResult(is_valid=True)

    @staticmethod
    def error(message: str) -> 'ValidationResult':
        """Create a failed validation result with a single error."""
        return ValidationResult(is_valid=False, errors=[message])

    @staticmethod
    def errors(messages: List[str]) -> 'ValidationResult':
        """Create a failed validation result with multiple errors."""
        return ValidationResult(is_valid=False, errors=list(messages))
```

**Call site migration patterns:**
```python
# Before: ValidationResult(is_valid=False, errors=["Fleet not found."])
# After:  ValidationResult.error("Fleet not found.")

# Before: ValidationResult(is_valid=False, errors=[f"...", f"..."])
# After:  ValidationResult.errors([f"...", f"..."])

# Before: ValidationResult()  or  ValidationResult(True)  or  ValidationResult(is_valid=True)
# After:  ValidationResult.success()
```

**Call sites (83 total across 11 files):**
- `game/strategy/engine/command_handlers.py` — 24 calls
- `game/strategy/validation/superweapon_validator.py` — 24 calls
- `game/strategy/engine/superweapon_command_handlers.py` — 20 calls
- `game/strategy/validation/transfer_validator.py` — 17 calls
- `game/simulation/validation/ship_validator.py` — 10 calls
- `game/strategy/validation/colonize_validator.py` — 9 calls
- `game/ui/screens/race_validator.py` — 9 calls
- `game/strategy/facade/strategy_session_facade.py` — 5 calls
- `game/core/validation.py` — 3 calls
- `game/simulation/validation/base.py` — 2 calls
- `game/strategy/data/race_config.py` — 1 call

---

### Cluster 3: CrewRequired Legacy Fix
**File:** `game/simulation/components/abilities/crew.py:73`

```python
# Before (legacy inline pattern):
val = data if isinstance(data, (int, float)) else data.get('value', data.get('amount', 0))
self.amount = int(val)

# After (use existing base class helper):
self.amount = int(self._parse_primary_value(data))
```

**Pre-check:** Grep all component JSON for `"amount"` key usage with CrewRequired. If found, use `_parse_primary_value(data, fallback_keys=('amount',))` instead (requires adding `fallback_keys` parameter to base method).

---

### Cluster 10: Validator Shared Primitives
**File:** NEW `game/strategy/validation/primitives.py`
**Mechanism:** Composable pure functions (NOT a base class — per DESIGN agent recommendation)

```python
"""Composable validation guard-clause helpers for strategy validators.

These are pure functions that return Optional[ValidationResult].
Return None to indicate the check passed, or a ValidationResult to short-circuit.
"""
from typing import Optional
from game.core.validation import ValidationResult

def require_fleet(session, fleet_id: str, empire_id: str) -> Optional[ValidationResult]:
    """Validate that a fleet exists and belongs to the empire. Returns error or None."""
    fleet = session._get_fleet_by_id(fleet_id)
    if fleet is None:
        return ValidationResult.error("Fleet not found.")
    if fleet.owner_id != empire_id:
        return ValidationResult.error("Fleet does not belong to this empire.")
    return None

def require_planet(session, planet_id: str) -> Optional[ValidationResult]:
    """Validate that a planet exists. Returns error or None."""
    planet = session.galaxy.get_planet(planet_id) if session.galaxy else None
    if planet is None:
        return ValidationResult.error("Planet not found.")
    return None

def require_system_at_location(galaxy, location) -> Optional[ValidationResult]:
    """Validate that a star system exists at the given location."""
    system = galaxy.get_system_at_location(location)
    if system is None:
        return ValidationResult.error("No star system at this location.")
    return None
```

**Usage in validators:**
```python
# Before (superweapon_validator.py, repeated 12+ times):
fleet = session._get_fleet_by_id(cmd.fleet_id)
if fleet is None:
    return ValidationResult(is_valid=False, errors=["Fleet not found."])
if fleet.owner_id != empire_id:
    return ValidationResult(is_valid=False, errors=["Fleet does not belong to this empire."])

# After:
from game.strategy.validation.primitives import require_fleet
err = require_fleet(session, cmd.fleet_id, empire_id)
if err:
    return err
```

---

### Cluster 6: BaseCommandHandler Mixin
**File:** `game/strategy/engine/command_handlers.py`
**Mechanism:** Mixin class with resolution helpers (ICommandHandler protocol unchanged)

```python
class BaseCommandHandler:
    """Mixin providing common resolution helpers for command handlers."""

    @staticmethod
    def _resolve_fleet(session, fleet_id: str, empire_id: str) -> tuple:
        """Resolve a fleet, returning (fleet, error_result) tuple.
        If fleet is valid, error_result is None. If invalid, fleet is None."""
        fleet = session._get_fleet_by_id(fleet_id)
        if fleet is None:
            return None, ValidationResult.error("Fleet not found.")
        if fleet.owner_id != empire_id:
            return None, ValidationResult.error("Fleet does not belong to this empire.")
        return fleet, None

    @staticmethod
    def _resolve_planet(session, planet_id: str) -> tuple:
        """Resolve a planet, returning (planet, error_result) tuple."""
        planet = session.galaxy.get_planet(planet_id) if session.galaxy else None
        if planet is None:
            return None, ValidationResult.error("Planet not found.")
        return planet, None
```

**Usage in handlers:**
```python
# Before (repeated 19 times):
class MoveCommandHandler:
    def execute(self, session, cmd, empire_id):
        fleet = session._get_fleet_by_id(cmd.fleet_id)
        if fleet is None:
            return ValidationResult(is_valid=False, errors=["Fleet not found."])
        if fleet.owner_id != empire_id:
            return ValidationResult(is_valid=False, errors=["Fleet does not belong..."])
        ...

# After:
class MoveCommandHandler(BaseCommandHandler):
    def execute(self, session, cmd, empire_id):
        fleet, err = self._resolve_fleet(session, cmd.fleet_id, empire_id)
        if err:
            return err
        ...
```

---

### Cluster 4: SimpleMultiplierAbility Base Class
**File:** `game/simulation/components/abilities/base.py`
**Mechanism:** ABC subclass with class-attribute-driven configuration

```python
class SimpleMultiplierAbility(Ability):
    """Base class for abilities with a single numeric value modified by one multiplier.

    Subclasses configure behavior via class attributes:
        stat_key:    The modifier stat key string (e.g. 'thrust_mult')
        value_attr:  Name of the current-value attribute (e.g. 'thrust_force')
        base_attr:   Name of the base-value attribute (e.g. 'base_thrust')
        ui_label:    Display label for get_ui_rows() (e.g. 'Thrust')
        ui_format:   Format string for the value (e.g. '{:.0f} N')
        ui_color:    Color hint constant (e.g. HINT_THRUST)
        int_result:  If True, cast result to int (default: False)
    """
    stat_key: str = ''
    value_attr: str = ''
    base_attr: str = ''
    ui_label: str = ''
    ui_format: str = '{:.0f}'
    ui_color: str = '#FFFFFF'
    int_result: bool = False

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        required = ('stat_key', 'value_attr', 'base_attr', 'ui_label')
        for attr in required:
            val = getattr(cls, attr, '')
            if not val and cls.__name__ != 'SimpleMultiplierAbility':
                raise TypeError(f"{cls.__name__} must set class attribute '{attr}'")

    def __init__(self, component, data):
        super().__init__(component, data)
        base_val = self._parse_primary_value(data)
        if self.int_result:
            base_val = int(base_val)
        setattr(self, self.base_attr, base_val)
        setattr(self, self.value_attr, base_val)

    def sync_data(self, data):
        super().sync_data(data)
        base_val = self._parse_primary_value(data)
        if self.int_result:
            base_val = int(base_val)
        setattr(self, self.base_attr, base_val)
        setattr(self, self.value_attr, base_val)

    def recalculate(self):
        base = getattr(self, self.base_attr)
        mult = self.get_effective_stat(self.stat_key, 1.0)
        result = base * mult
        if self.int_result:
            result = int(result)
        setattr(self, self.value_attr, result)

    def get_ui_rows(self):
        val = getattr(self, self.value_attr)
        return [{'label': self.ui_label, 'value': self.ui_format.format(val), 'color_hint': self.ui_color}]

    def get_primary_value(self) -> float:
        return float(getattr(self, self.value_attr))
```

**Migration candidates (7 classes):**

| Class | File | stat_key | value_attr | base_attr | ui_format | int_result | Lines Saved |
|-------|------|----------|------------|-----------|-----------|------------|-------------|
| ShieldProjection | defense.py:9-31 | capacity_mult | capacity | base_capacity | {:.0f} | No | 5 |
| ShieldRegeneration | defense.py:33-54 | energy_gen_mult | rate | base_rate | {:.1f}/s | No | 5 |
| CombatPropulsion | propulsion.py:8-32 | thrust_mult | thrust_force | base_thrust | {:.0f} N | No | 7 |
| ManeuveringThruster | propulsion.py:35-59 | turn_mult | turn_rate | base_turn_rate | {:.1f} deg/s | No | 7 |
| StrategicMovement | propulsion.py:62-104 | strategic_mult | movement_points | base_movement_points | {:.0f} MP | No | 7 |
| CrewCapacity | crew.py:9-27 | crew_capacity_mult | amount | _base_amount | {} | Yes | 3 |
| LifeSupportCapacity | crew.py:30-48 | life_support_capacity_mult | amount | _base_amount | {} | Yes | 3 |

**NOT candidates (13 classes):** ResourceConsumption, ResourceStorage, ResourceGeneration, CargoStorage, EmpireStorageAbility, VehicleLaunchAbility, CrewRequired, WeaponAbility, BeamWeaponAbility, SeekerWeaponAbility, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor — all have multi-field init, custom UI logic, or complex formulas.

---

### Cluster 4 Bonus: SuperweaponMarker Base Class
**File:** `game/simulation/components/abilities/superweapons.py`

```python
class SuperweaponMarker(Ability):
    """Base class for all superweapon marker abilities."""
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []
    weapon_name: str = ''

    def get_ui_rows(self):
        return [{'label': 'Superweapon', 'value': self.weapon_name, 'color_hint': HINT_SUPERWEAPON}]

    def get_primary_value(self) -> float:
        return 0.0

class DestroyPlanet(SuperweaponMarker):
    weapon_name = 'Planet Imploder'

class DestroyStar(SuperweaponMarker):
    weapon_name = 'Stellerator'
# ... 4 more two-line subclasses
```

**Before:** ~110 lines (6 classes at ~18 lines each)
**After:** ~35 lines (base class + 6 two-line subclasses)
**Lines Saved:** ~75

---

## Dependencies & Risks

### Dependency Graph
```
Phase 1: Cluster 5 (ValidationResult) ──> Cluster 10 (Validator Primitives)
                                      └──> Phase 2: Cluster 6 (BaseCommandHandler)
Phase 1: Cluster 3 (CrewRequired) ──> independent

Phase 3: Cluster 4 (SimpleMultiplierAbility) ──> independent
Phase 3: Cluster 4 bonus (SuperweaponMarker) ──> independent
```

### Risk Matrix
| Cluster | Risk Level | Mitigation |
|---------|-----------|------------|
| 5 (ValidationResult) | VERY LOW | Additive factory methods, existing API unchanged |
| 3 (CrewRequired) | LOW | 1 line change, verify JSON data first |
| 10 (Validator Primitives) | LOW | Pure functions, no state, no inheritance |
| 6 (BaseCommandHandler) | LOW | Mixin helpers only, ICommandHandler unchanged |
| 4 (SimpleMultiplierAbility) | MEDIUM | setattr/getattr — needs `__init_subclass__` validation. 943 ability tests. Migrate one class at a time. |
| 4 bonus (SuperweaponMarker) | VERY LOW | Pure marker abilities with no combat logic |

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
