---
### 📝 User Update 2026-01-03 16:39
BUG-10

Ship Stats not updating for Ammo/Ordinance

## Description
Logistics:
Adding a Railgun should immediately trigger the Ship stats view to show the stats for Ammo/ordinance since the railgun uses ordinance.  Teh capital ship missle should also trigger it.  I see No panel showing ordinance use when they were added: C:\Dev\Starship Battles\screenshots\screenshot_20260103_162244_763808_mouse_focus.png shows that there is no logistics indicating ammo use, but the Racomendations show that ammo is recomended since the design has components that use ammo.  Similarly a Laser cannon does not trigger the addition of Energy to the Logistics.

## Status
[Pending]

## Work Log
*   **[2026-01-03 16:39] Bug Ingested:**
    *   Created ticket.
*   **[2026-01-03 17:54] Phase 1: Reproduction:**
    *   Created `tests/repro_issues/test_bug_10_logistics_update.py`.
    *   Test passed (row appeared), but calculation logic was found to be flawed.
    *   **Root Cause Analysis:** `ShipStatsCalculator` attempts to read `reload_time` from the Component object (`getattr(c, 'reload_time', 1.0)`), but `reload_time` resides in the `WeaponAbility` instance. This causes the consumption rate calculation to default to 1.0/reload instead of the actual weapon reload rate, leading to incorrect "Max Usage" values. If `reload_time` effectively defaults to values that result in 0 consumption (edge case), the row disappears. Fixing the lookup will ensure accurate `max_usage` and force the row to appear.
*   **[2026-01-03 17:58] Phase 2: The Fix:**
    *   Modified `ship_stats.py`: Updated `_calculate_combat_endurance` to iterate through `component.ability_instances` and find the first `WeaponAbility` (or subclass) to retrieve the correct `reload_time`.
    *   Verified fix with `tests/repro_issues/test_bug_10_logistics_update.py`. The test now passes and correctly asserts that a Railgun (Reload 5.0, Cost 1.0) consumes 0.2 Ammo/s.
    *   Ran regression tests `tests/unit/test_combat_endurance.py` - All Passed.
*   **[2026-01-03 18:00] Phase 3: Documentation:**
    *   Files modified: `ship_stats.py`.
    *   Status updated to `[Awaiting Confirmation]`.

