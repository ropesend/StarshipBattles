# PROJ-451: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture analysis

PROJ-436 Phase 8 introduced the `IProductionResourceSource` Protocol (`production_engine.py:34-95`) as a unified seam that both Planet (stockpile API) and Fleet (cargo API) implement. The Protocol replaced the legacy `ProductionEngine.context_type` dispatch. Phase 12 added the affordability/consumption symmetry contract: an implementation MUST return True from `production_consume_resource` whenever `production_has_resources` returned True for the same `(resource_type, amount)` in the same engine tick.

Two engine-side gaps remain:

1. **DI-006 (UX gap)** — When Fleet builds use fractional per-step costs that round to 0 against the integer cargo store, the data-layer rounding (post-PROJ-444 Phase 2) makes affordability symmetric — `has_cargo_resources(0.1)` returns True (rounds to 0 ≤ stored). But `_apply_resource_consumption` does the `before/after` diff, captures `actually_consumed == 0`, decrements `tick_capacity`, and the queue stalls without a RESOURCE_SHORTAGE event. The player has no signal.

2. **DI-007 (engine contract enforcement)** — `_apply_resource_consumption` at `production_engine.py:677-682` does not capture the bool return of `production_consume_resource`. If a future implementer breaks the symmetry contract (returns False after affordability passed), the engine silently burns tick_capacity. Contract violations don't surface as bugs; they manifest as mysterious stalls.

F-B-019 is the implementer-side ratchet of the same contract. The Protocol contract docstring was tightened by PROJ-444 Phase 2 (MUST-language landed at `production_engine.py:60-95`), but no test asserts that EVERY implementer satisfies the symmetry — only the engine's defensive plumbing.

## Sequencing rationale

The 4-phase breakdown is shaped by TDD discipline + a deliberate Phase 3 decision gate:

- **Phase 1 — RED.** Two failing tests: the integration-level rounded-to-zero stall reproduction + the unit-level zero-consume detection. Both use `xfail` so the sharded suite stays green.
- **Phase 2 — GREEN.** Engine emits RESOURCE_SHORTAGE on `actually_consumed == 0`. Phase 1 RED tests turn GREEN (un-xfail). DI-006 engine UX gap closed.
- **Phase 3 — decision gate.** Choose between (a) defensive bool-capture + tick_capacity skip OR (b) strict hard-assert. Default to (b) per Codex r4 + CLAUDE.md "Capability validation is hard, not soft." Either option closes DI-007.
- **Phase 4 — ratchet.** Parametrized test for every concrete `IProductionResourceSource` implementer. Defense-in-depth complement to Phase 3's engine-side enforcement. Closes F-B-019.

## Key patterns reused

- **PROJ-436 Phase 12 "Option C diff truth-up"** — the before/after diff at `_apply_resource_consumption:679-683` is the existing engine-side reconciliation pattern. Phase 2 extends it with the "actually_consumed==0 emit" logic.
- **FEAT-09 RESOURCE_SHORTAGE event** — `production_engine.py:588-647` (`_log_resource_shortage`) is the existing emit path. Phase 2 routes the new detection through this existing path rather than introducing a sibling.
- **PROJ-438 Phase 6 unified Protocol contract** — Phase 3 option (b) mirrors the "Capability validation is hard, not soft" pattern that PROJ-438 used (`docs/03_CONVENTIONS.md` Conventions §"Capability validation is hard, not soft").
- **`tests/static_guards/` ratchet pattern** — Phase 4 mirrors how `test_specs_sharing_order_type_declare_same_codec` enforces invariants at the implementer level.

## Dependencies & Risks

1. **No project dependency.** Parallel-safe with PROJ-449 and PROJ-450 — no shared file surface.
2. **Phase 3 decision risk.** Option (a) creates new code path in `_process_queue_tick_dynamic`; option (b) is one assertion. Default to (b) unless a concrete future implementer requires defensive plumbing.
3. **`Fleet.consume_cargo_resource` zero-amount semantics.** When amount rounds to 0 (e.g. 0.1 → 0), the consume call may still return True trivially (consuming 0 succeeds). Verify Phase 4 ratchet handles this correctly. Pre-PROJ-451 hand-check: `Fleet.consume_cargo_resource(rt, 0.1)` → `self._resource_agg.unload_cargo_from_fleet(rt, int(round(0.1)))` → `unload_cargo_from_fleet(rt, 0)`. The cargo aggregator should return True for "unload 0 succeeded".
4. **`_log_resource_shortage` cause-detection risk.** The existing limiting-resource logic at lines 605-624 finds the "largest shortfall ratio." For the rounded-to-zero case where `available == requested` (because both rounded to 0), the existing logic may not flag the resource as limiting. Phase 2 Task 2.3 verifies this and either augments the logic or uses an explicit cause-emit path.
5. **`_shortage_logged` flag duplication.** The existing path at `_process_queue_tick_dynamic:424-428` sets this flag after affordability-fail. The new Phase 2 emit path also needs to respect / set this flag to avoid duplicate emits in one turn.

## Opportunities discovered

- **Phase 4 ratchet catches future implementer bugs.** Any new `IProductionResourceSource` (e.g. a Complex that satisfies the Protocol) gets vetted by the parametrized ratchet at test time. Adding the implementer to the parametrize list is one line; the contract is enforced.
- **Phase 2 RESOURCE_SHORTAGE cause field** — the event currently carries `limiting_resource` + `available` + `needed`. Adding `cause="rounded_to_zero"` (Phase 2 Task 2.3) lets UI distinguish between "true shortage" and "fractional cost stall" if it ever cares to.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
