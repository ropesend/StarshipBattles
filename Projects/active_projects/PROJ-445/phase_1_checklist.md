# PROJ-445 Phase 1: LayMines TypeError fix + ratchet parity-gap closure (HIGH-SEVERITY)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-445 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Resolve the only HIGH-SEVERITY finding in the entire 112-issue residue review. Any planet-issued `OrderType.LAY_MINES` order will currently raise `TypeError` because `LayMinesOrderHandler.execute_for_issuer` is missing the `registries` kwarg that `ActionExecutionEngine._execute_planet_action` unconditionally passes post-PROJ-438 Phase 6. Phase 1 = 3-line production fix + new integration test + 2-handler extension to the existing contract ratchet (the prophylactic test that would have caught this prophylactically).

**Cross-bucket file-ownership rule:** Only edit `game/strategy/engine/`, `game/strategy/services/`, and engine/services-subject tests. Do NOT touch other directories. Three sibling agents run PROJ-444/446/447 in parallel.

**Source-of-truth findings:** [`findings/bucket_b_engine_services_scan.md`](findings/bucket_b_engine_services_scan.md) — F-B-001 (high), F-B-020, F-B-022 in full. Codex consult that confirmed F-B-001 + traced the planet-FMS dispatch path: `AgentCoordination/Scratchpad/Consult/20260518T174511Z_post-refactor-residue-review-verification/response.md`.

---

## Tasks

### Task 1.1: Write the failing integration test FIRST (TDD red) [Small]
**File (new):** `tests/integration/test_fms_planet_lay_mines.py`
**Tests:** `pytest tests/integration/test_fms_planet_lay_mines.py -v`

- [ ] Read existing planet-FMS integration tests for the fixture pattern: `tests/integration/test_fms_planet_launch.py`, `tests/integration/test_fms_planet_recovery.py`
- [ ] Read DI-2026-05-18-001 in `AgentCoordination/discovered_issues/log.jsonl` for the deferred Phase-10 scaffolding context
- [ ] Construct a fixture: 1 empire with `_registries` attribute set, 1 owned planet with operational facility carrying a fighter/satellite/mine-laying bay, queued `LAY_MINES` order via typed command path, and any deployed groups needed
- [ ] Write `test_planet_issued_lay_mines_dispatches_through_engine` that drives one tick through `_process_planet_action_tick → _execute_planet_action → handler.execute_for_issuer(..., registries=...)` for `OrderType.LAY_MINES`. Assert: order queue advanced, handler invoked, no exception.
- [ ] Run the test — it MUST fail with `TypeError: execute_for_issuer() got an unexpected keyword argument 'registries'`. If it fails for any other reason, debug the fixture before proceeding.
- [ ] **Parametrize the test across all 5 entries in `command_registry.planet_fms_action_order_types()`** (LAY_MINES, LAUNCH_FIGHTERS, RECOVER_FIGHTERS, LAUNCH_SATELLITES, RECOVER_SATELLITES). Currently LAY_MINES fails; the other 4 pass. This is the F-B-022 scaffold.

### Task 1.2: F-B-001 — Add registries kwarg to LayMinesOrderHandler (TDD green) [Simple]
**File:** `game/strategy/engine/order_handlers/lay_mines.py:184`
**Tests:** Re-run the test from Task 1.1.

- [ ] Read `RecoverFightersOrderHandler.execute_for_issuer` at `game/strategy/engine/order_handlers/recover_fighters.py:107-120` — this is the canonical 5-kwarg shape. Note the accept-and-ignore pattern.
- [ ] Read the `IOrderHandler` Protocol declaration at `game/strategy/engine/order_handlers/base.py:83-113`
- [ ] Read the current `LayMinesOrderHandler.execute_for_issuer` signature at `lay_mines.py:184-191`
- [ ] **GREEN**: Add `registries: Any = None` as a keyword-only parameter to `execute_for_issuer`. Mirror the `recover_fighters.py` shape exactly. Add `Any` import if not present.
- [ ] Re-run the Task 1.1 test for LAY_MINES — it MUST now pass. All 5 parametrized cases pass.
- [ ] Run targeted unit tests: `pytest tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py -v` (note: handler file uses the `_handler` suffix). Must remain green.

### Task 1.3: F-B-022 + prophylactic parity gap — Extend the existing contract ratchet [Simple]
**File:** `tests/unit/strategy/engine/test_issuer_execution_contract.py:36-65`
**Tests:** `pytest tests/unit/strategy/engine/test_issuer_execution_contract.py -v`

- [ ] Read the existing ratchet. Confirm Codex's finding: it asserts the 5-kwarg `execute_for_issuer` signature ONLY for `RecoverFightersOrderHandler`, `RecoverSatellitesOrderHandler`, `LaunchFightersOrderHandler` — `LayMinesOrderHandler` and `LaunchSatellitesOrderHandler` are omitted.
- [ ] **GREEN**: Add the two missing handlers to the assertion loop. Use `inspect.signature(handler.execute_for_issuer)` to assert all 5 parameter names (`issuer`, `order_owner`, `empire`, `galaxy`, `registries`) are present with their kwarg-only / default-None shape.
- [ ] Re-run the ratchet — all 5 handlers covered, all 5 assertions pass.
- [ ] This is the test that would have caught F-B-001 prophylactically. Without it, the next handler added in the same shape will drift again.

### Task 1.4: F-B-020 — Subcategory-tag spelling ratchet [Simple]
**File:** `tests/unit/strategy/engine/commands/test_command_registry.py` (or create `test_planet_fms_subcategory.py` if no fitting test file exists)
**Tests:** `pytest tests/unit/strategy/engine/commands/ -v`

- [ ] Read `CommandRegistry.planet_fms_action_order_types` at `game/strategy/engine/commands/registry.py:312-325` — the `if "planet_fms" in s.subcategories` predicate
- [ ] Find the 5 CommandSpecs that should contribute: search `game/strategy/engine/handlers/` for `subcategories=frozenset({"planet_fms"})` declarations. Confirm 5 hits (handlers/lay_mines.py:40, plus 4 others).
- [ ] **GREEN**: Add `test_planet_fms_subcategory_tag_spelling_or_set_size` that asserts:
  - `len(command_registry.planet_fms_action_order_types()) == 5`
  - `set(command_registry.planet_fms_action_order_types()) == {OrderType.LAY_MINES, OrderType.LAUNCH_FIGHTERS, OrderType.RECOVER_FIGHTERS, OrderType.LAUNCH_SATELLITES, OrderType.RECOVER_SATELLITES}`
- [ ] Verify the test catches typo regressions: temporarily change a `"planet_fms"` to `"planet-fms"` in one handler, confirm the test fails. Revert.
- [ ] Optional: extract `"planet_fms"` to a `SUBCATEGORY_PLANET_FMS = "planet_fms"` module-level constant in `commands/__init__.py` and update the 5 handlers + the registry method. Defer if it expands scope.

---

## Phase Completion Checklist

- [ ] F-B-001 production fix applied (3-line change in `lay_mines.py:184`)
- [ ] New integration test `test_fms_planet_lay_mines.py` exists, parametrized across all 5 planet-FMS handlers, all 5 cases pass
- [ ] Contract ratchet `test_issuer_execution_contract.py:36-65` extended to cover LayMines + LaunchSatellites; all 5 ratchet cases pass
- [ ] Subcategory-tag ratchet locks the planet-FMS surface at 5 entries; catches typo regressions
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-445 1` — PASSED
- [ ] Update `discovered_issues/log.jsonl`: mark DI-2026-05-18-001 as `partial` (LAY_MINES slice closed; broader planet-FMS coverage scaffolding remains as Phase 2 work)
- [ ] Update status to `Complete`; plan.md phase table + Current State → Phase 2
- [ ] No regressions in any other test under `pytest tests/integration/test_fms_planet_*.py`

## Risks / Notes

- This phase is the urgent fix for a production bug. Do not bundle other findings into it; keep Phase 1 narrowly scoped so it can ship as its own PR fast.
- Codex consult 2026-05-18 confirmed: `RecoverFightersOrderHandler` (signature mirror), `IOrderHandler` Protocol contract, `ActionExecutionEngine._execute_planet_action` dispatch site, `LayMinesCommandHandler` CommandSpec planet_fms tag, AND the contract ratchet parity gap. Every claim in this phase is independently verified.
- If you discover further engine-side residue while working in `order_handlers/`, log it via /claude-di-log or note in decisions.md — do NOT fix in place during Phase 1.
