# BUG-02

## Description
Weapons Report: Seeker Stats missing. Range = 80% * Speed * Endurance.

---
### 📝 User Update [2026-01-03 15:17]
Weapons Report Panel: The panel is significantly improved, it shows most of the info but: The panel doesn't show the range and damage of seeker weapons, the range is supposed to be 80% of the speed time s the straight line endurance.  Here is an image:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_134933_808287_mouse_focus.png
---

## Status
Pending

## Work Log
* [2026-01-03 15:35] Phase 1 Reproduction: Created `tests/repro_issues/test_bug_02_seeker.py`. Confirmed failure: Range reverts to 0.0 after `recalculate()` because `_base_range` is not updated when `SeekerWeaponAbility` derives the default range.
* [2026-01-03 15:40] Phase 2 Fix: Updated `SeekerWeaponAbility.__init__` in `game/simulation/components/abilities.py` to correctly synchronized `_base_range` with the calculated range. Verified with `test_bug_02_seeker.py` and regression tests `tests/unit/test_seeker_range.py`, `tests/unit/test_weapons.py`. All passed.
