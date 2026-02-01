# PROJ-44: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Analysis of 35+ code quality issues from `findings_02_code_quality_god_classes.md`:

### God Classes Identified (8 total)
| Class | File | LOC | Primary Issues |
|-------|------|-----|----------------|
| RaceSetupScreen | `game/ui/screens/race_setup_screen.py` | 1231 | 5 tabs, multiple galleries, validation |
| FormationEditor | `game/ui/screens/formation_editor.py` | 1103 | UI/data coupling, state machine |
| BuilderSceneGUI | `game/ui/screens/builder/main.py` | 1100 | Feature envy, cross-layer deps |
| FleetReportWindow | `game/ui/screens/fleet_report_window.py` | 1034 | Virtual scrolling, image processing |
| BattleController | `game/simulation/battle_controller.py` | 889 | 4 battle modes, 40+ methods |
| Component | `game/simulation/components/component.py` | 878 | 40+ methods, abilities/modifiers/stats |
| Ship | `game/simulation/entities/ship.py` | 834 | Components, layers, stats, combat |
| ShipCombatEngine | `game/simulation/entities/ship_combat_engine.py` | 655 | Targeting, firing, damage |

### Test Baseline
- **5199 tests passing**, 3 skipped
- **28291 warnings** (mostly deprecation warnings for registry access)
- Good coverage on BattleController (100 tests), Component (22 tests), ShipCombatEngine (22 tests)
- Partial coverage on UI screens (validation logic only for most)

---

## Swarm Findings Summary

### Architecture Analysis

**Dependency Graph - Most Dependent Modules:**
1. `component.py` - 200+ incoming dependencies (CRITICAL)
2. `ship.py` - 150+ incoming dependencies (CRITICAL)
3. `battle_controller.py` - 25+ incoming dependencies

**Layer Violations Identified:**
- BuilderSceneGUI directly imports Ship, Component, VEHICLE_CLASSES, VALIDATOR
- BuilderSceneGUI directly manipulates ship.layers dict (13+ locations)
- BuilderSceneGUI clears registries directly (lines 859-869)

**Feature Envy (AR-03) in BuilderSceneGUI:**
- Line 90-91: Direct Ship creation
- Line 569: Direct VALIDATOR access
- Lines 277-280, 454, 498, 518, 545, 563, 630, 653, 1068: Direct layer dict access
- Lines 859-862, 972: Registry manipulation

### Key Patterns to Reuse

- **Service Pattern**: `BattleService` - Result wrappers, private state, error handling
- **Manager Pattern**: `RetreatManager` - State tracking, callbacks, query methods
- **Mixin Pattern**: `ShipPhysicsMixin` - Clear requirements, focused responsibility
- **Panel Extraction**: `RaceEnvironmentPanel` - `_create_content()`, `update_config()`, `set_from_config()`
- **Calculator Pattern**: `ShipStatsCalculator` - Multi-phase computation, stateless
- **DI Container**: `GameRegistries` - Frozen dataclass, multiple registries
- **Protocol Pattern**: `IRegistryProvider` - @runtime_checkable for type safety

### Dependencies & Risks

1. **State Corruption in Component.recalculate_stats()** - Multi-phase method can fail mid-execution leaving partial state
   - Mitigation: Consider transaction pattern, snapshot before changes

2. **Modification During Iteration in Ship** - `iter_components()` iterates live dict
   - Mitigation: Create snapshot copies in iteration methods

3. **Registry Stale References** - Module-level MODIFIER_REGISTRY can become stale after clear()
   - Mitigation: Use dependency injection, don't hold module-level refs

4. **Damage Threshold Conflict (CQ-018)** - 50% in simulation vs 30% in strategy
   - Resolution: Unify to 50% everywhere per user decision

### Opportunities Discovered

1. **Existing DI infrastructure** - GameRegistries and IRegistryProvider already exist
2. **Partial decomposition done** - Ship has mixins, RaceSetupScreen has extracted panels
3. **Good test coverage** - 5199 tests provide safety net for refactoring
4. **Existing patterns** - Services, managers, calculators can be followed

---

## Risk-Based Refactoring Order

Based on dependency analysis, refactoring order minimizes ripple effects:

| Priority | Target | Rationale |
|----------|--------|-----------|
| 1 | Quick Wins (DRY, constants) | Low risk, builds momentum |
| 2 | RegistryManager service | Reduces global state hazards |
| 3 | Ship helper methods | Reduces BuilderSceneGUI coupling |
| 4 | Component decomposition | Core simulation, high dependency count |
| 5 | ShipCombatEngine decomposition | Combat isolation |
| 6 | BattleController handlers | Strategy pattern for modes |
| 7 | UI god classes | Final cleanup, depends on simulation stability |
| 8-9 | Long methods, minor cleanup | Lower priority |

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

**Key Decisions Made During Planning:**
1. **Approach**: Risk-based (most coupled first) vs complexity-based
2. **PROJ-12**: Fresh start, not reviewing archived project
3. **Damage Threshold**: Unify to 50% everywhere (Option A)
