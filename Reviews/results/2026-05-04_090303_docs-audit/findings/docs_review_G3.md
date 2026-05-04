# Documentation Review: How-To Guides
## Summary
- Group: How-To Guides
- Docs in Scope: 9
- Docs Actually Read: 9
- Total Findings: 11
- Critical: 2 | Major: 5 | Minor: 4

## Dead Reference Findings

### 1. CRITICAL — `adding_modifiers.md` Step 6 references nonexistent test file
- **File:** `docs/guides/adding_modifiers.md:166`
- **Referenced path:** `tests/regression/test_modifier_ability_snapshots.py`
- **Status:** File does not exist. The test was split from a single file into a package at commit `472d062e0` (PROJ-48 Phase 3 Task 3.2).
- **Actual location:** `tests/regression/modifier_ability_snapshots/` (package with `conftest.py`, `test_utility_modifiers.py`, `test_weapon_modifiers.py`)
- **Severity:** CRITICAL — guide instructs users to add tests to a file that no longer exists.

### 2. CRITICAL — `adding_abilities.md` Step 2 references nonexistent module `movement.py`
- **File:** `docs/guides/adding_abilities.md:136`
- **Code example:** `from .movement import ThrusterAbility`
- **Status:** `movement.py` does not exist in `game/simulation/components/abilities/`. The directory contains `propulsion.py` (which holds `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `WarpJump`), `markers.py`, `weapons.py`, etc. — but no `movement.py`.
- **Severity:** CRITICAL — code example uses a nonexistent module import. A developer following this guide would get `ModuleNotFoundError`.

## Stale PROJ Reference Findings

### 3. MAJOR — `component_system.md` PROJ-237/238 status ambiguous
- **File:** `docs/guides/component_system.md:63-64, 93`
- **Context:** Lines 63-64 show `StrategicResourceGeneration (PROJ-238: per-turn generation for strategy layer)` and `PlanetaryShieldAbility (PROJ-237: planetary shield, strategy marker)` in the ability hierarchy. Section "Strategic-Layer Abilities (PROJ-237/238)" on line 93 describes these as current features.
- **Status:** Both PROJ-237 and PROJ-238 are completed and archived (in `Projects/deep_archive/` per `deep_archive_index.md:238-239`). The doc correctly treats them as completed/current features — no stale "planned" language.
- **Verdict:** References are **accurate** — PROJ-237/238 are correctly described as implemented features, not as in-progress work. The PROJ labels serve as historical provenance. No change needed.

## Content Accuracy Findings

### 4. MAJOR — `adding_modifiers.md` "Last verified" date is stale (2026-03-14)
- **File:** `docs/guides/adding_modifiers.md:3`
- **Current date:** `2026-03-14`
- **Issue:** The test file referenced in Step 6 was refactored after this date. The doc was last touched at commit `0ae2e8aa8` (PROJ-307 backfill) which only added the timestamp without verifying content accuracy.
- **Severity:** MAJOR — the verification date implies the content was reviewed but a CRITICAL dead-reference exists within the same doc.

## Code Example Issues

### 5. CRITICAL — Already documented in Dead Reference #2 (`movement.py` import)

### 6. MAJOR — `adding_abilities.md` Integration test example references `Component` import that is technically valid but code pattern is misleading
- **File:** `docs/guides/adding_abilities.md:422`
- **Import:** `from game.simulation.components.component import Component`
- **Status:** The import path is valid (`Component` exists at `game/simulation/components/component.py:81`). However, the test passes `registries=provider` to `Component()` which is the correct keyword argument name per `Component.__init__()`.
- **Verdict:** Code works as written. No issue.

## Missing Documentation

### 7. MAJOR — No guide exists for the Replay System
- **Production files:** `game/simulation/replay/` (8 files: `replay_serialization.py`, `replay_spec.py`, `replay_player.py`, `replay_capture.py`, `replay_outcome.py`, `replay_record.py`) + `game/strategy/services/replay_store.py` + `game/strategy/services/replay_resolver.py`
- **Gap:** Adding replay support for new abilities, debugging replay issues, or understanding the replay capture/playback lifecycle has no guide. The replay system is a cross-cutting concern that touches simulation and strategy layers.
- **Severity:** MAJOR — common developer task with no documentation.

### 8. MAJOR — No guide exists for Strategy Session Facade
- **Production file:** `game/strategy/facade/strategy_session_facade.py`
- **Gap:** The facade is the primary API surface for the strategy layer. Extending strategy features, adding new facade methods, or understanding the facade's relationship to the underlying engine has no guide. The `component_system.md` mentions the `StrategySessionFacade` contract guard (via PROJ-326) but gives no guidance on its use or extension.
- **Severity:** MAJOR — extending the strategy layer requires understanding this API.

### 9. MINOR — No guide for `battle_ui_service.py` (299 LOC)
- **Production file:** `game/ui/services/battle_ui_service.py`
- **Gap:** Renders battle UI elements (health bars, targeting indicators, etc.). Understanding this service is needed for modifying battle UI behavior but it is considered internal plumbing.
- **Severity:** MINOR — specialized UI service, not a common extension point.

### 10. MINOR — No guide for `input_mapper.py` (380 LOC)
- **Production file:** `game/ui/services/input_mapper.py`
- **Gap:** Maps raw input events to game commands. Modifying input bindings or adding new input handlers requires understanding this.
- **Severity:** MINOR — internal input plumbing, though 380 LOC suggests non-trivial complexity.

### 11. MINOR — No guide for `strategy_renderer.py`
- **Production file:** `game/ui/screens/strategy_renderer.py`
- **Gap:** Renders the strategy map. Adding new visual elements to the strategy layer requires understanding this.
- **Severity:** MINOR — rendering code is generally self-documenting through visual patterns.

## "Last Verified" Coverage

| Doc File | Has "Last verified"? | Date | Status |
|----------|----------------------|------|--------|
| `adding_abilities.md` | Yes | 2026-04-28 | OK |
| `adding_modifiers.md` | Yes | 2026-03-14 | **STALE** — predates test file refactor |
| `component_system.md` | Yes | 2026-04-28 | OK |
| `modifier_system.md` | Yes | 2026-04-13 | OK (184 days before audit) |
| `performance_profiling.md` | **MISSING** | — | **MINOR** — no verification date |
| `pre_commit_hooks.md` | **MISSING** | — | **MINOR** — no verification date |
| `qs_complex_design.md` | Yes | 2026-04-11 | OK |
| `simulation_testing.md` | Yes | 2026-04-18 | OK |
| `testing_infrastructure.md` | Yes | 2026-05-02 | OK |

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `adding_abilities.md` (565 LOC) | 1 CRITICAL | Step 2 import: `from .movement import ThrusterAbility` — `movement.py` does not exist; should be `from .propulsion import ThrusterAbility` (or a correctly-named module). All other code examples, class references, and file paths validated clean. |
| `adding_modifiers.md` (229 LOC) | 1 CRITICAL, 1 MAJOR | Step 6 test path `tests/regression/test_modifier_ability_snapshots.py` is dead — tests live at `tests/regression/modifier_ability_snapshots/` (package). "Last verified" date (2026-03-14) is stale. |
| `component_system.md` (353 LOC) | Clean | All referenced classes, files, and imports verified. Ability hierarchy accurate. `VehicleLaunchAbility` exists at `markers.py:9`. `StaticValueAbility` exists at `base.py:428`. |
| `modifier_system.md` (533 LOC) | Clean | All API references (`ModifierEffectEvaluator`, `ModifierIntrospection`, `ModifierService`, `Modifier` dataclass) verified against live code at expected paths. File location table accurate. |
| `performance_profiling.md` (99 LOC) | 1 MINOR | Missing "Last verified" line. Tool references (`Tools/profiling/run_scalene.py`, `Tools/profiling/workflows/profile-pass-template.md`) all valid. |
| `pre_commit_hooks.md` (74 LOC) | 1 MINOR | Missing "Last verified" line. Tool reference (`Tools/lint_test_files.py`) valid. PROJ-326 (now Complete) accurately referenced as origin. |
| `qs_complex_design.md` (293 LOC) | Clean | All file paths (`game/strategy/quickstart_builder.py`, `data/designs/`, `game/strategy/data/planetary_facility.py`, etc.) verified. `INITIAL_COMPLEXES` list accurate. |
| `simulation_testing.md` (914 LOC) | Clean | All file paths, class references (`TestScenario`, `TestMetadata`, `ABBattleOutcome`, `CombatLabTelemetry`, `build_test_battle_spec`, `ABBattleRunner`), and import paths verified against live code. `tests/unit/combat_lab/test_scenario_roles_consistency.py` exists. |
| `testing_infrastructure.md` (258 LOC) | Clean | All fixture names, file paths, and pytest markers verified. `SessionRegistryCache`, `reset_game_state`, `enforce_headless` all exist in root `conftest.py`. Test fixture files at expected paths. |

## Recommendations

1. **CRITICAL — Fix `adding_modifiers.md` Step 6**: Update test file path from `tests/regression/test_modifier_ability_snapshots.py` to `tests/regression/modifier_ability_snapshots/` (package). Provide an example referencing one of the actual test files (e.g., `tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py`).

2. **CRITICAL — Fix `adding_abilities.md` Step 2 import**: Change `from .movement import ThrusterAbility` to `from .propulsion import ThrusterAbility` (or whichever module the ability author chooses). The `movement.py` module does not exist.

3. **MAJOR — Create a Replay System guide**: Document the replay capture/playback lifecycle, how to add replay support for new abilities, and the relationship between `game/simulation/replay/` and `game/strategy/services/replay_*.py`.

4. **MAJOR — Create a Strategy Facade guide**: Document `strategy_session_facade.py` — its role as the strategy layer API, how to extend it, facada patterns, and relationship to the underlying strategy engine.

5. **MAJOR — Re-verify `adding_modifiers.md`**: After fixing the test file path, update the "Last verified" date.

6. **MINOR — Add "Last verified" lines to `performance_profiling.md` and `pre_commit_hooks.md`**: Both are missing the verification metadata that other guide docs carry.

7. **MINOR — Consider guides for `battle_ui_service.py`, `input_mapper.py`, and `strategy_renderer.py`**: These are lower-priority extension points but at 299, 380, and significant LOC respectively, they represent non-trivial code surfaces currently undocumented in the How-To section.
