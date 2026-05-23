# Phase 8: `ProductionEngine.context_type` deletion

**Status:** Complete (branch `proj/PROJ-436/phase_8`, awaiting merge to `main`)
**Depends on:** phase_7
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_8.planned_files

**Objective:** Delete the 3 `context_type` storage-dispatch sites in
`ProductionEngine._check_affordability` / `_log_resource_shortage` /
`_apply_resource_consumption` (previously at production_engine.py:524,
561, 629). ProductionEngine reads inputs / writes outputs through a
unified `IProductionResourceSource` Protocol satisfied by both Planet
(over its stockpile API) and Fleet (over its cargo API).

---

## What landed

Audit-driven single cutover (Phase 4f / 5f / 6b / 7 pattern):

- **Substrate**: defined `IProductionResourceSource` runtime_checkable
  Protocol in `production_engine.py` with three methods —
  `production_has_resources(costs)`, `production_get_resource(rid)`,
  `production_consume_resource(rid, amount)`.
- **Polymorphic delegators on Planet and Fleet**: 3 each, thin one-line
  forwards to the existing entity-specific stockpile / cargo APIs. The
  entity-specific names (`has_stockpile`, `has_cargo_resources`, etc.)
  remain as the public surface for non-engine callers
  (`transfer_branches.py`, `IStockpileHolder` protocol). See
  `decisions.md` Phase 8 design row for the three alternatives weighed.
- **Engine cutover**: the 3 dispatch sites collapse to single-line
  protocol method calls. All `getattr(colony_or_fleet, 'context_type',
  None)` reads deleted. The Phase 5 explicit `ValueError`-on-unknown-
  owner contract dissolves into the natural `AttributeError` Python
  raises when a method is called on an object that doesn't declare it.
- **AST guard**: `tests/static_guards/test_no_legacy_storage_fields.py`
  extended with 3 new tests: one pinning absence of the
  `getattr(colony_or_fleet, 'context_type'` text in production_engine.py
  source; two pinning the unified-protocol methods exist on Planet /
  Fleet.
- **Focused integration test**: new file
  `tests/integration/test_production_engine_container_unified.py`
  (17 tests across 5 classes) pins the protocol-conformance contract
  end-to-end including the engine's read/consume routing through real
  Planet and real Fleet.
- **Test-mock migration**: 6 engine-side test files updated to use the
  unified protocol-method names. The Phase 5 `ValueError`-on-unknown-
  owner unit tests rewritten to assert `AttributeError`.

## What was NOT done (intentional, per project plan)

- `transfer_branches.py` was not migrated off Planet's stockpile API
  (out of Phase 8 scope; transfer flow has its own contract).
- `IStockpileHolder` protocol was NOT touched (Phase 6 audit explicitly
  chose "leave as-is"; non-engine callers consume the protocol).
- `Planet.stockpile` and `Fleet` aggregate cargo were NOT flipped to
  actual `Container` instances (the original Phase 8 plan called for
  this, but Phase 4 decisions row deferred it; the manager-routed
  internal storage can swap from `Dict` to `Container` in a future
  session without touching any caller).
- UI `context_type` reads in `build_queue_controller.py` /
  `build_queue_source.py` / et al were NOT touched (Phase 6a audit
  confirmed those are entity-routing for the UI DTO, not storage-typed
  dispatch).

## Phase Completion Checklist

- [x] All sub-phases complete (single-cutover commit, not sub-phased)
- [x] Grep gate: zero executable `context_type` reads in
      `game/strategy/engine/production_engine.py` (only 3 docstring
      comment references remain at lines 49, 544, 630)
- [x] `tests/integration/test_production_engine_container_unified.py`
      green (17/17)
- [x] Existing production engine integration tests green
- [x] Full sharded suite green (23205/23207, +20 from Phase 7 baseline)
- [x] OpenCode `pre-final-check` `--allow-tests` consult complete
      (Codex CLI not installed on this machine; substituted with
      OpenCode per fallback). All 7 verification checks PASS, 1
      finding remediated, 2 dispositioned without code change.
- [x] Update status to Complete; update plan.md + phase_state.json +
      decisions.md.
