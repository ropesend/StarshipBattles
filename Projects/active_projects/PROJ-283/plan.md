# PROJ-283: Race Setup & Habitability Foundation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-283` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-283 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. EnvironmentalPreference + Factor Registry | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. New habitability pipeline (parallel to old) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Unified point budget | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Switch callers + delete legacy fields | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Race Environment UI rebuild | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs + cleanup | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 1 Complete; ready to start Phase 2
**Last Action:** Phase 1 complete. All 6 tasks done, all 62 new tests passing (12 `EnvironmentalPreference` + 39 `HabitabilityFactor` + 11 new `RaceConfig` preference/repro/happiness tests). Full sharded suite 14776/14777 (sole failure is pre-existing flaky quickstart test). `validate_phase.py PROJ-283 1` → PASSED.
**Next Action:** Phase 2 Task 2.1 — add `calculate_habitability_v2(planet, race_config)` to `game/strategy/formulas/habitability.py` iterating `FACTOR_REGISTRY`. Keep v1 intact until Phase 4.
**Blockers:** None. PROJ-284 and PROJ-285 both still depend on PROJ-283 Phase 4+ completing.
**Context for Next Agent:**
- New modules to build on: `game/strategy/data/environmental_preference.py` and `game/strategy/data/habitability_factors.py`. Import `_gaussian_factor` from `habitability.py` — no circular dep because habitability.py only references `RaceConfig` under `TYPE_CHECKING`.
- Each `HabitabilityFactor` carries `weight`, `extractor(planet)->Optional[float]`, and `scorer(value, pref)->[0,1]`. Default scorer is `_default_gaussian_scorer` which coerces `None` to `0.0` before calling `_gaussian_factor`.
- Every `RaceConfig` now carries `preferences: Dict[str, EnvironmentalPreference]` (17 entries: 7 scalar + 10 gas) backfilled from `FACTOR_REGISTRY` defaults via `__post_init__`. Explicit constructor entries are preserved.
- New `base_reproduction_rate: float = 0.03` and `base_happiness: float = 0.5` replace `aptitude_population_growth`/`aptitude_happiness` (still parallel; both live side-by-side during Phase 1–3, deleted in Phase 4).
- Factor weights (tunable, set in Phase 1): gravity=1.0, temperature=1.0, water=0.8, pressure=0.9, tectonic=0.4, magnetic=0.6, radiation=0.6, each gas=0.15 (gas bucket totals 1.5). Phase 2 parity tests may retune.
- Radiation extractor reads `planet.radiation_shielding` — Planet has no intrinsic "incident radiation" field. Default setpoint 0 / tolerance 50 documents "race doesn't care by default." Phase 2 parity tests should flag if this feels off.
- Pre-existing bug: `TestRaceConfigValidation` in `tests/unit/strategy/data/test_race_config.py` has 16 tests that unpack `config.validate()` as a tuple but it returns `ValidationResult`. These failures have been hidden in sharded runs because collection-errors in a sibling file abort the `tests/unit/strategy/` collection before this file is reached. Not in PROJ-283 scope; flagged for later cleanup.

## Overview

Replace the ad-hoc race environment configuration (separate `_ideal`/`_tolerance` field pairs per axis, a `Dict[gas_name, float(-100..100)]` atmosphere-preferences model, an aptitude-driven reproduction rate) with a single **registry-driven** preference system. Every axis — gravity, temperature, water, total pressure, tectonic activity, magnetic field, radiation, and each of 10 gases — is represented by one `EnvironmentalPreference(setpoint, tolerance, ...)` dataclass. The habitability formula and the race setup UI both iterate the same `FACTOR_REGISTRY`, so adding a new axis is a single data edit.

This project is the foundation. PROJ-284 (Colony Demographics Loop) and PROJ-285 (Habitability-to-Production Economy Hook) both depend on it.

## Goals
- Unify all 4 scalar preference axes (gravity/temp/water + new total-pressure) under `(setpoint, tolerance)` with exponential tolerance cost in width.
- Add total surface pressure, tectonic activity, and magnetic field as first-class habitability factors (magnetic splits off from the radiation formula).
- Introduce 10-gas atmosphere preferences (match AtmosphereEngine): O2, N2, CO2, H2O, CH4, H2, He, Ar, NH3, SO2.
- Replace `aptitude_population_growth` with `RaceConfig.base_reproduction_rate` (default 0.03, exponential cost above, linear refund to 0.5% floor).
- Delete `aptitude_happiness` (happiness becomes fully derived in PROJ-284; paying points for it on top of habitability was double-dipping).
- Rebuild the race Environment tab to iterate `FACTOR_REGISTRY` instead of hardcoded sections — one `PreferenceRow` per factor; 10 gases in a collapsible, scrollable sub-panel.
- Update CREATE_DYSON_SPHERE to seed atmosphere from positive-value `gas.*` setpoints rather than the deleted `atmosphere_preferences` dict.
- Leave all existing tests green throughout. User confirmed existing races/saves disposable.

## Scope
**In:**
- New dataclasses `EnvironmentalPreference`, `HabitabilityFactor`; module-level `FACTOR_REGISTRY`.
- Rewrite of `calculate_habitability` to iterate the registry.
- Rewrite of `race_point_budget` around per-factor step constants.
- New fields on `RaceConfig`: `preferences: Dict[str, EnvironmentalPreference]`, `base_reproduction_rate: float`, `base_happiness: float`.
- Deletion of legacy fields: `gravity_ideal`/`gravity_tolerance`, `temperature_ideal`/`temperature_tolerance`, `water_ideal`/`water_tolerance`, `atmosphere_preferences`, `radiation_tolerance`, `aptitude_population_growth`, `aptitude_happiness`.
- Updates to callers: `PopulationEngine` (read `base_reproduction_rate`), `SuperweaponOrderProcessor` (Dyson Sphere atmosphere seeding), habitability callers in strategy layer.
- Full rebuild of `RaceEnvironmentPanel` iterating the registry; new reusable `PreferenceRow` widget.
- Deletion of existing user race JSON files (user confirmed disposable).
- Docs: update `docs/systems/strategy_layer.md` and `docs/04_SERVICES.md` for the new registry pattern.

**Out:**
- Colony-per-species data (`ColonySpeciesConfig`) -> PROJ-284.
- Organics consumption engine, happiness engine, population-engine rework -> PROJ-284.
- Habitability -> harvesting/production multiplier -> PROJ-285.
- Save-game migration.

## Key Files
| Component | File Path |
|-----------|-----------|
| NEW EnvironmentalPreference dataclass | `game/strategy/data/environmental_preference.py` |
| NEW HabitabilityFactor + FACTOR_REGISTRY | `game/strategy/data/habitability_factors.py` |
| RaceConfig | `game/strategy/data/race_config.py` |
| Race point budget | `game/strategy/data/race_point_budget.py` |
| Habitability formula | `game/strategy/formulas/habitability.py` |
| Population engine (reads `base_reproduction_rate`) | `game/strategy/engine/population_engine.py` |
| Dyson Sphere atmosphere seeding | `game/strategy/engine/superweapon_order_processor.py` |
| Race Environment panel UI | `game/ui/panels/race_environment_panel.py` |
| NEW PreferenceRow widget | `game/ui/widgets/preference_row.py` |
| Docs | `docs/systems/strategy_layer.md`, `docs/04_SERVICES.md` |

## Architectural overview (from master plan)

- **One dataclass for every axis.** `EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)`. `RaceConfig.preferences: Dict[str, EnvironmentalPreference]` keyed by canonical axis IDs: `"gravity"`, `"temperature"`, `"water"`, `"pressure"`, `"tectonic"`, `"magnetic"`, `"radiation"`, and `"gas.O2"` ... `"gas.SO2"`.
- **Registry-driven habitability.** `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]` defines each factor's weight, unit, display scale (Pa->kPa for pressures), `extractor(planet)->value`, and `scorer(value, pref)->[0,1]`. `habitability.py` and `race_environment_panel.py` both iterate this registry.
- **Reproduction rate**: new field `base_reproduction_rate: float = 0.03`. Cost: `2^steps - 1` above 3%, linear refund to 0.5% floor. Reuses existing `_exponential_cost(steps)` helper at `race_point_budget.py:125`.
- **Weights (tunable):** gravity=1.0, temperature=1.0, pressure=0.9, water=0.8, radiation=0.6, magnetic=0.6, tectonic=0.4; per-gas weight normalized so the gas bucket sums to 1.5.
- **Happiness** field stays on `RaceConfig` (`base_happiness: float = 0.5`) but stops being a paid aptitude — becomes a pure seed for the PROJ-284 HappinessEngine.

## Reused existing utilities

- `race_point_budget._exponential_cost(steps) = 2^steps - 1` — already present at line ~125, reused for both tolerance and reproduction-rate costs.
- `habitability._weighted_geometric_mean` / `_gaussian_factor` — reused; the registry-driven combiner calls the same helpers with different inputs.
- `get_default_* / set_default_*` module-level accessor pattern (from CLAUDE.md).

## Related Documents
- [design.md](design.md) — Architecture analysis (initial + post-swarm)
- [decisions.md](decisions.md) — Decisions log (includes the user Q&A that shaped this project)
- [manifest.md](manifest.md) — Full file manifest for parallel execution

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual: create a race with 101 kPa pressure ±5 kPa, O2 21 kPa ±3 kPa, temperature 293 K ±20 K, base reproduction 4%, base happiness 0.6. Confirm live budget display matches predicted tolerance costs. Confirm environment tab renders one PreferenceRow per registry entry.
- [ ] Regression: existing habitability tests for near-ideal planets still produce habitability ≈ 0.9 with the new formula (legacy test fixtures updated to use new fields).
- [ ] Docs updated: `docs/systems/strategy_layer.md` documents factor registry + adding-a-factor recipe; `docs/04_SERVICES.md` updated service index.
- [ ] User verified end-to-end by running the race creator.
