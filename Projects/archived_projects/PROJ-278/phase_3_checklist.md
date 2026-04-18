# Phase 3: Combat Lab scenario_role registry (data + machinery)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-278 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Ship the read-only `combat_lab_role_registry` (a `RoleRegistry` instance with `allow_runtime_add=False`) loaded from a new `combat_lab/data/scenario_roles.json` file. Add a validation test that every role label referenced in `combat_lab/scenarios/` exists in the registry — catches typos at test time. Phase 3 does NOT change `ShipSpec` or remove substring parsing — that's Phase 4's job. Phase 3 establishes the source-of-truth data file + registry instance that Phase 4 will consume.

**User decisions (locked) for Combat Lab roles:**
- `combat_lab/data/scenario_roles.json` is the moddable source of truth (matches Combat Lab's existing pattern of owning its own data files)
- Registry is **read-only at runtime** (`allow_runtime_add=False`) — players don't write Combat Lab scenarios
- Scenario role labels and gameplay design_role share the `RoleRegistry` *machinery* but NOT instances (two registries, two files)

---

## Audit (already done — recorded here for reference)

Role labels currently used by scenarios:

| Role | Templates / Scenarios using it |
|------|-------------------------------|
| `attacker` | StaticTargetScenario, BeamScenarios, ToHitAttackFleetScenario, ResourceScenario (some) |
| `target` | StaticTargetScenario, BeamScenarios, ToHitAttackFleetScenario, ResourceScenario optional |
| `ship1` | DuelScenario |
| `ship2` | DuelScenario |
| `ship` | PropulsionScenario, ResourceScenario (single-ship variant) |
| `low` | PropulsionScenario mass-comparison subclasses (`combat_lab/scenarios/propulsion_scenarios.py:470`) |
| `med` | PropulsionScenario mass-comparison subclasses (`combat_lab/scenarios/propulsion_scenarios.py:471`) |
| `high` | PropulsionScenario mass-comparison subclasses (`combat_lab/scenarios/propulsion_scenarios.py:472,907`) |
| `provider_a` | ToHitAttackFleetScenario provider tests (`combat_lab/scenarios/tohit_attack_fleet_scenarios.py:277,328`) |
| `provider_b` | ToHitAttackFleetScenario provider tests (`combat_lab/scenarios/tohit_attack_fleet_scenarios.py:278,329`) |

Substring parsing call sites that Phase 4 will remove:
- `combat_lab/runner.py:27-38` — `_role_from_instance_id(instance_id)` splits on `":"`
- `combat_lab/services/scenario_run_helper.py:23,76` — imports + uses the parser

---

## Tasks

### Task 3.1: Create `combat_lab/data/scenario_roles.json` [Simple]
**File:** `combat_lab/data/scenario_roles.json` (NEW)
**Tests:** Validated by Task 3.4

- [x] Create the file with the 10 roles from the audit
- [x] Each role: `id`, `display_name`, `description`. Empty `vehicle_type_filter` (Combat Lab roles have no vehicle restriction)
- [x] Verify JSON parses

**Notes:** All 10 roles loaded, IDs unique. JSON includes a `_comment` explaining the registry's read-only nature and pointing at the consistency test.

### Task 3.2: Write tests for `combat_lab_role_registry` [Medium]
**File:** `tests/unit/combat_lab/test_scenario_role_registry.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/test_scenario_role_registry.py`

- [x] Decided test location: `tests/unit/combat_lab/` (matches existing convention)
- [x] Tests cover: returns `RoleRegistry`, singleton behavior, `allow_runtime_add=False` raises on add, `set_default_*` / `reset_default_*` work, all 10 expected roles present, every role has display_name + description, all Combat Lab roles have empty `vehicle_type_filter`
- [x] Tests fail with `ModuleNotFoundError` (TDD red phase verified)

**Notes:** Used pytest autouse fixture `_reset_registry` so each test starts with a clean module-level state — same pattern as `test_design_role_registry_loader.py` from Phase 2.

### Task 3.3: Implement `combat_lab/scenario_role_registry.py` [Medium]
**File:** `combat_lab/scenario_role_registry.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/test_scenario_role_registry.py` — 8/8 pass

- [x] Module-level accessor pattern (matches `design_role_registry.py`)
- [x] `_build_default()` constructs `RoleRegistry(allow_runtime_add=False)` and loads from `combat_lab/data/scenario_roles.json`
- [x] No mod overlay, no user overlay (Combat Lab roles are static)
- [x] Module docstring explains the relationship to `design_role_registry` (same machinery, different instance, different scope)
- [x] Run tests — confirm pass

**Notes:** Used `Path(__file__).parent / "data" / "scenario_roles.json"` for the data file constant — keeps the dependency self-contained within `combat_lab/`. No `Paths` constant needed since this file is Combat-Lab-private.

### Task 3.4: Add validation test — every role used by scenarios is registered [Medium]
**File:** `tests/unit/combat_lab/test_scenario_roles_consistency.py` (NEW)
**Tests:** `pytest tests/unit/combat_lab/test_scenario_roles_consistency.py`

- [x] Helper `_extract_referenced_role_names(scenarios_dir) -> Set[str]` walks every `.py` under `combat_lab/scenarios/`
- [x] AST scanner finds:
  - `Subscript` nodes with receiver `ships_by_role` or `initial_state` and literal-string slice
  - `Call` nodes with `ships_by_role.get/.pop(...)` and literal-string first arg
- [x] Skips dynamic keys (Names, Attributes, f-strings) — documented limitation
- [x] Test: every literal role name referenced is registered in `combat_lab_role_registry`
- [x] Test: scanner finds at minimum the baseline 5 roles (`attacker`, `target`, `ship1`, `ship2`, `ship`) — guards against scanner regression
- [x] Run test — confirm pass with current scenarios (10 literal roles found, all registered)
- [x] Verified test would FAIL if a role were missing from data file (manual simulation)

**Notes:** Scanner found exactly the 10 audited roles with no false positives or misses. One known dynamic-key site at `templates.py:1115` (uses `role_attacker` / `role_target` variables) is documented in the test module docstring as an unavoidable scanner limitation — those rely on author discipline.

### Task 3.5: Update documentation [Simple]
**File:** `docs/guides/simulation_testing.md`
**Tests:** N/A

- [x] `docs/guides/simulation_testing.md` — added new §"2.5 Scenario Role Labels (PROJ-278)" with authoring rule, AST scanner limitation, and cross-link to `docs/systems/strategy_layer.md` for the gameplay variant
- [x] Updated `combat_lab/` directory tree to include `scenario_roles.json` and `scenario_role_registry.py`
- [x] `docs/01_ARCHITECTURE.md` — no Combat Lab section to update (Combat Lab is documented via `combat_lab/README.md` + simulation_testing.md, not 01_ARCHITECTURE.md)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/core/` still green
- [x] `pytest tests/unit/strategy/data/test_design_role_registry*.py` still green
- [x] New consistency test `pytest tests/unit/combat_lab/test_scenario_roles_consistency.py` passes
- [x] Combat Lab full suite passes: `python -m combat_lab.run_tests --fast` returns 162 passed / 0 failed / 0 skipped
- [x] Targeted regression: `pytest tests/unit/core/ tests/unit/strategy/data/test_design_role_registry*.py tests/unit/combat_lab/` returns 1325 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (ShipSpec field separation + delete substring parsing)
