# UI/Screens System Analysis Report

## Summary
- **Total issues found:** 3
- **Critical:** 1, **Major:** 2, **Minor:** 0, **Info:** 0

---

## LARGEST ISSUE

### CRITICAL: Direct Mutation of Simulation Entities by UI Screens

**ID:** UI-01

**Location:**
- `game/ui/screens/builder/main.py` (lines 77-78, 497, 508, 559, 963-964, 1060, 1067)
- `game/ui/screens/formation_editor.py` (lines 200, 548, 591)
- `game/ui/screens/race_setup_screen.py` (lines 83-88)
- `game/ui/screens/fleet_report_window.py` (lines 41, 596)

**Issue:**
UI screen classes directly instantiate, hold references to, and mutate simulation entities:

1. **BuilderSceneGUI** maintains `self.ship` (a Ship entity) and directly manipulates it:
   - Directly calls `ship.recalculate_stats()`
   - Directly removes components: `self.ship.remove_component(found_layer, found_idx)`
   - Directly adds components: `self.ship.add_component(new_comp, target_layer)`
   - Directly mutates layer data: `self.ship.layers[layer_type]['components'] = []`

2. **FormationEditor** maintains `self.arrows` data and `self.core` managing spatial state

3. **RaceSetupScreen** creates and holds `self.race_config` and directly modifies it

4. **FleetReportWindow** directly accesses `self.fleet` properties without view models

**Impact on Maintenance/Extensibility:**

1. **No Separation of Concerns:** UI logic intermingled with entity state management
2. **Impossible to Unit Test UI:** Cannot test screens in isolation
3. **Cannot Reuse Across UI Frameworks:** Migrating requires rewriting all entity mutation logic
4. **State Consistency Issues:** Multiple panels independently access and mutate the same object
5. **Difficult to Add Undo/Redo:** No audit trail of changes
6. **Tight Binding to Domain Classes:** Simple domain refactors cascade through UI layers
7. **Cannot Enforce Business Rules:** All mutations happen directly in UI handlers

**Recommendation:**
Introduce a **View Model / Presentation Model** layer:
- ViewModel exposes read-only computed properties
- Provides command methods for user actions
- Application Services handle actual entity mutations with validation
- Use dependency injection so screens depend on ViewModel interfaces

**Effort:** Complex (refactoring 4,400+ lines across 4+ files)

---

## Secondary Findings

### MAJOR: Bloated Screen Classes with Mixed Concerns

**ID:** UI-02

**Location:**
- `game/ui/screens/builder/main.py` (1,091 lines, 26 methods)
- `game/ui/screens/race_setup_screen.py` (1,227 lines, 35 methods)
- `game/ui/screens/formation_editor.py` (1,055 lines, 42 methods)
- `game/ui/screens/fleet_report_window.py` (1,034 lines, 27 methods)

**Issue:**
Each screen handles multiple responsibilities:
- UI rendering and layout
- State management (holding entities)
- Event handling (user input)
- Business logic (filtering, sorting, transformations)
- Data access (image loading, stat calculations)

**Impact:**
- Difficult to understand complete flow
- Cannot test individual responsibilities
- Changes to one aspect risk breaking others

**Recommendation:**
Extract into focused classes: Panels (rendering), ViewModels (state), Services (logic), DataLoaders (I/O)

**Effort:** Complex (2-3 weeks of systematic extraction)

---

### MAJOR: Implicit Dependencies on Global Singletons

**ID:** UI-03

**Location:**
- `game/ui/screens/builder/main.py` (lines 81, 83, 88)
- `game/ui/screens/fleet_report_window.py` (line 605)
- Multiple screens using `ShipThemeManager.instance()`, `SpriteManager.instance()`

**Issue:**
Screens depend on singleton instances with hidden dependencies.

**Impact:**
- Cannot create isolated instances
- Testing requires mocking multiple singletons
- Singleton refactors break all dependent screens

**Recommendation:**
Pass as constructor dependencies instead of using singletons.

**Effort:** Simple (~4 hours)

---

## Assessment

**Current Health: POOR (2/10)**

### Root Problems:
1. UI screens act as "smart views" holding and mutating domain entities directly
2. No abstraction layer between UI and simulation
3. Screens are god classes (1,000+ LOC each) mixing rendering, logic, I/O, and state
4. Hidden dependencies on singletons

### Maintenance Burden:
- High friction to change domain models (cascades to 5+ UI files)
- Impossible to test UI in isolation
- Cannot parallelize feature development (merge conflicts in god classes)

### Priority Actions:
1. **First:** Extract ViewModel layer (UI-01) - highest-leverage change
2. **Second:** Break screens into smaller components (UI-02)
3. **Third:** Remove global singletons (UI-03)

Without these changes, the system becomes unmaintainable as it grows.
