# Phase 3: Empire.resident_species()

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-287 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `Empire.resident_species() -> Set[str]` — the canonical "species living in this empire" query used by PROJ-290's uncolonized habitability UI and by PROJ-289's per-species aggregation.

---

## Tasks

### Task 3.1: Write failing tests for `resident_species` [Simple]
**File:** `tests/unit/strategy/data/test_empire.py` (create if missing; check first)
**Tests:** `pytest tests/unit/strategy/data/test_empire.py`

- [x] Test: empire with no colonies → returns `set()`.
- [x] Test: empire with colonies but no populations → returns `set()`.
- [x] Test: single colony with human count=1000 → returns `{"human"}`.
- [x] Test: multi-colony multi-species (human on colony A, voidari on B, both on C) → returns `{"human", "voidari"}` (no duplicates).
- [x] Test: species with count=0 on every colony → EXCLUDED from the set.
- [x] Test: species with count=0 on one colony + count=1 on another → INCLUDED (any colony meets the threshold).

**Notes:** Created `tests/unit/strategy/data/test_empire.py` (no prior file existed). Uses `types.SimpleNamespace` as a minimal `Planet` stand-in (only `populations` is needed) and real `SpeciesPopulation` dataclass instances for the population records. Verified failure mode: `AttributeError: 'Empire' object has no attribute 'resident_species'`.

### Task 3.2: Implement `resident_species` [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/unit/strategy/data/test_empire.py`

- [x] Add method:
  ```python
  def resident_species(self) -> Set[str]:
      """PROJ-287: Return the set of race_ids with count >= 1 anywhere
      in this empire's colonies. Canonical 'species living in this
      empire' set. Used by UI that iterates per-species (e.g.
      uncolonized-habitability display in PROJ-290)."""
      species: Set[str] = set()
      for colony in self.colonies:
          for pop in colony.populations:
              if pop.count >= 1:
                  species.add(pop.race_id)
      return species
  ```
- [x] Add `Set` to typing import if not already present.

**Notes:** Added under a new `--- Population Queries (PROJ-287) ---` banner after the resource-economy methods. Matches the signature in the design sketch verbatim; docstring notes the "not cached" decision with its rationale (see decisions.md 2026-04-18).

### Task 3.3: Verify tests green [Simple]
**Tests:** `pytest tests/unit/strategy/data/test_empire.py`

- [x] All 6 new tests pass.
- [x] Other empire tests unchanged.

**Notes:** 47/47 across `test_empire.py`, `test_empire_fleet_registration.py`, `test_empire_resources.py`.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 4: docs + cleanup)
