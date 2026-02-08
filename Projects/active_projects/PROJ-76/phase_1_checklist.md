# Phase 1: Data Layer - Empire-Wide Queue Collection

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add function to collect all build queue sources across the empire

---

## Tasks

### Task 1.1: Add `collect_all_build_queues_for_empire()` function [Simple]

**File:** `game/strategy/data/build_queue_source.py`
**Tests:** `pytest tests/unit/strategy/data/test_build_queue_source.py`

- [x] Add new function after `collect_build_queues_at_hex()` (after line 136)
- [x] Iterate `empire.colonies` to collect planet base queues
- [x] For each planet, iterate facilities to find shipyard queues (use `_facility_is_shipyard()`)
- [x] Iterate `empire.fleets` to collect fleet space yard queues
- [x] Return `List[BuildQueueSource]` with all sources
- [ ] Add `get_hex_for_source(source, galaxy)` helper to get global hex coordinate (deferred to Phase 5 - Navigation)

**Implementation Pattern:**
```python
def collect_all_build_queues_for_empire(empire, galaxy) -> List[BuildQueueSource]:
    """Gather all build queue sources across the entire empire."""
    sources: List[BuildQueueSource] = []

    # Planet queues
    for planet in empire.colonies:
        # Base queue (complexes only)
        sources.append(BuildQueueSource(
            queue_id=f"planet_{planet.id}_base",
            display_name=f"{planet.name} - Base",
            owner_entity=planet,
            construction_queue=planet.construction_queue,
            can_build_ships=False,
            can_build_complexes=True,
            context_type="planet",
        ))

        # Shipyard facility queues
        shipyard_index = 0
        for facility in planet.facilities:
            if _facility_is_shipyard(facility):
                shipyard_index += 1
                sources.append(BuildQueueSource(
                    queue_id=facility.instance_id,
                    display_name=f"{planet.name} - Shipyard {shipyard_index}",
                    owner_entity=planet,
                    construction_queue=facility.construction_queue,
                    can_build_ships=True,
                    can_build_complexes=True,
                    context_type="planet",
                ))

    # Fleet queues
    for fleet in empire.fleets:
        if not fleet.has_space_shipyard:
            continue
        sources.append(BuildQueueSource(
            queue_id=f"fleet_{fleet.id}",
            display_name=f"{fleet.name} - Space Yard",
            owner_entity=fleet,
            construction_queue=fleet.construction_queue,
            can_build_ships=True,
            can_build_complexes=True,
            context_type="fleet",
        ))

    return sources
```

**Notes:**

---

### Task 1.2: Add tests for empire-wide collection [Simple]

**File:** `tests/unit/strategy/data/test_build_queue_source.py`
**Tests:** Run same file

- [x] Add test: `test_collect_all_build_queues_empty_empire` - empty empire returns empty list
- [x] Add test: `test_collect_all_build_queues_with_planet_base_queue` - planet has base queue
- [x] Add test: `test_collect_all_build_queues_with_shipyard_facility` - planet with shipyard facility
- [x] Add test: `test_collect_all_build_queues_with_fleet_space_yard` - fleet with space yard
- [x] Add test: `test_collect_all_build_queues_mixed_sources` - combination of all types
- [x] Add test: `test_collect_all_build_queues_non_operational_shipyard_excluded` - broken yard excluded
- [x] Add test: `test_collect_all_build_queues_fleet_without_yard_excluded` - no-yard fleet excluded

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests pass: `pytest tests/unit/strategy/data/test_build_queue_source.py` (22 passed)
- [x] No regressions: `pytest tests/ --testmon` (183 passed, 2 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
