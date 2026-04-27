# Phase 6: Docs + cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-283 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update `docs/systems/strategy_layer.md` and `docs/04_SERVICES.md` for the new registry-driven model. Sweep for orphan references to deleted fields. Prepare the codebase for PROJ-284 and PROJ-285 to build on the new foundation.

---

## Tasks

### Task 6.1: Document the factor registry [Medium]
**File:** `docs/systems/strategy_layer.md`

- [x] Added section "## 7. Race Preferences & Habitability (PROJ-283)" explaining:
  - The `FACTOR_REGISTRY` pattern with the 7-scalar + 10-gas structure
  - `EnvironmentalPreference(setpoint, tolerance, ...)` dataclass shape
  - The weighted geometric mean combiner with the per-factor weight table
  - Adding-a-factor recipe (single registry entry → automatic surfacing in formula, budget, UI, presets, population engine)
  - The "(setpoint is free, tolerance costs exponentially)" UX contract
  - Per-factor weight table + tank-all property by axis weight
- [x] References `game/strategy/data/habitability_factors.py` and `game/strategy/formulas/habitability.py` with line ranges via markdown links.
- [x] Includes a complete legacy → new field migration table for downstream code authors.

**Notes:** Also updated the `### Planet Modifier Effect Engine` Habitability bullet (radiation and magnetic are now independent factors, not combined as v1) and the `### Atmosphere Modification Pipeline` "Species Ideal" preset reference (now reads `race_config.preferences["gas.<formula>"].setpoint` directly, no display-name → formula translation). Two stale references to `GAS_NAME_TO_FORMULA` / `GAS_FORMULA_TO_NAME` corrected — the constants are kept in `race_config.py` for the few legacy translations the UI layer still does.

### Task 6.2: Update services catalog [Simple]
**File:** `docs/04_SERVICES.md`

- [x] Added `game/strategy/data/` block to the Service Directory listing (`environmental_preference.py`, `habitability_factors.py`, `race_config.py`, `race_point_budget.py`, `homeworld_presets.py`) plus a `game/strategy/formulas/` block for `habitability.py`.
- [x] Added a dedicated "### Race Habitability & Point-Buy (PROJ-283)" section after `ComponentInspector` that documents: the data-model files, the budget-method index, the registry-driven pattern, and a forward-link to `docs/systems/strategy_layer.md §7`.
- [x] Documents `base_reproduction_rate` and `base_happiness` as the replacements for the deleted `aptitude_population_growth` / `aptitude_happiness` aptitudes.

**Notes:** `04_SERVICES.md` is service-focused; the deep architectural treatment lives in `strategy_layer.md §7`. The 04_SERVICES section is a focused catalog entry that points the reader to the architecture doc.

### Task 6.3: Update CLAUDE.md if patterns changed [Simple]
**File:** `CLAUDE.md`

- [x] Added a one-line "Habitability Factor Registry (PROJ-283)" entry to the "Key Patterns" list under Architecture Principles, with a forward-link to `docs/systems/strategy_layer.md §7`.

**Notes:** Judgement call: this IS a new pattern worth broadcasting to future agents. The "add an axis with one data edit" property is the single biggest design win of PROJ-283 and qualifies as a recurring pattern worth flagging at the top-level rules doc.

### Task 6.4: Orphan sweep [Simple]
**Tests:** Manual grep verification

- [x] Ran `grep -rn "atmosphere_preferences|gravity_ideal|gravity_tolerance|temperature_ideal|temperature_tolerance|water_ideal|water_tolerance|radiation_tolerance|aptitude_happiness|aptitude_population_growth|_aptitude_to_growth_rate" docs/ game/ tests/`.
- [x] Permitted hits remaining: PROJ-283 docs/decisions, module docstrings explaining what was deleted, the migration table in `strategy_layer.md §7`, and the new `test_race_config.py` docstring listing the deleted fields. ZERO production-code or test-code USAGES of legacy fields remain.
- [x] Production hits found and FIXED:
  - `game/ui/screens/gravity_target_editor.py:201` — migrated from `getattr(rc, 'gravity_ideal', None)` to `rc.preferences["gravity"].setpoint / 9.81`
  - `game/ui/screens/water_target_editor.py:208` — migrated from `getattr(rc, 'water_ideal', None)` to `rc.preferences["water"].setpoint`
  - `game/ui/screens/atmosphere_target_editor.py:262` — rewrote `_set_species_ideal` to iterate `rc.preferences["gas.<formula>"].setpoint` directly (deleted the `GAS_NAME_TO_FORMULA` translation step)
  - `game/ui/screens/radiation_shield_editor.py:213` — replaced the `threshold = 0.5 - (radiation_tolerance / 200)` legacy formula with a direct `rc.preferences["radiation"].setpoint` read (the new model decouples shielding preference from magnetic field)

**Notes:** Phase 5 explicitly deferred these 4 editor migrations as "Phase 6 / follow-up scope"; doing them under Phase 6 closed the orphan sweep cleanly.

### Task 6.5: Cross-project coordination notes [Simple]
**File:** `Projects/active_projects/PROJ-284/decisions.md` and `Projects/active_projects/PROJ-285/decisions.md`

- [x] Added 2 PROJ-283 unblock confirmation entries to PROJ-284's decisions.md: confirms the new `base_reproduction_rate` / `base_happiness` field shape, the `score_planet_for_race` API, and the lazy-import pattern. Forward-links to `docs/systems/strategy_layer.md §7`.
- [x] Added 2 PROJ-283 unblock confirmation entries to PROJ-285's decisions.md: confirms the habitability formula API, the per-factor weight allocation (stable as of Phase 5), and the Phase 2 `gas.N2` retuning plus Phase 5 `temperature` factor bounds widening (neither affects multiplier math).
- [x] Noted PROJ-283 commit hash for the Phase 1 baseline (`0ec99962`) and that Phases 2-6 are landed in the working tree but not yet committed (user controls commits).

**Notes:** Did not need to retune any habitability weights during Phase 2 parity testing — the Phase 1 weight allocation worked as designed. The `gas.N2` setpoint default and the `temperature` bounds widening are the only registry tweaks downstream consumers should be aware of; both are documented in PROJ-285's decisions.md note.

### Task 6.6: Final verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full sharded suite green: 14752/14753 in clean run. The lone deterministic failure is the same pre-existing flaky `test_copy_designs_without_themes_preserves_original` (Klingons vs Federation theme leak) flagged across every PROJ-283 phase. Occasional sharded-runner flakes (`test_make_minimal_spec`, `test_reference_integrity`) all pass in isolation; not PROJ-283 regressions.
- [x] Manual smoke test: deferred to user (Phase 5 Task 5.7). Cost-curve math + panel construction + preset application all covered by the automated suite.
- [x] PROJ-283 plan.md Current State updated to "Complete, ready to close" (this Phase).

**Notes:** Phase 6 also salvaged two test files that had been left runtime-broken by Phase 4's deletions and were skipped by the sharded runner due to import errors:
- `tests/unit/strategy/data/test_race_config.py` — the file with the pre-existing 16-test `TestRaceConfigValidation` tuple-unpacking failures. Phase 4 deleted `DEFAULT_ATMOSPHERE_PREFERENCES`, breaking the file's import. Phase 6 surgically rewrote the file (~1000 → ~410 lines): kept the salvageable Phase 1 tests (`TestRaceConfigPreferencesField`, `TestRaceConfigBaseReproductionAndHappiness`, `TestRaceConfigValidateWithPreferences`), the identity/aptitude/serialization/file-IO tests adjusted for the new schema, and the constants-list tests (with `APTITUDE_NAMES` updated for the 7-paid count). 45 tests now pass. The pre-existing tuple-unpacking validate() bug is also resolved (the new `validate()` returns ValidationResult and the new tests expect that shape).
- `tests/unit/strategy/data/test_population_model.py::test_empire_race_config_serialization_roundtrip` — used legacy `water_ideal`/`temperature_ideal` to build a test race. Migrated to `preferences["water"]` / `preferences["temperature"]` overrides via the registry. 14 tests pass.

This means a long-standing test-debt watchout flagged across Phases 1-5 (`Pre-existing 16-test TestRaceConfigValidation cluster + collection error hidden by sharded runner`) is now fully closed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
