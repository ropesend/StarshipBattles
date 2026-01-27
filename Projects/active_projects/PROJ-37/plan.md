# PROJ-37: Fragile Asset Loading Refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-37` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-37 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Test Foundation | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Manifest Extension | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extend RaceAssetLoader | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor strategy_scene | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-27
**Active Phase:** Planning Complete - Awaiting Approval
**Last Action:** Completed Phase B Swarm Review with 6 agents, created detailed plan
**Next Action:** User approval, then run `pytest tests/` baseline, begin Phase 1
**Blockers:** None

## Overview
Refactor hardcoded asset paths and magic numbers in `strategy_scene.py` (lines 435-508) to use centralized configuration and existing asset management infrastructure. This eliminates brittle path strings and RGB threshold magic numbers by leveraging the existing `RaceAssetLoader` and `asset_manifest.json`.

## Goals
- Move hardcoded asset paths to use `RaceAssetLoader` (extend with empire asset methods)
- Move star color RGB thresholds from code to `asset_manifest.json`
- Eliminate magic numbers (100, 150, 200) for color classification
- Reduce `_load_assets()` from 55+ lines of path logic to delegated loader calls
- Maintain backward compatibility with existing saves

## Scope
**In:**
- `game/ui/screens/strategy_scene.py` lines 435-508 (asset loading + color mapping)
- `game/ui/screens/race_asset_loader.py` (extend with empire asset methods)
- `assets/asset_manifest.json` (add star_colors section)
- `game/assets/asset_manager.py` (add color lookup method)
- New unit tests for star color mapping and empire asset loading

**Out:**
- ShipThemeManager refactoring
- Performance optimizations (lazy loading, cache cleanup)
- Other asset loaders (SpriteManager, etc.)
- UI changes

## Key Files
| Component | File Path | Lines |
|-----------|-----------|-------|
| Asset Loading (refactor target) | `game/ui/screens/strategy_scene.py` | 435-508 |
| Star Color Logic | `game/ui/screens/strategy_scene.py` | 497-508 |
| RaceAssetLoader (extend) | `game/ui/screens/race_asset_loader.py` | All |
| Asset Manifest | `assets/asset_manifest.json` | All |
| AssetManager | `game/assets/asset_manager.py` | All |
| StrategyRenderer (consumer) | `game/ui/screens/strategy_renderer.py` | 462-524 |
| Empire class | `game/strategy/data/empire.py` | 1-14 |

## Related Documents
- [design.md](design.md) - Architecture analysis and swarm findings
- [decisions.md](decisions.md) - Full decisions log

## Verification
### Project Start (REQUIRED)
- [ ] Run `pytest tests/` - all tests pass (establishes baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: Start new game, verify empires have correct flags/icons
- [ ] Manual test: Load existing save, verify assets load correctly

### Final Verification
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] Start new game with 4+ empires, different races and themes
- [ ] Verify star colors render correctly (red, blue, yellow, white, orange stars visible)
- [ ] Verify colony flags appear on owned planets
- [ ] Verify fleet icons appear with correct skins
- [ ] Load a save from before the refactor - verify backward compatibility
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
