# Handoff: PROJ-283 — Phase 2 (New Habitability Pipeline, Parallel to Old)

Resume **PROJ-283** at **Phase 2**. The previous session ended after completing Phase 1 (data model foundation). Context was at roughly 52% at session start and climbed during implementation; stopping cleanly at the phase boundary preserves a full-cache start for Phase 2.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. The project plan assumes you understand the surrounding architecture, conventions, and related code — if you don't, you'll make short-sighted decisions that the plan's author took for granted. Prefer loading extra context.

### 1. Foundation docs (always read these first)
- `docs/README.md` — doc index + task-driven reading order
- `docs/01_ARCHITECTURE.md` — layer structure + package APIs + dependency rules
- `docs/02_PATTERNS.md` — design patterns used in this codebase
- `docs/03_CONVENTIONS.md` — naming, file org, test conventions, line budgets
- `CLAUDE.md` — project non-negotiables (3 NON-NEGOTIABLE RULES: TDD, docs-in-sync, clean-sheet design)

### 2. Task-specific docs
- `docs/systems/strategy_layer.md` — strategy-layer architecture; habitability scoring section
- `docs/systems/production_system.md` — for Phase 2 weight-tuning sanity check (production/harvest don't yet use habitability; those hooks land in PROJ-285)

### 3. Related code (read for context, even if you won't modify it)
- `game/strategy/data/environmental_preference.py` — Phase 1 creation. `EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)`, self-validates on construction, `to_dict`/`from_dict` JSON-tolerant (casts int to float). Docstring encodes the semantic contract.
- `game/strategy/data/habitability_factors.py` — Phase 1 creation. Top-level `FACTOR_REGISTRY: Dict[str, HabitabilityFactor]`. Helpers: `get_factor(id)`, `iter_scalar_factors()`, `iter_gas_factors()`. **Read the `_default_gaussian_scorer` docstring** — it encodes the None-handling contract (`None` → treat as `0.0`, so race with `setpoint > 0` scores low on missing data, race with `setpoint == 0` scores ideal).
- `game/strategy/data/race_config.py` — existing. Phase 1 added `preferences`, `base_reproduction_rate`, `base_happiness` **parallel to legacy fields**. `__post_init__` backfills `preferences` from registry defaults for missing factor ids. Legacy `gravity_ideal`/`atmosphere_preferences`/etc. still exist and still drive the old `calculate_habitability` — deleted in Phase 4, NOT Phase 2.
- `game/strategy/formulas/habitability.py` — existing. Current `calculate_habitability(...)` is the v1 formula. **Keep it callable; Phase 2 adds `calculate_habitability_v2` in PARALLEL.** The existing helpers `_gaussian_factor` (line ~23) and the weighted-geometric-mean combiner (lines ~267-285 inside `calculate_habitability`) are reusable — extract or reuse via direct call.
- `game/strategy/data/planet.py` — Planet dataclass has `surface_gravity`, `surface_temperature`, `surface_water`, `surface_pressure`, `tectonic_activity`, `magnetic_field`, `radiation_shielding`, `atmosphere: Dict[str, float]` (Pa). Extractors in `habitability_factors.py` already read these. No Planet changes needed in Phase 2.
- `game/strategy/engine/population_engine.py` — uses v1 habitability today. Leave alone until Phase 4.
- `game/strategy/engine/superweapon_order_processor.py` — CREATE_DYSON_SPHERE uses `race.atmosphere_preferences`. Leave alone until Phase 4.

### 4. Related tests (read so you know what "working" looks like)
- `tests/unit/strategy/data/test_environmental_preference.py` — 12 tests, demonstrates construction + validation + round-trip.
- `tests/unit/strategy/data/test_habitability_factors.py` — 39 tests, demonstrates registry-iteration patterns; the `TestScorer` class has the exact edge cases your v2 formula must match (at-setpoint=1.0, 1σ≈0.61, far→0, None-with-zero=1.0, None-with-nonzero→near-zero).
- `tests/unit/strategy/data/test_race_config.py::TestRaceConfigPreferencesField` — 5 tests demonstrating how `race_config.preferences` is populated and round-tripped.
- `tests/unit/strategy/formulas/test_habitability.py` — existing v1 tests; preserve them. Phase 2 parity tests should confirm v1 vs v2 agree on the 5 shared axes (gravity/temperature/water/atmosphere/radiation) for near-ideal inputs.

## Only now: read the project files
Read in this order — the plan depends on all of the above:
1. `Projects/active_projects/PROJ-283/design.md` — architectural rationale (initial analysis + swarm findings)
2. `Projects/active_projects/PROJ-283/decisions.md` — full decision log including the user Q&A that shaped the design
3. `Projects/active_projects/PROJ-283/plan.md` § **Current State** — authoritative handoff (updated end of Phase 1)
4. `Projects/active_projects/PROJ-283/phase_2_checklist.md` — Phase 2 task list
5. `Projects/active_projects/PROJ-283/manifest.md` — file manifest (Phase 1 files checked with ✓)

## First action
Open `phase_2_checklist.md`. The literal next unchecked item is:

> **Task 2.1: Implement `calculate_habitability_v2`** [Medium]
> - [ ] Add function `calculate_habitability_v2(planet, race_config) -> float`.

Follow Strict TDD: create the test file first (`tests/unit/strategy/formulas/test_habitability_v2.py`), add a single failing test, then implement. The `test_habitability_factors.py::TestScorer` class models the per-factor scorer behavior you'll combine.

## Watchouts (from the previous session)

1. **Test collection bug**: `tests/` full-collection aborts with a collection error in `tests/unit/strategy/engine/test_build_order_command_handler.py`, which **silently skips** `tests/unit/strategy/data/test_race_config.py` and several sibling files. This has been hiding 16 pre-existing `TestRaceConfigValidation` failures where the tests unpack `config.validate()` as a tuple but it returns `ValidationResult`. **NOT in PROJ-283 scope** — flagged for later cleanup. Always verify with `python -m pytest <specific_file>` directly if you're adding tests anywhere near `test_race_config.py`.

2. **Import cycle shape**: `habitability_factors.py` imports `_gaussian_factor` from `habitability.py`. `habitability.py` uses `TYPE_CHECKING` for `RaceConfig`, so no cycle. When you add `calculate_habitability_v2` to `habitability.py`, importing `FACTOR_REGISTRY` from `habitability_factors.py` **would** create a cycle. Two options: (a) move `_gaussian_factor` to a shared helper module, or (b) lazy-import `FACTOR_REGISTRY` inside `calculate_habitability_v2`. Option (b) is lighter and matches the TYPE_CHECKING pattern already in use. Recommend (b).

3. **Radiation extractor caveat**: Phase 1 made the radiation factor read `planet.radiation_shielding` — Planet has no ambient-radiation field. Defaults are setpoint=0 tolerance=50 so a race "doesn't care by default." If Phase 2 parity tests fail because the old formula used `magnetic_field + radiation_shielding` together (so an unshielded planet with strong magnetic field scored WELL on radiation), you may need to retune radiation weight down or widen the default tolerance. Record the tuning rationale in `decisions.md`.

4. **Weight parity with v1**: v1 weights are `gravity=1.0, temperature=1.0, water=0.8, atmosphere=0.7, radiation=0.6` (in habitability.py `FACTOR_WEIGHTS`). v2 splits atmosphere into 10 gases (bucket 1.5), adds pressure=0.9, tectonic=0.4, magnetic=0.6, and radiation=0.6 retained. Total v1 weight = 4.1; total v2 weight = 1.0+1.0+0.8+0.9+0.4+0.6+0.6+1.5 = 6.8. Because the combiner is a weighted *geometric* mean, the absolute weight magnitudes don't matter — only the *ratios* matter, so drift-direction matters more than drift-magnitude. A near-ideal planet should still produce habitability ≈ 0.9 under v2.

5. **Gas-missing = 0 Pa semantics**: gas extractors return `0.0` (not `None`) for absent gases. Scorer also coerces `None` to `0.0`. This means a race with `setpoint=0 tolerance=wide` scores near 1.0 on any planet — that's the "don't care" default. A race with `setpoint > 0` (e.g., the default O2 setpoint of 21 kPa) scores low on a planet without that gas. Keep this in mind when writing parity tests — v1's atmosphere scorer computed contributions per gas present, so v1 would rate a pure-CO2 planet identically for an O2-lover and a CO2-lover (both get some "recognized gas weight"), while v2 correctly penalizes the O2-lover more harshly.

## Protocol
Follow `Projects/protocols/03a_continue_working.md`. Check context at natural handoff points via `python Tools/check_context/check_context.py`. Run `python Projects/scripts/validate_phase.py PROJ-283 2` before stopping.
