# BUG-73: Species Setup - Homeworld type selection still reports "Custom"

## Description
In the species setup: When I select a homeworld type it still reports it as Custom.

## Priority
Medium

## Status (Awaiting Confirmation)

## Work Log
### 2026-02-08 - Fix Applied
**Root Cause:** Type mismatch between dropdown display names and preset IDs. The homeworld dropdown returns display names (e.g., "Continental") but `apply_homeworld_preset()` calls `get_preset_for_planet_type()` which expects preset IDs (e.g., "CONTINENTAL"). The lookup fails, returning None, so `race_config.homeworld_type` is never set — causing the summary to show "Custom".

**Fix:**
1. In `handle_dropdown_change()`: Convert display name to preset ID using `get_preset_id_from_name()` before calling `apply_homeworld_preset()`
2. In `_format_homeworld_summary()`: Convert preset ID back to display name (title case) for clean UI display

**Files Modified:**
- `game/ui/panels/race_environment_panel.py` - Added import and name-to-ID conversion in dropdown handler
- `game/ui/panels/race_summary_panel.py` - Format preset ID as display name in summary
