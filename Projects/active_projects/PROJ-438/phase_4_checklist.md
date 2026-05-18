# Phase 4: Planet / Fleet / Empire state-surface slimming

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 3 (ShipInstance categorical doc/invariant pass landed)
**Objective:** Address only the bounded aggregate-root residue that remains after storage moves out: `Planet`'s save-schema breadth and directly-owned adjunct state, `Fleet`/`Empire` persistence-facing aggregate behavior, and the matching read contracts in `galaxy_protocols.py`. Per `decisions.md`, this phase MAY collapse to a smaller protocol/doc sync if the audit shows no high-value extractions — that is a valid outcome, not a failure.

**Resolution (2026-05-18):** Phase 4 collapsed — PROJ-436 Phases 4, 5, and 6 already absorbed every bounded-scope target. Phase 4 produces a contract-pinning test ratchet only. See `decisions.md` row dated 2026-05-18 for the full audit.

---

## Tasks

### Task 4.0: Re-audit the three bounded-scope targets [Simple, planning]
**Files:** `game/strategy/data/planet.py`, `game/strategy/data/fleet.py`, `game/strategy/data/empire.py`, `game/strategy/data/galaxy_protocols.py`, `game/strategy/data/planet_serde.py`
**Tests:** None (planning)

- [x] Planet save-schema breadth + directly-owned adjunct state. *(PROJ-436 Phase 4f already deleted `stockpile`/`max_stockpile`/`staging_yard` dataclass fields and replaced with backward-compat properties. 47 fields are kept per PROJ-372 Risk R1.)*
- [x] Fleet/Empire persistence-facing aggregate behavior. *(PROJ-436 Phase 5 deleted `Empire._fleet_resource_pool`; `resource_pool` is a pure aggregation property over colony stockpiles.)*
- [x] `galaxy_protocols.py` read contracts. *(PROJ-436 Phase 6 explicitly chose "leave as-is" for both `IStockpileHolder` and `IStagingYardHolder` — writers route through `IPlanetMutator`. Shape pinned by `tests/static_guards/test_no_legacy_protocol_names.py`.)*
- [x] Conclude: no new high-ROI extraction. Phase 4 collapses to a contract-pinning ratchet.

### Task 4.1: Pin the post-PROJ-436 contract on Planet/Empire [Simple, TDD-shaped]
**Files:** `tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py` (new)
**Tests:** `pytest tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py`

- [x] Pin `Planet.stockpile`/`max_stockpile`/`staging_yard` as backward-compat properties (NOT dataclass fields).
- [x] Pin `Empire._fleet_resource_pool` is NOT reintroduced during construction.
- [x] Pin `Empire.resource_pool` is a property returning an empty dict for a colonyless empire.
- [x] Add a documentation-marker test (`TestPhase4ScopeCollapseRationale::test_phase_4_collapsed_per_decisions`) so future agents grepping for "Phase 4" find the decisions.md row immediately.
- [x] 6/6 green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. Phase 0 baseline)
- [x] Game still runnable / savable / loadable (no behavior changed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
- [x] `python Projects/scripts/validate_phase.py PROJ-438 4` passes
