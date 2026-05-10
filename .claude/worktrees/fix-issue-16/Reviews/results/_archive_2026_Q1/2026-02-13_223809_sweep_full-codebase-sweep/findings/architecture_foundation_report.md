# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Files Scanned:** 36
- **Total Issues Found:** 4
- **Critical:** 0 | **Major:** 2 | **Minor:** 1 | **Info:** 1

## Findings

#### MAJOR: Research UI Layer Contains Late Import of game.ui.renderer.camera
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:45`
**Issue:** The research layer imports from game.ui inside a factory function to create a Camera instance. While this is mitigated by using a late import inside a function and dependency injection pattern (PROJ-132), the research module still has knowledge of and depends on game.ui internals.
**Impact:** The research layer is not fully decoupled from the UI layer. If game.ui.renderer.camera changes its API or location, research_scene.py must be updated. This creates a maintenance burden and prevents the research layer from being used in a headless context without the UI layer present.
**Recommendation:**
1. Create an `ICameraFactory` protocol in game.core.protocols
2. Have the caller (game.ui) inject a camera factory instead of letting research create its own camera
3. Alternatively, extract camera to game.core or game.engine since it's pure math (coordinate transformations)
**Effort:** Medium

#### MAJOR: Research UI Subdirectory Uses Pygame Directly
**ID:** ADR-FND-002
**Location:** `game/research/ui/research_controls.py:11-14`, `game/research/ui/research_renderer.py:9`, `game/research/ui/research_scene.py:17-18`
**Issue:** The `game/research/ui/` subdirectory imports pygame and pygame_gui directly. According to the architecture rules, pygame should only be used in `game/ui/`. While this is technically a UI component within research, it violates the principle that pygame is UI-layer-only.
**Impact:**
- The research module cannot be tested in a headless environment
- Pygame initialization is required to use any part of research.ui
- Coupling to pygame makes it harder to port to other rendering backends
**Recommendation:**
1. Move `game/research/ui/` to `game/ui/research/` to align with the layer architecture
2. Or create a clear interface boundary where research data layer provides pure data and UI layer handles all rendering
**Effort:** Complex (requires moving files and updating all imports)

#### MINOR: TYPE_CHECKING Block in ai_factory.py Imports from Both Simulation and Engine
**ID:** ADR-FND-003
**Location:** `game/ai/ai_factory.py:27-29`
**Issue:** The TYPE_CHECKING block imports `Ship` from `game.simulation.entities.ship` and `SpatialGrid` from `game.engine.spatial`. While TYPE_CHECKING imports don't create runtime dependencies, they indicate architectural awareness. The AI layer correctly depends on simulation, but SpatialGrid is in the engine layer which is supposed to be a thin orchestration layer.
**Impact:** Minor - TYPE_CHECKING imports are only used for static type checking and don't affect runtime. However, this indicates the dependency graph may not be perfectly clean.
**Recommendation:** Consider whether SpatialGrid belongs in game.engine or if it should be in game.core (pure data structures) or game.simulation (combat-related spatial indexing).
**Effort:** Simple (documentation/design clarification, no code changes required)

#### INFO: Core Layer Properly Isolates Strategy and UI Concerns
**ID:** ADR-FND-004
**Location:** `game/core/constants.py:84`, `game/core/config.py:137`
**Issue:** These files contain comments indicating code was moved FROM strategy/UI layers TO core, and notes about where UIConfig was moved. This is not a violation - it's evidence of proper refactoring. The comments reference game.strategy and game.ui but only in documentation/comments explaining migrations, not in actual imports.
**Impact:** None - this is positive evidence of proper layer separation. PLANET_RESOURCES was moved from game.strategy.data.planet to game.core.constants to eliminate a simulation->strategy dependency (PROJ-11). UIConfig was properly moved to game.ui.config (PROJ-113).
**Recommendation:** No action needed. These migrations demonstrate the project actively maintains layer boundaries.
**Effort:** N/A

## Observations

### Clean Architecture in Core Layer
The game/core layer has **zero** violations of the dependency rules:
- No imports from game.simulation, game.strategy, game.ui, or game.ai
- No pygame imports
- Provides pure utilities (math, logging, config, validation, paths, exceptions)
- Properly uses protocols for cross-layer type contracts (ICamera, IFleet, IPlanet, etc.)

### Clean Architecture in AI Layer
The game/ai layer properly depends only on:
- game.core (math, config, constants, protocols, logger)
- game.simulation (interfaces/ai_controller for IAIController protocol)
- No UI imports, no pygame imports
- Uses IControllable interface to decouple from Ship internals

### Clean Architecture in Engine Layer
The game/engine layer properly depends only on:
- game.core (math, config)
- No simulation, strategy, UI, or AI imports
- No pygame imports

### Research Layer Structure
The research layer has a mixed structure:
- `game/research/data/` and `game/research/systems/` - Clean, only depend on game.core
- `game/research/ui/` - Contains pygame usage, which violates "pygame is UI-only" rule

### No Circular Dependencies Detected
No circular import patterns found in the foundation layers. TYPE_CHECKING blocks are used appropriately for type hints without creating runtime dependencies.

### No God Classes
All classes are under 500 lines:
- Largest: `game/core/protocols.py` at 579 lines (but this is a protocols/interfaces file, not a single class)
- Largest actual class file: `game/ai/behaviors.py` at 520 lines (but contains multiple behavior classes)

## Top 5 Priority Issues
1. **ADR-FND-002** (Major): Research UI uses pygame directly - Move to game/ui/research/ or create proper interface boundary
2. **ADR-FND-001** (Major): Research scene imports Camera from game.ui - Improve DI pattern or extract Camera to lower layer
3. **ADR-FND-003** (Minor): SpatialGrid's layer placement could be clearer
4. *(No additional issues)* - Foundation layers are well-architected
5. *(No additional issues)* - Core, AI, and Engine layers are clean
