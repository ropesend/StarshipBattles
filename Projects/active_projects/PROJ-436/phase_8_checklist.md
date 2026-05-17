# Phase 8: `ProductionEngine.context_type` deletion

**Status:** Not Started
**Depends on:** phase_7
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_8.planned_files

**Objective:** Delete the 3 `context_type` branch sites in `game/strategy/engine/production_engine.py` (lines 503-521, 549, 606-615). ProductionEngine reads inputs from any `Container` whose policy accepts them and writes outputs to any `Container` whose policy accepts them. `context_type` stops being a routing signal — what kind of entity holds the container is irrelevant to production.

---

## Tasks

To be authored at phase start. Expected sub-phase shape:
- 8a — `ProductionEngine._select_input_container(costs)` / `_select_output_container(output)` helpers that dispatch by `Container.accepts()` per costs/output.
- 8b — migrate the lines 503-521 branch to use the helpers.
- 8c — migrate the line 549 branch.
- 8d — migrate the lines 606-615 branch (empire-pool fallback removed).
- 8e — final cutover: delete `getattr(colony_or_fleet, 'context_type', None)` reads; grep gate.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] Grep gate: zero `context_type` reads in `game/strategy/engine/production_engine.py`
- [ ] `tests/integration/test_production_engine_container_unified.py` green
- [ ] Existing production engine integration tests green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
