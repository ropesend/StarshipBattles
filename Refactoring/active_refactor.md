# Active Refactor: Hull Component & Ship Cohesion
**Goal:** Unify Ship stats with V2 Ability System (Hull Component) and eliminate architectural incoherence.

## Status
**Current Phase:** Phase 1 (Data & State Foundations)
**Start Date:** 2026-01-05
**Status:** [PLANNING_COMPLETE]

---

## Migration Map (The Constitution)

| Concept | Legacy State | Target State | Source of Truth |
| :--- | :--- | :--- | :--- |
| **Hull Definition** | `vehicleclasses.json` (hull_mass, hp) | `components.json` ("type": "Hull") | Component Data |
| **Base Mass** | `Ship.base_mass` (manual float) | Sum of `Hull` component + Systems | `ShipStatsCalculator` |
| **Requirements** | Hardcoded checks & `Ship.requirements` | `CrewRequired`, `FuelStorage` Abilities | Ability System V2 |
| **Resource State** | Reset on Load (Volatile) | Persisted in `Ship.resources` | Save Data |
| **UI Layout** | Hardcoded Pixel Overlaps | Responsive/Grid-based | `builder_utils.py` |

---

## Phased Schedule

### Phase 1: Data & State Foundations (The Bedrock)
**Objective:** Fix critical state bugs and prepare data structures.
- [ ] **Critical Fix:** Patch `resource_manager.py` clamping bug (resets to 0 on overflow).
- [ ] **Data Migration:** Create `Hull` components in `data/components.json` for all 18 classes. [Data Architect]
- [ ] **Data Migration:** Add `default_hull_id` to `data/vehicleclasses.json`. [Data Architect]
- [ ] **Serialization:** Update `Ship.to_dict`/`from_dict` to persist `ResourceRegistry` values. [Data Architect]
- [ ] **Cleanup:** Remove hardcoded ability string maps in `Component._instantiate_abilities`.

### Phase 2: Core Logic & Stability (The Engine)
**Objective:** Implement the "Hull as Component" logic and fix core simulation loops.
- [ ] **Refactor:** Update `Ship.__init__` to auto-equip `default_hull_id`. [Core Engineer]
- [ ] **Refactor:** Switch `Ship.mass` and `Ship.hp` to cached properties in `ShipStatsCalculator`.
- [ ] **Refactor:** Implement `CommandAndControl` and `CrewRequired` logic in `update_derelict_status`.
- [ ] **Cleanup:** Remove duplicate To-Hit/Derelict initializations in `Ship.py`.
- [ ] **Cleanup:** Standardize MRO-based identity checks (remove brittle class name checks).

### Phase 3: Test Infrastructure & Verification (The Guardrails)
**Objective:** Restore test isolation and verify unified stats.
- [ ] **Infrastructure:** Restore/Fix `tests/conftest.py` for proper `RegistryManager` isolation. [QA Lead]
- [ ] **New Test:** Create `tests/unit/entities/test_ship_core.py` (Mocked Hull/Stat verification).
- [ ] **Audit:** Verify `Ship` tests typically use `RegistryManager` utilities.

### Phase 4: UI Reconstruction (The Interface)
**Objective:** Resolve layout overlaps and ensure builder compatibility.
- [ ] **Restoration:** Create/Restore `game/ui/screens/builder_utils.py` (Layout constants). [UI Specialist]
- [ ] **Layout Fix:** Implement relative/grid sizing for `builder_screen.py` to fix 1920px overlap.
- [ ] **Layout Fix:** Resolve vertical collision between Weapons Report and Nav Panels.
- [ ] **Logic Fix:** Switch `BuilderSceneGUI` to event-based data sync (stop recreating dropdowns).

### Phase 5: Legacy Purge & Final Polish (The Cleanup)
**Objective:** Remove deprecated data and finalize the refactor.
- [ ] **Cleanup:** Remove `hull_mass` and `requirements` from `vehicleclasses.json`.
- [ ] **Cleanup:** Remove hardcoded ship fallback registry in `load_vehicle_classes`.
- [ ] **Final Verification:** Run Full Gauntlet (Target: 100% Pass).
- [ ] **Definition of Done:**
    - `Ship.py` has ZERO hardcoded mass/hp assignments.
    - `vehicleclasses.json` contains NO physical stats.
    - Ship Builder UI renders without overlap on 1080p+.
    - Save/Load persists fuel/ammo levels correctly.

---

## Test Triage Table
| Test File | Status | Owner | Notes |
| :--- | :--- | :--- | :--- |
| (Empty) | | | |
