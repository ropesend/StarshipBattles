# Code Quality Analyst Report

## Summary
- **Total issues found:** 28
- **Critical:** 3, **Major:** 12, **Minor:** 10, **Info:** 3

---

## Findings

### CRITICAL: Security Risk with eval() in Formula System
**ID:** CQ-001
**Location:** `game/simulation/formula_system.py:4-32`
**Issue:** The formula evaluation system uses `eval()` to execute arbitrary formulas. While mitigations are in place (disabled `__builtins__`, whitelisted context), this is inherently risky.
**Impact:** Security vulnerability. Any compromise of data files or future refactoring that accidentally passes user input to this function could lead to arbitrary code execution.
**Recommendation:** Replace `eval()` with a safe expression evaluator library (e.g., `numexpr`, `simpleeval`, or `ast`-based evaluation).
**Effort:** Complex

### CRITICAL: Deeply Nested Control Flow in ship_combat.fire_weapons()
**ID:** CQ-002
**Location:** `game/simulation/entities/ship_combat.py:51-217`
**Issue:** The `fire_weapons()` method contains 5-6 levels of nesting with complex targeting, weapon type switching, and projectile creation logic.
**Impact:** Maintainability blocker. Difficult to unit test individual targeting logic. Bug fixes require understanding entire nested structure.
**Recommendation:** Extract nested logic into helper methods: `_process_hangar_launch()`, `_fire_weapon_ability()`, `_select_target_from_candidates()`, `_create_projectile()`.
**Effort:** Medium

### CRITICAL: God Class - Ship Class Has 50+ Methods and 750+ Lines
**ID:** CQ-003
**Location:** `game/simulation/entities/ship.py:1-762`
**Issue:** The Ship class violates Single Responsibility Principle handling physics, combat, formation, stats, components, serialization, and validation.
**Impact:** Severe maintainability impact. Changes to one aspect require understanding entire class. Testing individual features requires mocking the entire Ship object.
**Recommendation:** Break into focused classes: `ShipComponentManager`, `ShipStatsAggregator`, `ShipCombatEngine`.
**Effort:** Complex

### MAJOR: Excessive Use of getattr() with Fallback Values
**ID:** CQ-004
**Location:** Multiple files (ship.py, ship_combat.py, controller.py) - 20+ instances
**Issue:** Widespread use of `getattr()` with fallback values indicates attributes may not be guaranteed to exist.
**Impact:** Hides missing attribute definitions. Makes code harder to understand. Difficult to catch attribute errors during development.
**Recommendation:** Ensure all Ship attributes are declared in `__init__`, use dataclass-style type hints.
**Effort:** Medium

### MAJOR: Silent Exception Handling (pass statements)
**ID:** CQ-005
**Location:** `game/simulation/systems/battle_engine.py:59,68`, `game/simulation/components/modifier_effects.py:149`, `game/simulation/entities/ship.py:431`
**Issue:** Multiple places silently catch and ignore exceptions with `pass` statements.
**Impact:** Hidden bugs. When something fails, the system continues with fallback values, making root cause analysis impossible.
**Recommendation:** Log all exceptions at WARNING or ERROR level. Use specific exception handling.
**Effort:** Simple

### MAJOR: Unused Parameters in Methods
**ID:** CQ-006
**Location:** `game/simulation/components/abilities/weapons.py:85-149`
**Issue:** The `WeaponAbility.recalculate()` method has `pass` statement followed by logic that appears dead code.
**Impact:** Confusing code maintenance. Unclear intent.
**Recommendation:** Remove the `pass` statement or clarify method purpose.
**Effort:** Simple

### MAJOR: Copy-Paste Code - find_target() and find_secondary_targets()
**ID:** CQ-007
**Location:** `game/ai/controller.py:61-138`
**Issue:** Methods are nearly identical with 40+ lines of duplicated logic for enemy queries, missile checks, and scoring.
**Impact:** Maintenance nightmare. Bug fixes must be applied in multiple places.
**Recommendation:** Extract common logic into `_find_enemies_in_radius()` and `_score_and_sort_enemies()` helper methods.
**Effort:** Medium

### MAJOR: Missing Input Validation in Component Addition
**ID:** CQ-008
**Location:** `game/simulation/entities/ship.py:479-514`
**Issue:** The `add_components_bulk()` method silently stops adding components on first validation failure.
**Impact:** Silent failures. Caller has no way to know how many components failed.
**Recommendation:** Return detailed result object with success count, failed count, and first failure reason.
**Effort:** Simple

### MAJOR: Magic Numbers Throughout Codebase
**ID:** CQ-009
**Location:** Multiple files - `game/simulation/entities/ship.py:372-374`, `game/simulation/systems/battle_engine.py:300-301`, `game/ui/screens/strategy_renderer.py:126-130`
**Issue:** Hard-coded numeric values scattered throughout code with no explanation.
**Impact:** Difficult to tune game balance. When values need adjustment, difficult to find all instances.
**Recommendation:** Move all magic numbers to constants.py or config files.
**Effort:** Medium

### MAJOR: Inconsistent Exception Handling Patterns
**ID:** CQ-010
**Location:** `game/ui/screens/builder_screen.py:40-48`, `game/ui/screens/workshop_screen.py`
**Issue:** Tkinter initialization has defensive checks but no cleanup handling.
**Impact:** Potential runtime errors if tkinter is unavailable but code assumes it's initialized.
**Recommendation:** Create `TkinterManager` class that handles initialization/cleanup safely.
**Effort:** Medium

### MAJOR: Complex Conditional Logic Not Extracted
**ID:** CQ-011
**Location:** `game/simulation/entities/ship.py:269-312`
**Issue:** Method has three independent multi-step conditional blocks checking different requirements with repeated patterns.
**Impact:** Difficult to add new derelict conditions. Similar checks must be added to multiple places.
**Recommendation:** Create derelict condition strategy objects in a list.
**Effort:** Simple

### MAJOR: Workshop Screen Backward Compatibility Wrapper
**ID:** CQ-012
**Location:** `game/ui/screens/builder_screen.py:46-163`
**Issue:** Entire wrapper class exists solely for backward compatibility, proxying 50+ method calls.
**Impact:** Code maintenance burden. Developers unsure which class to modify.
**Recommendation:** Create deprecation plan, migrate all callers, remove wrapper class.
**Effort:** Medium

### Minor: Incomplete Refactoring - Multiple __init__ Patterns
**ID:** CQ-013
**Location:** Component loading files (ship_loader.py related)
**Issue:** Initialization code scattered across Ship.__init__(), ship_loader.load_vehicle_classes(), ship_loader.initialize_ship_data().
**Impact:** Difficult to understand initialization sequence.
**Recommendation:** Create `ShipInitializer` class with clear dependencies.
**Effort:** Medium

### Minor: Inconsistent Naming Conventions
**ID:** CQ-014
**Location:** Throughout codebase
**Issue:** Inconsistent naming patterns for private methods, component properties, ability class names.
**Impact:** Cognitive load. Developers must remember different conventions.
**Recommendation:** Establish naming guide and apply consistently.
**Effort:** Simple

### Minor: Missing Docstrings in Complex Methods
**ID:** CQ-015
**Location:** `game/simulation/entities/ship_stats.py:15-150`
**Issue:** ShipStatsCalculator.calculate() is 140+ lines with sparse docstrings.
**Impact:** Difficult for new developers to understand calculation phases.
**Recommendation:** Add comprehensive docstring with calculation phase overview.
**Effort:** Simple

### Minor: Debug Print Statements Left in Code
**ID:** CQ-020
**Location:** `game/ui/screens/workshop_screen.py:107-109`
**Issue:** Debug print statements remain in production code.
**Impact:** Pollutes console output. Inconsistent with game's logging system.
**Recommendation:** Replace all `print()` with `log_debug()`.
**Effort:** Simple

### Minor: Duplicated Default Values in Multiple Places
**ID:** CQ-022
**Location:** `game/simulation/entities/ship.py`, `game/ai/controller.py`
**Issue:** Default value 1 for max_targets repeated in three places.
**Impact:** If default changes, must update all three places.
**Recommendation:** Create `ShipDefaults` enum with all default values.
**Effort:** Simple

### Info: Architectural Pattern - Service Layer Not Fully Utilized
**ID:** CQ-026
**Location:** `game/simulation/services/` directory
**Issue:** Services directory exists but many core operations still in entity classes.
**Impact:** Inconsistent architecture. Harder to extend business logic.
**Recommendation:** Consolidate all business operations into service classes.
**Effort:** Complex

### Info: Performance - Excessive Object Creation in Hot Loops
**ID:** CQ-027
**Location:** `game/ai/controller.py:63-94`
**Issue:** Creates temporary list allocations in hot loop for targeting.
**Impact:** Performance impact in large battles. Memory pressure.
**Recommendation:** Use generators, reuse lists via object pooling.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CQ-003: God Class - Ship** (CRITICAL) - 750+ lines with 50+ methods. Breaking it down should be highest priority.
2. **CQ-001: Security Risk with eval()** (CRITICAL) - Formula evaluation using eval() is a potential security vulnerability.
3. **CQ-002: Deeply Nested fire_weapons()** (CRITICAL) - 5-6 level nesting makes code untestable.
4. **CQ-007: Copy-Paste Code - Target Finding** (MAJOR) - find_target() and find_secondary_targets() nearly identical.
5. **CQ-004: Excessive getattr() Usage** (MAJOR) - Widespread defensive programming indicates attribute design issues.
