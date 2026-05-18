# PROJ-447 Phase 2: Stale-comment cleanup (simulation + AI + interfaces)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-447 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None (independent of other phases)
**Objective:** Rewrite 8 inline docstrings/comments across `game/simulation/`, `game/ai/`, and `game/strategy/interfaces/` that narrate retired surfaces (`carried_items`, `cargo_contents`, `AreaEffectManager`, `BattleController slated for deletion`, etc.). Pure docstring polish; no behavior change; no test impact.

**Cross-bucket file-ownership rule:** Only edit `game/simulation/`, `game/ai/`, and `game/strategy/interfaces/`. **F-D-024 (`game/strategy/services/fleet_speed_calculator.py:175`) is DEFERRED to PROJ-445 Phase 3 Task 3.8** — that file is PROJ-445's territory, and PROJ-445's agent will fold the fix into its F-B-016 sibling work.

**Source-of-truth findings:** [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-001 (codex seed), F-D-002 (codex seed), F-D-009, F-D-010, F-D-021, F-D-022, F-D-023, F-D-026.

---

## Tasks

### Task 2.1: F-D-001 — Rewrite SimulationDesignLoader class docstring (codex seed) [Simple]
**File:** `game/simulation/services/design_loader.py:39`

- [ ] Read class docstring at design_loader.py:39 — currently "Strategy layer code should use `DesignLibrary.load_design_data()` to get raw design data without creating Ship objects."
- [ ] Confirm via `git grep -n "class DesignLibrary"` that `DesignLibrary` is truly deleted (verified by codex consult 2026-05-18)
- [ ] Read the current canonical surface: `DesignRepository.load_design_data(design_id)` at `game/strategy/systems/design_repository.py:280` and `DesignCatalog.load_design_data` at `game/strategy/systems/design_catalog.py:236`
- [ ] **GREEN**: Replace "use `DesignLibrary.load_design_data()`" with "use `DesignRepository.load_design_data(design_id)` (engine-internal) or `DesignCatalog.load_design_data` (workshop/UI-facing)"
- [ ] No test change.

### Task 2.2: F-D-002 — One-word swap on ship_stats.py carried_items comment (codex seed) [Simple]
**File:** `game/simulation/entities/ship_stats.py:208-211`

- [ ] Read existing inline comment: "depends on what's in `ShipInstance.carried_items` and is exposed via `ShipInstance.bay_current_mass` / `ShipCargoManager.get_vehicle_bay_capacity()`"
- [ ] **GREEN**: Replace `ShipInstance.carried_items` with `ShipInstance.bay_inventory.bay` (one-word swap). Keep the rest of the comment as-is.
- [ ] No test change.

### Task 2.3: F-D-009 — Battle runner "slated for deletion" lie [Simple]
**File:** `game/simulation/battle_runner.py:8-12`

- [ ] Read existing module docstring claiming `BattleController` / `BattleConfig` / `BattleMode` are "slated for deletion in the same phase"
- [ ] Verify the lie: `git grep -n "BattleController\|BattleConfig\|BattleMode" game/` should show active production use (`game/app.py:366`, `game/screen_router.py:482-503`, `game/ui/screens/battle_screen.py:28`, `game/ui/screens/test_lab/screen.py:429-477`)
- [ ] **GREEN**: Replace with: "The legacy `BattleController` + `BattleConfig` + `BattleMode` chain remains the visual-mode and replay-replay path; this entry covers headless / spec-in run_battle. A future project to retire the legacy chain remains open."
- [ ] No test change.

### Task 2.4: F-D-010 — Rewrite IEnvironmentalHazardEngine docstring + uncompileable example [Simple]
**File:** `game/strategy/interfaces/engines/combat.py:82, 87`

- [ ] Read the existing docstring claiming `AreaEffectManager` queries + the example showing `engine = EnvironmentalHazardEngine(area_effect_manager)`
- [ ] Confirm `AreaEffectManager` is deleted: `game/strategy/engine/environmental_hazard_engine.py:6, 58` should say "no longer takes AreaEffectManager"; `docs/04_SERVICES.md:602` and `docs/systems/strategy_layer.md:1134` confirm deletion
- [ ] **GREEN — docstring**: Replace the `AreaEffectManager` bullet with: "Querying ability_iterator / SystemEffectsCollector at fleet locations for environmental effects"
- [ ] **GREEN — example**: Replace `engine = EnvironmentalHazardEngine(area_effect_manager)` with `engine = EnvironmentalHazardEngine()` (current constructor signature per `environmental_hazard_engine.py:58`)
- [ ] No test change.

### Task 2.5: F-D-021 — Rename _pop_carried_vehicles_legacy + drop stale narration [Simple]
**File:** `game/ai/carrier_controller.py:275-279`

- [ ] Read the method `_pop_carried_vehicles_legacy` — the name says "legacy" but the docstring describes the modern typed-bay path. The "legacy" suffix is misleading.
- [ ] **GREEN — rename**: `_pop_carried_vehicles_legacy` → `_pop_carried_vehicles_count_based` (matches the docstring's "Legacy count-based pop" intent — the legacy aspect is the API shape, not the substrate). Update internal callers.
- [ ] **GREEN — drop stale narration**: Edit the docstring to keep only the current-behavior description. Drop the second half: "The legacy `carried_items` / `CarriedVehicle.from_any` discriminator path is gone."
- [ ] Run `git grep -n "_pop_carried_vehicles_legacy"` to confirm all callers updated.
- [ ] Run targeted tests: `pytest tests/unit/ai/test_carrier_controller.py -v`.

### Task 2.6: F-D-022 — One-word swap on launch.py stat_contributor docstring [Simple]
**File:** `game/simulation/entities/stat_contributors/launch.py:111`

- [ ] Read existing `contribute_vehicle_bay` docstring mentioning `ShipInstance.carried_items`
- [ ] **GREEN**: Replace `ShipInstance.carried_items` with `ShipInstance.bay_inventory.bay`. One-word swap.

### Task 2.7: F-D-023 — Drop "Generalises the previous" migration narration [Simple]
**File:** `game/simulation/components/abilities/vehicle_bay.py:5`

- [ ] Read existing module docstring claim: "Generalises the previous drop-pod-specific `carried_items` flow into a typed substrate."
- [ ] **GREEN**: Reword to current-state-only: "Typed substrate for design-backed vehicles (mines / fighters / satellites) stored in `BayInventory.bay`. Mass is the capacity gate."
- [ ] Drop the "Generalises the previous" historical framing; a fresh reader shouldn't have to parse migration archaeology.

### Task 2.8: F-D-026 — Trim SimulationDesignLoader module docstring [Simple]
**File:** `game/simulation/services/design_loader.py:1-13`

- [ ] Read existing module docstring — heavy with PROJ-30 / PROJ-45 / PROJ-50 historical provenance
- [ ] **GREEN**: Replace with a 2-3 line current-behavior description. Drop the multi-project archaeology. Keep nothing older than PROJ-422 (the strategy tech-debt cluster anchor).

---

## Phase Completion Checklist

- [ ] All 8 stale-comment sites rewritten to describe current behavior
- [ ] `_pop_carried_vehicles_legacy` renamed; all callers updated
- [ ] No remaining `ShipInstance.carried_items` or `_cargo_contents` references in `game/simulation/` / `game/ai/` outside historical/changelog context (run `rg "carried_items|_cargo_contents" game/simulation/ game/ai/` to verify — PowerShell-friendly)
- [ ] F-D-024 (fleet_speed_calculator.py:175) explicitly noted as DEFERRED to PROJ-445 F-B-016 in decisions.md
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-447 2` — PASSED
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 3

## Notes

- Pure docstring + comment polish. No production behavior changes.
- F-D-024 is the only finding in this phase deferred to a sibling project (PROJ-445). The deferral exists because `game/strategy/services/fleet_speed_calculator.py` is in PROJ-445's bucket; touching it violates the parallelism partition.
- If you find additional stale comments while editing (other deleted-class references, other PROJ-30-era archaeology): log via `/claude-di-log` or note in decisions.md; do NOT fix inline (keep Phase 2 narrowly scoped).
