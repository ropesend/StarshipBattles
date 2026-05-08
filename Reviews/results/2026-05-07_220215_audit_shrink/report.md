# Code Shrinkage Audit — Final Report

**Date:** 2026-05-07 22:02 UTC
**Review Directory:** `Reviews/results/2026-05-07_220215_audit_shrink`
**Shard Reviewed (rotating):** Shard 02 (188 files, ~40,241 LOC)
**Seed:** `shrink-2026-05-07_220215`

---

## 1. Executive Summary

Full audit of 749 production files (~161,231 LOC) completed. Deterministic Phase 1 ran vulture, radon, and clone detection across all files (100% coverage). Phase 2 launched 3 LLM agents: cross-shard duplication hunter (749 files), deep reviewer on Shard 02 (188 files, 100% read), and dead code validator (8 vulture candidates). Phase 2b cross-verification re-checked every CRITICAL finding against tests, docs, and data files.

**Headline findings:**
- Only **1 truly dead symbol** found (`IControllableShip` import — symbol no longer exists)
- **22 clone detector clusters** validated (all genuine), plus **8 additional cross-shard findings** discovered manually
- **13 files exceed the 500 LOC ceiling** (planet_list_window leads at 732 LOC)
- **47 complexity hotspots** with CC >= 20 (worst: `race_setup/input_handler.py:handle` at CC=52)
- **475 LOC of achievable consolidation** identified across duplication findings, with **190 LOC safe (Simple effort)**
- Deep review of Shard 02: **5 Major** internal duplication findings, **13 ceiling violators**

**Coverage status:** 100% deterministic coverage every run. LLM deep review rotates 1 of 4 shards per run (this run: Shard 02). Full LLM coverage every 4 cycles. Next run reviews Shard 03.

---

## 2. Coverage Status

| Shard | Files | LOC | Deep Review File | Status |
|-------|-------|-----|-----------------|--------|
| Shard 01 | 183 | 40,262 | — | Last reviewed 2026-05-05 |
| Shard 02 | 188 | 40,241 | `deep_review.md` | **Reviewed this run** ✓ |
| Shard 03 | 190 | 40,241 | — | Next in rotation |
| Shard 04 | 188 | 40,487 | — | Pending |

100% LLM deep-review coverage achieved every 4 runs via manifest shard rotation (01 → 02 → 03 → 04).

---

## 3. Dead Code Inventory

### Tier 4: Dead Imports (confirmed safe)
| Import | File:Line | LOC | Verified |
|--------|-----------|-----|----------|
| `IControllableShip` | `game/ai/controller.py:56` | ~2 | Symbol no longer exists in target module. MyPy corroborates. Zero test/doc/data refs. |

### False Positives (not dead)
| Item | Reason |
|------|--------|
| `exc_type`/`exc_val`/`exc_tb` (battle_engine.py:98) | Standard `__exit__` context manager protocol parameters |
| `RegionClassifier` (galaxy.py:29, galaxy_warp_generator.py:15) | TYPE_CHECKING-guarded; actively used at runtime |
| `BuildContext` (build_queue_controller.py:19) | TYPE_CHECKING under `from __future__ import annotations`; protocol used in type hints |
| `validate_positive` (galaxy.py:6) | Actively used at galaxy.py:299; documented in `docs/05_ERROR_HANDLING.md` |

### 3b. Product Decision Required

| Item | File | LOC | Ref Type | Source | Recommendation |
|------|------|-----|----------|--------|----------------|
| `create_brick` / `create_interceptor` | `game/simulation/designs.py:11-68` | 68 | Tests only | Combat Lab fixtures import these | Move to `tests/fixtures/` or update to use quickstart data |
| `ShipPickerStub` | `game/ui/screens/strategy_windows/ship_picker.py:16-43` | 43 | Production + Tests | Wired in strategy_window_manager.py | PROJ-198 placeholder; implement or inline |
| `allocate_crew_and_life_support` | `game/simulation/entities/stat_contributors/command.py:56-100` | 44 | Production + Tests | Called by ShipStatsCalculator | Correctly placed; clarify via docstring |
| `has_superweapons` | `game/ui/screens/builder/stat_getters.py:315-321` | 7 | Tests only | Only test calls exist | Inline into test or register as test-helper |

Total product-decision LOC: **162** (not counted toward safe shrinkage)

---

## 4. Duplication Clusters

### Clone Detector Validation
All 22/22 clone detector clusters confirmed genuine. One cluster (Cluster 21: empire.add_resources / planet.add_to_stockpile) downrated — protocol conformance, not duplication. Cluster 10 (deprecated ModifierManager static methods) already marked for deletion in Task 1.3.

### Cross-Shard Findings (8 additional)
#### CRITICAL: DUP-X-01 — Superweapon Mission Handler Template
**Location:** `game/strategy/engine/superweapon_command_handlers.py:296-438` (5 execute methods)
**Layer:** strategy (command handler registry)
**Issue:** Five mission handlers (`StellerateStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `ImplodePlanet`) duplicate identical 4-step execute skeleton (~23 lines each). Contradicts CommandHandlerRegistry pattern #7.
**Estimated LOC Savings:** 60
**Effort:** Medium

#### CRITICAL: DUP-X-02 — LLM/Image Provider Factory Duplication (Pattern #15 Violation)
**Location:** `game/services/llm/factory.py:52-87` AND `game/ui/services/image/factory.py:47-79`
**Layer:** services (cross-cutting)
**Issue:** Two near-identical static factory methods reimplementing Factory pattern (#15) with only env-var and exception-class differences.
**Estimated LOC Savings:** 25
**Effort:** Simple

#### MAJOR Duplication (12 findings, top 5 by savings):
| ID | Description | Locations | Savings | Effort |
|----|-------------|-----------|---------|--------|
| DUP-X-05 | Delete deprecated ModifierManager static methods | `modifier_manager.py:166-330` | 100 | Simple |
| DUP-X-03 | Ability `__init__` boilerplate (6+ classes) | `planetary.py:453-800` | 30 | Medium |
| DUP-X-04 | Hit effect rendering parameterization | `hit_effects.py:146-219` | 25 | Simple |
| DUP-X-12 | Ability source provider boilerplate | `ability_iterator.py:217-298` | 25 | Medium |
| DUP-X-07 | Right-click cancel + cargo/transfer handler consolidation | `strategy_click_dispatcher.py:125-297` | 24 | Medium |

#### MINOR Duplication (13 findings, top 5 by savings):
| ID | Description | Savings | Effort |
|----|-------------|---------|--------|
| DUP-X-06 | Cargo load/unload mirror methods | 18 | Simple |
| DUP-X-13 | Selection prompt window creation | 15 | Simple |
| DUP-X-16 | Tkinter file dialog functions | 15 | Simple |
| DUP-X-08 | Superweapon ability check + coordinate conversion | 15 | Simple |
| DUP-X-15 | Race randomizer pick functions | 12 | Simple |

**Total duplication:** 22 clone clusters + 8 cross-shard findings = **30 findings**, **475 LOC achievable**.

---

## 5. Complexity Hotspots (CC >= 20)

| CC | Function | File | Line |
|----|----------|------|------|
| 52 | `handle` | `game/ui/screens/race_setup/input_handler.py` | 30 |
| 37 | `process_event` | `game/ui/screens/planet_list_window.py` | 425 |
| 37 | `_handle_button` | `game/ui/screens/battle_setup/input_handler.py` | 44 |
| 35 | `apply_planet_list_state` | `game/ui/screens/planet_list_presets.py` | 124 |
| 31 | `build` | `game/ui/screens/battle_setup/panels/center_panel.py` | 14 |
| 31 | `set_items` | `game/ui/panels/system_tree_panel.py` | 177 |
| 29 | `format_planet_info` | `game/ui/screens/strategy_detail_fmt.py` | 147 |
| 28 | `_format_orders` | `game/ui/screens/strategy_detail_fmt.py` | 542 |
| 28 | `RaceSetupInputHandler` | `game/ui/screens/race_setup/input_handler.py` | 21 |
| 28 | `update_component_list` | `game/ui/screens/builder/left_panel.py` | 246 |
| 27 | `draw_ship` | `game/ui/renderer/game_renderer.py` | 53 |
| 27 | `_resolve_planets_for_scope` | `game/strategy/services/strategic_ability_scanner.py` | 185 |
| 27 | `_eval_node` | `game/core/formula_evaluator.py` | 81 |
| 26 | `process_environmental_tick` | `game/strategy/engine/environmental_hazard_engine.py` | 84 |
| 25 | `process_event` | `game/ui/screens/star_list_window.py` | 308 |
| 25 | `_build_resource_rows` | `game/ui/screens/builder/stat_rows_dynamic.py` | 80 |
| 25 | `handle_event` | `game/ui/screens/builder/left_panel.py` | 362 |
| 24 | `_compute_local_positions` | `game/simulation/combat/formation.py` | 128 |
| 24 | `_recalculate` | `game/simulation/combat/fleet_aura_manager.py` | 326 |
| 23 | `draw_system_details` | `game/ui/screens/strategy_render/systems.py` | 173 |

Full list: 47 functions with CC >= 20 across 34 files.

---

## 6. In-Shard Deep Review Summary (Shard 02)

**Coverage:** 188/188 files read (100%).

### Key Findings:
- **No CRITICAL dead code** found within Shard 02 — clean codebase
- **3 PRODUCT_DECISION** items: legacy test-ship constructors (68 LOC), ShipPickerStub (43 LOC), and docstring clarification for allocate_crew_and_life_support (44 LOC)
- **5 MAJOR** internal duplication findings:
  - `classification_config.py`: 26-field assignment duplication in `_use_defaults()` / `_load_from_json()` (~50 LOC reduction)
  - `battle_setup/controller.py`: Duplicated TF/SQ ship-cloning loops (~120 LOC via planned `FleetHierarchyEditor` extraction)
  - `stat_rows_dynamic.py`: Repeated resource-iteration patterns (~80 LOC reduction)
  - `stat_getters.py`: 7 near-identical resource getter functions (~40 LOC reduction)
  - Module-level `_cached_registries` globals (PROJ-211 cleanup)
- **13 files exceed 500 LOC ceiling** (identified with actionable extraction targets)
- **1 documented latent bug**: undefined `screen_diameter` in `dyson_spheres.py` (NameError in rare code path)
- **5 MINOR** findings + **11 INFO** quality/LOC-reduction items

### LOC Ceiling Violations (Shard 02):
| File | LOC | Over Ceiling | Suggested Extraction |
|------|-----|-------------|---------------------|
| `planet_list_window.py` | 732 | +232 | `PlanetListEventRouter` (200 LOC) |
| `build_queue_controller.py` | 707 | +207 | Category/add/report controllers |
| `turn_engine.py` | 700 | +200 | `turn_tick_runner.py`, snapshot handler |
| `workshop_screen.py` | 648 | +148 | `WorkshopLayoutBuilder` (150 LOC) |
| `virtual_table.py` | 607 | +107 | Replay tooltip module (100 LOC) |
| `strategy_click_dispatcher.py` | 593 | +93 | Mode-specific handler modules |
| `keybindings_scene.py` | 582 | +82 | `KeybindingsRenderer` (100 LOC) |
| `battle_setup/controller.py` | 579 | +79 | `FleetHierarchyEditor` (120 LOC) |
| `battle_panels.py` | 563 | +63 | `ShipListPanel` extraction |
| `event_log_window.py` | 539 | +39 | `ReplayButtonHandler` (100 LOC) |
| `layer_panel.py` | 536 | +36 | `LayerGroupingControls` (80 LOC) |
| `app.py` | 533 | +33 | Startup/exit helpers |
| `stat_rows_dynamic.py` | 515 | +15 | Resource row builder abstraction |

---

## 7. Shrinkage Scorecard

| Category | Estimated Reclaimable LOC | Effort | Risk | Source |
|----------|--------------------------|--------|------|--------|
| Dead imports (verified safe) | 2 | Simple | Safe | Dead code validator |
| Deprecated duplicate deletion | 100 | Simple | Safe | DUP-X-05 (ModifierManager static) |
| Duplicate consolidation (simple) | 190 | Simple | Safe | Cross-shard duplication report |
| Duplicate consolidation (medium) | 163 | Medium | Needs design | Cross-shard duplication report |
| Duplicate consolidation (complex) | 40 | Complex | Needs design | DUP-X-11 (serialization) |
| In-shard internal duplication | ~290 | Low-Medium | Safe | Deep review (Shard 02 only) |
| **Total (safe items, shard reviewed)** | **~230** | | | 1 dead import + 190 simple + safe internal |
| **Total (all achievable + this shard)** | **~825** | | | Full consolidation potential |

### 7b. Product Decision Required (not counted toward safe totals)

| Item | File | LOC | Ref Type | Source | Recommendation |
|------|------|-----|----------|--------|----------------|
| `create_brick` / `create_interceptor` | `game/simulation/designs.py` | 68 | Tests | Combat Lab fixtures | Move to test fixtures |
| `ShipPickerStub` | `game/ui/screens/strategy_windows/ship_picker.py` | 43 | Prod + Tests | strategy_window_manager.py | PROJ-198: implement or inline |
| `allocate_crew_and_life_support` | `game/simulation/entities/stat_contributors/command.py` | 44 | Prod + Tests | ShipStatsCalculator | Clarify docstring |
| `has_superweapons` | `game/ui/screens/builder/stat_getters.py` | 7 | Tests | test_stat_getters.py | Inline or register |

These items must NOT be counted in the safe-shrinkage total. They inflate estimates until product decisions are made.

---

## 8. Prioritized Cleanup Plan (verified-safe only)

| Rank | ID | Item | Savings | Effort | Category |
|------|-----|------|---------|--------|----------|
| 1 | DUP-X-05 | Delete deprecated `ModifierManager` static methods | 100 LOC | Simple | Dead code removal |
| 2 | DUP-X-02 | Provider factory base class (LLM + Image) | 25 LOC | Simple | Duplicate consolidation |
| 3 | DUP-X-04 | Parameterize hit effect rendering | 25 LOC | Simple | Duplicate consolidation |
| 4 | DUP-X-06 | Consolidate cargo load/unload mirror methods | 18 LOC | Simple | Duplicate consolidation |
| 5 | DUP-X-13 | Generic selection prompt window helper | 15 LOC | Simple | Duplicate consolidation |
| 6 | DUP-X-16 | Tkinter file dialog consolidation | 15 LOC | Simple | Duplicate consolidation |
| 7 | DUP-X-08 | Camera.hex_at_screen convenience method | 15 LOC | Simple | API consolidation |
| 8 | DUP-X-09 | Event log cell detail helper | 12 LOC | Simple | Duplicate consolidation |
| 9 | DUP-X-15 | Race randomizer generic pick function | 12 LOC | Simple | Duplicate consolidation |
| 10 | DCV-01 | Remove dead `IControllableShip` import | 2 LOC | Simple | Dead code removal |

**Top 10 verified-safe savings: 239 LOC** (all Simple effort).

---

## 9. Trend Comparison

| Metric | 2026-05-05 | 2026-05-07 | Trend |
|--------|------------|------------|-------|
| Production LOC | 158,476 | 161,231 | +2,755 |
| Duplication clusters | 39 | 30 | -9 |
| Dead code functions | 1 | 1 | 0 |
| Dead imports | 0 | 1 | +1 |
| Estimated shrinkable LOC | 533 | ~825* | +292* |
| Top CC hotspot | 52 (same file) | 52 | 0 |
| Ceiling violators (shard only) | — | 13 | First measurement |

*^* *Increase vs previous run reflects expanded cross-shard hunting (8 additional findings not present in clone detector) and first-time deep review of Shard 02 with its 13 ceiling violators and internal duplication findings. Safe-only total remains comparable: ~230 vs 533 (the previous run's estimate included cross-shard agent findings; this run separates safe from total).*

**LOC growth note:** +2,755 LOC in 2 days. Main contributors: continued feature development across strategy and UI layers.

---

## 10. Appendices

### Raw Tool Outputs
- `raw/loc_baseline.txt` — Full LOC breakdown by layer
- `raw/vulture_100.txt` — Vulture 100% confidence (3 entries, all false positive __exit__ params)
- `raw/vulture_80.txt` — Vulture 80% confidence (7 entries, 1 confirmed dead)
- `raw/radon.json` — Cyclomatic complexity data (47 CC >= 20)
- `raw/clones.json` — Clone detector clusters (22 clusters, 488 duplicated LOC)
- `raw/manifest.json` — File inventory + shard assignments

### Agent Reports
- `findings/duplication_cross_shard.md` — Cross-shard duplication report (30 findings)
- `findings/deep_review.md` — In-shard deep review (Shard 02, 24 findings)
- `findings/dead_code_validation.md` — Dead code validation (1 confirmed, 7 false positives)
- `findings/verification.md` — Cross-verification (8 findings verified)

### Historical
- `../shrink_tracker.json` — All historical run data (4 runs tracked)
