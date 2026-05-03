# Conventions

> **Last verified:** 2026-05-03 — Added §11 Git Branch Conventions for 03c phase-aware execution (`proj/{PROJ-ID}/main`, `proj/{PROJ-ID}/{phase-id}`, `tmp/{PROJ-ID}/integrate-...`). §10 Ship Theme Asset Conventions (PROJ-314) unchanged.

This document defines the naming, coding, file organization, and testing conventions for Starship Battles. Follow these rules when adding or modifying code.

---

## 1. Naming Conventions

### 1.1 Battle vs Combat

These terms are **not interchangeable**. They indicate scope.

| Term | Scope | Examples |
|------|-------|----------|
| **Battle** | Simulation orchestration: full engagements, state, resolution | `BattleEngine`, `BattleService`, `BattleController`, `BattleState`, `BattleResult` |
| **Combat** | Entity-level behavior: per-ship, per-tick mechanics | `ShipCombatEngine`, `CombatPropulsion`, `CombatConstants` |

**Rule:** Creating a system that manages the overall engagement? Use **Battle**. Adding per-ship or per-component behavior? Use **Combat**.

### 1.2 Screen vs Scene

Major game states use **Screen**. Minor/modal states use **Scene**.

| Suffix | Usage | Actual classes |
|--------|-------|----------------|
| **Screen** | Major game states: battle, strategy, workshop, setup | `BattleScreen`, `StrategyScreen`, `DesignWorkshopScreen`, `BuildQueueScreen`, `FleetBattleSetupScreen` (aliased as `BattleSetupScreen` in app.py), `TestLabScreen`, `NewGameSetupScreen`, `RaceSetupScreen`, `GalaxyTestScreen` |
| **Scene** | Minor overlays: menus, settings | `MenuScene`, `KeybindingsScene` |

- **DO:** Name new major game states with `Screen`.
- **DON'T:** Use `Scene` for anything that occupies the full display as a primary game state.
- **DON'T:** Use `BattleScene` or `StrategyScene` -- these do not exist.

### 1.3 Builder vs Workshop

| Term | Layer | Location |
|------|-------|----------|
| **Builder** | Internal panels (reusable UI components) | `game/ui/screens/builder/` |
| **Workshop** | Top-level screen that composes Builder panels | `game/ui/screens/workshop_*.py` |

Builder panels live in `game/ui/screens/builder/` (e.g., `left_panel.py`, `right_panel.py`, `schematic_view.py`, `detail_panel.py`, `weapons_panel.py`).

Workshop files live directly in `game/ui/screens/` (**not** a `workshop/` subdirectory): `workshop_screen.py` (class: `DesignWorkshopScreen`), `workshop_viewmodel.py`, `workshop_context.py`, `workshop_event_router.py`, `workshop_data_loader.py`, `workshop_data_reloader.py`, `workshop_ship_io.py`.

### 1.4 Star System vs Sector

These terms describe **different spatial granularities** on the galaxy hex map. They are not interchangeable.

| Term | Scope | Data Type | Examples |
|------|-------|-----------|----------|
| **Star system** | A circular region of the galaxy map (radius 50 hexes / 101 hexes across) centered on a star, containing all planets, warp points, and storms within its boundary | `StarSystem` | `galaxy.get_system_at_location()`, `system.name`, `system.global_location` |
| **Sector** | A single hex coordinate on the galaxy map — the smallest addressable location | `HexCoord` | `fleet.location`, `warp_point.location`, `planet.location` |

**Star system spatial properties:**
- **Center:** `system.global_location` — the origin hex in global galaxy coordinates.
- **Boundary:** Circular, radius 50 hexes from center. Defined by `get_system_at_hex()` in `game/strategy/data/pathfinding.py` (`radius=50`). Any sector within 50 hexes of a system center belongs to that system.
- **Separation:** Systems are placed at least 400 hexes apart (center to center), ensuring no overlap.
- **Contents:** Stars (with their own `radius_hexes` for multi-hex visual footprint), planets (at orbital distances up to ~20 hexes), warp points, and storms — each at a specific sector within the system.
- **Coordinate duality:** Entities within a system store **local** coordinates (offset from system center). Convert to global: `global_hex = system.global_location + entity.location`.

**Key distinctions:**
- A system contains **many sectors**. A star system's hexes include the central star, orbiting planets, and warp points — each at a different sector (hex).
- A system can have **multiple warp points in different sectors**. Validating "fleet is in the right system" is not sufficient when targeting a specific warp point — you must validate the fleet is in the correct **sector**.
- `fleet.location` is always a **sector** (specific hex). `system.global_location` is the system's **origin sector** (center hex).
- When an order targets a specific location (warp point, planet), store the **sector** (`HexCoord`) for execution-time validation, not just the system name.

**Rule:** Use **star system** (or just **system**) when referring to the entire region (e.g., "fleet is in the Alpha system"). Use **sector** when referring to a specific hex coordinate (e.g., "fleet is at the warp point's sector"). When validating fleet position for an order, always validate at **sector** precision.

### 1.5 Handler Naming

Input handlers are prefixed with their screen/context name:

| Class | File |
|-------|------|
| `StrategyInputHandler` | `game/ui/screens/strategy_input_handler.py` |
| `TestLabInputHandler` | `game/ui/screens/test_lab/test_lab_input_handler.py` |
| `WeaponsInputHandler` | `game/ui/screens/builder/weapons_input_handler.py` |

- **DON'T:** Reference `InputHandler` at `game/core/input_handler.py` -- it does not exist.
- **DO:** The core layer has `input_actions.py` (`game/core/input_actions.py`), not an input handler.

### 1.6 MVVM Pattern Files

Complex screens use Model-View-ViewModel:

| Suffix | Purpose | Example |
|--------|---------|---------|
| `*_viewmodel.py` | Screen state, events, business logic (no Pygame) | `workshop_viewmodel.py`, `build_queue_viewmodel.py` |
| `*_context.py` | Shared data context between panels | `workshop_context.py` |
| `*_event_router.py` | Event dispatch between UI components | `workshop_event_router.py`, `strategy_event_router.py` |
| `*_data_loader.py` | Data loading coordination | `workshop_data_loader.py` |

### 1.7 Ability Module Names

All ability modules live in `game/simulation/components/abilities/`:

```
__init__.py       # Registry and public exports
base.py           # Ability base class
cargo.py          # CargoStorage
colonize.py       # ColonizePlanet
crew.py           # CrewCapacity, LifeSupportCapacity, CrewRequired
defense.py        # ShieldProjection, ShieldRegeneration, EmissiveArmor, ToHit*Modifier
harvester.py      # ResourceHarvesterAbility, SpaceShipyardAbility, LocalStorageAbility
markers.py        # VehicleLaunchAbility, CommandAndControl, StructuralIntegrity
propulsion.py     # CombatPropulsion, ManeuveringThruster, StrategicMovement, WarpJump
resources.py      # ResourceConsumption, ResourceStorage, ResourceGeneration (component abilities; see also game/core/resources.py for ResourceCatalog)
stat_keys.py      # StatKey, AbilityStatBinding
planetary.py      # PlanetaryShieldAbility, StrategicResourceGenerationAbility (PROJ-237/238)
superweapons.py   # DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, etc.
ui_colors.py      # HINT_SHIELD_CAP, HINT_DAMAGE, etc. (UI hint color constants)
weapons.py        # WeaponAbility, BeamWeaponAbility, etc.
```

- **DO:** Import abilities from the package, not individual files:
  ```python
  from game.simulation.components.abilities import CombatPropulsion, WeaponAbility
  ```

### 1.8 Order System Names (PROJ-238)

`FleetOrder` was renamed to `Order` to support both fleet and planet orders.
`PlanetOrderType` was merged into the unified `OrderType` enum.

| Old Name | New Name | Notes |
|----------|----------|-------|
| `FleetOrder` | `Order` | `from game.strategy.data.order_types import Order` |
| `PlanetOrderType` | merged into `OrderType` | `ACTIVATE_ABILITY`, `DEACTIVATE_ABILITY` added (generic ability toggles) |
| `FleetOrderProcessor` | `OrderProcessor` | Old module deleted; import from `order_processor.py` |
| `FleetOrderSerializer` | `OrderSerializer` | Old module deleted; import from `order_serializer.py` |
| `FleetOrdersWindow` | `OrdersWindow` | Old module deleted; import from `orders_window.py` |

Old backward compatibility alias modules have been deleted. All code must use
the new names and import paths directly.

---

## 2. File Organization

### 2.1 Layer Structure

| Layer | Path | Dependencies |
|-------|------|-------------|
| **Core** | `game/core/` | None (foundation layer) |
| **Services** | `game/services/` | Core only |
| **Assets** | `game/assets/` | Core, Services |
| **Engine** | `game/engine/` | Core, Services (spatial, collision utilities) |
| **Simulation** | `game/simulation/` | Core, Services, Engine (no UI, no Pygame) |
| **Research** | `game/research/` | Core, Services |
| **Strategy** | `game/strategy/` | Core, Services, Engine, Simulation |
| **AI** | `game/ai/` | Core, Services, Engine, Simulation |
| **UI** | `game/ui/` | All layers (top-level) |

- **DO:** Respect dependency direction. Simulation must never import from UI.
- **DON'T:** Import Pygame in simulation or strategy code.

### 2.2 Where New Files Go

| You are adding... | Put it in... |
|-------------------|-------------|
| A new ship ability | `game/simulation/components/abilities/` (new file or extend existing) |
| A new component modifier | `game/simulation/components/` |
| A new battle system | `game/simulation/systems/` |
| A new strategy system | `game/strategy/systems/` |
| A new UI screen | `game/ui/screens/` |
| A new builder panel | `game/ui/screens/builder/` |
| JSON game data | `data/` (root level) |
| Starter ship/complex designs | `data/designs/` (`qs_*.json`) |
| Starter race configurations | `data/races/` (`qs_*.json`) |

### 2.3 File Size

Production-source files under `game/` should remain **below 500 lines**. When a file approaches or crosses 500 LOC, that's a signal it has accreted multiple responsibilities and needs to be split.

**Current baseline:** historical production files already exceed this limit.
Do not use that as precedent for new work. When touching an over-limit file,
prefer extracting the changed responsibility into a cohesive helper/module or
creating a follow-up cleanup ticket if the requested change cannot safely
absorb the refactor.

**When a file crosses 500 LOC:**

1. **Diagnose:** Has the file accreted multiple responsibilities? Almost always yes once it crosses this threshold.
2. **Split:** Extract cohesive sub-modules. The split direction depends on the file — by render layer, by domain, by concern, etc. Avoid arbitrary "first half / second half" splits — each sub-module should have one reason to change.
3. **Preserve API:** Use a re-export shim (the original module re-exports from the new sub-modules) when many callers exist; full caller migration when few. The choice is per-file.

**Subpackage vs flat:** Use a subpackage (directory with `__init__.py`) when there are 3+ closely related files that form a logical unit (e.g., `builder/`, `battle_controller/`). Keep it flat when files are loosely related.

**Test files are exempt.** Long test files (under `tests/`, `combat_lab/`, etc.) are often legitimate — do not apply the 500-line rule to them.

See PROJ-309 for the audit that established this rule and the decomposition of the original top-10 files.

### 2.4 UI Screen Line Budget (PROJ-282)

UI screen classes (anything implementing `IScene`) should stay **under 300 lines**.

Several existing UI screen modules are above this soft limit. Treat them as
decomposition candidates: new UI behavior should go into controller,
view-model, renderer, input-handler, or data-source collaborators rather than
growing the screen class further.

Logic for mutation, derived view state, rendering, and event handling should
live in sibling delegate classes following the **MVVM pattern** established by
`TestLabScreen` ([game/ui/screens/test_lab/](../game/ui/screens/test_lab/)) and
`FleetBattleSetupScreen` ([game/ui/screens/battle_setup/](../game/ui/screens/battle_setup/)) post-PROJ-282:

- **Controller** — mutations on the data model, save/load, lifecycle, battle launch
- **ViewModel** — selection + derived view state (pure data, no pygame imports)
- **Renderer** — pygame_gui element construction (often split into per-panel builders)
- **InputHandler** — pygame_gui event dispatch (button/dropdown → controller calls)
- **Helpers** — domain-specific sub-services (e.g. `FleetHierarchyEditor` for TF/SQ CRUD)

If you find yourself adding a method to a screen class that is over 300 lines,
stop and identify which delegate it belongs in.

Sibling delegate classes should also aim for ≤300 lines. A Controller over 300
lines is a review signal — not a blocker — that the mutation surface may
warrant a sub-service extraction. Concentrated single-responsibility code (e.g.
a controller with 15+ mutation methods + save/load + battle launch) can legitimately
exceed 300; the rule exists to make rebloat visible, not to enforce a brittle cap.

**This is a soft limit.** The goal is to give reviewers grounds to push back on
drift. When a file grows past 300 lines, expect to justify why — not to pass
a gate.

---

## 3. Import Conventions

Imports follow a three-group ordering, separated by blank lines:

```python
# 1. Standard library
import logging
import os
from typing import List, Optional, TYPE_CHECKING

# 2. Third-party
import pygame

# 3. Game modules
from game.core.math import Vector2
from game.core.config import PhysicsConfig, BattleTuning
from game.simulation.entities.ship import Ship
```

Additional rules:
- **DO:** Use `from __future__ import annotations` when needed for forward references.
- **DO:** Use `TYPE_CHECKING` blocks for imports only needed by type checkers:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from game.core.registry import GameRegistries
  ```
- **DON'T:** Use wildcard imports (`from module import *`).
- **DO:** Import abilities from the abilities package, not from individual submodules.

### 3.1 File Path Convention (PROJ-256)

All file/directory paths in production code must use constants from `game.core.paths.Paths`. Never hardcode paths like `"data/components.json"` or `os.path.join("assets", "ShipThemes", ...)`.

```python
# WRONG
path = os.path.join(os.getcwd(), "data", "components.json")
path = os.path.join("assets", "ShipThemes", theme, "Portraits", filename)

# RIGHT
from game.core.paths import Paths
path = Paths.COMPONENTS_FILE
path = os.path.join(Paths.SHIP_THEMES_DIR, theme, "Portraits", filename)
```

For functions with path defaults, use `None` with body resolution:
```python
def load_data(file_path=None):
    if file_path is None:
        file_path = Paths.COMPONENTS_FILE
```

**Exceptions:** Test files may use relative paths to test-specific data directories. Scripts with CLI `--output` arguments are also exempt.

### 3.2 Image Asset Format Convention

**All image assets must use PNG format.** This is the standard for the project going forward.

- **New assets:** Must be `.png`. Do not introduce new `.jpg`, `.jpeg`, or `.webp` files.
- **Existing `.jpg` files:** Should be transitioned to `.png` when touched or as part of asset work. Do not convert them all at once — migrate them when working in the area.
- **Code that loads images:** Should accept `.png` as the primary format. Filter conditions that accept multiple formats (e.g., `.endswith(('.png', '.jpg'))`) are acceptable for backward compatibility during the transition, but new code should construct filenames with `.png`.

**Component images** follow a resolution-based directory structure under `assets/Images/Components/`:

| Directory | Resolution | Filename pattern | Usage |
|-----------|-----------|-----------------|-------|
| `Components 64/` | 64x64 | `64Portrait_Comp_{NNN}.png` | SpriteManager tile grid |
| `Components 128/` | 128x128 | `128Portrait_Comp_{NNN}.png` | Small icons |
| `Components 256/` | 256x256 | `256Portrait_Comp_{NNN}.png` | Medium thumbnails |
| `Components 512/` | 512x512 | `512Portrait_Comp_{NNN}.png` | Large thumbnails |
| `Components 1024/` | 1024x1024 | `1024Portrait_Comp_{NNN}.png` | High-res display |
| `Components 2048/` | 2048x2048 | `2048Portrait_Comp_{NNN}.png` | Detail panel portraits |

The filename prefix matches the actual resolution of the images in that directory. Use `Paths.COMPONENTS_64_DIR` through `Paths.COMPONENTS_2048_DIR` for path constants.

`Components 1024/` is the tracked source-of-truth set. The `2048`, `512`, `256`, `128`, and `64` directories are generated derivatives and must not be committed. Runtime startup calls `game.assets.component_derivatives.ensure_component_derivatives()` before component sprites load; it creates missing derivatives and refreshes stale derivatives when a 1024 source hash changes. The hash manifest lives at `assets/Images/Components/.component_derivatives_manifest.json` and is intentionally ignored.

---

## 4. Test Conventions

### 4.1 Directory Mirroring

Test files mirror the source structure:

| Source | Test |
|--------|------|
| `game/simulation/systems/battle_engine.py` | `tests/unit/simulation/systems/` |
| `game/ui/screens/strategy_screen.py` | `tests/unit/ui/screens/test_strategy_screen.py` |
| `game/simulation/components/abilities/defense.py` | `tests/unit/simulation/components/abilities/` |

Test file names: `test_<source_file_name>.py`

### 4.2 conftest.py Hierarchy

The project uses a layered conftest structure:

| File | Scope | Provides |
|------|-------|----------|
| `tests/conftest.py` | Root | `session_registries`, `fresh_registries`, `minimal_registries`, `mock_registries`, `ship_factory`, global ship data loading |
| `tests/unit/conftest.py` | Unit tests | Unit-specific fixtures |
| `tests/unit/<layer>/conftest.py` | Per-layer | Layer-specific fixtures (e.g., `tests/unit/combat/conftest.py`) |
| `tests/integration/<domain>/conftest.py` | Per-domain | Integration scenario fixtures |

- **DO:** Put shared fixtures in the nearest common ancestor conftest.
- **DON'T:** Duplicate fixtures across conftest files.

### 4.3 Fixture Naming

Standard fixture names from root conftest:

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `session_registries` | session | Loaded once, shared across all tests (read-only) |
| `fresh_registries` | function | Deep copy per test for isolation |
| `minimal_registries` | function | Empty registries for pure unit tests |
| `mock_registries` | function | Minimal registries with mock data |
| `ship_factory` | function | Helper to create ships from fresh registries |

### 4.4 Test Commands

```bash
pytest tests/ --testmon              # Incremental (fast, runs only affected tests)
pytest tests/path/to/test.py         # Targeted single file
python Tools/test_sharded/test_sharded.py        # Full suite with sharded parallel runner
pytest tests/ --cov=game -n 12       # Full suite with coverage
```

---

## 5. JSON Data Conventions

### 5.1 Component Data (`data/components.json`)

Components are defined in a top-level `"components"` array. Each entry has:

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
        "CrewRequired": "=ceil(5 * sqrt(ship_class_mass / 1000))"
    },
    "major_classification": "Crewsupport",
    "construction_cost": {
        "metals": 80,
        "organics": 20
    }
}
```

Key rules:
- `id` is the unique component identifier (snake_case).
- `mass` and `hp` can be formulas (prefixed with `=`) or plain numbers.
- `abilities` maps ability class names to `true`, a number, or `{"value": N}` format.
- `allowed_vehicle_types` restricts which vehicle types can equip the component.

### 5.2 Static Game Data

| File | Contents |
|------|----------|
| `data/homeworld_presets.json` | Homeworld planet configuration presets |
| `data/race_names.json` | Generated race name pools |
| `data/components.json` | All component definitions |
| `data/targeting_policies.json` | Targeting rule sets for per-ship AI (standard, sniper, brawler, anti_fighter, self_defense) |
| `data/movement_policies.json` | Movement behavior presets for per-ship AI (kite_max, brawl_close, strafe_run, etc.) |
| `data/group_policies.json` | Group-level combat policy presets (targeting, movement, retreat — 21 presets for fleet hierarchy) |
| `data/design_roles.json` | Design role definitions (27 roles) with vehicle type restrictions — loaded by `RoleRegistry` via `game/strategy/data/design_role_registry.py::get_default_design_role_registry` (PROJ-278). Layered: base + `mods/*/design_roles.json` + `output/design_roles_overlay.json` |

### 5.3 Starter Designs and Races

Starter designs (`data/designs/`) and starter races (`data/races/`) are shipped game data used by both quickstart and normal new games. All files use the `qs_` prefix.

**Adding a new starter design:**
1. Create `data/designs/qs_<name>.json` with required fields: `name`, `ship_class`, `vehicle_type`, `design_role`, `layers`, `expected_stats`, `_metadata`
2. Run `python Tools/validate_designs/validate_designs.py` to validate
3. Add tests in `tests/unit/quickstart/test_quickstart_designs.py` if the design has special requirements
4. If the design is a starting complex (auto-built on homeworld), add its design_id to `INITIAL_COMPLEXES` in `game/strategy/quickstart_builder.py`

**Combat QS ship designs** (for battle setup testing):
- `qs_light_combat_escort.json` — Escort with beam weapons and PDC (fleet_escort)
- `qs_heavy_cruiser.json` — Cruiser with beams, railguns, shields, armor (line_combatant)
- `qs_missile_cruiser.json` — Cruiser with 6 seeker missiles and PDC (missile_platform)
- `qs_battleship.json` — Battleship with heavy railguns, lasers, shields, armor (line_combatant)

**Adding a new starter race:**
1. Create `data/races/qs_<name>.json` with required fields: `race_id`, `name`, `flag_id`, `portrait_id`, `theme_id`, homeworld/environment preferences, and aptitudes
2. Add tests in `tests/unit/quickstart/test_quickstart_races.py`

**Note:** `data/races/` holds shipped starter races. User-created races are saved to `output/races/`.

### 5.4 Simulation Test Data

Test-specific data lives in `combat_lab/data/`:
- `components.json` -- Test-only components (e.g., `TestS_2L` class ships)
- `ships/` -- Test ship JSON definitions
- `schemas/` -- JSON schemas (may be outdated; verify against actual data before use)

---

## 6. Code Quality Rules

### 6.1 Type Hints and Docstrings

- **DO:** Add type hints to all function signatures.
- **DO:** Add docstrings to public APIs.
- **DON'T:** Add docstrings to trivial getters/setters or test functions.
- **PRIORITY (PROJ-255):** Constructors and hot-path methods in engine/controller code must have full annotations. Use `TYPE_CHECKING` imports to avoid circular dependencies.

### 6.2 Function Size and Nesting

- **Target:** Functions under 50 lines.
- **Maximum nesting:** 3 levels. Extract helper functions or use early returns to flatten.

### 6.3 Preferred Patterns

| Prefer | Over |
|--------|------|
| Proper refactor | Quick fix |
| Root cause fix | Workaround |
| Named constants | Magic numbers |
| Specific exceptions | Broad `except` catches |
| Dependency injection | Singletons |
| Extract abstraction | Copy-paste |
| Clean-sheet design | Design compromise |
| Data-driven lookups | Hardcoded type/class name lists |

### 6.4 Error Handling Conventions (PROJ-251)

- **Sub-engines must validate preconditions** before mutating state via `_validate_tick_inputs()`
- **Serialization `from_dict()` methods propagate errors**, not swallow them — corrupt data raises `PersistenceException`
- **`except Exception` in strategy layer** must wrap and re-raise via `EnginePhaseError`, not return `None`
- **Design library** uses `DesignLoadResult` result objects for non-critical file loading (not exceptions)

See `docs/05_ERROR_HANDLING.md` for the full error handling reference.

### 6.5 No Hardcoded Type Lists

**Never hardcode lists of ability names, component types, or class names** to control behavior. Instead, search data structures generically or use registry lookups.

```python
# WRONG — breaks when a new weapon type is added:
_WEAPON_NAMES = ['BeamWeaponAbility', 'ProjectileWeaponAbility', 'SeekerWeaponAbility']
for name in _WEAPON_NAMES:
    if name in abilities: ...

# RIGHT — searches all abilities for the relevant property:
for ab_data in abilities.values():
    if isinstance(ab_data, dict) and 'firing_arc' in ab_data: ...
```

If code needs to distinguish types, use a shared property or protocol — not a list of class name strings.

### 6.5 System Migration

When a new system replaces an old one, **eradicate the old system completely**. Delete old code, update all call sites, remove old data files. No fallback paths, no backward compatibility layers. Save files are disposable -- never write migration code for save data.

---

## 7. Python Style

- **Logging:** `logger = logging.getLogger(__name__)` at module level.
- **Constants:** `ALL_CAPS` for module-level constants.
- **Classes:** `PascalCase`. One primary class per file when the class is substantial.
- **Functions/methods:** `snake_case`.
- **Private members:** Single underscore prefix (`_private_method`).
- **File names:** `snake_case`, matching the primary class (`battle_engine.py` contains `BattleEngine`).

---

## 8. Type Annotations

### Return types (required)
Every public function/method must carry a return-type annotation.

- **Modern syntax for new or touched signatures:** `int | None`, `list[int]`, `dict[str, T]` — not `Optional[int]`/`List[int]`/`Dict[str, T]`. Python 3.13+ baseline (PROJ-295) means new code does not need legacy syntax. Existing legacy annotations remain cleanup backlog; do not expand them when editing a file.
- **No `return` statement:** annotate `-> None` explicitly
- **`__init__` and other dunders:** exempt per PEP 484
- **Forward references:** add `from __future__ import annotations` at the top of the file if needed (or use string literals in the annotation)
- **Don't lie:** if the function returns `Any`, annotate `Any`. Don't make up a more specific type the code doesn't enforce

### Parameter types (encouraged)
Parameter annotations are encouraged but not project-wide-mandatory yet. Add them where they improve clarity.

### Generics and protocols
Prefer `Protocol` (from `game.core.protocols.*`) over concrete types when the function only needs duck-typed surface. Use `TypeVar` for generic helpers.

See PROJ-311 for the audit that established the return-type requirement.

---

## 9. Documentation Freshness

Every file under `docs/` must carry a verification timestamp directly below its H1:

> **Last verified:** YYYY-MM-DD — <one-sentence summary of what was verified>

Rules:
- **Date format:** `YYYY-MM-DD` (ISO 8601)
- **"Verified" means:** the maintainer read the file and confirmed it matches current code/behavior — not that they made a cosmetic edit
- **Bump the date when:** you substantively edit the doc, or you re-read it and confirm current accuracy
- **Don't bump:** for typo/formatting fixes that don't reflect any verification work

See PROJ-307 for the backfill that established this convention.

---

## 10. Ship Theme Asset Conventions (PROJ-314)

Every ship-theme directory under `assets/ShipThemes/<Theme>/` must
declare its skin and portrait art via a single `theme.json` file in the
canonical schema below. The legacy `images:` schema (flat
`{class: path}` map) and the hardcoded `<Class>_Portrait.jpg` filename
convention have both been retired.

### 10.1 Canonical `theme.json` schema

```json
{
  "schema_version": 1,
  "name": "Federation",
  "description": "...",
  "image_sizes": {
    "skin":     [2048, 2048],
    "portrait": [2048, 2048]
  },
  "assets": {
    "Battleship": {
      "skin":     "Skins/battleship.png",
      "portrait": "Portraits/battleship.png",
      "scale":    1.0
    }
  }
}
```

- `schema_version: 1` is required. Unknown versions log a warning and
  the loader continues (forward compatibility).
- `name` is the human-readable theme name shown in Race Setup.
- `description` is a free-form string, also fed to the AI portrait-
  regenerator (`Tools/regenerate_ship_portraits/`) as theme-style
  context for `gpt-image-2`.
- `image_sizes.skin` and `image_sizes.portrait` are `[width, height]`
  arrays. The loader compares declared vs. actual via PIL and logs a
  warning on mismatch (it does NOT reject the asset).
- `assets` keys MUST exactly match
  `game.core.ship_classes.SHIP_CLASSES_WITH_VISUAL_THEMES` (display
  form: `"Light Cruiser"`, `"Fighter (Medium)"`, etc.). Extras log a
  warning, missing entries log info.
- `assets[<class>].skin` is required.
- `assets[<class>].portrait` is OPTIONAL. When absent or pointing at a
  missing file, `ShipThemeManager.get_portrait_image()` returns the
  synthetic placeholder Surface (consistent with `load_image()`).
- `assets[<class>].scale` defaults to `1.0`.

### 10.2 Image format and resolution

- All ship-theme assets are PNG only (per §5 / `docs/03_CONVENTIONS.md`
  §285–288). JPG is not supported.
- Standard resolution is **2048×2048 square**, exposed as
  `Paths.SHIP_THEMES_TARGET_SIZE` (PROJ-314 Phase 1).

### 10.3 Filename rules

- Filenames MUST be `lowercase_with_underscores.png`.
- Skin and portrait basenames MUST match per ship class (e.g.
  `Skins/battle_cruiser.png` and `Portraits/battle_cruiser.png`). This
  removes the cross-platform case-sensitivity hazard that broke Linux
  CI on mixed-case Federation/Klingons/Romulans/Atlantians filenames
  prior to PROJ-314.

### 10.4 Adding a new theme

1. Create `assets/ShipThemes/<NewTheme>/`,
   `<NewTheme>/Skins/`, `<NewTheme>/Portraits/`.
2. Place 19 lowercase_with_underscores `.png` skins (one per canonical
   ship class).
3. Optionally place 19 portraits with the same basenames; or run the
   regenerator CLI:

   ```sh
   python -m Tools.regenerate_ship_portraits.cli --theme <NewTheme>
   ```

4. Author `theme.json` in the canonical schema above.
5. Run `python -m Tools.regenerate_ship_portraits.audit
   --theme <NewTheme>` to verify there are no coverage / casing / size
   gaps.
6. Run the integration smoke test:
   `pytest tests/integration/ui/test_race_setup_ships_smoke.py`.

Established by PROJ-314.

---

## 11. Git Branch Conventions

### 11.1 Standard branch prefixes

| Prefix | Purpose | Example |
|---|---|---|
| `feature/` | Feature development | `feature/dynamic-screen-resize` |
| `cleanup/` | Cleanup / refactor | `cleanup/remove-unused-types` |
| `claude/`, `codex/`, `copilot/` | Per-agent feature branches | `claude/snapshot-cache-fix` |
| `worktree-agent-*` | Auto-named worktree branches (legacy) | (do not adopt for new work) |

### 11.2 03c phase-aware execution branches

Per [Projects/protocols/03c_phase_aware_execution.md](../Projects/protocols/03c_phase_aware_execution.md):

| Branch pattern | Purpose | Lifetime |
|---|---|---|
| `proj/{PROJ-ID}/main` | Project trunk; carries plan + code from execution start to final merge | Created at first `claude-proj-continue`; merged to `main` at project completion. |
| `proj/{PROJ-ID}/{phase-id}` | Phase branch; one per phase (e.g. `proj/PROJ-300/phase_1`) | Created by `spawn_phase_worker.py`; merged into `proj/{PROJ-ID}/main` via temp-integration. |
| `tmp/{PROJ-ID}/integrate-{phase-id}-{shortsha}` | Ephemeral integration branch for sibling-aware testing | Created and deleted within `phase_complete.py`. |

**Rationale for `/main` suffix on the project trunk.** Git refs cannot
have both `proj/{PROJ-ID}` (a file at `refs/heads/proj/{PROJ-ID}`) and
`proj/{PROJ-ID}/{phase}` (a directory under `refs/heads/proj/{PROJ-ID}/`).
Adding the `/main` segment puts the trunk inside the same namespace as
the phase branches, so all live alongside each other.

Worktree paths follow the same shape, gitignored:

| Worktree path | Owner |
|---|---|
| `.worktrees/phases/{PROJ-ID}/{phase-id}/` | Phase worker |
| `.worktrees/integration/{PROJ-ID}-{phase-id}-{shortsha}/` | `phase_complete.py` (ephemeral) |
| `AgentCoordination/opencodereview/local/worktrees/{request-id}/` | Daemon (ephemeral, SHA-pinned) |

Established by 03c (2026-05-03).
