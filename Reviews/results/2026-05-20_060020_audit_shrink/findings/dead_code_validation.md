# Dead Code Validation Report

## Summary
- **Total Candidates Reviewed:** 33 (3 vulture + 12 orphan modules + 18 dead-dependency files)
- **Confirmed Dead:** 1
- **Product Decision Required:** 22 (19 files + 3 vulture → already classified)
- **False Positives:** 10
- **Documentation Discrepancies:** 5

---

## Confirmed Dead Code (no tests, docs, or production references)

### Tier 1: Dead Files (delete entire files)

| File | Source | LOC | Test refs? | Doc refs? | Verified? |
|------|--------|-----|------------|-----------|-----------|
| `game/ui/orchestration/__init__.py` | dead_deps | 1 | No | No | Yes - empty stub, zero imports across entire repo |

---

## False Positives (Not Dead)

| # | Item | Reason It's Actually Used |
|---|------|--------------------------|
| 1 | `exc_tb`, `exc_type`, `exc_val` at `battle_logger.py:35` | `__exit__` parameters required by Python context manager protocol. Not dead. |
| 2 | `RegionClassifier` at `galaxy.py:26` | `if TYPE_CHECKING:` guarded import. Used as string annotation at line 258: `region_classifier: 'Optional[RegionClassifier]'`. At runtime, `RegionClassifier` objects flow through `Galaxy.generate_warp_lanes()` → `GalaxyWarpGenerator`. Class is heavily tested (43 test refs). |
| 3 | `RegionClassifier` at `galaxy_warp_generator.py:16` | `if TYPE_CHECKING:` guarded import. Used in string annotations at lines 193, 207, 279, 291, 317, 330. `RegionClassifier.get_region(system)` called at runtime. Class is heavily tested (43 test refs). |
| 4 | `BuildContext` at `build_queue_controller.py:19` | `if TYPE_CHECKING:` guarded import under `from __future__ import annotations`. Used at line 68: `Union['Planet', 'Fleet', 'BuildContext']`. Protocol class tested for structural compliance (`test_build_context.py`), 15+ test refs. At runtime Planet/Fleet satisfy protocol via structural conformance. |
| 5 | `game/ui/screens/test_lab/details/chrome.py` (244 LOC) | Actively imported by `test_lab/details/panel.py` via `from . import chrome, validation, resource_outcomes, propulsion_outcomes`. Called at runtime for header, metadata, metrics, action buttons, scrollbar drawing. |
| 6 | `game/ui/screens/test_lab/details/propulsion_outcomes.py` (229 LOC) | Imported + used by `panel.py`: `propulsion_outcomes.is_propulsion_test()` and `propulsion_outcomes.draw_propulsion_outcomes()`. |
| 7 | `game/ui/screens/test_lab/details/resource_outcomes.py` (294 LOC) | Imported + used by `panel.py`: `resource_outcomes.is_resource_test()` and `resource_outcomes.draw_resource_outcomes()`. |
| 8 | `game/ui/screens/test_lab/details/validation.py` (253 LOC) | Imported + used by `panel.py`: `validation.draw_validation_results()`. Also used for `run_record.validation_results` attribute. |
| 9 | `game/strategy/data/design_role_registry.py` | Not in dead list — actively imported from `game/ui/screens/builder/right_panel.py`, `game/ui/screens/design_selector_window.py`, and `game/ui/screens/workshop_event_router.py`. |
| 10 | `game/ui/screens/empire_build_queue_viewmodel.py` | Not in dead list — actively imported from `empire_build_queue_window.py`, `empire_build_queue_data_source.py`, `empire_build_queue_sidebar.py`. |

---

## Product Decision Required

Items with zero production code callers but referenced by tests or docs.
Per methodology: do NOT report as dead — downgrade to PRODUCT_DECISION.

| # | Item | File:Line | Production refs | Test refs | Doc refs | LOC | Recommendation |
|---|------|-----------|-----------------|-----------|----------|-----|----------------|
| 1 | `GroupTargetCoordinator` (class) | `game/ai/group_target_coordinator.py` | **0** | 24 imports in `tests/unit/ai/test_group_target_coordinator.py` | 0 | 144 | Investigate why AI pipeline doesn't wire this. Implement or delete. |
| 2 | Spatial behaviors package (9 files) | `game/ai/spatial_behaviors/` | **0** external | 1 file: `tests/unit/ai/spatial_behaviors/test_spatial_behaviors.py` | 0 | ~618 | Full spatial behavior system: `BattleLineBehavior`, `ColumnBehavior`, `EscortBehavior`, `FreeManeuverBehavior`, `PatrolZoneBehavior`, `ScreenBehavior`, `SpatialBehavior` base, `_formation_utils`. Has public `__init__.py` re-exports. Not wired into `game/ai/behaviors.py` or `game/ai/controller.py`. Docs claim AI layer owns spatial_behaviors (01_ARCHITECTURE.md:184). Either wire it into the AI pipeline or delete. |
| 3 | `ModifierIntrospection` (class) | `game/simulation/components/modifier_introspection.py` | **0** | 20 imports across 2 test files | 0 | 311 | Large utility class never called. Investigate if needed for modifier debugging/UI. |
| 4 | `create_brick`, `create_interceptor` | `game/simulation/designs.py` | **0** | `tests/unit/builder/test_designs.py` | 0 | 68 | Test-only convenience factory functions. Should these move to a test utility? |
| 5 | `TechPresetLoader` (class) | `game/simulation/systems/tech_preset_loader.py` | **0** | 30 imports in `test_tech_preset_loader.py` | 0 | 203 | Tech preset loading from disk. Never called in production. Wire up or delete. |
| 6 | `DesignRole` (Enum) | `game/strategy/data/design_role.py` | **0** | `tests/unit/strategy/data/test_design_role.py` (16 imports) | 0 | 179 | Enum class not imported by any production code. Only `ship_instance.py:line ?` comment mentions `DesignRole`. Production uses `DesignRoleRegistry` instead (separate file). Delete or wire. |
| 7 | `FleetHierarchyDTO` classes | `game/strategy/facade/dto/fleet_hierarchy_dto.py` | **0** | 5 imports in `test_fleet_hierarchy_dto.py` | `docs/systems/strategy_layer.md` | 104 | DTO file with `TaskForceInfo`, `SquadronInfo`, `ShipInfoExtended`. Zero production callers. If the facade no longer uses these DTOs, delete. |
| 8 | `DeploymentZoneCalculator` | `game/strategy/services/deployment_zone_calculator.py` | **0** | 12 imports in `test_deployment_zone_calculator.py` | `docs/04_SERVICES.md` | 107 | Battle role → battlefield position mapping. Never called in production. Wire up or delete. |
| 9 | `MineGroupService` | `game/strategy/services/mine_group_service.py` | **0** | 3 test files (`test_mine_group_service.py`, `test_fms_b_e2e.py`, `test_minefield_resolver_no_legacy_substrate.py`) | `docs/systems/minefields.md` | 151 | Player operations on mine groups. Zero production callers. Mine group ops may be going through a different path. |
| 10 | `TaskGroupSuggester` | `game/strategy/services/task_group_suggester.py` | **0** | 8 imports in `test_task_group_suggester.py` | `docs/04_SERVICES.md` | 125 | Fleet hierarchy auto-suggestion. Never called. Wire up or delete. |
| 11 | `BuildQueueViewModel` (class) | `game/ui/screens/build_queue_viewmodel.py` | **0** | `tests/unit/ui/screens/test_build_queue_viewmodel.py` | 0 | 268 | Superseded by `EmpireBuildQueueViewModel` in `empire_build_queue_viewmodel.py`. Old ViewModel kept alive by tests only. Delete if migration is complete. |
| 12 | `BattleSetupScreen` (class) | `game/ui/screens/setup_screen.py` | **0** | `tests/unit/ui/screens/test_setup_screen.py` (5 imports) + `test_scene_protocol.py` | 0 | 292 | Superseded by `FleetBattleSetupScreen` in `game/ui/screens/battle_setup/screen.py`. Screen router imports from `battle_setup.screen`, NOT `setup_screen`. Delete the superseded file. |
| 13 | `setup_data_io.py` (setup Data I/O helpers) | `game/ui/screens/setup_data_io.py` | **0** (only imported by dead `setup_screen.py`) | 0 (tests use `setup_screen.py`) | 0 | 220 | Only consumer is dead `setup_screen.py`. Delete as part of setup_screen cleanup. |
| 14 | `setup_renderer.py` (setup Renderer) | `game/ui/screens/setup_renderer.py` | **0** (only imported by dead `setup_screen.py`) | 0 (tests use `setup_screen.py`) | 0 | 216 | Only consumer is dead `setup_screen.py`. Delete as part of setup_screen cleanup. |
| 15 | `PanelFactory` | `game/ui/widgets/panel_factory.py` | **0** | `tests/unit/ui/widgets/test_panel_factory.py` (5 imports) | `docs/02_PATTERNS.md` Pattern #15 | 46 | Pattern #15 (Factory) mentions this file. If Factory pattern is implemented elsewhere, delete this and update docs. |
| 16 | `UIElementRegistry` | `game/ui/widgets/ui_element_registry.py` | **0** | `tests/unit/ui/widgets/test_ui_element_registry.py` (7 imports) | 0 | 62 | UI element registry never called. Delete if unused. |
| 17 | `qa_launcher.py` (root) | `qa_launcher.py` | **0** (game/ doesn't import) | `tests/unit/tools/test_qa_launcher.py` | `Tools/qa_observer/README.md` | ~260 | Standalone QA observer launcher script. Referenced by `Tools/qa_observer/`. Not a production-code concern. Keep or delete based on whether QA observer is still active. |
| 18 | `conftest.py` (root) | `conftest.py` | **0** (game/ only comments to it) | Pytest auto-discovers it | 0 | ~250 | Root pytest configuration. Detection in dead_deps is a false signal — `conftest.py` is pytest infrastructure, consumed by the test runner, not by production code. Always live. |

---

## Documentation Discrepancies

| Dead Code Item | docs/ File | What docs say | Recommendation |
|----------------|------------|---------------|----------------|
| `deployment_zone_calculator.py` | `docs/04_SERVICES.md` | "deployment_zone_calculator.py — BattleRole -> battlefield positions" | Remove reference if file is deleted; wire up if service is needed. |
| `task_group_suggester.py` | `docs/04_SERVICES.md` | "task_group_suggester.py — Fleet hierarchy auto-suggestion" | Remove reference if file is deleted; wire up if service is needed. |
| `fleet_hierarchy_dto.py` | `docs/systems/strategy_layer.md` | Lists `TaskForceInfo`, `SquadronInfo`, `ShipInfoExtended` from this file | Remove reference if DTOs are deleted. |
| `mine_group_service.py` | `docs/systems/minefields.md` | "Player operations on mine_groups" with file path reference | Remove reference if file is deleted. |
| `panel_factory.py` | `docs/02_PATTERNS.md` Pattern #15 (Factory) | Lists `game/ui/widgets/panel_factory.py` as a factory example alongside `ai_factory.py` and `ship_factory.py` | If `PanelFactory` is deleted, update Pattern #15 to remove the reference or document the replacement. |

---

## Prioritized Cleanup Order

Ordered by safety (dead files first) then by LOC savings:

### Immediate (no risk)
1. **`game/ui/orchestration/__init__.py`** (1 LOC) — CONFIRMED DEAD. Empty stub. Delete immediately.

### Phase 1: Superseded UI code (safe — replacement exists)
2. **`game/ui/screens/setup_screen.py`** (292 LOC) — superseded by `battle_setup/screen.py`
3. **`game/ui/screens/setup_data_io.py`** (220 LOC) — only consumer is dead
4. **`game/ui/screens/setup_renderer.py`** (216 LOC) — only consumer is dead
5. **`game/ui/screens/build_queue_viewmodel.py`** (268 LOC) — superseded by `empire_build_queue_viewmodel.py`

**Subtotal Phase 1:** 996 LOC deletable after test migration

### Phase 2: Unwired services with no docs refs (moderate risk)
6. **`game/ai/spatial_behaviors/`** (9 files, ~618 LOC) — large unwired system
7. **`game/simulation/components/modifier_introspection.py`** (311 LOC) — large utility, never called
8. **`game/simulation/systems/tech_preset_loader.py`** (203 LOC) — tech preset system, never called
9. **`game/strategy/data/design_role.py`** (179 LOC) — enum not wired
10. **`game/ui/widgets/ui_element_registry.py`** (62 LOC) — small utility, never called

**Subtotal Phase 2:** ~1,373 LOC (all test-only, needs confirmation before deleting)

### Phase 3: Services with doc refs (requires doc update coordination)
11. **`game/simulation/designs.py`** (68 LOC) — move to test utilities or delete
12. **`game/ai/group_target_coordinator.py`** (144 LOC) — AI feature, wire or delete
13. **`game/strategy/services/mine_group_service.py`** (151 LOC) — mine group ops
14. **`game/strategy/services/deployment_zone_calculator.py`** (107 LOC) — deployment logic
15. **`game/strategy/services/task_group_suggester.py`** (125 LOC) — fleet hierarchy
16. **`game/strategy/facade/dto/fleet_hierarchy_dto.py`** (104 LOC) — DTOs
17. **`game/ui/widgets/panel_factory.py`** (46 LOC) — docs mention

**Subtotal Phase 3:** 745 LOC (requires doc coordination)

### Non-production tooling
18. **`qa_launcher.py`** (~260 LOC) — root-level script, not production code
19. **`conftest.py`** (~250 LOC) — pytest configuration, always live (false signal)

### Total Deletable LOC (all phases): ~3,114 LOC + 1 file

### Total Production LOC Savings (excluding conftest.py and qa_launcher.py): ~2,604 LOC
