# Phase 6: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update `docs/systems/strategy_layer.md` and `docs/04_SERVICES.md` for the new registry-driven model. Sweep for orphan references to deleted fields. Prepare the codebase for PROJ-284 and PROJ-285 to build on the new foundation.

---

## Tasks

### Task 6.1: Document the factor registry [Medium]
**File:** `docs/systems/strategy_layer.md`

- [ ] Add a section "Race Preferences & Habitability (PROJ-283)" explaining:
  - The `FACTOR_REGISTRY` pattern
  - `EnvironmentalPreference(setpoint, tolerance, ...)` dataclass
  - The weighted geometric mean combiner with factor weights
  - Adding-a-factor recipe: one `HabitabilityFactor` registration, nothing else
  - The `(setpoint is free, tolerance costs exponentially)` UX contract
- [ ] Reference `game/strategy/data/habitability_factors.py` and `game/strategy/formulas/habitability.py` with line numbers.
- [ ] Show the per-factor weight table.

### Task 6.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [ ] Add entries for `environmental_preference.py` and `habitability_factors.py` under `game/strategy/data/`.
- [ ] Update the `habitability.py` entry to reference the new registry-driven `calculate_habitability` function.
- [ ] Add a callout about the `base_reproduction_rate` and `base_happiness` fields on `RaceConfig` replacing the deleted aptitudes.

### Task 6.3: Update CLAUDE.md if patterns changed [Simple]
**File:** `CLAUDE.md`

- [ ] Review the "Architecture Principles" and "Key Patterns" sections.
- [ ] Add a one-line reference to the factor-registry pattern if it's a new pattern worth broadcasting (judgement call by implementer).

### Task 6.4: Orphan sweep [Simple]
**Tests:** Manual grep verification

- [ ] `grep -rn "atmosphere_preferences\|gravity_ideal\|gravity_tolerance\|temperature_ideal\|temperature_tolerance\|water_ideal\|water_tolerance\|radiation_tolerance\|aptitude_happiness\|aptitude_population_growth\|_aptitude_to_growth_rate" .` in the repo root.
- [ ] The only permitted hits: `decisions.md`, archived projects under `Projects/deep_archive/` or `Projects/archived_projects/`, `docs/_ignore/`, and historical commit messages (git log).
- [ ] Any remaining production / test code hit = bug. Fix or document as a PROJ-284 / PROJ-285 responsibility.

### Task 6.5: Cross-project coordination notes [Simple]
**File:** Add brief notes to `Projects/active_projects/PROJ-284/decisions.md` and `Projects/active_projects/PROJ-285/decisions.md`

- [ ] Note the actual commit hash where PROJ-283 landed.
- [ ] Confirm `base_reproduction_rate` / `base_happiness` field shapes for downstream consumers.
- [ ] Document any weight retuning done during Phase 2 (PROJ-285 hooks multiply habitability into rates — wants stable weights).

### Task 6.6: Final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Full suite green.
- [ ] Manual: end-to-end smoke test from PROJ-283 plan.md Verification section.
- [ ] PROJ-283 plan.md Current State updated to "Complete, ready to close."

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
