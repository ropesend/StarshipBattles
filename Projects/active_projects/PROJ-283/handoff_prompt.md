# Handoff: PROJ-283 — Phase 4 (Switch callers + delete legacy fields)

Resume **PROJ-283** at **Phase 4**. The previous session ended after Phase 3 closed cleanly (validator PASS, 0 errors / 0 warnings; full sharded suite 14797/14798 — sole failure is the same pre-existing flaky quickstart test from prior sessions). Stopping at the phase boundary preserves a full-cache start for Phase 4, which the plan explicitly flags as **the riskiest phase**: "one commit that removes the parallel fields and rewires every caller."

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. The project plan assumes you understand the surrounding architecture, conventions, and related code — if you don't, you'll make short-sighted decisions that the plan's author took for granted. Prefer loading extra context.

### 1. Foundation docs (always read these first)
- `docs/README.md` — doc index + task-driven reading order
- `docs/01_ARCHITECTURE.md` — layer structure + package APIs + dependency rules
- `docs/02_PATTERNS.md` — design patterns used in this codebase
- `docs/03_CONVENTIONS.md` — naming, file org, test conventions, line budgets
- `CLAUDE.md` — three non-negotiable rules (TDD, docs-in-sync, clean-sheet design) + System Migration Policy ("eradicate the old completely, no fallbacks, no backward-compat shims")

### 2. Task-specific docs
- `docs/systems/strategy_layer.md` — strategy-layer architecture; population engine + race system sections
- `docs/04_SERVICES.md` — service registration; will need to be updated in Phase 6 (not Phase 4) to reflect the registry-driven habitability + budget API

### 3. Related code (read for context, even if you won't modify it)

**Phase 1-3 outputs (these define the contract Phase 4 migrates TO):**
- `game/strategy/data/environmental_preference.py` — `EnvironmentalPreference(setpoint, tolerance, min_value, max_value, step)` self-validates on construction; `to_dict`/`from_dict` JSON-tolerant
- `game/strategy/data/habitability_factors.py` — `FACTOR_REGISTRY`, `get_factor(id)`, `iter_scalar_factors()`, `iter_gas_factors()`. **Read `_default_gaussian_scorer` docstring** — encodes the None/0.0 → "infinite deviation" contract
- `game/strategy/data/race_config.py` — `RaceConfig.preferences: Dict[str, EnvironmentalPreference]` populated from registry defaults via `__post_init__`. `base_reproduction_rate: float = 0.03`. `base_happiness: float = 0.5`. **Legacy fields still present** (`gravity_ideal`, `gravity_tolerance`, `temperature_ideal`, `temperature_tolerance`, `water_ideal`, `water_tolerance`, `atmosphere_preferences`, `radiation_tolerance`, `aptitude_population_growth`, `aptitude_happiness`) — these are what Phase 4 deletes
- `game/strategy/data/race_point_budget.py` — Phase 3 rewrite. `RacePointBudget` class methods: `calculate_aptitude_cost`, `calculate_preferences_cost`, `calculate_reproduction_cost(rate)`, `calculate_total_cost`, `get_remaining_points`, `get_aptitude_breakdown`, `get_breakdown`. Legacy `calculate_tolerance_cost` and `get_tolerance_breakdown` are gone. `aptitude_happiness`/`aptitude_population_growth` are excluded from cost (but the FIELDS still exist on `RaceConfig` until Phase 4 removes them)
- `game/strategy/formulas/habitability.py` — both v1 (`calculate_habitability` + 5 factor functions + `score_planet_for_race`) and v2 (`calculate_habitability_v2`) live in parallel. **Phase 4 Task 4.1 promotes v2 to canonical and deletes v1.** Lazy imports `FACTOR_REGISTRY` inside `calculate_habitability_v2` to break the otherwise-circular import.

**Phase 4 modification targets (read before editing):**
- `game/strategy/engine/population_engine.py` — line 112 reads `race_config.aptitude_population_growth` via `_aptitude_to_growth_rate`. Phase 4 Task 4.3 deletes the helper and switches to `race_config.base_reproduction_rate`. **Do NOT change the logistic formula** (that's PROJ-284's job)
- `game/strategy/engine/superweapon_order_processor.py` — `process_create_dyson_sphere` (around lines 595-605) iterates `race.atmosphere_preferences` and uses `GAS_NAME_TO_FORMULA` to translate display names → chemical formulas. Phase 4 Task 4.4 replaces this with iteration over `race.preferences` filtered to `factor_id.startswith("gas.")` with `setpoint > 0` (formulas are already the dict suffix, no translation needed)
- `game/ui/panels/race_summary_panel.py` (line 432) — displays `rc.aptitude_happiness` + `rc.aptitude_population_growth`. Phase 4 should switch to `rc.base_happiness` + `rc.base_reproduction_rate` to keep UI usable between Phase 4 and Phase 5
- `game/ui/screens/empire_panel_window.py` (lines 358-359) and `game/ui/screens/race_validator.py` (lines 82-83) — same legacy-aptitude display pattern. Same migration

**Helper modules that Phase 4 may need:**
- `game/core/json_utils.py` — `load_json`/`save_json` used by `RaceConfig.save`/`load`. Save format will change once `to_dict` drops legacy keys
- `game/strategy/systems/race_library.py` and `race_randomizer.py` — likely callers of legacy fields; grep them

### 4. Related tests (read so you know what "working" looks like)
- `tests/unit/strategy/data/test_environmental_preference.py` — 12 tests, demonstrates construction + validation + round-trip
- `tests/unit/strategy/data/test_habitability_factors.py` — 39 tests, demonstrates registry-iteration patterns
- `tests/unit/strategy/data/test_race_config.py` — preference-related tests (Phase 1) still pass; **the 16-test `TestRaceConfigValidation` cluster fails for an unrelated pre-existing tuple-unpacking bug** (see Watchout #1 below). Phase 4's `to_dict`/`from_dict` deletions will further break tests that round-trip the legacy keys — those need migrating
- `tests/unit/strategy/data/test_race_point_budget_v2.py` — 46 tests, the canonical budget API tests
- `tests/unit/strategy/formulas/test_habitability_v2.py` — 21 tests for v2 habitability. After Phase 4 Task 4.1 renames v2 → canonical, this file's tests should pass against the canonical name (or the file gets renamed too)
- `tests/unit/strategy/formulas/test_habitability.py` — v1 tests. **Many of these break in Phase 4 Task 4.1** when v1 is deleted. Strategy: move per-factor regression coverage into `test_habitability_factors.py`'s `TestScorer` class (already exists) or `test_habitability_v2.py`; delete tests that just exercise the v1 entry-point signature
- `tests/unit/strategy/engine/test_population_engine.py` — uses `aptitude_population_growth` to seed test races; Phase 4 Task 4.3 migrates these to `base_reproduction_rate`
- `tests/unit/strategy/engine/test_superweapon_order_processor.py` and `tests/integration/strategy/test_superweapon_integration.py::TestCreateDysonSphere` — Dyson Sphere fixtures use `race.atmosphere_preferences`; migrate to `race.preferences`

## Only now: read the project files
Read in this order — the plan depends on all of the above:
1. `Projects/active_projects/PROJ-283/design.md` — architectural rationale (initial analysis + swarm findings)
2. `Projects/active_projects/PROJ-283/decisions.md` — full decision log including 4 Phase 2 + 5 Phase 3 entries
3. `Projects/active_projects/PROJ-283/plan.md` § **Current State** — authoritative handoff (updated end of Phase 3)
4. `Projects/active_projects/PROJ-283/phase_4_checklist.md` — Phase 4 task list (8 tasks)
5. `Projects/active_projects/PROJ-283/manifest.md` — file manifest with Phase 1/2/3 ✓ markers

## First action
Open `phase_4_checklist.md`. The literal next unchecked item is:

> **Task 4.1: Promote v2 habitability to the canonical name [Simple]**
> - [ ] Delete the legacy `calculate_habitability`, `calculate_atmosphere_factor`, `calculate_gravity_factor`, `calculate_temperature_factor`, `calculate_water_factor`, `calculate_radiation_factor`.
> - [ ] Rename `calculate_habitability_v2` to `calculate_habitability`.
> - [ ] `score_planet_for_race(planet, race_config)` stays as the public entry; updates to call the new function.
> - [ ] Update any tests that imported the deleted per-factor functions (move them into the registry module if still useful).

Recommended TDD order: rename `calculate_habitability_v2` → `calculate_habitability` first (with v1 still present so old tests stay green during the rename), then delete v1 (will break v1 tests), then surgically migrate v1 tests to the new function or delete them as obsolete. Per System Migration Policy: do NOT keep parallel implementations.

## Watchouts (from Phases 1-3)

1. **Pre-existing test collection bug**: `tests/` full-collection aborts with a collection error in `tests/unit/strategy/engine/test_build_order_command_handler.py`, which **silently skips** `tests/unit/strategy/data/test_race_config.py` and several sibling files. This hides 16 pre-existing `TestRaceConfigValidation` failures where the tests unpack `config.validate()` as a tuple but it returns `ValidationResult`. **NOT in PROJ-283 scope.** When Phase 4 deletes legacy `RaceConfig` fields, expect MORE tests to fail in this file (the `_validate_environment_ranges` table currently lists those fields). Verify your test changes by running `python -m pytest tests/unit/strategy/data/test_race_config.py -n 0` directly — sharded runs hide the failures.

2. **Pre-existing flaky quickstart test**: `tests/unit/quickstart/test_quickstart_builder.py::TestQuickstartBuilderDesignCopying::test_copy_designs_without_themes_preserves_original` consistently fails with "Klingons vs Federation" theme leak. Has nothing to do with PROJ-283 (no `RaceConfig` or habitability code in the call path). Persistently identified in Phase 1, 2, and 3 handoffs. Treat as known noise: full sharded baseline is 14797/14798.

3. **`GAS_NAME_TO_FORMULA` / `GAS_FORMULA_TO_NAME` constants**: keep these in `race_config.py` for now even though Task 4.4 says the Dyson Sphere seeder no longer needs them. The new factor extractors in `habitability_factors.py` ALSO read planet atmosphere by formula (`O2`, `N2`), and v1 atmosphere helpers used `GAS_FORMULA_TO_NAME` for display-name → formula translation. Once v1 is deleted (Task 4.1) and the Dyson Sphere seeder is migrated (Task 4.4), grep for remaining callers of these dicts before deleting them. UI panels likely use them for display — if so, defer their deletion to Phase 5 (UI rebuild).

4. **`test_habitability.py` (v1 tests) deletion strategy**: when Phase 4 Task 4.1 deletes the v1 functions, the per-factor + integration tests break. Two valid migration patterns:
   - Move per-factor regression tests into `test_habitability_factors.py::TestScorer` (already covers per-factor scorer behaviour with `EnvironmentalPreference`)
   - Move overall-habitability regression tests into `test_habitability_v2.py` (rename to `test_habitability.py` after Task 4.1's rename) — most are already covered by `TestCalculateHabitabilityV2HappyPath` etc.
   Do NOT delete tests blindly. The v1 tests encoded valuable regression cases (e.g. extreme gravity scenarios). Find the equivalent v2 test or write one.

5. **`RaceConfig.__post_init__` backfill behavior** is critical: when Phase 4 deletes `atmosphere_preferences`, the `__post_init__` block that defaults it (lines 172-178) must also go. The block that backfills `preferences` from `FACTOR_REGISTRY` (lines 180-193) must STAY — that's the new contract. Read `__post_init__` end-to-end before editing.

6. **Reproduction-rate refund math (Phase 3 design choice)**: Phase 3 chose linear-in-rate (not integer-step) refund for the 0.5% floor case. Don't second-guess this. The plan's pseudocode used integer steps but Python's `round(-2.5) == -2` (banker's rounding) breaks the table — see decisions.md (2026-04-18 Phase 3 entry).

7. **Save-game policy**: per CLAUDE.md and decisions.md, save files are disposable. Don't write migration code for `RaceConfig.from_dict` — just remove the legacy keys from the parsing. Old save files won't load; that's the documented stance.

8. **Task 4.7 `make_test_race` helper — implement EARLY**: this dramatically reduces churn in Phase 4-6 test migrations. The plan lists 4.7 after 4.2-4.5 but the actual ergonomic order is helper-first. Recommend doing 4.7 immediately after 4.1, before 4.2 deletes the fields, so subsequent test edits use the helper from the start.

9. **Class vs module functions for `RacePointBudget`**: Phase 3 kept `RacePointBudget` as a class (5 UI files instantiate it). Don't refactor to module functions in Phase 4 — UI rebuild happens in Phase 5; if that phase wants module functions, do it then. See decisions.md (2026-04-18 Phase 3 entry).

10. **Two new `RaceConfig` fields shipped in Phase 1**: `base_reproduction_rate: float = 0.03` and `base_happiness: float = 0.5`. The UI migration for happiness is "display `rc.base_happiness` instead of `rc.aptitude_happiness`" — same display contract, different source.

## Protocol
Follow `Projects/protocols/03a_continue_working.md`. Check context at natural handoff points via `python Projects/scripts/check_context.py`. Run `python Projects/scripts/validate_phase.py PROJ-283 4` before stopping. Phase 4 is large (8 tasks across data model + 2 engines + UI labels + tests); plan to stop at task boundaries if context approaches threshold.
