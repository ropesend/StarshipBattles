# Testing Infrastructure

> **Last verified:** 2026-05-20 - PROJ-469 cross-doc fix: corrected the dead `newdocs/02_PATTERNS.md` cross-reference to `docs/02_PATTERNS.md` (the `newdocs/` directory does not exist). Earlier (2026-05-20): Fixed dead single-file pytest example to `tests/unit/simulation/combat/test_damage_calculator.py` (PROJ-468). Prior verification 2026-05-17 against `conftest.py`, `tests/conftest.py`, `tests/unit/conftest.py`, `tests/unit/ui/conftest.py`, `tests/infrastructure/session_cache.py`, `pytest.ini`, `Tools/test_sharded/`, `combat_lab/run_tests.py`, current fixture modules, and the PROJ-443 `norecursedirs` config flip.

Use this as the compact contract for test work. Keep strict TDD: add or identify the failing test first, run it, implement the root-cause fix, then rerun the same test path. Do not read `docs/_ignore/`.

## Core Invariants

- Root `conftest.py` owns global isolation for every pytest test and force-sets `SDL_VIDEODRIVER=dummy` before game imports.
- Every pytest test gets a fresh default `RegistryManager`; production registry hydration is skipped only with `@pytest.mark.use_custom_data`.
- Registry-dependent objects use DI. Ship/component factories and constructors require explicit `registries=`.
- `session_registries` is read-only reference data. Use `fresh_registries` for mutable production-like data and `minimal_registries` for custom empty data.
- `SessionRegistryCache` loads production data once per pytest process or xdist worker, then serves deep copies for mutable dictionaries.
- Pygame runs headless. Root setup initializes Pygame/font once, and `reset_game_state` recovers them before every test because legacy tests may call `pygame.quit()`.
- Real HTTP is blocked for the whole pytest session. Patch `requests.post/get/request/...` inside an individual test when HTTP behavior is the subject.
- The default image provider in tests is `NullImageProvider`; image-generation tests must inject a mock provider explicitly.
- xdist workers isolate process state, not filesystem targets. File-output tests must use `tmp_path` or another test-owned path.
- Combat Lab scenarios are not part of the main pytest suite. Root `pytest.ini` ignores `combat_lab`; the current contract is `python -m combat_lab.run_tests`, not a `combat_lab/pytest.ini` suite.

## Conftest Stack

`conftest.py` at repo root provides autouse fixtures for all pytest tests:

- `reset_game_state` (function scope): creates a fresh `RegistryManager`, resets component caches and `STAT_CONTRIBUTOR_REGISTRY` before and after each test, reinitializes Pygame/font if needed, hydrates production data from `SessionRegistryCache` unless `use_custom_data` is present, injects component/modifier caches, patches `game.simulation.entities.ship_loader.load_vehicle_classes` to avoid disk I/O, hydrates `PolicyManager`, and finally clears registry/event/policy/UI defaults.
- `enforce_headless` (session scope): sets dummy SDL video, initializes Pygame/font, and creates a persistent dummy display at `DisplayConfig.test_resolution()`.
- `configure_test_logging` (session scope): attaches `NullHandler` to the `game` logger to suppress file I/O.

`tests/conftest.py` adds shared project fixtures and test guards:

- `_block_real_http` (session autouse): replaces `requests.post`, `get`, `put`, `delete`, `patch`, `head`, and `request` with raisers.
- `_reset_image_provider` (function autouse): resets the module-level image provider to `NullImageProvider` before and after every test.
- Registry fixtures: `session_registries`, `fresh_registries`, `minimal_registries`, `mock_registries`, `stable_component_registries`.
- Data fixtures: `global_ship_data`, `global_ship_data_with_modifiers`.
- Helpers: `ship_factory`, `make_mock_ship_instance()`, `make_colony_ship_for_planet()`, `make_test_race()`, `assert_success()`, `assert_list_length()`.

`tests/unit/conftest.py` pre-imports `game.ui` and verifies `renderer`, `screens`, and `panels` are loaded to reduce parallel collection races.

`tests/unit/ui/conftest.py` adds UI-specific imports, `ui_manager`, and `pygame_display_reset`. Use `ui_manager` for pygame_gui tests; it clears and reuses a cached manager and normalizes the display to 1440x900 around each UI test.

There is no top-level `tests/integration/conftest.py`. Integration subdirectories may define domain-local conftests and still inherit root plus `tests/` fixtures.

## Registry Fixtures

| Fixture | Scope | Data | Use |
|---|---:|---|---|
| `session_registries` | session | cached production data plus `ResourceCatalog.from_json()` | read-only reference |
| `fresh_registries` | function | deep copy of production dictionaries, shared resource catalog | default mutable registry |
| `minimal_registries` | function | empty dictionaries | isolated unit tests |
| `mock_registries` | function | alias for `minimal_registries` | tests emphasizing mocked data |
| `stable_component_registries` | function | production data plus `tests/fixtures/test_components.json` overlays | regression tests that must not drift with balance data |

Production-like test:

```python
def test_ship_creation(fresh_registries):
    ship = Ship(
        "Test",
        0,
        0,
        (255, 255, 255),
        ship_class="Escort",
        registries=fresh_registries,
    )
    comp = create_component("laser_cannon", registries=fresh_registries)
    ship.add_component(comp, LayerType.OUTER)
    ship.recalculate_stats()
```

Custom empty-data test:

```python
@pytest.mark.use_custom_data
def test_custom_component(minimal_registries):
    minimal_registries.components["my_comp"] = {"id": "my_comp"}
```

If `use_custom_data` is missing, root hydration runs first and may overwrite or conflict with custom data.

## Session Registry Cache

File: `tests/infrastructure/session_cache.py`

`SessionRegistryCache` is a thread-safe singleton for test data loading. `load_all_data()` uses real loaders with `Paths.DATA_DIR`: `load_modifiers`, `load_components`, `load_vehicle_classes`, and `PolicyManager.load_data`. It captures components, modifiers, vehicle classes, targeting policies, and movement policies after loader logic has run.

Getter methods (`get_components()`, `get_modifiers()`, `get_vehicle_classes()`, `get_targeting_policies()`, `get_movement_policies()`) return deep copies. Do not add cached mutable data without also adding a deep-copy getter and wiring it through `reset_game_state` or the relevant fixture.

`session_registries` separately loads `ResourceCatalog.from_json()`; the cache does not currently own the resource catalog.

## Fixture Modules

Files under `tests/fixtures/` are reusable helper modules, not globally available pytest fixtures unless a conftest imports them or a test imports the helper directly.

`tests/fixtures/ships.py`

- `create_test_ship(..., registries=...)` creates a `Ship` with optional bridge, engine, weapons, shields, and crew support. Crew goes in CORE; engine/weapons/shields use legal layers.
- Common fixtures, when imported by a conftest: `empty_ship`, `basic_ship`, `armed_ship`, `shielded_ship`, `fully_equipped_ship`, `two_opposing_ships`, `basic_cruiser_ship`, `basic_escort_ship`.

`tests/fixtures/components.py`

- Factories requiring `registries=`: `create_weapon()`, `create_engine()`, `create_shield()`, `create_armor()`, `create_bridge()`, `create_crew_quarters()`, `create_life_support()`.
- Matching component fixtures exist when imported by a conftest.

`tests/fixtures/battle.py`

- `make_minimal_spec()` builds a minimal `BattleSpec` for spec-based battle tests.
- `start_battle_screen_with_minimal_spec()` replaces legacy `BattleScreen.start(team0, team1)` test setup.
- `create_battle_engine()`, `create_battle_engine_with_ships(..., registries=...)`, `create_mock_battle_engine()`, and `create_mock_battle_screen()` cover engine and screen setup.

`tests/fixtures/ai.py`

- `policy_manager_with_test_data` loads test policies from `tests/unit/data/test_targeting_policies.json` and `test_movement_policies.json`, then clears the manager afterward.

`tests/fixtures/test_scenarios.py`

- Combat Lab helpers: `create_test_metadata()`, `create_mock_test_scenario()`, `create_mock_test_registry()`, `create_mock_test_runner()`, `create_mock_test_history()`, `create_scenario_info()`, sample ship/component data fixtures.
- `patch_spec_compiler_to_delegate_to_mock_scenario()` patches `combat_lab.spec_compiler.build_test_battle_spec` so old scenario mocks still delegate through `scenario.to_spec()`.

`tests/fixtures/paths.py`

- Repo path helpers delegate to `game.core.paths.Paths`.
- Current fixtures: `project_root`, `data_dir`, `assets_dir`, `test_data_dir`, `unit_test_data_dir`, `combat_lab_data_dir`.
- Stale name to avoid: `simulation_test_data_dir`; the current helper is `combat_lab_data_dir`.

Other important fixture modules:

- `tests/fixtures/common.py`: `initialized_ship_data`, `initialized_ship_data_with_modifiers`.
- `tests/fixtures/turn_engine.py`: turn-engine builder helpers used by strategy integration/unit conftests.
- `tests/fixtures/strategy_entities.py`, `galaxy_fixtures.py`, `mock_planet.py`, `yard_facility.py`: strategy-domain fixtures.
- `tests/fixtures/ui_widget_factory.py` plus `*_ui_builder.py` fixtures: UI construction seams documented in `docs/02_PATTERNS.md`.

## Test Layout

| Path | Purpose | Registry norm |
|---|---|---|
| `tests/unit/` | isolated unit tests | `fresh_registries`, `minimal_registries`, or local mocks |
| `tests/integration/` | cross-module workflows | `fresh_registries` plus domain conftests |
| `tests/integration/simulation/` | simulation integration tests | `fresh_registries` |
| `tests/performance/` | benchmarks and count-based performance gates | focused fixtures, often `fresh_registries` |
| `tests/regression/` | bug and behavior regression tests | fixture depends on domain |
| `tests/projects/` | project-specific acceptance/regression tests | project-specific |
| `tests/repro_issues/` | focused reproductions | minimal setup for the issue |
| `combat_lab/` | Combat Lab scenario framework | own runner and data, excluded from main pytest |

Stale path to avoid: there is no top-level `tests/simulation/`; use `tests/unit/simulation/` or `tests/integration/simulation/`.

Performance gate to preserve: `tests/performance/test_contested_hex_round_budget.py` locks the per-fleet-tick combat-dispatch budget. The 5-hex, 3-empire, 2-fleet scenario must stay at no more than 150 dispatches per turn.

Known flakes from repo instructions: if 1-4 random failures appear around `test_colony_owner_id_matches_empire` or `test_fleet_operations.py` resource accumulation, rerun before deep triage.

## Commands

Canonical full suite:

```powershell
python Tools/test_sharded/test_sharded.py
```

Sharded runner options:

```powershell
python Tools/test_sharded/test_sharded.py --shards 8
python Tools/test_sharded/test_sharded.py --verbose
.\Tools\test_sharded\test.ps1
```

Targeted and incremental pytest:

```powershell
pytest tests/ --testmon
pytest tests/unit/simulation/combat/test_damage_calculator.py -n 0
pytest tests/integration/ -n 0
pytest tests/ -k "test_shield_absorb" -n 0
pytest tests/ --cov=game -n 12
pytest tests/performance/test_contested_hex_round_budget.py -n 0
```

Combat Lab:

```powershell
python -m combat_lab.run_tests
python -m combat_lab.run_tests --list
python -m combat_lab.run_tests --fast
python -m combat_lab.run_tests BEAM
python -m combat_lab.run_tests PROP-001
```

Root `pytest.ini` defaults:

```ini
testpaths = tests
addopts = -n 4 --ignore=Refactoring --ignore-glob=*.txt --ignore=combat_lab --junitxml=./.pytest_cache/test-results.xml
python_files = test_*.py
pythonpath = .
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ship_themes
```

`norecursedirs` rationale (PROJ-443): three tokens were removed from the
default list — `data`, `combat_lab`, and `Assets`. `norecursedirs`
patterns are matched against directory **basenames at any depth** (per
`_pytest/main.py:455-458`), so those tokens collided with real test
directories (`tests/unit/strategy/data/`, `tests/unit/combat_lab/`,
`tests/unit/assets/`, etc.), silently hiding 126 test files from the
canonical sharded run. The top-level `data/` / `Assets/` / `combat_lab/`
directories that the tokens were trying to skip are already excluded by
`testpaths = tests` (which restricts default collection to `tests/`),
plus the explicit `--ignore=combat_lab` in `addopts`. The structural
file-level regression guard at `tests/static_guards/test_no_hidden_test_files.py`
prevents this class of mistake from recurring.

Markers in `pytest.ini`: `use_custom_data`, `simulation`, `slow`, `integration`, `performance`.

## Sharded Runner Contract

File: `Tools/test_sharded/test_sharded.py`

- Auto-detects physical CPU cores for the default shard count.
- Collects pytest node IDs with `pytest tests/ --collect-only -q --no-header -n 0`.
- Groups tests by source file so one file is assigned to one shard.
- First run uses round-robin by file; later runs use greedy duration balancing when timing coverage is sufficient.
- Each shard runs as a single-threaded pytest subprocess with `--override-ini=addopts=`, `--tb=short`, `-q`, and `-n 0`.
- Timing data is local: `.test_durations.json` and `.test_file_duration_history.json`.
- Per-shard JUnit XML and duration sidecars live under `.pytest_cache/shard_results/`.
- Green whole-suite runs update `AgentCoordination/generated/test_baseline.json` only when canonical counts change or schema migration is needed.
- Every green whole-suite run writes a per-install receipt under `AgentCoordination/generated/test_baseline/by_install/<install_id>.json`; install ID comes from `AgentCoordination/local/install_id.json`.

## Extension Recipes

Add a mutable module-level service:

1. Prefer constructor or fixture injection for new code.
2. Add pre-test and post-test cleanup in root `reset_game_state` if module-level state remains.
3. Reset defaults with existing `set_default_xxx()` accessors or add explicit reset APIs.
4. Add a focused test that fails when state leaks across tests.

Add production data to cached test setup:

1. Load it in `SessionRegistryCache.load_all_data()` using `Paths`, not hardcoded checkout paths.
2. Store captured state on the cache.
3. Expose a deep-copy getter for mutable data.
4. Hydrate the corresponding manager in `reset_game_state` or the nearest fixture.
5. Add or update tests for the cache behavior.

Add registry-dependent factories:

1. Require keyword-only `registries=`.
2. Use `fresh_registries` in pytest fixtures.
3. Use `minimal_registries` plus `@pytest.mark.use_custom_data` for empty/custom registry tests.
4. Never fall back to global registry lookup from simulation-layer helpers.

Add reusable fixtures:

1. Put shared fixtures in the nearest common ancestor `conftest.py`.
2. Keep reusable helpers in `tests/fixtures/<domain>.py`.
3. Import helper fixtures into conftests that need them; do not assume `tests/fixtures/` is automatically discovered.
4. Avoid duplicate fixture definitions across conftests.

Add file-output tests:

1. Use `tmp_path` or a test-owned temporary directory.
2. Do not write logs, saves, generated assets, snapshots, or histories to shared repo paths unless cleanup is explicit and xdist-safe.
3. Avoid depending on local files produced by previous runs.

Add UI or Pygame tests:

1. Rely on root headless setup and `tests/unit/ui/conftest.py` fixtures.
2. Use `ui_manager` for pygame_gui widget tests.
3. Avoid individual `pygame.display.set_mode()` calls unless the test fully restores state.
4. For isolated UIWindow/widget construction, use `tests/fixtures/ui_widget_factory.py` and the relevant `Null*UiBuilder` or `Mock*UiBuilder` fixture.

Add a marker or test category:

1. Register the marker in `pytest.ini`.
2. Document the command users should run.
3. If the category should stay out of default runs, add the appropriate ignore rule and explain the alternate runner.

## Common Failure Modes

- Missing `@pytest.mark.use_custom_data`: root hydration runs and conflicts with custom registry data.
- Missing `registries=`: ship/component construction raises `TypeError`.
- Mutating `session_registries`: mutable state leaks into later tests.
- Mutating shared resource catalog assumptions: use a fresh/local catalog if a test needs to alter resources.
- Calling disk loaders directly: bypasses session cache patches and can introduce slow or stale data reads.
- Component cache pollution: rely on root `reset_component_caches()` or clean manual cache writes.
- Stat contributor pollution: root resets `STAT_CONTRIBUTOR_REGISTRY`; tests that register contributors should still clean up handles when they assert local registry behavior.
- Real HTTP call: session guard raises `RuntimeError`; mock `requests` methods inside the test scope.
- Image-generation call without injection: `NullImageProvider` raises; inject a mock provider explicitly.
- Pygame display/font errors: root recovers init/font state, and UI conftest normalizes display for UI tests.
- Shared file writes under xdist: process isolation does not protect shared paths.

## Key Files

| File | Role |
|---|---|
| `conftest.py` | root isolation, headless Pygame, logging suppression |
| `tests/conftest.py` | HTTP/image guards, registry fixtures, ship factory, shared helpers |
| `tests/unit/conftest.py` | early `game.ui` import for collection stability |
| `tests/unit/ui/conftest.py` | UI manager and display reset fixtures |
| `tests/infrastructure/session_cache.py` | production data session cache with deep-copy getters |
| `tests/fixtures/ships.py` | ship factory and ship fixtures |
| `tests/fixtures/components.py` | component factories and fixtures |
| `tests/fixtures/battle.py` | battle spec, engine, and screen helpers |
| `tests/fixtures/ai.py` | AI policy fixture |
| `tests/fixtures/test_scenarios.py` | Combat Lab scenario mock helpers |
| `tests/fixtures/paths.py` | repo/data/assets/test/combat-lab path helpers |
| `tests/fixtures/common.py` | initialized ship-data fixtures |
| `tests/fixtures/turn_engine.py` | strategy turn-engine test builder |
| `tests/fixtures/ui_widget_factory.py` | UI widget construction helper |
| `pytest.ini` | default pytest config, markers, ignores, warnings |
| `Tools/test_sharded/test_sharded.py` | canonical full-suite sharded runner |
| `Tools/test_sharded/README.md` | sharded-runner behavior and baseline schema |
| `combat_lab/run_tests.py` | Combat Lab scenario runner |
