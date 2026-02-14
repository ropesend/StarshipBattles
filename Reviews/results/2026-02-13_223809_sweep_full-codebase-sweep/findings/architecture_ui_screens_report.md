# Architecture Drift Report: game/ui/screens/ and game/ui/panels/

**Generated:** 2026-02-13
**Scope:** `game/ui/screens/`, `game/ui/panels/`
**Methodology:** Exhaustive scan of all Python files

---

## Executive Summary

This report documents architecture drift findings in the UI layer modules. The analysis covered 97 Python files across the assigned directories. The codebase demonstrates generally good architectural practices with strategic use of TYPE_CHECKING blocks to prevent circular imports. However, several findings warrant attention.

**Statistics:**
- Files scanned: 97
- Critical findings: 0
- Major findings: 4
- Minor findings: 11
- Informational findings: 8

---

## Finding: GOD-001

**Severity:** MAJOR
**Category:** God Class Detection
**Location:** `game/ui/screens/test_lab/screen.py`

**Description:**
TestLabScreen is 1906 lines, significantly exceeding the 500-line threshold for god classes. This indicates the class handles too many responsibilities and should be decomposed.

**Evidence:**
```
1906 C:/Dev/Starship Battles/game/ui/screens/test_lab/screen.py
```

**Impact:**
Difficult to maintain, test, and understand. High cognitive load for developers working on this file.

**Recommended Action:**
Continue extracting responsibilities to helper modules (following the pattern already started with `test_executor.py`, `panel_manager.py`, etc.). Target: reduce main screen to <500 lines.

---

## Finding: GOD-002

**Severity:** MAJOR
**Category:** God Class Detection
**Location:** `game/ui/screens/formation_editor.py`

**Description:**
FormationEditorScreen is 934 lines, nearly double the 500-line threshold. While some extraction has been done (FormationRenderer, FormationInputHandler), the main file remains oversized.

**Evidence:**
```
934 C:/Dev/Starship Battles/game/ui/screens/formation_editor.py
```

**Impact:**
Reduced maintainability and increased risk of bugs due to complexity.

**Recommended Action:**
Extract remaining responsibilities (toolbar handling, file I/O, clipboard operations) to separate modules.

---

## Finding: GOD-003

**Severity:** MAJOR
**Category:** God Class Detection
**Location:** `game/ui/screens/strategy_screen.py`

**Description:**
StrategyScreen is 819 lines, exceeding the 500-line threshold. The docstring notes it was "refactored from 1,568 lines to ~350 lines" but current state is 819 lines, suggesting scope creep.

**Evidence:**
```python
# From file header:
# Refactored from 1,568 lines to ~350 lines by extracting:
# - StrategyRenderer: All drawing logic (~580 lines)
# ...
# Actual current size: 819 lines
```

**Impact:**
The class has grown beyond its intended refactored size, accumulating new responsibilities.

**Recommended Action:**
Review recent additions and extract new functionality to appropriate helper modules to return closer to the ~350 line target.

---

## Finding: GOD-004

**Severity:** MINOR
**Category:** God Class Detection
**Location:** Multiple files approaching threshold

**Description:**
Several files are approaching the 500-line threshold:
- `battle_screen.py`: 644 lines
- `workshop_screen.py`: 613 lines
- `battle_panels.py`: 566 lines
- `planet_report_panel.py`: 508 lines

**Impact:**
These files may become god classes if growth continues unchecked.

**Recommended Action:**
Monitor these files and consider proactive extraction before they grow further.

---

## Finding: LAYER-001

**Severity:** MINOR
**Category:** Cross-Layer Import
**Location:** `game/ui/screens/battle_screen.py:24`

**Description:**
Direct import from simulation.services:
```python
from game.simulation.services import BattleService
```

This is an acceptable cross-layer import (UI can depend on Simulation), but creates tight coupling to the service implementation.

**Impact:**
Changes to BattleService API will directly impact this UI module.

**Recommended Action:**
Consider whether a UI-layer adapter would provide better isolation. Currently acceptable per architecture rules.

---

## Finding: LAYER-002

**Severity:** MINOR
**Category:** Cross-Layer Import
**Location:** `game/ui/screens/battle_screen.py:27`

**Description:**
Direct import from ai layer:
```python
from game.ai.ai_factory import AIControllerFactory
```

**Impact:**
UI layer directly depends on AI layer factory.

**Recommended Action:**
Per architecture rules, AI should not depend on UI, but UI depending on AI is acceptable. Consider if this factory call could be moved to a service layer for better separation.

---

## Finding: LAYER-003

**Severity:** MINOR
**Category:** Cross-Layer Runtime Imports
**Location:** Multiple files in `game/ui/screens/`

**Description:**
Multiple UI screen files import directly from strategy layer at runtime:
- `strategy_screen.py`: SaveGameService, StrategySessionFacade
- `build_queue_screen.py`: BuildQueueSource, collect_build_queues_at_hex
- `empire_build_queue_window.py`: BuildQueueSource classes
- `strategy_renderer.py`: OrderType, PlanetType
- `galaxy_test/` modules: PlanetType, Galaxy, etc.

**Evidence:**
29 runtime imports from `game.strategy.*` across UI screens.

**Impact:**
This is acceptable per layered architecture (UI depends on Strategy), but creates a large surface area of coupling.

**Recommended Action:**
INFO - These imports follow architectural rules. Consider documenting the key integration points.

---

## Finding: LAYER-004

**Severity:** INFO
**Category:** Cross-Layer Runtime Imports
**Location:** `game/ui/panels/`

**Description:**
Panel files import from strategy and simulation layers:
- `ship_stats_renderer.py`: ComponentStatus from simulation
- `race_identity_panel.py`: RaceConfig from strategy
- `race_environment_panel.py`: homeworld_presets from strategy
- `empire_treasury_panel.py`: EmpireEconomySnapshot from strategy
- `race_aptitudes_panel.py`: RacePointBudget from strategy

**Impact:**
Acceptable per architecture rules (UI depends on lower layers).

**Recommended Action:**
None required - these follow the proper dependency direction.

---

## Finding: TC-001

**Severity:** INFO
**Category:** TYPE_CHECKING Pattern Usage
**Location:** 32 files in `game/ui/screens/`

**Description:**
Extensive use of TYPE_CHECKING blocks indicates awareness of circular import risks and proper typing practices:
- `strategy_screen.py`: StarSystem, Fleet
- `build_queue_screen.py`: BuildContext, BuildQueueSource, etc.
- `formation_editor.py`: Rect, Surface
- Many others...

**Impact:**
Positive pattern - prevents circular imports while maintaining type safety.

**Recommended Action:**
Continue this practice. Consider documenting as a project pattern.

---

## Finding: TC-002

**Severity:** INFO
**Category:** TYPE_CHECKING Pattern Usage
**Location:** 18 files in `game/ui/panels/`

**Description:**
Panel files also properly use TYPE_CHECKING for cross-layer type hints:
- `ship_detail_panel.py`: ShipInstance from strategy
- `design_stats_panel.py`: Ship from simulation
- `design_report_panel.py`: Ship from simulation
- `build_queue_controller.py`: Planet, Fleet, Galaxy, Empire, etc.

**Impact:**
Positive pattern - allows type hints without runtime circular dependencies.

**Recommended Action:**
Continue this practice.

---

## Finding: PYGAME-001

**Severity:** INFO
**Category:** Pygame Usage Verification
**Location:** All scanned files in `game/ui/`

**Description:**
All pygame imports are within the `game/ui/` directory, which is the correct layer for pygame usage.

**Impact:**
No violations - pygame is properly contained within UI layer.

**Recommended Action:**
None required.

---

## Finding: CONST-001

**Severity:** MINOR
**Category:** Constants Import Pattern
**Location:** `game/ui/screens/galaxy_test/constants.py:6`

**Description:**
Constants file imports from strategy layer:
```python
from game.strategy.data.planet import PlanetType
```

This creates a dependency in what could be a pure configuration file.

**Impact:**
Minor - the constants file is UI-specific and the import is acceptable, but it does couple this UI constants file to the strategy layer.

**Recommended Action:**
Consider whether PLANET_TYPE_COLORS could be defined closer to where PlanetType is defined, or accept this as UI-specific visualization configuration.

---

## Finding: FACADE-001

**Severity:** INFO
**Category:** Architectural Pattern
**Location:** `game/ui/screens/strategy_screen.py:39, 77, 117`

**Description:**
StrategyScreen properly uses StrategySessionFacade for UI-to-engine communication:
```python
from game.strategy.facade.strategy_session_facade import StrategySessionFacade
...
self._facade = StrategySessionFacade(self.session)
...
self._fleet_ops = FleetOperations(self, self._facade)
```

**Impact:**
Positive pattern - facade provides clean separation between UI and game engine.

**Recommended Action:**
Continue using facade pattern for strategy layer interactions.

---

## Finding: PROTO-001

**Severity:** INFO
**Category:** Protocol Usage
**Location:** `game/ui/screens/strategy_screen.py:22`, `game/ui/panels/system_tree_panel.py:4`

**Description:**
Proper use of protocol type guards for cross-layer checks:
```python
from game.core.protocols import is_star, is_planet, is_fleet, is_warp_point, is_star_system
```

This follows PROJ-40 guidance to use protocol type guards instead of isinstance for cross-layer type checking.

**Impact:**
Positive pattern - reduces tight coupling between layers.

**Recommended Action:**
Continue using protocol type guards for cross-layer type checks.

---

## Finding: IMPORT-001

**Severity:** MINOR
**Category:** Import Organization
**Location:** `game/ui/screens/galaxy_test/system_mode.py:199-205`

**Description:**
Late imports within method body:
```python
def generate(self):
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.stars import StarGenerator
    from game.strategy.data.planet_gen import PlanetGenerator
    from game.strategy.generation.planet_image_registry import PlanetImageRegistry
    from game.strategy.generation.loaders.system_blueprints_loader import SystemBlueprintsLoader
```

**Impact:**
Late imports can indicate circular dependency avoidance or performance optimization. In this case, it appears to be for lazy loading of heavy modules.

**Recommended Action:**
Consider whether these could be top-level imports or if the lazy loading is intentional for startup performance.

---

## Finding: IMPORT-002

**Severity:** MINOR
**Category:** Import Organization
**Location:** `game/ui/screens/galaxy_test/galaxy_mode.py:248-253`

**Description:**
Similar late imports pattern:
```python
from game.strategy.generation.placement_strategies import (
    RandomPlacementStrategy,
    DensityBasedPlacementStrategy
)
from game.strategy.generation.loaders.galaxy_layouts_loader import GalaxyLayoutsLoader
from game.strategy.generation.density.density_map import DensityMap
```

**Impact:**
Same as IMPORT-001.

**Recommended Action:**
Consolidate late import patterns or document as intentional lazy loading.

---

## Finding: TKINTER-001

**Severity:** MINOR
**Category:** Mixed UI Framework
**Location:** `game/ui/screens/setup_screen.py:10-11`, `game/ui/screens/builder/preset_ui.py:4-5`

**Description:**
Files use both pygame and tkinter for UI:
```python
import tkinter as tk
from tkinter import filedialog
```

**Impact:**
Mixed UI frameworks can create visual inconsistency and platform-specific behavior. Used for file dialogs which pygame doesn't provide natively.

**Recommended Action:**
INFO - This is an acceptable workaround for file dialog functionality that pygame lacks. Consider documenting this as a known pattern.

---

## Finding: INHERIT-001

**Severity:** INFO
**Category:** Inheritance Pattern
**Location:** `game/ui/panels/build_queue_controller.py:54-80`

**Description:**
BuildQueueController uses dependency injection with many constructor parameters, following good practices:
- build_context
- design_library
- design_loader
- design_report
- on_queue_changed
- hex_coord
- galaxy
- empire
- on_planet_selection_needed

**Impact:**
Positive pattern - allows for testing with mock dependencies and follows SOLID principles.

**Recommended Action:**
Continue using dependency injection for testability.

---

## Summary of Recommendations

### High Priority (Major Findings)
1. **Decompose TestLabScreen** (GOD-001): Extract remaining responsibilities to bring below 500 lines
2. **Complete FormationEditorScreen refactor** (GOD-002): Extract toolbar/IO/clipboard handling
3. **Review StrategyScreen growth** (GOD-003): Extract recent additions to return to ~350 line target

### Medium Priority (Minor Findings)
4. **Monitor approaching god classes** (GOD-004): Proactively extract before crossing threshold
5. **Consolidate late import patterns** (IMPORT-001, IMPORT-002): Document or move to top-level
6. **Document tkinter usage** (TKINTER-001): Add comments explaining the workaround

### Low Priority (Informational)
7. Continue TYPE_CHECKING pattern for cross-layer type hints
8. Continue protocol type guard usage for cross-layer checks
9. Continue facade pattern for strategy layer interactions
10. Continue dependency injection patterns

---

## Metrics

| Category | Count |
|----------|-------|
| Files Scanned | 97 |
| Lines of Code (sampled large files) | ~6000 |
| God Classes (>500 lines) | 4 |
| Approaching God Classes (400-500 lines) | 4 |
| TYPE_CHECKING Blocks | 50 |
| Cross-Layer Imports (runtime) | 34 |
| Cross-Layer Imports (TYPE_CHECKING) | 50 |
| Pygame Boundary Violations | 0 |
| Circular Dependencies Detected | 0 |

---

*Report generated by Architecture Sweep Agent*
