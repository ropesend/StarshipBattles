# Code Quality Analysis Report

## Summary
- **Total issues found:** 23
- **Critical:** 3
- **Major:** 8
- **Minor:** 12
- **Info:** 0

---

## Findings

### CRITICAL: God Class - Component System (878 LOC)
**ID:** CQ-01
**Location:** `game/simulation/components/component.py:1-879`
**Issue:** Single Component class handles all aspects: initialization, abilities, modifiers, stats recalculation, damage tracking, and resource management across 878 lines. The class violates SRP with 40+ methods covering disparate concerns.
**Impact:** Extremely difficult to test, maintain, and extend. Changes to any feature risk cascading failures.
**Recommendation:** Extract separate classes: AbilityManager, ModifierManager, StatsCalculator, ResourceCostCalculator. Use composition pattern.
**Effort:** Complex

### CRITICAL: Deeply Nested UI Screen (1231 LOC)
**ID:** CQ-02
**Location:** `game/ui/screens/race_setup_screen.py:1-1231`
**Issue:** Single UIWindow subclass handles tab switching, preview rendering, event routing, and state management. Methods contain nested loops and conditionals 5+ levels deep.
**Impact:** New team members cannot quickly understand flow. Tab-specific bug fixes create high regression risk.
**Recommendation:** Extract TabPanel base class with specialized subclasses. Use ViewModel pattern to separate state from UI.
**Effort:** Complex

### CRITICAL: High Cyclomatic Complexity - Validation Rules
**ID:** CQ-03
**Location:** `game/simulation/systems/validator.py:120-180`
**Issue:** LayerRestrictionDefinitionRule.validate() has 7 nested conditionals checking block/allow rules with repeated string parsing and loose coupling to rule format.
**Impact:** Hard to add new rule types. String parsing errors go undetected.
**Recommendation:** Create Rule class hierarchy (BlockRule, AllowRule) with polymorphic validate().
**Effort:** Medium

### MAJOR: Duplicate Code - Image Scaling Pattern
**ID:** CQ-04
**Location:** `game/ui/screens/race_setup_screen.py:879-914` (and 10+ other files)
**Issue:** Same image scaling pattern repeated verbatim across 10+ files.
**Impact:** Bug fixes require changes in 10+ places. Maintenance burden.
**Recommendation:** Extract utility function `scale_to_fit(surface, max_w, max_h)` in ui/utils.py
**Effort:** Simple

### MAJOR: Missing Error Handling - Resource Consumption
**ID:** CQ-05
**Location:** `game/simulation/components/component.py:335-357`
**Issue:** `try_activate()`, `consume_activation()` methods silently return False/None without logging.
**Impact:** Silent failures in activation logic. Debugging UI issues becomes difficult.
**Recommendation:** Add logging at WARN level for failures. Return typed Result objects.
**Effort:** Simple

### MAJOR: Single Letter Variables
**ID:** CQ-06
**Location:** Multiple files - `game/ui/screens/planet_list_window.py:156-157`, `game/ui/screens/race_setup_screen.py:810-926`
**Issue:** Loop variables named `i`, `x`, `y`, `w`, `h` in complex layout logic.
**Impact:** Cognitive overhead. Copy-paste bugs when similar loops are duplicated.
**Recommendation:** Use descriptive names: `formation_index`, `x_pos`, `panel_width`.
**Effort:** Simple

### MAJOR: Magic Numbers Throughout
**ID:** CQ-07
**Location:** Multiple UI screens: `builder/weapons_panel.py:10-75`, `race_setup_screen.py:862`
**Issue:** Hardcoded values like `0.5` for damage threshold, `150` for ship preview size with no context.
**Impact:** Hard to maintain consistent UI theme. Scaling to different resolutions requires grep-and-replace.
**Recommendation:** Create UIConstants class with named fields.
**Effort:** Medium

### MAJOR: Complex Conditional - Ship Stats Calculation
**ID:** CQ-08
**Location:** `game/simulation/systems/stats.py:74-82`
**Issue:** Damage threshold check uses conditional with inverted logic and duplicated damage checks.
**Impact:** Armor damage logic scattered. Hard to verify correctness.
**Recommendation:** Extract `check_component_damage(comp)` method with clear intent.
**Effort:** Simple

### MAJOR: God Class - Builder GUI (1100 LOC)
**ID:** CQ-09
**Location:** `game/ui/screens/builder/main.py:1-1100`
**Issue:** BuilderSceneGUI mixes UI rendering, event handling, selection logic, data persistence, and validation. 40+ attributes.
**Impact:** New developers need 2+ days to understand flow. Adding features breaks existing code.
**Recommendation:** Split into BuilderPresentation, BuilderModel, BuilderController using MVC.
**Effort:** Complex

### MINOR: Inconsistent Naming
**ID:** CQ-10
**Location:** `game/ui/screens/fleet_report_window.py:45-65`
**Issue:** Mix of naming conventions: `sidebar_width` vs `self.header_height`. Some abbreviations, others spelled out.
**Impact:** New contributors follow wrong patterns.
**Recommendation:** Establish naming guide with consistent suffixes.
**Effort:** Simple

### MINOR: Unused Parameters
**ID:** CQ-11
**Location:** `game/ui/screens/race_setup_screen.py:250`
**Issue:** Methods with partially used parameters like `stats` passed but not always accessed.
**Impact:** IDE warnings ignored. Dead code pathway confusion.
**Recommendation:** Remove unused params or document why retained.
**Effort:** Simple

### MINOR: Cross-Layer Imports
**ID:** CQ-12
**Location:** `game/ui/screens/builder/main.py:30-36`
**Issue:** UI layer directly imports Ship, VEHICLE_CLASSES from simulation layer.
**Impact:** Simulation refactoring requires UI changes. Hard to test UI in isolation.
**Recommendation:** Create DTO/facade layer: BuilderShipAdapter.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **CQ-01: God Class - Component System (878 LOC)** - Root of maintainability problems. Every new feature risks regressions. Highest maintenance burden.

2. **CQ-02: Deeply Nested UI Screen (1231 LOC)** - Most complex screen. Blocks new UI features. Constant bug reports.

3. **CQ-04: Duplicate Code - Image Scaling** - Low effort, high ROI. Bug fix in one place prevents 10+ locations.

4. **CQ-07: Magic Numbers Throughout** - Blocks UI theme consistency. Scaling to new resolutions hard.

5. **CQ-09: God Class - Builder GUI (1100 LOC)** - Second most complex. Builder features blocked.
