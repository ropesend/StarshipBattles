# PROJ-230: Planet Generation Balance Tuning

## Overview

Planet generation produces 98% cold/gas planets and only 2% terrestrial types. Four root causes identified through quantitative analysis using the galaxy inspector tool. This project fixes radiation flux scaling, moon mass distribution, orbital slot bias, and default mass distribution to achieve a game-balanced planet type spread.

## Goals
- Achieve ~20-30% terrestrial planets (Continental, Arid, Pelagic, Magma, Barren)
- Reduce cold/gas dominance from 98% to ~70-80%
- Keep physics internally consistent (temperature still drops with distance, mass determines classification)
- Maintain all existing tests (update hardcoded values where physics constants change)

## Scope

**In Scope:**
- Radiation flux scaling in `physics.py`
- Moon mass distribution in `planet_gen.py`
- Orbital slot distribution bias in `planet_gen.py`
- Default mass distribution parameters in `planet_gen.py`
- Updating affected tests to match new physics constants

**Out of Scope:**
- Classification thresholds in `astrophysics.json` (these are fine; the inputs are wrong)
- Atmosphere generation formula (mass^2 scaling is well-designed)
- Star generation (spectrum normalization is fine; the issue is in the flux bridge)
- Resource generation
- UI changes

## Current State
**Last Updated:** 2026-03-27
**Current Phase:** Planning
**Last Agent Action:** Completed deep dive swarm review
**Next Action:** User approval, then Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** Baseline is 13,866 passed, 2 skipped. The galaxy inspector tool at `scripts/strategy/inspect_galaxy.py` is the verification tool.

## Key Files Reference

| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Radiation flux | `game/strategy/data/physics.py` | `calculate_incident_radiation()` |
| Planet generation | `game/strategy/data/planet_gen.py` | `PlanetGenerator` |
| Moon mass | `game/strategy/data/planet_gen.py` | `_generate_moon_mass()` |
| Orbital slots | `game/strategy/data/planet_gen.py` | `_generate_orbital_slots()` |
| Mass distribution | `game/strategy/data/planet_gen.py` | `_generate_mass_constrained()` |
| Classification | `game/strategy/data/planet_gen.py` | `_determine_type()` |
| Classification config | `game/strategy/data/classification_config.py` | `ClassificationConfig` |
| Blackbody temp | `game/strategy/data/planet_physics.py` | `calculate_blackbody_temperature()` |
| Atmosphere | `game/strategy/data/planet_atmosphere.py` | `generate_atmosphere()` |
| Galaxy inspector | `scripts/strategy/inspect_galaxy.py` | CLI tool |

## Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-27 | Add FLUX_SCALE constant instead of changing spectrum generation | Spectrum normalization is used for rendering and other purposes; adding a physics bridge constant is cleaner than changing the spectrum output units |
| 2026-03-27 | Reduce falloff from r^2.1 to r^1.95 | Broadens habitable zone; small change from inverse-square law stays physically plausible |
| 2026-03-27 | Log-uniform moon mass (0.001%-5%) instead of gaussian(10%) | Real moons are 0.008% of parent (Ganymede/Jupiter). 10% produces Neptune-mass moons from Jupiter parents |
| 2026-03-27 | Triangular orbital distribution instead of uniform | Biases toward inner orbits where planets are warmer, matching real solar system (4 inner planets vs 4 outer) |
| 2026-03-27 | Shift mass mu from 24.5 to 24.0, sigma from 1.5 to 1.0 | giant_min is at log10(6e24)=24.78, only 0.19 sigma above old mean. New params keep most planets terrestrial |

## Initial Analysis

### Root Cause 1: Radiation Flux Units Mismatch (CRITICAL)
`_generate_spectrum()` normalizes so `total_output = luminosity` (solar units, ~1.0 for Sun). But `calculate_incident_radiation()` feeds this into `calculate_blackbody_temperature(flux)` which expects W/m2. A 1-Lsol star produces only 1 W/m2 total, giving 36K at orbit 3. Everything is frozen. Need FLUX_SCALE ~11,500 to get 288K at orbit 5.

### Root Cause 2: Moon Mass Too High
`_generate_moon_mass()` uses gaussian(10%, 2%) of parent. Jupiter parent -> Neptune-mass moons -> ICE_GIANT classification. This inflates the ICE_GIANT count significantly.

### Root Cause 3: Uniform Orbital Distribution
`random.randint(safe_start, 20)` places ~70% of planets at distance >10 (cold zone). No bias toward inner orbits.

### Root Cause 4: Mass Distribution Too Wide
Default log_mu=24.5, log_sigma=1.5. The giant threshold (6e24 kg = log10 24.78) is only 0.19 sigma above mean, so ~40% of planets exceed it.

## Swarm Findings Summary

### Test Impact
- **20+ test files affected**, ~200+ test cases
- **Critical:** `test_radiation_physics.py` and `test_radiation.py` hardcode `1/r^2.1` falloff -- must update to `1/r^1.95`
- **Critical:** `test_radiation_physics.py` tests raw spectrum values without FLUX_SCALE -- tests remain valid since FLUX_SCALE is applied in the calculation, not stored in spectrum
- `test_planet_gen.py` -- moon tests hardcode 10% expectation, must update
- `test_planet_gen.py` -- mass generation tests check bounds, should still pass
- Classification tests use explicit mass/temp inputs -> unaffected by generation changes
- Fixture `create_test_planet()` uses hardcoded Earth values -> unaffected

### Classification Decision Tree (Key Thresholds)
- `giant_min`: 6e24 kg -> ICE_GIANT/JOVIAN branch
- `cryo_max`: 255K -> CRYOPLANET if below
- `vacuum`: 500 Pa -> BARREN if above 200K, CRYO if below
- `continental_temp_min/max`: 255K-330K, pressure > 5000 Pa
- Catch-all: temp < 350K, water > 0.10 -> CONTINENTAL

### Atmosphere Pressure Analysis
- Mars-mass (0.1 Earth): median 1.17 Pa -> 100% below vacuum threshold -> always BARREN/CRYO
- 0.5 Earth-mass: median 25 kPa -> viable for CONTINENTAL
- Earth-mass: median 101 kPa -> robustly habitable
- **No changes needed to atmosphere formula** -- the mass^2 scaling creates a realistic progression

### Risks Identified
1. **FLUX_SCALE could over-correct** -- too high and inner planets become MAGMA. Mitigation: tune iteratively with inspector tool.
2. **Changing falloff exponent affects all systems equally** -- very luminous stars may produce too many hot planets. Mitigation: verify across star types with batch runs.

---

## Phases

### Phase 1: Radiation Flux Fix + Test Updates [Medium]
**Objective:** Fix the temperature calculation so planets get realistic temperatures
**Status:** Not Started

#### Task 1.1: Add FLUX_SCALE and reduce falloff exponent [Simple]
**File:** `game/strategy/data/physics.py`
**Tests:** `pytest tests/unit/strategy/data/test_radiation_physics.py tests/integration/strategy/test_radiation.py -v`
- [ ] Add `FLUX_SCALE = 11500.0` constant with docstring explaining calibration (1 Lsol star at orbit 5 = ~288K)
- [ ] Change falloff from `r ** 2.1` to `r ** 1.95` (line 49)
- [ ] Apply FLUX_SCALE: change `falloff = 1.0 / (r ** 2.1)` to `falloff = FLUX_SCALE / (r ** 1.95)`
- [ ] Update all spectrum band multiplications to use the new falloff

#### Task 1.2: Update radiation tests [Simple]
**File:** `tests/unit/strategy/data/test_radiation_physics.py`
**Tests:** `pytest tests/unit/strategy/data/test_radiation_physics.py -v`
- [ ] Update `test_single_star_at_same_hex`: falloff at r=1 is now FLUX_SCALE (11500), values become `10.0 * 11500 = 115000`
- [ ] Update `test_single_star_distance_2`: expected falloff = `FLUX_SCALE / 2^1.95`
- [ ] Update `test_single_star_distance_5`: expected falloff = `FLUX_SCALE / 5^1.95`
- [ ] Update `test_two_stars_sum_contributions`: star1 at r=1 gets full FLUX_SCALE, star2 at r=3 gets `FLUX_SCALE / 3^1.95`
- [ ] Update `test_zero_distance_clamped`: same as same_hex (FLUX_SCALE applied)
- [ ] Update `test_all_spectrum_bands_scaled`: falloff = `FLUX_SCALE / 2^1.95`
- [ ] Import FLUX_SCALE constant in tests for maintainability

**File:** `tests/integration/strategy/test_radiation.py`
**Tests:** `pytest tests/integration/strategy/test_radiation.py -v`
- [ ] Update `test_falloff_distance_1`: `100 * FLUX_SCALE / 1^1.95 = 100 * 11500`
- [ ] Update `test_falloff_distance_2`: `100 * FLUX_SCALE / 2^1.95`
- [ ] Update `test_falloff_distance_10`: `100 * FLUX_SCALE / 10^1.95`
- [ ] Update `test_clamping`: `100 * FLUX_SCALE`
- [ ] Update `test_additive_measure`: `200 * FLUX_SCALE`
- [ ] Import FLUX_SCALE constant

#### Task 1.3: Verify temperature output [Simple]
**Tests:** Manual verification with inspector
- [ ] Run: `python scripts/strategy/inspect_galaxy.py --seed 42 --systems 10 -v 2`
- [ ] Verify planet temperatures span 50K-1000K+ range (not all frozen)
- [ ] Verify habitable temperatures (255-330K) appear at orbital distances 4-8 for Sun-like stars
- [ ] Check no NaN or extreme values

### Phase 2: Moon Mass + Orbital Bias + Mass Distribution [Medium]
**Objective:** Fix generation parameters to produce more diverse planet populations
**Status:** Not Started

#### Task 2.1: Fix moon mass distribution [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py -v -k moon`
- [ ] Replace `_generate_moon_mass()` (lines 298-315):
  - Remove gaussian(10%, 2%) approach
  - Use log-uniform from 0.001% to 5% of parent mass
  - Keep MASS_CERES floor
  - Remove "moon >= primary" check (log-uniform from 0.001%-5% can't exceed parent)
- [ ] Update moon mass tests to expect new range

#### Task 2.2: Bias orbital slots toward inner orbits [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py -v -k orbital`
- [ ] In `_generate_orbital_slots()`, replace `random.randint(safe_start, max_dist)` (line 156) with triangular distribution: `int(random.triangular(safe_start, max_dist, safe_start + (max_dist - safe_start) * 0.3))`
- [ ] Same for all other `random.randint(safe_start, max_dist)` calls in the method
- [ ] Orbital slot tests should still pass (they test structure, not distribution)

#### Task 2.3: Adjust default mass distribution [Simple]
**File:** `game/strategy/data/planet_gen.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py -v -k mass`
- [ ] In `_generate_mass_constrained()`, change default branch (line 226-228):
  - `log_mu = 24.0` (was 24.5)
  - `log_sigma = 1.0` (was 1.5)
- [ ] Mass generation tests check bounds (MASS_CERES to MASS_JUPITER), should still pass

### Phase 3: Integration Testing + Tuning [Medium]
**Objective:** Verify balance, tune FLUX_SCALE if needed, run full test suite
**Status:** Not Started

#### Task 3.1: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`
- [ ] All tests pass (fix any remaining failures from Phase 1/2)

#### Task 3.2: Balance verification with inspector [Medium]
**Tests:** Manual verification
- [ ] Run: `python scripts/strategy/inspect_galaxy.py --batch 20 --seed 1000 --systems 50 -v 1`
- [ ] Compare planet type distribution against baseline:
  - Baseline: Terrestrial 2.2%, Gas Giants 47.9%, Cold/Small 49.9%
  - Target: Terrestrial ~20-30%, Gas Giants ~20-30%, Cold/Small ~40-50%
- [ ] Verify resource distribution is still reasonable
- [ ] Verify habitability scores improved (avg should be >0.15, was 0.11)
- [ ] Verify connectivity unchanged (warp lanes not affected)

#### Task 3.3: Tune FLUX_SCALE if needed [Simple]
**File:** `game/strategy/data/physics.py`
- [ ] If terrestrial % is too low: increase FLUX_SCALE
- [ ] If too many MAGMA planets: decrease FLUX_SCALE
- [ ] If habitable zone too narrow: decrease falloff exponent further (e.g., 1.9)
- [ ] Re-run tests after any tuning changes
- [ ] Document final FLUX_SCALE value in decisions.md

#### Task 3.4: Verify across galaxy types [Simple]
**Tests:** Manual verification
- [ ] Run inspector with `--type spiral`, `--type cluster`, `--type ring`
- [ ] Verify balance is consistent across galaxy types (generation is per-system, not per-galaxy)

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/` - 13,866 passed, 2 skipped

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Run inspector: `python scripts/strategy/inspect_galaxy.py --seed 42 --systems 10 -v 1`

### Final Verification
- [ ] `python scripts/strategy/inspect_galaxy.py --batch 20 --seed 1000 --systems 50` -- improved distribution
- [ ] `python scripts/strategy/inspect_galaxy.py --seed 42 --type spiral --systems 25 -v 2` -- reasonable per-planet values
- [ ] Run full test suite: `pytest tests/ -n 12` -- all pass
- [ ] Verify no docs need updating (these changes affect generation tuning, not architecture)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (13,866+)
- [ ] Balance target achieved (terrestrial >15%)
- [ ] User verified
