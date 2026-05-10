## Description
In the Build Queue, designs from other games are being shown.

## Status (Awaiting Confirmation)
Fix applied. Awaiting user verification.

## Work Log
- 2026-01-20: Ticket created by Project Manager.
- 2026-01-20: Deep Investigation initiated. 4 Explore agents deployed in parallel.

---

## Investigation Report

### Code Path Trace

```
[StrategyScene.on_build_yard_click()]
    ↓ (game/ui/screens/strategy_scene.py:319-340)
    │ Calls: BuildQueueScreen(self.ui.manager, planet, self.session, ...)
    │ Key params: planet (with planet.owner_id), self.session (GameSession)
    │
[BuildQueueScreen.__init__()]
    ↓ (game/ui/screens/build_queue_screen.py:21-74)
    │ Line 46: savegame_path = getattr(session, 'save_path', None)
    │ Line 50: empire_id = planet.owner_id  ← KEY FILTERING POINT
    │ Line 55: self.design_library = DesignLibrary(savegame_path, empire_id)
    │
[DesignLibrary.__init__()]
    ↓ (game/strategy/systems/design_library.py:20-60)
    │ Line 40: self.designs_folder = os.path.join(savegame_path, "designs", f"empire_{empire_id}")
    │ Result: e.g., "C:\Dev\Starship Battles\saves\Master 7\designs\empire_0"
    │
[BuildQueueScreen._refresh_items_list()]
    ↓ (game/ui/screens/build_queue_screen.py:334-386)
    │ Line 343: designs = self._load_designs_by_category(self.selected_category)
    │
[BuildQueueScreen._load_designs_by_category()]
    ↓ (game/ui/screens/build_queue_screen.py:300-332)
    │ Line 312: all_designs = self.design_library.scan_designs()
    │
[DesignLibrary.scan_designs()]
    ↓ (game/strategy/systems/design_library.py:62-99)
    │ Line 78: pattern = os.path.join(self.designs_folder, "*.json")
    │ Line 81: matching_files = list(glob.glob(pattern))
    │ Returns: List[DesignMetadata] from empire's designs folder
```

### Dependency Map

**Callers:**
- `StrategyScene._open_build_queue()` → creates BuildQueueScreen
- User clicks "Build Queue" button on planet

**Callees:**
- `DesignLibrary.__init__(savegame_path, empire_id)` - creates design library scoped to empire
- `DesignLibrary.scan_designs()` - scans all JSON files in designs_folder
- `DesignMetadata.from_design_file()` - reads individual design JSON files
- `glob.glob()` - finds all matching files in designs_folder

**Data Sources:**
- `session.save_path` - path to current savegame folder (e.g., `saves/Master 7`)
- `planet.owner_id` - empire ID used to scope designs folder
- Design JSON files in `{savegame_path}/designs/empire_{empire_id}/`

### Similar Patterns Found

**Pattern 1: Turn Engine - Correct Design Library Initialization**
- File: `game/strategy/engine/turn_engine.py:159`
- Uses `DesignLibrary(save_path, empire.id)` - passes empire ID explicitly

**Pattern 2: Workshop Screen - Design Save/Load**
- File: `game/ui/screens/workshop_screen.py:698-700`
- Uses `self.context.empire_id` from workshop context

**Pattern 3: Planet List Window - Empire Filtering**
- File: `game/ui/screens/planet_list_filters.py:66-88`
- Compares `planet.owner_id` to current `empire_id` for filtering

**Key Finding:** All other patterns correctly establish empire context from session. Build Queue uses `planet.owner_id` which SHOULD be correct if the planet belongs to the right game session.

### Git History Analysis

**Affected Files:**
- `game/ui/screens/build_queue_screen.py`
- `game/strategy/systems/design_library.py`

**Recent Commits:**
- 212c466 (2026-01-19): Implement new game setup UI, core game session
- 531f353 (2026-01-18): Add UI for design management, build queue, and design library system
- 2235d2f (2026-01-17): Introduce save/load game functionality

**Suspect Commits:**
- Commit 212c466 changed design storage from flat `designs/` folder to per-empire `designs/empire_N/` subfolders
- Possible migration issue if old flat folder designs still exist

**Critical Observation:**
The code flow appears correct - it scopes to `{savegame_path}/designs/empire_{empire_id}/`. If designs from "other games" are appearing, the issue must be one of:
1. `session.save_path` is wrong/shared across games
2. Old designs exist in a shared location
3. The user is misidentifying which game they're in

---

## User Context

**Reproduction Steps:**
1. Start a brand new game
2. Go to the only colony's Build Queue
3. Observe designs appearing (4 complexes, 2+ ships)

**Expected Behavior:** New game should have NO designs - empty Build Queue

**Actual Behavior:** Designs from other save games appear in the Build Queue

**History:** User created these designs in previous game sessions (experimenting with the game)

**Consistency:** Happens every time a new game is started

**Game State:** Brand new game, first colony, Build Queue screen

**Known Workarounds:** None discovered

**Key User Insight:** "Either the new session puts some designs in the folder automatically, or the load button is looking in the wrong folder."

---

## ROOT CAUSE IDENTIFIED ✓ (CORRECTED)

### Initial Theory (Wrong)
First investigation suggested DesignLibrary was using a shared temp folder when `save_path` was `None`. However, user logs revealed the actual issue.

### Actual Root Cause: Temp Design Migration

**User logs showed:**
```
2026-01-21 05:11:37,531 - INFO - Migrating 6 designs for empire 0
2026-01-21 05:11:37,532 - DEBUG -   Migrated design: Cplex1.json
...
```

The `save_path` WAS correctly set. The problem was in `SaveGameService.save_game()`:

**File:** [save_game_service.py:74-75](game/strategy/systems/save_game_service.py#L74-L75)
```python
# Migrate designs from temp folder if this is the first save
SaveGameService._migrate_temp_designs(game_session, designs_folder)
```

This function **copies all designs from the temp folder into every new save**. The temp folder (`/tmp/starship_battles_temp_designs/empire_0/`) contained designs from previous game sessions, which were then copied into the new game's save folder.

### The Bug Mechanism (Corrected)

1. **Previous sessions:** User creates designs in standalone Workshop or early game sessions
2. **Designs saved to temp folder:** `%TEMP%/starship_battles_temp_designs/empire_0/`
3. **New game created:** `SaveGameService.save_game()` is called
4. **`_migrate_temp_designs()` runs:** Copies ALL temp folder designs to new save
5. **Build Queue loads:** Shows designs that were migrated from temp folder

---

## Hypothesis Log

### Hypothesis 1: Shared Temp Folder (DesignLibrary) - REJECTED
**Theory:** DesignLibrary was reading from shared temp folder when `save_path` was `None`.
**Evidence Against:** User logs showed `save_path` was correctly set to `C:\Dev\Starship Battles\saves\TestingSaves1`
**Result:** REJECTED - `save_path` is set before Build Queue opens

### Hypothesis 2: Temp Design Migration on Save - CONFIRMED ✓
**Theory:** `SaveGameService._migrate_temp_designs()` copies designs from temp folder to new saves.
**Evidence For:**
- Log shows "Migrating 6 designs for empire 0" when creating new game
- Designs are read from correct save folder, but they were migrated there
- `save_game_service.py:74-75` explicitly calls migration function
**Result:** **CONFIRMED** - This is the actual root cause

---

## Fix Applied (Corrected)

### TDD Approach

**1. Failing Test Written:**
- `test_new_game_does_not_migrate_temp_designs` - Verifies new saves have empty design folders

**2. Fix Applied:**
File: [save_game_service.py:74-75](game/strategy/systems/save_game_service.py#L74-L75)

**Before (Buggy):**
```python
# Migrate designs from temp folder if this is the first save
SaveGameService._migrate_temp_designs(game_session, designs_folder)
```

**After (Fixed):**
```python
# BUG-29 FIX: Do NOT migrate designs from temp folder
# New games should start with empty design libraries
# The temp folder migration was causing designs from other games to appear
# SaveGameService._migrate_temp_designs(game_session, designs_folder)
```

**3. Tests Passing:**
- All 1 new BUG-29 test: ✓ PASSED
- All 12 SaveGameService tests: ✓ PASSED
- All 20 DesignLibrary tests: ✓ PASSED
- All 15 BuildQueueScreen tests: ✓ PASSED

### Diagnostic Logging

| File | Line | What is Logged |
|------|------|----------------|
| save_game_service.py | 104 | Save completed message |
| design_library.py | 33-35 | `DesignLibrary.__init__` params |
| design_library.py | 41 | Savegame designs folder path |
| build_queue_screen.py | 52-53 | DesignLibrary initialization params |
| build_queue_screen.py | 313 | Total designs scanned |

---

## Work Log (continued)
- 2026-01-20: Root cause confirmed - shared temp folder contamination
- 2026-01-20: TDD tests written (3 tests, all failing as expected)
- 2026-01-20: Fix applied to `design_library.py` - set `designs_folder = None` when no save_path
- 2026-01-20: All tests passing (23 DesignLibrary + 15 BuildQueue = 38 tests)
- 2026-01-20: Status set to [Awaiting Confirmation]
- 2026-01-21: User provided logs showing actual root cause - temp design migration
- 2026-01-21: Reverted DesignLibrary fix, applied correct fix to SaveGameService
- 2026-01-21: Commented out `_migrate_temp_designs()` call in `save_game()`
- 2026-01-21: All 48 tests passing (SaveGameService + DesignLibrary + BuildQueue)
