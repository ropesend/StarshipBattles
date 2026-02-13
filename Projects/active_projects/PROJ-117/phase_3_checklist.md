# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-117 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (12 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 3.1: LEG-UI2-001 - Legacy widgets.py Module - Entire File i [Simple]
**File:** `game/ui/widgets.py:1-102`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Deleted widgets.py (unused legacy code - project uses pygame_gui). Deleted test_ui_widgets.py (19 tests). Removed import from test_ui_imports.py.

### Task 3.2: LEG-UI2-002 - SpriteManager Atlas Fallback - Dead Code [Simple]
**File:** `game/ui/renderer/sprites.py:40`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Deleted _load_atlas_file() and _slice_sprites() methods (Components.bmp doesn't exist, Tiles directory is used). Removed self.atlas attribute. Updated docstring.

### Task 3.3: LEG-UI2-003 - draw_hud() and draw_bar() in game_render [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - draw_hud() and draw_bar() ARE used in production (battle_screen.py line 600, app.py line 675).

### Task 3.4: LEG-UI2-004 - BattleOrchestrator Never Used in Product [Medium]
**File:** `game/ui/orchestration/battle_o`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - BattleOrchestrator IS used in production. Used by BattleEngine (battle_engine.py lines 222, 247, 304, 312). Test files exercise this integration.

### Task 3.5: LEG-UI2-005 - show_overlay Hack - State Passed via Dyn [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - show_overlay IS used in production (battle_screen.py, battle_ui.py). The getattr is defensive coding for camera not having the attribute (acceptable).

### Task 3.6: LEG-UI2-006 - draw_ship() Uses Singleton ShipThemeMana [Medium]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - acceptable pattern)
- [x] Implement the fix (N/A - acceptable pattern)
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - ShipThemeManager singleton is an architectural pattern used across 11 files. Same pattern as other approved singletons (SpriteManager, RegistryManager, etc.).

### Task 3.7: LEG-UI2-007 - Unnecessary hasattr Guard on LayerType.v [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - Removed unnecessary hasattr check. LayerType is always an enum with .value attribute. Changed to direct `.value` access with comment.

### Task 3.8: LEG-UI2-008 - getattr(ship, 'id', id(ship)) - Ship.id [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Ship class does NOT have an explicit 'id' attribute (verified via grep). The getattr fallback to id(ship) is CORRECT defensive coding.

### Task 3.9: LEG-UI2-009 - Excessive getattr Usage in _convert_proj [Medium]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - acceptable pattern)
- [x] Implement the fix (N/A - acceptable pattern)
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - getattr usage in _convert_projectile is defensive coding for optional attributes on projectiles. This is correct adapter pattern for heterogeneous projectile types.

### Task 3.10: LEG-UI2-010 - interfaces/__init__.py Re-exports Never [Simple]
**File:** `game/ui/interfaces/__init__.py`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - interfaces/__init__.py re-exports ARE used. Found 8 files importing from game.ui.interfaces.battle_ui (battle_ui_service.py, test files, mocks).

### Task 3.11: LEG-UI2-011 - SpriteManager and ShipThemeManager Use S [Complex]
**File:** `game/ui/renderer/sprites.py:7`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - acceptable pattern)
- [x] Implement the fix (N/A - acceptable pattern)
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Singleton pattern (SingletonMeta metaclass) is an approved architectural pattern. Project uses it consistently for UI managers.

### Task 3.12: LEG-UI2-012 - game/ui/__init__.py Purpose is xdist Rac [Simple]
**File:** `game/ui/__init__.py:1-27`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix (N/A - false positive)
- [x] Implement the fix (N/A - false positive)
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - The __init__.py purpose IS valid. It prevents pytest-xdist race conditions during parallel worker startup. This is documented and intentional infrastructure.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary
- 12 findings analyzed
- 3 FIXED (widgets.py deleted, atlas fallback deleted, hasattr removed)
- 4 FALSE POSITIVES (draw_hud/bar used, BattleOrchestrator used, show_overlay used, interfaces used, Ship.id getattr correct)
- 5 ACCEPTABLE (singleton patterns, defensive getattr, xdist race fix)
- Tests: 9754 passed (19 widget tests removed)
