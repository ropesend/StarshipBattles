# PROJ-52: Galaxy Generation Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-52` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-52 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Foundation & Math Engine | **Complete** | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Galaxy Generator Integration | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Performance Optimizations | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Galaxy Layout Sandbox (Mode A) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Physics-Driven Systems | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. System Inspector (Mode B) | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-01-31 14:30
**Active Phase:** Phase 2 - Galaxy Generator Integration
**Last Action:** Phase 1 complete - all 85 new tests passing (5926 total)
**Next Action:** Create placement strategy interface and integrate with Galaxy class
**Blockers:** None

## Overview
Replace hardcoded procedural galaxy generation with a fully data-driven, layered system using:
1. **Composite Density Fields** for galaxy layouts (7 types: Spiral, Cluster, Barred, Ring, Irregular, Diamond, Uniform)
2. **Physics-First Simulation** for planetary classification
3. **Visual Verification Tool** (Galaxy Generation Sandbox) in main menu

## Goals
- Implement data-driven galaxy layouts via JSON configuration
- Support 7 distinct galaxy types with unique visual characteristics
- Enable 2500 system galaxies with 60 FPS rendering
- Provide visual sandbox for rapid layout iteration and physics inspection
- Add deterministic generation via seed control

## Scope
**In:**
- Density field primitives and composition system
- Galaxy layout JSON configuration
- Placement strategy integration with Galaxy class
- Performance optimizations for scale
- Galaxy Generation Sandbox UI (both modes)
- System blueprints and physics-derived classification

**Out:**
- Backward compatibility with existing saves (clean break)
- AI behavior changes (use existing pathfinding)
- Gameplay balance changes
- New ship types or combat mechanics

## Key Files
| Component | File Path | Key Lines |
|-----------|-----------|-----------|
| Galaxy Generation | `game/strategy/data/galaxy.py` | `generate_systems()` 198-236 |
| Game Session | `game/strategy/engine/game_session.py` | `_initialize_galaxy()` 126-130 |
| Game Config | `game/strategy/engine/game_config.py` | `GameConfig` 99-162 |
| Strategy Renderer | `game/ui/screens/strategy_renderer.py` | `_draw_warp_lanes()` 212-251 |
| Main App | `game/app.py` | `GameState` enum, menu buttons 135-162 |
| **NEW: DensityMap** | `game/strategy/generation/density/density_map.py` | Composite density field |
| **NEW: Primitives** | `game/strategy/generation/density/primitives/` | 6 density primitives |
| **NEW: Layout Loader** | `game/strategy/generation/loaders/galaxy_layouts_loader.py` | JSON config loading |
| **NEW: Layouts Config** | `data/galaxy_layouts.json` | 7 galaxy type definitions |

## User Decisions
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Save Compatibility | Clean break | Simpler implementation, cleaner architecture |
| Sandbox Priority | Build together | Both modes developed in parallel |
| Development Strategy | Parallel implementation | New system alongside old, config flag switch |
| Galaxy Types | All 7 types | Full implementation from the start |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Full plan: `C:\Users\rossr\.claude\plans\crispy-gliding-garden.md`

## Verification
- [x] Baseline tests passing (5841 passed, 5 skipped)
- [ ] All phase checklists complete
- [ ] All tests passing after implementation
- [ ] Audit passed
- [ ] User verified
