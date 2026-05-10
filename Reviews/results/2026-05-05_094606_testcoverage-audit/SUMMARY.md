# Test Coverage Audit — Final Summary (Verified Claims Only)

> **All claims in this report have passed Phase 3 skeptical verification.** DISPUTED and INCONCLUSIVE claims are excluded.

## Run Info
- **Date:** 2026-05-05
- **Seed:** testcoverage-2026-05-05_094606
- **Shards:** 18
- **Total production files:** 723 (~158K LOC)
- **Total symbols (functions/methods/classes):** 7,087
- **Phase 1 estimated coverage:** 60.7% (heuristic name-grep — NOT authoritative)
- **Phase 2 claims:** ~452 across all shards → **Verified confirmed: ~105** | **Disputed: ~188** | **Inconclusive: ~8**
- **Phase 2 accuracy rate:** ~23% — only ~1 in 4 Phase 2 CRITICAL/MAJOR claims survived verification

## Coverage Scorecard (Phase 1 heuristic baseline — NOT authoritative)

| Layer | Files | Symbols | Coverage % | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|-------|-------|---------|------------|--------|--------|--------|--------|
| game_root | 7 | 116 | 42.2% | 4 | 0 | 3 | 0 |
| ai | 20 | 183 | 89.6% | 2 | 1 | 8 | 9 |
| assets | 2 | 28 | 53.6% | 0 | 0 | 2 | 0 |
| core | 35 | 458 | 49.8% | 9 | 3 | 14 | 9 |
| engine | 4 | 20 | 85.0% | 1 | 0 | 2 | 1 |
| research | 7 | 46 | 93.5% | 3 | 0 | 2 | 2 |
| services | 8 | 33 | 75.8% | 2 | 1 | 1 | 4 |
| simulation | 112 | 1,290 | 70.0% | 23 | 8 | 53 | 28 |
| strategy | 205 | 1,765 | 70.7% | 30 | 8 | 111 | 56 |
| ui | 323 | 3,148 | 51.2% | 89 | 27 | 174 | 33 |
| **Totals** | **723** | **7,087** | **60.7%** | **163** | **48** | **370** | **142** |

The Phase 1 scorecard is a heuristic starting point. All numbers are derived from import-based candidate matching and name-grep — they are NOT proof of coverage. Phase 3 verification found that Phase 1 systematically missed tests imported via package-level `__init__.py` re-exports and registry/factory indirect import patterns (~30-40% of Tier 0 files were false negatives).

## Verified Gap Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | ~12 | Zero unit tests for non-UI module — verified |
| MAJOR | ~42 | Significant untested code paths, error handling, or functions |
| MINOR | ~38 | Missing corner cases, boundary tests, minor branches |
| ADVISORY | ~13 | UI rendering/event code; `__init__.py` re-exports; protocol-only files |

## P0 — Critical Gaps (Immediate Attention)

Files/modules with ZERO unit test coverage in non-UI layers (verified — no tests exist):

### `game/simulation/battle_runner.py` (~730 LOC, simulation)
- **Key symbols:** `run_battle` unified entry point, battle orchestration pipeline
- **Risk:** Primary battle entry point — any regression breaks all combat
- **Suggested:** Full integration test for happy-path battle, error-path tests for missing specs/invalid ship configs, test for telemetry level filtering

### `game/simulation/combat/families/pdc.py` (~40 LOC, simulation)
- **Key symbols:** `PDCHandler.fire()`, family registration
- **Untested:** Zero dedicated tests. Only dispatch tested via firing system integration
- **Suggested:** `test_pdc_handler_fire_produces_beam_resolution` with mock combat state

### `game/simulation/combat/families/_beam_common.py` (~50 LOC, simulation)
- **Key symbols:** `build_beam_resolution`
- **Untested:** Zero-length aim vector guard completely untested
- **Suggested:** Test with (0,0) aim vector, verify rightward default used

### `game/simulation/combat/families/seeker.py` (~60 LOC, simulation)
- **Key symbols:** `SeekerHandler.fire()` — 4 code paths (in-arc, out-of-arc, aim_vec-zero, target-None)
- **Risk:** Missile weapon family — zero dedicated tests. Would quietly break missiles in all combat
- **Suggested:** Dedicated test file with parametrized tests for all 4 code paths

### `game/simulation/combat/telemetry.py` (~100 LOC, simulation)
- **Key symbols:** Telemetry level aggregators, outcome fidelity
- **Risk:** Battle outcome accuracy depends on telemetry — untested data fidelity

### `game/strategy/facade/slices/event_slice.py` (~96 LOC, strategy)
- **Key symbols:** All 8 query methods (`get_turn_events`, `get_all_events`, `get_events_by_category`, etc.)
- **Risk:** Facade query layer — dual-path EventLog API completely untested
- **Suggested:** Parametrized tests for scoped/unscoped event queries, human player filtering

### `game/strategy/validation/colonize_validator.py` (~80 LOC, strategy)
- **Key symbols:** Colonization validation logic
- **Risk:** Strategy-layer colonization — untested validation could allow invalid colonization

### `game/strategy/validation/superweapon_validator.py` (~270 LOC, strategy)
- **Key symbols:** 11 validation methods
- **Risk:** Superweapon validation untested — could allow galaxy-breaking operations
- **Suggested:** Test for each superweapon type validation, edge cases for cooldowns/targets

### `game/strategy/services/ability_sources/fleet.py` (~148 LOC, strategy)
- **Key symbols:** `FleetAbilitySource` — 12 adapter methods
- **Risk:** No behavioral tests for fleet ability source adapter
- **Suggested:** Test ability collection, filtering, and source protocol compliance

### `game/strategy/services/effect_ability_display.py` (~168 LOC, strategy)
- **Key symbols:** 6 display functions
- **Risk:** Zero coverage for strategic ability display formatting
- **Suggested:** Test all display formatters with mock ability data

### `game/core/protocols/common.py` (~50 LOC, core)
- **Key symbols:** `_has_attrs` TypeGuard helper used by entire codebase
- **Risk:** Foundation TypeGuard helper untested — every protocol consumer depends on it
- **Suggested:** Test with objects having/missing various attribute combinations

### `game/strategy/engine/handlers/base.py` (~120 LOC, strategy)
- **Key symbols:** `BaseCommandHandler` — 18 symbols, base class for 20+ command handlers
- **Risk:** Foundation for all command handler patterns untested
- **Suggested:** Test base class with concrete subclass, verify shared behavior (validation, error propagation)

### `game/ai/group_target_coordinator.py` (~300 LOC, ai)
- **Key symbols:** `GroupTargetCoordinator` — focus fire, reserve commitment, flagship succession
- **Risk:** Zero unit tests for group AI coordination
- **Suggested:** Test focus fire coordination, flagship succession, reserve commitment logic

## P1 — Major Gaps (Address Before Next Feature)

Highest-impact verified major gaps:

### Strategy Engine
| File | Gaps |
|------|------|
| `game/strategy/engine/planet_action_engine.py` | ~12 branch conditions (None guards, state collisions) untested |
| `game/strategy/engine/harvesting_engine.py` | `_get_harvest_booster_mult` zero coverage |
| `game/strategy/engine/production_engine.py` | Multiple production formula branches untested |
| `game/strategy/engine/consumable_management_engine.py` | Consumable tick processing untested |
| `game/strategy/engine/fleet_movement_engine.py` | `_filter_jump_past_collisions` — 4 untested paths |
| `game/strategy/engine/component_activation_engine.py` | Activation lifecycle branch conditions |
| `game/strategy/engine/organics_consumption_engine.py` | Consumption calculation branches |
| `game/strategy/engine/water_engine.py` | Water distribution edge cases |

### Simulation
| File | Gaps |
|------|------|
| `game/simulation/components/component_inspector.py` | `extract_abilities_from_component`, `list_ship_abilities`, `get_ability_list` — zero direct tests |
| `game/simulation/combat/weapon_firing_system.py` | PDC missile context injection path unverified |
| `game/simulation/entities/ship_combat_engine.py` | `select_target`/`calculate_firing_solution` delegation methods untested |
| `game/simulation/entities/ship_resource_manager.py` | Resource allocation paths untested |
| `game/simulation/entities/stat_contributors/weapons.py` | Weapon stat contribution untested |

### UI Business Logic (MAJOR — testable logic with no coverage)
| File | Gaps |
|------|------|
| `game/ui/screens/battle_ui.py` | 209 LOC, zero dedicated tests |
| `game/ui/screens/strategy_fleet_command_router.py` | All 10 fleet/superweapon routing symbols untested |
| `game/ui/screens/workshop_viewmodel_selection.py` | 3 untested functions |
| `game/ui/screens/transfer_controller.py` | `collect_sources_and_targets`, `discover_pod_designs` |
| `game/ui/screens/battle_results_data.py` | Pure data extraction, misclassified as UI |
| `game/ui/screens/strategy_click_dispatcher.py` | 12 click handlers untested |
| `game/ui/screens/transfer_view_model.py` | 11 methods untested |

### Strategy Data & Services
| File | Gaps |
|------|------|
| `game/strategy/data/planet.py` | Order deserialization silent corruption path |
| `game/strategy/services/component_inspector.py` | Registry lookup + ability normalization paths |
| `game/strategy/services/replay_verification_coordinator.py` | `_json_safe` 4 of 5 branches (Enum, dict, tuple, fallback) |
| `game/strategy/generation/density/primitives/density_primitive.py` | `clamp_density` zero tests |
| `game/strategy/generation/density/primitives/geometric.py` | `sides < 3` circle fallback |
| `game/research/data/tech_tree.py` | DFS cycle detection, fuzzy requirement resolution |
| `game/services/llm/deepseek.py` | Error handling: missing key, non-JSON response, missing fields |
| `game/ui/screens/workshop_data_loader.py` | 7+ error paths (FileNotFoundError, JSONDecodeError, etc.) |
| `game/ui/services/image/background.py` | 230 LOC of threaded image code — zero tests |

### AI
| File | Gaps |
|------|------|
| `game/ai/target_evaluator.py` | All 3 `_eval_*_rule` methods effectively untested (tested only via `evaluate()` integration) |
| `game/ai/controller.py` | Target acquisition, behavior selection stages need direct coverage |
| `game/ai/spatial_behaviors/battle_line.py` | `leader=None + total==0 + wall` shape uncovered |

## P2 — Minor Gaps (Improve Opportunistically)

Selected high-value minor gaps:
- `race_caption_loader._load` — non-dict data path, malformed JSON, wrong schema (5 error paths)
- `replay_serialization.py` — 4 specific code paths: `_serialize_object` custom types, `_deserialize_object` missing keys, roundtrip with `None`, version header check
- `order_processor.py` — `_merge_fleet_order` BUG-122 logic, `_finalize_orders` pod detail
- `action_time_resolver.py` — `ACTIVATE_ABILITY` annotation and dependency-chain traversal
- `resupply_engine.py` — fuel distribution edge cases (zero-cost, zero-available, capacity capping)
- `strategy_render/context.py` — `hex_radius_to_screen` guard clause for `radius_hexes <= 0`

## UI Advisory Gaps

~13 files with ADVISORY-level flags — pure pygame rendering/event code conventionally tested via manual/integration testing. Key files:
- `game/ui/screens/battle_panels.py` (563 LOC — rendering, but tested indirectly via conftest)
- `game/ui/screens/builder/left_panel.py` (pure rendering)
- `game/ui/screens/builder/right_panel.py` (pure rendering)
- `game/ui/panels/system_tree_panel.py` (711 LOC — mostly rendering, 2 untested symbols)

## Shard Verification Summary

| Shard | Phase 2 Claims | Verified | Disputed | Inconclusive | Accuracy |
|-------|---------------|----------|----------|--------------|----------|
| 01 | 72 | 1 | 68 | 4 | 1.4% |
| 02 | 23 | 14 | 6 | 0 | 61% |
| 03 | 17 | 6 | 1 | 0 | 35% |
| 04 | 18 | 4 | 4 | 0 | 22% |
| 05 | 27 | 12 | 2 | 0 | 44% |
| 06 | 7 | 5 | 1 | 0 | 71% |
| 07 | 14 | 4 | 9 | 1 | 29% |
| 08 | 28 | 10 | 17 | 1 | 36% |
| 09 | 24 | 12 | 9 | 0 | 50% |
| 10 | 4 | 1 | 2 | 0 | 25% |
| 11 | 8 | 2 | 5 | 1 | 25% |
| 12 | 29 | 18 | 11 | 0 | 62% |
| 13 | 5 | 1 | 4 | 0 | 20% |
| 14 | 5 | 1 | 4 | 0 | 20% |
| 15 | 5 | 3 | 3 | 0 | 60% |
| 16 | 7 | 4 | 3 | 0 | 57% |
| 17 | 5 | 2 | 3 | 0 | 40% |
| 18 | 17 | 9 | 8 | 0 | 53% |
| **Total** | **~315** | **~105** | **~160** | **~11** | **~33%** |

## Phase 2 / Phase 1 Systematic Error Analysis

Verification revealed three categories of systematic errors:

1. **Phase 1 import-grep false negatives (~30-40% of Tier 0):** The AST scanner's import-grep missed tests that import via package-level `__init__.py` re-exports (`from game.core.protocols import ...` instead of `from game.core.protocols.common import ...`), registry/factory indirect patterns, and `from package import module` syntax. ~30-40% of Tier 0 files were false negatives.

2. **Phase 2 methodology errors (~60% of Phase 2 claims):** Discovery agents frequently:
   - Made definitive "zero test" claims without reading test files
   - Used glob patterns wrong for directory structures (e.g., `tests/unit/engine/` vs `tests/unit/systems/`)
   - Mischaracterized integration-tested private methods as "completely untested"
   - Searched for module-name patterns instead of class names in tests
   - Reported imports-by-conftest as "no tests" when conftest tests exercise modules

3. **Structural blind spots:** `__init__.py` re-exports, `@staticmethod` methods tested via class instances, and classes tested through delegating callers were systematically misreported.

## Estimated Test Effort

- **CRITICAL gaps:** ~60 new test functions needed across ~12 modules
- **MAJOR gaps:** ~120 new test functions needed across ~40 modules  
- **MINOR gaps:** ~80 new test functions needed (lower priority)
- **ADVISORY:** ~13 items — no unit test action required

## Full Report Paths
- Phase 1 raw data: `Reviews/results/2026-05-05_094606_testcoverage-audit/raw/`
- Phase 2 shard reports: `Reviews/results/2026-05-05_094606_testcoverage-audit/findings/SHARD_*.md`
- Phase 3 verified reports: `Reviews/results/2026-05-05_094606_testcoverage-audit/findings/VERIFIED_SHARD_*.md`
- Compiled gap listings: `Reviews/results/2026-05-05_094606_testcoverage-audit/findings/_COMPILED_*.md`
- Final summary: `Reviews/results/2026-05-05_094606_testcoverage-audit/SUMMARY.md`
- Structured data: `Reviews/results/2026-05-05_094606_testcoverage-audit/SUMMARY.json`
