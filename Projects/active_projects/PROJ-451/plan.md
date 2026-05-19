# PROJ-451: Production resource-consumption semantics (DI-006 + DI-007 engine half)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-451` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-451 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03a-continue-working (serial on `main`, no worktrees — per standing user preference)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. RED — write the rounded-to-zero stall reproduction tests | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. GREEN — emit RESOURCE_SHORTAGE when affordability passes but consumption charges 0 | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Decide: `_apply_resource_consumption` bool-return handling | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Stocked-fleet ratchet tests for `IProductionResourceSource` implementers | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-18
**Active Phase:** Phase 2 (ready)
**Last Action:** Phase 1 RED complete. Added 3 xfail-strict reproduction tests: (1) `TestFractionalCostRoundedToZeroEmitsResourceShortage::test_engine_level_zero_consume_emits_resource_shortage` and (2) `TestQueueLoopRoundedToZeroEmitsResourceShortage::test_fractional_per_step_cost_against_int_cargo_emits_resource_shortage` in `tests/integration/test_production_engine_fractional_fleet_cost.py`; (3) `test_apply_resource_consumption_emits_shortage_on_zero_consume` in `tests/unit/strategy/engine/test_production_engine_consumption.py`. All three confirmed RED via `--runxfail`, then xfail-strict markers added. Sharded 23373 tests | 23370 passed | 0 failed | 0 errors | 3 xfailed.

**Original action (2026-05-19):** Group A cross-group collision resolution applied. Codex r5 group1-preexecution-review caught that the data-half DI-006 fix is only PARTIALLY closed — `Fleet.consume_cargo_resource` at `fleet.py:285` still gates on raw `amount` while `has_cargo_resources` rounds. PROJ-451 scope expanded: Phase 2 now adds Task 2.0 (round the consume-side gate) + Task 2.5 (production_engine.py module docstring polish). Group A is ready for execution.
**Next Action:** Execute Phase 2 — Task 2.0 (data-side gate symmetry fix at `fleet.py:285`) + Task 2.1+ (engine-side RESOURCE_SHORTAGE emit on zero-consume) + Task 2.5 (module docstring polish). All three RED tests should turn GREEN.
**Blockers:** None hard. Functionally independent of PROJ-449/450 — sequenced second purely for orderly throughput.
**Context for Next Agent:** This is the closure of two discovered-issues that PROJ-436 Phase 12 left open in May 2026: DI-006 (rounded-to-zero Fleet build stall, no RESOURCE_SHORTAGE event when fractional cost rounds to 0 and affordability passes vacuously) and DI-007 (engine ignores `production_consume_resource` bool return; tick capacity burns without progress on contract breach). **Codex review 2026-05-19 (group1-preexecution-review/response.md) found the data-half is only PARTIALLY closed:** PROJ-444 Phase 2 rounded `Fleet.has_cargo_resources` at `fleet.py:265-268` but the sibling `Fleet.consume_cargo_resource` at `fleet.py:285` still gates on RAW `amount`. Net: `has_cargo_resources({"metals": 0.5})` returns True with cargo=0 (rounded gate, `0 < 0` is False) while `consume_cargo_resource("metals", 0.5)` returns False with cargo=0 (raw gate, `0 < 0.5` is True) — the two methods still disagree. PROJ-451 now closes BOTH the data-side gate symmetry AND the engine-side UX gap + contract enforcement.

## Overview
Finish the engine-side half of the fleet-production resource-consumption contract. Two open issues:

1. **DI-006 (UX gap)**: when a Fleet build has fractional per-step costs that round to 0 against the integer cargo store (`Fleet.has_cargo_resources` returns True for `amount=0.1` against `cargo=1`), the engine consumes 0, `_apply_resource_consumption` records 0 progress, `tick_capacity` decrements, the queue stalls without a `RESOURCE_SHORTAGE` event. Player sees a stuck fleet build with no shortage indicator.

2. **DI-007 (engine contract enforcement)**: `_apply_resource_consumption` (`production_engine.py:677-682`) does not capture or honor the bool return of `production_consume_resource`. If a future implementer returns False after affordability returned True (e.g. sub-tick race, partial-charge contract), the engine still decrements tick_capacity — capacity burns without forward progress.

Both surface as engine-side gaps in the affordability/consumption symmetry contract that PROJ-436 Phase 12 tightened. PROJ-444 Phase 2 closed the data-layer half. PROJ-451 closes the engine-side half + adds ratchet tests to all `IProductionResourceSource` implementers.

## Goals
- Reproduce the DI-006 rounded-to-zero stall in a focused test (RED, Phase 1).
- Emit `RESOURCE_SHORTAGE` event when `_apply_resource_consumption` records 0 progress despite affordability passing (GREEN, Phase 2).
- Decide between option (a) `_apply_resource_consumption` honors the bool return AND option (b) the Protocol contract is hard-asserted (DI-007 closure, Phase 3). Record decision in `decisions.md`.
- Add a ratchet test that every `IProductionResourceSource` implementer satisfies `production_has_resources(costs) is True → production_consume_resource(resource, amount) is True` (Phase 4).
- Sharded suite green at every phase boundary.

## Scope

**In Scope:**
- `game/strategy/data/fleet.py:285` — `Fleet.consume_cargo_resource` gate must round to match `has_cargo_resources` (codex r5 finding: data-half is asymmetric on current HEAD).
- `game/strategy/engine/production_engine.py:649-687` — `_apply_resource_consumption` engine-side bool-return handling and RESOURCE_SHORTAGE emit on actually-consumed==0.
- `game/strategy/engine/production_engine.py:60-95` — `IProductionResourceSource.production_consume_resource` Protocol docstring tightening (Phase 3 decision option b).
- `game/strategy/engine/production_engine.py:10-16` — module docstring still mentions "empire pool" (pre-PROJ-436); update to reference `IProductionResourceSource` per the engine's current routing.
- `tests/integration/test_production_engine_fractional_fleet_cost.py` — reproduction tests for DI-006 stall.
- `tests/unit/strategy/engine/test_production_engine_consumption.py` — engine-side bool return + RESOURCE_SHORTAGE emit unit tests.
- `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py` (new) — ratchet that `has_cargo_resources` and `consume_cargo_resource` agree on rounded-to-zero costs.
- `tests/unit/strategy/data/test_production_resource_source_ratchet.py` (new) — Phase 4 ratchet test for every implementer.
- `decisions.md` for the Phase 3 (a) vs (b) decision.

**Out of Scope:**
- Staging-yard substrate widening (PROJ-450).
- Strategy entity wrapper retirement (PROJ-449).
- Other Codex r4 jobs (catalog-driven resource surfaces, UI shim retirement, etc.).
- `_resource_agg.unload_cargo_from_fleet` widening (Option A from PROJ-444 Phase 2 decision). The Phase 2 decision picked Option B (round in `has_cargo_resources`); PROJ-451 finishes Option B by also rounding the consume-side gate. Widening the cargo store typing is a separate future project.
- Changes to `Planet.has_stockpile` or `Planet.consume_from_stockpile` — already symmetric (both compare float against float).

## Findings Summary
Source: `AgentCoordination/discovered_issues/log.jsonl` (DI-2026-05-18-006, DI-2026-05-18-007) + `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` (F-B-019 Protocol contract complement). Per-finding entries with current-state verification land in [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md).

| Finding | Severity | File:line | Status |
|---------|----------|-----------|--------|
| DI-2026-05-18-006 | medium | `fleet.py:285` (data-half gate asymmetry — codex r5 finding) + `production_engine.py:649-687` (UX gap engine half) | data half PARTIALLY-resolved (PROJ-444 Phase 2 rounded `has_cargo_resources` only; consume-side gate still raw); engine UX gap open |
| DI-2026-05-18-007 | low | `production_engine.py:677-682` | partially-resolved (Codex r4 verified the engine bool-return is still ignored) |
| F-B-019 | medium | `production_engine.py:60-95` (Protocol contract docstring) | open — Protocol contract tightened in archived PROJ-445 Phase 2; the engine-side defensive branch never landed |
| NEW-2 (codex r5) | low | `production_engine.py:10-16` (module docstring "empire pool" pre-PROJ-436 stale reference) | open — fold into Phase 2 |

## Key Files
| Component | File Path |
|-----------|-----------|
| Engine consumption (DI-006 UX gap site) | `game/strategy/engine/production_engine.py:649-687` (`_apply_resource_consumption`) |
| RESOURCE_SHORTAGE emit (existing) | `game/strategy/engine/production_engine.py:588-647` (`_log_resource_shortage`) |
| Engine tick loop (calls _apply_resource_consumption) | `game/strategy/engine/production_engine.py:330-440` (`_process_queue_tick_dynamic`) |
| Protocol contract docstring | `game/strategy/engine/production_engine.py:60-95` (`IProductionResourceSource.production_consume_resource`) |
| Data-layer half (already resolved) | `game/strategy/data/fleet.py:245-269` (`Fleet.has_cargo_resources` / `Fleet.consume_cargo_resource`) |
| Existing Fleet build test | `tests/integration/test_production_engine_fractional_fleet_cost.py` |
| Existing consumption test | `tests/unit/strategy/engine/test_production_engine_consumption.py` |

Full enumeration per phase in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1: RED — write the rounded-to-zero stall reproduction tests
Construct a focused integration test that:
- Sets up a Fleet with cargo `{"metals": 1}` (integer storage).
- Adds a build to the fleet queue with `cost_per_tick={"metals": 0.1}` (fractional per-step cost).
- Calls `ProductionEngine._process_queue_tick_dynamic` for tick 1.
- Asserts the queue STALLS (tick_capacity exhausted without progress).
- Asserts a `RESOURCE_SHORTAGE` event WAS emitted (RED — currently no event is emitted because affordability passes vacuously).

Plus a unit test for `_apply_resource_consumption` that:
- Mocks an `IProductionResourceSource` with `production_get_resource(res) → 1.0` (constant — no consumption happens).
- Calls `_apply_resource_consumption(empire, item, {"metals": 0.1}, mock)`.
- Asserts the diff captured by the engine equals 0.
- Asserts (currently failing — RED) that a follow-on call to a RESOURCE_SHORTAGE emit path happens.

Both tests are RED at the start of the phase.

### Phase 2: GREEN — emit RESOURCE_SHORTAGE when actually-consumed == 0 despite affordability
Modify `_apply_resource_consumption` to detect the "actually_consumed==0 despite `amount > 0`" case. When detected, route to `_log_resource_shortage` (the existing emit path at `:588-647`). The shortage log carries cause "amount rounded to zero against integer cargo store" so the player sees a clear shortage signal rather than a silent stall.

Verify the Phase 1 tests turn GREEN. The integration test now sees the RESOURCE_SHORTAGE event; the unit test sees the emit-path being invoked.

### Phase 3: Decide between (a) bool-return handling vs (b) Protocol contract hard-assert
DI-007 documented two closure paths:
- **(a) Defensive**: capture the `production_consume_resource` return value in `_apply_resource_consumption`; if False, signal back to `_process_queue_tick_dynamic` to skip the `tick_capacity` decrement (preserve capacity for retry).
- **(b) Strict**: tighten the Protocol contract docstring + add a hard assertion at the engine call site: `assert colony_or_fleet.production_consume_resource(res, amount), "Contract breach: consume returned False after affordability passed"`. Failure is a programmer error, not a runtime degradation mode.

Codex r4 recommends option (b) as cheaper. CLAUDE.md "Capability validation is hard, not soft" supports this. Record decision in `decisions.md`. Either option closes DI-007.

If option (a): implement the bool capture + tick_capacity skip path. Add unit tests proving the skip occurs.

If option (b): add the hard assertion + a unit test that constructs a misbehaving mock implementer and asserts the engine raises a clear error rather than silently burning capacity. Update the Protocol contract docstring at `production_engine.py:60-95` to make the affordability→consumption symmetry MUST-language stronger (it already is — verify the docstring text precisely declares the invariant and the engine NOW enforces it via the assertion).

### Phase 4: Stocked-fleet ratchet tests
Add a new ratchet test file at `tests/unit/strategy/data/test_production_resource_source_ratchet.py`. For every concrete `IProductionResourceSource` implementer (`Planet`, `Fleet`), the test asserts:

```python
def test_production_consume_resource_succeeds_when_affordability_passes(implementer, sample_costs):
    if implementer.production_has_resources(sample_costs):
        for resource_type, amount in sample_costs.items():
            assert implementer.production_consume_resource(resource_type, amount) is True
```

Parametrize across a fixture set spanning:
- Integer / float requested amounts (small fractional, exact integer, large)
- Integer / float storage types (Fleet integer cargo, Planet float stockpile)
- Edge case: requested amount that rounds to zero against integer storage

The ratchet test enforces the affordability/consumption symmetry contract at the implementer level. Future implementers (e.g. a Complex that satisfies the Protocol) must pass this test.

## Related Documents
- [design.md](design.md) — design rationale (DI-006 vs DI-007 separation; option a/b trade-off).
- [decisions.md](decisions.md) — decisions log.
- [findings/PROJ-451_findings.md](findings/PROJ-451_findings.md) — consolidated findings with current-state verification.
- [manifest.md](manifest.md) — file manifest grouped by phase + production/test/doc type.
- Codex r4 redesign: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (job 3 row).
- `AgentCoordination/discovered_issues/log.jsonl` — DI-2026-05-18-006 (data half resolved; engine UX gap open) + DI-2026-05-18-007 (engine bool-return).
- PROJ-444 Phase 2 closure of DI-006 data half: `Projects/archived_projects/PROJ-444/` (the rounding alignment in `fleet.py:245-269`).
- F-B-019 in `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`.

## Dependencies & Sibling Projects

| This project depends on | What | Why |
|-------------------------|------|-----|
| (none) | none | The engine-side residue is entirely contained in `production_engine.py` + tests |

| Sibling projects | Their dependency on PROJ-451 | When unblocked |
|------------------|------------------------------|----------------|
| PROJ-449 | independent | parallel-safe |
| PROJ-450 | independent | parallel-safe |
| PROJ-459 (Strategy data LOC extractions) | depends on **PROJ-451 completion** (Phase 1+) | After this project closes; sibling pre-requisite for `fleet_serde` extraction |

### Group A serial order (2026-05-19 collision resolution)

Group A executes its 4 projects in this serial order: **PROJ-449 → PROJ-451 → PROJ-459 → PROJ-450**.

This project (PROJ-451) is second. It runs after PROJ-449 closes and before PROJ-459 starts. PROJ-451 is functionally independent of PROJ-449 and PROJ-450 — the serial position is for orderly throughput, not a hard gate.

## Verification
- [ ] Phase 1 RED tests reproduce the rounded-to-zero stall + the bool-return-ignored seam
- [ ] Phase 2 GREEN: RESOURCE_SHORTAGE emitted when affordability passes but consumption charges 0
- [ ] Phase 3 decision recorded (option (a) defensive or option (b) strict assertion)
- [ ] Phase 4 ratchet test exists and passes for every concrete `IProductionResourceSource` implementer
- [ ] DI-2026-05-18-006 engine UX gap closed
- [ ] DI-2026-05-18-007 fully closed (either option a or b)
- [ ] F-B-019 closed (Protocol contract MUST-language landed)
- [ ] Sharded suite green
- [ ] Audit passed (end-of-project Codex consult)
- [ ] User verified
