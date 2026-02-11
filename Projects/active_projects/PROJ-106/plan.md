# PROJ-106: Architecture Layer Violations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-106` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-106 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Simple Encapsulation Fixes | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Remove Deprecated Legacy AI Paths | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Create Strategy Metadata Service | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Centralize SimulationDesignLoader Access | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Fix Research/UI Camera Dependency | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. BattleUIService Contract Hardening | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Audit and Final Verification | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Phase 4 (Centralize SimulationDesignLoader Access)
**Last Action:** Phase 3 Complete -- Created StrategyMetadataService in game.core, updated all 8 UI files, zero AI imports remain in UI (except battle_orchestrator.py)
**Next Action:** Begin Phase 4 (route SimulationDesignLoader through DesignLoaderAdapter)
**Blockers:** None

## Overview
Fix architecture layer violations identified during the 2026-02-10 full-codebase sweep. These are cross-layer dependency violations where modules import from layers they should not depend on, breaking the established architecture rules (Core < Simulation < Strategy < UI, with AI depending on Simulation/Strategy only).

## Goals
- Eliminate all cross-layer import violations
- Ensure simulation layer has zero pygame dependencies
- Remove unauthorized AI layer imports from UI
- Clean up private attribute access across layer boundaries
- Strengthen layer contracts with proper interfaces/protocols

## Scope
**In:**
- Cross-layer import violations (pygame in simulation, AI in UI, etc.)
- Private attribute access across module boundaries
- Missing interface contracts between layers
- Fragile getattr() chains indicating missing protocols
- Deprecated legacy code paths that bypass proper layer boundaries

**Out:**
- God class decomposition (covered by PROJ-86/87/88/89)
- Test coverage gaps (covered by PROJ-110/111)
- Code duplication (covered by PROJ-108)
- Law of Demeter violations (ADR-UI1-006, 27 files -- too broad, deferred)
- DI pattern standardization (ADR-UI2-006 -- separate concern)

## Phase Overview

### Phase 1: Simple Encapsulation Fixes (7 tasks)
Quick wins requiring no new abstractions. Replace pygame in simulation, add public property/method wrappers for private attributes, fix thread safety.

### Phase 2: Remove Deprecated Legacy AI Paths (4 tasks)
Remove deprecated code in BattleEngine that directly imports from game.ai. All production code already uses the ai_factory pattern from PROJ-43.

### Phase 3: Create Strategy Metadata Service (10 tasks)
Create `StrategyMetadataService` in game.core to provide strategy names/IDs to UI. Update 8 UI files to use it instead of importing from game.ai.strategy_manager.

### Phase 4: Centralize SimulationDesignLoader Access (4 tasks)
Route all UI-layer SimulationDesignLoader usage through the existing DesignLoaderAdapter. Eliminates 4 files with direct simulation-layer imports.

### Phase 5: Fix Research/UI Camera Dependency (4 tasks)
Create ICamera protocol in game.core. Update research layer to depend on protocol instead of game.ui Camera class.

### Phase 6: BattleUIService Contract Hardening (3 tasks)
Replace defensive getattr() chains with direct attribute access now that Ship interface is stable. Fix hardcoded magic numbers in game_renderer.

### Phase 7: Audit and Final Verification (4 tasks)
Systematic cross-layer import scan, private attribute audit, document deferred findings.

## Source: Sweep Findings

### CRITICAL Findings (Addressed)

| ID | Finding | Phase |
|----|---------|-------|
| ADR-SIM-001 | Pygame import in simulation layer | Phase 1 |
| ADR-SIM-002 | AI layer imports in simulation (deprecated paths) | Phase 2 |
| ADR-FND-001 | Research/UI cross-layer dependency | Phase 5 |
| ADR-UI1-001 | Unauthorized AI layer dependencies (8 UI files) | Phase 3 |
| ADR-UI1-002 | UI importing simulation service internals | Phase 4 |
| ADR-UI2-001 | Private _resources attribute access | Phase 1 |
| ADR-UI2-002 | Excessive getattr() chains (fragile contract) | Phase 6 |

### MAJOR Findings (Addressed)

| ID | Finding | Phase |
|----|---------|-------|
| ADR-UI2-003 | ShipThemeManager thread safety gap | Phase 1 (already fixed) |
| ADR-UI2-004 | game_renderer.py hardcoded radius values | Phase 6 |
| ADR-UI2-005 | DesignLoaderAdapter lazy import pattern | Phase 1 |

### MINOR Findings (Addressed)

| ID | Finding | Phase |
|----|---------|-------|
| ADR-SIM-005 | Private _registries attribute access | Phase 1 |
| ADR-SIM-006 | Private _hp_ratio_dirty modification | Phase 1 |
| ADR-UI1-009 | Private session._facade access | Phase 1 (false positive) |

### Findings Deferred (Out of Scope)

| ID | Finding | Reason |
|----|---------|--------|
| ADR-UI2-006 | Inconsistent DI patterns | Separate DI standardization project |
| ADR-UI1-006 | Law of Demeter violations (27 files) | Too broad for this project |
| ADR-UI1-007 | Strategy data objects in UI | Requires DTO extraction design |
| ADR-UI1-008 | TYPE_CHECKING imports insufficient | Acceptable trade-off |
| ADR-UI2-009 | TYPE_CHECKING not isolated in BattleUIService | Acceptable trade-off |
| ADR-UI2-010 | BattleOrchestrator cross-layer imports | Intentional design |
| ADR-SIM-007 | Simulation-AI coupling is controlled | Monitoring only |

### God Class Findings (Out of Scope -- Other Projects)

| ID | Finding | Project |
|----|---------|---------|
| ADR-SIM-003 | Ship (804 lines) | PROJ-88 |
| ADR-SIM-004 | BattleEngine (674 lines) | PROJ-88 |
| ADR-FND-002 | behaviors.py (513 lines) | PROJ-88 |
| ADR-FND-003 | AIController (479 lines) | PROJ-88 |
| ADR-FND-004 | TargetEvaluator (459 lines) | PROJ-88 |
| ADR-UI1-003 | TestLabScreen (1837 lines) | PROJ-89 |
| ADR-UI1-004 | BuilderScreen (1124 lines) | PROJ-89 |
| ADR-UI1-005 | FormationEditorScreen (929 lines) | PROJ-89 |
| ADR-STR-001 | ProductionEngine (731 lines) | PROJ-87 |
| ADR-STR-002 | Galaxy (707 lines) | PROJ-87 |
| ADR-STR-003 | ShipInstance (688 lines) | PROJ-87 |
| ADR-STR-004 | Stars (560 lines) | PROJ-87 |

## Key Files
| Component | File Path |
|-----------|-----------|
| Pygame in Sim | `game/simulation/services/design_loader.py` |
| AI imports in Sim | `game/simulation/systems/battle_engine.py` |
| AI factory (boundary) | `game/simulation/factories/ai_factory.py` |
| Research/UI coupling | `game/research/ui/research_scene.py`, `research_renderer.py` |
| Strategy metadata (NEW) | `game/core/strategy_metadata.py` |
| AI imports in UI (8 files) | See Phase 3 tasks |
| Sim imports in UI | `game/ui/screens/strategy_screen.py` + 3 more |
| Design loader adapter | `game/ui/services/design_loader_adapter.py` |
| BattleUIService | `game/ui/services/battle_ui_service.py` |
| GameRenderer | `game/ui/renderer/game_renderer.py` |
| Ship (registries) | `game/simulation/entities/ship.py` |
| Component (cache dirty) | `game/simulation/components/component.py` |
| Camera | `game/ui/renderer/camera.py` |
| Camera protocol (NEW) | `game/core/protocols.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- **Source sweep:** `Reviews/results/2026-02-10_sweep_full-codebase-sweep/findings/architecture_*.md`

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (8164+)
- [ ] No cross-layer imports remain (verified by Phase 7 audit)
- [ ] Audit passed
- [ ] User verified
