# Dependency Analyst Report
**Focus:** Circular Import & Dependency Safety
**Date:** 2026-01-04
**Target Files:** `game/simulation/components/component.py`, `game/simulation/entities/ship.py`

## 1. Executive Summary
The analysis reveals a **High Severity** dependency tangle, particularly within `component.py`. The code relies heavily on "local imports" (imports inside methods) to bypass Python's circular import restrictions. This indicates a structural architectural flaw where "Data" classes (`Component`, `Ship`) contain "Logic" that depends on "Systems" (`ResourceManager`, `AbilityRegistry`), which in turn depend on the Data classes.

This circularity creates a fragile runtime environment where import errors may only occur when specific methods are called, rather than at startup.

## 2. Critical Issues

### A. Circular Import Workarounds (Runtime Imports)
The code systematically uses imports within function scopes to avoid `ImportError: cannot import name...`. This is an accepted temporary Python workaround but a major architectural anti-pattern for production code.

**`game/simulation/components/component.py` Findings:**
1.  **`Component.__init__`**: Imports `MODIFIER_REGISTRY` from *itself* (`game.simulation.components.component`). This is bizarre and suggests `MODIFIER_REGISTRY` should be in a separate, lower-level module.
2.  **`Component.get_abilities`**: Imports `ABILITY_REGISTRY` from `abilities`.
3.  **`Component._instantiate_abilities`**: Imports `ABILITY_REGISTRY` and `create_ability` from `resource_manager`.
4.  **`Component.update`**: Imports `ResourceConsumption` form `resource_manager`.
5.  **`Component.can_afford_activation`**: Imports `ResourceConsumption` form `resource_manager`.
6.  **`Component.consume_activation`**: Imports `ResourceConsumption` form `resource_manager`.
7.  **`Component._calculate_modifier_stats`**: Imports `apply_modifier_effects` from `modifiers`.
8.  **`Component._apply_base_stats`**: Imports `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration` from `resource_manager`.

**`game/simulation/entities/ship.py` Findings:**
1.  **`Ship.max_weapon_range`**: Imports `SeekerWeaponAbility` from `abilities`.
2.  **`Ship.recalculate_stats`**: Imports `SeekerWeaponAbility` (via `max_weapon_range`).

### B. Global State & Registry Hazards
The codebase relies on module-level global dictionaries that are mutated at runtime. This "Singleton-by-Global" pattern makes dependency injection impossible and testing difficult (state pollution).

*   **`MODIFIER_REGISTRY`** (`component.py`): Populated by `load_modifiers`. Global mutable state.
*   **`COMPONENT_REGISTRY`** (`component.py`): Populated by `load_components`. Global mutable state.
*   **`VEHICLE_CLASSES`** (`ship.py`): Populated by `load_vehicle_classes`. Global mutable state.
*   **`_VALIDATOR`** (`ship.py`): Global instance of `ShipDesignValidator`.

### C. Hardcoded System Coupling
`Component` is not just a data container; it performs active logic that belongs in a System.
*   The `Component` class knows *too much* about resources. It explicitly handles `trigger == 'activation'` vs `trigger == 'constant'` logic. This logic violates the Single Responsibility Principle and couples usage to the implementation of `ResourceManager`.

## 3. Detailed Recommendations

### Phase 1: Break Circular Cycles via "Forward References" & "Type Checking"
For type hinting, use `if TYPE_CHECKING:` blocks. For runtime logic, `Component` should not import `Ability` or `Resource` logic.

### Phase 2: Refactor to ECS / Data-Logic Separation
The primary cause of the circular imports is that `Component` (Data) tries to execute behavior (Logic) that requires System knowledge.
*   **Action**: Move `update()`, `can_afford_activation()`, and `consume_activation()` **out** of `Component` and into a `ResourceSystem` or `AbilitySystem`.
*   **Result**: `Component` becomes a simple data holder. It no longer needs to import `resource_manager`. `resource_manager` can import `Component` freely. Cycle broken.

### Phase 3: Registry Encapsulation
Move global registries to a `RegistryManager` or dedicated Registry modules (`registries/component_registry.py`) that do not import the classes they store (store Factories or configuration data instead), or use a dependency injection container.

### Immediate "Band-Aid" Fixes (Code Hygiene)
*   Consolidate the repeated local imports of `ResourceConsumption` into a single `TYPE_CHECKING` import and use strict dependency injection or specific methods if full refactor is delayed.
*   Move `MODIFIER_REGISTRY` to a dedicated `game.registries.modifiers` module to allow both `component.py` and loaders to import it without self-referential issues.

---
**Status**: Analysis Complete.
**Verdict**: **High Technical Debt**. The `Component` class effectively functions as a "God Object" regarding dependency linking, acting as the nexus for disparate systems (Abilities, Resources, Modifiers) via fragile runtime imports.
