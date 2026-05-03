### Summary
- Total issues found: 6
- Critical: 0, Major: 3, Minor: 2, Info: 1

### Findings

#### MAJOR: God Class / Mega-File Pattern
**ID:** CQ-01
**Location:** `game/ui/screens/test_lab_screen.py:1-4703`
**Issue:** File contains 4700+ lines of code, likely mixing UI, logic, and simulation test orchestration.
**Impact:** Extremely difficult to maintain, test, or refactor. High risk of regressions.
**Recommendation:** Decompose into smaller sub-components (e.g., specific test panels, logic handlers).
**Effort:** Complex

#### MAJOR: Excessive File Size in Simulation Tests
**ID:** CQ-02
**Location:** `simulation_tests/scenarios/*.py`
**Issue:** Scenario files (Beam, Propulsion, Resource) are exceptionally large (1500-2700 lines).
**Impact:** Tests become fragile monoliths; hard to read and debug failures.
**Recommendation:** Refactor scenarios into smaller, composable test cases or fixture-driven tests.
**Effort:** Medium

#### MAJOR: Builder UI Complexity
**ID:** CQ-03
**Location:** `game/ui/screens/builder/main.py:1-1047`
**Issue:** Ship Builder UI main file is over 1000 lines.
**Impact:** The Ship Builder is a core feature; complexity here slows down iteration and introduces UI bugs.
**Recommendation:** Extract widgets and state management into separate modules.
**Effort:** Medium

#### MINOR: Large Battle Controller
**ID:** CQ-04
**Location:** `game/simulation/battle_controller.py:1-955`
**Issue:** BattleController is nearing 1000 lines, suggesting it might be taking on too many responsibilities (User Input + Sim Logic).
**Impact:** Coupling of input handling and simulation state.
**Recommendation:** Review responsibilities and extract InputHandlers or PhaseManagers.
**Effort:** Medium

#### MINOR: Ship Entity Complexity
**ID:** CQ-05
**Location:** `game/simulation/entities/ship.py:1-895`
**Issue:** Ship entity class is very large.
**Impact:** Entities should ideally be lightweight composed objects (Entity Component System pattern).
**Recommendation:** Verify if this is a "God Object" or just a component aggregator. Move logic to Systems if possible.
**Effort:** Medium

#### INFO: High Component Count
**ID:** CQ-06
**Location:** `General`
**Issue:** 1096 Python files found.
**Impact:** Large surface area for a single developer.
**Recommendation:** Ensure strict module boundaries to manage mental load.
**Effort:** Simple

### Top 5 Priority Issues
1. Decompose `test_lab_screen.py` (CQ-01)
2. Refactor `simulation_tests` scenarios (CQ-02)
3. Modularize `builder/main.py` (CQ-03)
4. Audit `battle_controller.py` for Separation of Concerns (CQ-04)
5. Review `ship.py` for ECS compliance (CQ-05)
