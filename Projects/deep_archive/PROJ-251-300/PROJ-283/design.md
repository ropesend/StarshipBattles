# PROJ-283: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Findings from code review of the existing race + habitability system (agent sweep before project breakdown):

### Current `RaceConfig` (game/strategy/data/race_config.py)

- **Environment preferences** are spread across multiple ad-hoc fields: `gravity_ideal`/`gravity_tolerance`, `temperature_ideal`/`temperature_tolerance`, `water_ideal`/`water_tolerance`, `radiation_tolerance` (single-sided), and `atmosphere_preferences: Dict[gas_name, float(-100..100)]`.
- **Atmosphere preferences** do not express pressure or tolerance — they are qualitative weights. `GAS_NAME_TO_FORMULA` supports 6 gases (O2, N2, CO2, CH4, H2, He) while `AtmosphereEngine` supports 10 (adds H2O, Ar, NH3, SO2). Mismatch.
- **Aptitudes** (9 fields at 1-100, default 50) include `aptitude_happiness` and `aptitude_population_growth`. Both cost points.
- **Validation** bounds exist per-field, duplicated across fields with the same shape (ideal + tolerance).

### Current `race_point_budget.py`

- Total budget: 100.
- Aptitude costs: linear below 50, exponential `2^((value-50)/10)` above.
- Tolerance costs: `2^steps - 1` per tolerance-axis, with hardcoded per-axis step constants (gravity 0.1 g, temperature 10 K, water 0.1, radiation 10, atmosphere 10 per gas).
- Existing helper `_exponential_cost(steps)` at line ~125 is ready to reuse.

### Current `habitability.py`

- `score_planet_for_race(planet, race_config)` -> `calculate_habitability()`.
- Factors: gravity (Gaussian, weight 1.0), temperature (Gaussian, weight 1.0), water (Gaussian, weight 0.8), atmosphere (preference-weighted, weight 0.7), radiation (threshold + magnetic-field fallback, weight 0.6).
- Combiner: weighted geometric mean via `exp(Σw*log(f)/Σw)` with epsilon clamping. One near-zero factor tanks the score.
- `_gaussian_factor` and the weighted-geometric-mean combiner are reusable utility functions.
- Atmosphere scoring today maps planet gas partial pressures to race preferences via `(pref+100)/200`, weighted by gas fraction and preference magnitude.
- Radiation factor uses `magnetic_field + radiation_shielding`; splitting magnetic out is a behavior change not a drop-in.

### Current `RaceEnvironmentPanel` (game/ui/panels/race_environment_panel.py)

- Hardcoded sections per axis: Gravity (ideal + tolerance sliders), Temperature (ideal + tolerance), Radiation (single slider), Water (ideal + tolerance), Atmosphere (one slider per gas for 6 gases).
- Live budget label at top reads `RacePointBudget.get_remaining_points()`.
- Used only by `RaceSetupScreen`.

### Callers of legacy fields

- `PopulationEngine.process_population_growth()` — reads `aptitude_population_growth` via `_aptitude_to_growth_rate()` helper.
- `SuperweaponOrderProcessor.process_create_dyson_sphere` — reads `race.atmosphere_preferences`, filters positive values, translates display names to formulas, scales to Pa.
- `habitability.calculate_atmosphere_factor` — reads `race.atmosphere_preferences`.
- Various test fixtures across the suite.

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

- UI -> Strategy -> Simulation -> Core layering; `game/strategy/data/` contains `RaceConfig` and the data classes this project extends. No layer-violation concerns with the planned changes.
- Extend `game/strategy/data/` with `environmental_preference.py` and `habitability_factors.py`. Both are pure data + pure functions; no cross-layer imports.
- `game/ui/panels/race_environment_panel.py` and a new `game/ui/widgets/preference_row.py` iterate `FACTOR_REGISTRY` — the registry is imported top-down; no circular deps because the registry module imports nothing from strategy-formulas or UI.

### Key Patterns to Reuse

- **`_exponential_cost(steps) = 2^steps - 1`**: `game/strategy/data/race_point_budget.py:~125` — reused for tolerance cost and (new) reproduction rate cost.
- **Weighted geometric mean + Gaussian factor**: `game/strategy/formulas/habitability.py` — reused; the registry-driven combiner calls the same helpers with different inputs.
- **`get_default_* / set_default_*` module accessor pattern** (see CLAUDE.md): applied to loading the registry and any cached data.
- **Dataclass with `to_dict`/`from_dict`**: matches existing `SpeciesPopulation`, `PlanetaryFacility` serialization style.

### Dependencies & Risks

1. **Callers of `race.atmosphere_preferences`** — four known sites (habitability, Dyson Sphere seeding, validators, race library tests). Phase 4 must migrate all four in the same commit. Mitigation: grep sweep and dedicated migration task per call site.
2. **Factor weight retuning** — current habitability formula uses weights `1.0/1.0/0.8/0.7/0.6`. Splitting magnetic out of radiation and adding total-pressure/tectonic requires retuning. Mitigation: include parity tests where the new formula matches the old for the 5 shared axes on ideal planets; adjust weights if drift > 0.05.
3. **Race fixtures across test suite** — dozens of tests construct `RaceConfig` with legacy kwargs. Phase 4 ripples broadly. Mitigation: introduce a `make_test_race(preferences_overrides=...)` helper in conftest/fixtures early to minimize fixture churn.
4. **Dyson Sphere atmosphere seeding** — `SuperweaponOrderProcessor` currently iterates `atmosphere_preferences` positives to seed atmosphere. After removing the field, seed from `race.preferences["gas.*"]` entries with setpoint > 0. Behavior equivalent for races with meaningful preferences.
5. **UI layout** — 10 gases x 2 sliders + 7 scalar axes + base reproduction + base happiness is a lot of vertical space. Scrollable container + collapsible gas group required.

### Opportunities Discovered

- Adding a new habitability factor (e.g. "day length" later) becomes a single `HabitabilityFactor(...)` registration. No engine, UI, budget, or formula edits.
- Per-gas partial-pressure tolerance eliminates the current "atmosphere_preference" fuzziness and gives the habitability formula sharper gradients.
- Deleting `aptitude_happiness` removes the long-standing double-dip where players could pay points for happiness AND gain it again via habitability score.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
