# Phase 1: Pin the target surface (red contract first)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-430 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** none
**Review Mode:** standard
**Files (planned):**
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (rewrite)
- `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` (new)

**Objective:** Drive TD-08 with the failing test. Rewrite the frozen public-API contract test to assert the **target** shape (10 attrs) instead of the current 68-method roster, and author a new behavior-parity test file for the grouped namespaces. Confirm all new assertions are red against current `main`. No production code changes in this phase.

---

## Tasks

### Task 1.1: Read foundation docs + source plan [Simple]
**Files:** `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, the TD-08 plan
**Tests:** none — discovery work

- [ ] Read `docs/README.md` (documentation index)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read the TD-08 source plan in full: [`TD-08_facade_api_reduction.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-08_facade_api_reduction.md)
- [ ] Read [`docs/systems/strategy_layer.md`](../../../docs/systems/strategy_layer.md) for the current facade boundary description (Phase 6 will rewrite this)
- [ ] Read the current contract test [`tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`](../../../tests/unit/strategy/facade/test_strategy_session_facade_public_api.py) end-to-end so the rewrite preserves coverage intent

**Notes:** [Filled during implementation]

### Task 1.2: Reconfirm the baseline [Simple]
**Files:** none (read-only verification)
**Tests:** none

- [ ] Reconfirm the public-method count matches the TD-08 plan:
  ```
  pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q
  ```
  Expected: green against current `main`, with `PUBLIC_METHODS` of 68 entries. If the count has drifted, reconcile with the TD-08 plan before continuing.
- [ ] Reconfirm the dispatch-helper count:
  ```
  rg "facade_helper_name\s*=\s*'dispatch_" game/strategy/engine | wc -l
  ```
  Expected: 36. Drift → stop and reconcile.
- [ ] Reconfirm the cache-forwarder block is still at the expected lines (`strategy_session_facade.py:114-164`) and the legacy alias is still at `strategy_session_facade.py:372-374`:
  ```
  rg -n "preserved for legacy tests" game/strategy/facade/strategy_session_facade.py
  rg -n "_resolve_economy_config" game/strategy/facade/strategy_session_facade.py
  ```
- [ ] Re-enumerate the current UI callers — do not trust the "25 files" count:
  ```
  rg -n "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui | sort -u
  ```
  Record the count and the file list in `findings/phase_1_ui_caller_inventory.md`. Phase 3 uses this as its starting point.

**Notes:** [Filled during implementation. If TD-02/TD-03 ship between this phase and Phase 5, re-run the baseline checks before each subsequent phase.]

### Task 1.3: Rewrite `test_strategy_session_facade_public_api.py` to assert the target shape [Medium]
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q` — MUST be red after rewrite

The rewritten contract test pins the *post-TD-08* shape:

- [ ] Replace `PUBLIC_METHODS` (68 entries) with:
  ```
  PUBLIC_TOP_LEVEL = {"handle_command", "process_turn"}
  PUBLIC_GROUP_ACCESSORS = {
      "facade_state",
      "commands", "fleets", "systems", "planets",
      "empires", "events", "session_meta", "economy", "validation",
  }
  ```
- [ ] Add `test_only_target_top_level_callables_exist` — asserts the set of public callables on `StrategySessionFacade` equals `PUBLIC_TOP_LEVEL`.
- [ ] Add `test_only_target_top_level_attrs_exist` — asserts the set of public *attributes* on `StrategySessionFacade` equals `PUBLIC_GROUP_ACCESSORS`.
- [ ] Add `test_no_legacy_flat_methods` — asserts none of the 36 `dispatch_*` names and none of the 32 flat read methods exist as top-level attributes anymore. Source the legacy name list from a frozen constant in the test (`LEGACY_FLAT_METHODS`) so the assertion is explicit.
- [ ] Add `test_grouped_namespaces_expose_expected_methods` — walk each group accessor and assert the per-group method list against a `GROUP_CONTRACT` dict declared in the test. Example entry: `"fleets": {"get", "at_hex", "path_preview", "path_projection", "remaining_pods"}`.
- [ ] Add `test_legacy_cache_attrs_removed` — assert `_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry` are **not** settable on a fresh instance (e.g. by `setattr` then re-read, expect AttributeError or the value not to round-trip).
- [ ] Drop the old `PROTECTED_ATTRS` constant entirely. The legacy-cache assertion replaces it.
- [ ] Run the test, confirm it is **red**:
  ```
  pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q
  ```
  Expected failures: legacy flat methods exist; group accessors missing; legacy cache attrs are settable. That's the documented TDD red.

**Notes:** [Filled during implementation. The frozen `LEGACY_FLAT_METHODS` constant in the test should match the current 68-entry roster — capture it from the pre-rewrite version so the assertion is exhaustive.]

### Task 1.4: Author `test_facade_grouped_namespaces.py` (behavior parity tests) [Medium]
**File:** `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` (new)
**Tests:** `pytest tests/unit/strategy/facade/test_facade_grouped_namespaces.py -q` — MUST be red after authoring

Each test exercises the new grouped surface and asserts the result matches what the old flat surface returned. Use existing fixtures from the facade test suite.

- [ ] `test_commands_strips_dispatch_prefix` — pick 3 representative dispatch helpers (e.g. `issue_move`, `issue_colonize`, `delete_fleet`) and assert `facade.commands.<verb>(...)` produces the same `CommandResult` as the legacy `facade.dispatch_<verb>(...)`.
- [ ] `test_fleets_namespace_parity` — for each of the 5 fleet read methods, assert the grouped form returns the same `FleetInfo` (or equivalent) as the flat form:
  - `facade.fleets.get(id)` == `facade.get_fleet(id)`
  - `facade.fleets.at_hex(...)` == `facade.get_fleets_at_hex(...)`
  - `facade.fleets.path_preview(...)` == `facade.get_fleet_path_preview(...)`
  - `facade.fleets.path_projection(...)` == `facade.get_fleet_path_projection(...)`
  - `facade.fleets.remaining_pods(...)` == `facade.get_fleet_remaining_pods(...)`
- [ ] `test_planets_namespace_parity` — same pattern for the 2 planet read methods.
- [ ] `test_systems_namespace_parity` — same pattern for the 6 system/star/storm methods.
- [ ] `test_empires_namespace_parity` — same pattern for the 6 empire methods.
- [ ] `test_events_namespace_parity` — same pattern for the 3 event methods.
- [ ] `test_session_meta_namespace_parity` — `facade.session_meta.turn_number`, `.save_path`, `.human_player_ids`.
- [ ] `test_economy_namespace_parity` — `facade.economy.race_registry`, `.colony_demographic_view(...)`, `.resolve_config(...)`.
- [ ] `test_validation_namespace_parity` — `facade.validation.can_colonize(...)`, `.can_move_to(...)`.
- [ ] Run, confirm **red** — the grouped accessors don't exist yet:
  ```
  pytest tests/unit/strategy/facade/test_facade_grouped_namespaces.py -q
  ```
  Expected: `AttributeError: 'StrategySessionFacade' object has no attribute 'commands'` (and similar for the other 8 accessors).

**Notes:** [Filled during implementation. The "parity" assertion is critical — if the namespace returns a *different* object than the flat form, the migration broke behavior and Phase 2 needs to investigate.]

### Task 1.5: Confirm reds, capture baseline output [Simple]
**Files:** none (verification)
**Tests:** the two files just authored

- [ ] Run the focused facade test set:
  ```
  pytest tests/unit/strategy/facade -q
  ```
- [ ] Confirm the new assertions are red and capture the failure summary in `findings/phase_1_red_baseline.md`. This is the TDD anchor — Phase 5 verification compares against it.
- [ ] Confirm no *other* tests regressed (the unrelated `tests/unit/strategy/facade/test_strategy_session_facade.py` should still pass; if any green tests turn red, the contract rewrite has a bug — investigate before continuing).

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Contract test (`test_strategy_session_facade_public_api.py`) is red for the documented reasons (legacy flat methods exist, group accessors missing, legacy cache attrs still settable)
- [ ] Grouped-namespace behavior test file is red for the documented reason (group accessors don't exist yet)
- [ ] `findings/phase_1_red_baseline.md` records the red failures so Phase 5 can verify they all flip to green
- [ ] `findings/phase_1_ui_caller_inventory.md` records the current UI caller list for Phase 3
- [ ] `python Projects/scripts/validate_phase.py PROJ-430 1` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
