# Code Review Report: Self-Contained Systems Analysis

## Metadata
- **Date:** 2026-01-27
- **Type:** General Review
- **Scope:** Entire codebase - Identify self-contained systems for parallel development
- **Agents Used:** 7 (Core Foundation, Physics Engine, Simulation/Battle, Strategy Mode, AI System, Research System, UI/Screens)

---

## Executive Summary

- **Total Findings:** 21
- **Critical:** 7 | **Major:** 10 | **Minor:** 4 | **Info:** 0
- **Overall Assessment:** The codebase has clear system boundaries enabling parallel development, but each system has at least one significant maintenance/extensibility issue requiring attention.

---

## Systems Overview

| System | Location | Isolation | Largest Issue | Severity |
|--------|----------|-----------|---------------|----------|
| Core Foundation | `game/core/` | Very High | Registry singleton pattern | Critical |
| Physics Engine | `game/engine/` | Very High | Physics constants duplication | Critical |
| Simulation/Battle | `game/simulation/` | High | Bidirectional Ship coupling | Critical |
| Strategy Mode | `game/strategy/` | High | Cross-layer import violation | Critical |
| AI System | `game/ai/` | Very High | Duplicate behavior implementations | Critical |
| Research System | `game/research/` | Very High | State mutation on reset | Critical |
| UI/Screens | `game/ui/` | Medium | Direct entity mutation | Critical |

---

## Priority Findings (Top 7 - One Per System)

### 1. CRITICAL: Direct Mutation of Simulation Entities by UI Screens
**ID:** UI-01
**System:** UI/Screens
**Location:** `game/ui/screens/builder/main.py`, `formation_editor.py`, `race_setup_screen.py`, `fleet_report_window.py`
**Issue:** UI screens directly instantiate, hold references to, and mutate simulation entities. BuilderSceneGUI (1,091 lines), RaceSetupScreen (1,227 lines), FormationEditor (1,055 lines) all directly manipulate Ship objects.
**Impact:** Cannot test UI in isolation, no undo/redo capability, domain changes cascade to UI, violates separation of concerns.
**Recommendation:** Introduce ViewModel/Presentation Model layer between UI and domain entities.
**Effort:** Complex (2-3 weeks)

---

### 2. CRITICAL: Bidirectional Coupling Between Ship and BattleController/BattleEngine
**ID:** SIM-01
**System:** Simulation/Battle
**Location:** `game/simulation/entities/ship.py`, `battle_controller.py`, `systems/battle_engine.py`
**Issue:** Ship has circular dependencies with BattleController and BattleEngine. Ship manages targeting state while BattleController manages retreat; BattleEngine mutates ship properties while Ship.update() requires combat context from BattleEngine.
**Impact:** Cannot test Ship in isolation, ships can't be reused across battle contexts, adding battle modes is fragile.
**Recommendation:** Introduce BattleShipAdapter pattern to decouple Ship from battle orchestration.
**Effort:** Complex (3-5 days)

---

### 3. CRITICAL: Direct Simulation Layer Import Violates Architectural Boundaries
**ID:** STRAT-01
**System:** Strategy Mode
**Location:** `game/strategy/systems/design_library.py:14`
**Issue:** DesignLibrary imports `Ship` from simulation layer directly. The `load_design()` method exists to support Ship Builder UI (simulation layer concern) but was placed in strategy layer.
**Impact:** Strategy layer cannot be tested independently, changes to Ship break strategy layer, violates clean architecture.
**Recommendation:** Remove `load_design()` from DesignLibrary, move Ship loading to simulation layer.
**Effort:** Medium (2-3 days)

---

### 4. CRITICAL: Duplicate Behavior and Controller Implementations
**ID:** AI-01
**System:** AI System
**Location:** `game/ai/behaviors.py` vs `game/ai/core/behaviors.py`, `game/ai/controller.py` vs `game/ai/core/system.py`
**Issue:** Two complete, near-identical implementations exist. Primary (active) in `game/ai/` and secondary (dead code) in `game/ai/core/`. ~1,000+ lines of unreachable code.
**Impact:** Maintenance nightmare (bug fixes need replication), confusion about which to extend, tests may validate wrong implementation.
**Recommendation:** Delete `game/ai/core/behaviors.py` and duplicates from `game/ai/core/system.py`.
**Effort:** Medium (1-2 hours)

---

### 5. CRITICAL: Singleton Anti-Pattern Creates Systemic Testability Hazards
**ID:** CORE-01
**System:** Core Foundation
**Location:** `game/core/registry.py`, `logger.py`, `profiling.py`, `screenshot_manager.py`
**Issue:** 268 direct `RegistryManager.instance()` calls, 191 calls to `get_component_registry()`. Services are untestable without full global state. conftest.py must reset 7+ singletons per test.
**Impact:** Tests cannot run in parallel, adding registry types requires modifying singleton AND all fixtures.
**Recommendation:** Introduce constructor-based dependency injection (phased approach).
**Effort:** Complex (phased)

---

### 6. CRITICAL: Physics Constants Duplication - Multiple Sources of Truth
**ID:** PHYS-01
**System:** Physics Engine
**Location:** `game/simulation/physics_constants.py` vs `game/simulation/systems/stats.py:243-251`
**Issue:** K_SPEED, K_THRUST, K_TURN defined in physics_constants.py as "Single Source of Truth" but stats.py hardcodes duplicate values.
**Impact:** If physics constants need tuning, stats.py duplicates could go stale causing inconsistent ship behavior.
**Recommendation:** stats.py should import from physics_constants.py instead of hardcoding.
**Effort:** Simple (15 minutes)

---

### 7. CRITICAL: Control Panel State Mutation on Reset
**ID:** RES-01
**System:** Research System
**Location:** `game/research/ui/research_scene.py:343-349`
**Issue:** Reset flow directly assigns `self.control_panel.tracker = self.tracker`, bypassing constructor initialization.
**Impact:** Adding initialization logic requires updates in multiple locations, state assumptions are violated.
**Recommendation:** Create proper `reset()` method in ResearchControlPanel.
**Effort:** Simple

---

## Findings by System

### Core Foundation (4 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| CORE-01 | Critical | Singleton anti-pattern | Complex |
| CORE-02 | Major | Logger module-level instantiation | Simple |
| CORE-03 | Major | No abstraction between services and registries | Medium |
| CORE-04 | Minor | Inconsistent singleton reset patterns | Simple |

### Physics Engine (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| PHYS-01 | Critical | Physics constants duplication | Simple |
| PHYS-02 | Major | Weak type coupling in CollisionSystem | Medium |
| PHYS-03 | Minor | Hardcoded beam visualization color | Simple |

### Simulation/Battle (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| SIM-01 | Critical | Bidirectional Ship coupling | Complex |
| SIM-02 | Major | Ship.update() dispatcher without strategy | Medium |
| SIM-03 | Major | BattleController handles too many concerns | Medium |

### Strategy Mode (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| STRAT-01 | Critical | Cross-layer import violation | Medium |
| STRAT-02 | Major | Service importing from simulation | Medium |
| STRAT-03 | Minor | TYPE_CHECKING imports mask coupling | Simple |

### AI System (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| AI-01 | Critical | Duplicate behavior implementations | Medium |
| AI-02 | Major | Incomplete interface in behaviors | Simple |
| AI-03 | Minor | Inconsistent TargetEvaluator usage | Simple |

### Research System (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| RES-01 | Critical | Control panel state mutation on reset | Simple |
| RES-02 | Major | Depth cache not invalidated | Simple |
| RES-03 | Minor | Tightly coupled status logic | Medium |

### UI/Screens (3 findings)
| ID | Severity | Title | Effort |
|----|----------|-------|--------|
| UI-01 | Critical | Direct entity mutation by screens | Complex |
| UI-02 | Major | Bloated screen classes (1000+ LOC) | Complex |
| UI-03 | Major | Implicit singleton dependencies | Simple |

---

## Quick Wins (Low Effort, High Impact)

1. **PHYS-01** - Fix physics constants import in stats.py (15 minutes)
2. **AI-01** - Delete duplicate AI implementations (~700 lines of dead code, 1-2 hours)
3. **RES-01** - Extract reset method in ResearchControlPanel (30 minutes)
4. **UI-03** - Pass singletons as constructor dependencies (4 hours)

---

## Parallel Development Safety

**Safe for parallel work (Very High Isolation):**
- Research System - completely self-contained
- AI System - only imports core modules
- Physics Engine - leaf layer with no outbound dependencies
- Core Foundation - leaf modules (but changes affect everyone)

**Requires coordination:**
- UI/Screens <-> Simulation - direct Ship imports create coupling
- Strategy <-> Simulation - DesignLibrary imports Ship

---

## Agent Reports
- [Core Foundation Report](findings/core_foundation_report.md)
- [Physics Engine Report](findings/physics_engine_report.md)
- [Simulation/Battle Report](findings/simulation_battle_report.md)
- [Strategy Mode Report](findings/strategy_mode_report.md)
- [AI System Report](findings/ai_system_report.md)
- [Research System Report](findings/research_system_report.md)
- [UI/Screens Report](findings/ui_screens_report.md)

---
*Report generated: 2026-01-27*
