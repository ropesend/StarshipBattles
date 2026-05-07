# Inconsistency Hunter Report

**Date:** 2026-03-13
**Scope:** Full codebase (`game/` - 429 files, `tests/` - 900 files)

---

### Summary
- Total issues found: 12
- Critical: 1, Major: 5, Minor: 4, Info: 2

---

### Findings

#### CRITICAL: Strategy Engine Interface Adoption is Incomplete

**ID:** IH-01
**Location:** `game/strategy/interfaces/engines.py` vs `game/strategy/engine/*.py`
**Issue:** PROJ-43 Phase 4 created ABC interfaces for all TurnEngine sub-engines (`IMovementEngine`, `IProductionEngine`, `IConflictEngine`, `IResourceEngine`, `IMaintenanceEngine`, `IOrderProcessor`, `IEnvironmentalHazardEngine`), but only 4 of 10 concrete engines actually implement their corresponding interface:

Implements ABC:
- `HarvestingEngine(IHarvestingEngine)`
- `ResupplyEngine(IResupplyEngine)`
- `ActionExecutionEngine(IActionExecutionEngine)`
- `PopulationEngine(IPopulationEngine)`

Does NOT implement ABC:
- `FleetMovementEngine` (should implement `IMovementEngine`)
- `ProductionEngine` (should implement `IProductionEngine`)
- `MaintenanceEngine` (should implement `IMaintenanceEngine`)
- `ResourceManagementEngine` (should implement `IResourceEngine`)
- `ConflictResolutionEngine` (should implement `IConflictEngine`)
- `EnvironmentalHazardEngine` (should implement `IEnvironmentalHazardEngine`)

**Impact:** The interfaces exist but provide no compile-time or runtime contract enforcement for 6 of 10 engines. This defeats the purpose of having interfaces for dependency injection, as TurnEngine cannot rely on the interface contract. Tests cannot use the ABC to verify mock completeness either.
**Recommendation:** Add the ABC base class to all 6 missing engine implementations. This is a mechanical change with no behavioral impact.
**Effort:** Simple

---

#### MAJOR: Mixed ABC and Protocol for Interface Definitions

**ID:** IH-02
**Location:** `game/strategy/interfaces/engines.py` (ABC), `game/core/protocols.py` (Protocol), `game/simulation/interfaces/` (Protocol), `game/ai/interfaces/controllable.py` (ABC)
**Issue:** The codebase uses two different approaches for defining interfaces:

- **ABC pattern** (16 classes): Used in `game/strategy/interfaces/engines.py` (11 engine interfaces), `game/simulation/validation/base.py` (ValidationRule), `game/ai/interfaces/controllable.py` (IControllable), `game/ui/panels/base_gallery.py` (BaseGallery), `game/strategy/interfaces/battle_resolver.py` (IBattleResolver)
- **Protocol pattern** (42+ classes): Used extensively in `game/core/protocols.py` (25 protocols), `game/simulation/interfaces/` (9 protocols), `game/ai/protocols.py` (3 protocols), `game/ui/` (3 protocols), plus scattered others

There is no clear boundary for when to use which approach. Even within the same layer (`strategy`), the engine interfaces use ABC while `BuildContext` and `ICommandHandler` use Protocol.

**Impact:** Developers must choose between two patterns without guidance. ABC requires explicit inheritance; Protocol uses structural typing. Mixing them means some code requires inheritance while similar code doesn't.
**Recommendation:** Establish a clear policy. Protocol is generally preferred in modern Python for interface contracts (structural typing, no inheritance needed). Reserve ABC for cases with shared implementation (template method). Some current ABCs like `IMovementEngine` have no shared implementation and should be Protocols.
**Effort:** Complex (many files, requires careful evaluation of each interface)

---

#### MAJOR: Dual Validation Return Types (ValidationResult vs Tuple[bool, str])

**ID:** IH-03
**Location:** Multiple files across `game/strategy/`, `game/ui/`, `game/simulation/`
**Issue:** The codebase has a canonical `ValidationResult` class (in `game/core/validation.py`, consolidated in PROJ-21), but many validation methods still return `Tuple[bool, str]` or `tuple[bool, str]` instead:

Using `Tuple[bool, str]` (old pattern, ~15 methods):
- `game/strategy/systems/save_game_service.py` - `save_game()`, `delete_save()`, `_validate_save()`
- `game/strategy/systems/design_library.py` - `save_design()`, `mark_obsolete()`, `delete_design()`
- `game/strategy/systems/race_library.py` - `save_race()`
- `game/strategy/data/race_config.py` - `_validate_required_fields()`, `_validate_environment_ranges()`, etc. (6 methods)
- `game/ui/services/ship_io.py` - `save_ship()`
- `game/ui/screens/new_game_setup_screen.py` - `validate_save_name()`
- `game/simulation/managers/retreat_manager.py` - 2 methods

Using `ValidationResult` (canonical pattern):
- `game/simulation/validation/ship_validator.py`
- `game/ui/services/validation_service.py`
- `game/strategy/validation/transfer_validator.py`
- `game/strategy/validation/colonize_validator.py`
- `game/strategy/engine/turn_engine.py`
- And many more

Additionally, some use lowercase `tuple[bool, str]` (PEP 585) while others use `Tuple[bool, str]` from `typing`, adding a secondary inconsistency.

**Impact:** Two different contracts for the same operation. Callers must know which pattern a method uses. `ValidationResult` supports multiple errors, error codes, and warnings; `Tuple[bool, str]` only carries one message.
**Recommendation:** Migrate all `Tuple[bool, str]` validation returns to `ValidationResult`. The canonical class already exists and is widely adopted.
**Effort:** Medium

---

#### MAJOR: Duplicate _get_registries() Module Functions (Copy-Paste)

**ID:** IH-04
**Location:** `game/ui/services/ship_io.py:41-53`, `game/ui/screens/strategy_build_queue_manager.py:37-49`
**Issue:** Two identical `_get_registries()` functions exist as module-level functions with identical implementations:

```python
_cached_registries = None

def _get_registries() -> 'GameRegistries':
    global _cached_registries
    if _cached_registries is None:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        _cached_registries = GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
        )
    return _cached_registries
```

Both were added in PROJ-211. This is a textbook copy-paste duplication that has divergence risk.

**Impact:** Two separate caches for the same data. Bug fixes to one copy won't reach the other. Two separate `GameRegistries` instances are created unnecessarily.
**Recommendation:** Extract to a shared utility (e.g., `game/core/registry.py` already has `get_default_registry_provider()`; add a `get_default_registries()` function there). Both call sites import from the same place.
**Effort:** Simple

---

#### MAJOR: Inconsistent Event Handler Method Names (handle_event vs process_event)

**ID:** IH-05
**Location:** All UI widget and screen classes in `game/ui/`
**Issue:** UI components use two different names for the same concept -- processing a pygame event:

- `handle_event()`: 39 occurrences across 34 files (panels, widgets, screens, builder, test_lab)
- `process_event()`: 17 occurrences across 17 files (windows, dialogs, panels)

The split appears to be partially correlated with class type: "window" classes tend to use `process_event`, while "screen/panel" classes tend to use `handle_event`, but this is not consistent. For example, `system_tree_panel.py` uses `process_event` while `race_identity_panel.py` uses `handle_event`.

Furthermore, the return type annotations are inconsistent even within `handle_event`:
- 6 files: `-> bool` (returns whether event was consumed)
- 24 files: no return annotation (implicitly returns None or bool)
- 3 files: `-> None` (explicitly returns nothing)

**Impact:** Impossible to grep for "the event handling method" without checking both names. No uniform contract for whether the method returns a consumption flag.
**Recommendation:** Standardize on `handle_event(self, event) -> bool` everywhere. The bool return (event consumed) is the more useful contract. Rename all `process_event` to `handle_event`.
**Effort:** Medium

---

#### MAJOR: Two BattleConfig Classes in Different Modules

**ID:** IH-06
**Location:** `game/core/config.py:111` and `game/simulation/battle_config.py:27`
**Issue:** Two classes named `BattleConfig` exist in different modules:

1. `game.core.config.BattleConfig` - A namespace class holding static constants (TARGET_QUERY_RADIUS, COLLISION_BUFFER, RAMMING_DAMAGE_FACTOR, etc.)
2. `game.simulation.battle_config.BattleConfig` - A `@dataclass` holding per-battle instance configuration (mode, seed, max_ticks, headless, etc.)

These serve fundamentally different purposes but share the same name, creating confusion for developers and making imports ambiguous.

**Impact:** `from game.core.config import BattleConfig` and `from game.simulation.battle_config import BattleConfig` are two different classes. IDE auto-import will pick one arbitrarily.
**Recommendation:** Rename `game.core.config.BattleConfig` to `CombatConstants` or `BattleConstants` to distinguish it from the per-instance configuration dataclass.
**Effort:** Simple

---

#### MINOR: Inconsistent Dependency Injection for Registries (Required vs Optional)

**ID:** IH-07
**Location:** All engine and service constructors across `game/simulation/` and `game/strategy/`
**Issue:** Constructor signatures for the `registries` parameter vary in three ways:

1. **Required keyword-only** (`*, registries: GameRegistries`) - 4 files: `ResupplyEngine`, `ResourceManagementEngine`, `EmpireEconomyCalculator`, `Ship.__init__`
2. **Required keyword-only with type hint** (`*, registries: 'GameRegistries'`) - 5 files: `ShipValidator`, `DesignLoader`, `MaintenanceEngine`, `Component`, etc.
3. **Optional positional/keyword** (`registries=None` or `registries: Optional[...] = None`) - 12+ files: `ProductionEngine`, `HarvestingEngine`, `ConflictResolutionEngine`, `Fleet.from_dict`, `Empire.from_dict`, `ShipInstance`, etc.

The PROJ-211 migration moved toward required DI, but many older call sites still accept `None` with fallback behavior.

**Impact:** Inconsistent contracts make it unclear whether registries are truly required. Optional registries with fallbacks mean DI can silently fail in some paths.
**Recommendation:** Complete the PROJ-211 migration: make `registries` required (`*, registries: GameRegistries`) in all constructors. Remove all `Optional` + fallback patterns.
**Effort:** Medium

---

#### MINOR: Inconsistent Use of IRegistryProvider vs GameRegistries

**ID:** IH-08
**Location:** `game/ui/services/` (uses IRegistryProvider), `game/simulation/` and `game/strategy/engine/` (uses GameRegistries)
**Issue:** Two DI mechanisms coexist:

1. **IRegistryProvider protocol** (`game/core/protocols.py`) - interface with `get_components()`, `get_modifiers()`, etc. Used primarily in UI services (125 references in 20 files).
2. **GameRegistries dataclass** (`game/core/registry.py`) - frozen container with direct attribute access. Used primarily in simulation and strategy engines (120 references in 30+ files).

`GameRegistries` now implements the `IRegistryProvider` interface (PROJ-211), but the two approaches create confusion about which to accept in function signatures. Some code constructs `GameRegistries` from an `IRegistryProvider`, adding unnecessary indirection.

**Impact:** A function accepting `IRegistryProvider` cannot use `.components` directly. A function accepting `GameRegistries` excludes alternative providers. The adapter pattern between them (`_get_registries()`) is copy-pasted.
**Recommendation:** Since `GameRegistries` already implements `IRegistryProvider`, consider standardizing on `GameRegistries` as the single DI type. The Protocol can remain for backward compatibility but new code should accept `GameRegistries`.
**Effort:** Medium

---

#### MINOR: Mixed PEP 585 and typing Module Generic Types

**ID:** IH-09
**Location:** Across all `game/` modules
**Issue:** Most of the codebase (139 files) imports generic types from `typing` (e.g., `List`, `Dict`, `Tuple`, `Optional`). However, 20+ files use Python 3.9+ lowercase generics (`list[...]`, `dict[...]`, `tuple[...]`). Notable examples:

- `game/strategy/data/race_config.py`: Uses `tuple[bool, str]` in some methods
- `game/ui/panels/race_environment_panel.py`: 10 occurrences of lowercase generics
- `game/simulation/components/modifiers.py`: 10 occurrences
- `game/strategy/data/homeworld_presets.py`: 12 occurrences

**Impact:** Style inconsistency. Not a functional issue, but makes the codebase look like it was written at different times with different conventions.
**Recommendation:** Either migrate everything to PEP 585 lowercase generics (preferred for modern Python) or keep `typing` imports. Pick one and enforce with a linter rule.
**Effort:** Simple (but many files to touch)

---

#### MINOR: Raw ValueError/TypeError Raised Instead of Custom Exceptions

**ID:** IH-10
**Location:** `game/strategy/data/fleet_capability_calculator.py`, `game/strategy/engine/command_handlers.py`, `game/strategy/data/ship_instance.py`, `game/simulation/entities/ship_loader.py`, `game/simulation/components/component.py`, `game/ui/screens/builder/modifier_logic.py`, `game/simulation/components/abilities/base.py`
**Issue:** Despite a well-designed custom exception hierarchy (PROJ-45: `GameException` -> `ValidationException`, `StateException`, `ComponentException`, etc.), 12+ locations still raise raw `ValueError`, `TypeError`, or `RuntimeError`.

Examples:
- `fleet_capability_calculator.py:72` raises `ValueError` -- should be `ValidationException`
- `command_handlers.py:175,178` raises `ValueError` -- should be `StateException` or `ValidationException`
- `ship_loader.py:136`, `component.py:566,672` raises `ValueError("registry_provider is required (PROJ-211: no fallback)")` -- should be `ValidationException` with `ErrorCode`
- `modifier_logic.py:57` raises `RuntimeError` -- should be `ComponentException`
- `abilities/base.py:374` raises `TypeError` -- should be `ComponentException`

**Impact:** Generic exceptions bypass the structured error handling. Callers catching `GameException` or `ValidationException` will miss these errors. Error codes and context dicts are lost.
**Recommendation:** Replace all raw exception raises with appropriate custom exception classes, using ErrorCode where applicable.
**Effort:** Simple

---

#### INFO: UI Layer Bypasses Strategy Facade, Accesses Domain Objects Directly

**ID:** IH-11
**Location:** `game/ui/screens/*.py` importing from `game/strategy/data/`
**Issue:** A strategy facade pattern exists (`game/strategy/facade/`) with immutable DTOs (`FleetInfo`, `PlanetInfo`, `SystemInfo`, `EmpireInfo`), but only 4 UI files use it:
- `strategy_fleet_ops.py` (FleetInfo)
- `strategy_screen.py` (StrategySessionFacade)
- `strategy_colonization.py` (StrategySessionFacade)
- `strategy_superweapons.py` (StrategySessionFacade)

Meanwhile, 17+ UI files import domain objects directly from `game.strategy.data.*` (Fleet, Empire, Planet, Galaxy), bypassing the facade entirely. This includes `build_queue_controller.py`, `empire_build_queue_window.py`, `strategy_build_queue_manager.py`, and others.

**Impact:** The facade pattern provides immutable snapshots and decouples UI from domain internals, but its partial adoption means most UI code still has direct mutable access to domain objects.
**Recommendation:** This is likely a known partial migration. Continue migrating UI code to use the facade DTOs. Prioritize screens that mutate domain objects directly.
**Effort:** Complex

---

#### INFO: Inconsistent Layer Iteration (ship.iter_components vs iter_components from core.patterns)

**ID:** IH-12
**Location:** `game/simulation/` uses `ship.iter_components()`, `game/strategy/` uses `iter_components(design_data)` from `game.core.patterns`
**Issue:** Two approaches for iterating over ship components:

1. **Object method**: `ship.iter_components()` (in `game/simulation/`) - yields `(LayerType, Component)` tuples from a hydrated `Ship` object
2. **Standalone function**: `iter_components(design_data)` (from `game/core/patterns/layer_iterator.py`) - yields raw component entries from a `dict` (design_data)

Some strategy code also does manual `for layer_type, layer_data in ship.layers.items()` loops (14 occurrences) instead of using either helper.

**Impact:** The two approaches serve different contexts (hydrated Ship vs raw dict data), so this is partially by design. However, the manual `.layers.items()` loops duplicate logic that `ship.iter_components()` encapsulates.
**Recommendation:** Replace manual `.layers.items()` loops with `ship.iter_components()` where possible. The two helper approaches (object method vs standalone function) serve different use cases and can coexist.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **IH-01 (CRITICAL):** Strategy engine ABC interfaces not implemented by 6 of 10 engines - simple mechanical fix with high value for DI/testing
2. **IH-04 (MAJOR):** Duplicate `_get_registries()` copy-paste - simple extraction, eliminates redundant caching
3. **IH-06 (MAJOR):** Two `BattleConfig` classes with same name - simple rename prevents import confusion
4. **IH-05 (MAJOR):** `handle_event` vs `process_event` naming split - medium effort but high impact on discoverability
5. **IH-03 (MAJOR):** Mixed `ValidationResult` and `Tuple[bool, str]` returns - medium effort, aligns with existing PROJ-21 consolidation direction
