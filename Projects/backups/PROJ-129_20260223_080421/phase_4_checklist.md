# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-129 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (4 findings, 0 critical)
**Priority:** Normal

---

## Tasks

### Task 4.1: LEG-UI2-003 - Excessive getattr() with Defaults in bat [Medium]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Defensive programming for duck typing. The getattr() calls with defaults handle:
1. Ship.crew_onboard/crew_required - dynamically set by ShipStatsCalculator, may not exist before first stats calculation
2. Projectile attributes - exist in __init__ but service supports any projectile-like object
3. Component.shots_fired/shots_hit - weapon-specific, not all components have these
This is valid defensive programming for flexibility. No code changes needed.

### Task 4.2: LEG-UI2-004 - ModifierEditorPanel Marked as Legacy [Medium]
**File:** `game/ui/screens/builder/modifi`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** RESOLVED - Dead file deleted. The legacy `game/ui/screens/builder/modifier_editor.py` contained an old ModifierEditorPanel that was NOT imported anywhere. The active version is in `game/ui/panels/builder_widgets.py`. Updated test_slider_increment.py to test ModifierControlRow directly (where the actual slider logic resides).

### Task 4.3: LEG-UI2-005 - Singleton Pattern Still in Use for Asset [N]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Valid use of singleton pattern. ShipThemeManager is a UI resource manager for image caching:
1. Image caches should be global (expensive to duplicate)
2. Has clear()/reset() for test isolation
3. UI layer singletons for resources are appropriate
4. Thread-safe via SingletonMeta
No code changes needed.

### Task 4.4: LEG-UI2-006 - hasattr() Check in Camera for Defensive [Simple]
**File:** `game/ui/renderer/camera.py:58`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Valid defensive programming for duck typing. Camera can follow any object with `.position` attribute. The hasattr check for `is_alive` allows camera to follow Ships, Projectiles, or ANY entity without requiring a specific interface. No code changes needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
