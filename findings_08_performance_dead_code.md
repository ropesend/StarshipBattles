# Performance & Dead Code

**Theme:** Performance bottlenecks, dead code, unused modules, broken imports, and optimization opportunities.

---

## Critical Performance Issues

### PERF-01: Nested Component Iteration in Hot Path
**ID:** PERF-01
**Location:** `game/simulation/systems/battle_engine.py:515`, `game/simulation/entities/ship_stats.py:89-90`
**Issue:** `get_all_components()` called repeatedly in hot combat loops. Each call rebuilds a list by iterating all layers.
**Impact:** O(n) list construction multiple times per tick per ship. With 100+ ships, thousands of unnecessary iterations.
**Recommendation:** Cache component list on ship or use generator for immutable iteration.
**Effort:** Medium

---

### PERF-02: Projectile List Reconstruction Every Tick
**ID:** PERF-02
**Location:** `game/simulation/projectile_manager.py:138`
**Issue:** `self.projectiles = [p for p in self.projectiles if i not in projectiles_to_remove]` rebuilds entire list every tick.
**Impact:** O(n) memory churn every tick.
**Recommendation:** Use index-based removal or mark dead projectiles for batch cleanup.
**Effort:** Medium

---

### PERF-03: O(n^2) Targeting Evaluation
**ID:** PERF-03
**Location:** `game/ai/controller.py:124-141`
**Issue:** `_score_and_sort_enemies()` sorts all candidates every tick. Evaluator scans all components for each target.
**Impact:** With 50+ targets, creates O(n^2) component scans per frame.
**Recommendation:** Cache weapon/ability availability per ship.
**Effort:** Medium

---

## Major Performance Issues

### PERF-04: Repeated Deep Copies on Initialization
**ID:** PERF-04
**Location:** `game/simulation/components/component.py:91, 134, 543`
**Issue:** Three `deepcopy()` calls during component init: data, abilities, base_abilities.
**Impact:** Expensive for complex components. Happens for every component in every ship.
**Recommendation:** Use shallow copies where mutation isn't needed.
**Effort:** Simple

---

### PERF-05: Inefficient Ability Lookup with MRO Fallback
**ID:** PERF-05
**Location:** `game/simulation/components/component.py:182-209`
**Issue:** `get_abilities()` uses fallback isinstance/MRO walking on every lookup.
**Impact:** O(n) method resolution order walk per ability query.
**Recommendation:** Build ability name index during instantiation.
**Effort:** Simple

---

### PERF-06: Spatial Grid Cleared Every Tick
**ID:** PERF-06
**Location:** `game/simulation/systems/battle_engine.py:344-351`
**Issue:** Entire spatial grid cleared and rebuilt with all ships/projectiles every tick.
**Impact:** Unnecessary O(n) churn. Could use incremental updates.
**Recommendation:** Use quad-tree or incremental grid updates.
**Effort:** Complex

---

### PERF-07: Beam Targeting Multiple Raycasts
**ID:** PERF-07
**Location:** `game/engine/collision.py:64-137`
**Issue:** Each beam recalculates sphere-ray intersection even for same target.
**Impact:** Multiple beams vs same target = repeated expensive math.
**Recommendation:** Cache intersection results per target per tick.
**Effort:** Medium

---

### PERF-08: Component Status Checks on Every Damage Frame
**ID:** PERF-08
**Location:** `game/simulation/entities/ship_stats.py:145-153`
**Issue:** Damage threshold checks iterated for all components during `calculate()` which runs frequently.
**Impact:** Repeated HP ratio calculations (division is expensive).
**Recommendation:** Cache damage status with dirty flag system.
**Effort:** Medium

---

## Minor Performance Issues

### PERF-09: Repeated Vector2 Conversions
**ID:** PERF-09
**Location:** `game/simulation/projectile_manager.py:47-48, 63-64`
**Issue:** Creates new Vector2 objects from existing ones for type safety.
**Impact:** Unnecessary allocations in tight collision loop.
**Recommendation:** Accept duck-typed vectors or use type hints.
**Effort:** Simple

---

### PERF-10: Sorted Enemies Multiple Times
**ID:** PERF-10
**Location:** `game/ai/target_evaluator.py:97-140`
**Issue:** Distance calculations repeated for same targets across rules.
**Impact:** Multiple distance.length() calls per target.
**Recommendation:** Pre-calculate sorted distances once.
**Effort:** Simple

---

### SIM-024: Missing Performance Optimizations
**ID:** SIM-024
**Location:** `game/simulation/systems/battle_engine.py:343-350`, `game/simulation/projectile_manager.py:27-103`
**Issue:** Spatial grid rebuilt completely each tick. Projectile iteration uses nested loops without spatial indexing.
**Recommendation:** Implement incremental grid updates. Use spatial queries for projectile collision.
**Effort:** Medium

---

### SIM-021: Evaluation of Math Formulas Uses eval()
**ID:** SIM-021
**Location:** `game/simulation/formula_system.py:65-100`
**Issue:** Uses Python eval() to evaluate formula strings from JSON data.
**Impact:** Security risk if data source compromised.
**Recommendation:** Use safer expression parser or implement custom safe parser.
**Effort:** Medium

---

## Critical Dead Code Issues

### DC-001: Duplicate Battle Panel Systems
**ID:** DC-001
**Location:**
- `game/ui/hud/panels.py` (705 lines)
- `game/ui/panels/battle_panels.py` (20KB)

**Issue:** Two parallel implementations of ShipStatsPanel, SeekerMonitorPanel, and BattleControlPanel classes exist in different locations. This creates confusion about which version is canonical:
- `game/ui/hud/battle.py` imports from `game.ui.hud.panels`
- `game/ui/screens/battle_screen.py` imports from `game.ui.panels.battle_panels`

**Impact:** Code duplication, maintenance burden, potential sync issues between implementations.
**Recommendation:** Consolidate into single location (suggest `game/ui/panels/battle_panels.py` as it has more recent refactoring with `ship_stats_renderer.py` imports).
**Effort:** Medium

**FLAG - DUPLICATE IMPLEMENTATIONS:** This issue identifies two parallel implementations of the same panels. One must be chosen as canonical.

---

### DC-01: Broken Import References in Main Application
**ID:** DC-01
**Location:** `game/app.py:28-29`
**Issue:** App imports non-existent modules:
```python
from Tools.formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
```
These modules don't exist at the referenced paths.
**Impact:** Runtime ImportError will occur if TEST_LAB or FORMATION states are activated.
**Recommendation:** Update imports to correct paths or move modules into proper game package structure.
**Effort:** Simple

---

### DC-02: Backup File Committed to Repository
**ID:** DC-02
**Location:** `ui/test_lab_scene.py.backup`
**Issue:** A 2,731-line backup file of test_lab_scene.py is committed alongside the active version.
**Impact:** Increases repo size, creates confusion about which version is active.
**Recommendation:** Delete the `.backup` file. Use git history if older version is needed.
**Effort:** Simple

---

### UI-001: Duplicate Class Definition - BattleSetupScreen
**ID:** UI-001
**Location:**
- `game/ui/screens/setup.py:134` (680 lines)
- `game/ui/screens/setup_screen.py:27` (same class name, ~400 lines)

**Issue:** Two separate implementations of BattleSetupScreen class exist in different files, creating ambiguity and maintenance burden. No clear indication which is canonical or if they serve different purposes.
**Impact:** Import ambiguity, potential runtime errors from importing wrong version, code duplication, maintenance nightmare when bugs are fixed in one but not the other.
**Recommendation:** Consolidate into single canonical BattleSetupScreen. If they differ in functionality, rename one (e.g., BattleSetupScreenLegacy). Update all imports to use canonical version.
**Effort:** Medium

**FLAG - DUPLICATE CLASSES:** This issue identifies two classes with the same name in different files. One must be canonical.

---

### UI-002: Broken Import Path in workshop_screen.py
**ID:** UI-002
**Location:** `game/ui/screens/workshop_screen.py:25, 27-29, 59`
**Issue:** Uses incorrect relative imports `from ui.builder ...` instead of `from game.ui.screens.builder ...`. Lines affected:
```python
from ui.builder import BuilderLeftPanel, BuilderRightPanel, WeaponsReportPanel, LayerPanel
from ui.builder.schematic_view import SchematicView
from ui.builder.interaction_controller import InteractionController
from ui.builder.event_bus import EventBus
from ui.builder.detail_panel import ComponentDetailPanel
```
**Impact:** These imports will fail at runtime. The DesignWorkshopGUI cannot load.
**Recommendation:** Replace all `from ui.builder` with `from game.ui.screens.builder`. Verify imports work by running application.
**Effort:** Simple

---

### UI-003: Broken Import Paths in design_report_panel.py
**ID:** UI-003
**Location:** `game/ui/panels/design_report_panel.py:19-20`
**Issue:** Uses incorrect relative imports:
```python
from ui.builder.right_panel import StatRow
from ui.builder.stats_config import STATS_CONFIG, get_construction_rows
```
Should be `from game.ui.screens.builder...`
**Impact:** Import failures, DesignReportPanel cannot load.
**Recommendation:** Fix import paths to use full module path `from game.ui.screens.builder...`.
**Effort:** Simple

---

## Major Dead Code Issues

### DC-002: Stub Functions with NotImplementedError
**ID:** DC-002
**Location:** `game/ai/behaviors.py:79`
**Issue:** Base class `AIBehavior.update()` raises `NotImplementedError` but is never actually called - appears to be incomplete design pattern.
**Code:**
```python
def update(self, target: Any, strategy: Dict[str, Any]) -> None:
    """Execute behavior logic."""
    raise NotImplementedError
```
**Impact:** Dead code if subclasses override before parent is used, confusing interface contract.
**Recommendation:** Use `@abstractmethod` if truly abstract.
**Effort:** Simple

---

### DC-003: Marked-for-Deletion Directory Unresolved
**ID:** DC-003
**Location:** `./_marked_for_deletion_2026-01-27/`
**Issue:** Entire directory marked for deletion but still in the repository.
**Impact:** Clutters repo, indicates incomplete cleanup.
**Recommendation:** Delete the entire directory or properly archive.
**Effort:** Simple

---

### DC-004: Incorrect Import Path for TestLabScene
**ID:** DC-004
**Location:** `game/app.py:29` / Actual module at `ui/test_lab_scene.py`
**Issue:** app.py imports from `ui.test_lab_scene` but ui/ is outside the game package.
**Impact:** Import will fail at runtime when TEST_LAB state is accessed.
**Recommendation:** Move `ui/` into `game/ui/screens/` or create proper import path handling.
**Effort:** Medium

---

### DC-005: Incorrect Import Path for FormationEditorScene
**ID:** DC-005
**Location:** `game/app.py:28` / Actual module at `Tools/formation_editor.py`
**Issue:** app.py imports from `Tools.formation_editor` but Tools/ is outside game package.
**Impact:** Import will fail at runtime when FORMATION state is accessed.
**Recommendation:** Move Tools into proper package structure or fix import paths.
**Effort:** Medium

---

### DC-006: Empty Init Files - Incomplete Package Setup
**ID:** DC-006
**Location:** Multiple `__init__.py` files (14 files with 0 lines)
**Issue:** Empty __init__.py files without package-level exports for cleaner imports.
**Impact:** Forces deep import paths, makes package exports unclear.
**Recommendation:** Add meaningful __all__ exports or remove unnecessary package structure.
**Effort:** Medium

---

### DC-04: Empty Service Module
**ID:** DC-04
**Location:** `game/strategy/services/__init__.py` (1 line only comment)
**Issue:** Package is empty except for comment "# Strategy services package"
**Impact:** Dead package namespace, no exports defined
**Recommendation:** Either populate with real services or delete package and import directly from submodules.
**Effort:** Simple

---

### DC-05: Unimplemented Method with TODO
**ID:** DC-05
**Location:** `game/app.py:671`
**Issue:**
```python
available_tech_ids = []  # TODO: Replace with empire.available_tech or similar
```
**Impact:** Placeholder code left in production, no available tech returned to workshop.
**Recommendation:** Implement proper empire tech tracking or remove placeholder.
**Effort:** Medium

---

### DC-06: _ValidatorProxy Never Used
**ID:** DC-06
**Location:** `game/simulation/entities/ship.py:29-34`
**Issue:** `_ValidatorProxy` class is instantiated as `VALIDATOR = _ValidatorProxy()` but the VALIDATOR constant is never referenced in the codebase. Validator is accessed directly via `get_or_create_validator()`.
**Impact:** Dead code adds maintenance burden, confuses developers.
**Recommendation:** Remove `_ValidatorProxy` class and VALIDATOR global.
**Effort:** Simple

---

### SIM-006: Unused Dead Code - _ValidatorProxy Pattern
**ID:** SIM-006
**Location:** `game/simulation/entities/ship.py:29-34, 22`, `game/simulation/entities/ship_loader.py`
**Issue:** _ValidatorProxy is instantiated but never used (VALIDATOR = _ValidatorProxy() on line 34 is never referenced). The validator is accessed directly via get_or_create_validator() in add_component methods.
**Impact:** Dead code adds to maintenance burden, confuses developers, suggests incomplete refactoring.
**Recommendation:** Remove _ValidatorProxy class and VALIDATOR global. Import validator directly where needed.
**Effort:** Simple

---

### SIM-009: Multiple Projectile Manager Implementations
**ID:** SIM-009
**Location:** `game/simulation/projectile_manager.py` (212 LOC) vs `game/simulation/systems/projectile_manager.py`
**Issue:** Two separate projectile manager implementations in different locations with different interfaces and implementations.
**Impact:** Code duplication, maintenance burden, unclear which one to use.
**Recommendation:** Consolidate into single implementation. Keep one in systems/. Update all imports.
**Effort:** Medium

**FLAG - DUPLICATE IMPLEMENTATIONS:** This issue identifies two projectile manager implementations. One must be chosen as canonical.

---

## Minor Dead Code Issues

### DC-07: Unused Backward Compatibility Path Exports
**ID:** DC-07
**Location:** `game/core/paths.py:89-98`
**Issue:** Module exports old-style path constants for backward compatibility that duplicate the Paths class API.
**Impact:** Code duplication, confusing API surface.
**Recommendation:** Migrate all uses to `Paths.` class API. Remove once converted.
**Effort:** Simple

---

### DC-08: Unused Path Constants
**ID:** DC-08
**Location:** `game/core/paths.py:59-60, 98`
**Issue:** `VEHICLE_CLASSES_FILE` and `VEHICLE_LAYERS_FILE` defined but rarely used in active code.
**Impact:** Dead API surface.
**Recommendation:** Verify not needed; remove or consolidate.
**Effort:** Simple

---

### DC-09: Debug Flag Always Enabled
**ID:** DC-09
**Location:** `game/core/constants.py:56`
**Issue:**
```python
DEBUG_SCREENSHOTS = True
```
**Impact:** Debug feature cannot be toggled at runtime, potential performance issue if screenshots are continuously saved.
**Recommendation:** Make configurable or disable by default.
**Effort:** Simple

---

### DC-10: Obsolete Commented Code Reference
**ID:** DC-10
**Location:** `game/ui/screens/test_lab.py:88-99`
**Issue:** Obsolete commented code block with notes about removed functionality.
**Impact:** Minor - shows incomplete cleanup from refactoring.
**Recommendation:** Remove once surrounding code is stable.
**Effort:** Simple

---

### DC-11: Debugging Scripts Not Integrated
**ID:** DC-11
**Location:** `Debugging/archive_confirmed.py`, `Debugging/confirm_bugs_ui.py`
**Issue:** Debug automation scripts exist but aren't integrated into CI pipeline.
**Impact:** Unused tooling.
**Recommendation:** Integrate into debug workflow or remove if not needed.
**Effort:** Simple

---

### DC-07: Dead pycache Directories
**ID:** DC-07
**Location:** 36 `__pycache__` directories throughout game/
**Issue:** Compiled Python bytecode cached directories should not be in version control.
**Impact:** Bloats repository.
**Recommendation:** Add to .gitignore if not already present.
**Effort:** Simple

---

### DC-08: Empty Module Exports
**ID:** DC-08
**Location:**
- `game/ai/__init__.py` (0 bytes)
- `game/__init__.py` (0 bytes)
- `game/simulation/__init__.py` (0 bytes)

**Issue:** Package __init__ files are completely empty with no exports defined.
**Impact:** Reduces code discoverability, requires importing from submodules.
**Recommendation:** Define meaningful `__all__` exports.
**Effort:** Simple

---

## Top Priority Issues

### Performance
1. **PERF-01: Nested Component Iteration** - Hot path inefficiency affecting every tick
2. **PERF-02: Projectile List Reconstruction** - Memory churn every tick
3. **PERF-03: O(n^2) Targeting Evaluation** - Scales poorly with fleet size
4. **PERF-06: Spatial Grid Rebuild** - Could use incremental updates
5. **PERF-04: Repeated Deep Copies** - Expensive initialization pattern

### Dead Code
1. **DC-01/UI-002/UI-003: Broken Imports** - Will cause immediate runtime failures
2. **DC-001/UI-001: Duplicate Implementations** - Choose canonical versions
3. **DC-02: Backup File Committed** - Quick win: delete backup file
4. **DC-03: Marked-for-Deletion Directory** - Quick win: delete entire directory
5. **SIM-009: Duplicate Projectile Managers** - Consolidate implementations
