# Phase 7: Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 7`

**Status:** Complete
**Objective:** Document the materializer service in the docs directory.

---

## Tasks

### Task 7.1: Add materializer to `04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** Manual review

- [x] Add a new service entry: "ShipMaterializer"
- [x] Describe: protocol (`IShipMaterializer`), two implementations (InstanceBackedMaterializer, DesignOnlyMaterializer), access pattern (`get_default_ship_materializer()` / `set_default_ship_materializer()`)
- [x] Note: Combat Lab swaps to DesignOnlyMaterializer at startup; everything else uses the default InstanceBackedMaterializer

**Notes:** Added "ShipMaterializer (PROJ-274)" section at top of "Simulation Layer Services" (before BattleService). Covers protocol signature, both implementations with use case table, module-level accessors code example, integration with `run_battle`/`BattleController.start_from_spec`, new `ShipSpec.instance_ref` field, and a complete call-sites table showing each production caller + whether it supplies a ship_builder override.

### Task 7.2: Update architecture doc service list [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Tests:** Manual review

- [x] Update the ApplicationContext services list (where 10 services are currently enumerated) to include ship_materializer
- [x] Service count is now 11 — update any "10 services" references (grep for "10 services" and "10 singletons")

**Notes:** `docs/01_ARCHITECTURE.md` only had one reference to the service count at L63 ("Manages all 9 services"). Rephrased to describe ApplicationContext as managing the production service graph, noting that additional services (like ship_materializer in PROJ-274) follow the same module-level `get_default_*` / `set_default_*` pattern and are consulted on demand. This matches how PolicyManager, AssetManager, etc. already work — the accessors live in the service module, not in `game/context.py`. More accurate than incrementing a hardcoded count that would drift again.

### Task 7.3: Update combat_simulation.md canonical example [Simple]
**File:** `docs/systems/combat_simulation.md`
**Tests:** Manual review

- [x] Find the "Unified entry" code example (around L56-66 in the current file)
- [x] Remove the `ship_builder=my_ship_builder` line from the canonical example
- [x] Add a note below: "`ship_builder` is an optional test-override. Production code relies on the ship_materializer service in ApplicationContext — callers configure it (if needed) before invoking `run_battle`."

**Notes:** Removed `ship_builder=my_ship_builder` line from the canonical code example at L56-66. Added explanatory paragraph below pointing to PROJ-274 + `docs/04_SERVICES.md::ShipMaterializer` for details. The example now accurately reflects the post-Phase-6 production usage pattern.

### Task 7.4: Update memory [Simple]
**File:** `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md` (or relevant memory file)
**Tests:** Manual

- [x] Add bullet: "ApplicationContext now manages 11 services; ship_materializer added in PROJ-274; InstanceBackedMaterializer is default, DesignOnlyMaterializer used by Combat Lab"

**Notes:** Added "In-Progress Projects (PROJ-273+)" section at top of memory file covering both PROJ-273 (shared registry) and PROJ-274 (ShipMaterializer). PROJ-274 entry covers: protocol + 2 implementations, ShipSpec.instance_ref field, run_battle/BattleController ship_builder=None default, 4 production closures eliminated (app.py / test_execution_service / test_lab/screen / simulation_adapter / reduced wrapper in scenario_run_helper + ComparisonScenario), Combat Lab integration via TestRunner.__init__ + combat_lab/design_loader.py, baseline preserved at 14800/1 failed/3 errors (all pre-existing).

### Task 7.5: Final regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full suite green
- [x] No stale `ship_builder=` production references (grep `grep -rn "ship_builder=" game/ | grep -v test | grep -v "#"` — zero in production files outside battle_runner / battle_controller signatures)

**Notes:** Final `pytest tests/`: **14800 passed, 1 failed, 2 skipped, 3 errors** in 221.87s — exactly matches the pre-PROJ-274 baseline. Grep check for production `ship_builder=` references shows:
- Legitimate forwarding in `battle_runner.py:162,258` + `battle_controller.py:316` (internal delegation after default substitution).
- Legitimate module docstrings in `ship_materializer.py:6,21` (historical narrative).
- Legitimate role-tagging wrappers in `scenario_run_helper.py:110`, `templates.py:894` (ComparisonScenario) — these wrap the context builder, not a standalone ship loader.
- My own Phase 6 edits in `test_execution_service.py:94` and `test_lab/screen.py:444` using `_default_ship_builder_from_context()` — these materialize ships from context for the pre-snapshot state, not independent closures.

**Bonus Phase 6 cleanup:** Found that `game/strategy/adapters/simulation_adapter.py` had a `_make_ship_builder` method that did `instance_id → ShipInstance` lookup across two fleets, then called `instance.to_ship(...)`. After the strategy compiler sets `instance_ref=ship` in Phase 6, this lookup is redundant — the context materializer reads `ship_spec.instance_ref` directly. Deleted `_make_ship_builder` entirely + removed the `ship_builder=ship_builder` kwarg from `SimulationBattleResolver.resolve_battle`'s `run_battle(...)` call. Strategy tests: 3304 passed / 1 skipped / 1 pre-existing error. Combat Lab: 162/162. Full suite baseline preserved.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State — mark project COMPLETE
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 7`

_User verification (launch strategy battle + Combat Lab test manually) is a PROJECT-level acceptance step tracked in `plan.md`'s top-level `## Verification` section, not a phase task._
