# Phase 1: Component ability convergence (`Container` parser)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-436 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/simulation/components/abilities/container.py` (new)
- `game/simulation/components/abilities/cargo.py`
- `game/simulation/components/abilities/resources.py`
- `tests/unit/simulation/components/abilities/test_container_ability.py` (new)

**Objective:** Add the `Container` ability parser (`{capacity_mass, allowed_kinds, allowed_type_ids}`). Keep `ResourceStorage` / `CargoStorage` / `VehicleBay` as legacy parsers that compile to `Container` internally so existing `data/components.json` keeps loading without any data-file changes. No runtime behavior change yet — this phase is the bridge that lets later phases swap callers to `Container` while existing components stay valid.

---

## Tasks

To be authored at phase start. Expected shape:

1. RED — `test_container_ability.py` parser parity tests: loading the existing 3 ability JSON shapes through the new Container parser produces equivalent runtime state.
2. GREEN — implement `Container` ability class (mirrors structure of `CargoStorage` / `ResourceStorage` / `VehicleBay`); register through ability registry.
3. Make `ResourceStorage` / `CargoStorage` / `VehicleBay` constructors emit equivalent `Container` instances internally (or delegate to a shared compile step).
4. Run existing `tests/unit/validation/test_component_definitions.py` (1014 tests per shard timing) — must stay green.
5. Run full sharded suite; confirm zero regression.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Existing component definitions tests green
- [ ] Full sharded suite green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] Update `phase_state.json` phase_1.status to `complete`
