# PROJ-284: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Findings from the code sweep done before project breakdown:

### Current `PopulationEngine` (`game/strategy/engine/population_engine.py`)

- `process_population_growth()` runs once per turn (not per tick).
- Iterates empires -> colonies -> species populations.
- Skips if `pop.count <= 0`.
- Fetches `race_config`; calls `score_planet_for_race(colony, race_config)`.
- Effective carrying capacity: `K = int(max_population * habitability)`.
- Base rate: `r = 0.0005 * race.aptitude_population_growth` (1 -> 0.05%, 100 -> 5%). Helper `_aptitude_to_growth_rate` at line ~174.
- Logistic: `growth = r * P * (1 - P/K) * happiness_modifier`.
- Happiness: read directly from `pop.happiness` (0.0-1.0), clamped defensively.
- Applies growth via `int(growth)`; no decline path aside from `P > K` natural negative growth term.

### Current `SpeciesPopulation` (`game/strategy/data/species_population.py`)

- Fields: `race_id: str`, `count: int = 0`, `happiness: float = 0.5`.
- No per-colony configuration fields. No organics consumption tracking.
- Stored as `Planet.populations: List[SpeciesPopulation]` — a flat list, NOT a dict.
- `game_initializer.py` seeds new colonies with `happiness=0.7`.

### Current "happiness" implementation

- Field exists on `SpeciesPopulation` but NO engine ever updates it. It's a static dial.
- `aptitude_happiness` on `RaceConfig` costs points but has no effect on gameplay beyond being a settable number.
- No morale / mood / approval system anywhere else.

### Organics resource

- Defined in `data/resources.json` with `id: "organics"`, `has_quality: true`, `display_group: "planetary"`.
- Harvested by `ResourceHarvester` abilities matching `resource_type: "organics"`.
- Stored in `Planet.stockpile: Dict[resource_id, float]` and aggregated in `Empire.resource_pool`.
- No consumer today. Freely harvested; freely stockpiled.

### Per-colony slider UI pattern (to mirror)

- `AtmosphereTargetEditor` (`game/ui/screens/atmosphere_target_editor.py`): per-gas sliders + species-ideal presets + numeric input. Saves to `planet.atmosphere_target: Dict[str, float]`. Apply callback: `on_apply_callback(planet.id, target_dict)`.
- `GravityTargetEditor`, `WaterTargetEditor`, `RadiationShieldEditor` — all follow the same pattern.
- Accessed via a button on the planet detail; routed through `strategy_window_manager.py`.

### Turn pipeline (`TurnEngine.process_turn` -> sub-ticks)

- 100 sub-ticks per turn. Each tick runs phases 0 through 4 (harvesting, consumption, resupply, production, hazards, orders, actions, planet actions, component activation, movement, conflict).
- AFTER the tick loop: `PopulationEngine.process_population_growth`, `QualityEngine.process_quality_improvement`, `AtmosphereEngine.process_atmosphere`, `WaterEngine.process_water`.
- This project adds two per-turn (not per-tick) steps before population growth: organics consumption + happiness. They land at the same phase-site as population growth — after the 100-tick loop.

## Swarm Findings Summary

Combined analysis from the exploration agents launched during planning.

### Architecture

- All changes land inside `game/strategy/`. No layer-violation concerns.
- `game/strategy/config/economy_config.py` is a new lightweight config module; fits alongside existing `RaceConfig` / game config patterns.
- The consumption engine, happiness engine, and reworked population engine are sequential dependencies: consumption -> happiness -> population. The TurnEngine wiring is a three-line change; the engines themselves are pure per-colony iterators.
- `FoodAllocationEditor` UI lives under `game/ui/screens/`. The existing planet detail panel opens it via an event-router -> `strategy_window_manager.py` redirect (see `atmosphere_target_editor.py` for the reference implementation).

### Key Patterns to Reuse

- **`atmosphere_target_editor.py` UI structure** (`game/ui/screens/atmosphere_target_editor.py`): slider + label + apply callback. Copy-paste the skeleton with race-id per-species rows.
- **`ResourceCatalog` / `get_default_* / set_default_*`** (`game/core/resources.py` + CLAUDE.md): food-resource label lookup + lazy-loaded economy config singleton.
- **`PopulationEngine._get_race_config()` helper**: existing race-id -> `RaceConfig` lookup pattern; reusable in the new engines.

### Dependencies & Risks

1. **PROJ-283 dependency** — PROJ-284 cannot start until `base_reproduction_rate`, `base_happiness`, and the registry-driven `preferences` dict are on `RaceConfig`. Mitigation: strict phase ordering in `projects_index.md`; no code changes on PROJ-284 before PROJ-283 Phase 6 complete.
2. **Test fixture churn** — lots of tests construct `SpeciesPopulation(happiness=X)` with a static value. Those assertions become meaningless after happiness is derived. Mitigation: update tests to either (a) seed the config + food ratio before the engine runs, or (b) assert post-engine happiness by its formula.
3. **`last_food_ratio` is transient** — it's a runtime cache the engines write every turn, not a persisted config value. It must NOT be serialized in `ColonySpeciesConfig.to_dict`. Risk: easy to accidentally serialize; add an explicit test.
4. **Starvation + decline vs. logistic term** — need to make sure the decline term and the logistic term don't compound into overshoot negative populations. Cap at 0.
5. **UI "infinity" slider** — user said food-allocation range is 0 to infinity. Practical UI: slider 0-5 with a typed-value field that accepts higher. Starvation branch makes over-allocation above available stockpile cap at `supplied/needed = (available) / (allocation * pop * food_per_pop)` which will auto-cap.
6. **Dyson-Sphere edge** — a Dyson Sphere planet has no standard extractors (tectonic=0, magnetic=1, etc.) but PROJ-283 defines these as "defined values, not missing". Double check Dyson Sphere tests in PROJ-283 Phase 4 don't crash under PROJ-284.

### Opportunities Discovered

- Once `ColonySpeciesConfig` exists, future per-species knobs (labor share, relocation policy, tax rate) slot in without touching `SpeciesPopulation`.
- `HappinessEngine` is a natural seam for future happiness inputs (war weariness, cultural events, military presence): each added as a term.
- Data-driven food resource sets precedent for data-driven "key resource roles" (e.g. "fuel is whichever resource has role=propellant" pattern could follow).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
