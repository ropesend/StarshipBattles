# Large File Splitting Plan

## Executive Summary

This document provides a comprehensive plan for splitting 14 files exceeding 500 lines. Each file has been analyzed for cohesive modules, dependencies, and extraction priorities.

**Total files analyzed:** 14
**Total lines across all files:** 10,342
**Estimated reduction in largest file:** 60-75%

---

## Priority Matrix

| Priority | File | Lines | Recommended Splits | Effort | Risk |
|----------|------|-------|-------------------|--------|------|
| **HIGH** | strategy_scene.py | 1,568 | 6 modules | High | Medium |
| **HIGH** | abilities.py | 780 | 5 modules (package) | Medium | Low |
| **HIGH** | controller.py | 668 | 3 modules | Medium | Low |
| **MEDIUM** | planet_list_window.py | 991 | 4 modules | Medium | Medium |
| **MEDIUM** | ship.py | 785 | 3 modules | Medium | Medium |
| **MEDIUM** | battle_panels.py | 694 | 3 modules | Medium | Low |
| **MEDIUM** | ship_stats.py | 678 | 4 modules | High | Medium |
| **MEDIUM** | component.py | 671 | 4 modules | High | High |
| **LOW** | builder_screen.py | 809 | 5 modules | Medium | Low |
| **LOW** | strategy_screen.py | 786 | 5 modules | Medium | Medium |
| **LOW** | setup_screen.py | 668 | 3 modules | Low | Low |
| **LOW** | app.py | 601 | 5 modules | Medium | Medium |
| **LOW** | planet_gen.py | 516 | 4 modules | Low | Low |
| **LOW** | builder_viewmodel.py | 511 | 3 modules | Low | Low |

---

## Detailed Plans by File

### 1. strategy_scene.py (1,568 lines) - HIGHEST PRIORITY

**Current:** Single `StrategyScene` class handling everything

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `strategy_renderer.py` | ~580 | All `_draw_*` methods, rendering coordinator |
| `fleet_movement.py` | ~130 | Fleet commands, pathfinding, hex navigation |
| `colonization_system.py` | ~175 | Colonization logic (fix duplicate at line 902) |
| `camera_navigator.py` | ~90 | Camera focus, zoom_to_galaxy/system |
| `input_handler.py` | ~180 | Event routing, handle_click, handle_event |
| `strategy_scene.py` | ~413 | Coordinator + state management |

**Key Issues:**
- Duplicate `request_colonize_order` method (lines 147-153 vs 902-924)
- Heavy `self.camera`, `self.ui`, `self.session` coupling
- `self.selected_fleet` state shared across modules

**Extraction Order:** Renderer → Camera Nav → Fleet Ops → Colonization → Input

---

### 2. abilities.py (780 lines) - HIGH PRIORITY

**Current:** 22 ability classes + registry in single file

**Recommended Structure (Package):**

```
abilities/
├── __init__.py          (exports + ABILITY_REGISTRY)
├── base.py              (~70 lines - Ability base class)
├── resources.py         (~130 lines - ResourceConsumption/Storage/Generation)
├── weapons.py           (~277 lines - WeaponAbility + variants)
├── propulsion.py        (~33 lines - CombatPropulsion, ManeuveringThruster)
├── crew.py              (~50 lines - CrewCapacity, LifeSupportCapacity, CrewRequired)
├── defense.py           (~70 lines - Shields, EmissiveArmor, ToHitDefenseModifier)
└── markers.py           (~25 lines - CommandAndControl, RequiresX, StructuralIntegrity)
```

**Benefits:**
- Very high cohesion within groups
- ABILITY_REGISTRY stays accessible via `__init__.py`
- No circular dependency risk

**Extraction Order:** weapons.py → resources.py → crew.py → propulsion.py → defense.py

---

### 3. controller.py (668 lines) - HIGH PRIORITY

**Current:** StrategyManager + TargetEvaluator + AIController mixed

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `strategy_manager.py` | ~180 | StrategyManager class + load functions |
| `target_evaluator.py` | ~150 | TargetEvaluator + ship stat utilities |
| `controller.py` | ~340 | AIController (reduced) |

**Key Issues:**
- `TargetEvaluator` calls `AIController._stat_*` methods
- Solution: Extract stat helpers to shared `ship_stats.py`

**Extraction Order:** StrategyManager → Ship Stats → TargetEvaluator

---

### 4. planet_list_window.py (991 lines) - MEDIUM PRIORITY

**Current:** Single `PlanetListWindow` class

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `planet_filters.py` | ~180 | Filter UI, state, and logic |
| `planet_column_mgr.py` | ~140 | Column definitions, reordering, visibility |
| `planet_list_renderer.py` | ~150 | Virtual list, row pool, rendering |
| `planet_list_window.py` | ~300 | Main window, coordination, presets |

**Key Issues:**
- Bidirectional state between filters and window
- Scroll offset management tightly coupled

---

### 5. ship.py (785 lines) - MEDIUM PRIORITY

**Current:** Ship class + module functions

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `ship_loader.py` | ~65 | load_vehicle_classes, initialize_ship_data, get_or_create_validator |
| `ship_abilities.py` | ~140 | get_ability_total, sensor/ecm scores, weapon range |
| `ship.py` | ~580 | Ship class (reduced) |

**Already Extracted:** ShipPhysicsMixin, ShipCombatMixin, ShipFormation, ShipSerializer

**Key Issues:**
- Validator singleton pattern
- Layer access patterns throughout

---

### 6. battle_panels.py (694 lines) - MEDIUM PRIORITY

**Current:** 4 panel classes (BattlePanel, ShipStatsPanel, SeekerMonitorPanel, BattleControlPanel)

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `ship_renderer_utils.py` | ~150 | Stats rendering, resource bars, weapons list |
| `seeker_renderer_utils.py` | ~50 | Missile telemetry rendering |
| `battle_panels.py` | ~485 | Panel classes (simplified) |

**Key Issue:** `ShipStatsPanel.draw_ship_details()` is 239 lines - needs internal refactoring

---

### 7. ship_stats.py (678 lines) - MEDIUM PRIORITY

**Current:** Single `ShipStatsCalculator` class with 326-line `calculate()` method

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `physics_calculator.py` | ~50 | Physics & mobility calculations |
| `combat_profile.py` | ~70 | Defense/offense stat calculations |
| `endurance_analyzer.py` | ~150 | Combat endurance (already a method) |
| `ability_aggregator.py` | ~130 | Ability totals calculation |
| `ship_stats.py` | ~280 | Calculator orchestrator |

**Key Issues:**
- 8-step calculation pipeline with ordering dependencies
- Circular import risk with ability system

---

### 8. component.py (671 lines) - MEDIUM PRIORITY (HIGH COMPLEXITY)

**Current:** Component class + enums + loaders + factories

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `component_constants.py` | ~20 | ComponentStatus, LayerType enums |
| `component_loader.py` | ~110 | load_components, load_modifiers, factories |
| `modifier_system.py` | ~75 | Modifier, ApplicationModifier, add/remove logic |
| `component.py` | ~460 | Component class (reduced) |

**Key Issues:**
- Modifier class duplicate (also in modifiers.py)
- Heavy ability system coupling
- Stats recalculation pipeline

**Extraction Order:** Enums → Loader → Modifier System → Component class

---

### 9. builder_screen.py (809 lines) - LOW PRIORITY

**Current:** `BuilderSceneGUI` with ViewModel pattern already in use

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `builder_ui_factory.py` | ~140 | `_create_ui()` panel initialization |
| `builder_selection_mgr.py` | ~100 | `on_selection_changed()` algorithm |
| `builder_rendering_mgr.py` | ~110 | `update()`/`draw()` with preview logic |
| `builder_persistence.py` | ~80 | Save/load/reload operations |
| `builder_screen.py` | ~380 | Coordinator class |

**Note:** Already uses composition (viewmodel, event_bus, controller)

---

### 10. strategy_screen.py (786 lines) - LOW PRIORITY

**Current:** Single `StrategyInterface` class

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `strategy_sidebar.py` | ~220 | Sidebar panel creation and management |
| `strategy_detail_fmt.py` | ~180 | Detail report formatting (planets, fleets, stars) |
| `strategy_buttons.py` | ~160 | Top bar button layout |
| `strategy_windows.py` | ~110 | Modal window creation |
| `strategy_screen.py` | ~250 | StrategyInterface coordinator |

**Key Issues:**
- Heavy scene reference dependencies
- Cross-panel state management

---

### 11. setup_screen.py (668 lines) - LOW PRIORITY

**Current:** `BattleSetupScreen` + module functions

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `setup_data_io.py` | ~120 | scan_ship_designs, scan_formations, load/save |
| `setup_renderer.py` | ~140 | draw() and draw_team() |
| `setup_input.py` | ~130 | update() event handling |
| `setup_screen.py` | ~150 | Screen coordinator |

---

### 12. app.py (601 lines) - LOW PRIORITY

**Current:** `Game` class with main loop

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `startup.py` | ~70 | Game initialization, pygame setup |
| `scene_manager.py` | ~80 | Scene transitions, start_* methods |
| `exit_dialog.py` | ~65 | Exit confirmation dialog |
| `battle_coordinator.py` | ~135 | Battle update with speed/accumulator logic |
| `app.py` | ~250 | Game class coordinator |

---

### 13. planet_gen.py (516 lines) - LOW PRIORITY

**Current:** `PlanetGenerator` class

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `planet_physics.py` | ~80 | Constants, radius/density calculations |
| `planet_atmosphere.py` | ~110 | Atmosphere generation |
| `planet_naming.py` | ~60 | Roman numerals, naming logic |
| `planet_gen.py` | ~200 | Generator orchestrator |

---

### 14. builder_viewmodel.py (511 lines) - LOW PRIORITY

**Current:** `BuilderViewModel` class

**Recommended Splits:**

| New Module | Lines | Contents |
|------------|-------|----------|
| `builder_selection_mgr.py` | ~105 | Selection logic (shared with builder_screen) |
| `template_modifiers_mgr.py` | ~30 | Template modifier state |
| `ship_operations_facade.py` | ~207 | Service delegation, result caching |
| `builder_viewmodel.py` | ~180 | ViewModel coordinator |

---

## Implementation Strategy

### Phase 1: Quick Wins (1-2 sprints)
Extract modules with lowest coupling and highest benefit:

1. **abilities.py → package** - High impact, low risk
2. **controller.py → strategy_manager.py** - Self-contained singleton
3. **ship.py → ship_loader.py** - Module functions only
4. **component.py → component_constants.py** - Just enums

### Phase 2: Medium Complexity (2-3 sprints)
Tackle files with clear boundaries:

1. **strategy_scene.py → renderer extraction** - Largest file, clear boundary
2. **battle_panels.py → renderer utilities** - Shared drawing logic
3. **planet_list_window.py → filters module** - Self-contained UI

### Phase 3: Deep Refactoring (3-4 sprints)
Address tightly coupled files:

1. **ship_stats.py → calculation pipeline** - Complex ordering
2. **component.py → full split** - High coupling to resolve
3. **app.py → scene management** - Architectural change

---

## Success Criteria

After all splits:
- [ ] No file exceeds 500 lines (with documented exceptions)
- [ ] Each file has single clear responsibility
- [ ] Circular imports eliminated or documented
- [ ] All tests passing
- [ ] Import statements clean and organized

---

## Exceptions (Files That May Exceed 500 Lines)

Some files may legitimately exceed 500 lines after careful analysis:

1. **ship.py** (~580 lines after extraction) - Core entity with many responsibilities
2. **component.py** (~460 lines after extraction) - Core entity with ability system

These should be documented as acceptable exceptions if further splitting would reduce cohesion.

---

## Notes for Implementation

1. **Always run tests** after each extraction
2. **Use `__init__.py` patterns** for package extractions (abilities)
3. **Preserve backward compatibility** via re-exports when needed
4. **Update imports incrementally** - don't batch too many changes
5. **Document circular dependency solutions** when TYPE_CHECKING is used
