# PROJ-73: Rotating Warp Point Graphics

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-73` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-73 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add Animation State | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** All phases complete - Ready for Audit
**Last Action:** Phase 1 complete: animation state, renderer update wiring, rotation rendering
**Next Action:** Audit
**Blockers:** None

## Overview
Add slow, continuous rotation animation to warp point graphics on the strategy layer sector view. Each warp point rotates at a unique offset angle for visual variety. This is a purely visual enhancement with no gameplay impact.

## Goals
- Warp points rotate slowly and continuously (ambient animation)
- Each warp point has a different rotation offset (visual variety)
- Animation is smooth and frame-rate independent

## Scope
**In:**
- Add elapsed time tracking to StrategyRenderer
- Wire up renderer update in strategy screen
- Apply rotation during warp point rendering
- Use existing `scale_and_rotate_image()` utility

**Out:**
- Rotation speed configuration UI
- Per-warp-point rotation direction variation
- Shader-based rotation (pygame limitation)

## Key Files
| Component | File Path |
|-----------|-----------|
| Renderer | `game/ui/screens/strategy_renderer.py` |
| Strategy Screen | `game/ui/screens/strategy_screen.py` |
| Rotation Utility | `game/ui/utils.py` (existing, no changes) |
| WarpPoint Data | `game/strategy/data/galaxy.py` (reference only) |
| Camera (pattern ref) | `game/ui/renderer/camera.py` (reference only) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Visual test: warp points rotate smoothly with unique offsets
- [ ] Audit passed
- [ ] User verified
