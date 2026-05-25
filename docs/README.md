# Starship Battles Documentation Routing

> **Last verified:** 2026-05-20 - foundation doc-drift sweep (PROJ-467)

Source comparison: `docs/README.md` and
`AgentCoordination/Scratchpad/reports/README_ALT_compact.md`. This is a
compact agent index, not a replacement for the deeper docs.

## Required Reading

Always start here. Before any work, read:

1. `docs/01_ARCHITECTURE.md` - layers, package APIs, protocol boundaries, data flow.
2. `docs/02_PATTERNS.md` - core patterns and extension surfaces.
3. `docs/03_CONVENTIONS.md` - naming, organization, imports, tests, quality rules.

Then read task/domain guides below. Never read `docs/_ignore/`; it is personal
notes, not project documentation.

## Task Docs

- Services/business logic: `docs/04_SERVICES.md`
- Errors/logging: `docs/05_ERROR_HANDLING.md`
- UI/rendering: `docs/06_UI_STYLE_GUIDE.md`
- Development tools, processors, editors, runners: `Tools/README.md`

## Domain Docs

| System | Read | Scope |
|---|---|---|
| Combat/Simulation | `docs/systems/combat_simulation.md` | battle modes, damage pipeline, ship architecture, abilities, replay capture/playback |
| Abilities | `docs/systems/ability_reference.md` | ability registry keys, parameters, source files, stat bindings |
| Strategy/Turn Engine | `docs/systems/strategy_layer.md` | facade, command dispatch, turn phases, fleet hierarchy, policies, deployment zones, events, replay persistence |
| AI | `docs/systems/ai_system.md` | movement behaviors, target evaluation, group targeting, policy manager, adapters |
| Research | `docs/systems/research_system.md` | tech tree, research tracker, leaky bucket mechanics |
| Orders | `docs/systems/orders_system.md` | order lifecycle, types, execution engines |
| Production | `docs/systems/production_system.md` | queues, tick production, spawning, rate resolution, habitability multiplier |
| Resources | `docs/systems/resource_system.md` | unified material/consumable catalog, definitions, component-driven behavior |
| Save / Load | `docs/systems/save_load.md` | `SaveGameService` v3.0.0, turn-based disk layout, atomic writes, no migration, replay-store coupling |
| Fighters | `docs/systems/fighters.md` | fighter design -> bay -> strategic launch -> tactical combat -> recovery; mid-battle launch + end-of-battle reboard; overflow into sector fighter_group |
| Satellites | `docs/systems/satellites.md` | satellite design -> bay -> strategic launch -> stationary tactical combat -> recovery; mirrors fighters with stationary AI, separate ability gates, separate satellite_group namespace |
| Minefields | `docs/systems/minefields.md` | mine design -> bay -> strategic lay -> entry resolution -> tactical per-tick resolver; sensitivity / threshold; selective self-destruct; ramming via warhead detonation |

## How-To Guides

| Task | Read |
|---|---|
| Components/abilities | `docs/guides/component_system.md` |
| Add an ability | `docs/guides/adding_abilities.md` |
| Modifiers | `docs/guides/modifier_system.md` |
| Add a modifier | `docs/guides/adding_modifiers.md` |
| QS complexes | `docs/guides/qs_complex_design.md` |
| Simulation tests | `docs/guides/simulation_testing.md` |
| Test infrastructure | `docs/guides/testing_infrastructure.md` |
| Profiling | [performance_profiling.md](guides/performance_profiling.md) |

## Layer Contract

Dependency flow is bottom-up:

`Core -> Services -> Assets/Engine -> Simulation/Research -> Strategy/AI -> UI`

| Layer | Path | May depend on |
|---|---|---|
| Core | `game/core/` | standard library only |
| Services | `game/services/` | Core only |
| Assets | `game/assets/` | Core, Services |
| Engine | `game/engine/` | Core, Services |
| Simulation | `game/simulation/` | Core, Services, Engine |
| Research | `game/research/` | Core, Services |
| Strategy | `game/strategy/` | Core, Services, Engine, Simulation |
| AI | `game/ai/` | Core, Services, Engine, Simulation |
| UI | `game/ui/` | all layers |

Forbidden shortcuts:

- Core imports no game layer.
- Services imports no game layer except Core.
- Simulation imports no Strategy, AI, or UI.
- Strategy imports no UI.
- Engine imports no Simulation, Strategy, AI, or UI.
- Assets imports no UI, Strategy, Simulation, Research, AI, or Engine.

## Current Contracts

- Strict TDD: write or identify the failing test first, run it, then implement.
- Do not revert unrelated changes; this repo often has parallel workers.
- Python baseline is 3.13. Public functions/methods require return-type
  annotations using PEP 604 style (`int | None`). Dunders are exempt.
- Production files under `game/` have a 500 LOC ceiling; split by responsibility
  when approaching it.
- Broad `except Exception` requires `# Intentional broad catch: <reason>` on the
  same line.
- No save-file migration. Old saves/replays are disposable; do not add
  compatibility shims, fallback systems, or field-rename adapters.
- Use `game.core.paths.Paths` for production paths. Do not hardcode checkout roots
  in agent skills, protocols, prompts, or coordination tools.
- All new image assets are PNG. Component 1024px images are the tracked source set;
  other component sizes are generated derivatives.
- A star system is a radius-50 region around a star; a sector is one `HexCoord`.
  Orders targeting a warp point/planet must validate sector precision, not just
  system membership.
- Historical archives under `Projects/deep_archive/` and
  `Projects/archived_projects/` are not current behavior references.

## Architecture Anchors

- `game/context.py` owns `ApplicationContext`. It manages 10 services:
  `RegistryManager`, `Profiler`, `ComponentCacheManager`, `PolicyManager`,
  `AssetManager`, `SpriteManager`, `ShipThemeManager`, `GameSettings`,
  `LLMProvider`, `ImageProvider`.
- Cross-layer protocols live in the `game/core/protocols/` package, not a single
  `protocols.py` file. Read protocols pair with mutator protocols where write
  ownership matters.
- Registry access should be injected through `IRegistryProvider`. Simulation code
  must not call `get_default_registry_provider()`.
- `run_battle(spec, ai_factory, ship_builder=None, registry_provider=None, ...)`
  is the unified headless entry. If `ship_builder is None`, callers must pass
  `registry_provider`.
- Visual battle setup uses `BattleController.start_from_spec(...)`, which shares
  the same engine construction path as `run_battle`; every battle emits a
  `BattleOutcome`.
- `TurnEngineConfig` has 22 fields: 18 engines plus 4 mutator protocols. Production
  uses `TurnEngineConfig.create_default(...)`; tests override with
  `dataclasses.replace(cfg, field=mock)`.
- `DEFAULT_TICK_PHASE_LIST` and `DEFAULT_END_OF_TURN_PHASE_LIST` define strategy
  turn phase execution. `tick=0` is the end-of-turn sentinel.
- Galaxy/Planet/Star are facade/delegate objects with AST guard tests enforcing
  small method bodies and state encapsulation.
- Habitability factors are registry-driven in
  `game/strategy/data/habitability_factors.py`; habitability feeds carrying
  capacity, happiness, harvest, and production.
- Replay records live under `output/saves/<save>/replays/replay_<uuid>.json`.
  Replay settings live at `output/settings/replay_settings.json`
  (`max_replays_per_save` default 50, `verification_queue_cap` default 16).

## Extension Recipes

- New ability: add or extend a module under
  `game/simulation/components/abilities/`, register through the ability package,
  document registry key/parameters/stat bindings, update data/tests. Abilities
  that parse data must refresh through `_parse_attrs`, not only `__init__`.
- New stat contributor: use
  `game/simulation/entities/stat_contributors/registry.py`. Call
  `register_stat_contributor(...)`, keep the returned handle, and clean up with
  `unregister_stat_contributor(handle)` or `reset_stat_contributor_registry()`.
- New weapon family: add `game/simulation/combat/families/<name>.py`, implement
  `WeaponHandler.fire(...)`, register with `WEAPON_REGISTRY`, add
  `FAMILY_METADATA` if targeting policy differs, and import it from
  `families/__init__.py`. Do not edit central firing/targeting/collision dispatch.
- New strategy command: add a handler module using metadata-only
  `@command_spec(...)`, expose per-module `register(registry)`, and seed through
  the command registry. Do not restore tuple-literal command specs.
- New order execution behavior: add an `IOrderHandler` implementation under
  `game/strategy/engine/order_handlers/` and register it in `OrderHandlerRegistry`.
- New QS design: create `data/designs/qs_<name>.json`, run
  `python Tools/validate_designs/validate_designs.py`, add focused quickstart
  tests, and add starting complexes to `INITIAL_COMPLEXES` when needed.
- New starter race: create `data/races/qs_<name>.json` with race id, flag,
  portrait, theme, homeworld preferences, and aptitudes; cover it in quickstart
  tests.
- New ship theme: create `assets/Images/ShipThemes/<Theme>/theme.json`, 19 PNG skins,
  optional matching portraits, then run the portrait audit and race-setup smoke
  test.

## Stale Name Traps

- Pattern index currently includes sections `#34 Weapon Family Registry` and
  `#35 Stat Contributor Registry`; older "33 patterns" summary text is stale.
- Use `Order`, `OrderType`, `OrderProcessor`, `OrderSerializer`, `OrdersWindow`.
  Do not reintroduce `FleetOrder`, `PlanetOrderType`, or `FleetOrdersWindow`.
- There is no `game/core/input_handler.py`; core input bindings are in
  `game/core/input_actions.py`.
- Major game states are Screens (`BattleScreen`, `StrategyScreen`,
  `DesignWorkshopScreen`, etc.). Do not invent `BattleScene` or `StrategyScene`.
- Workshop files live directly under `game/ui/screens/`; builder panels live under
  `game/ui/screens/builder/`.

## UI Targets

- Minimum supported resolution: 2560x1600.
- Optimized for 4K: 3840x2160.

## Commands

```bash
python Tools/test_sharded/test_sharded.py
pytest tests/ --testmon
pytest tests/path/to/test.py -k test_name
python -m combat_lab.run_tests
python Tools/validate_designs/validate_designs.py
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance
python Tools/audit_shrink/audit_shrink.py
python -m Tools.regenerate_ship_portraits.audit --theme <Theme>
```

Test notes:

- `conftest.py` sets `SDL_VIDEODRIVER=dummy` before imports for headless tests.
- `reset_game_state` clears singletons and hydrates registries between tests.
- Full-suite baseline receipts live under
  `AgentCoordination/generated/test_baseline/`.
- Known flakes: `test_colony_owner_id_matches_empire` isolation and some
  `test_fleet_operations.py` resource accumulation tests. Re-run before triage
  when only 1-4 random failures appear in those areas.

## Doc Map

```text
docs/
  README.md
  01_ARCHITECTURE.md
  02_PATTERNS.md
  03_CONVENTIONS.md
  04_SERVICES.md
  05_ERROR_HANDLING.md
  06_UI_STYLE_GUIDE.md
  _ignore/                         # Personal notes. NOT docs. DO NOT READ.
  guides/
    component_system.md
    adding_abilities.md
    modifier_system.md
    adding_modifiers.md
    qs_complex_design.md
    simulation_testing.md
    testing_infrastructure.md
    performance_profiling.md
  systems/
    ability_reference.md
    combat_simulation.md
    strategy_layer.md
    ai_system.md
    research_system.md
    orders_system.md
    production_system.md
    resource_system.md
    save_load.md
    fighters.md
    satellites.md
    minefields.md
```

