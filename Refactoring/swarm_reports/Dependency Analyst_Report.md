# Dependency Analyst Report

**Date:** 2026-01-04
**Subject:** Dependency Analysis of `component.py` and `ship.py`
**Focus:** Circular Imports, Global State Dependencies, Module Initialization

## Executive Summary
The analysis of `game/simulation/components/component.py` and `game/simulation/entities/ship.py` reveals significant architectural fragility due to **recursive dependency cycles**, **reliance on global mutable state**, and **order-dependent initialization**. 

The code relies heavily on local (inside function) imports to bypass top-level circular dependencies, indicating that the module boundaries are not cleanly defined. Furthermore, logic is tightly coupled to global registries (`COMPONENT_REGISTRY`, `VEHICLE_CLASSES`) which poses strict limits on testability and modularity.

## Detailed Analysis: `component.py`

### 1. Circular Import Evasion (High Severity)
The `Component` class is tightly coupled to the `ResourceManager`, `Ability` system, and `Modifier` system. To avoid `ImportError` due to circular dependencies, imports are deferred to function scopes. This pattern hides dependencies and makes static analysis difficult.

*   **`__init__`**: Imports `MODIFIER_REGISTRY` from itself (likely to ensure visibility if imported elsewhere).
*   **`get_abilities`**: Imports `ABILITY_REGISTRY` locally.
*   **`_instantiate_abilities`**: Imports `ABILITY_REGISTRY` and `create_ability` from `resource_manager`.
*   **`update` / `can_afford_activation` / `consume_activation`**: Imports `ResourceConsumption` from `resource_manager`.
*   **`recalculate_stats` -> `_calculate_modifier_stats`**: Imports `apply_modifier_effects` from `modifiers`.
*   **`_apply_base_stats`**: Imports `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration` from `resource_manager`.

**Impact:** The `Component` class effectively knows about too many high-level systems. It acts as a hub that pulls in logic from systems that should ideally be operating *on* components, rather than components operating on themselves via these systems.

### 2. Global State Dependencies (Critical)
*   **`MODIFIER_REGISTRY`**: A global dictionary at the module level.
*   **`COMPONENT_REGISTRY`**: A global dictionary at the module level.
*   **`COMPONENT_TYPE_MAP`**: Hardcoded mapping of strings to classes.

**Impact:** Tests running in parallel or sequentially without strict teardown will suffer from state pollution. If `load_components` is called twice, it modifies the global dictionary in place.

### 3. Module Initialization
*   **`load_components` / `load_modifiers`**: These functions rely on relative file paths or `os.getcwd()`. This makes the code brittle when run from different directories (e.g., test runners vs. game launch).
*   **Implicit Order**: Components check `MODIFIER_REGISTRY` during `__init__`. If modifiers are not loaded *before* components are instantiated, the components will spawn without modifiers, potentially silently failing or behaving incorrectly.

## Detailed Analysis: `ship.py`

### 1. Global State Dependencies (Critical)
*   **`VEHICLE_CLASSES`**: A global dictionary storing ship class definitions.
*   **`_VALIDATOR` / `VALIDATOR`**: A module-level instance of `ShipDesignValidator`.
*   **`Ship` Class Coupling**: The `Ship` class directly accesses `VEHICLE_CLASSES` in `__init__`, `update_derelict_status`, `recalculate_stats`, and `change_class`.

**Impact:** The `Ship` entity cannot be instantiated meaningfully without the global `VEHICLE_CLASSES` being populated. This makes unit testing `Ship` logic difficult without bootstrapping the entire vehicle data layer. `initialize_ship_data` is a facade that mutates this global state.

### 2. Validation Coupling
*   The `Ship` class is coupled to a global `_VALIDATOR` instance. This makes it impossible to inject a different validator (e.g., a lax validator for testing or a strict one for gameplay) without monkey-patching the global.

### 3. Circular Import Evasion
*   **`max_weapon_range`**: Local import of `SeekerWeaponAbility`. This suggests `Ship` needs to know about specific Ability implementations, breaking the abstraction of the Ability system.

## Findings & Recommendations

### Issue 1: The "Registry Trap"
**Observation:** Both files use global dictionaries (`REGISTRY = {}`) populated by `load_*` functions.
**Risk:** High probability of test interference (State Pollution).
**Recommendation:** 
*   Adopt the **RegistryManager** pattern as proposed in the Refactor Plan. 
*   Move registries into a scoped container that can be instantiated and discarded per test/session.

### Issue 2: Hidden Dependencies via Local Imports
**Observation:** `Component` imports `ResourceManager` logic inside its update loop.
**Risk:** Performance overhead (minor) and architectural obscurity (major). Logic regarding *how* a resource is consumed is leaking into the data container (`Component`).
**Recommendation:**
*   Refactor `Component` to be a pure data container/state machine.
*   Move the update/consumption logic into a `System` (e.g., `ResourceSystem` or `AbilitySystem`) that iterates over components. This resolves the circular dependency by having the System import both Component and Resource definitions, while Component remains ignorant of the System.

### Issue 3: Hardcoded Data Loading
**Observation:** `load_vehicle_classes` and `load_components` have hardcoded fallback logic for file paths.
**Risk:** fragile initialization in CI/CD or distinct runtime environments.
**Recommendation:**
*   Pass configuration/data paths into the initialization system explicitly.
*   Decouple "Data Loading" from "Registry Population".

## Conclusion
The current implementation allows for functional gameplay but presents severe blocks to reliable testing and clean refactoring. The priority must be to **encapsulate the global registries** and **break the dependency cycles** by extracting logic out of the Entity/Component classes and into Systems.
