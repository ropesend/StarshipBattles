# Cross-Verification Report

## Summary
- **Total CRITICAL findings reviewed:** 19 (from `deep_review.md` Product Decision items + `dead_code_validation.md` Confirmed Dead + Prioritized Cleanup Order items)
- **Confirmed CRITICAL:** 1
- **Downgraded to PRODUCT_DECISION:** 18
- **Total safe-deletion LOC:** 216

---

## Critical Finding Verification

| Finding ID | Symbol | Test refs? | Doc refs? | Data refs? | Verdict |
|------------|--------|------------|-----------|------------|---------|
| DCV-001 | `game/ui/orchestration/__init__.py` (1 LOC) | No (zero imports across entire repo) | Yes (`docs/01_ARCHITECTURE.md:207` — "retained package") | No | **PRODUCT_DECISION** — documented architectural placeholder, intentionally retained |
| DCV-002 | `game/ui/screens/setup_screen.py` (292 LOC) | Yes (`test_setup_screen.py`, `test_scene_protocol.py`) | Yes (`docs/01_ARCHITECTURE.md:199,467`, `docs/03_CONVENTIONS.md:17-18`) | No | **PRODUCT_DECISION** — test + doc references; `FleetBattleSetupScreen` alias is documented architecture |
| DCV-003 | `game/ui/screens/setup_data_io.py` (220 LOC) | Yes (`test_setup_data_io.py`, `test_fleet_composition.py`) | No | No | **PRODUCT_DECISION** — test references from 2 test files; `test_fleet_composition.py` imports are independent of setup_screen |
| DCV-004 | `game/ui/screens/setup_renderer.py` (216 LOC) | **No** | **No** | **No** | **CRITICAL** — truly dead. Zero test/doc/data refs. Only consumer is dead `setup_screen.py`. |
| DCV-005 | `game/ui/screens/build_queue_viewmodel.py` (268 LOC) | Yes (`test_build_queue_viewmodel.py`) | Yes (`docs/03_CONVENTIONS.md:46`) | No | **PRODUCT_DECISION** — test + doc references; superseded by `EmpireBuildQueueViewModel` but tests still cover it |
| DCV-006 | `game/ai/spatial_behaviors/` (9 files, 542 LOC) | Yes (`test_spatial_behaviors.py`, `test_anti_clumping.py` — 69 matches) | Yes (`docs/01_ARCHITECTURE.md:184`, `docs/systems/ai_system.md`, `docs/systems/strategy_layer.md`) | No | **PRODUCT_DECISION** — documented planned feature with full test coverage; AI layer architecture reserves this |
| DCV-007 | `game/simulation/components/modifier_introspection.py` (311 LOC) | Yes (`test_modifier_introspection.py` × 2 — 20 imports) | Yes (`docs/guides/modifier_system.md:47`, `docs/guides/component_system.md:239,324`) | No | **PRODUCT_DECISION** — test + doc references; UI summaries and tooltips system documented |
| DCV-008 | `game/simulation/systems/tech_preset_loader.py` (203 LOC) | Yes (`test_tech_preset_loader.py` — 103 matches) | No | No | **PRODUCT_DECISION** — test-only infrastructure; no doc or data refs |
| DCV-009 | `game/strategy/data/design_role.py` (179 LOC) | Yes (`test_design_role.py` — 53 matches; also referenced in registry tests) | Yes (`docs/systems/strategy_layer.md:414`, `docs/systems/satellites.md:300`, `docs/03_CONVENTIONS.md`, `docs/systems/combat_simulation.md`) | Yes (`data/design_roles.json` + 41 `data/designs/*.json` files use `design_role` field) | **PRODUCT_DECISION** — test + doc + data references; `DesignRole` enum values are configured by `data/design_roles.json` |
| DCV-010 | `game/ui/widgets/ui_element_registry.py` (62 LOC) | Yes (`test_ui_element_registry.py` — 17 matches) | No | No | **PRODUCT_DECISION** — test-only infrastructure |
| DCV-011 | `game/simulation/designs.py::create_brick/create_interceptor` (~68 LOC) | Yes (`test_designs.py` imports both) | No | No | **PRODUCT_DECISION** — test-only convenience factory functions |
| DCV-012 | `game/ai/group_target_coordinator.py` (144 LOC) | Yes (`test_group_target_coordinator.py` — 49 matches) | Yes (`docs/01_ARCHITECTURE.md:185`, `docs/systems/ai_system.md`, `docs/systems/strategy_layer.md:455`) | No | **PRODUCT_DECISION** — documented AI coordination feature; full test coverage |
| DCV-013 | `game/strategy/services/mine_group_service.py` (151 LOC) | Yes (`test_mine_group_service.py`, `test_fms_b_e2e.py`, `test_minefield_resolver_no_legacy_substrate.py` — 16 matches) | Yes (`docs/systems/minefields.md:223,326,338`) | No | **PRODUCT_DECISION** — test + doc references; documented mine group operations service |
| DCV-014 | `game/strategy/services/deployment_zone_calculator.py` (107 LOC) | Yes (`test_deployment_zone_calculator.py` — 34 matches) | Yes (`docs/04_SERVICES.md:59,394`, `docs/systems/strategy_layer.md:454`) | No | **PRODUCT_DECISION** — test + doc references; documented BattleRole→position mapping |
| DCV-015 | `game/strategy/services/task_group_suggester.py` (125 LOC) | Yes (`test_task_group_suggester.py` — 10 matches) | Yes (`docs/04_SERVICES.md:90,398`, `docs/systems/strategy_layer.md:456`) | No | **PRODUCT_DECISION** — test + doc references; documented fleet hierarchy auto-suggestion |
| DCV-016 | `game/strategy/facade/dto/fleet_hierarchy_dto.py` (104 LOC) | Yes (`test_fleet_hierarchy_dto.py` — 5 matches) | Yes (`docs/systems/strategy_layer.md:331`) | No | **PRODUCT_DECISION** — test + doc references; documented DTO layer |
| DCV-017 | `game/ui/widgets/panel_factory.py` (46 LOC) | Yes (`test_panel_factory.py` — 5 imports from `game.ui.widgets.panel_factory`) | Yes (`docs/02_PATTERNS.md:411` — Pattern #15 Factory example) | No | **PRODUCT_DECISION** — test + doc references; documented pattern example |
| DCV-018 | `container_view_from_resource_storage/cargo_storage/vehicle_bay` in `container.py` (~72 LOC) | Yes (`test_container_ability.py` — 11 matches) | No | No | **PRODUCT_DECISION** — test-only; re-exported in `__init__.py`; awaiting ContainerAbility rollout completion |
| DCV-019 | `BattleService.add_ship/remove_ship/start_battle` (~115 LOC) | Yes (`test_battle_service.py` — 6 matches) | No | No | **PRODUCT_DECISION** — test-only legacy API; superseded by `adopt_started_engine` flow but tests still cover |

---

## Downgraded to Product Decision

Items that should **NOT** be deleted because tests, docs, or data reference them:

| # | Item | LOC | Evidence |
|---|------|-----|----------|
| 1 | `game/ui/orchestration/__init__.py` | 1 | `docs/01_ARCHITECTURE.md:207` reserves as "retained package" — intentional architectural placeholder |
| 2 | `game/ui/screens/setup_screen.py` | 292 | 5 test imports + docs reference `BattleSetupScreen` alias as canonical name |
| 3 | `game/ui/screens/setup_data_io.py` | 220 | 58 test refs across 2 test files; `test_fleet_composition.py` imports independently |
| 4 | `game/ui/screens/build_queue_viewmodel.py` | 268 | `test_build_queue_viewmodel.py` + `docs/03_CONVENTIONS.md` naming convention |
| 5 | `game/ai/spatial_behaviors/` (9 files) | 542 | 69 test refs + 3 doc files (`01_ARCHITECTURE.md`, `ai_system.md`, `strategy_layer.md`) |
| 6 | `game/simulation/components/modifier_introspection.py` | 311 | 20 test imports + 2 doc files (`modifier_system.md`, `component_system.md`) |
| 7 | `game/simulation/systems/tech_preset_loader.py` | 203 | 103 test refs — test-only tech preset infrastructure |
| 8 | `game/strategy/data/design_role.py` | 179 | 53 test refs + 5 doc files + `data/design_roles.json` + 41 design files |
| 9 | `game/ui/widgets/ui_element_registry.py` | 62 | 17 test refs — test-only UI infrastructure |
| 10 | `game/simulation/designs.py::create_brick/create_interceptor` | 68 | `test_designs.py` imports — test-only factory functions |
| 11 | `game/ai/group_target_coordinator.py` | 144 | 49 test refs + 4 doc references — documented AI coordination feature |
| 12 | `game/strategy/services/mine_group_service.py` | 151 | 16 test refs across 3 files + `docs/systems/minefields.md` |
| 13 | `game/strategy/services/deployment_zone_calculator.py` | 107 | 34 test refs + 3 doc references |
| 14 | `game/strategy/services/task_group_suggester.py` | 125 | 10 test refs + 3 doc references |
| 15 | `game/strategy/facade/dto/fleet_hierarchy_dto.py` | 104 | 5 test refs + `docs/systems/strategy_layer.md` |
| 16 | `game/ui/widgets/panel_factory.py` | 46 | 5 test imports + `docs/02_PATTERNS.md` Pattern #15 |
| 17 | `container_view_from_*` helpers in `container.py` | 72 | 11 test refs — test-only ContainerAbility parity helpers |
| 18 | `BattleService.add_ship/remove_ship/start_battle` | 115 | 6 test refs — test-only legacy API surface |

---

## Confirmed Safe Deletions

Items with **zero** references in tests, docs, or data — truly dead code:

| # | File | LOC | Evidence |
|---|------|-----|----------|
| 1 | `game/ui/screens/setup_renderer.py` | 216 | **Zero test imports.** Zero doc mentions. Zero data references. Only consumer is `setup_screen.py` (which itself has zero production callers). The replacement `battle_setup/` package handles rendering. |

**Total safe-deletion LOC:** 216

---

## Methodology Notes

- **CRITICAL** = zero test refs AND zero doc refs AND zero data refs — no trace of intended use.
- **PRODUCT_DECISION** = at least one test, doc, or data reference exists. Deletion would orphan test infrastructure, break documented architecture, or remove configured data. These require an explicit product decision before deletion.
- `data/design_roles.json` and 41 `data/designs/*.json` files contain `design_role` field values that `design_role.py::DesignRole` enum represents — this qualifies as data infrastructure.
- `docs/01_ARCHITECTURE.md:207` explicitly calls `orchestration/` a "retained package" — this is an intentional architectural reservation, not dead code.
- `setup_data_io.py` is imported by `tests/unit/builder/test_fleet_composition.py` which is NOT a setup_screen test — it has independent test value.
- `conftest.py` and `qa_launcher.py` are excluded from verification as non-production tooling (false signals in the dead-dependency analysis).

### Items NOT in scope (non-production)

| File | Reason |
|------|--------|
| `conftest.py` (~250 LOC) | pytest infrastructure; auto-discovered by test runner. Always live. |
| `qa_launcher.py` (~260 LOC) | Root-level QA observer launcher script; not production code. |

---

## Combined Cleanup Recommendation

1. **Immediate — delete `setup_renderer.py`** (216 LOC). Zero risk.
2. **Product decision needed** for 18 items totaling ~2,874 production LOC. These are wired into tests, docs, or data but have zero production callers. Options per-item: (a) wire into production, (b) keep as test-only infrastructure, or (c) delete and migrate/remove tests and docs.
3. **Doc update needed** for 13 items with current doc references (see DCV-001,002,005,006,007,009,012,013,014,015,016,017). If any are deleted, corresponding docs must be updated.
