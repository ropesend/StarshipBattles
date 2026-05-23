# PROJ-474: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source / gating
Deferred tail of **PROJ-472** (closed the StrategySessionFacade read-path gap).
The gate ("PROJ-472's two read-path guards must land first") is **CLEARED**:
`tests/static_guards/test_facade_read_path_imports_guard.py` +
`test_facade_read_path_session_guard.py` exist and are green (verified
2026-05-22, 340 passed in the import guard). See PROJ-472 `decisions.md` (the
policy=option-(b) decision and the "UISAFE must not drift" decision) and the
pre-flesh consult at
`AgentCoordination/Scratchpad/Consult/proj474_preflesh/advice.md`.

## The problem precisely
PROJ-472 documented the UI-safe surface (Pattern #5) and parked the types in a
`UISAFE`-commented block of the flat import allowlist. But:

1. `UISAFE` is a **comment**, not data. Nothing prevents a UI-safe symbol being
   dumped in `TAIL`, or a live symbol sneaking into `UISAFE`.
2. The flat structure has **already drifted** (all verified live 2026-05-22):
   - `VALID_GALAXY_TYPES`: UISAFE for `new_game_setup_screen.py`
     (`...imports_guard.py:95`), TAIL for `galaxy_test/galaxy_mode.py` (`:154`).
   - `RaceConfig`/`RacePointBudget`: named UI-safe in Pattern #5
     (`docs/02_PATTERNS.md:188-195`) but allowlisted in TAIL
     (`...imports_guard.py:181-182,188-191`).
   - `ComponentActivationState`: in the UISAFE block (`...imports_guard.py:104`)
     but absent from the Pattern #5 list (`docs/02_PATTERNS.md:190-193`).

## Membership criteria (the testable definition)
An imported `game.strategy.*` member belongs to the **UI-safe read surface** iff
ALL of:

1. It is usable **before a `GameSession` exists**, or against detached
   config/value objects not owned by a live session.
2. The runtime operations the UI uses do **not** require or return live strategy
   graph objects or session-bound services (`GameSession`, `Galaxy`, `Empire`,
   `Fleet`, `Planet`, `StarSystem`, `Facility`, `DesignCatalog`, save/replay
   services).
3. It is one of: an **enum / constant / frozen-or-static metadata table**; a
   **detached config/value type** whose fields are scalars or other detached
   value objects; or a **static-data loader/query/applicator** that touches only
   repo data + detached config/value objects.
4. It exposes **no** live owner references, mutable queue lists, session caches,
   or traversal helpers.

**Sharp edge:** a helper is NOT UI-safe just because it is pure. If it *takes* a
live domain object it is out: `calculate_habitability(planet, race_config)`
(`game/strategy/formulas/habitability.py:48-84`),
`project_fleet_position(fleet)` (`game/strategy/services/cargo_transfer_service.py:23-42`),
`SectorEnvironment(local_hex, system)` (`game/strategy/data/physics.py:22-36`).
Detached-config *mutation* is allowed (e.g. `apply_preset_to_config(...)` on a
standalone `RaceConfig` — already blessed by Pattern #5).

## Structure decision: symbol-level data, NOT module prefixes
Chosen (consult §2 option (a), refined):

- Add `_UISAFE_SYMBOLS: frozenset[tuple[str, str]]` of `(module, member)`.
- The matcher allows an import if: it is the always-allowed facade/commands path
  **OR** `(module, member) ∈ _UISAFE_SYMBOLS` **OR** the exact
  `(file, module, member)` is in the transitional file-scoped allowlist
  (`CLUSTER`/`FLEETCAP`/`TAIL`).
- Add a **parity test**: `_UISAFE_SYMBOLS` must equal a parseable canonical
  `module.member` token list embedded in Pattern #5 (a fenced block of one token
  per line — NOT scraped prose, to avoid brittleness).
- Add a **no-misfile test**: no `(module, member)` in `_UISAFE_SYMBOLS` may also
  appear in any transitional triple.

**Why not module prefixes** (consult §2/§6): `game.strategy.data.*` and several
service modules are *mixed*. Counterexamples that a prefix would wrongly bless:
- `race_description_llm_controller.py`: `FieldStatus` enum (`:47`) is safe but
  `RaceDescriptionLLMController` (`:90`) is a live state machine.
- `economy_config.py`: `get_default_economy_config()` (`:135`) is safe but
  `set_default_economy_config()` (`:143`) mutates the module cache.
The transitional allowlist STAYS file-scoped: the same symbol can be safe in one
file and live in another (`RaceLibrary`, `DesignCatalog`).

## TAIL triage

### Promote to UISAFE (meets all 4 criteria) — verified live 2026-05-22
| `(module, member)` | TAIL site(s) today | Evidence |
|---|---|---|
| `game.strategy.engine.game_config` · `VALID_GALAXY_TYPES` | `galaxy_test/galaxy_mode.py` | static scalar (`game_config.py:39`); already UISAFE elsewhere — fixes the split |
| `game.strategy.data.race_config` · `RaceConfig` | `race_setup/controller.py`, `race_setup/screen.py` | detached config dataclass (`race_config.py:90`); named in Pattern #5 |
| `game.strategy.data.race_point_budget` · `RacePointBudget` | `race_setup/controller.py`, `race_validator.py` | detached cost calc (`race_point_budget.py:35`); named in Pattern #5 |
| `game.strategy.data.order_types` · `OrderType` | `orders_window.py`, `strategy_build_queue_manager.py`, `strategy_detail_fmt.py`, `strategy_screen_order_editing.py` | pure enum (`order_types.py:18`) |
| `game.strategy.data.planet` · `PlanetType` | `galaxy_test/constants.py`, `galaxy_test/system_mode.py`, `strategy_render/dyson_spheres.py`, `strategy_render/systems.py` | pure enum (`planet.py:89`) |
| `game.strategy.data.fleet_hierarchy` · `BattleRole` | `battle_setup/constants.py`, `battle_setup/controller.py` | pure enum (`fleet_hierarchy.py:18`) |
| `game.strategy.data.fleet_hierarchy` · `CombatPolicy` | `battle_setup/fleet_hierarchy_editor.py` | detached scalar dataclass (`fleet_hierarchy.py:32`) |
| `game.strategy.config.economy_config` · `get_default_economy_config` | `empire_panel_window.py`, `strategy_event_router.py` | cached static-config getter (`economy_config.py:135`) |
| `game.strategy.services.race_description_llm_controller` · `FieldStatus` | `race_description_panel.py`, `race_setup/llm_dialog_service.py` | pure enum (`...llm_controller.py:47`) — symbol-level entry is what makes this safe while the module's controller stays excluded |
| `game.strategy.services.ability_metadata` · `StrategicKind` | `builder/stat_rows_dynamic.py` | enum over static metadata (`ability_metadata.py:83`) |
| `game.strategy.services.ability_metadata` · `abilities_with_kind_tag` | `builder/stat_rows_dynamic.py` | pure frozenset query over prebuilt tables (`ability_metadata.py:512`) |
| `game.strategy.services.superweapon_registry` · `SUPERWEAPONS` | `builder/stat_getters.py` | immutable tuple of frozen specs (`superweapon_registry.py:70`) |

Also reconcile (already in UISAFE block, ensure listed in `_UISAFE_SYMBOLS` +
Pattern #5 token list): the existing UISAFE entries
(`EnvironmentalPreference`, `habitability_factors.*`, `homeworld_presets.*`,
`RacePointBudget`, `race_config` label tuples, `game_config` scalars,
`PlayerConfig`, `RaceLibrary` for `new_game_setup_screen`? **no** — see below),
`ContainableKind`, `ActivationPhase`, `ComponentActivationState`. Note
`RaceLibrary` is NOT UISAFE (filesystem load/save orchestration — stays TAIL).

### In-pass decisions on the two open items
- **`ComponentActivationState`** (`...imports_guard.py:104`,
  `strategy_detail_fmt.py`): detached `@dataclass` of a `phase` enum + scalar
  tick counters (`component_activation_state.py:33-52`), holds no live session
  ref. **Bless it**: add to `_UISAFE_SYMBOLS` AND to the Pattern #5 token list
  (closes the doc/guard drift in the safe direction).
- **`EmpireEconomySnapshot`** (`empire_treasury_panel.py:33`): used ONLY as a
  type annotation (`:65`, `:301`, `:306`). **Delete the runtime import** — move
  under `TYPE_CHECKING` and rely on `from __future__ import annotations` — and
  drop the TAIL entry. Do NOT promote (it would broaden policy for a symbol the
  UI does not use at runtime).

### Stay deferred — PROJ-475 (live session/service readers)
`DesignValidator`, `EmpireEconomyService`, `compute_planet_production`,
`calculate_habitability`, `extract_abilities_from_component`/`ship_has_ability`/
`has_warp_capability`, `FleetSpeedCalculator`, `system_effects_collector.*`
(`collect_system_effects`/`collect_sector_effects`/`make_group_key`/
`make_display_name`/`format_intrinsic_ability_magnitude`), `FighterWing`/
`SatelliteConstellation` (live deployed-group models with `ships`/`location` and
mutators — `deployed_group.py:333-415`), `FacilityAbilitySource`,
`SectorEnvironment` (captures live `StarSystem`), `DropPod`/`CarriedVehicle`
(runtime cargo state), `cargo_transfer_service.*`, runtime `DesignCatalog`
(`strategy_build_queue_manager.py`), live-context `RaceLibrary`
(`strategy_event_router.py`, `species_selector_mixin.py`), `GameSession`,
`SaveGameService`, `ReplayResolver`, `GalaxyPathfindingService`.

### Stay deferred — PROJ-476 (tooling/editor/sandbox)
`battle_setup_state.py` / `fleet_hierarchy_editor.py` live models (`Fleet`,
`ShipInstance`, `TaskForce`, `Squadron`); `galaxy_test/*` generation
(`Galaxy`, `DensityMap`, loaders, placement strategies, `Planet`,
`PlanetGenerator`, `planet_physics.*`, `StarSystem`, `Star`, `StarGenerator`,
`SystemBlueprintsLoader`, `PlanetImageRegistry`); race-setup tooling services
(`RaceLibrary`, `RaceRandomizer`, `RaceCaptionLoader`,
`RaceDescriptionLLMController` — the controller, NOT its `FieldStatus` enum);
`get_default_design_role_registry`; tooling `DesignCatalog` browser
(`design_selector_window.py`).

> NOTE on `PlanetType`/`OrderType`/`BattleRole`/`CombatPolicy`/
> `get_default_economy_config`/`FieldStatus`/builder metadata: several of these
> ARE imported by tooling files (galaxy_test, battle_setup, builder). They are
> promoted to UISAFE anyway because membership is a property of the **symbol**
> (a pure enum / static table / detached value), not the file. The symbol-level
> structure is precisely what lets a tooling file legitimately import a UI-safe
> enum while its live/generation imports stay TAIL for PROJ-476.

## Risks (consult §6)
- Promoting a pure-but-live-consuming helper (the `calculate_habitability` /
  `project_fleet_position` / `SectorEnvironment` traps). Mitigation: criterion 2
  ("does not require/return live objects") + per-symbol evidence in this table.
- Module-prefix accidental blessing — avoided by choosing symbol-level data.
- Parity test brittleness — avoided by a parseable fenced token list in Pattern
  #5, not prose scraping.
- Turning the parity test on before reconciling drift — Phase 1 reconciles
  (`ComponentActivationState`, `VALID_GALAXY_TYPES`) in the SAME task that adds
  the test, so the suite never goes red between commits.
- Category creep into a de-facto 476 triage — capped: promote ONLY the listed
  symbols; everything else stays file-scoped TAIL.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
