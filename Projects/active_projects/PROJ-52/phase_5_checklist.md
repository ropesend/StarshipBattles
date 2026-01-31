# Phase 5: Physics-Driven System Generation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-52 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Data-driven system blueprints with physics-derived classification

---

## Task 5.1: Create System Blueprints JSON [Medium]
**File:** `data/system_blueprints.json`
**Tests:** `python -m pytest tests/unit/strategy/generation/test_system_blueprints.py`

- [ ] Define blueprint schema (star_count distribution, mass ranges, planet slot ranges)
- [ ] Create "Binary_NoPlanets" blueprint
- [ ] Create "Solar_Like" blueprint (1 star, 4-8 planets)
- [ ] Create "RedDwarf_Pack" blueprint (dense small planets)
- [ ] Create "Empty_Warp_Hub" blueprint (0-1 planets)
- [ ] Create "Gas_Giant_System" blueprint (large outer planets)
- [ ] Add weighted selection mechanism

**Notes:**

---

## Task 5.2: Create Astrophysics JSON [Medium]
**File:** `data/astrophysics.json`
**Tests:** `python -m pytest tests/unit/strategy/generation/test_astrophysics.py`

- [ ] Define mass distributions (log-normal curves for Rocky, GasGiant, Star)
- [ ] Define orbit zone calculations (Hot, Goldilocks, Cold relative to luminosity)
- [ ] Define habitable zone formula parameters
- [ ] Define ice line calculation parameters
- [ ] Define atmospheric retention thresholds

**Notes:**

---

## Task 5.3: Refactor Planet Classification [Medium]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `python -m pytest tests/unit/strategy/data/test_planet_classification_logic.py`

- [ ] Load classification rules from `astrophysics.json`
- [ ] Replace hardcoded thresholds in `_determine_type()` (lines 274-352)
- [ ] Derive classification from: mass + orbit zone + stellar radiation + atmosphere
- [ ] Add "habitable zone" calculation based on star luminosity
- [ ] Ensure all 11 planet types still achievable
- [ ] Maintain backward compatibility (same inputs → same outputs for existing tests)

**Notes:**

---

## Task 5.4: Refactor Star System Generation [Medium]
**Files:** `game/strategy/data/stars.py`, `galaxy.py`
**Tests:** `python -m pytest tests/integration/strategy/test_star_generation.py`

- [ ] Load system blueprints in `StarGenerator`
- [ ] Implement `generate_from_blueprint(blueprint_name)` method
- [ ] Update `generate_system_stars()` to optionally use blueprints
- [ ] Add blueprint parameter to `Galaxy.generate_planets()`

**Notes:**

---

## Task 5.5: Add Physics Validation [Simple]
**File:** `game/strategy/data/planet_physics.py`
**Tests:** `python -m pytest tests/unit/strategy/data/test_planet_physics.py`

- [ ] Add `validate_planet_parameters(mass, radius, density) -> List[str]`
- [ ] Check radius is sensible for mass (1e6 - 1e8 meters)
- [ ] Check escape velocity < 0.1c
- [ ] Check surface gravity in reasonable range
- [ ] Call validation in `_create_single_planet()` with logging for violations

**Notes:**

---

## Phase 5 Verification
- [ ] All unit tests pass: `python -m pytest tests/unit/strategy/`
- [ ] System blueprints load and apply correctly
- [ ] Planet classification matches physics expectations
- [ ] Habitable zone planets appear in correct orbital range
- [ ] All 11 planet types are still achievable
- [ ] Full test suite still passes: `python -m pytest tests/`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

## Handoff Notes
(To be filled when phase completes)
