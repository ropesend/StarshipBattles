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
| 1. Test Foundation | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Manifest Extension | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extend RaceAssetLoader | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Refactor strategy_scene | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Update Tests | Complete (audit verified) | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-01-28
**Active Phase:** AUDIT PASSED - Pending user verification
**Last Action:** Audit cycle 1 passed with no significant issues. All automated tests verified.
**Next Action:** User manual verification required (Task 5.4), then close project.
**Blockers:** None

**Context for Next Agent:**
- Full test suite: 4998 tests passing
- All phases complete (Phases 1-5)
- Audit verified:
  - 15 star color mapping tests passing
  - 10 empire asset loading tests passing
  - 6 BUG-13 regression tests passing
  - 8 AssetManager.get_star_color_key tests passing
- Implementation verified:
  - `strategy_scene._load_assets()` uses RaceAssetLoader
  - `strategy_scene._get_object_asset()` uses AssetManager.get_star_color_key()
  - Star colors defined in asset_manifest.json
- Only remaining: User manual verification (Task 5.4)

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
- [x] Run full test suite: `pytest tests/` (NOT --testmon) - 4998 passed
- [ ] Start new game with 4+ empires, different races and themes
- [ ] Verify star colors render correctly (red, blue, yellow, white, orange stars visible)
- [ ] Verify colony flags appear on owned planets
- [ ] Verify fleet icons appear with correct skins
- [ ] Load a save from before the refactor - verify backward compatibility
- [x] All phase checklists complete
- [x] All tests passing
- [x] Audit passed (cycle 1)
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-01-28 | Phase 5 checklist not updated (Minor) | Updated checklist to reflect actual state. All tests passing. PASSED |
