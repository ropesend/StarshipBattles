---
### 📝 User Update 2026-01-03 16:39
BUG-09

Fuel Endurance Infinite Calculation Error

## Description
Logistics:
Fuel Endurance is not being correctly calculated, I have 1 engine, and one fuel tank in my design, and Endurance is considered to be infinite:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_162014_213895_mouse_focus.png (Shows that the Fuel Capcity is finite, and being used, and yet Endurance says Infinite).

## Status
[Pending]

## Work Log
*   **[2026-01-03 16:39] Bug Ingested:**
    *   Created ticket.
*   **[2026-01-03 17:39] Reproduction Phase:**
    *   Created `tests/repro_issues/test_bug_09_endurance.py`.
    *   **Root Cause Identified:** The `fmt_time` function in `ui/builder/stats_config.py` arbitrarily treats any duration > 99,999 seconds (~27 hours) as "Infinite".
    *   A ship with `standard_engine` (0.5 consumption) and `fuel_tank` (50,000 capacity) lasts 100,000 seconds, triggering this bug.
    *   Confirmed via test failure where formatted string was "Infinite" instead of finite time.
*   **[2026-01-03 17:41] Phase 2: Fix**
    *   Removed the arbitrary limit (`val > 99999`) in `ui/builder/stats_config.py`.
    *   Now only `float('inf')` triggers the "Infinite" label.
*   **[2026-01-03 17:43] Phase 3: Verification**
    *   Ran `tests/repro_issues/test_bug_09_endurance.py`.
    *   Test passed. Output: "27.8h". 
    *   Confirmed fix.
