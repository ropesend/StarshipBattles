# Data Architect Report: JSON Data Migration & Legacy Cleanup (Phase 1 & 4)

## Executive Summary
This report analyzes the current state of JSON data structures, ship serialization logic, and ability-system integration. While the structural shift to an ability-based model is largely complete, significant "bridge logic" and legacy initializations remain. Critical gaps in state persistence during serialization were also identified, which will cause state loss during save/load operations.

---

## 1. Serialization & Persistence Gaps (Phase 4)

### 1.1 Volatile Resource State
The `Ship.to_dict` method correctly captures component configurations and expected stats but fails to serialize the **current value** of the `ResourceRegistry`.
*   **Location:** `game/simulation/entities/ship.py` -> `to_dict()`
*   **Impact:** Any ship loaded via `from_dict` will have its fuel, ammo, and energy reset to full (or recalculated defaults), regardless of its state when saved. This breaks combat persistence.
*   **Recommendation:** Update `to_dict`/`from_dict` to include `ship.resources.get_value(name)` for all registered resources.

### 1.2 Serialization Redundancy
`Ship.to_dict` saves a large `expected_stats` block. While useful for "mismatch warnings" in `from_dict`, it stores data that is 100% derivable from the component list.
*   **Impact:** Minor maintenance overhead. If the stat calculation logic changes, old saves may trigger false-positive warnings.

---

## 2. Legacy Cleanup & Logic Duplication (Phase 4)

### 2.1 Conflicting Field Initializations
In `Ship.__init__`, core targeting and defense stats are initialized twice with conflicting default values.
*   **Location:** `ship.py`, Lines 264-265 (initialized to `0.0`) and Lines 313-315 (initialized to `1.0`).
*   **Impact:** Potential for non-deterministic behavior if different parts of the code access these before the first `recalculate_stats` call. 
*   **Recommendation:** Remove the duplicate initialization at Lines 264-265. Use `1.0` as the baseline multiplier.

### 2.2 Brittle Ability Bridge
`Component._instantiate_abilities` (Lines 240-245) contains hardcoded string-to-class name mappings for `FuelStorage`, `EnergyStorage`, etc.
*   **Impact:** High architectural debt. These mappings already exist as lambda factories in `ABILITY_REGISTRY` (`abilities.py`). 
*   **Recommendation:** Remove the manual mapping in `component.py` and rely entirely on `create_ability`, ensuring the `ABILITY_REGISTRY` is the single source of truth for name-to-class resolution.

---

## 3. JSON Schema & Data Invariants (Phase 1)

### 3.1 Inconsistent Ability Property Naming
There is a high degree of variance in how ability values are named in the schema and handled in code (`amount`, `value`, `thrust_force`, `capacity`, `max_amount`, `rate`).
*   **Location:** `ship_stats.py` -> `calculate_ability_totals` (Lines 588-594).
*   **Impact:** Requires a complex `if/elif` chain for even simple aggregations.
*   **Recommendation:** Standardize the ability object schema in `abilities.json` (or internal registry) to use a unified `primary_value` key where applicable, or a mapping field in the Ability class.

### 3.2 Redundant Modifier Data
Several entries in `components.json` (e.g., `emissive_armor`, `crystalline_armor`) contain `modifiers: []`.
*   **Impact:** Low. Data clutter. These components rely on internal abilities for their scaling, and active modifiers are handled by the `RegistryManager` at runtime.

### 3.3 Hardcoded Fallback Registry
`load_vehicle_classes` (Line 185) contains a hardcoded dictionary of default ship classes.
*   **Impact:** High. If `vehicleclasses.json` is missing or corrupted, the game falls back to a "ghost" schema that may not match the rest of the simulation logic (e.g., missing layer configs).
*   **Recommendation:** Move these fallbacks to a `defaults/vehicleclasses_baseline.json` file.

---

## 4. Phase Migration Checklist Status

| Task | Status | Notes |
| :--- | :--- | :--- |
| Component Schema Migration | **Partial** | Abilities are decoupled, but naming is inconsistent. |
| Ship Serialization (to/from dict) | **Needs Fix** | Missing Resource State persistence. |
| Legacy Shim Removal | **Partial** | Redundant hit-profile fields identified. |
| Formula System Integration | **Complete** | Math formulas are correctly evaluated via context. |

---
**Report compiled by:** Data Architect (Swarm Node)
**Status:** Analysis Complete
