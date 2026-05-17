# Phase 10: Doc refresh

**Status:** Not Started
**Depends on:** phase_9
**Review Mode:** lightweight
**Files (planned):** see `phase_state.json` phase_10.planned_files

**Objective:** Update documentation to reflect the unified Container substrate. Touch only what this project changed; broader doc drift from PROJ-422..435 stays out of scope (logged for a separate hygiene pass if needed).

---

## Tasks

To be authored at phase start. Expected:
- 10a — `docs/systems/resource_system.md`: rewrite around the unified `Container`. Drop references to `VALID_CARGO_TYPES`.
- 10b — `docs/systems/production_system.md`: update for ProductionEngine consuming Container protocol; remove `context_type` references.
- 10c — `docs/systems/strategy_layer.md`: update storage/inventory section; reference `Container` model.
- 10d — `docs/01_ARCHITECTURE.md`: if it describes the old storage abstractions, update.
- 10e — `docs/02_PATTERNS.md`: add or update the Container pattern entry (alongside existing Pattern #34 Weapon Family Registry, Pattern #35 Stat Contributor Registry, Pattern #37 Typed `DeployedGroup` Family).
- 10f — Add `> **Last verified:**` blockquote update per PROJ-307 convention (docs/03_CONVENTIONS.md §9).

---

## Phase Completion Checklist
- [ ] All touched docs reflect the unified Container substrate
- [ ] Doc-sync grep checks (e.g., references to deleted symbols `VALID_CARGO_TYPES`, `_fleet_resource_pool`, `_CarriedItemsProxy`) all return zero in docs
- [ ] `> **Last verified:**` blockquote stamps updated
- [ ] Update status to Complete; update plan.md + phase_state.json
