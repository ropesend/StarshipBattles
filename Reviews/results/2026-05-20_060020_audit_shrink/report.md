# Code Shrinkage Audit Report

**Date:** 2026-05-20  
**Review Directory:** `Reviews/results/2026-05-20_060020_audit_shrink`  
**Seed:** `shrink-2026-05-20_060020`

---

## 1. Executive Summary

Audited 846 production files (182,101 LOC) across `game/`. Vulture found zero production dead code (3 false positives — `__exit__` params). The clone detector found 26 near-duplicate clusters (754 LOC); the cross-shard agent found 9 additional findings (+490 LOC). The in-shard deep review of Shard 03 (192 files, ~45K LOC) found zero critical dead code and identified 11 files exceeding the 500-LOC ceiling. Only 1 file (`setup_renderer.py`, 216 LOC) is confirmed safe to delete after cross-verification. All other flagged items are PRODUCT_DECISION — unwired code with test/doc/data references.

- **Deterministic coverage:** 846/846 files, every run  
- **LLM deep-review coverage:** 1 rotating shard per run (Shard 03 this run, 25% cycle progress)  
- **Trend:** First run — no baseline comparison available

---

## 2. Coverage Status

| Shard | Label | Files | LOC | Reviewed | Status |
|-------|-------|-------|-----|----------|--------|
| 01 | Shard 01 | 203 | 45,700 | pending | next run (rotation slot 1) |
| 02 | Shard 02 | 215 | 45,455 | pending | run after next |
| **03** | **Shard 03** | **205** | **45,378** | **deep_review.md** | **Reviewed this run** |
| 04 | Shard 04 | 223 | 45,568 | pending | run 4 |

100% LLM deep-review coverage achieved every 4 runs via manifest shard rotation (01 -> 02 -> 03 -> 04). Current cycle: 25% complete (1 of 4 shards reviewed).

---

## 3. Dead Code Inventory

### Verified Dead Code (Safe to Delete)

After cross-verification against tests, docs, and data:

#### Tier 1: Dead Files

| File | Source | LOC | Test refs? | Doc refs? | Data refs? | Verified? |
|------|--------|-----|------------|-----------|------------|-----------|
| `game/ui/screens/setup_renderer.py` | dead_deps + verification | 216 | No | No | No | Yes |

#### Tiers 2-4: No confirmed dead classes, functions, or imports

**Total Safe Deletion:** 216 LOC (1 file)

### 3b. Product Decision Required

Items with zero production callers but referenced by tests, docs, or data files. NOT counted toward safe-shrinkage totals.

| Item | File | LOC | Ref Type | Recommendation |
|------|------|-----|----------|----------------|
| Spatial behaviors (9 files) | `game/ai/spatial_behaviors/` | 542 | Tests + Docs | Wire into AI or remove |
| ModifierIntrospection | `simulation/components/modifier_introspection.py` | 311 | Tests + Docs | Wire or remove |
| BattleSetupScreen (superseded) | `ui/screens/setup_screen.py` | 292 | Tests + Docs | Delete if migration complete |
| EmpireBuildQueueVm (superseded) | `ui/screens/build_queue_viewmodel.py` | 268 | Tests + Docs | Delete if migration complete |
| setup_data_io.py | `ui/screens/setup_data_io.py` | 220 | Tests | Delete if migration complete |
| TechPresetLoader | `simulation/systems/tech_preset_loader.py` | 203 | Tests | Wire or remove |
| DesignRole enum | `strategy/data/design_role.py` | 179 | Tests+Docs+Data | Wire (42 data files depend on it) |
| MineGroupService | `strategy/services/mine_group_service.py` | 151 | Tests + Docs | Wire or remove |
| GroupTargetCoordinator | `ai/group_target_coordinator.py` | 144 | Tests + Docs | Wire into AI pipeline |
| TaskGroupSuggester | `strategy/services/task_group_suggester.py` | 125 | Tests + Docs | Wire or remove |
| BattleService legacy API | `simulation/services/battle_service.py` | 115 | Tests | Remove after engine migration |
| DeploymentZoneCalculator | `strategy/services/deployment_zone_calculator.py` | 107 | Tests + Docs | Wire or remove |
| FleetHierarchyDTO | `strategy/facade/dto/fleet_hierarchy_dto.py` | 104 | Tests + Docs | Wire or remove |
| ContainerAbility helpers | `simulation/components/abilities/container.py` | 72 | Tests | Wire after rollout |
| create_brick/create_interceptor | `simulation/designs.py` | 68 | Tests | Move to test utils or delete |
| UIElementRegistry | `ui/widgets/ui_element_registry.py` | 62 | Tests | Wire or remove |
| PanelFactory | `ui/widgets/panel_factory.py` | 46 | Tests + Docs | Wire or update docs |
| orchestration/__init__.py | `ui/orchestration/__init__.py` | 1 | Docs | Retained package marker |

**Product Decision Subtotal:** ~2,874 LOC

---

## 4. Duplication Clusters

### Clone Detector Validation: 26/26 confirmed, 0 false positives

#### CRITICAL (6 findings)
| ID | Description | Savable LOC | Effort |
|----|-------------|-------------|--------|
| DUP-X-1 | Unify `_find_ship` into BaseCommandHandler (10 copies) | 50 | Simple |
| DUP-X-2 | Unify `facility_has_ability` across 3 implementations | 30 | Medium |
| DUP-X-3 | Template Method for handler validation pipeline (5 families) | 280 | Complex |
| Cluster 1 | `execute_action_order` across 5 order handlers | 120 | Complex |
| Cluster 4+5 | `_execute_fleet` + `_execute_planet` across 5 handlers | 165 | Complex |
| Cluster 12+21 | `_run_with_issuer` variants (recover + launch) | 170 | Complex |

#### MAJOR (14 findings)
| ID | Description | Savable LOC | Effort |
|----|-------------|-------------|--------|
| DUP-X-4 | Canonical bay_inventory accessor (16 locations) | 30 | Medium |
| DUP-X-5 | Template `_from_dict_payload` for deployed groups | 35 | Simple |
| DUP-X-6 | Centralize warp capability check (9 locations) | 15 | Medium |
| DUP-X-7 | Fleet-ship resolution inline duplicate | 30 | Simple |
| Cluster 2 | Consume SimpleMultiplierAbility for stat_modifiers | 30 | Simple |
| Cluster 3 | Parameterize superweapon designation handlers | 80 | Medium |
| Cluster 6 | Generic selection modal opener | 25 | Simple |
| Cluster 7 | Shared DismissableDialog for UI windows | 14 | Simple |
| Cluster 9 | Shared base cancel() for background calls | 20 | Simple |
| Cluster 10 | Unify hit effect drawing functions | 20 | Simple |
| Cluster 11 | `execute_for_issuer` shared base | 30 | Complex |
| Cluster 19 | Parameterize stat contributor launch functions | 40 | Simple |
| Cluster 25 | Template `_from_dict_payload` all variants | 40 | Simple |
| Cluster 26 | Generic deployed-group finder | 14 | Simple |

---

## 5. Complexity Hotspots (CC >= 35)

| CC | File | Line | Symbol |
|----|------|------|--------|
| 52 | `game/ui/screens/race_setup/input_handler.py` | 30 | RaceSetupInputHandler.handle |
| 37 | `game/ui/screens/planet_list_event_router.py` | 47 | process_event |
| 37 | `game/ui/screens/battle_setup/input_handler.py` | 44 | _handle_button |
| 35 | `game/ui/screens/planet_list_presets.py` | 124 | apply_planet_list_state |
| 35 | `game/ui/screens/strategy_detail_fmt.py` | 147 | format_planet_info |

Top 5 hotspots (CC >= 35) are all UI event handlers — candidates for event-handler decomposition or state-machine refactoring. Full complexity data in `raw/radon.json` (50 functions with CC >= 20).

---

## 6. In-Shard Deep Review Summary (Shard 03)

**Shard:** Shard 03 — 192 files, ~45,378 LOC  
**Coverage:** 192/192 files read (100%)  
**Findings:** 27 (0 Critical, 3 Product Decision, 8 Major, 10 Minor, 6 Info)

### Key Findings
- **11 files exceed 500 LOC ceiling** — `battle_runner.py` (735), `replay_serialization.py` (634), `commands/__init__.py` (629), `tactical_mine_resolver.py` (597), `stat_contributors/registry.py` (570), `ship_stats.py` (559), `simulation_adapter.py` (549), `exceptions.py` (544), `base.py` (535), `vehicle_design_service.py` (516), `planet.py` (504)
- **`_validate_tick_inputs` copy-pasted** across 4+ strategy engines (DEEP-03-004, ~40 LOC)
- **`OrbitalGenerationConfig` has redundant attribute assignments** (DEEP-03-005, ~90 LOC)
- **Triplicate lazy JSON cache pattern** in galaxy generation (DEEP-03-006, ~40 LOC)

### Pending in Rotation
- Shard 04 (223 files) — ahead
- Shard 01 (203 files) — next run  
- Shard 02 (215 files) — run 3

---

## 7. Shrinkage Scorecard

| Category | Reclaimable LOC | Effort | Risk |
|----------|----------------|--------|------|
| **Dead files (verified safe)** | **216** | Simple | Safe |
| Dead classes/functions (verified) | 0 | — | — |
| Dead imports | 0 | — | — |
| Duplicate consolidation (clone detector) | 754 | Medium-High | Needs design |
| Duplicate consolidation (cross-shard) | 490 | Medium-High | Needs design |
| In-shard cleanup (Shard 03) | ~170 | Low-Medium | Safe |
| **Total Safe Items** | **216** | | |
| **Total Including Duplication** | **~1,460** | | |

### 7b. Product Decision Required (NOT counted toward safe totals)

| Item | LOC | Ref Type |
|------|-----|----------|
| spatial_behaviors/ (9 files) | 542 | Tests + Docs |
| modifier_introspection.py | 311 | Tests + Docs |
| setup_screen.py | 292 | Tests + Docs |
| build_queue_viewmodel.py | 268 | Tests + Docs |
| setup_data_io.py | 220 | Tests |
| tech_preset_loader.py | 203 | Tests |
| design_role.py | 179 | Tests+Docs+Data |
| Remaining 11 items | 659 | Tests + Docs |
| **Product Decision Total** | **~2,874** | |

These items inflate shrinkage estimates until product decisions are made. They are separated clearly so the scorecard is actionable without waiting.

---

## 8. Prioritized Cleanup Plan

Top 10 items by impact/effort ratio (verified-safe + high-ROI duplication):

| Priority | ID | Description | Savable LOC | Effort |
|----------|----|-------------|-------------|--------|
| 1 | VERIFY-001 | Delete `setup_renderer.py` | 216 | Simple |
| 2 | DUP-X-1 | Unify `_find_ship` into BaseCommandHandler | 50 | Simple |
| 3 | Cluster 8 | Merge launch_fighters/launch_satellites_in_battle | 35 | Simple |
| 4 | Cluster 2 | Consume SimpleMultiplierAbility | 30 | Simple |
| 5 | DUP-X-5 | Template _from_dict_payload for deployed groups | 35 | Simple |
| 6 | Cluster 9 | Shared base cancel() for background calls | 20 | Simple |
| 7 | Cluster 26 | Generic deployed-group finder | 14 | Simple |
| 8 | DUP-X-9 | Unify ship-to-carried-vehicle converters | 30 | Simple |
| 9 | Cluster 10 | Unify hit effect drawing functions | 20 | Simple |
| 10 | DUP-X-3 | Template Method for handler pipeline | 280 | Complex |

---

## 9. Trend Comparison

**First run** — no baseline data available. The shrink tracker has been initialized with this run's data for future trend comparison.

---

## 10. Appendices

### Raw Instrument Outputs
- `raw/loc_baseline.txt` — LOC by layer (180,938 production Python LOC)
- `raw/vulture_100.txt` — 3 items (all `__exit__` false positives)
- `raw/vulture_80.txt` — 6 items (3 `__exit__` + 3 TYPE_CHECKING imports)
- `raw/orphans.txt` — 13 orphaned modules
- `raw/dead_deps.txt` — 30 potentially unreachable files
- `raw/radon.json` — 50 functions with CC >= 20
- `raw/clones.json` — 26 clone clusters (754 duplicated LOC)
- `raw/manifest.json` — File inventory + shard assignments

### Agent Reports
- `findings/duplication_cross_shard.md` — Cross-Shard Duplication Report (35 findings)
- `findings/deep_review.md` — Deep Review: Shard 03 (27 findings)
- `findings/dead_code_validation.md` — Dead Code Validation (1 dead, 22 product decisions)
- `findings/verification.md` — Cross-Verification Report (1 critical, 18 downgraded)
