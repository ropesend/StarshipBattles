# Phase 6: System Inspector Sandbox (Mode B)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Detailed physics inspection of single systems

---

## Task 6.1: Add Mode Toggle UI [Simple]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - mode switches correctly

- [ ] Add mode state variable (LAYOUT_VIEW / SYSTEM_INSPECTOR)
- [ ] Update control panel to show mode-specific controls
- [ ] Hide/show appropriate UI elements per mode

**Notes:**

---

## Task 6.2: Implement System Inspector Controls [Medium]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - controls work correctly

- [ ] Add "System Blueprint" dropdown (from `system_blueprints.json`)
- [ ] Add "Seed" input for system generation
- [ ] Add "Generate System" button
- [ ] Add star property overrides (optional: mass, type)

**Notes:**

---

## Task 6.3: Implement System Visualization [Medium]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - system renders correctly

- [ ] Render central star(s) with size based on mass
- [ ] Render orbital rings at each planet's orbit distance
- [ ] Render planets with size/color based on type
- [ ] Add labels for planet names
- [ ] Center view on system

**Notes:**

---

## Task 6.4: Implement Inspector Panel [Medium]
**File:** `game/ui/screens/galaxy_gen_sandbox.py`
**Tests:** Manual - clicking shows correct data

- [ ] Click detection for stars and planets
- [ ] Display panel showing clicked object's properties:
  - Stars: Mass, Temperature, Luminosity, Type, Spectrum
  - Planets: Mass, Radius, Gravity, Temperature, Pressure, Type, Atmosphere
- [ ] Show "Calculated Class" with explanation of why
- [ ] Show physics derivation chain (mass → density → gravity → etc.)

**Notes:**

---

## Phase 6 Verification
- [ ] Mode toggle switches between Layout/Inspector
- [ ] System Inspector generates single systems correctly
- [ ] Click inspection shows correct physics data
- [ ] Classification explanation is accurate
- [ ] All planet types render with appropriate visuals
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"

---

## Handoff Notes
(To be filled when phase completes)

---

## Final Project Verification
When Phase 6 is complete, run final verification:
- [ ] Full test suite passes: `python -m pytest tests/` (NOT --testmon)
- [ ] All 7 galaxy types generate correctly
- [ ] Sandbox works for both modes (Layout View and System Inspector)
- [ ] Performance targets met (2500 systems, 60 FPS)
- [ ] No regressions in existing gameplay
- [ ] Update plan.md Verification section
