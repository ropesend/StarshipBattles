## Description
The generator does not appear to be generating energy. Here are 2 images:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_182552_724483_mouse_focus.png (shows that ther is a battery, a generator, and a laser cannon)
C:\Dev\Starship Battles\screenshots\screenshot_20260103_182628_318021_mouse_focus.png (shows 0 energy generation, it should be 25/s)

## Status
[Awaiting Confirmation]

## Solution Summary
**WORKING AS DESIGNED** - Not a code bug.

The Generator component has `CrewRequired: 1` in its abilities definition. When a ship lacks Crew Quarters or Life Support, the Generator is deactivated due to unmet crew requirements, causing its ResourceGeneration ability to be skipped during stat calculation.

**User's ship is missing:** Crew Quarters and/or Life Support components.

**Fix:** Add Crew Quarters (provides crew capacity) and Life Support (enables crew) to the ship before the Generator can operate.

## Work Log
### 2026-01-03 18:58 - Phase 1: Reproduction
- **Test File:** `tests/repro_issues/test_bug_12_energy_gen.py`
- **Result:** CONFIRMED FAILURE
- **Assertion:** `Energy gen rate should be 25.0, got 0.0`
- **Analysis:** Generator component's `ResourceGeneration` ability is being created with rate=25, but `ship_stats.py` is not correctly accumulating it into `ship.resources.regen_rate`.

### 2026-01-03 19:02 - Phase 2: Root Cause Analysis
- **Finding:** Generator `is_active=False` after calculation
- **Root Cause:** Generator has `CrewRequired: 1` but ship has no Crew Quarters or Life Support
- **Verification:** When crew components added, Generator correctly shows 25/s energy generation
- **Conclusion:** Working as designed. User needs to add crew infrastructure to their ship.

### Files Modified
- `tests/repro_issues/test_bug_12_energy_gen.py` - Updated to document expected behavior
