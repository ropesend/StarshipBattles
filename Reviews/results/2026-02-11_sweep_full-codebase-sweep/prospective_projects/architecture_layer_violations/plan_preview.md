# PROJ-XX: Architecture Layer Violations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-XX` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-XX [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Layer Purification | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Simulation Layer Isolation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Strategy Layer Boundaries | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI Encapsulation | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Circular Import Cleanup | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-11
**Active Phase:** Planning
**Last Action:** Project created from sweep findings
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Remove all cross-layer dependency violations: pygame and tkinter imports in core/simulation, UI concerns leaking into data layers, circular dependency workarounds, and encapsulation breaches. This restores the intended architecture where Core has no framework dependencies, Simulation depends only on Core, and UI-specific code stays in the UI layer.

## Goals
- Remove all pygame imports from `game/core/` (input_mapper, screenshot_manager, constants, config)
- Remove tkinter dependency from `game/simulation/systems/persistence.py`
- Fix all TYPE_CHECKING import violations that leak layer boundaries
- Eliminate circular dependency workarounds (lazy/late imports) by proper dependency inversion
- Ensure UI layer uses facades for data mutation rather than direct strategy object manipulation
- Extract UI-specific data (colors, display formatting) from simulation and strategy layers
- Enable headless operation of core and simulation layers without pygame installed

## Scope
**In:**
- All cross-layer import violations across core, simulation, strategy, and UI layers
- TYPE_CHECKING import boundary violations
- Circular dependency workarounds (lazy imports, late imports)
- UI concern leakage into non-UI layers (colors, display config, visual properties)
- Encapsulation violations (private attribute access across module boundaries)

**Out:**
- God class decomposition (separate project)
- Legacy dead code removal (separate project)
- New feature development beyond remediation
- Other sweep findings not related to layer violations

## Key Files
| Component | File Path |
|-----------|-----------|
| InputMapper (pygame in core) | `game/core/input_mapper.py` |
| ScreenshotManager (pygame in core) | `game/core/screenshot_manager.py` |
| ShipIO (tkinter in sim) | `game/simulation/systems/persistence.py` |
| AIControllerFactory (ai import in sim) | `game/simulation/factories/ai_factory.py` |
| ResearchScene (ui import in research) | `game/research/ui/research_scene.py` |
| Core Protocols (sim TYPE_CHECKING) | `game/core/protocols.py` |
| Galaxy (circular deps) | `game/strategy/data/galaxy.py` |
| GameRenderer (sim direct access) | `game/ui/renderer/game_renderer.py` |
| TestLabScreen (test infra imports) | `game/ui/screens/test_lab/screen.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] `game/core/` has zero pygame or tkinter imports
- [ ] `game/simulation/` has zero UI framework imports
- [ ] No circular dependency workarounds remain in affected files
- [ ] Audit passed
- [ ] User verified
