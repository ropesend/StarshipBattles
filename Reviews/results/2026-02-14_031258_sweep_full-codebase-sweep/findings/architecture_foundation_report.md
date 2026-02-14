# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 36
- **Total Issues Found:** 2
- **Critical:** 0 | **Major:** 1 | **Minor:** 1 | **Info:** 0

## Findings

#### MAJOR: Research UI imports game.ui.renderer.camera at runtime
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:45`
**Issue:** The research module contains a late import `from game.ui.renderer.camera import Camera` inside the `_create_default_camera()` function. While the file documents this as a "PROJ-132 fix" to avoid layer violations at module level, the research package should not depend on the UI layer at all. The research package has its own `ui/` subpackage which arguably makes it a UI component itself, creating architectural ambiguity.
**Impact:**
- Research system is not fully headless-testable without pygame/UI dependencies
- Blurs the boundary between research data/logic and UI presentation
- Creates a hidden dependency that's not visible at module level
**Recommendation:**
1. Consider restructuring research as follows:
   - Move `game/research/ui/` contents to `game/ui/research/` (canonical location for UI)
   - Keep `game/research/data/` and `game/research/systems/` as the headless research layer
2. Alternatively, if research is intended to be a self-contained mini-application, document this explicitly and ensure all UI components stay within `game/research/ui/`
**Effort:** Medium

#### MINOR: Research UI subpackage uses pygame directly
**ID:** ADR-FND-002
**Location:** `game/research/ui/research_controls.py:11-14`, `game/research/ui/research_renderer.py:9`, `game/research/ui/research_scene.py:17-18`
**Issue:** The `game/research/ui/` subpackage contains direct pygame imports. According to the architecture rules, "Pygame is UI-only" and research should depend on core only. However, the existence of a `ui/` subpackage within research creates an exception to this rule.
**Impact:**
- If the research package is meant to be headless, this violates layering
- If research/ui is meant to be UI code, it should arguably live in `game/ui/research/`
- Creates architectural ambiguity about where UI code should live
**Recommendation:**
- If this is intentional (research as a self-contained sandbox app), document the architectural exception
- Consider moving `game/research/ui/` to `game/ui/research/` to follow the standard pattern where all pygame-dependent code lives under `game/ui/`
**Effort:** Medium

## Files Scanned

### game/core/ (17 files)
| File | Status |
|------|--------|
| `__init__.py` | Clean |
| `config.py` | Clean |
| `constants.py` | Clean |
| `error_codes.py` | Clean |
| `exceptions.py` | Clean |
| `hex_math.py` | Clean |
| `input_actions.py` | Clean |
| `json_utils.py` | Clean |
| `logger.py` | Clean |
| `math.py` | Clean |
| `paths.py` | Clean |
| `profiling.py` | Clean |
| `protocols.py` | Clean |
| `registry.py` | Clean |
| `resources.py` | Clean |
| `singleton.py` | Clean |
| `strategy_metadata.py` | Clean |
| `validation.py` | Clean |

### game/ai/ (8 files)
| File | Status |
|------|--------|
| `__init__.py` | Clean |
| `ai_factory.py` | Clean (correctly imports from simulation) |
| `behaviors.py` | Clean |
| `combat_utils.py` | Clean |
| `controller.py` | Clean |
| `strategy_manager.py` | Clean |
| `target_evaluator.py` | Clean |
| `interfaces/__init__.py` | Clean |
| `interfaces/controllable.py` | Clean |

### game/engine/ (4 files)
| File | Status |
|------|--------|
| `__init__.py` | Clean |
| `collision.py` | Clean |
| `physics.py` | Clean |
| `spatial.py` | Clean |

### game/research/ (9 files)
| File | Status |
|------|--------|
| `__init__.py` | Clean |
| `data/__init__.py` | Clean |
| `data/research_tracker.py` | Clean |
| `data/tech_node.py` | Clean |
| `data/tech_tree.py` | Clean |
| `systems/__init__.py` | Clean |
| `systems/research_service.py` | Clean |
| `ui/__init__.py` | See ADR-FND-002 |
| `ui/research_controls.py` | See ADR-FND-002 |
| `ui/research_renderer.py` | See ADR-FND-002 |
| `ui/research_scene.py` | See ADR-FND-001, ADR-FND-002 |

## Architecture Compliance Notes

### Correct Layer Dependencies Observed

1. **game/core/**: No dependencies on simulation, strategy, ui, or ai layers. All imports are standard library or local modules. The `math.py` file provides a pure-Python `Vector2` class that avoids pygame dependency.

2. **game/ai/**: Correctly imports from:
   - `game.core.*` (logger, constants, json_utils, singleton, strategy_metadata)
   - `game.simulation.interfaces.ai_controller` (via TYPE_CHECKING for protocol)
   - `game.engine.spatial` (via TYPE_CHECKING for SpatialGrid)

   No UI or strategy layer imports detected.

3. **game/engine/**: Only imports from:
   - `game.core.math` (Vector2)
   - `game.core.config` (PhysicsConfig, BattleConfig)

   No pygame, simulation, strategy, ui, or ai imports.

4. **game/research/data/** and **game/research/systems/**: Only import from:
   - `game.core.*` (logger, json_utils, paths)
   - Internal research modules

   Properly headless and testable.

### Design Patterns Observed

1. **Singleton Pattern**: Used correctly in `SingletonMeta` and applied to `Logger`, `Profiler`, `RegistryManager`, `StrategyManager`, `StrategyMetadataService`.

2. **Protocol Pattern**: `ICamera` in `game/core/protocols.py` allows research layer to depend on camera abstraction without importing concrete UI classes.

3. **Adapter Pattern**: `ShipControllableAdapter` in AI layer wraps Ship to implement `IControllable`, decoupling AI from specific entity implementations.

4. **Dependency Injection**: `ResearchTreeScene` accepts optional `camera` parameter (PROJ-132), allowing camera to be injected rather than created internally.

### No Pygame in Non-UI Layers

Verified that `import pygame` and `from pygame` do NOT appear in:
- `game/core/` (0 occurrences)
- `game/ai/` (0 occurrences)
- `game/engine/` (0 occurrences)

### No Circular Dependencies Detected

TYPE_CHECKING blocks are used appropriately:
- `game/core/protocols.py`: TYPE_CHECKING for HexCoord (same package)
- `game/ai/ai_factory.py`: TYPE_CHECKING for Ship, SpatialGrid (cross-layer type hints only)
- `game/research/data/research_tracker.py`: TYPE_CHECKING for TechTree (same package)
- `game/research/ui/*`: TYPE_CHECKING for ICamera, TechNode, NodeState (appropriate)

No evidence of "import here to avoid circular" patterns or mutually importing modules.

## Top 5 Priority Issues

1. **ADR-FND-001 (MAJOR)**: Research UI late-imports game.ui.renderer.camera - structural ambiguity about where research UI belongs architecturally.

2. **ADR-FND-002 (MINOR)**: Research UI contains pygame imports - while arguably acceptable for a self-contained sandbox, it creates inconsistency with the stated architecture rules.

---

*Sweep completed: 2026-02-14*
*Agent: Architecture Drift (Foundation Shard)*
