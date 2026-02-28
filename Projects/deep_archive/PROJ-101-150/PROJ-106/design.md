# PROJ-106: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Architecture Layer Rules
The codebase follows a strict layered architecture:

```
Core (game/core/)           -- Foundation, no external layer dependencies
   |
Engine (game/engine/)       -- Physics/spatial, depends on Core only
   |
Simulation (game/simulation/) -- Combat simulation, depends on Core + Engine
   |
Strategy (game/strategy/)   -- Galaxy/fleet management, depends on Core + Simulation
   |
AI (game/ai/)               -- AI controllers, depends on Core + Simulation + Strategy
   |
Research (game/research/)   -- Tech tree, depends on Core only
   |
UI (game/ui/)               -- Top layer, can depend on all others
```

**Key constraint:** Dependencies flow downward only. No layer may import from a layer above it in the stack.

### Violations Found (by severity)

**Simulation layer violations:**
- `design_loader.py` imports `pygame` -- simulation must be framework-agnostic
- `battle_engine.py` has deprecated legacy paths that import from `game.ai` directly
- `battle_engine.py:485` accesses `ship._registries` (private attribute)
- `battle_state.py:301` modifies `component._hp_ratio_dirty` (private attribute)

**Research layer violations:**
- `research_scene.py` and `research_renderer.py` import `Camera` from `game.ui`

**UI layer violations (AI coupling):**
- 8 files import `StrategyManager` from `game.ai` for dropdown population
- These use StrategyManager.instance().strategies to get strategy names/IDs

**UI layer violations (Simulation coupling):**
- 4 files import `SimulationDesignLoader` directly, bypassing the DesignLoaderAdapter
- `BattleUIService` accesses private `_resources` attribute of ResourceRegistry

**Contract fragility:**
- `BattleUIService` has 20+ getattr() calls that are overly defensive for a stable interface
- `game_renderer.py` has hardcoded magic numbers that should use LayerDefaults

## Swarm Findings Summary

### Architecture

The codebase's layer boundaries are largely well-maintained:
- **Core layer is clean** -- zero upward dependencies
- **Strategy layer is clean** -- correct dependency direction, facade pattern, DTOs
- **Engine layer is clean** -- TYPE_CHECKING blocks properly used
- **AI layer respects rules** -- only imports from core, simulation, strategy

The violations are concentrated in:
1. Simulation layer (pygame, legacy AI paths)
2. UI layer (AI coupling for strategy names, simulation service coupling)
3. Research layer (Camera import from UI)

### Key Patterns to Reuse

- **AIControllerFactory** (`game/simulation/factories/ai_factory.py`): The pattern for isolating cross-layer AI imports to a single factory class. Created in PROJ-43.
- **DesignLoaderAdapter** (`game/ui/services/design_loader_adapter.py`): Existing facade for SimulationDesignLoader access from UI. Needs to be used consistently.
- **StrategySessionFacade** (`game/strategy/facade/`): Clean facade pattern for UI-to-strategy communication. Model for new StrategyMetadataService.
- **ResourceRegistry.get_all_resources()** (`game/simulation/systems/resource_manager.py:200`): Existing public API that BattleUIService should use instead of private attribute access.
- **game.core.math.Vector2** (`game/core/math.py`): Framework-agnostic Vector2 that simulation layer should use instead of pygame.math.Vector2.

### Dependencies and Risks

1. **Phase 2 (legacy path removal)** -- Risk: Some test fixtures might use BattleEngine.start() without ai_factory. Mitigation: Audit all callers before removing.
2. **Phase 3 (StrategyMetadataService)** -- Risk: WorkshopDataLoader uses StrategyManager for both reading AND writing (load_data, clear). The new service must support the same lifecycle. Mitigation: Include load_data() and clear() on the service.
3. **Phase 4 (DesignLoaderAdapter)** -- Risk: BuildQueueController may call SimulationDesignLoader-specific methods not on the adapter. Mitigation: Check API compatibility before switching types.
4. **Phase 5 (Camera protocol)** -- Risk: ResearchTreeScene may create Camera internally rather than receiving it via DI. Mitigation: May need to keep runtime import for construction while using protocol for type hints.
5. **Phase 6 (getattr removal)** -- Risk: Some Ship properties may be genuinely optional depending on context. Mitigation: Only remove getattr() for properties confirmed in Ship.__init__.

### Opportunities Discovered

- **StrategyMetadataService** could eventually serve as the single source of truth for all strategy display data, replacing scattered dict lookups across 8 UI files
- Camera protocol in core could be reused by future rendering layers beyond research
- Phase 2's legacy path removal simplifies BattleEngine significantly (~40 lines removed)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Design Choices

1. **StrategyMetadataService in game.core (not game.strategy):** The service provides display-facing metadata (names, IDs). It belongs in core because it's consumed by both UI and AI layers. The AI layer populates it; the UI layer reads it.

2. **ICamera Protocol (not ABC, not move Camera to core):** Camera depends on pygame internally, so moving it to core would require refactoring Camera internals. A Protocol is zero-runtime-cost and doesn't require Camera to inherit from anything.

3. **Keep DesignLoaderAdapter as facade:** The adapter already exists from PROJ-43. We just need to use it consistently rather than creating a new abstraction.

4. **Replace getattr() selectively:** Only remove getattr() for Ship properties confirmed in __init__. Keep it for genuinely optional properties like `source_file`.

5. **Deferred findings:** Law of Demeter (27 files) and DI standardization are out of scope. They are real issues but too broad for this architecture-focused project.
