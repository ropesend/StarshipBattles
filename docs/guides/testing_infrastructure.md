# Testing Infrastructure Guide

Reference for agents working with the Starship Battles test suite. Covers DI fixtures, conftest hierarchy, test helpers, and common patterns.

---

## Conftest Hierarchy

Three conftest files form a layered fixture system. Fixtures from parent directories are available to all children automatically.

### `conftest.py` (root)

The most critical file. Provides two autouse fixtures that run for **every test**:

1. **`reset_game_state`** (function-scoped, autouse) -- The primary test isolation fixture. For each test it:
   - Creates fresh `RegistryManager` instance via `set_default_registry_manager()` and clears module-level component caches (pre-test)
   - Checks for `@pytest.mark.use_custom_data` -- if present, skips production hydration
   - Loads data via `SessionRegistryCache` (once per session, cached thereafter)
   - Calls `mgr.hydrate()` to populate the registry from cached data
   - Patches `ComponentCacheManager` and `load_vehicle_classes` to prevent disk I/O
   - Hydrates `StrategyManager` from cache
   - Post-test: resets all service instances (RegistryManager, event handler, component caches, StrategyManager, ShipThemeManager, ScreenshotManager, SpriteManager) via `set_default_xxx()` calls

2. **`enforce_headless`** (session-scoped, autouse) -- Sets `SDL_VIDEODRIVER=dummy`, initializes Pygame, creates a dummy display at `DisplayConfig.test_resolution()`.

3. **`configure_test_logging`** (session-scoped, autouse) -- Attaches `NullHandler` to suppress file I/O from the `game` logger.

### `tests/conftest.py`

Provides DI registry fixtures and shared test helpers:

- **Registry fixtures**: `session_registries`, `fresh_registries`, `minimal_registries`, `mock_registries`
- **Data loading fixtures**: `global_ship_data`, `global_ship_data_with_modifiers`
- **Factory fixtures**: `ship_factory` — creates `ShipInstance` with DI. For designs without real component layers, pre-caches `expected_stats` as `_cached_stats` and initializes `consumable_levels` from `resource_storage` to avoid running `calculate_design_stats()` on empty designs.
- **Helper functions**: `make_mock_ship_instance()`, `make_colony_ship_for_planet()`, `assert_success()`, `assert_list_length()`

### `tests/unit/conftest.py`

Minimal. Runs `pytest_configure` to pre-import `game.ui` and verify submodules (`renderer`, `screens`, `panels`) are loaded. Prevents race conditions during parallel test collection.

### `tests/integration/conftest.py`

Does not exist. Integration tests rely on root and `tests/` conftest fixtures.

---

## DI Registry Fixtures

The project uses dependency injection via `GameRegistries` objects. Four fixtures provide registries at different scopes:

| Fixture | Scope | Data | Use Case |
|---|---|---|---|
| `session_registries` | session | Production (cached) | Read-only reference; do not mutate |
| `fresh_registries` | function | Deep copy of production | Most tests; safe to mutate |
| `minimal_registries` | function | Empty dicts | Isolated unit tests; add only what you need |
| `mock_registries` | function | Empty dicts (alias) | Same as minimal; emphasizes mocking intent |

### Usage Pattern

```python
def test_ship_creation(fresh_registries):
    ship = Ship("Test", 0, 0, (255, 255, 255), ship_class="Escort",
                registries=fresh_registries)
    comp = create_component("laser_cannon", registries=fresh_registries)
    ship.add_component(comp, LayerType.OUTER)
    ship.recalculate_stats()
```

For tests that need custom or empty registries, use `minimal_registries` and mark with `@pytest.mark.use_custom_data` to skip production hydration:

```python
@pytest.mark.use_custom_data
def test_empty_registry(minimal_registries):
    minimal_registries.components["my_comp"] = {"id": "my_comp", ...}
```

---

## SessionRegistryCache

**File**: `tests/infrastructure/session_cache.py`

A session-scoped cache that loads all game data from disk exactly once per test session, then serves deep copies to every test via `reset_game_state`.

### How It Works

1. On first call to `load_all_data()`, it triggers the real game loaders (`load_components`, `load_modifiers`, `load_vehicle_classes`, `StrategyManager.load_data`)
2. Captures the resulting state from `RegistryManager` via deep copy
3. Sets `_is_loaded = True`; subsequent calls return immediately
4. Getter methods (`get_components()`, `get_modifiers()`, etc.) return **deep copies** to prevent cross-test pollution

### Why Deep Copies

Component and vehicle class objects are mutable. Tests that call `recalculate_stats()` or modify component abilities would corrupt the session cache without deep copies. Every `get_*` call returns an independent copy.

---

## Test Helpers and Factories

### Ship Fixtures (`tests/fixtures/ships.py`)

**Factory function**: `create_test_ship()` -- creates ships with configurable components. Requires `registries` keyword argument.

Parameters: `add_bridge`, `add_engine`, `add_weapons` (count), `add_shields` (count), `add_crew` (default True).

Components are placed in correct layers (crew in CORE, weapons in OUTER, etc.).

**Pytest fixtures** (all use `fresh_registries`):
- `empty_ship` -- hull only
- `basic_ship` -- bridge + engine
- `armed_ship` -- bridge + engine + 2 weapons + shield + armor
- `shielded_ship` -- bridge + engine + shield
- `fully_equipped_ship` -- all component types
- `two_opposing_ships` -- tuple of (team 0, team 1) ships
- `basic_cruiser_ship`, `basic_escort_ship` -- class-specific ships

### Component Fixtures (`tests/fixtures/components.py`)

Factory functions: `create_weapon()`, `create_engine()`, `create_shield()`, `create_armor()`, `create_bridge()`, `create_crew_quarters()`, `create_life_support()`. All require `registries` keyword.

Pytest fixtures: `weapon_component`, `engine_component`, `shield_component`, `armor_component`, `bridge_component`, `crew_quarters_component`, `life_support_component`.

### Battle Fixtures (`tests/fixtures/battle.py`)

- `create_battle_engine()` -- clean BattleEngine, no ships
- `create_battle_engine_with_ships()` -- engine with two opposing teams (requires `registries`)
- `create_mock_battle_engine()` -- Mock object for unit tests
- `create_mock_battle_screen()` -- Mock screen with engine

Pytest fixtures: `battle_engine`, `battle_engine_with_ships`, `mock_battle_engine`, `mock_battle_screen`.

### AI Fixtures (`tests/fixtures/ai.py`)

- `strategy_manager_with_test_data` -- loads test AI strategies from `tests/unit/data/`

### Test Scenario Fixtures (`tests/fixtures/test_scenarios.py`)

Helpers for Combat Lab / simulation test scenarios:
- `create_test_metadata()` -- TestMetadata with defaults
- `create_mock_test_scenario()` -- Mock scenario object
- `create_mock_test_registry()`, `create_mock_test_runner()`, `create_mock_test_history()`
- `create_sample_ship_data()`, `create_sample_component_data()` -- raw JSON data dicts

### Path Utilities (`tests/fixtures/paths.py`)

Functions: `get_project_root()`, `get_data_dir()`, `get_assets_dir()`, `get_test_data_dir()`, `get_unit_test_data_dir()`, `get_simulation_test_data_dir()`.

Pytest fixtures: `project_root`, `data_dir`, `assets_dir`, `test_data_dir`, `unit_test_data_dir`, `simulation_test_data_dir`.

---

## Test Categories

| Directory | Purpose | Speed | Registry |
|---|---|---|---|
| `tests/unit/` | Isolated unit tests | Fast | `fresh_registries` or `minimal_registries` |
| `tests/integration/` | Cross-module integration | Medium | `fresh_registries` |
| `tests/simulation/` | Simulation subsystem tests | Medium | `fresh_registries` |
| `tests/regression/` | Bug regression tests | Varies | `fresh_registries` |
| `tests/performance/` | Performance benchmarks | Slow | `fresh_registries` |
| `combat_lab/` | Combat Lab scenarios (separate pytest root) | Slow | Own conftest and data |

The `combat_lab/` directory has its own `pytest.ini` and is **excluded** from the main test run (`--ignore=combat_lab` in root `pytest.ini`). Run it separately.

---

## Running Tests

```bash
# Full suite with sharded parallel runner (auto-detects CPU count)
python Tools/test_sharded/test_sharded.py

# Incremental (only tests affected by changes)
pytest tests/ --testmon

# Targeted file or directory
pytest tests/unit/simulation/test_damage.py
pytest tests/integration/

# Simulation tests (separate suite)
cd combat_lab && pytest

# With coverage
pytest tests/ --cov=game -n 12

# Single test by name
pytest tests/ -k "test_shield_absorb" -n 0
```

Default `pytest.ini` settings: `testpaths = tests`, `addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --junitxml=./.pytest_cache/test-results.xml`.

---

## Pytest Markers

| Marker | Effect |
|---|---|
| `@pytest.mark.use_custom_data` | Skips production registry hydration in `reset_game_state` |
| `@pytest.mark.simulation` | Tags as simulation test |
| `@pytest.mark.slow` | Tags as slow-running |
| `@pytest.mark.integration` | Tags as integration test |

---

## Common Pitfalls

### 1. Stale Service State Between Tests

`reset_game_state` resets all service instances pre- and post-test via `set_default_xxx()` calls. If you create a new service that holds mutable state, you must add cleanup to the `finally` block in root `conftest.py` or tests will leak state.

### 2. Missing `@pytest.mark.use_custom_data`

If a test needs empty/custom registries but does not use this marker, `reset_game_state` will hydrate production data first, and your custom data will conflict or be overwritten.

### 3. Forgetting `registries=` Keyword

All ship/component creation requires explicit `registries`. Omitting it raises `TypeError`. Use `fresh_registries` fixture in most tests.

### 4. Mutating Session-Scoped Data

Never mutate `session_registries` directly. Always use `fresh_registries` (which deep-copies) for tests that modify registry data.

### 5. Disk I/O in Tests

`reset_game_state` patches loaders to prevent disk reads. If you bypass these patches (e.g., calling `load_components()` directly), you incur disk I/O and may get stale or conflicting data. Use the provided fixtures instead.

### 6. Pygame Display Errors

The `enforce_headless` fixture creates a dummy display. If a test creates its own display or calls `pygame.display.set_mode()`, it may interfere with other tests. Rely on the session-scoped display.

### 7. Component Cache Pollution

`ComponentCacheManager` uses a module-level cache accessed via `get_default_cache_manager()`. `reset_game_state` calls `reset_component_caches()` pre- and post-test. If you manually populate caches, ensure they are cleaned up.

### 8. Parallel Test Isolation (pytest-xdist)

Each xdist worker gets its own process with independent service instances. The `SessionRegistryCache` loads once per worker. Issues arise when tests write to shared files (logs, save files). Use `tmp_path` fixture for file output.

---

## Key File Reference

| File | Purpose |
|---|---|
| `conftest.py` | Root: `reset_game_state`, `enforce_headless`, `configure_test_logging` |
| `tests/conftest.py` | DI fixtures, ship factory, assertion helpers |
| `tests/unit/conftest.py` | Pre-imports `game.ui` to prevent race conditions |
| `tests/infrastructure/session_cache.py` | `SessionRegistryCache` (session-scoped data cache) |
| `tests/fixtures/ships.py` | Ship factory + fixtures |
| `tests/fixtures/components.py` | Component factory + fixtures |
| `tests/fixtures/battle.py` | BattleEngine factory + fixtures |
| `tests/fixtures/ai.py` | StrategyManager test fixture |
| `tests/fixtures/test_scenarios.py` | Combat Lab mock helpers |
| `tests/fixtures/paths.py` | Path resolution utilities |
| `tests/fixtures/common.py` | `initialized_ship_data` fixtures |
| `pytest.ini` | Test config, markers, filter warnings |
