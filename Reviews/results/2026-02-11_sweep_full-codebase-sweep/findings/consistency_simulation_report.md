# Consistency Violations Report: `game/simulation/`

**Sweep Date:** 2026-02-11
**Agent:** Consistency Violations
**Scope:** `game/simulation/` and all subdirectories (72 Python files)
**Baseline:** 7353 tests passing, 0 failures

---

## Phase 1: Naming Convention Analysis

### CON-SIM-001 [MAJOR] Resource attribute naming inconsistency across ability classes

**Files:**
- `game/simulation/components/abilities/resources.py`

**Description:**
`ResourceConsumption` uses the attribute name `resource_name` (line ~30) to identify the resource type, while `ResourceStorage` and `ResourceGeneration` both use `resource_type` for the same semantic concept. This inconsistency forces call sites to use conditional attribute access patterns.

**Evidence:**
```python
# ResourceConsumption (resources.py)
self.resource_name = data.get('resource', '')

# ResourceStorage (resources.py)
self.resource_type = data.get('resource', '')

# ResourceGeneration (resources.py)
self.resource_type = data.get('resource', '')
```

The downstream impact is visible in `ship_validator.py` line ~356:
```python
res_name = getattr(ab, 'resource_type', getattr(ab, 'resource_name', None))
```

This double-`getattr` pattern is a direct symptom of the naming inconsistency.

**Recommendation:** Standardize on `resource_type` for all three classes. Update `ResourceConsumption.resource_name` to `resource_type` and migrate call sites.

---

### CON-SIM-002 [MAJOR] Confusingly similar method names: `get_ability_total` vs `get_total_ability_value`

**Files:**
- `game/simulation/entities/ability_aggregator.py`
- `game/simulation/entities/ship.py`
- `game/simulation/entities/ship_stat_querier.py`

**Description:**
Two methods with nearly identical names exist with different semantics:
- `get_ability_total(components, ability_name)` in `ability_aggregator.py` -- returns the two-stage aggregated total (MAX within group, SUM across groups) for a specific ability across a list of components.
- `get_total_ability_value(ability_name)` on `Ship` / `ShipStatQuerier` -- calls into `get_ability_total` but operates on the ship's own component pool.

The naming pattern `get_ability_total` vs `get_total_ability_value` is a word-order swap that reads almost identically but lives at different abstraction levels. A developer searching for "get ability total" could easily pick the wrong one.

**Recommendation:** Rename the Ship-level method to `aggregate_ability(ability_name)` or `query_ability_total(ability_name)` to clearly distinguish from the lower-level utility function.

---

### CON-SIM-003 [MINOR] `AbilityLayer` uses string values inconsistently with enum usage

**Files:**
- `game/simulation/components/abilities/base.py`
- `game/simulation/components/abilities/cargo.py`

**Description:**
`AbilityLayer` is defined as an enum in `base.py` (with values like `AbilityLayer.COMBAT`, `AbilityLayer.STRATEGIC`). Most ability classes correctly use the enum:
```python
layer = AbilityLayer.STRATEGIC  # colonize.py, superweapons.py, markers.py
```

However, `CargoStorage` in `cargo.py` uses a raw string instead:
```python
layer = 'strategic'  # Should be AbilityLayer.STRATEGIC
```

**Recommendation:** Change `cargo.py` line 29 to use `AbilityLayer.STRATEGIC` for consistency with all other ability classes.

---

### CON-SIM-004 [MINOR] Mixed naming conventions for "team" parameter

**Files:**
- `game/simulation/systems/battle_engine.py`
- `game/simulation/factories/ai_factory.py`
- `game/simulation/managers/retreat_manager.py`

**Description:**
The concept of "the opposing team ID" is named differently across files:
- `BattleEngine.start()`: `enemy_team` (computed internally, line 470)
- `AIControllerFactory.create_for_ship()`: `enemy_team_id` (parameter name)
- `RetreatManager`: No concept of enemy team, uses `team_id` for the retreating ship's team

While not breaking, the inconsistency between `enemy_team` and `enemy_team_id` across the two most closely-related call sites (engine and factory) adds friction.

**Recommendation:** Standardize on `enemy_team_id` as the parameter name in all APIs.

---

### CON-SIM-005 [INFO] Inconsistent underscore prefix convention for private attributes

**Files:**
- `game/simulation/components/component.py`
- `game/simulation/services/vehicle_design_service.py`
- `game/simulation/entities/ship_combat_engine.py`

**Description:**
Some classes use underscore-prefixed private attributes for registries (`self._registries`) while the same semantic is stored as `self.registries` on Ship (via `__init__` parameter). The convention is mixed:
- `Component._registries` -- underscore (private)
- `Ship.registries` -- public property (exposed via `@property`)
- `VehicleDesignService._registries` -- underscore (private)

This is inconsistent but the `Ship` case is justified by providing a public `@property`. Still worth noting for uniformity.

---

## Phase 2: Structural Pattern Analysis

### CON-SIM-006 [CRITICAL] `modifiers.py` and `modifier_effects.py` use `logging.getLogger(__name__)` instead of project logger

**Files:**
- `game/simulation/components/modifiers.py`
- `game/simulation/components/modifier_effects.py`

**Description:**
Every other file in `game/simulation/` (and the broader codebase) uses the project-specific logger:
```python
from game.core.logger import log_warning, log_error, log_debug, log_info
```

These two files instead use the standard Python logging module:
```python
import logging
logger = logging.getLogger(__name__)
```

This means log messages from the modifier system may:
1. Not appear in the game's log output if the project logger routes to a custom handler
2. Not follow the project's log formatting conventions
3. Be at a different log level than expected

This is the only instance of raw `logging.getLogger` in the entire `game/simulation/` directory.

**Recommendation:** Replace `logging.getLogger(__name__)` calls with `from game.core.logger import log_warning, log_debug, log_error` in both files.

---

### CON-SIM-007 [MAJOR] Duplicate/unreachable except clauses in multiple files

**Files:**
- `game/simulation/services/design_loader.py` (lines 118-133)
- `game/simulation/systems/persistence.py` (lines 60-71)
- `game/simulation/components/component.py` (lines 535-543)

**Description:**
Several files have except clauses that catch exception types already caught by earlier except blocks in the same try statement, making the later clauses unreachable dead code.

**design_loader.py `load_ship_from_file()`:**
```python
try:
    ...
except json.JSONDecodeError as e:    # Line 118 - catches JSONDecodeError
    ...
except (KeyError, TypeError, ValueError) as e:  # Line 122 - catches Key/Type/Value
    ...
except OSError as e:                  # Line 126 - catches OSError
    ...
except (KeyError, TypeError, ValueError, json.JSONDecodeError) as e:  # Line 130 - UNREACHABLE
    ...
```

The final except clause on line 130 can never execute because all its exception types are already caught by earlier handlers.

**persistence.py `ShipIO.save_ship()`:**
```python
except PermissionError as e:          # Line 60
    ...
except OSError as e:                  # Line 63
    ...
except (TypeError, ValueError) as e:  # Line 66
    ...
except (OSError, PermissionError) as e:  # Line 69 - UNREACHABLE
    ...
```

The same pattern: `OSError` and `PermissionError` are already caught.

**persistence.py `ShipIO.load_ship()`:**
```python
except json.JSONDecodeError as e:     # Line 104
    ...
except KeyError as e:                 # Line 107
    ...
except PermissionError as e:          # Line 110
    ...
except OSError as e:                  # Line 113
    ...
except (OSError, PermissionError, json.JSONDecodeError, KeyError, TypeError, ValueError) as e:  # Line 116 - UNREACHABLE
    ...
```

**component.py `load_components_data()`:**
```python
except KeyError as e:                 # Line 535
    ...
except json.JSONDecodeError as e:     # Line 538
    ...
except (FileNotFoundError, OSError, KeyError, TypeError, ValueError) as e:  # Line 541 - PARTIALLY UNREACHABLE
    ...
```

`KeyError` is already caught. `FileNotFoundError` is a subclass of `OSError` so it would never be caught separately either.

**Recommendation:** Remove unreachable except clauses. If a broad catch-all is desired, use `except Exception` with a comment explaining the intent.

---

### CON-SIM-008 [MAJOR] Mixed `Optional[X]` vs `X | None` type hint syntax

**Files:**
- `game/simulation/components/component.py` (line 155)

**Description:**
The project uses `Optional[X]` from the `typing` module consistently across all files (70+ files). However, `component.py` line 155 uses the newer `X | None` syntax:
```python
self._resource_mgr: ComponentResourceManager | None = None
self._health_mgr: ComponentHealthManager | None = None
```

While functionally equivalent in Python 3.10+, mixing syntax styles within a single codebase (and especially within a single file that also uses `Optional` elsewhere) hurts readability.

**Recommendation:** Convert to `Optional[ComponentResourceManager]` for consistency with the rest of the codebase.

---

### CON-SIM-009 [MINOR] Duplicate comment line in `resource_manager.py`

**Files:**
- `game/simulation/systems/resource_manager.py` (lines 211-213)

**Description:**
```python
# --- Ability System ---

# --- Ability System ---
```

The section comment is duplicated on consecutive lines. This appears to be a copy-paste artifact.

**Recommendation:** Remove the duplicate line.

---

### CON-SIM-010 [MINOR] Missing type hints on Projectile methods

**Files:**
- `game/simulation/entities/projectile.py`

**Description:**
The `Projectile` class is missing return type annotations on several methods including `update()`, `take_damage()`, and constructor parameters. While the class uses type hints on some attributes, the methods are inconsistently annotated compared to other entity classes like `Ship` and `Component` which have comprehensive type hints.

**Recommendation:** Add return type annotations (`-> None`, `-> bool`) to all public methods.

---

### CON-SIM-011 [MINOR] `ProjectileManager` uses `Any` type hints extensively

**Files:**
- `game/simulation/projectile_manager.py`

**Description:**
`ProjectileManager` uses `Any` for projectile parameters and return types where `Projectile` would be more descriptive:
```python
def get_active_projectiles(self) -> List[Any]:
def add_projectile(self, projectile: Any):
```

The `Projectile` class is already imported (via TYPE_CHECKING block), so using it would provide better IDE support and documentation.

**Recommendation:** Replace `Any` with `'Projectile'` (string annotation) for all projectile-typed parameters.

---

### CON-SIM-012 [INFO] Inconsistent docstring style across subdirectories

**Files:**
- `game/simulation/combat/` (comprehensive Google-style docstrings)
- `game/simulation/entities/ship_stats.py` (minimal inline comments, few docstrings on private methods)
- `game/simulation/systems/resource_manager.py` (module-level docstring is excellent, class-level sparse)

**Description:**
The `combat/` subdirectory files consistently use detailed Google-style docstrings with Args/Returns/Raises sections. The `entities/` subdirectory is mixed -- some files like `ship_serialization.py` have thorough docstrings, while `ship_stats.py` has short one-liner docstrings on private methods. The `systems/` files fall in between.

**Recommendation:** Adopt the `combat/` style as the standard and gradually bring other subdirectories into compliance.

---

## Phase 3: API Design Consistency

### CON-SIM-013 [MAJOR] Inconsistent error handling: raises vs returns error result

**Files:**
- `game/simulation/battle_controller.py`
- `game/simulation/services/battle_service.py`

**Description:**
`BattleController` mixes two error reporting strategies within the same class:
1. `run_headless()` raises `StateException` on errors
2. `update()` returns `BattleServiceResult(success=False, error=...)` on errors
3. `start_battle()` returns `BattleServiceResult` on errors

A caller cannot predict whether a method will throw or return an error object without reading the implementation. This violates the principle of least surprise.

**Recommendation:** Standardize on one pattern. Given that `BattleServiceResult` is already established as the return type for most methods, convert `run_headless()` to return `BattleServiceResult` with error details instead of raising.

---

### CON-SIM-014 [MAJOR] `Ship.from_dict` has optional registries while `ShipSerializer.from_dict` requires them

**Files:**
- `game/simulation/entities/ship.py`
- `game/simulation/entities/ship_serialization.py`

**Description:**
`Ship.from_dict()` accepts `registries: Optional[GameRegistries] = None` and then passes it through to `ShipSerializer.from_dict()`. However, `ShipSerializer.from_dict()` declares `registries: 'GameRegistries'` as required (keyword-only) and raises `TypeError` if None.

This means the `Optional` annotation on `Ship.from_dict` is misleading -- calling it with `registries=None` will always raise `TypeError`. The API contract is inconsistent between the two layers.

Additionally, `persistence.py` `ShipIO.load_ship()` line 92 calls `Ship.from_dict(data)` without passing registries at all, which would fail at runtime under strict DI.

**Recommendation:** Either make `Ship.from_dict` also declare registries as required (removing `Optional`), or add a fallback in `Ship.from_dict` that creates registries from the default provider. The current state is a half-migration.

---

### CON-SIM-015 [MINOR] Inconsistent return type conventions for removal operations

**Files:**
- `game/simulation/components/component.py`
- `game/simulation/components/modifier_manager.py`

**Description:**
`Component.remove_modifier()` delegates to `ModifierManager.remove_modifier()` which returns a new list (non-mutating):
```python
self.modifiers = ModifierManager.remove_modifier(self.modifiers, mod_id)
```

But `Component.add_modifier()` delegates to `ModifierManager.add_modifier()` which mutates the list in-place and returns a boolean:
```python
result = ModifierManager.add_modifier(self.modifiers, mod_id, value, ...)
```

The asymmetry between add (mutates, returns bool) and remove (returns new list) is surprising.

**Recommendation:** Either make both operations return a new list, or both mutate in-place with a boolean return.

---

### CON-SIM-016 [MINOR] `BattleStateManager.validate_state` uses `hasattr` instead of type checking

**Files:**
- `game/simulation/managers/battle_state_manager.py` (lines 113-132)

**Description:**
```python
def validate_state(self, state: Optional[BattleState]) -> bool:
    if state is None:
        return False
    if not hasattr(state, 'mode'):
        return False
    if not hasattr(state, 'ships'):
        return False
    return True
```

The `state` parameter is typed as `Optional[BattleState]`. If it is a `BattleState`, it will always have `mode` and `ships` attributes (they are defined in the dataclass). Using `hasattr` checks on a typed parameter suggests defensive programming against incorrect types, which would be better handled by a type check (`isinstance`).

**Recommendation:** Replace `hasattr` checks with `isinstance(state, BattleState)`.

---

## Phase 4: Project Pattern Adherence

### CON-SIM-017 [CRITICAL] `component.py` still uses `get_default_registry_provider` (legacy DI pattern)

**Files:**
- `game/simulation/components/component.py` (line 65, used in `load_components_data`, `load_components`, `load_modifiers`)

**Description:**
PROJ-50 established strict DI via `GameRegistries` as the mandatory pattern. The `Component` class constructor properly requires `registries: GameRegistries`. However, the module-level functions in the same file still use the legacy `get_default_registry_provider()`:

```python
from game.core.registry import get_default_registry_provider  # Line 65

def load_components_data(..., registries=None):
    if registries is None:
        provider = get_default_registry_provider()  # Line 502 - LEGACY FALLBACK
        registries = GameRegistries(...)

def load_components(...):
    provider = get_default_registry_provider()  # Line 557 - LEGACY
    comps = provider.get_components()

def load_modifiers(...):
    mods = get_default_registry_provider().get_modifiers()  # Line 656 - LEGACY
```

Per CLAUDE.md ("System Migration Policy"): "When a new system replaces an old one, ERADICATE the old system completely." The `get_default_registry_provider` pattern should not co-exist with strict DI.

**Recommendation:** Migrate `load_components`, `load_modifiers`, and `load_components_data` to accept `registries: GameRegistries` as required parameters, removing the `get_default_registry_provider` import entirely.

---

### CON-SIM-018 [MAJOR] `ProjectileManager` imports `BattleConfig` from `game.core.config` instead of simulation's own `battle_config.py`

**Files:**
- `game/simulation/projectile_manager.py` (line 4)
- `game/simulation/battle_config.py`

**Description:**
The simulation layer defines its own `BattleConfig` dataclass in `game/simulation/battle_config.py` (containing `BattleMode`, seed, max_ticks, etc.). However, `ProjectileManager` imports a *different* `BattleConfig` from `game.core.config`:

```python
from game.core.config import BattleConfig  # projectile_manager.py
```

This `game.core.config.BattleConfig` is a separate class with collision-related constants like `PROJECTILE_QUERY_BUFFER`, `PROJECTILE_HIT_TOLERANCE`, `MISSILE_INTERCEPT_BUFFER`, and `FIGHTER_LAUNCH_SPEED`.

The same class name `BattleConfig` existing in two different modules (`game.core.config` and `game.simulation.battle_config`) with different purposes is confusing. The core one holds physics/collision constants while the simulation one holds battle session configuration.

**Recommendation:** Rename `game.core.config.BattleConfig` to `CollisionConfig` or `CombatConfig` to disambiguate from the simulation-layer `BattleConfig`.

---

### CON-SIM-019 [MAJOR] `resource_manager.py` re-exports from abilities module (forwarding pattern)

**Files:**
- `game/simulation/systems/resource_manager.py` (lines 211-222)

**Description:**
The bottom of `resource_manager.py` contains forwarding imports:
```python
# --- Ability System ---
# Forwarding to new module
from game.simulation.components.abilities import (
    Ability, ResourceConsumption, ResourceStorage,
    ResourceGeneration, ABILITY_REGISTRY, create_ability
)
```

This creates an indirect import path that hides the true module location. Code importing `ResourceConsumption` from `resource_manager` is actually getting it from `components.abilities.resources`. This forwarding exists likely for backward compatibility from an earlier module reorganization.

Per CLAUDE.md ("System Migration Policy"): backward compatibility layers should be eradicated. Any call sites should import directly from `game.simulation.components.abilities`.

**Recommendation:** Remove the forwarding imports from `resource_manager.py`. Update all call sites to import from `game.simulation.components.abilities` directly.

---

### CON-SIM-020 [MINOR] `ShipStatsCalculator` checks ability types by string class name instead of using isinstance

**Files:**
- `game/simulation/entities/ship_stats.py` (lines 284-301)

**Description:**
The stats aggregation phase checks ability types using string comparison:
```python
ab_cls = ability.__class__.__name__
if ab_cls == 'ResourceStorage':
    ...
elif ab_cls == 'ResourceGeneration':
    ...
```

This pattern breaks if the class is renamed, subclassed, or if there are typos. The project's ability system supports `isinstance` checks and the `get_abilities()` method with polymorphic lookup. Using string comparison bypasses the type system.

**Recommendation:** Use `isinstance(ability, ResourceStorage)` or `comp.get_abilities('ResourceStorage')` for type-safe checks.

---

### CON-SIM-021 [MINOR] Excessive use of `getattr` with defaults instead of proper attribute declarations

**Files:**
- `game/simulation/entities/ship_stats.py` (lines 496-499, 506)
- `game/simulation/entities/ship_serialization.py` (lines 62-67)
- `game/simulation/entities/ship_combat_engine.py`

**Description:**
Several files use `getattr(ship, 'attribute', default)` for attributes that should always exist on the ship:
```python
prev_max_fuel = getattr(ship, '_prev_max_fuel', 0)
prev_max_ammo = getattr(ship, '_prev_max_ammo', 0)
```

```python
"strategic_movement": getattr(ship, 'total_strategic_movement', 0),
"warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
```

These attributes are set during `recalculate_stats()`, which runs before serialization. The `getattr` pattern suggests the attributes might not exist, which indicates they should be initialized in `Ship.__init__()` instead.

**Recommendation:** Initialize all ship stat attributes to their defaults in `Ship.__init__()` and remove `getattr` defensive patterns.

---

## Phase 5: Per-Module Internal Consistency

### CON-SIM-022 [MAJOR] `persistence.py` (`ShipIO`) uses Tkinter at module level -- breaks headless/test environments

**Files:**
- `game/simulation/systems/persistence.py` (lines 1-22)

**Description:**
`persistence.py` initializes Tkinter at import time:
```python
import tkinter
from tkinter import filedialog

try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except ...:
    tk_root = None
```

This code runs when any module imports from `persistence.py`, even indirectly. In headless test environments or CI servers, this can cause failures or delays. Other modules in the simulation layer avoid platform-specific UI dependencies.

Additionally, `ShipIO.load_ship()` calls `Ship.from_dict(data)` without passing registries, which would fail under the strict DI policy (PROJ-50).

**Recommendation:** Move Tkinter initialization into a lazy-init pattern (only when `save_ship`/`load_ship` are actually called). Fix the `from_dict` call to pass registries.

---

### CON-SIM-023 [MINOR] `superweapons.py` has 6 nearly identical classes with no shared base behavior

**Files:**
- `game/simulation/components/abilities/superweapons.py`

**Description:**
All 6 superweapon classes (`DestroyPlanet`, `DestroyStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `SelfDestruct`) share identical structure:
- Same `layer`, `allowed_scopes`, `default_scope`, `STAT_BINDINGS`
- Same `__init__` signature
- Same `get_primary_value()` returning 0.0
- Only `get_ui_rows()` differs (just the value string)

This is a case for a shared base class `SuperweaponAbility` that handles the common attributes and constructor, with subclasses only overriding the display name.

**Recommendation:** Extract `SuperweaponAbility` base class to reduce ~150 lines of duplicate code to ~40 lines.

---

### CON-SIM-024 [MINOR] `combat/` subdirectory has inconsistent class instantiation patterns

**Files:**
- `game/simulation/combat/targeting_system.py`
- `game/simulation/combat/damage_calculator.py`
- `game/simulation/combat/weapon_firing_system.py`

**Description:**
These three classes are instantiated differently:
- `TargetingSystem()` -- no constructor args, stores no state
- `DamageCalculator()` -- no constructor args, stores no state
- `WeaponFiringSystem()` -- no constructor args, stores no state

All three are used as utility classes with instance methods but no instance state. They could be static utility classes (like `AbilityManager` and `ModifierManager` in `components/`) or remain instances for future state injection.

The inconsistency is with the rest of the codebase: `components/` uses `@staticmethod` on similar utility classes, while `combat/` uses instance methods.

**Recommendation:** Align with whichever pattern the project intends to standardize on. If these classes will never hold state, convert to `@staticmethod` methods for consistency with `AbilityManager`/`ModifierManager`.

---

### CON-SIM-025 [INFO] `battle_config.py` defines `BattleConfig` as a dataclass, `battle_end_conditions.py` uses plain class

**Files:**
- `game/simulation/battle_config.py`
- `game/simulation/systems/battle_end_conditions.py`

**Description:**
`BattleConfig` is defined as a `@dataclass` with `field()` defaults, while `BattleEndCondition` uses a plain class with manual `__init__`. Both are configuration containers with similar semantics (immutable-ish config objects created once and passed around).

This is a minor style inconsistency within the systems layer.

**Recommendation:** Convert `BattleEndCondition` to a `@dataclass` for consistency with `BattleConfig`.

---

### CON-SIM-026 [INFO] `TYPE_CHECKING` import path inconsistency for `GameRegistries`

**Files:**
- `game/simulation/services/design_loader.py` (line 25)
- All other files

**Description:**
`design_loader.py` imports under `TYPE_CHECKING`:
```python
from game.core.registries import GameRegistries  # Note: "registries" (plural)
```

All other files import from:
```python
from game.core.registry import GameRegistries  # Note: "registry" (singular)
```

If `game.core.registries` is a different module than `game.core.registry`, this could cause subtle type-checking inconsistencies. If it is an alias, it is still confusing.

**Recommendation:** Standardize on `from game.core.registry import GameRegistries` in all files.

---

### CON-SIM-027 [INFO] `ship_stats.py` uses `tuple[list, int, int]` (PEP 585) while rest uses `Tuple[...]` (typing module)

**Files:**
- `game/simulation/entities/ship_stats.py` (line 417)

**Description:**
```python
def _phase_damage_check_and_supply(self, ship) -> tuple[list, int, int]:
```

All other files in the codebase use `Tuple[...]` from the `typing` module for return type annotations. This is the same issue as CON-SIM-008 (mixing old and new syntax) but for `tuple` vs `Tuple`.

**Recommendation:** Use `Tuple[List, int, int]` from typing for consistency.

---

## Top 5 Priority Issues

| Rank | ID | Severity | Summary | Estimated Effort |
|------|----|----------|---------|-----------------|
| 1 | CON-SIM-017 | CRITICAL | `component.py` still uses `get_default_registry_provider` (legacy DI pattern violating PROJ-50 and System Migration Policy) | Medium -- update 3 module-level functions to require `registries` parameter, update all call sites |
| 2 | CON-SIM-006 | CRITICAL | `modifiers.py` and `modifier_effects.py` use `logging.getLogger` instead of project logger -- logs may be silently lost | Low -- simple import replacement in 2 files |
| 3 | CON-SIM-007 | MAJOR | Duplicate/unreachable except clauses in 3+ files -- dead code that obscures actual error handling intent | Low -- remove unreachable except blocks |
| 4 | CON-SIM-001 | MAJOR | `resource_name` vs `resource_type` naming split across ability classes forces double-`getattr` workarounds | Medium -- rename attribute + update call sites (search for `resource_name` in ability contexts) |
| 5 | CON-SIM-014 | MAJOR | `Ship.from_dict` declares `Optional` registries but the callee always requires them -- misleading API contract | Low -- remove `Optional` annotation, add `None` guard, or fix persistence.py call site |
