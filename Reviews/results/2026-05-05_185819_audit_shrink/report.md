# Code Shrinkage Audit Report

**Date:** 2026-05-05  
**Review Directory:** `Reviews/results/2026-05-05_185819_audit_shrink`  
**Seed:** `shrink-2026-05-05_185819`

---

## 1. Executive Summary

Audit of the Starship Battles production codebase (`game/`, 724 files, ~158K LOC). Deterministic analysis (vulture, radon, clone detector) ran on 100% of production files. LLM deep review covered **Shard 01** (182 files) this cycle; full 4-shard LLM coverage will be achieved over 4 runs via rotating shard review.

- **0 dead code files or classes** detected — vulture found zero genuine dead code candidates (all 7 flags were false positives: 3 `__exit__` protocol params, 4 `TYPE_CHECKING` imports)
- **1 dead method** confirmed: `_find_shield_component_id` in `planet_action_engine.py` (3 LOC, superseded by `_find_ability_component_id`)
- **31 duplication clusters** from clone detector, **8 additional cross-shard duplication patterns** found by LLM agent
- **~530 LOC** of consolidatable duplication identified
- **2 files** exceed the 500 LOC ceiling: `order_processor.py` (910) and `turn_engine.py` (802)
- **47 functions** with cyclomatic complexity >= 20; top offenders are UI event handlers

**Trend:** First run — no prior comparison available.

---

## 2. Coverage Status

| Shard | Files | LOC | Deep Review File | Status |
|-------|-------|-----|-----------------|--------|
| Shard 01 | 182 | 39,696 | `findings/deep_review.md` | Reviewed this run |
| Shard 02 | 187 | 39,614 | — | Pending (next run) |
| Shard 03 | 198 | 39,541 | — | Pending |
| Shard 04 | 157 | 39,617 | — | Pending |

Deterministic coverage: 724/724 files (100%). LLM deep review: 182/724 files (25.1%) this run, 100% over 4 runs.

---

## 3. Dead Code Inventory

### Tier 1: Dead Files
*None confirmed.*

### Tier 2: Dead Classes
*None confirmed.*

### Tier 3: Dead Functions/Methods

| Function | File:Line | LOC | Verified? |
|----------|-----------|-----|-----------|
| `_find_shield_component_id` | `game/strategy/engine/planet_action_engine.py:385-387` | 3 | Verified — zero grep hits in game/, tests/, docs/. Superseded by `_find_ability_component_id` |

### Tier 4: Dead Imports
*None confirmed.* All 4 vulture import flags (`IControllableShip`, `RegionClassifier` ×2, `BuildContext`) are `TYPE_CHECKING`-guarded imports used in type annotations.

---

## 3b. Product Decision Required

| Item | File | LOC | Ref Type | Recommendation |
|------|------|-----|----------|----------------|
| `_handle_right_click` NO-OP stub | `game/ui/screens/workshop_event_router.py:541-544` | 4 | Called from event loop (line 105), returns `False` | Delete if right-click won't be used; keep as placeholder otherwise |

---

## 4. Duplication Clusters

### CRITICAL (1 finding)

**DUP-X-01: Owner-ID validation repeated 7× in planet_command_handlers.py**  
7 handlers duplicate `planet.owner_id != session.active_empire.id` check. `_resolve_fleet` has `empire_id` param but `_resolve_planet` does not.  
**LOC savings:** 14 | **Effort:** Simple

### MAJOR (12 findings)

| ID | Title | Files | LOC Savings | Effort |
|----|-------|-------|-------------|--------|
| DUP-X-02 | "Iterate→extract→read field" pattern in 8+ engines | `planet_action_engine`, `water_engine`, `quality_engine`, `atmosphere_engine`, `harvesting_engine`, etc. | 80 | Medium |
| DUP-X-03 | Workshop dropdown handlers — 5 near-clones | `workshop_event_router.py:441,464,493,505,517` | 50 | Simple |
| DUP-X-04 | Planet/star list `update()` + filters duplication | `planet_list_window.py`, `star_list_window.py` | 60 | Medium |
| DUP-X-05 | Race description bio/socio axis mirrored | `race_description_llm_controller.py:198-307` | 55 | Simple |
| DUP-X-06 | 4 ability-extraction variant methods in planet_action_engine | `planet_action_engine.py:296-340` | 20 | Medium |
| DUP-X-07 | Superweapon handlers don't use `_emit_validated_order` | `superweapon_command_handlers.py:222-353` | 45 | Simple |
| DUP-X-08 | LLM + Image provider factories are structural clones | `services/llm/factory.py`, `ui/services/image/factory.py` | 30 | Medium |
| Cluster 5 | 3 environment target handlers are near-clones | `planet_command_handlers.py:163,184,205` | 30 | Medium |
| Cluster 6 | `_rebuild_modifier_icons` duplicated (identical 40 LOC) | `structure_list_items.py:195,472` | 40 | Medium |
| Cluster 6+8 | Planet/star list windows share update + filter patterns | `planet_list_window.py`, `star_list_window.py` | 50 | Medium |
| Cluster 11 | 4 superweapon mission handlers share pattern | `superweapon_command_handlers.py` | 40 | Medium |
| Cluster 29+30 | Harvesting engine registry lookups + info extraction | `harvesting_engine.py:38-301` | 25 | Simple |

### MINOR (12 findings)
See full `duplication_cross_shard.md` for remaining 12 MINOR items totaling ~120 LOC.

---

## 5. Complexity Hotspots (CC >= 25)

| Function | File | CC | LOC |
|----------|------|-----|-----|
| `RaceSetupInputHandler.handle` | `ui/screens/race_setup/input_handler.py` | F (52) | — |
| `BattleSetupInputHandler._handle_button` | `ui/screens/battle_setup/input_handler.py` | E (37) | — |
| `PlanetListWindow.process_event` | `ui/screens/planet_list_window.py` | E (37) | — |
| `apply_planet_list_state` | `ui/screens/planet_list_window.py` | E (35) | — |
| `SystemTreePanel.set_items` | `ui/panels/system_tree_panel.py` | E (31) | — |
| `build` (battle setup screen) | `ui/screens/battle_setup/screen.py` | E (31) | — |
| `format_planet_info` | `ui/screens/strategy_detail_fmt.py` | D (29) | — |
| `_format_orders` | `ui/screens/strategy_detail_fmt.py` | D (28) | — |
| `BuilderLeftPanel.update_component_list` | `ui/screens/builder/left_panel.py` | D (28) | — |
| `RaceSetupInputHandler` (class) | `ui/screens/race_setup/input_handler.py` | D (28) | — |
| `_eval_node` | `game/core/formula_evaluator.py` | D (27) | 100 |
| `_resolve_planets_for_scope` | `game/strategy/services/strategic_ability_scanner.py` | D (27) | — |
| `draw_ship` | `game/ui/renderer/sprites.py` | D (27) | — |
| `EnvironmentalHazardEngine.process_environmental_tick` | `game/strategy/engine/environmental_hazard_engine.py` | D (26) | — |
| `OrderProcessor.process_transfer` | `game/strategy/engine/order_processor.py` | D (26) | — |
| `StarListWindow.process_event` | `ui/screens/star_list_window.py` | D (25) | — |
| `BuilderLeftPanel.handle_event` | `ui/screens/builder/left_panel.py` | D (25) | — |
| `_build_resource_rows` | `ui/screens/builder/stat_rows_dynamic.py` | D (25) | — |
| `FleetAuraManager._recalculate` | `game/simulation/combat/fleet_aura_manager.py` | D (24) | — |
| `_compute_local_positions` | `game/simulation/combat/formation.py` | D (24) | — |

**Observation:** 15 of the 20 highest-CC functions are in `ui/`, predominantly event handlers and renderers — a common pattern in Pygame applications where input dispatch and drawing naturally accumulate branches.

---

## 6. In-Shard Deep Review Summary (Shard 01)

22 key files reviewed covering strategy engine, UI screens, simulation, and core. Findings:

- **1 CRITICAL** dead code: `_find_shield_component_id` (3 LOC) — zero callers, superseded by `_find_ability_component_id`
- **2 MAJOR** internal duplications: `_get_energy_drain_rate` / `_get_deactivation_time` (30 LOC), `_validate_tick_inputs` boilerplate across 4 engines (15 LOC)
- **2 MAJOR** LOC ceiling violations: `order_processor.py` (910 LOC, 82% over), `turn_engine.py` (802 LOC, 60% over)
- **3 MINOR** items: right-click cancel clones (6 LOC), redundant `has_ability` check (1 LOC), `_handle_right_click` stub
- **Risk assessment:** Low — all findings are well-contained and individually safe to address

Remaining shards (02, 03, 04) scheduled for review in subsequent runs.

---

## 7. Shrinkage Scorecard

| Category | Reclaimable LOC | Effort | Risk |
|----------|----------------|--------|------|
| Dead methods (verified safe) | 3 | Simple | Safe |
| Duplicate consolidation (CRITICAL + MAJOR) | ~450 | Simple-Medium | Needs design |
| Duplicate consolidation (MINOR) | ~80 | Simple | Safe |
| Complexity reduction | — | Medium-High | Needs care |
| In-shard cleanup (Shard 01) | ~40 | Low-Medium | Safe |
| LOC ceiling splits (order_processor + turn_engine) | — | Medium | Structural |
| **Total (safe items)** | **~533** | | |

### 7b. Product Decision Required

| Item | File | LOC | Ref Type | Recommendation |
|------|------|-----|----------|----------------|
| `_handle_right_click` NO-OP stub | `game/ui/screens/workshop_event_router.py:541` | 4 | Production call (line 105) | Delete or keep as placeholder |

---

## 8. Prioritized Cleanup Plan (Top 10)

| Priority | ID | Action | LOC | Effort |
|----------|----|--------|-----|--------|
| 1 | DEEP-01-001 | Delete `_find_shield_component_id` | 3 | Simple |
| 2 | DUP-X-01 | Add `_resolve_player_planet` to `BaseCommandHandler` | 14 | Simple |
| 3 | DUP-X-05 | Unify race description bio/socio axis via field dict | 55 | Simple |
| 4 | DUP-X-03 | Unify workshop dropdown handlers via config dispatch | 50 | Simple |
| 5 | DUP-X-07 | Refactor superweapon handlers to use `_emit_validated_order` | 45 | Simple |
| 6 | Cluster 29+30 | Generic ability data extractor in `harvesting_engine` | 25 | Simple |
| 7 | DUP-X-02 | Add `get_ability_field_from_facility` to `component_inspector` | 80 | Medium |
| 8 | DUP-X-04 | Extract `ListWindowBase` for planet/star list windows | 60 | Medium |
| 9 | DEEP-01-007 | Extract transfer execution from `order_processor.py` (910→~625 LOC) | 285 | Medium |
| 10 | DEEP-01-008 | Extract tick runner + DRY lazy properties in `turn_engine.py` (802→~660 LOC) | 140 | Medium |

---

## 9. Trend Comparison

**First run.** No historical comparison available. This report establishes the baseline for future trend tracking.

---

## 10. Appendices

### Raw Tool Outputs
| Tool | Output | Status |
|------|--------|--------|
| LOC baseline | `raw/loc_baseline.txt` | FAILED (missing tiktoken) |
| Vulture 100% | `raw/vulture_100.txt` | 3 false positives |
| Vulture 80% | `raw/vulture_80.txt` | 7 false positives |
| Radon CC | radon output (captured live) | OK |
| Clone detector | `raw/clones.json` | 31 clusters |
| Manifest | `raw/manifest.json` | 4 shards |

### Agent Reports
- Cross-shard duplication: `findings/duplication_cross_shard.md`
- Deep review (Shard 01): `findings/deep_review.md`
- Dead code validation: `findings/dead_code_validation.md`

### Codebase Signal
Vulture found **zero genuine dead code**. The codebase practices — TDD, consistent `TYPE_CHECKING` guards, registry-based dispatch, strict LOC ceilings, and regular PROJ-driven refactoring — have been effective at preventing dead code accumulation. The major shrinkage opportunity is **duplicate consolidation** (~530 LOC) and **LOC ceiling splits** (~425 LOC extractable), not dead code removal.
