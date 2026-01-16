# Starship Battles Unit Test Plan

This document provides an overview of the unit testing strategy and infrastructure for Starship Battles.

## Test Infrastructure Overview

### Directory Structure

```
tests/
├── fixtures/              # Shared test fixtures and factories
│   ├── __init__.py
│   ├── paths.py           # Path utilities (get_project_root, get_data_dir)
│   ├── ships.py           # Ship fixtures (empty_ship, basic_ship, armed_ship)
│   ├── components.py      # Component fixtures
│   ├── battle.py          # Battle engine fixtures
│   ├── ship_fixtures.py   # Additional ship utilities
│   └── test_scenarios.py  # TestScenario helpers
├── infrastructure/        # Test infrastructure
│   └── session_cache.py   # Session-level registry caching
├── unit/                  # Unit tests organized by module
│   ├── ai/               # AI controller and behavior tests
│   ├── builder/          # Ship builder tests
│   ├── combat/           # Combat and weapon tests
│   ├── entities/         # Ship and component tests
│   ├── systems/          # Physics and system tests
│   └── ui/               # UI component tests
└── conftest.py           # Root pytest configuration
```

### Core Test Fixtures

All tests use shared fixtures from `tests/fixtures/`:

**Path Fixtures** (`paths.py`):
- `project_root` - Project root directory
- `data_dir` - Game data directory (components.json, etc.)
- `test_data_dir` - Test-specific data directory
- `unit_test_data_dir` - Unit test data directory

**Ship Fixtures** (`ships.py`):
- `empty_ship` - Ship with only auto-equipped hull
- `basic_ship` - Ship with bridge and engine
- `armed_ship` - Ship with weapons
- `shielded_ship` - Ship with shields
- `fully_equipped_ship` - Ship with all common component types
- `create_test_ship()` - Factory function for custom ships

**Battle Fixtures** (`battle.py`):
- `battle_engine` - Configured BattleEngine instance
- `two_ship_battle` - Engine with two opposing ships

### Registry Hydration

Tests use **Fast Hydration** to populate the registry from cached session data:

1. `SessionRegistryCache` loads all production data once per test session
2. Each test gets a fresh registry populated from cache (no disk I/O)
3. Registry is cleared after each test for isolation

See `conftest.py` and `tests/infrastructure/session_cache.py` for implementation.

---

## Original Test Plan Areas

After a comprehensive review of the codebase (including `ai_behaviors.py`, `battle_setup.py`, `ship_theme.py`, and the `tests/` directory), three distinct areas were identified that historically lacked rigorous unit testing. These have since been addressed in the consolidation refactoring.

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

---

## Running Tests

### Full Test Suite

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with parallel execution (requires pytest-xdist)
pytest tests/unit/ -v -n auto

# Run specific test module
pytest tests/unit/ai/test_ai_behaviors.py -v

# Run tests matching pattern
pytest tests/unit/ -v -k "behavior"
```

### Test Markers

```bash
# Run only simulation tests
pytest -m simulation

# Skip slow tests
pytest -m "not slow"
```

### Test Coverage

```bash
# Run with coverage report
pytest tests/unit/ --cov=game --cov-report=html
```

---

## Configuration Classes Used in Tests

Tests can access centralized configuration values:

```python
from game.core.config import DisplayConfig, AIConfig, PhysicsConfig

# Use test resolution for pygame display
resolution = DisplayConfig.test_resolution()  # (1440, 900)

# Physics tick rate
dt = PhysicsConfig.TICK_RATE  # 0.01

# AI constants
spacing = AIConfig.MIN_SPACING  # 150
```

---

## Consolidation Summary

The following test infrastructure improvements were made during the 14-phase consolidation:

1. **Phase 5**: Created shared fixtures in `tests/fixtures/`
2. **Phase 5**: Migrated hardcoded paths to `get_data_dir()` fixtures
3. **Phase 5**: Consolidated duplicate conftest.py code
4. **Phase 10**: Merged fragmented test framework
5. **Phase 13**: Configuration migration (DisplayConfig, AIConfig, PhysicsConfig)

**Test Count**: 845+ unit tests passing

---

## Legacy Notes

**Summary of Original Work Assignments**:
1.  **Agent A**: Write `tests/test_ai_behaviors.py` - COMPLETED
2.  **Agent B**: Write `tests/test_fleet_composition.py` - COMPLETED
3.  **Agent C**: Write `tests/test_ship_theme_logic.py` - COMPLETED
