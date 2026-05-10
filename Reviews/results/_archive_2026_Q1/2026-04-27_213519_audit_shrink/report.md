# Code Shrinkage Audit — Final Report

**Date:** 2026-04-27
**Review Directory:** `Reviews/results/2026-04-27_213519_audit_shrink`
**Production Codebase:** `game/` (143,262 LOC across 656 files)
**Scope:** All 4 shards deep-reviewed (100% coverage)

---

## 1. Executive Summary

Full-coverage audit across all 656 production files. **146 findings** (19 critical, 33 major, 48 minor, 46 info) with **~3,770 LOC estimated reclaimable**. The Simulation layer holds the most dead code (~484 LOC) while the UI layer has the most duplication by volume (~1,700 LOC cross-shard + ~323 in-shard). This is the **first full-coverage run** — no trend comparison available.

---

## 2. Coverage Status

| Shard | Label | Files | LOC | Deep Review File | Status |
|-------|-------|-------|-----|-----------------|--------|
| UI | UI Layer | 292 | 68,448 | `deep_review_UI.md` | ✓ 292/292 (100%) |
| SIM | Simulation Layer | 89 | 22,145 | `deep_review_SIM.md` | ✓ 89/89 (100%) |
| STR | Strategy Layer | 194 | 39,784 | `deep_review_STR.md` | ✓ 194/194 (100%) |
| FND | Foundation Layer | 81 | 12,885 | `deep_review_FND.md` | ✓ 81/81 (100%) |

---

## 3. Dead Code Inventory

| Source | Tier 1 (Files) | Tier 2 (Classes) | Tier 3 (Functions/Params) | Tier 4 (Imports) | Total LOC |
|--------|:---:|:---:|:---:|:---:|-----:|
| Dead code validator (Agent 3) | 0 | 0 | 4 (~8 LOC) | 8 (~7 LOC) | ~15 |
| SIM in-shard | 2 (TechPresetLoader, designs.py) | 0 | 5 | 0 | 484 |
| FND in-shard | 1 (GroupTargetCoordinator) | 0 | 3 | 0 | 214 |
| UI in-shard | 0 | 1 (ModifierLogic) | 2 | 1 | 68 |
| STR in-shard | 0 | 0 | 0 | 0 | 0 |
| **Total** | **3** | **1** | **14** | **9** | **~781** |

### Notable Dead Items

| Item | File | LOC | Layer |
|------|------|----:|-------|
| `TechPresetLoader` (entire class + file) | `simulation/systems/tech_preset_loader.py` | 203 | SIM |
| `GroupTargetCoordinator` (entire class + file) | `ai/group_target_coordinator.py` | 124 | FND |
| Deprecated static methods | `simulation/components/modifier_manager.py` | 109 | SIM |
| `create_brick` / `create_interceptor` | `simulation/designs.py` | 68 | SIM |
| Deprecated static methods | `simulation/components/ability_manager.py` | 52 | SIM |
| `ModifierLogic` deprecated wrapper | `ui/screens/builder/modifier_logic.py` | 52 | UI |
| `apply_separation` (never called) | `ai/spatial_behaviors/base.py` | 39 | FND |
| `calculate_stat_multipliers` | `simulation/components/modifiers.py` | 26 | SIM |
| `create_spatial_behavior` factory | `ai/spatial_behaviors/__init__.py` | 26 | FND |
| `_extract_weapon_summaries` | `simulation/battle_runner.py` | 25 | SIM |
| `is_component_health` + `IComponentHealth` | `ai/protocols.py` | 25 | FND |
| `_show_coming_soon` | `ui/screens/strategy_screen.py` | 15 | UI |
| 8 dead imports across 8 files | 8 files | ~7 | All |

---

## 4. Duplication Clusters

From cross-shard duplication analysis: **52 findings** across all layers.

### By Severity

| Severity | Count | Estimated LOC Savings |
|----------|-------|-----------------------|
| Critical | 8 | ~1,200 |
| Major | 19 | ~770 |
| Minor | 16 | ~140 |
| Info | 9 | ~160 (long-term) |
| **Total** | **52** | **~2,270** |

### Top Critical Duplications

1. **DUP-X-004 — ModifierManager static/instance duplication** (SIM, ~160 LOC): 6 methods duplicated as static+instance versions from Task 1.3 migration. Confirmed by both cross-shard and in-shard agents.

2. **DUP-X-002 — PlanetListWindow / StarListWindow near-twin classes** (UI, ~300 LOC): Two major UI windows share 90%+ structural similarity including update(), process_event(), presets, columns, filters. Also confirmed by cross-agent finding DUP-X-008 of PlanetDataSource/StarDataSource near-twins (105 LOC additional).

3. **DUP-X-001 — Target editor class family** (UI, ~200 LOC): 4 target editors share 80%+ code with no base class. Template Method pattern missing.

4. **DUP-X-005 — SuperweaponCommandHandlers** (STR, ~200 LOC): 8 handlers across two families repeating identical structure. Parameterized base class needed.

5. **DUP-X-006 — StrategyClickDispatcher** (UI, ~90 LOC): 8 identical click handlers dispatchable via dict lookup.

6. **DUP-X-003 — Race config resolution** (UI→STR, ~80 LOC): 4 different implementations across UI and Strategy layers.

7. **DUP-X-008 — PlanetDataSource / StarDataSource near-twins** (UI, ~105 LOC): 30 LOC exact duplicate `_extract_value()` plus shared structure.

8. **DUP-X-009 — PlanetListFilterManager / StarListFilterManager near-twins** (UI, ~70 LOC): File header admits "Mirrors PlanetListFilterManager."

**Clone detector validation:** 29 of 49 clusters confirmed genuine. 20 downrated as legitimate pattern variation.

---

## 5. Complexity Hotspots

From `raw/radon.json`: **287 functions with CC >= 11**. Top 20 by complexity:

| CC | Function | Location | Layer |
|----|----------|----------|-------|
| 52 | `handle` (RaceSetupInputHandler) | `ui/screens/race_setup/input_handler.py:30` | UI |
| 47 | `_aggregate` | `strategy/services/system_effects_collector.py:228` | STR |
| 37 | `_handle_button` (BattleSetupInputHandler) | `ui/screens/battle_setup/input_handler.py:44` | UI |
| 31 | `set_items` (SystemTreePanel) | `ui/panels/system_tree_panel.py:191` | UI |
| 31 | `process_event` (PlanetListWindow) | `ui/screens/planet_list_window.py:257` | UI |
| 31 | `build` | `ui/screens/battle_setup/panels/center_panel.py:14` | UI |
| 28 | `apply_planet_list_state` | `ui/screens/planet_list_presets.py:113` | UI |
| 28 | `format_planet_info` | `ui/screens/strategy_detail_fmt.py:147` | UI |
| 28 | `_format_orders` | `ui/screens/strategy_detail_fmt.py:565` | UI |
| 28 | `update_component_list` (BuilderLeftPanel) | `ui/screens/builder/left_panel.py:246` | UI |
| 27 | `_eval_node` | `core/formula_evaluator.py:81` | FND |
| 27 | `_resolve_planets_for_scope` | `strategy/services/strategic_ability_scanner.py:185` | STR |
| 27 | `draw_ship` | `ui/renderer/game_renderer.py:53` | UI |
| 26 | `_recalculate` (FleetAuraManager) | `simulation/combat/fleet_aura_manager.py:293` | SIM |
| 26 | `process_environmental_tick` | `strategy/engine/environmental_hazard_engine.py:71` | STR |
| 26 | `process_transfer` | `strategy/engine/order_processor.py:251` | STR |

### CC >= 20 by Layer

| Layer | Functions with CC >= 20 |
|-------|------------------------|
| UI | 22 |
| Strategy | 8 |
| Simulation | 2 |
| Foundation | 1 |

---

## 6. In-Shard Deep Review Summaries

### UI Layer (292 files, ~323 LOC)
- 18 findings: 0 critical, 4 major, 8 minor, 6 info
- Major: Duplicate `_rebuild_modifier_icons` (42 LOC), resource icon loading in 3 files (60 LOC), selection normalization split (30 LOC), race_summary_panel formatters (80 LOC)
- `system_tree_panel.py` (718 LOC) and `race_summary_panel.py` (716 LOC) exceed 500-LOC ceiling
- `_show_coming_soon` method never called (15 LOC)

### Simulation Layer (89 files, ~1,297 LOC)
- 38 findings: 7 critical, 8 major, 12 minor, 11 info
- Critical: TechPresetLoader dead file (203 LOC), 2 sets of deprecated static methods (161 LOC), 2 dead factory functions (93 LOC), 2 dead calculation functions (51 LOC)
- Major: Stabilizer/modifier/environmental ability classes with ~85% structure duplication
- 8 files exceed 500-LOC ceiling (ship.py at 724 LOC, battle_engine.py at 881 LOC, etc.)

### Strategy Layer (194 files, ~447 LOC)
- 11 findings: 0 critical, 2 major, 4 minor, 5 info
- Major: Duplicated `_get_race_config` (25 LOC), 9 engines share identical `_validate_tick_inputs` (60 LOC)
- No true dead code — well-maintained layer
- `command_handlers.py` is an 82-line re-export shim (transitional per PROJ-309)

### Foundation Layer (81 files, ~290 LOC)
- 16 findings: 4 critical, 4 major, 4 minor, 4 info
- Critical: GroupTargetCoordinator (124 LOC), create_spatial_behavior factory (26 LOC), apply_separation (39 LOC), is_component_health + IComponentHealth (25 LOC) — all never imported/called
- Major: Circle-distribution math duplicated in 3 behaviors, find_target/find_secondary_targets share 70% logic, exit dialog button handlers are identical twins, atomic-write pattern duplicated

---

## 7. Shrinkage Scorecard

| Category | Estimated Reclaimable LOC | Effort | Risk |
|----------|--------------------------|--------|------|
| Dead files (SIM, FND) | 395 | Simple | Safe |
| Dead classes (ModifierLogic) | 52 | Simple | Safe |
| Dead functions/params (in-shard) | 316 | Simple | Safe |
| Dead imports (Agent 3) | ~7 | Simple | Safe |
| ModifierManager static removal (+AbilityManager) | 161 | Simple | Safe |
| Duplicate consolidation (cross-shard critical) | 1,200 | Medium-Complex | Needs design |
| Duplicate consolidation (cross-shard major) | 770 | Simple-Medium | Safe |
| Duplicate consolidation (cross-shard minor) | 140 | Simple | Safe |
| In-shard cleanup (UI) | 323 | Low-Medium | Safe |
| In-shard cleanup (SIM) | 813 | Simple-Medium | Safe |
| In-shard cleanup (STR) | 267 | Simple-Medium | Safe |
| In-shard cleanup (FND) | 101 | Simple | Safe |
| **Total (with overlap reduction)** | **~3,770** | | |

Note: Some items appear in both cross-shard and in-shard reports (e.g., ModifierManager statics, race config, circle-distribution math). The total includes a ~15% overlap reduction.

---

## 8. Prioritized Cleanup Plan (Top 15)

| # | ID(s) | Title | LOC | Effort | Layer |
|---|-------|-------|-----|--------|-------|
| 1 | SIM-001 | Delete dead TechPresetLoader file | 203 | Simple | SIM |
| 2 | DUP-X-004 + SIM-002/003 | Delete deprecated static methods (ModifierManager + AbilityManager) | 161 | Simple | SIM |
| 3 | FND-001 | Delete GroupTargetCoordinator dead file | 124 | Simple | FND |
| 4 | DUP-X-006 | StrategyClickDispatcher registry-driven dispatch | 90 | Simple | UI |
| 5 | SIM-005 | Delete dead designs.py factory functions | 68 | Simple | SIM |
| 6 | DUP-X-017 + DEEP-UI-005 | Delete duplicated _rebuild_modifier_icons | 42 | Simple | UI |
| 7 | FND-003 | Delete apply_separation dead code | 39 | Simple | FND |
| 8 | DUP-X-010 | PlanetCommandHandlers single handler | 50 | Simple | STR |
| 9 | DUP-X-012 | Extract RangeFilterFactory | 40 | Simple | UI |
| 10 | DUP-X-011 | Extract ColumnToggleSection widget | 30 | Simple | UI |
| 11 | FND-005 | Extract circle-distribution spatial helper | 18 | Simple | FND |
| 12 | DUP-X-019 | Extract cached JSON loader utility | 30 | Simple | STR |
| 13 | SIM-004/006 | Delete dead calculation functions | 51 | Simple | SIM |
| 14 | Dead imports cleanup | Remove 8 dead imports | ~7 | Simple | All |
| 15 | DUP-X-018 | Event router editor opener consolidation | 50 | Simple | UI |

**Quick wins (items 1-15):** ~1,003 LOC, all Simple effort, no behavioral risk.
**Medium-term:** Target editor base class (200 LOC), superweapon handler parameterization (200 LOC), race config unification (80 LOC).
**Complex:** PlanetListWindow/StarListWindow base class (300 LOC), serialization schema helper (200 LOC).

---

## 9. Trend Comparison

**First full-coverage run** — baseline established:
- Production LOC: 143,262
- Dead code items: 27 (3 files, 1 class, 14 functions, 9 imports)
- Duplication clusters: 29 confirmed (from 49 clone-detected)
- Total findings: 146
- Estimated shrinkable LOC: ~3,770

---

## 10. Appendices

### Raw Tool Outputs
- `raw/loc_baseline.txt` — LOC by section
- `raw/vulture_100.txt` — Dead code at 100% confidence (7 items)
- `raw/vulture_80.txt` — Dead code at 80% confidence (18 items)
- `raw/orphans.txt` — Orphan module detection (641 flagged — tool config issue)
- `raw/dead_deps.txt` — Unreachable files from entry points (197 — mostly non-game/)
- `raw/radon.json` — Cyclomatic complexity (287 hotspots CC >= 11)
- `raw/clones.json` — AST clone detector (49 clusters, 1,056 duplicated LOC)
- `raw/manifest.json` — File inventory + shard definitions

### Agent Reports
- `findings/duplication_cross_shard.md` — Cross-shard duplication analysis (52 findings)
- `findings/deep_review_UI.md` — In-shard deep review: UI Layer (18 findings)
- `findings/deep_review_SIM.md` — In-shard deep review: Simulation Layer (38 findings)
- `findings/deep_review_STR.md` — In-shard deep review: Strategy Layer (11 findings)
- `findings/deep_review_FND.md` — In-shard deep review: Foundation Layer (16 findings)
- `findings/dead_code_validation.md` — Dead code validation (11 confirmed dead)
