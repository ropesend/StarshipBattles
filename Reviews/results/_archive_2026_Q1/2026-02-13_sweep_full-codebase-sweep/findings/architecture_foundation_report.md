# Architecture Drift Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 37
- **Total Issues Found:** 3
- **Critical:** 1 | **Major:** 1 | **Minor:** 1 | **Info:** 0

## Analysis Methodology

All 37 Python files in the assigned shard were examined for:
1. Import violations between layers
2. Pygame usage outside UI layer
3. Circular dependencies (TYPE_CHECKING blocks, late imports)
4. God classes (>500 LOC)
5. Data flow violations
6. Dependency direction violations

### Files Scanned by Directory

**game/core/** (18 files):
- `__init__.py`, `math.py`, `json_utils.py`, `paths.py`, `input_actions.py`
- `exceptions.py`, `error_codes.py`, `singleton.py`, `validation.py`, `logger.py`
- `config.py`, `strategy_metadata.py`, `profiling.py`, `protocols.py`, `resources.py`
- `registry.py`, `constants.py`, `hex_math.py`

**game/ai/** (8 files):
- `__init__.py`, `combat_utils.py`, `target_evaluator.py`, `controller.py`
- `strategy_manager.py`, `behaviors.py`, `interfaces/__init__.py`, `interfaces/controllable.py`

**game/research/** (11 files):
- `__init__.py`, `data/__init__.py`, `data/tech_node.py`, `data/tech_tree.py`
- `data/research_tracker.py`, `systems/__init__.py`, `systems/research_service.py`
- `ui/__init__.py`, `ui/research_controls.py`, `ui/research_renderer.py`, `ui/research_scene.py`

**game/engine/** (4 files):
- `__init__.py`, `physics.py`, `collision.py`, `spatial.py`

---

## Findings

#### CRITICAL: Research UI Layer Imports Concrete Camera from game.ui
**ID:** ADR-FND-001
**Location:** `game/research/ui/research_scene.py:19`
**Issue:** The research scene imports the concrete Camera class from `game.ui.renderer.camera`, creating a direct dependency from the research layer to the UI layer.
**Code:**
```python
from game.ui.renderer.camera import Camera
```
**Impact:**
- The research layer cannot be tested without the full UI layer loaded
- Creates a coupling that violates the architectural intent for research to be a standalone module
- If Camera implementation changes, research layer must be updated
**Recommendation:**
- Move Camera to a shared location (e.g., `game.core.camera` or `game.engine.camera`)
- OR create a minimal camera interface/factory in core that research can use
- The renderer already uses `ICamera` protocol correctly; the scene should accept a camera via constructor injection
**Effort:** Medium

---

#### MAJOR: protocols.py is Approaching God Class Territory
**ID:** ADR-FND-002
**Location:** `game/core/protocols.py` (547 lines)
**Issue:** The protocols module has grown to 547 lines with 20+ protocol definitions. While each protocol is individually small, the module as a whole is becoming a catch-all for interface definitions across all layers.
**Impact:**
- Changes to any protocol require reading through the entire file
- New developers struggle to find relevant protocols
- Risk of unrelated protocols evolving dependencies on each other
- Import of this module loads all protocol definitions even if only one is needed
**Recommendation:**
- Split into domain-specific protocol modules:
  - `protocols/strategy.py` (IFleet, IPlanet, IStarSystem, IWarpPoint, etc.)
  - `protocols/combat.py` (ICombatant, IDamageable, IPostBattleShip)
  - `protocols/registry.py` (IRegistryProvider, IResourceReader)
  - `protocols/ui.py` (ICamera, IScene)
- Keep `protocols/__init__.py` re-exporting all for backward compatibility
**Effort:** Medium

---

#### MINOR: behaviors.py File Growing Large
**ID:** ADR-FND-003
**Location:** `game/ai/behaviors.py` (520 lines)
**Issue:** The AI behaviors module contains 13 behavior classes in a single file. While still technically under the 500-line threshold for "god class," it's growing toward that boundary and mixing production behaviors with test-only behaviors.
**Impact:**
- Harder to navigate and understand individual behaviors
- Test behaviors (`DoNothingBehavior`, `StationaryFireBehavior`, `ErraticBehavior`) mixed with production behaviors
- Growing toward maintainability concerns
**Recommendation:**
- Consider splitting into:
  - `behaviors/combat.py` (KiteBehavior, AttackRunBehavior, RamBehavior, FleeBehavior)
  - `behaviors/formation.py` (FormationBehavior)
  - `behaviors/utility.py` (OrbitBehavior)
  - `behaviors/test.py` (DoNothingBehavior, StationaryFireBehavior, StraightLineBehavior, RotateOnlyBehavior, ErraticBehavior)
**Effort:** Simple

---

## Positive Observations

### Clean Layer Separations Found

1. **game/core/** has NO imports from simulation, strategy, ui, or ai layers
   - All 18 files correctly depend only on core modules and standard library

2. **game/engine/** has NO imports from simulation, strategy, ui, or ai layers
   - Uses only `game.core.math` and `game.core.config`

3. **game/ai/** has NO imports from ui or strategy layers
   - Correctly uses only core modules and internal AI modules

4. **Pygame isolation is excellent in most areas**
   - NO pygame imports in `game/core/`, `game/ai/`, or `game/engine/`
   - Pygame usage in `game/research/ui/` is appropriate (UI subfolder)

5. **TYPE_CHECKING usage is appropriate**
   - `game/core/protocols.py` uses TYPE_CHECKING only for same-layer imports (HexCoord)
   - `game/research/data/research_tracker.py` uses TYPE_CHECKING for same-package imports
   - No TYPE_CHECKING blocks are hiding cross-layer violations

### Well-Designed Patterns

1. **ICamera protocol in core** - The protocol is defined in core, allowing research renderer to use it without depending on UI
2. **StrategyMetadataService** - Properly decouples UI from AI layer for strategy display
3. **IControllable interface** - Clean abstraction between AI and simulation entities
4. **Framework-agnostic Vector2** - `game/core/math.py` provides a pygame-independent Vector2 implementation

---

## Top 5 Priority Issues

1. **ADR-FND-001 (CRITICAL)**: Research UI imports Camera from game.ui - This is the only true layer violation in the shard and should be addressed to maintain architectural integrity.

2. **ADR-FND-002 (MAJOR)**: protocols.py growing large - While functional, splitting this file would improve maintainability and make the architecture more discoverable.

3. **ADR-FND-003 (MINOR)**: behaviors.py approaching size limit - Preventive refactoring to split production and test behaviors would improve code organization.

---

## Recommendations Summary

| ID | Severity | Issue | Effort | Priority |
|----|----------|-------|--------|----------|
| ADR-FND-001 | CRITICAL | Camera import crosses layers | Medium | High |
| ADR-FND-002 | MAJOR | protocols.py too large | Medium | Medium |
| ADR-FND-003 | MINOR | behaviors.py growing | Simple | Low |

---

*Report generated: 2026-02-13*
*Sweep Agent: Architecture Drift*
*Shard: Foundation (core, ai, research, engine)*
