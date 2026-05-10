# PROJ-37: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### The Problem
In `strategy_scene.py` (lines 435-508), asset loading has several fragility issues:
- **Hardcoded paths**: `Images/Flags/Processed`, `Skins/Battlecruiser.png`, `Flags/Colony_Flag.jpg`
- **Hardcoded filenames**: `rectangle.png`, `shield.png`, `Colony_Flag.jpg`, `Battlecruiser.png`
- **Magic number thresholds** (lines 497-508): Color-based star selection using arbitrary RGB values (100, 150, 200)

### Existing Infrastructure (Already Available!)
The codebase already has well-designed asset management that's simply **not being used** in this file:

| Component | Location | Purpose |
|-----------|----------|---------|
| `AssetManager` | `game/assets/asset_manager.py` | Singleton, manifest-based loading, caching |
| `ShipThemeManager` | `game/ui/assets/ship_theme_manager.py` | Theme discovery, lazy loading |
| `RaceAssetLoader` | `game/ui/screens/race_asset_loader.py` | Flag loading with resolution hierarchy |
| `asset_manifest.json` | `assets/asset_manifest.json` | Exists but doesn't include empire assets |
| `ASSET_DIR` constant | `game/core/constants.py` | Centralized path definitions |

---

## Swarm Findings Summary

### Architecture
- **Module boundaries are clean**: `game/assets/` (core), `game/ui/assets/` (UI-specific), `game/ui/screens/` (race/empire loaders)
- **AssetManager is singleton** with thread-safe double-checked locking
- **RaceAssetLoader** uses instance methods with resolution hierarchy (1024 > 512 > 256 > root)
- **No circular dependencies** detected - safe to refactor

### Key Patterns to Reuse
- **Resolution Hierarchy** (`race_asset_loader.py:load_flag_full`): Try 1024 > 512 > 256 > root
- **Placeholder Creation** (`race_asset_loader.py:create_placeholder`): Gray crossed rectangle for missing assets
- **Manifest Lookup** (`asset_manager.py:get_image`): category.key hierarchical access
- **Naming Convention**: `load_*_full()`, `load_*_preview()`, `get_*()`, `create_placeholder()`
- **Caching Pattern**: Check cache first, then load, then store in cache
- **Type Hints**: Return `pygame.Surface`, `List[pygame.Surface]`, `Optional[pygame.Surface]`
- **Error Handling**: Use `log_error()`, `log_warning()` from `game.core.logger`

### Dependencies & Risks
1. **Color edge cases** (Medium) - Cyan/magenta stars fall to yellow default
   - Mitigation: Add explicit rules in manifest for edge cases
2. **Missing theme directory** (High) - Falls back to pink placeholder
   - Mitigation: Validate at game load time
3. **Memory growth** (Medium) - AssetManager cache grows unbounded
   - Mitigation: Future work - clear external assets on new game load
4. **Race vs Theme precedence** - Already correctly handled (race flags take priority)
   - Current logic is good, just needs to be moved to RaceAssetLoader

### Test Coverage Gaps (CRITICAL)
- **ZERO tests** for star color mapping logic (lines 497-508)
- **ZERO tests** for `_get_object_asset()` method
- **Only 1 test** exercises empire asset loading (`test_bug_13_colony_flags.py`)
- Need 15-20 new tests before/during refactor

### Opportunities Discovered
- RaceAssetLoader already has resolution hierarchy logic that can be reused
- AssetManager already has manifest lookup pattern
- Consolidating empire asset loading will reduce code duplication

---

## Data Flow Reference

```
Empire Creation:
  RaceConfig.flag_id → PlayerConfig → Empire(flag_id, empire_theme_id)

Asset Loading (strategy_scene.py:435-491):
  empire.flag_id → race_flags_base/flag_id/256/rectangle.png → empire_assets[id]['colony']
  empire.flag_id → race_flags_base/flag_id/256/shield.png → empire_assets[id]['fleet_flag']
  empire.empire_theme_id → theme_path/Flags/Colony_Flag.jpg → empire_assets[id]['colony']
  empire.empire_theme_id → theme_path/Skins/Battlecruiser.png → empire_assets[id]['fleet']

Asset Usage (strategy_renderer.py):
  self.empire_assets[emp.id]['colony'] → rendered on owned planets (lines 470-480)
  self.empire_assets[emp.id]['fleet'] → rendered on fleet icons (lines 500-509)
  self.empire_assets[emp.id]['fleet_flag'] → rendered on fleet (lines 515-524)
```

### empire_assets Dict Structure (Must Preserve)
```python
self.empire_assets = {
    empire_id: {
        'colony': pygame.Surface,      # Rectangle flag (planet ownership)
        'fleet': pygame.Surface,       # Ship silhouette (fleet icon)
        'fleet_flag': pygame.Surface   # Shield flag (race identity, optional)
    }
}
```

---

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

### Key Architectural Decisions
1. **Extend RaceAssetLoader** rather than create new EmpireAssetLoader
   - Rationale: Reuse existing flag loading logic with resolution hierarchy
   - Trade-off: RaceAssetLoader is currently stateless utility; new methods will maintain this pattern

2. **Star colors in asset_manifest.json** rather than separate config file
   - Rationale: Centralized config, follows existing manifest pattern
   - Structure: `"star_colors": { "red": {"r_min": 200, ...}, ... }`

3. **Add get_star_color_key() to AssetManager** rather than strategy_scene
   - Rationale: Keeps color logic with manifest data
   - AssetManager already loads/caches manifest
