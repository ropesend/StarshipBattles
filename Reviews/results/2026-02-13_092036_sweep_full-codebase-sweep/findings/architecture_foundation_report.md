# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 42
- **Total Issues Found:** 4
- **Critical:** 1 | **Major:** 1 | **Minor:** 1 | **Info:** 1

## Findings

#### CRITICAL: Research UI layer imports from game.ui
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** The research module imports `Camera` from `game.ui.renderer.camera`. According to the architecture rules, the research layer should only depend on core. This violates the layer hierarchy by making research dependent on the UI layer.
**Import line:** `from game.ui.renderer.camera import Camera`
**Impact:**
- The research module cannot be used without the UI layer being available
- Creates a circular dependency concern if UI needs to import from research
- Prevents headless operation of research systems for testing or server-side use
- Breaks the single-direction dependency flow
**Recommendation:**
- Extract a `Camera` interface/protocol to `game.core.protocols` (similar to `ICamera` which already exists)
- Have the research scene accept the camera via dependency injection using the `ICamera` protocol
- Alternatively, move `ResearchTreeScene` entirely to `game.ui` since it is fundamentally a UI component
**Effort:** Medium

#### MAJOR: IControllable interface exceeds god class metrics
**ID:** ADR-FND-002
**Location:** `game/ai/interfaces/controllable.py:1-478`
**Issue:** The `IControllable` interface and `ShipControllableAdapter` class together span 478 lines with 78 methods. While the adapter pattern is appropriate, the interface defines too many methods (40+ abstract methods), indicating the interface may be doing too much.
**Impact:**
- High cognitive load for implementers
- Difficult to maintain as changes require updating many locations
- Increased coupling between AI and Ship implementation details
- Testing requires extensive mock setup
**Recommendation:**
- Consider splitting into smaller role-specific interfaces (e.g., `IMovable`, `ICombatant`, `IFormationMember`)
- Apply Interface Segregation Principle (ISP)
- Group related methods and extract sub-interfaces
**Effort:** Complex

#### MINOR: protocols.py exceeds 500 lines
**ID:** ADR-FND-003
**Location:** `game/core/protocols.py:1-547`
**Issue:** The protocols module contains 547 lines with 67 functions/methods. While this is not a god class per se (protocols are intentionally thin), the file is becoming a catch-all for all protocol definitions in the project.
**Impact:**
- Increasing file size makes navigation difficult
- Risk of becoming a maintenance bottleneck
- Changes to one protocol may accidentally affect others
**Recommendation:**
- Consider splitting protocols by domain (e.g., `protocols/combat.py`, `protocols/registry.py`, `protocols/camera.py`)
- Use a `protocols/` sub-package with focused modules
**Effort:** Simple

#### INFO: Research module structure mixes layers internally
**ID:** ADR-FND-004
**Location:** `game/research/ui/`
**Issue:** The research module has its own internal `ui/` subdirectory containing `research_scene.py`, `research_controls.py`, and `research_renderer.py`. These are UI components that use pygame directly (`import pygame`, `import pygame_gui`).
**Impact:**
- The research module is not purely a core/data layer module
- The internal structure mirrors the project's main layer structure, which may cause confusion
- Future maintainers may be unsure whether research UI belongs in `game/research/ui/` or `game/ui/research/`
**Recommendation:**
- Clarify the research module's role: either (a) make it a pure data/logic layer and move UI to `game/ui/research/`, or (b) explicitly document that research is a self-contained feature module with its own UI
- The current approach (self-contained feature module) is valid but should be documented
**Effort:** Simple (documentation) or Medium (restructuring)

## Analysis Details

### Phase 1: Import Graph Analysis

**game/core/ (18 files):** CLEAN
- All imports are from Python standard library or internal game.core modules
- No pygame imports
- No imports from simulation, strategy, ui, or ai layers

**game/ai/ (9 files):** CLEAN
- Imports from game.core: YES (appropriate)
- Imports from game.simulation: YES (appropriate - AI depends on simulation)
- Imports from game.strategy: NO
- Imports from game.ui: NO
- TYPE_CHECKING imports from simulation for type hints: YES (acceptable pattern)

**game/engine/ (4 files):** CLEAN
- Only imports from game.core (math, config)
- No pygame imports
- No simulation, strategy, ui, or ai imports

**game/research/ (11 files):** VIOLATION FOUND
- Data layer (game/research/data/): Only imports from game.core - CLEAN
- Systems layer (game/research/systems/): Only imports from game.core and internal research modules - CLEAN
- UI layer (game/research/ui/):
  - Uses pygame and pygame_gui directly (expected for UI)
  - Imports from game.ui.renderer.camera - VIOLATION

### Phase 2: Pygame Boundary Violations

**game/core/:** No pygame imports found
**game/ai/:** No pygame imports found
**game/engine/:** No pygame imports found
**game/research/data/:** No pygame imports found
**game/research/systems/:** No pygame imports found
**game/research/ui/:** Uses pygame (expected - this is the UI layer of research)

### Phase 3: Circular Dependencies

No circular import patterns detected in the scanned modules:
- No "import here to avoid circular" comments (only documentation mentions)
- TYPE_CHECKING blocks used appropriately for type hints only
- No mutual A->B and B->A import patterns found

### Phase 4: God Classes

| File | Lines | Methods | Assessment |
|------|-------|---------|------------|
| game/core/protocols.py | 547 | 67 | Near threshold - monitor |
| game/ai/behaviors.py | 520 | 18 | Multiple small behavior classes - OK |
| game/ai/interfaces/controllable.py | 478 | 78 | Interface too large - should split |
| game/research/ui/research_controls.py | 470 | ~20 | UI panel - acceptable |
| game/ai/controller.py | 450 | ~15 | Complex controller - monitor |

### Phase 5: Data Flow Violations

No data flow violations detected:
- No UI-specific data (colors, fonts, pixel positions) flowing into lower layers
- No screen resolution dependencies in core/data modules
- Research tracker uses abstract data structures, not UI-specific types

### Phase 6: Dependency Direction Violations

One violation found:
- research.ui -> ui.renderer (ADR-FND-001)

No other reverse dependencies detected:
- No lower layers registering callbacks to higher layers
- No UI-specific exceptions in lower layers
- No abstract classes designed around UI needs in core/engine

## Top 5 Priority Issues

1. **ADR-FND-001 (CRITICAL):** Research module importing from game.ui breaks layer boundaries. This should be fixed before the research module grows further. Either use dependency injection with ICamera protocol or move the UI components to game/ui.

2. **ADR-FND-002 (MAJOR):** IControllable interface with 40+ methods is too large. Apply Interface Segregation Principle by splitting into role-specific interfaces (IMovable, ICombatant, IFormationMember).

3. **ADR-FND-003 (MINOR):** protocols.py growing beyond 500 lines. Consider splitting into a protocols/ sub-package before it becomes harder to refactor.

4. **ADR-FND-004 (INFO):** Research module structure should be documented to clarify whether it's a self-contained feature module or whether its UI should live in game/ui.

5. **(Observation):** The engine layer is well-isolated and follows architecture rules strictly. The core layer is also clean with no inappropriate dependencies.
