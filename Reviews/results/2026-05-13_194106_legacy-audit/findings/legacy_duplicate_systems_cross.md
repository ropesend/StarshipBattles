# Cross-System Duplicate-Systems Report

## Summary
- Pairs Analyzed: 12
- Clear Legacy: 0
- Ambiguous: 0
- Intentional Split (NOT findings): 12
- Total Findings: 0
- Critical: 0 | Major: 0 | Minor: 0 | Info: 0

**Key conclusion:** The codebase exhibits strong architectural discipline. Every candidate pair identified through method-overlap analysis, registry scanning, and loader/comparator hunting proved to be an intentional architectural split — most are explicitly documented in `docs/01_ARCHITECTURE.md` or `docs/02_PATTERNS.md`. Recent consolidation efforts (PROJ-204, PROJ-269, PROJ-274) have eliminated the last real duplicates, and the Phase 1 name_pair_drift finding is a false positive.

---

## Phase 1 Name-Pair Drift Validation

### 1. `ModifierManager` vs `ModifierService`

| | ModifierManager | ModifierService |
|---|---|---|
| **File** | `game/simulation/components/modifier_manager.py:30` | `game/simulation/services/modifier_service.py:16` |
| **Role** | Stateful per-Component delegate — owns `_modifiers` list | Cross-cutting validation service — modifier rules |
| **Shared methods** | `__init__` only (trivial, all classes have it) | |

**Analysis:**

- `ModifierManager` owns the per-component modifier lifecycle: `add_modifier()`, `remove_modifier()`, `get_modifier()`, `get_all_effects()`, `get_stat_summary()`. It is a **stateful delegate** following the `ComponentHealthManager`/`ComponentResourceManager` pattern (Pattern #5 Facade/Delegate).
- `ModifierService` handles cross-cutting modifier rules: `is_modifier_allowed()`, `get_mandatory_modifiers()`, `ensure_mandatory_modifiers()`, `get_initial_value()`, `get_local_min_max()`. It is a **validation/rules service** with no per-instance state.
- They share zero methods beyond `__init__` (which is universal). The AST detector was misled by the `manager_service_overlap` rule matching two classes with different suffix conventions in the same subsystem.

**Verdict: Intentional Split — NOT a finding**

The two classes serve genuinely different concerns within the simulation layer. `ModifierManager` is a Component delegate (owns state), while `ModifierService` is a horizontal service (validates rules). Consolidation would violate the Facade/Delegate pattern and the single-responsibility principle.

---

## Narrative Pairs (Phase 1 did not catch)

Each candidate pair below was investigated through method-overlap analysis, responsibility mapping, and architectural documentation cross-reference.

### 1. Two BattleSpec Compilers
| Candidate A | Candidate B |
|---|---|
| `build_manual_battle_spec()` | `build_strategy_battle_spec()` |
| `game/ui/screens/battle_setup/spec_compiler.py:91` | `game/strategy/combat/spec_compiler.py:78` |

**Overlap:** Both produce frozen `BattleSpec` DTOs consumed by `run_battle()`.

**Resolution:** This is **Pattern #13 (Spec Compiler + run_battle)** — explicitly documented architecture. Each compiler translates a different domain source (UI fleet-setup state vs strategy fleet/infrastructure state) into the same frozen DTO. The architecture doc states: "Caller-specific compilers emit frozen BattleSpec DTOs." The three compilers (plus Combat Lab's `build_test_battle_spec`) share the same output contract but differ in input domain.

**Verdict: Intentional Split**

---

### 2. `DesignLibrary` vs `SimulationDesignLoader`
| Candidate A | Candidate B |
|---|---|
| `DesignLibrary` | `SimulationDesignLoader` |
| `game/strategy/systems/design_library.py:99` | `game/simulation/services/design_loader.py:31` |

**Overlap:** Both read design JSON files. `DesignLibrary` has `load_design_data()`, `scan_designs()`, `save_design()`. `SimulationDesignLoader` has `load_ship_from_design_data()`, `load_ship_from_file()`.

**Resolution:** Architecture docs explicitly separate these:
- `DesignLibrary` — strategy layer: file management, metadata (obsolete marking, built-count tracking), raw dict loading. "Strategy layer code should use DesignLibrary.load_design_data() to get raw design data without creating Ship objects."
- `SimulationDesignLoader` — simulation layer: creates `Ship` simulation entities from design data. Has DI through `GameRegistries`.

**Verdict: Intentional Split**

---

### 3. `ShipFactory` vs `VehicleDesignService`
| Candidate A | Candidate B |
|---|---|
| `ShipFactory` | `VehicleDesignService` |
| `game/ui/services/ship_factory.py:28` | `game/simulation/services/vehicle_design_service.py:37` |

**Overlap:** Both create `Ship` objects and have methods operating on them.

**Resolution:** They serve completely different UI workflows:
- `ShipFactory`: Battle setup — creates Ships from designs for combat, configures positions/angles/formations. Methods: `create_from_design()`, `configure_ship()`, `setup_formation()`.
- `VehicleDesignService`: Design workshop — creates/edits/validates ship designs. Methods: `create_ship()`, `add_component()`, `remove_component()`, `move_component()`, `change_class()`, `validate_design()`.
- `ShipFactory` has 0 methods shared with `VehicleDesignService` beyond `create_from_design()` / `create_ship()` which have different signatures and semantics.

**Verdict: Intentional Split**

---

### 4. `ResourceRegistry` (simulation) vs `ResourceCatalog` (core)
| Candidate A | Candidate B |
|---|---|
| `ResourceRegistry` | `ResourceCatalog` |
| `game/simulation/systems/resource_manager.py:101` | `game/core/resources.py:47` |

**Overlap:** Both are named "resource" registries.

**Resolution:** Fundamentally different:
- `ResourceRegistry`: Per-ship **runtime state** — tracks fuel/energy/ammo current values, regeneration, consumption. Lives on `Ship.resources`.
- `ResourceCatalog`: Static **type definitions** — what resources exist (metals, organics, fuel, etc.), loaded once from `data/resources.json`. Used by `GameRegistries`.
- No method overlap at all.

**Verdict: Intentional Split**

---

### 5. `FleetAuraManager` (simulation) vs `CombatModifierCollector` (strategy)
| Candidate A | Candidate B |
|---|---|
| `FleetAuraManager` | `CombatModifierCollector` |
| `game/simulation/combat/fleet_aura_manager.py:70` | `game/strategy/services/combat_modifier_collector.py:38` |

**Overlap:** Both aggregate combat-affecting modifiers.

**Resolution:** Different timing and scope:
- `FleetAuraManager`: **In-battle** per-tick aura/projection application on ships. Reads `ModifierStack` entries → populates `ship.external_stats`.
- `CombatModifierCollector`: **Pre-battle** strategic modifier collection (facility-based ShieldModifier, DamageModifier, ShieldProjection). Feeds into the strategy spec compiler's ModifierStack.
- Documented as part of Pattern #29 (Universal Ability Source) and Pattern #24 (External-Stats Bridge).

**Verdict: Intentional Split**

---

### 6. `ability_aggregator.py` (simulation) vs `StrategicAbilityScanner` (strategy)
| Candidate A | Candidate B |
|---|---|
| `calculate_ability_totals()` | `find_abilities_in_scope()` |
| `game/simulation/entities/ability_aggregator.py:64` | `game/strategy/services/strategic_ability_scanner.py` |

**Overlap:** Both aggregate abilities across components — one uses two-phase MAX/SUM aggregation, the other uses `aggregate_multipliers()` which does intra-MAX/inter-MULTIPLY.

**Resolution:** Different layers, different scope types, different aggregation rules:
- `ability_aggregator`: Simulation — ship component abilities (combat layer: damage, shield, thrust). Two-phase: MAX within stack_group, SUM across groups.
- `StrategicAbilityScanner`: Strategy — facility/storm/planet abilities across spatial scopes (planet/sector/system). Two-phase: MAX intra-provider, MULTIPLY inter-provider.
- Both use two-phase aggregation but on different entity types with different aggregation operators — this is a deliberate pattern choice (Pattern #14), not a duplicate.

**Verdict: Intentional Split**

---

### 7. `DesignValidator` (strategy) vs `ShipDesignValidator` (simulation)
| Candidate A | Candidate B |
|---|---|
| `DesignValidator` | `ShipDesignValidator` |
| `game/strategy/services/design_validator.py:38` | `game/simulation/validation/ship_validator.py` |

**Overlap:** Both validate ship designs.

**Resolution:** `DesignValidator` is an **adapter** that delegates to `ShipDesignValidator`:
- `DesignValidator.validate()` checks component existence first, then instantiates a `Ship` and runs simulation-layer validation rules. Returns its own `DesignValidationResult`.
- `ShipDesignValidator` has 13+ validation rules (LayerConstraintRule, ClassRequirementsRule, MassBudgetRule, CrewCapacityRule, etc.) — it is the canonical validation engine.
- `DesignValidator` adds a strategy-specific `DesignValidationResult` wrapper and pre-checks. It does not duplicate validation logic.

**Verdict: Intentional Split**

---

### 8. `ComponentInspector` (strategy) vs `ComponentService` (UI)
| Candidate A | Candidate B |
|---|---|
| `ComponentInspector` | `ComponentService` |
| `game/strategy/services/component_inspector.py` | `game/ui/services/component_service.py` |

**Overlap:** Both provide component data access.

**Resolution:** Completely different APIs and callers:
- `ComponentInspector`: Pure functions for strategy-layer validation — extracts abilities from design-data dicts and component objects. Used by strategy validators and engines. Functions: `get_component_abilities()`, `extract_abilities_from_component()`, `ship_has_ability()`, `count_ability()`, `has_warp_capability()`.
- `ComponentService`: UI facade wrapping `IRegistryProvider` — provides `get_all_components()`, `get_modifier_registry()`, `get_modifier_definition()`. Used by UI panels.
- Zero method name overlap.

**Verdict: Intentional Split**

---

### 9. `FleetBattleAdapter` vs `ShipInstanceBridge`
| Candidate A | Candidate B |
|---|---|
| `FleetBattleAdapter` | `ShipInstanceBridge` |
| `game/strategy/data/fleet_battle_adapter.py:33` | `game/strategy/data/ship_instance_bridge.py:25` |

**Overlap:** Both convert strategy ShipInstances to simulation Ships.

**Resolution:**
- `FleetBattleAdapter.to_battle_ships()` iterates an entire Fleet's ships, resolves hierarchy movement/targeting policies, generates default formation positions, and calls `ShipInstance.to_ship()` (which delegates to `ShipInstanceBridge.to_ship()`) for each ship.
- `ShipInstanceBridge.to_ship()` handles a **single** ShipInstance → Ship conversion with damage state application.
- `FleetBattleAdapter` is a Fleet-level orchestrator; `ShipInstanceBridge` is a per-instance bridge. The former delegates to the latter. No duplication.

**Verdict: Intentional Split**

---

### 10. `ShipFactory.setup_formation()` (UI) vs `FormationResolver` (simulation)
| Candidate A | Candidate B |
|---|---|
| `ShipFactory.setup_formation()` | `FormationResolver.resolve()` |
| `game/ui/services/ship_factory.py:135` | `game/simulation/combat/formation.py:94` |

**Overlap:** Both set up ship formations.

**Resolution:**
- `ShipFactory.setup_formation()`: Links follower ships to formation masters for UI battle setup. Uses existing ship positions to calculate offsets.
- `FormationResolver.resolve()`: Generates world-space ship positions from `FormationSpec` (shape + spacing) for the simulation engine. Handles 8 formation shapes (WEDGE, LINE_ABREAST, SCREEN, CARRIER_PROTECTED, etc.).
- `ShipFactory.setup_formation()` is a UI helper for the old manual battle setup path; `FormationResolver` is the canonical engine formation system introduced by PROJ-269 Phase 4.

**Verdict: Intentional Split** (though `ShipFactory.setup_formation()` may be a legacy path worth auditing as the PROJ-269 formation system matures)

---

### 11. `RegistryLoader` vs `WorkshopDataLoader`
| Candidate A | Candidate B |
|---|---|
| `RegistryLoader` | `WorkshopDataLoader` |
| `game/simulation/services/registry_loader.py` | `game/ui/screens/workshop_data_loader.py:33` |

**Overlap:** Both load `components.json`, `modifiers.json`, and `vehicleclasses.json`.

**Resolution:**
- `RegistryLoader`: Simulation service that populates the `RegistryManager` on startup. Reads data files into typed registry dicts.
- `WorkshopDataLoader`: UI helper for the Design Workshop screen. Handles file discovery with priority (test files first, then fallback to default data dir). Drives the "Reload Data" workflow.
- They load the same files but for different lifecycle events (app startup vs UI reload). `WorkshopDataLoader` delegates to `RegistryLoader` for actual registry population.

**Verdict: Intentional Split**

---

### 12. `FleetCargoProjector` vs `CargoTransferService`
| Candidate A | Candidate B |
|---|---|
| `FleetCargoProjector` | `CargoTransferService` |
| `game/strategy/services/fleet_cargo_projector.py:18` | `game/strategy/services/cargo_transfer_service.py:97` |

**Overlap:** Both operate on fleet cargo.

**Resolution:**
- `FleetCargoProjector`: Projects **future** cargo state by simulating queued transfer orders. Used by validators to check "will the fleet have enough cargo after earlier orders?"
- `CargoTransferService`: Handles **actual** transfer command assembly — colony resolution, population extraction, transfer command creation.
- They occupy different phases of the order lifecycle (validation/projection vs execution).

**Verdict: Intentional Split**

---

## Prioritized Consolidation Plan

No findings to consolidate. All 12 pairs analyzed are intentional architectural splits.

The codebase shows excellent hygiene:
- **PROJ-204** consolidated cost calculation (eliminating duplicate paths in `ProductionEngine` and `DesignMetadata`).
- **PROJ-269** consolidated battle spec compilation (replaced ad-hoc ship mutation with three documented compilers → one `run_battle` path).
- **PROJ-274** consolidated ship materialization (replaced six closure variations with `IShipMaterializer` protocol + two implementations).
- **PROJ-382** consolidated stat calculation (`calculate_design_stats()` as single source of truth).

The only low-priority follow-up item is the legacy `ShipFactory.setup_formation()` path in `game/ui/services/ship_factory.py:135`, which handles formation linking for the old manual battle setup flow. As PROJ-269 Phase 4's `FormationResolver` matures and Battle Setup transitions to TaskForce-based formations, this may eventually be removable. Currently it still serves the CUSTOM formation positioning path.
