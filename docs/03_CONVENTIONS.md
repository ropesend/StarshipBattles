# Conventions

> **Last verified:** 2026-05-22 - PROJ-483 Phase 4: added mypy `--strict` coverage section under Type Hints noting the 6 strict Foundation layers (research/services/assets/engine/ai/core) and the 3 deferred heavy layers (simulation/strategy/ui). Earlier (2026-05-20): PROJ-469 cross-doc fix: corrected the `IIssuerAdapter` cross-reference from Pattern #40 to Pattern #41 (Polymorphic Order Issuer; #40 is the Named Pre-Tick Setup Registry) per `docs/02_PATTERNS.md:74-75`. Earlier (2026-05-20): PROJ-467 foundation doc-drift sweep: corrected the `get_system_at_hex()` path to `game/strategy/services/galaxy_pathfinding_service.py` and removed a hardcoded `C:/Users/rossr/...` checkout path that violated the doc's own no-checkout-path convention. Earlier (2026-05-17): Round 4 doc-audit fixes: corrected `markers.py` listing (removed retired `VehicleLaunchAbility`), added the "polymorphic FMS commands (`planet_id` rule)" convention, the right-click context-menu triple convention, and the "Capability validation is hard, not soft" convention.

Compact convention reference for Starship Battles. Use this with `docs/01_ARCHITECTURE.md` and `docs/02_PATTERNS.md` before coding.

## Naming Rules

### Battle vs Combat

- **Battle** means full simulation orchestration, engagement state, resolution, and high-level APIs. Examples: `BattleEngine`, `BattleService`, `BattleController`, `BattleState`, `BattleResult`.
- **Combat** means entity-level per-ship or per-component behavior. Examples: `ShipCombatEngine`, `CombatPropulsion`, `CombatConstants`.
- Use **Battle** for systems that manage an overall engagement. Use **Combat** for per-ship or per-component mechanics.

### Screen vs Scene

- **Screen** means major game state: `BattleScreen`, `StrategyScreen`, `DesignWorkshopScreen`, `BuildQueueScreen`, `FleetBattleSetupScreen`, `TestLabScreen`, `NewGameSetupScreen`, `RaceSetupScreen`, `GalaxyTestScreen`.
- `FleetBattleSetupScreen` is aliased as `BattleSetupScreen` by `game/screen_router.py`.
- **Scene** means menu/minor state: `MenuScene`, `KeybindingsScene`.
- Do not introduce `BattleScene` or `StrategyScene`.

### Builder vs Workshop

- **Builder** panels are reusable UI internals under `game/ui/screens/builder/`: `left_panel.py`, `right_panel.py`, `schematic_view.py`, `detail_panel.py`, `weapons_panel.py`.
- **Workshop** is the top-level design screen family directly under `game/ui/screens/`: `workshop_screen.py` (`DesignWorkshopScreen`), `workshop_viewmodel.py`, `workshop_context.py`, `workshop_event_router.py`, `workshop_data_loader.py`, `workshop_data_reloader.py`, `workshop_ship_io.py`.
- Workshop files do not live in a `workshop/` subdirectory.

### Star System vs Sector

- **Star system/system** means a circular map region centered on a star. Data type: `StarSystem`.
- **Sector** means one addressable galaxy hex. Data type: `HexCoord`.
- A system boundary has radius 50 hexes from `system.global_location`, defined by `GalaxyPathfindingService.get_system_at_hex()` in `game/strategy/services/galaxy_pathfinding_service.py`; systems are placed at least 400 hexes apart center-to-center.
- A system contains many sectors: central star, orbiting planets, warp points, and storms each occupy specific sectors.
- Entities inside a system store local coordinates. Convert with `global_hex = system.global_location + entity.location`.
- `fleet.location`, `warp_point.location`, and `planet.location` are sectors. `system.global_location` is the system origin sector in global coordinates.
- Validate fleet position at sector precision for orders targeting a planet, warp point, or location. Being in the right system is not enough.

### Handler Names

- Prefix input handlers by screen/context: `StrategyInputHandler`, `TestLabInputHandler`, `WeaponsInputHandler`.
- Current files: `game/ui/screens/strategy_input_handler.py`, `game/ui/screens/test_lab/screen_input_handler.py`, `game/ui/screens/builder/weapons_input_handler.py`.
- `game/core/input_handler.py` does not exist. Core owns `game/core/input_actions.py`.

### MVVM and UI Decomposition Names

- `*_viewmodel.py` / `*_view_model.py`: screen state, events, and business logic without Pygame. Examples: `workshop_viewmodel.py`, `build_queue_viewmodel.py`, `transfer_view_model.py`.
- `*_controller.py`: facade queries and command emission boundary. Examples: `transfer_controller.py`, `new_game_setup_controller.py`.
- `*_renderer.py`: `pygame_gui` widget construction, update, and destruction.
- `*_ui_builder.py`: per-class UI builder protocol; pair with `Null{Foo}UiBuilder` and `Mock{Foo}UiBuilder` fixtures.
- `*_context.py`: shared data context between panels.
- `*_event_router.py`: event dispatch between UI components.
- `*_data_loader.py`: data loading coordination.
- The `controller` / `renderer` / `ui_builder` split follows compositional construction and the UI widget factory/two-stage UIWindow retrofit in `docs/02_PATTERNS.md`.
- UI builder test fixtures live under `tests/fixtures/` with the same base name, for example `tests/fixtures/transfer_ui_builder.py`.

#### Right-click context menus

Per-entity right-click menus follow the
`<entity>_menu_items.build_menu_items(...)` + `<entity>_context_menu`
+ shared `<feature>_menu_callbacks` triple:

- Fleet precedent: `game/ui/screens/fleet_menu_items.py`.
- Planet (Round 4): `game/ui/screens/planet_menu_items.py`,
  `planet_context_menu.py`, and the shared
  `fms_menu_callbacks.py` (Lay Mines / Launch * / Recover *).

`build_menu_items` returns a flat list of menu rows derived from
capability gates and the issuer's current state (carrier present,
staging-yard contents, etc.). The shared `*_menu_callbacks` module
dispatches the matching `IssueCommand` via the facade — UI menu code
never builds DTOs inline. Reuse this triple when adding context-menu
entries for new entity kinds rather than wiring callbacks directly
into the context menu.

### Ability Module Names

All ability modules live in `game/simulation/components/abilities/`.

- `__init__.py`: registry and public exports.
- `base.py`: ability base classes.
- `cargo.py`: `CargoStorage`.
- `colonize.py`: `ColonizePlanet`.
- `crew.py`: `CrewCapacity`, `LifeSupportCapacity`, `RequiresMaintenance`, `ProvidesMaintenance`.
- `defense.py`: `ShieldProjection`, `ShieldRegeneration`, `EmissiveArmor`, `ToHit*Modifier`.
- `harvester.py`: `ResourceHarvesterAbility`, `SpaceShipyardAbility`, `LocalStorageAbility`.
- `markers.py`: `CommandAndControl`, `StructuralIntegrity`, `RequiresCommandAndControl`, `RequiresCombatMovement`, `MultiplexTrackingAbility`, `VehicleStorageAbility`, `PodStorageAbility` (the legacy `VehicleLaunchAbility` was removed in PROJ-FMS-C audit Fix 1; tactical launch lives in `launch.py::TacticalFighterLaunchAbility`).
- `propulsion.py`: `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `WarpJump`.
- `resources.py`: component-level `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`; `game/core/resources.py` owns `ResourceCatalog`.
- `stat_keys.py`: `StatKey`, `AbilityStatBinding`.
- `planetary.py`: `PlanetaryShieldAbility`, `StrategicResourceGenerationAbility`.
- `superweapons.py`: star, planet, warp-point, and strategic effects.
- `ui_colors.py`: UI hint color constants.
- `weapons.py`: `WeaponAbility`, `BeamWeaponAbility`, and related weapon abilities.

Import abilities from the package, not individual submodules:

```python
from game.simulation.components.abilities import CombatPropulsion, WeaponAbility
```

### Order System Names

Use the unified order API:

- `Order` from `game.strategy.data.order_types`.
- `OrderType`, including generic ability toggles such as `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY`.
- `OrderProcessor` from `order_processor.py`.
- `OrderSerializer` from `order_serializer.py`.
- `OrdersWindow` from `orders_window.py`.

Old fleet-only names and compatibility alias modules are deleted. Do not reintroduce `FleetOrder`, `PlanetOrderType`, `FleetOrderProcessor`, `FleetOrderSerializer`, or `FleetOrdersWindow`.

### Polymorphic FMS commands (`planet_id` rule)

All five FMS `Issue*Command` DTOs in
`game/strategy/engine/commands/__init__.py` accept an optional
`planet_id: Optional[int] = None` alongside the existing
`fleet_id: Optional[int] = None`:

- `IssueLayMinesCommand`
- `IssueLaunchFightersCommand`
- `IssueLaunchSatellitesCommand`
- `IssueRecoverFightersCommand`
- `IssueRecoverSatellitesCommand`

Exactly one of `fleet_id` / `planet_id` must be set per command;
`count` is `Optional[int] = None` (None = lay/launch/recover ALL
matching, positive int = partial). Order handlers operate on
`IIssuerAdapter` (`game/strategy/engine/issuer_adapter.py`) so the
same handler family serves fleet-ship and planet-facility issuers —
see Pattern #41 in `docs/02_PATTERNS.md`. Do not add a parallel
`PlanetIssue*Command` family or fork the order handlers.

## File Organization

### Layer Dependencies

| Layer | Path | Allowed dependencies |
|---|---|---|
| Core | `game/core/` | Standard library only |
| Services | `game/services/` | Core only |
| Assets | `game/assets/` | Core, Services |
| Engine | `game/engine/` | Core, Services |
| Simulation | `game/simulation/` | Core, Services, Engine |
| Research | `game/research/` | Core, Services |
| Strategy | `game/strategy/` | Core, Services, Engine, Simulation |
| AI | `game/ai/` | Core, Services, Engine, Simulation |
| UI | `game/ui/` | All layers |

Rules:

- Respect downward dependency flow.
- Core must not import game layers. Services must not import any game layer except Core.
- Simulation must not import Strategy, AI, UI, or Pygame.
- Strategy must not import UI or Pygame.
- Engine must not import Simulation, Strategy, AI, or UI.
- Assets must not import UI, Strategy, Simulation, Research, AI, or Engine.

### New File Placement

- Cross-cutting service used by 2+ layers: `game/services/`, with a documented protocol and testable implementation.
- Layer-local service: `game/<layer>/services/`.
- New ship ability: `game/simulation/components/abilities/`.
- New component modifier: `game/simulation/components/`.
- New battle system: `game/simulation/systems/`.
- New strategy system: `game/strategy/systems/`.
- New UI screen: `game/ui/screens/`.
- New builder panel: `game/ui/screens/builder/`.
- JSON game data: `data/`.
- Starter ship/complex designs: `data/designs/qs_*.json`.
- Starter race configs: `data/races/qs_*.json`.

### File Size

- Production files under `game/` should stay below 500 LOC.
- Test files under `tests/`, `combat_lab/`, and similar test-only areas are exempt.
- If a production file approaches or exceeds 500 LOC, split by cohesive responsibility rather than by arbitrary line ranges.
- Preserve public API with a re-export shim only when many callers exist; migrate callers directly when few.
- Use a subpackage when 3+ closely related files form a logical unit. Keep flat layout for loosely related files.
- Existing over-limit files are not precedent for new growth.

### UI Screen Budget

- Classes implementing `IScene` should stay under 300 LOC.
- Add UI behavior to controllers, view models, renderers, input handlers, data sources, or helpers instead of growing large screen classes.
- Delegate classes should also aim for 300 LOC. A larger controller is a review signal and needs clear single-responsibility justification.
- For 4K UI work, minimum supported resolution is 2560x1600; the game is optimized for 3840x2160.

## Import, Path, and Asset Conventions

### Imports

Use three import groups separated by blank lines:

```python
import logging
import os
from typing import TYPE_CHECKING

import pygame

from game.core.config import BattleTuning, PhysicsConfig
from game.core.math import Vector2
from game.simulation.entities.ship import Ship
```

Rules:

- Use `from __future__ import annotations` when needed for forward references.
- Put type-only imports under `if TYPE_CHECKING:`.
- Do not use wildcard imports.
- Import abilities from `game.simulation.components.abilities`, not individual ability files.

### Production Paths

- Production code must use `game.core.paths.Paths` constants for repo file paths.
- Do not hardcode paths such as `"data/components.json"` or `os.path.join("assets", "Images", "ShipThemes", ...)`.
- For path default arguments, use `None` and resolve inside the body.
- Tests may use relative paths to test-specific data.
- CLI scripts with explicit path arguments such as `--output` are exempt.

```python
from game.core.paths import Paths

path = Paths.COMPONENTS_FILE
theme_dir = os.path.join(Paths.SHIP_THEMES_DIR, theme, "Portraits")
```

### Agent and Tool Paths

Reusable agent instructions, skills, protocols, daemon prompts, and coordination scripts must not embed developer-machine checkout roots such as `C:\Dev2\StarshipBattles`.

Use:

- Repo-relative paths when commands run from repo root.
- Runtime repo-root discovery by walking upward to sentinels such as `game/`, `data/`, and `AGENTS.md`.
- Script-relative discovery via `Path(__file__).resolve()` for repo-local tools.
- `<repo-root>` placeholders in illustrative docs.

Hardcoded checkout paths are allowed only in ignored machine-local files or historical examples explicitly marked non-reusable. `docs/_ignore/` is personal notes, not project documentation.

### Image Assets

- New image assets must be PNG. Do not add new `.jpg`, `.jpeg`, or `.webp`.
- Existing JPG assets should migrate to PNG only when touched or during focused asset work.
- New code should construct PNG filenames. Temporary multi-format filters are acceptable during transition.

#### Image Asset Derivatives — canonical pattern

**Each multi-size image-asset family stores exactly one master size in source control. All other sizes are regenerated locally at startup.**

This applies to every size-tiered image family in the repo:

| Family | Root | Master | Generated sizes | Wrapper module |
|---|---|---:|---|---|
| Components | `assets/Images/Components/` | `1024/` | `2048`, `512`, `256`, `128`, `64` | [`game/assets/component_derivatives.py`](game/assets/component_derivatives.py) |
| Flags | `assets/Images/Flags/Processed/` | `flag_*/1024/` | `512`, `256`, `128`, `64`, `32` (per flag) | [`game/assets/flag_derivatives.py`](game/assets/flag_derivatives.py) |
| Stars | `assets/Images/Stellar Objects/Stars/` | `1024/` | `512`, `256`, `128` | [`game/assets/star_derivatives.py`](game/assets/star_derivatives.py) |
| Planets | `assets/Images/Stellar Objects/Planets/` | `2048/` | `1024`, `512`, `256`, `128` | [`game/assets/planet_derivatives.py`](game/assets/planet_derivatives.py) |

The shared engine lives at [`game/assets/image_derivatives.py`](game/assets/image_derivatives.py). Each per-family module is a thin wrapper that configures a `DerivativeFamilySpec` (root dir, master size, derivative sizes, master glob, optional filename transform) and calls `ensure_image_derivatives(spec)`. The bootstrap sequence calls every wrapper in turn (see [`game/app_bootstrap.py`](game/app_bootstrap.py)).

Contracts:

- The master directory is the only tracked size for each family.
- Derivative size directories and the per-family `.<family>_derivatives_manifest.json` hash manifest are intentionally `.gitignore`'d.
- A SHA-256-keyed manifest fast-paths runs where the master is unchanged on disk. A content change (or a `git checkout` of new master bytes) bumps mtime, invalidates the manifest entry, and triggers regeneration of every size for that master.
- Derivatives have the same image format and aspect as the master (square assumed). The engine resizes with `PIL.Image.Resampling.LANCZOS`.
- Generated derivative files are written atomically (`<file>.tmp` → `os.replace`).
- Components encode the size in the filename (`1024Portrait_Comp_001.png` → `64Portrait_Comp_001.png`); all other families keep the filename unchanged.

**Adding a new size-tiered family.** Add a wrapper module that imports the engine, declares `MASTER_SIZE` / `DERIVATIVE_SIZES` / `MANIFEST_NAME`, builds a `DerivativeFamilySpec`, and exposes an `ensure_<family>_derivatives()` function. Wire that function into `app_bootstrap.py`. Add the master directory to the `Paths` registry and the derivative sizes + manifest to `.gitignore`. Add tests for the wrapper in `tests/unit/assets/`.

**Adding a new asset to an existing family.** Drop the new master PNG into the master directory. Startup will generate the derivatives on next run. No code change needed.

#### Special stellar-object portraits

Special stellar-object portraits (e.g., the Dyson Sphere) live in dedicated `assets/Images/Stellar Objects/<thing>/` folders (e.g., `Sphere world/Sphereworld_Portrait.png`) — one resolution per object, not size-tiered, so they do not participate in the derivative pipeline. `AssetManager.load_planet_image()` searches the planet size chain first, then falls back to the stellar-object directories listed in its `_STELLAR_OBJECT_FALLBACK_DIRS` tuple. To add a new special stellar-object portrait, place the PNG in its own `Stellar Objects/<thing>/` folder, expose a `Paths.<THING>_DIR` constant, and append it to `_STELLAR_OBJECT_FALLBACK_DIRS` — no asset duplication into the planet pool.

## Test Conventions

### Strict TDD

Write or identify the failing test first, run it to confirm failure, then implement. For documentation-only replacement work, use a focused validation command that fails before the file/content exists, then re-run it after writing.

### Test Layout

Tests mirror source structure:

- `game/simulation/systems/battle_engine.py` -> `tests/unit/simulation/systems/`
- `game/ui/screens/strategy_screen.py` -> `tests/unit/ui/screens/test_strategy_screen.py`
- `game/simulation/components/abilities/defense.py` -> `tests/unit/simulation/components/abilities/`

Test file names use `test_<source_file_name>.py`.

### conftest Hierarchy and Fixtures

- `conftest.py`: repo-root autouse isolation. It force-sets `SDL_VIDEODRIVER=dummy`, owns `reset_game_state`, clears singleton/module state, hydrates registries from the session cache, and restores pygame/font state per test.
- `tests/conftest.py`: shared data fixtures including `session_registries`, `fresh_registries`, `minimal_registries`, `mock_registries`, and `ship_factory`.
- `tests/unit/conftest.py`: unit-wide fixtures.
- `tests/unit/<layer>/conftest.py`: layer-specific fixtures.
- `tests/integration/<domain>/conftest.py`: integration scenario fixtures.

Fixture contracts:

- `session_registries`: session-scoped loaded registries, read-only.
- `fresh_registries`: function-scoped deep copy for isolation.
- `minimal_registries`: empty registries for pure unit tests.
- `mock_registries`: alias/minimal registries with mock data.
- `ship_factory`: helper for ships from `fresh_registries`.

Put shared fixtures in the nearest common ancestor conftest. Do not duplicate fixtures.

### Test Commands

```bash
pytest tests/ --testmon
pytest tests/path/to/test.py -k test_name
python Tools/test_sharded/test_sharded.py
python -m combat_lab.run_tests
pytest tests/ --cov=game -n 12
```

`python Tools/test_sharded/test_sharded.py` is the canonical full-suite runner. If a small number of known-isolation/resource flakes appear, re-run before triaging.

## JSON Data Conventions

### Components

`data/components.json` has a top-level `"components"` array. Each component requires a unique snake_case `id`. `mass` and `hp` may be numbers or formulas prefixed with `=`. `abilities` maps ability class names to `true`, a number, a formula string, or `{"value": N}`. `allowed_vehicle_types` restricts valid vehicles.

#### One component per role; scale via `simple_size_mount`

Ship one component per role and let `simple_size_mount` (the canonical size scaler, see `data/modifiers.json`) drive size variation through `*_mult` stat keys: `damage_mult`, `mass_mult`, `hp_mult`, `cost_mult`, `launch_rate_mult`, `recovery_rate_mult`, `bay_capacity_mult`, `range_mult`, etc.

Do **not** ship per-size-tier component variants like `<role>_small / <role>_medium / <role>_large`. The size mount exists precisely to make this proliferation unnecessary, and tier triples are fragile — every balance change touches multiple JSON entries, every test fixture has to pick a tier, and every doc has to enumerate the tiers.

**Exception**: sizes that are *radically* different in role / mass / interface. A fighter-grade component and a ship-grade component differ enough in mass class, allowed-vehicle types, and ability surface that they are two distinct parts (e.g. `mini_railgun` vs the full `railgun`). When in doubt, prefer a single component plus a size-mount param over splitting.

Stat-binding requirement: an ability whose primary value should scale with the size mount must declare the matching `*_mult` binding in its `STAT_BINDINGS` and apply it in `recalculate()` (mirror `WeaponAbility` / `BeamWeaponAbility` / `WarheadAbility`). Without the binding, dropping `simple_size_mount` on the component has no effect on the ability's value.

Established by QA 2026-05-16 Obs 1 after `warhead_{small,medium,large}` and `laserhead_{small,medium,large}` were collapsed to single `warhead` / `laserhead` components in line with the earlier Round 3 bay / launch-bay consolidation. The originating preference (`feedback_one_component_per_role`) lives in the per-user Claude auto-memory store, not in the repo.

Example shape:

```json
{
  "id": "bridge",
  "name": "Bridge",
  "type": "Bridge",
  "mass": "=50 * sqrt(ship_class_mass / 1000)",
  "hp": "=200 * sqrt(ship_class_mass / 1000)",
  "allowed_vehicle_types": ["Ship"],
  "sprite_index": 4,
  "abilities": {
    "CommandAndControl": true,
    "RequiresMaintenance": "=ceil(5 * sqrt(ship_class_mass / 1000))"
  },
  "major_classification": "Crewsupport",
  "construction_cost": {
    "metals": 80,
    "organics": 20
  }
}
```

### Static Data Files

- `data/components.json`: component definitions.
- `data/modifiers.json`: component modifier definitions.
- `data/vehicleclasses.json`: vehicle class definitions.
- `data/resources.json`: unified resource catalog.
- `data/homeworld_presets.json`: homeworld presets.
- `data/race_names.json`: race name pools.
- `data/targeting_policies.json`: per-ship AI targeting rules.
- `data/movement_policies.json`: movement behavior presets.
- `data/group_policies.json`: group combat policy presets.
- `data/design_roles.json`: 27 design role definitions loaded by `RoleRegistry` through `game/strategy/data/design_role_registry.py::get_default_design_role_registry`; layered with `mods/*/design_roles.json` and `output/design_roles_overlay.json`.

### Starter Designs and Races

- Quickstart starter designs live in `data/designs/` and new starter files use the `qs_` prefix. Some legacy/non-QS design fixtures still exist; do not use them as a naming precedent.
- Required starter design fields include `name`, `ship_class`, `vehicle_type`, `design_role`, `layers`, `expected_stats`, and `_metadata`.
- Validate designs with `python Tools/validate_designs/validate_designs.py`.
- Add special design tests in `tests/unit/quickstart/test_quickstart_designs.py`.
- Starting complexes must be listed in `INITIAL_COMPLEXES` in `game/strategy/quickstart_builder.py`.
- Starter races live in `data/races/qs_*.json` and require `race_id`, `name`, `flag_id`, `portrait_id`, `theme_id`, homeworld/environment preferences, and aptitudes.
- Add starter race tests in `tests/unit/quickstart/test_quickstart_races.py`.
- User-created races save to `output/races/`.

Combat QS ship designs used for battle setup testing include:

- `qs_light_combat_escort.json`: escort with beam weapons and PDC (`fleet_escort`).
- `qs_heavy_cruiser.json`: cruiser with beams, railguns, shields, armor (`line_combatant`).
- `qs_missile_cruiser.json`: cruiser with seeker missiles and PDC (`missile_platform`).
- `qs_battleship.json`: battleship with heavy railguns, lasers, shields, armor (`line_combatant`).

### Simulation Test Data

Test-specific Combat Lab data lives in `combat_lab/data/`:

- `components.json`: test-only components.
- `ships/`: test ship definitions.
- `schemas/`: JSON schemas; verify against actual data before relying on them.

## Code Quality

### Type Hints and Docstrings

- Add type hints to all function signatures when touching code.
- Every public function/method requires a return type.
- Public APIs need docstrings.
- Trivial getters/setters and test functions usually do not need docstrings.
- Constructors and hot-path engine/controller methods should have full annotations.

#### mypy `--strict` coverage (PROJ-483 Phase 4)

The following Foundation layers are under `mypy --strict` per per-module
overrides in `mypy.ini`: `game.research.*`, `game.services.*`, `game.assets.*`,
`game.engine.*`, `game.ai.*`, `game.core.*`. New code in these layers must
type-check clean under strict mode. The heavier layers (`game.simulation`,
`game.strategy`, `game.ui`) remain non-strict pending a future dedicated
project — touching those layers does not require strict-clean status, but
prefer annotated signatures where practical.

### Function Shape

- Target functions under 50 LOC.
- Maximum nesting target is 3 levels.
- Prefer helpers and early returns to deeply nested logic.

### Preferred Decisions

- Root-cause refactor over quick fix.
- Named constants over magic numbers.
- Specific exceptions over broad catches.
- Dependency injection over singletons.
- Data-driven lookups over hardcoded type/class-name lists.
- Shared abstractions over copy-paste only when they remove real duplication or clarify ownership.
- Grouped feature-domain accessors over flat methods on large facade classes. New methods on a multi-domain facade land inside the appropriate group, not at the top level. Example: `StrategySessionFacade` (post-TD-08) exposes 2 top-level callables (`handle_command`, `process_turn`) plus 10 grouped namespace accessors (`commands`, `fleets`, `planets`, `systems`, `spatial`, `empires`, `events`, `session_meta`, `economy`, `validation`; `spatial` added by PROJ-477). New verbs land inside one of those groups.

### Error Handling

- Sub-engines validate preconditions before mutation via `_validate_tick_inputs()`.
- Serialization `from_dict()` methods propagate corrupt-data errors as `PersistenceException`.
- Strategy-layer `except Exception` must wrap and re-raise via `EnginePhaseError`, not return `None`.
- Any `except Exception` must carry `# Intentional broad catch: <reason>` on the same line.
- Design library uses `DesignLoadResult` objects for non-critical file loading.
- Full rules live in `docs/05_ERROR_HANDLING.md`.

### Capability validation is hard, not soft

When a design specifies a component that requires a capability the
ship/complex cannot provide, the validator MUST reject the design at
design-time rather than silently degrade runtime behaviour. Examples:

- `RequiresMaintenance` total > `ProvidesMaintenance` total — hard reject.
- A ship has `CrewCapacity` components but no `LifeSupportCapacity` —
  hard reject (crew without life support is invalid, not "crew that
  slowly suffocates").
- A weapon requires `CommandAndControl` (via `RequiresCommandAndControl`)
  but the design has none — hard reject.
- `RequiresCombatMovement` without combat propulsion — hard reject.

Validators live under `game/strategy/validation/` and
`game/simulation/validation/`; they raise `ValidationException` (or
return a failing `ValidationResult`) at the design-load /
design-edit boundary. Do not invent runtime degradation modes
("inoperative when over budget", "fires at half rate when crew is
short", etc.) — those are mode switches that hide configuration
bugs from the player. Bump capacities in the design, or rebalance,
or reject.

This matches the QA Round-2 observation captured in the
user-memory note `feedback_capability_missing_rejects_not_degrades.md`.

### No Hardcoded Type Lists

Do not hardcode lists of ability names, component types, or class names to control behavior. Prefer generic data inspection, registry metadata, shared properties, or protocols.

```python
# Wrong
_WEAPON_NAMES = ["BeamWeaponAbility", "ProjectileWeaponAbility", "SeekerWeaponAbility"]

# Right
for ab_data in abilities.values():
    if isinstance(ab_data, dict) and "firing_arc" in ab_data:
        ...
```

### System Migration

When replacing a system, delete the old one, update all call sites, and remove old data files. Do not add fallback paths or compatibility layers. Save files are disposable; do not write save migrations.

## Python Style and Type Annotations

### Python Style

- Module logger: `logger = logging.getLogger(__name__)`.
- Constants: `ALL_CAPS`.
- Classes: `PascalCase`.
- Functions, methods, and files: `snake_case`.
- Private members: single leading underscore.
- One substantial primary class per file.
- File names should match the primary class when applicable, for example `battle_engine.py` contains `BattleEngine`.

### Type Annotations

- Project baseline is Python 3.13+ (`pyproject.toml` declares `requires-python = ">=3.13"`). New/touched code uses modern syntax.
- Public functions and methods require return annotations.
- Use modern syntax on new/touched signatures: `int | None`, `list[int]`, `dict[str, T]`.
- Do not introduce legacy `Optional[int]`, `List[int]`, or `Dict[str, T]` in new code.
- Annotate no-return-value functions as `-> None`.
- `__init__` and other dunders are exempt.
- Use `from __future__ import annotations` or string annotations for forward references.
- Do not invent precision: if code returns `Any`, annotate `Any`.
- Parameter annotations are encouraged where they improve clarity.
- Prefer `Protocol` from `game.core.protocols.*` over concrete types when only duck-typed surface is needed.

## Documentation Freshness

Files under `docs/` must carry a timestamp directly below the H1:

```markdown
> **Last verified:** YYYY-MM-DD - <one-sentence summary>
```

Rules:

- Use ISO date format: `YYYY-MM-DD`.
- "Verified" means the maintainer confirmed the doc matches current code/behavior.
- Bump the date for substantive edits or real re-verification.
- Do not bump for cosmetic-only changes.

## Ship Theme Assets

### Canonical Theme Schema

Every `assets/Images/ShipThemes/<Theme>/` directory declares art through `theme.json`. Legacy flat image maps and hardcoded portrait filenames are retired.

```json
{
  "schema_version": 1,
  "name": "Federation",
  "description": "...",
  "image_sizes": {
    "skin": [2048, 2048],
    "portrait": [2048, 2048]
  },
  "assets": {
    "Battleship": {
      "skin": "Skins/battleship.png",
      "portrait": "Portraits/battleship.png",
      "scale": 1.0
    }
  }
}
```

Contracts:

- `schema_version: 1` is required.
- Unknown versions log a warning and the loader continues.
- `name` is shown in Race Setup.
- `description` is free-form and also feeds `Tools/regenerate_ship_portraits/` as theme-style context.
- `image_sizes.skin` and `image_sizes.portrait` are `[width, height]`; mismatches log warnings but do not reject assets.
- `assets` keys must exactly match the 19 display-form classes in `game.core.ship_classes.SHIP_CLASSES_WITH_VISUAL_THEMES`.
- `assets[<class>].skin` is required.
- `assets[<class>].portrait` is optional; missing portraits use the synthetic placeholder surface.
- `assets[<class>].scale` defaults to `1.0`.

### Ship Theme Image Rules

- Ship-theme assets are PNG only.
- Standard size is 2048x2048 square, exposed as `Paths.SHIP_THEMES_TARGET_SIZE`.
- Filenames must be `lowercase_with_underscores.png`.
- Skin and portrait basenames must match for each ship class, for example `Skins/battle_cruiser.png` and `Portraits/battle_cruiser.png`.

### Adding a Theme

1. Create `assets/Images/ShipThemes/<NewTheme>/Skins/` and `assets/Images/ShipThemes/<NewTheme>/Portraits/`.
2. Add 19 lowercase PNG skins, one per canonical ship class.
3. Optionally add 19 portraits with matching basenames, or run `python -m Tools.regenerate_ship_portraits.cli --theme <NewTheme>`.
4. Author `theme.json`.
5. Audit with `python -m Tools.regenerate_ship_portraits.audit --theme <NewTheme>`.
6. Run `pytest tests/integration/ui/test_race_setup_ships_smoke.py`.

## Git Branch Conventions

### Standard Prefixes

- `feature/`: feature work.
- `cleanup/`: cleanup/refactor.
- `claude/`, `codex/`, `copilot/`: per-agent branches.
- `worktree-agent-*`: legacy auto-named worktree branches; do not adopt for new work.

### Phase-Aware Project Branches

- `proj/{PROJ-ID}/main`: project trunk; carries plan and code from execution start to final merge.
- `proj/{PROJ-ID}/{phase-id}`: one branch per phase, for example `proj/PROJ-300/phase_1`.
- `tmp/{PROJ-ID}/integrate-{phase-id}-{shortsha}`: ephemeral integration branch for sibling-aware testing.

The `/main` suffix is required because Git refs cannot simultaneously have `proj/{PROJ-ID}` as a file-like branch and `proj/{PROJ-ID}/{phase}` as child branches under the same namespace.

Worktree paths:

- `.worktrees/phases/{PROJ-ID}/{phase-id}/`
- `.worktrees/integration/{PROJ-ID}-{phase-id}-{shortsha}/`
- `AgentCoordination/opencodereview/local/worktrees/{request-id}/`
