Step Id: 32
# Comparative Code Review and Unit Test Plan

After a comprehensive review of the codebase (including `ai_behaviors.py`, `battle_setup.py`, `ship_theme.py`, and the `tests/` directory), I have identified three distinct areas that consistently lack rigorous unit testing. While the "happy path" is often covered by integration tests (e.g., `test_ai.py` or smoke test scripts like `test_formation_flight.py`), the specific business logic, state transitions, and edge cases in these areas are under-tested.

## Area 1: AI Behavior Logic (`ai_behaviors.py`)

**Current State**: `test_ai.py` mostly verifies the high-level `AIController` and basic strategy dispatching. Specific behaviors like `KiteBehavior` and `FormationBehavior` contain complex logic (drift calculation, velocity synchronization, deadband smoothing) that is not isolated or tested.
**Risk**: Regressions in formation flying (ships drifting apart or oscillating) or kiting logic (ships getting stuck or not maintaining range) are high-risk.

### Implementation Plan
Create `tests/test_ai_behaviors.py`:
1.  **Test `KiteBehavior`**:
    *   Mock `AIController` and `Strategy` dictionary.
    *   Verify `opt_dist` calculation (including `engage_mult` scaling).
    *   Verify logic branching: test coordinates where `dist > opt_dist` (should close in) vs `dist <= opt_dist` (should kite).
    *   Verify collision avoidance integration (mock `check_avoidance` returning a value vs None).
2.  **Test `FormationBehavior`**:
    *   Mock `master` ship and `follower` ship with precise positions/angles.
    *   **Drift vs. Turn Logic**: Verify that small distance errors trigger "Drift" logic (position correction) while large errors trigger "Navigate" logic.
    *   **Velocity Sync**: Verify `engine_throttle` is set to match master's speed.
    *   **Rotation**: Verify `formation_offset` calculations for both `fixed` and `relative` rotation modes.
3.  **Test `RamBehavior`**:
    *   Verify it sets `stop_dist=0` and `precise=False`.

## Area 2: Fleet Composition & Battle Setup (`battle_setup.py`)

**Current State**: `battle_setup.py` contains critical logic for converting UI selections into simulation objects (`load_ships_from_entries`, `add_formation_to_team`). This logic handles formation linking (master/follower), relative positioning, and parsing valid designs. It currently has NO unit tests (`test_battle_setup_logic.py` tests the engine, not this setup logic).
**Risk**: Formation hierarchies being built incorrectly (loops, missing masters), invalid setups crashing the game start, or relative positions being calculated wrongly.

### Implementation Plan
Create `tests/test_fleet_composition.py`:
1.  **Test `load_ships_from_entries`**:
    *   Pass a mock list of team entries (dictionaries imitating UI state).
    *   Verify it returns correct `Ship` objects.
    *   **Formation Linking**: Create entries with `formation_id`. Verify the first ship is `master`, subsequent ships are `followers` (`formation_master` ref is set).
    *   **Positioning**: Verify `relative_position` is correctly applied to the `start_x`/`start_y`.
2.  **Test `scan_ship_designs`**:
    *   Use `unittest.mock.patch` to mock `glob.glob` and `open`.
    *   Verify it parses valid JSONs and skips invalid ones vs crashing.
3.  **Test `add_formation_to_team` Logic**:
    *   This method contains math for centering options. Extract this logic or test the side effects on the `team` list.
    *   Verify `formation_id` generation (UUID mocking) and arrow assignment.

## Area 3: Ship Theme & Visual System (`ship_theme.py`)

**Current State**: `ship_theme.py` manages loading, scaling, and fallback generation for ship visuals. `tests/verify_themes.py` is merely a file-existence checker, not a logic test. The class uses a Singleton pattern that makes stateful testing harder.
**Risk**: Visual regressions where ships disappear (fallback fails) or are scaled incorrectly (bad bounding box math) are possible if this logic breaks.

### Implementation Plan
Create `tests/test_ship_theme_logic.py`:
1.  **Test `ShipThemeManager` Logic** (Mocking `pygame` and `os`):
    *   **Singleton Handling**: Ensure tests clean up singleton instances (`_instance = None`).
    *   **Fallback Generation**: Verify `_create_fallback_image` returns a Surface of expected size when theme is missing.
    *   **Manual Scaling**: Mock a `theme.json` with `{"scale": 1.5}`. Verify `get_manual_scale` returns detection.
2.  **Test `get_image_metrics`**:
    *   Create a simple `pygame.Surface` with known transparent/opaque pixels.
    *   Verify `get_bounding_rect` logic is correctly cached and returned.
3.  **Test Error Handling**:
    *   Simulate malformed `theme.json`. Verify `_load_theme` logs error but doesn't crash functionality.

***

**Summary of Work for Parallel Agents**:
1.  **Agent A**: Write `tests/test_ai_behaviors.py`.
2.  **Agent B**: Write `tests/test_fleet_composition.py`.
3.  **Agent C**: Write `tests/test_ship_theme_logic.py`.
