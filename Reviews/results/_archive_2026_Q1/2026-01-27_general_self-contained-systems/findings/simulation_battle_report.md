# Simulation/Battle System Analysis Report

## Summary
- **Total issues found:** 3
- **Critical:** 1, **Major:** 2, **Minor:** 0, **Info:** 0

---

## LARGEST ISSUE

### CRITICAL: Bidirectional Coupling Between Ship and BattleController/BattleEngine

**ID:** SIM-01

**Location:**
- `game/simulation/entities/ship.py:34-140`
- `game/simulation/battle_controller.py:326-467`
- `game/simulation/systems/battle_engine.py:320-446`

**Issue:**

The Ship class has multiple bidirectional dependencies that violate the Single Responsibility Principle:

1. **Ship <-> BattleController circular dependency:**
   - Ship manages targeting state
   - BattleController manages ship retreat tracking
   - Retreat state mutations on ship come from BattleController

2. **Ship <-> BattleEngine circular dependency:**
   - BattleEngine directly mutates ship properties in update
   - Ship.update() requires combat context from BattleEngine
   - Ship holds `just_fired_projectiles` list that BattleEngine iterates

3. **No clear ownership boundaries:**
   - Ships don't own their AI behavior
   - Ships don't own their targeting decisions
   - Ships don't own their retreat mechanics

**Impact on Maintenance/Extensibility:**

1. **Testing becomes complex:** Cannot test Ship in isolation
2. **Reusing Ships is difficult:** Ships can't be moved between battle contexts
3. **Adding battle modes is fragile:** Each new mode needs its own adaptation
4. **Feature additions require changes across multiple files**
5. **State management is implicit**

**Recommendation:**

Introduce a **BattleShipAdapter** pattern:
1. Create adapter that wraps Ship and manages targeting, combat context, retreat state
2. Modify Ship to only own physics state, component state, internal combat mechanics
3. BattleController uses adapter instead of ship directly

**Effort:** Complex (3-5 days)

---

## Secondary Findings

### MAJOR: Ship.update() is a Dispatcher Without Strategy

**ID:** SIM-02

**Location:** `game/simulation/entities/ship.py:244-273`

**Issue:**
Ship.update() orchestrates 5 major subsystems without proper delegation strategy.

**Impact:**
- Coordination complexity with implicit ordering
- Difficult to override or add new update steps
- Must construct full Ship to test one aspect

**Recommendation:** Implement UpdateStrategy pattern with pluggable phases.

**Effort:** Medium (1-2 days)

---

### MAJOR: BattleController Handles Too Many Unrelated Concerns

**ID:** SIM-03

**Location:** `game/simulation/battle_controller.py:1-923`

**Issue:**
BattleController mixes 4 distinct responsibilities:
1. Battle Setup
2. Battle Execution
3. Retreat/Reinforcement Mechanics
4. State Serialization

**Impact:**
- 923 lines makes it difficult to understand
- Cannot test retreat mechanics without full battle setup
- Retreat logic cannot be reused elsewhere

**Recommendation:**
Extract into separate classes: RetreatManager, BattleStateCheckpoint, BattleOrchestrator

**Effort:** Medium (2-3 days)

---

## Assessment

**Overall System Health: Yellow Flag**

**Maintainability:** 5/10
- Multiple god classes (Ship at 793 lines, BattleController at 923 lines)
- Circular dependencies between core classes
- State scattered across multiple objects

**Extensibility:** 4/10
- Adding new battle modes requires touching BattleController
- Adding new ship mechanics requires modifying Ship AND BattleEngine
- No clear plugin points for new behaviors

**Strengths:**
- Good decomposition of combat logic (ShipCombatEngine extracted)
- Clear separation of physics (ShipPhysicsMixin)
- Component-based architecture working well
- PROJ-12 decomposition shows awareness of problem

**Critical Path Forward:**
1. Decouple Ship from BattleController/BattleEngine (SIM-01)
2. Introduce UpdateStrategy pattern (SIM-02)
3. Extract RetreatManager and BattleStateCheckpoint (SIM-03)
