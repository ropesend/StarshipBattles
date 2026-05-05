# Shard 13 — Test Coverage Audit Findings

**Audit date:** 2026-05-04
**Files in scope:** 47 production files (~9057 LOC)
**Matrix source:** `Reviews/results/2026-05-04_205404_testcoverage-audit/raw/coverage_matrix.json`

---

## Summary

| Severity | Count | Description |
|----------|-------|-------------|
| **CRITICAL** | 4 | Tier 0 non-UI files with zero tests |
| **MAJOR** | 3 | Tier 1/2 gaps in non-UI core logic (untested error paths, key methods) |
| **MINOR** | 18 | Tier 2 partial coverage — untested private helpers, dunders, edge branches |
| **ADVISORY** | 10 | Tier 0 UI/rendering + `__init__.py` files with zero tests |
| **Tier 3 (Verified)** | 12 | Files with apparent full coverage confirmed |

---

## CRITICAL — Tier 0 Non-UI Files (Zero Tests)

### 1. `game/core/protocols/boundary.py` (126 LOC, 0/23 symbols tested)
**Layer:** Core — Protocols for Strategy ↔ Simulation boundary
**Why CRITICAL:** This is the contract surface between two layers. Protocol compliance failures silently corrupt type narrowing across the layer boundary. `IResourceReader`, `IPostBattleShip`, and `IResourceHolder` are used by ShipInstance bridge methods (`to_ship`/`update_from_ship`) and the fleet post-battle hook — all of which are downstream from these contracts.
- **Untested symbols (all 23):**
  - `IResourceReader` protocol + `get_value`, `get_max_value`, `get_resource_names`
  - `IPostBattleShip` protocol + `instance_id`, `name`, `hp`, `max_hp`, `is_alive`, `is_derelict`, `layers`, `resources` properties
  - `IResourceHolder` protocol + `resources`, `hp`, `max_hp`, `is_alive`, `is_derelict`, `layers`
  - TypeGuards: `is_post_battle_ship`, `is_resource_reader`, `is_resource_holder`
- **Candidate test files:** None listed in matrix
- **Remediation:** Write `tests/unit/core/protocols/test_boundary.py` covering: (a) each TypeGuard returns True for compliant objects, False for non-compliant; (b) `isinstance(obj, IPostBattleShip)` check with `@runtime_checkable`; (c) a test mock implementing IPostBattleShip that the TypeGuard accepts.

### 2. `game/services/llm/defaults.py` (42 LOC, 0/2 symbols tested)
**Layer:** Services — Module-level default LLM provider slot
**Why CRITICAL:** This is production wiring. If `get_default_llm_provider()` returns a stale or incorrect instance, the LLM features (race description, diplomacy) silently break. The `global` mutation in `set_default_llm_provider` is a known sharp edge.
- **Untested symbols:** `get_default_llm_provider`, `set_default_llm_provider`
- **Candidate test files:** None
- **Remediation:** Write `tests/unit/services/llm/test_defaults.py`: test that (a) `get_default_llm_provider()` returns None before set, (b) round-trip set/get preserves identity, (c) setting to None works, (d) import isolation — tests don't leak state between each other.

### 3. `game/strategy/engine/handlers/registry_factory.py` (125 LOC, 1/1 symbol)
**Layer:** Strategy — Composes the default command-handler registry
**Why CRITICAL:** This wires 30+ command handlers. A missing import or bad registration key silently drops a command from the strategy turn engine. The file is 100% wiring with zero tests.
- **Untested symbol:** `create_default_registry` (matrix shows 0/1 tested despite function being listed)
- **Candidate test files:** `tests/unit/strategy/engine/handlers/test_registry_factory.py` (not found in matrix)
- **Remediation:** Write a test that calls `create_default_registry()` and asserts: (a) all expected command keys are present, (b) no duplicate registrations, (c) registry's internal handlers dict is non-empty.

### 4. `game/strategy/services/ability_sources/fleet.py` (148 LOC, 0/12 symbols tested)
**Layer:** Strategy — `FleetAbilitySource` implements IAbilitySource for strategic ability projection
**Why CRITICAL:** This is the only fleet-side implementation of the IAbilitySource interface (PROJ-300/305). It feeds into the SystemEffectsCollector which drives the Sector Effects panel and strategic combat modifiers. Untested: memoization cache, scope filtering, hidden-fleet guard, combat-capable gating, and error resilience in `_is_combat_capable`.
- **Untested symbols (all 12):** `FleetAbilitySource` class + all 8 methods/properties + `_is_combat_capable`, `_is_hidden`, `_walk_strategic_abilities`
- **Candidate test files:** None
- **Remediation:** Write `tests/unit/strategy/services/ability_sources/test_fleet.py`: (a) memoization — second call to `get_abilities()` returns cached result, (b) `_is_hidden` fleets return empty dict, (c) non-combat-capable ships excluded, (d) combat-only scopes filtered out, (e) `source_kind`/`source_label`/`source_id` return expected values.

---

## MAJOR — Tier 2 Partial Coverage in Non-UI Code

### 5. `game/simulation/battle_runner.py` (676 LOC, 6/11 symbols tested)
**Layer:** Simulation — Unified battle entry point `run_battle()`
**Severity: MAJOR.** Five private helpers are flagged untested. However, they are exercised *indirectly* through integration tests of `run_battle()`:
- `_attach_telemetry` (L374-412) — Called on L329 within `run_battle`. Tested implicitly by any test with `telemetry_level >= NORMAL`.
- `_build_ship_outcome` (L507-577) — Called within `extract_outcome` (L462). Integration-tested.
- `_apply_spec_components_to_ship` (L580-620) — Called within `materialize_spec_ships` (L135). Integration-tested.
- `_extract_component_states` (L622-643) — Called within `_build_ship_outcome` (L564). Integration-tested.
- `_derive_end_reason` (L646-667) — Called within `extract_outcome` (L480). Integration-tested.
**Gap:** No direct unit tests for the end-reason derivation edge case: when `absolute_max_ticks` fires but the spec also has a `TickLimitCondition` with `max_ticks <= absolute_max_ticks`, the disambiguation logic at L657-664 returns `TICK_LIMIT`. This specific case-path needs a focused test.
**Remediation:** Add a unit test for `_derive_end_reason` exercising all 11 end-condition class types plus the safety-ceiling disambiguation.

### 6. `game/simulation/components/component.py` (406 LOC, 28/35 symbols tested)
**Layer:** Simulation — Main Component class
**Severity: MAJOR.** The untested symbols (`health_manager` property, `mark_hp_cache_dirty`, `hp_ratio` property, `reset_hp`) are all facade delegates to `ComponentHealthManager`. While the health manager itself may be tested, the **facade boundary** is untested — a change to the delegate name or signature breaks the Component facade with no test to catch it.
- `health_manager` (L202-207) — Lazy-inits ComponentHealthManager. Untested: lazy-init path + second access returns same instance.
- `mark_hp_cache_dirty` (L226-232) — Public API wrapper for private `_hp_ratio_dirty`.
- `hp_ratio` (L234-244) — Delegates to health_manager.hp_ratio. Untested as a facade.
- `reset_hp` (L320-322) — Delegates to health_manager.reset_hp(). Untested as a facade.

### 7. `game/simulation/components/component_constants.py` (69 LOC, 5/7 symbols tested)
**Layer:** Simulation — Modifier and ApplicationModifier data classes
**Severity: MAJOR.** `Modifier.__init__` and `ApplicationModifier.__init__` are flagged untested. These are foundational data constructors used throughout the modifier system (ModifierService, ModifierManager, modifier effects). While implicitly tested through integration, zero direct tests mean no validation of:
- `Modifier.__init__` (L31-43): V2 effects format parsing, param min/max/default fallbacks.
- `ApplicationModifier.__init__` (L67-69): value fallback to `mod_def.default_val`.
**Remediation:** Write `tests/unit/simulation/components/test_component_constants.py` covering construction with minimal data, null effects, missing param, and value fallthrough.

---

## MINOR — Tier 2 Partial Coverage (Specific Gaps)

### 8. `game/core/validation.py` (209 LOC, 11/12 symbols tested)
- **Untested:** `ValidationResult.__post_init__` (L91-97)
- **Assessment:** The `__post_init__` guards against `None` passed for `errors`/`warnings` despite `field(default_factory=list)`. In Python 3.14 dataclasses, `default_factory` already handles this. The guard is defensive dead code from an older convention. MINOR.

### 9. `game/simulation/components/abilities/defense.py` (113 LOC, 6/7 symbols tested)
- **Untested:** `ShieldRegeneratingArmor` (L107-113)
- **Assessment:** Simple `StaticValueAbility` subclass with no custom logic (just ui_label/ui_color/ui_format/int_result). MINOR.

### 10. `game/simulation/services/modifier_service.py` (268 LOC, 9/10 symbols tested)
- **Untested:** `_has_arc_set_effect` (L142-155, static method)
- **Assessment:** Low-risk private helper that iterates effects list and checks for 'arc_set' stat. Called by `get_initial_value` and `get_local_min_max`. MINOR.

### 11. `game/simulation/services/registry_loader.py` (137 LOC, 1/2 symbols tested)
- **Untested:** `find_file` (L87-98, inner function within `reload_registries_from_directory`)
- **Assessment:** The `find_file` closure handles test_ prefix fallback and is indirectly tested by caller tests. MINOR.

### 12. `game/strategy/data/fleet_battle_adapter.py` (193 LOC, 3/6 symbols tested)
- **Untested:** `FleetBattleAdapter.__init__`, `_resolve_ship_policies`, `_apply_policy_override`
- **Assessment:** `__init__` is trivial assignment. `_resolve_ship_policies` walks the fleet hierarchy (Fleet→TaskForce→Squadron→Ship) mapping group policy keys — important logic but tested implicitly through `to_battle_ships`. `_apply_policy_override` is a static method mapping CombatPolicy→per-ship IDs. MINOR.

### 13. `game/strategy/data/galaxy_entity_registry.py` (188 LOC, 11/12 symbols tested)
- **Untested:** `GalaxyEntityRegistry._index_planet` (L34-55)
- **Assessment:** Called by `register_planet` and `restore_planet` (both public), so tested indirectly. MINOR.

### 14. `game/strategy/data/race_caption_loader.py` (116 LOC, 4/6 symbols tested)
- **Untested:** `RaceCaptionLoader.__init__`, `RaceCaptionLoader._load`
- **Assessment:** `__init__` is trivial path assignment. `_load` contains the non-trivial logic: file-exists check, JSON decode with sentinel, dict type check, schema_version validation. MINOR but the schema_version check (L106-111) is a test-worthy gate.

### 15. `game/strategy/data/stars.py` (770 LOC, 18/24 symbols tested)
- **Untested:** `StarGenerator._get_image_id`, `_compute_stefan_boltzmann_type`, `_generate_companions`, `generate_from_blueprint`, `_generate_random_stars`, `_generate_mass_constrained`
- **Assessment:** Stars.py is 770 LOC, well over the 500-line ceiling. The untested methods are all private generation helpers in StarGenerator. The large file size and missing tests suggest the StarGenerator should be split into sub-modules with concurrent test coverage. MINOR for now, but approaching the 500-LOC ceiling.

### 16. `game/strategy/data/task_force.py` (142 LOC, 7/10 symbols tested)
- **Untested:** `TaskForce.__init__`, `_formation_to_dict`, `_formation_from_dict`
- **Assessment:** `__init__` delegates to `super().__init__`. The module-level `_formation_to_dict`/`_formation_from_dict` are (de)serialization helpers. MINOR.

### 17. `game/strategy/generation/loaders/galaxy_layouts_loader.py` (182 LOC, 6/7 symbols tested)
- **Untested:** `GalaxyLayoutsLoader._scale_primitive` (L131-162)
- **Assessment:** Static method that applies SCALING_FIELDS/POSITION_FIELDS scaling. Called by `scale_layout_for_radius` which is tested. MINOR.

### 18. `game/strategy/generation/region_classifier.py` (275 LOC, 8/10 symbols tested)
- **Untested:** `RegionClassifier.__init__`, `RegionClassifier._build_regions`
- **Assessment:** `__init__` contains substantial parsing logic (spiral/cluster/bar/ring detection, pitch computations, core threshold pre-calculation). `_build_regions` constructs the regions list. Both exercised through `classify()` and `get_region_neighbors()`. MINOR.

### 19-26. UI files with partial coverage — see File Coverage Verification table below.

---

## Tier 3 Files — Verified Coverage

These files appear fully covered based on the matrix and source review:

| File | LOC | Symbols |
|------|-----|---------|
| `game/ai/interfaces/controllable.py` | 393 | 66/66 — Extensive test coverage across 8 test files |
| `game/core/combat_types.py` | 20 | 1/1 — DamageContext dataclass, used broadly in damage pipeline tests |
| `game/core/config.py` | 207 | 9/9 — All config classes tested across 16 test files |
| `game/research/systems/research_service.py` | 232 | 4/4 — Research mechanics tested |
| `game/services/llm/types.py` | 95 | 5/5 — Frozen DTOs, well-tested |
| `game/simulation/services/vehicle_design_service.py` | 516 | 14/14 — Heavily tested design service |
| `game/strategy/facade/dto/system_dto.py` | 162 | 5/5 — Immutable DTOs with factory methods |
| `game/strategy/interfaces/battle_resolver.py` | 109 | 3/3 — Interface + BattleResult DTO |
| `game/strategy/services/deployment_zone_calculator.py` | 107 | 3/3 — Static position calculators |
| `game/strategy/services/task_group_suggester.py` | 125 | 1/1 — Pure function tested |
| `game/ui/screens/strategy_menu_panel.py` | 103 | 5/5 — UI widget tested |
| `game/ui/services/ship_io_adapter.py` | 100 | 5/6 — ShipIOAdapter mostly covered (`__init__` untested but trivial) |

---

## File Coverage Verification Table

| # | File | LOC | Tier | Read | Symbols | Tested | Gaps |
|---|------|-----|------|------|---------|--------|------|
| 1 | `game/ai/interfaces/controllable.py` | 393 | 3 | ✓ | 66 | 66 | — |
| 2 | `game/core/combat_types.py` | 20 | 3 | ✓ | 1 | 1 | — |
| 3 | `game/core/config.py` | 207 | 3 | ✓ | 9 | 9 | — |
| 4 | `game/core/protocols/boundary.py` | 126 | 0 | ✓ | 23 | 0 | **CRITICAL** — all 23 symbols |
| 5 | `game/core/validation.py` | 209 | 2 | ✓ | 12 | 11 | `ValidationResult.__post_init__` (MINOR) |
| 6 | `game/research/__init__.py` | 8 | 0 | ✓ | 0 | 0 | ADVISORY — docstring only |
| 7 | `game/research/systems/research_service.py` | 232 | 3 | ✓ | 4 | 4 | — |
| 8 | `game/services/llm/defaults.py` | 42 | 0 | ✓ | 2 | 0 | **CRITICAL** — `get/set_default_llm_provider` |
| 9 | `game/services/llm/types.py` | 95 | 3 | ✓ | 5 | 5 | — |
| 10 | `game/simulation/battle_runner.py` | 676 | 2 | ✓ | 11 | 6 | **MAJOR** — 5 private helpers (indirectly tested) |
| 11 | `game/simulation/components/abilities/defense.py` | 113 | 2 | ✓ | 7 | 6 | `ShieldRegeneratingArmor` (MINOR) |
| 12 | `game/simulation/components/component.py` | 406 | 2 | ✓ | 35 | 28 | 7 delegate properties (MAJOR — untested facade) |
| 13 | `game/simulation/components/component_constants.py` | 69 | 2 | ✓ | 7 | 5 | 2 `__init__` dunders (MAJOR) |
| 14 | `game/simulation/services/modifier_service.py` | 268 | 2 | ✓ | 10 | 9 | `_has_arc_set_effect` (MINOR) |
| 15 | `game/simulation/services/registry_loader.py` | 137 | 2 | ✓ | 2 | 1 | `find_file` inner function (MINOR) |
| 16 | `game/simulation/services/vehicle_design_service.py` | 516 | 3 | ✓ | 14 | 14 | — |
| 17 | `game/strategy/__init__.py` | 79 | 0 | ✓ | 0 | 0 | ADVISORY — re-exports |
| 18 | `game/strategy/data/fleet_battle_adapter.py` | 193 | 2 | ✓ | 6 | 3 | `__init__`, `_resolve_ship_policies`, `_apply_policy_override` (MINOR) |
| 19 | `game/strategy/data/galaxy_entity_registry.py` | 188 | 2 | ✓ | 12 | 11 | `_index_planet` (MINOR) |
| 20 | `game/strategy/data/race_caption_loader.py` | 116 | 2 | ✓ | 6 | 4 | `__init__`, `_load` (MINOR) |
| 21 | `game/strategy/data/stars.py` | 770 | 2 | ✓ | 24 | 18 | 6 StarGenerator helpers (MINOR) |
| 22 | `game/strategy/data/task_force.py` | 142 | 2 | ✓ | 10 | 7 | `__init__` + 2 formation serializers (MINOR) |
| 23 | `game/strategy/engine/handlers/registry_factory.py` | 125 | 0 | ✓ | 1 | 0 | **CRITICAL** — `create_default_registry` |
| 24 | `game/strategy/facade/dto/system_dto.py` | 162 | 3 | ✓ | 5 | 5 | — |
| 25 | `game/strategy/generation/loaders/galaxy_layouts_loader.py` | 182 | 2 | ✓ | 7 | 6 | `_scale_primitive` (MINOR) |
| 26 | `game/strategy/generation/region_classifier.py` | 275 | 2 | ✓ | 10 | 8 | `__init__`, `_build_regions` (MINOR) |
| 27 | `game/strategy/interfaces/battle_resolver.py` | 109 | 3 | ✓ | 3 | 3 | — |
| 28 | `game/strategy/services/ability_sources/fleet.py` | 148 | 0 | ✓ | 12 | 0 | **CRITICAL** — all 12 symbols |
| 29 | `game/strategy/services/deployment_zone_calculator.py` | 107 | 3 | ✓ | 3 | 3 | — |
| 30 | `game/strategy/services/task_group_suggester.py` | 125 | 3 | ✓ | 1 | 1 | — |
| 31 | `game/ui/components/__init__.py` | 1 | 0 | ✓ | 0 | 0 | ADVISORY — 1-line docstring |
| 32 | `game/ui/screens/battle_setup/panels/left_panel.py` | 181 | 0 | ✓ | 1 | 0 | ADVISORY — `build()` pygame_gui construction |
| 33 | `game/ui/screens/battle_setup/screen.py` | 189 | 2 | ✓ | 31 | 8 | ADVISORY — 23 UI shim properties/methods |
| 34 | `game/ui/screens/builder_selection.py` | 123 | 2 | ✓ | 4 | 3 | `_is_component_like` (MINOR) |
| 35 | `game/ui/screens/event_log_data_source.py` | 242 | 2 | ✓ | 11 | 10 | `_recompute_filtered` (MINOR) |
| 36 | `game/ui/screens/event_log_sidebar.py` | 91 | 2 | ✓ | 6 | 3 | `__init__`, 2 widget builders (ADVISORY) |
| 37 | `game/ui/screens/fleet_report_window.py` | 430 | 2 | ✓ | 18 | 6 | LayoutBuilder + 11 window methods (ADVISORY) |
| 38 | `game/ui/screens/galaxy_test/screen.py` | 286 | 2 | ✓ | 16 | 3 | 13 UI lifecycle methods (ADVISORY) |
| 39 | `game/ui/screens/race_setup/llm_dialog_service.py` | 154 | 2 | ✓ | 5 | 3 | `check_dialog_thresholds`, `check_error_popups` (MINOR) |
| 40 | `game/ui/screens/star_data_source.py` | 71 | 0 | ✓ | 7 | 0 | ADVISORY — all 7 symbols |
| 41 | `game/ui/screens/strategy_menu_panel.py` | 103 | 3 | ✓ | 5 | 5 | — |
| 42 | `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | 159 | 0 | ✓ | 9 | 0 | ADVISORY — all 9 symbols |
| 43 | `game/ui/screens/strategy_windows/selection_prompts.py` | 85 | 0 | ✓ | 5 | 0 | ADVISORY — all 5 symbols |
| 44 | `game/ui/screens/test_lab/details/propulsion_outcomes.py` | 229 | 0 | ✓ | 5 | 0 | ADVISORY — all 5 drawing helpers |
| 45 | `game/ui/screens/workshop_viewmodel_selection.py` | 138 | 0 | ✓ | 3 | 0 | ADVISORY — 3 pure-function helpers |
| 46 | `game/ui/services/ship_io_adapter.py` | 100 | 2 | ✓ | 6 | 5 | `__init__` (MINOR) |
| 47 | `game/ui/widgets/preference_row.py` | 237 | 2 | ✓ | 9 | 4 | `__init__` + 4 methods (ADVISORY) |

---

## Context Usage Estimate

- **Production files read:** 47 of 47 (100%)
- **Estimated total LOC read:** ~9,057 (production) + ~500 (docs skim) + coverage matrix filtering
- **Context budget used:** Approximately 150k tokens (47 files × average 3000 chars/file + matrix entries + docs)

---

## Remediation Priorities

### P0 — Immediately (CRITICAL)
1. `game/core/protocols/boundary.py` — Protocol + TypeGuard unit tests
2. `game/services/llm/defaults.py` — Default accessor unit tests
3. `game/strategy/engine/handlers/registry_factory.py` — Handler wiring verification
4. `game/strategy/services/ability_sources/fleet.py` — IAbilitySource compliance tests

### P1 — This Sprint (MAJOR)
5. `game/simulation/components/component_constants.py` — Modifier constructor tests
6. `game/simulation/components/component.py` — Facade delegate boundary tests
7. `game/simulation/battle_runner.py` — `_derive_end_reason` disambiguation test

### P2 — Next Sprint (MINOR)
8. Remaining Tier 2 gaps: validation post_init, defense.py subclass, modifier_service helper, registry_loader find_file, fleet_battle_adapter policies, galaxy_entity_registry index, race_caption_loader load, stars.py generators, task_force serializers, galaxy_layouts scaling, region_classifier init, builder_selection duck-type check, event_log_data_source filter, llm_dialog_service threshold/error checks, ship_io_adapter init

### P3 — Backlog (ADVISORY)
9. All Tier 0 UI files: left_panel build(), star_data_source, event_log_window_ctrl, selection_prompts, propulsion_outcomes, workshop_viewmodel_selection, galaxy_test/screen, fleet_report_window layout, event_log_sidebar widgets, preference_row widgets
