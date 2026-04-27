# Phase 2: `StarSystem.archetype` + `intrinsic_abilities` fields + generation

**Status:** Not Started

---

## Tasks

### Task 2.1: Add fields to `StarSystem` [Simple]
**File:** `game/strategy/data/galaxy.py`
**Tests:** `pytest tests/unit/strategy/data/test_galaxy.py`

- [ ] Failing tests:
  - [ ] `test_starsystem_has_archetype_default_none`
  - [ ] `test_starsystem_has_intrinsic_abilities_default_empty`
  - [ ] `test_starsystem_to_dict_carries_archetype_and_abilities`
  - [ ] `test_starsystem_from_dict_defaults_when_missing`
- [ ] Add `archetype: Optional[str] = None` and `intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)`.
- [ ] Update serialization.

**Notes:**

### Task 2.2: Roll archetypes during galaxy generation [Medium]
**File:** Locate galaxy generation entry (`game/strategy/generation/`).
**Tests:** Galaxy generation tests.

- [ ] Failing tests:
  - [ ] `test_galaxy_generation_assigns_archetypes_at_configured_rate` — with `archetype_chance=1.0`, every system has an archetype.
  - [ ] `test_archetype_chance_zero_yields_no_archetypes` — opt-out works.
  - [ ] `test_assigned_archetype_populates_intrinsic_abilities` — non-void archetype yields non-empty intrinsic_abilities with rolled values.
  - [ ] `test_archetype_assignment_deterministic_with_seed`.
- [ ] In the generator: load `data/system_archetypes.json`. For each system, with probability `archetype_chance`, choose a non-`void` archetype uniformly and call `roll_intrinsic_abilities`.

**Notes:**

### Task 2.3: Save/load roundtrip [Simple]
**File:** `tests/integration/save_load/test_roundtrip_galaxy.py` (or similar).

- [ ] Generate a galaxy with archetype rolling. Save. Load. Assert archetype + intrinsic_abilities preserved.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
