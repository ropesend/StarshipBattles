# BUG-13: Colony Flags Replaced by Colored Circles

## Description
In the strategy Layer,  the colonies no longer use the flags, there a colored circles instead. Flag images are stored in the theme folders, for example: C:\Dev\Starship Battles\assets\ShipThemes\Atlantians\Flags\Colony_Flag.jpg

## Status
Pending

## Work Log

### 2026-01-18 - Phase 1: Reproduction (Red)

**Root Cause Identified:**

When loading a saved game, `Empire.from_dict()` uses the saved `theme_path` verbatim. This absolute path may not exist on the current machine if:
1. The project location changed (e.g., renamed folder)
2. Loading a save from a different machine

**Code Flow:**
1. [strategy_scene.py:79](game/ui/screens/strategy_scene.py#L79) - `_load_assets()` is called on scene init
2. [strategy_scene.py:427](game/ui/screens/strategy_scene.py#L427) - Checks `if emp.theme_path and os.path.exists(emp.theme_path)`
3. If path doesn't exist, the 'colony' key is never added to `empire_assets`
4. [strategy_renderer.py:446](game/ui/screens/strategy_renderer.py#L446) - Checks `if emp_assets and 'colony' in emp_assets`
5. Falls back to [strategy_renderer.py:457](game/ui/screens/strategy_renderer.py#L457) - `pygame.draw.circle()` instead of flag

**Reproduction Test Created:** `tests/repro_issues/test_bug_13_colony_flags.py`

**Failing Test Output:**
```
FAILED tests/repro_issues/test_bug_13_colony_flags.py::TestLoadedGameColonyFlags::test_empire_from_dict_uses_saved_path_verbatim
FAILED tests/repro_issues/test_bug_13_colony_flags.py::TestLoadedGameColonyFlags::test_load_assets_with_invalid_theme_path_results_in_no_colony_flag

AssertionError: BUG CONFIRMED: Empire loaded from save has invalid theme_path.
  Saved path: C:\SomeOther\Path\ShipThemes\Atlantians
  Path exists: False
  Correct path would be: C:\Dev\Starship Battles\assets\ShipThemes\Atlantians

  This causes colony flags to not load, falling back to circles.

AssertionError: BUG CONFIRMED: No colony flag loaded due to invalid theme_path.
  empire.theme_path: C:\NonExistent\Path\ShipThemes\Atlantians
  path exists: False
  empire_assets keys: []

  When 'colony' key is missing, renderer falls back to drawing circles.
```

**Proposed Fix:**
In `_load_assets()` ([strategy_scene.py:418](game/ui/screens/strategy_scene.py#L418)), instead of trusting `emp.theme_path`, recalculate the path using the current `GameConfig` and the empire's `empire_theme_id` field. This ensures paths are always relative to the current project location.

---

### 2026-01-18 - Phase 2: The Fix (Green)

**Implementation:**

Modified `_load_assets()` in [strategy_scene.py:418-446](game/ui/screens/strategy_scene.py#L418-L446):

**Before (buggy):**
```python
def _load_assets(self):
    for emp in self.empires:
        self.empire_assets[emp.id] = {}
        if emp.theme_path and os.path.exists(emp.theme_path):  # Uses saved path
            colony_path = os.path.join(emp.theme_path, "Flags", "Colony_Flag.jpg")
            ...
```

**After (fixed):**
```python
def _load_assets(self):
    from game.strategy.engine.game_config import GameConfig
    config = GameConfig()
    asset_base = config.asset_base_path  # Current project's asset path

    for emp in self.empires:
        self.empire_assets[emp.id] = {}
        # Recalculate theme_path using empire_theme_id and current asset location
        theme_path = os.path.join(asset_base, emp.empire_theme_id)

        if os.path.exists(theme_path):
            colony_path = os.path.join(theme_path, "Flags", "Colony_Flag.jpg")
            ...
```

**Files Modified:**
- [game/ui/screens/strategy_scene.py](game/ui/screens/strategy_scene.py) - Lines 418-446

**Tests Updated:**
- [tests/repro_issues/test_bug_13_colony_flags.py](tests/repro_issues/test_bug_13_colony_flags.py) - Updated to verify fix works

**Test Results:**
```
6 passed in 1.57s
```

**Regression Test Results:**
```
1399 passed, 1 unrelated failure (timing test)
```
