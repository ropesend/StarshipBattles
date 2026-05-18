# Phase 5: `Empire._fleet_resource_pool` deletion + `resource_pool` semantics

**Status:** Complete
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_5.planned_files

**Objective:** Delete `Empire._fleet_resource_pool: Dict[str, float]` durable
state (self-flagged TODO in current code per `empire.py:58-60`).
`Empire.resource_pool` property becomes a **pure aggregation query that
walks the empire's colony stockpiles** and sums by `resource_id`. Per
Phase 0 D2 default: pure-query, no caching — net-zero cost vs the pre-
Phase-5 implementation because the deleted summand was an empty-dict
no-op in production.

The "fleet construction resources move into per-fleet/per-ship
`Container`s" framing in earlier plan revisions was aspirational —
production code never read fleet cargo through `Empire.resource_pool`.
Fleet construction reads `Fleet.has_cargo_resources` /
`Fleet.consume_cargo_resource` directly in `ProductionEngine`. UI
seams (build-queue projector, treasury panel) tolerate the new pure-
aggregate semantics unchanged.

---

## Outcome

**Phase 5 collapsed from 5a-5g to a single 5f cutover** (mirroring
Phase 4f), plus 5g (the promised integration test) and 5h (project-
artifact reconciliation) as Codex-consult verified-finding
remediation.

### Sub-phases

- **5f** — substrate deletion + AST guard (commit `ec80b1648`):
  - Deleted `Empire._fleet_resource_pool` instance attribute.
  - Deleted `Empire.add_resources` / `Empire.consume_resources` mutators
    (zero production callers; the `consume_resources` call at
    `production_engine.py:614` was a dead `else`-branch fallback).
  - Deleted the `resource_pool` property setter (only used by the
    now-retired empire-level deserialization path).
  - Rewrote `Empire.resource_pool` as a pure aggregation query over
    `self.colonies[*].stockpile`.
  - Dropped `resource_pool` key from `Empire.to_dict` save shape;
    `from_dict` ignores it on pre-Phase-5 saves (per CLAUDE.md "no
    save-file migration" rule).
  - Replaced dead `else: empire.has_resources/.consume_resources/.
    resource_pool.get(...)` branches in `production_engine.py` with
    explicit `ValueError`.
  - Extended `tests/static_guards/test_no_legacy_storage_fields.py`
    with 2 new tests pinning absence of `_fleet_resource_pool` and
    the empty-aggregate contract.
  - Rewrote `tests/unit/strategy/data/test_empire_resources.py`
    end-to-end against the new contract.
  - Updated 3 production-engine fallback-branch tests to assert
    `pytest.raises(ValueError)`.
  - Migrated 4 test fixtures (`tests/fixtures/strategy_entities.py`,
    `test_economy_e2e.py`, `test_custom_resource_lifecycle.py`,
    `test_tick_consumption.py`) to seed resources via a hidden
    "_starting_reserve" colony.
  - Updated `docs/systems/resource_system.md` "Planet Storage
    Contract" section.

- **5g** — promised integration test:
  - Authored `tests/integration/test_empire_resource_aggregation.py`
    (14 tests across 3 classes — `TestEmpireResourcePoolAggregation`,
    `TestEmpireResourceQueryHelpers`, `TestEmpireResourceSaveShape`).
  - Closes the `manifest.md:116` promise that the original Phase 5
    prompt left dangling; landed as the Codex-consult verified-
    finding remediation.

- **5h** — project-artifact reconciliation:
  - Updated `plan.md` Phase 5 description, `manifest.md` Phase 5
    rows, this checklist, and `decisions.md` rows to reflect the
    actual shipped contract: `Empire.resource_pool` walks colony
    stockpiles only; fleet/ship cargo stays at its current per-
    fleet API. The original "all containers (planets + fleets +
    ships)" framing was aspirational — no production caller reads
    fleet cargo through `Empire.resource_pool`. Future flows that
    need that view land in Phase 6 (protocol churn) or post-PROJ-
    436 enhancements.

### Phase 0 D2 status

**Pure-query default ships unchanged.** No profiling artifact was
authored because the new aggregation walks the **same per-colony
loop** the previous implementation already walked — the deleted
`_fleet_resource_pool.items()` summand processed an empty dict for
every production code path, so the removal is net-zero cost (no
measurable change in the hot path). If a future large-empire stress
profile shows the colony walk is hot at scale (>100 colonies, hot UI
re-reads), caching with explicit invalidation (PROJ-293 pattern) can
land as a sibling project — not Phase 5 scope.

---

## Phase Completion Checklist

- [x] All sub-phases complete (5f cutover + 5g integration test + 5h docs sync)
- [x] `tests/integration/test_empire_resource_aggregation.py` GREEN (14/14)
- [x] Build-queue + treasury panel UI smoke tests green (read-only
      consumers route through `empire.resource_pool` and tolerate the
      new pure-aggregate semantics unchanged)
- [x] D2 result logged in `decisions.md` (pure-query default
      confirmed; no profiling artifact needed — see "Phase 0 D2
      status" above)
- [x] Full sharded suite green (21203/21203, +14 vs Phase 5f baseline,
      +16 vs Phase 4 baseline)
- [x] Codex consult round-trip complete (artifact at
      `AgentCoordination/Scratchpad/Consult/20260518T022611Z_proj436-phase5-cutover/`),
      verified findings remediated (5g + 5h), unverified findings
      dispositioned in `decisions.md`
- [x] Update status to Complete; update `plan.md` + `phase_state.json`
