# Phase 1: System archetypes data registry

**Status:** Not Started
**Objective:** Create `data/system_archetypes.json` with the initial archetype set.

---

## Tasks

### Task 1.1: Create `data/system_archetypes.json` [Simple]
**File:** `data/system_archetypes.json` (NEW)

- [ ] Write registry per [design.md](design.md). Confirm initial archetype set with the user (suggested: nebula, ancient_battlefield, precursor_ruins, ion_field, void).
- [ ] Add `Paths.SYSTEM_ARCHETYPES_FILE` to `game/core/paths.py`.

**Notes:**

### Task 1.2: Add archetype config to galaxy generation [Simple]
**File:** Locate galaxy generation config (e.g. `data/galaxy_generation_config.json`).

- [ ] Add `archetype_chance: 0.15` config knob (default).
- [ ] Document semantics: probability that any given system gets a non-null archetype.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] `pytest tests/ --testmon` clean
- [ ] Update status to `Complete`
- [ ] Update plan.md
