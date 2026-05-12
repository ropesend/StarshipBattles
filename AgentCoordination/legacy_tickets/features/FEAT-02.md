## Description
In the Species Setup dialogue, add a "Generate Random" button (positioned bottom-left, beside Cancel) to the Identity, Visual, and Ships tabs. The Identity button should randomize species name, plural, physical/government/society types, organization, leader title/name, and faction name. The Visual button should randomize flag and portrait. The Ships button should randomly select an available ship set.

**Requirement:** Pre-generate a list of plausible race names, their plural forms, and leader names for each available race portrait. Save these values in an existing or new `.json` file that the randomization logic can pull from.

**Screenshot:** `c:\Developer\StarshipBattles\tools\qa_observer\session_data\20260228_070811\images\bug_capture_070840.png`

## Priority
High

## Status
Awaiting Confirmation

## Work Log
- 2026-02-28: Feature created from QA session log.
- 2026-02-28: Implemented Generate Random functionality across 3 tabs.

  **Phase 0 — Deep Review:** Requirements clear. All 14 race portraits reviewed visually to assign thematically appropriate names.

  **Phase 1 — Analysis:** Clean implementation feasible. Architecture supports:
  - New `RaceRandomizer` service class with static methods (no refactoring needed)
  - One "Generate Random" button in navigation area, shown/hidden per tab
  - JSON data file for portrait-specific names in existing `game/data/` location

  **Phase 2 — Tests (Red):** Created `tests/unit/strategy/test_race_randomizer.py` with 23 tests covering:
  - Identity randomization (name, plural, leader, dropdowns, faction)
  - Portrait-aware name generation (known portrait, unknown portrait, no portrait)
  - Visual randomization (flag, portrait, empty lists)
  - Ship theme randomization (theme, empty list)
  - Data file integrity (loading, structure, required fields)

  **Phase 3 — Implementation (Green):**

  **New files created:**
  - `game/data/race_names.json` — Pre-generated race names, plurals, and leader names for all 14 portraits, plus fallback pools. Each portrait entry maps to thematically appropriate names based on the portrait's visual character (e.g., insectoid portrait gets names like "Khithari", "Mantid"; reptilian gets "Draconari", "Skarath").
  - `game/strategy/systems/race_randomizer.py` — `RaceRandomizer` class with static methods:
    - `randomize_identity(portrait_id)` — Returns dict of all identity fields; portrait-aware for name/leader
    - `randomize_flag(available_flags)` — Random flag from available list
    - `randomize_portrait(available_portraits)` — Random portrait from available list
    - `randomize_theme(available_themes)` — Random theme from available list
  - `tests/unit/strategy/test_race_randomizer.py` — 23 unit tests

  **Files modified:**
  - `game/ui/screens/race_setup_screen.py` — Added:
    - Import for `RaceRandomizer`
    - `btn_randomize` button (160px wide, beside Cancel) in `_create_navigation_buttons()`
    - Show/hide logic in `_update_navigation_buttons()` for Identity/Visuals/Ships tabs
    - Button click handling in `process_event()`
    - `_on_randomize()` dispatcher method
    - `_randomize_identity()` — Sets race_config fields, calls panel `set_from_config()`
    - `_randomize_visuals()` — Discovers available flags/portraits, picks random, updates galleries
    - `_randomize_ships()` — Discovers available themes, picks random, refreshes ship preview

  **Design decisions:**
  - Single button that dispatches by current tab (cleaner than 3 separate buttons)
  - Portrait-aware name generation: if a portrait is selected before randomizing identity, names come from that portrait's pool. Otherwise uses fallback pool.
  - Faction name auto-generated as `"{race_name} {government_type}"`
  - Uses cached gallery asset discovery (no redundant file scanning)

  **Regression:** 12,935 passed, 0 failures (23 new tests added).
