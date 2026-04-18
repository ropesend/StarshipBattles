# Phase 4: ShipSpec.scenario_role field — delete _role_from_instance_id substring parsing

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-17)
**Objective:** Add typed `scenario_role: Optional[str]` field to `ShipSpec`. Update `materialize_spec_ships` to read it instead of parsing `instance_id`. Update Combat Lab spec compiler + custom ShipSpec construction sites to populate it. Validate values against `combat_lab_role_registry` at compile time. Delete `_role_from_instance_id` substring parser. The user-visible payoff of Phases 1-3 lands here.

---

## Tasks

### Task 4.1: Add `scenario_role` field to `ShipSpec` [Simple]
**File:** `game/simulation/battle_spec.py`
**Tests:** Existing `tests/unit/simulation/` should still pass (additive change)

- [x] Add `scenario_role: Optional[str] = None` to `ShipSpec`
- [x] Add docstring explaining the field's purpose, source-of-truth registry, and that Battle Setup / Strategy callers leave it None

**Notes:** Field is `Optional[str]` with default `None` so non-Combat-Lab specs work unchanged. ShipSpec is a frozen dataclass — adding a field with default doesn't break existing construction sites.

### Task 4.2: Add 4 baseline/variant roles to scenario_roles.json [Simple]
**File:** `combat_lab/data/scenario_roles.json`
**Tests:** Validated by Phase 3's consistency test (still applies)

- [x] Add `baseline_attacker`, `baseline_target`, `variant_attacker`, `variant_target` entries
- [x] Each with `display_name` and `description`. Empty `vehicle_type_filter`.
- [x] Total roles in registry now: 14 (10 base + 4 ComparisonScenario)

**Notes:** ComparisonScenario uses these 4 roles to distinguish baseline vs variant ships in its A/B comparison. Without them in the registry, the compiler-side validation in Task 4.5 would reject scenarios that use them.

### Task 4.3: Update `materialize_spec_ships` to read `scenario_role` [Medium]
**File:** `game/simulation/battle_runner.py`
**Tests:** Targeted regression covered by Task 4.9

- [x] Replace `if ship_spec.instance_id and ":" in ship_spec.instance_id: role = ship_spec.instance_id.rsplit(":", 1)[1]` with `if ship_spec.scenario_role: ships_by_role[ship_spec.scenario_role] = ship`
- [x] Update docstring to describe new behavior (PROJ-278 Phase 4)

**Notes:** This is the single shared materialization path used by both `run_battle` (headless) and `BattleController.start_from_spec` (visual). Both paths now read the typed field — no caller-side substring parsing remains.

### Task 4.4: Update `_ship_spec` + custom ShipSpec call sites to set `scenario_role` [Medium]
**Files:**
  - `combat_lab/spec_compiler.py` (`_ship_spec` helper — used by all standard templates)
  - `combat_lab/scenarios/tohit_attack_fleet_scenarios.py` (`_ship` closure — fleet-aura tests)
  - `combat_lab/scenarios/propulsion_scenarios.py` (2 sites — multi-mass propulsion tests)
  - `combat_lab/scenarios/templates.py` (ComparisonScenario baseline ship construction — 2 sites)
**Tests:** Existing test_spec_compiler.py tests cover this (after Task 4.8 migration)

- [x] All ShipSpec construction sites now pass `scenario_role=role` alongside the existing `instance_id` field
- [x] `instance_id` format unchanged — retains the `:role` suffix for identity-disambiguation purposes (multiple ships per scenario need unique IDs)
- [x] Variant ships in ComparisonScenario flow through `_ship_spec` so they're covered by the shared helper update

**Notes:** The decision to KEEP the `:role` suffix in `instance_id` is deliberate — it makes IDs uniquely identifiable AND human-readable in logs/outcomes. The contract change is: readers MUST use the field, never parse the string. The historical pattern is now legacy text.

### Task 4.5: Compiler-side validation against combat_lab_role_registry [Simple]
**File:** `combat_lab/spec_compiler.py` (`_ship_spec` helper)
**Tests:** Manual verification

- [x] `_ship_spec` consults `combat_lab_role_registry` and raises `ValueError` if `role` is unregistered
- [x] Error message points the author to the data file
- [x] Lazy import to avoid circular dependency at module load

**Notes:** This catches typos at SCENARIO COMPILE TIME — earlier and louder than the Phase 3 AST consistency test (which catches consumer-side typos via static scan). Together they protect both producer and consumer.

### Task 4.6: Update ComparisonScenario `endswith(":baseline_*")` checks [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** Combat Lab simulation suite (162 scenarios)

- [x] Replace `if ship_spec.instance_id.endswith(":baseline_attacker")` with `if ship_spec.scenario_role == "baseline_attacker"`
- [x] Same for `:baseline_target` check
- [x] Comment marks the change with PROJ-278 Phase 4

**Notes:** ComparisonScenario's ship_builder closure uses scenario_role for baseline-ship routing. Variant-ship routing is handled by the wire_ships method which reads from `ships_by_role` keyed on scenario_role values (which materialize_spec_ships now populates).

### Task 4.7: Delete `_role_from_instance_id` from `combat_lab/runner.py` + update `scenario_run_helper.py` [Simple]
**Files:** `combat_lab/runner.py`, `combat_lab/services/scenario_run_helper.py`
**Tests:** Combat Lab full suite

- [x] Remove `_role_from_instance_id` function from `combat_lab/runner.py` (was lines 27-38)
- [x] Update import in `scenario_run_helper.py` — drop `_role_from_instance_id` from the import
- [x] Replace `role = _role_from_instance_id(ship_spec.instance_id)` with `role = ship_spec.scenario_role` in the ship_builder closure
- [x] Comment marks the change with PROJ-278 Phase 4
- [x] Grep confirms zero remaining call sites to `_role_from_instance_id` in code (only docstring breadcrumb in `battle_spec.py` and historical Projects/docs files)

**Notes:** Two files touched: `combat_lab/runner.py` (delete the helper) and `combat_lab/services/scenario_run_helper.py` (update import + call site). The `_snapshot_ship_state` helper next to the deleted function is unrelated and stays.

### Task 4.8: Update test assertions hardcoding `:role` suffixes [Medium]
**File:** `tests/unit/combat_lab/test_spec_compiler.py`
**Tests:** `pytest tests/unit/combat_lab/test_spec_compiler.py`

- [x] 8 assertions migrated from `instance_id.endswith(":role")` to `scenario_role == "role"`
- [x] Test names updated where they referenced `instance_id` to reflect the new typed field
- [x] Added comment in renamed `test_compiler_duel_ships_carry_scenario_role` explaining the new contract (readers consume field, never parse string)

**Notes:** All 8 hardcoded `endswith(":role")` assertions migrated. The renamed test method documents the new contract for future readers (avoid drift back to string parsing).

### Task 4.9: Regression sweep + docs [Medium]
**Files:** Various; `docs/systems/combat_simulation.md`, `docs/guides/simulation_testing.md`
**Tests:** Phase 4 regression scopes

- [x] `pytest tests/unit/core/ tests/unit/strategy/data/test_design_role_registry*.py tests/unit/combat_lab/ tests/unit/simulation/ tests/unit/ui/` — **7928 passed, zero failures**
- [x] `python -m combat_lab.run_tests --fast` — **162 passed / 0 failed / 0 skipped** (no Combat Lab simulation regression)
- [x] Updated [docs/guides/simulation_testing.md](../../../docs/guides/simulation_testing.md) §"2.5 Scenario Role Labels" — split producer-side / consumer-side, documented two-layer protection (compile-time + test-time), explained `instance_id` legacy text behavior
- [x] Added new section to [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md) — "Combat Lab Scenario Role Tagging (PROJ-278 Phase 4)" right above Component HP Persistence
- [x] Update plan.md phase table

**Notes:** Docs updated as part of Task 4.9.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` still green
- [x] `pytest tests/unit/strategy/data/test_design_role_registry*.py` still green
- [x] `pytest tests/unit/combat_lab/` still green
- [x] `pytest tests/unit/simulation/` still green
- [x] `pytest tests/unit/ui/` still green
- [x] Combat Lab simulation suite passes: 162 / 162
- [x] Grep `_role_from_instance_id` returns only docstring breadcrumbs + Projects history files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5 (cache invalidation hooks)
