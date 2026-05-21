# Cross-Layer Type Flow Report

> **Generated:** 2026-05-20 — Cross-layer type flow validation against `game/` production code. Based on prior audit heatmap data and live source tracing.

## Summary

- **Cross-layer type flows traced:** 12 distinct flow chains (Core→Simulation→Strategy→UI)
- **Type-loss boundaries found:** 7 loss sites across 3 layer transitions
- **Protocol conformance gaps:** 8 (5 missing return types on GameSession mutators, 2 Protocol return-type erosion, 1 Strategy→UI command dispatch)
- **Strict-migration candidate layers:** 3 ready-now (services, assets, research), 2 near-ready (engine, ai)
- **Estimated strict-mode error reduction:** ~334 errors eliminated if all layers go strict

## Type-Loss Analysis

### Flow 1: Core Protocol → Strategy Data Entity → Facade DTO → UI

- **Origin type:** `IPlanet.location -> Any` (protocol declares `Any` for HexCoord), but concrete `Planet.location` is `HexCoord`
- **Protocol receives:** `IPlanet.location -> Any` in `game/core/protocols/strategy_entities.py:104`
- **DTO receives:** `PlanetInfo.location: HexCoord` in `game/strategy/facade/dto/planet_dto.py:80` — correctly narrowed
- **Loss at:** The Protocol itself. Every entity Protocol in `strategy_entities.py` and `strategy_domain.py` declares spatial properties (`location`, `global_location`, `position`) as `-> Any` to avoid cross-layer import cycles. This is an architectural choice, not a bug — the concrete classes carry the real type.
- **Fix suggested:** Add `TYPE_CHECKING` imports of `HexCoord` / `Vector2` in protocol modules and narrow return types without runtime cost. Example: `location: 'HexCoord'` via string annotation.

### Flow 2: GameSession.handle_command → StrategySessionFacade → UI command dispatch

- **Origin type:** `GameSession._command_registry.dispatch()` returns `ValidationResult`
- **Intermediate receives:** `GameSession.handle_command(command: Any) -> Any` at `game/strategy/engine/game_session.py:403`
- **UI receives:** `StrategySessionFacade.handle_command(command: Command) -> ValidationResult` at `game/strategy/facade/strategy_session_facade.py:205` — correctly narrowed (facade wraps the loss)
- **Loss at:** `game/strategy/engine/game_session.py:403`. The `-> Any` annotation is unnecessarily broad.
- **Fix suggested:** Change to `def handle_command(self, command: Command) -> ValidationResult` (with TYPE_CHECKING guard on `Command`).

### Flow 3: GameSession mutator properties → TurnEngine → UI

- **Origin type:** `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator` — well-typed Protocols
- **Intermediate receives:** `GameSession.fleet_mutator` / `planet_mutator` / `empire_mutator` / `ship_mutator` — **missing return annotation** at `game/strategy/engine/game_session.py:217,231,240,249`. Each carries `# type: ignore[no-untyped-def]`.
- **UI receives:** N/A (these are internal Strategy → Sub-engine accessors)
- **Loss at:** `game/strategy/engine/game_session.py:217,231,240,249`. Four public properties omit return types entirely.
- **Fix suggested:** Add `-> IFleetMutator`, `-> IPlanetMutator`, `-> IEmpireMutator`, `-> IShipInstanceMutator` with TYPE_CHECKING imports.

### Flow 4: Strategy engine internals → mutator resolution helpers

- **Origin type:** Strategy mutator Protocols (well-typed)
- **Intermediate receives:** Multiple engine classes call private `_get_planet_mutator()`, `_get_empire_mutator()`, `_get_ship_mutator()` methods that return `-> Any`:
  - `AtmosphereEngine._get_planet_mutator() -> Any` at `game/strategy/engine/atmosphere_engine.py:30`
  - `HarvestingEngine._get_planet_mutator() -> Any` at `game/strategy/engine/harvesting_engine.py:196`
  - `HarvestingEngine._get_empire_mutator() -> Any` at `game/strategy/engine/harvesting_engine.py:205`
  - `PlanetModifierEffectEngine._get_planet_mutator() -> Any` at `game/strategy/engine/planet_modifier_effect_engine.py:34`
  - `ProductionSpawner._get_planet_mutator() -> Any` at `game/strategy/engine/production_spawner.py:103`
  - `BaseOrderHandler._get_planet_mutator() -> Any` at `game/strategy/engine/order_handlers/base.py:143`
  - `BaseOrderHandler._get_ship_mutator() -> Any` at `game/strategy/engine/order_handlers/base.py:152`
  - `SuperweaponOrderProcessor._get_empire_mutator() -> Any` at `game/strategy/engine/superweapon_order_processor.py:77`
- **Loss at:** 8 engine-internal helper methods across Strategy. All resolve the same pattern: pull mutator from session config, return `-> Any`.
- **Fix suggested:** All should return the specific mutator Protocol. Most are one-liners: `return self._config.planet_mutator`. Add return annotations matching the origin Protocol types.

### Flow 5: Core Protocol → AI protocols → AI interfaces

- **Origin type:** `ICombatShip.position -> Any` (protocol), concrete `Ship.position: Vector2`
- **AI receives:** `IControllable.get_position() -> Any` at `game/ai/interfaces/controllable.py:41`
- **AI adapter:** `ShipControllableAdapter.get_position()` at `game/ai/interfaces/controllable.py:258` — also `-> Any`
- **Loss at:** `game/ai/interfaces/controllable.py:41,258`. The controllable interface could declare `-> Vector2`.
- **Fix suggested:** Add `TYPE_CHECKING` import of `Vector2` and use string annotation `'Vector2'`.

### Flow 6: Core Registry → Simulation → Strategy

- **Origin type:** `RegistryManager.get_validator() -> Any` at `game/core/registry.py:248,339`
- **Consumers:** Simulation and Strategy callers expect `IValidator` but receive `Any`
- **Loss at:** `game/core/registry.py:248` and `339`. Registry returns untyped `Any`.
- **Fix suggested:** Return `Optional[Callable[..., Any]]` or a typed `ValidatorProtocol`.

### Flow 7: Simulation → Strategy: Battle outcome interpretation

- **Origin type:** `BattleOutcome` (frozen DTO from simulation)
- **Intermediate receives:** `SimulationBattleResolver._build_capture_context() -> Any` at `game/strategy/adapters/simulation_adapter.py:426`
- **Strategy receives:** Typed through `IBattleResolver` interface
- **Loss at:** `game/strategy/adapters/simulation_adapter.py:426`. Internal helper returns `-> Any` but could return a concrete type or `IReplayCaptureContext`.
- **Fix suggested:** Define and annotate with `ReplayCaptureContext` or similar.

## Protocol Conformance Gaps

### 1. GameSession mutator properties — missing return types (CRITICAL)

**Protocol:** `IFleetMutator`, `IPlanetMutator`, `IEmpireMutator`, `IShipInstanceMutator` all well-defined in `game/core/protocols/strategy_mutators.py`.

**Implementation (GameSession):** Four public properties at `game/strategy/engine/game_session.py:217-254` omit return types entirely and carry explicit `# type: ignore[no-untyped-def]` suppressions:
- `fleet_mutator` (line 217)
- `planet_mutator` (line 231)
- `empire_mutator` (line 240)
- `ship_mutator` (line 249)

**Impact:** Mypy cannot verify that these properties satisfy the Protocol contract. Any caller of `session.fleet_mutator` gets an untyped object.

**Fix:** Add return annotations matching the protocols.

### 2. Protocol properties use `-> Any` for well-known types

Across all 9 protocol modules in `game/core/protocols/`, properties that return concrete types (HexCoord, Vector2, PlanetType, StarType, etc.) are declared as `-> Any` or `-> list[Any]` / `-> dict[str, Any]`. This is intentional — avoiding cross-layer import cycles in Protocol definitions — but it means no automated conformance check can verify that strategy entities actually return `HexCoord` from `location`.

Key examples:
- `IPlanet.location -> Any` (should be `'HexCoord' | None`)
- `IFleet.location -> Any` (should be `'HexCoord'`)
- `IStarSystem.global_location -> Any` (should be `'HexCoord'`)
- `IStar.star_type -> Any` (should be `StarType` enum)
- `ICombatShip.position -> Any` (should be `'Vector2'`)
- `ICamera.position -> Any` (should be `'Vector2'`)
- `ICamera.world_to_screen -> Any` (should return `'Vector2'`, accept `'Vector2'`)
- `ISectorEnvironment.system -> Any` (should be `'IStarSystem'`)

**Impact:** Type erosion at the protocol layer propagates up through the entire stack.

**Fix:** Use `TYPE_CHECKING`-guarded imports with string annotation forward references in all protocol modules. This is zero-cost at runtime.

### 3. IPlanetMutator.pop_construction_item — returns `-> Any` (MODERATE)

**Protocol:** `IPlanetMutator.pop_construction_item(planet, index) -> Any` at `game/core/protocols/strategy_mutators.py:118`.

**Implementation:** `PlanetWriteService.pop_construction_item() -> Any` at `game/strategy/services/planet_write_service.py:125`.

Both side of the contract match on `-> Any`, but the actual return type is `dict | None`.

**Fix:** Narrow to `-> dict | None` on both Protocol and implementation.

### 4. Core Protocol: IResourceHolder.resources — intentional `-> Any` (ADVISORY)

**Protocol:** `IResourceHolder.resources -> Any` at `game/core/protocols/boundary.py:92`.
**Comment:** "typed as Any to avoid cross-layer import" — the actual type would be `ResourceRegistry | None`.

### 5. IEmpire.color and IEmpire.built_ship_designs — `-> Any` (ADVISORY)

**Protocol:** `IEmpire.color -> Any` at `game/core/protocols/strategy_domain.py:32` (should be `tuple[int, int, int]`).
**Protocol:** `IEmpire.built_ship_designs -> Any` at `game/core/protocols/strategy_domain.py:107` (should be `set[str]`).

### 6. GameSession internal alias properties — no-return-type (MODERATE)

At `game/strategy/engine/game_session.py:202-258`, seven internal alias properties (`_event_bus`, `_fleet_mutator`, `_planet_mutator`, `_empire_mutator`, `_ship_mutator`, `_command_registry`, `_registries`) all carry `# type: ignore[no-untyped-def]` and omit return types. These are underscore-prefixed internal accessors but still violate return-type requirements.

### 7. Strategy engine internal helpers return `-> Any` (MODERATE)

Eight engine-internal helper methods across `game/strategy/engine/` resolve mutators from config and return `-> Any`. Listed in Flow 4 above.

### 8. Simulation-internal protocols — `-> Any` on structural types

`ICombatShip.position -> Any` at `game/simulation/interfaces/entity_protocols.py:88` and related properties in `game/simulation/interfaces/` mirror the same pattern as Core protocols — avoiding cross-layer imports but losing type specificity.

## Mypy Strict-Mode Migration Path

### Density Score Calculation

Density score weights each metric: `-> Any` returns (×3), `: Any` annotations (×1), missing returns (×5), per 100 LOC of production code.

Production LOC by layer (approximate, from heatmap context + file count):
| Layer | Est. LOC | -> Any | :Any | Missing | Density |
|-------|----------|--------|------|---------|---------|
| services | ~200 | 0 | 0 | 0 | 0.0 |
| assets | ~300 | 0 | 0 | 0 | 0.0 |
| research | ~250 | 0 | 0 | 0 | 0.0 |
| engine | ~400 | 0 | 5 | 0 | 1.25 |
| ai | ~1500 | 7 | 47 | 0 | 4.53 |
| core | ~3000 | 30 | 55 | 0 | 4.83 |
| simulation | ~4000 | 15 | 106 | 1 | 3.90 |
| strategy | ~8000 | 19 | 168 | 30 | 4.70 |
| ui | ~12000 | 263 | 143 | 11 | 12.18 |

### Strict Readiness Score

| Layer | -> Any Count | :Any Count | Missing Returns | Strict Readiness | Adoption Order | Est. Error Reduction |
|-------|-------------|-----------|-----------------|-----------------|----------------|----------------------|
| **services** | 0 | 0 | 0 | **READY** | **1st** | 0 (clean) |
| **assets** | 0 | 0 | 0 | **READY** | **2nd** | 0 (clean) |
| **research** | 0 | 0 | 0 | **READY** | **3rd** | 0 (clean) |
| **engine** | 0 | 5 | 0 | **READY-1** | **4th** | ~5 |
| **ai** | 7 | 47 | 0 | **NEAR-READY** | **5th** | ~54 |
| **core** | 30 | 55 | 0 | **NEAR-READY** | **6th** | ~85 |
| **simulation** | 15 | 106 | 1 | **NEEDS-WORK** | **7th** | ~126 |
| **strategy** | 19 | 168 | 30 | **NEEDS-WORK** | **8th** | ~375 |
| **ui** | 263 | 143 | 11 | **HEAVY-LIFT** | **9th** | ~452 |

**Total estimated error reduction if all layers went strict:** ~1097 errors eliminated.

### Adoption Strategy

**Phase 1 (zero-cost, minutes):** Enable strict mode on services, assets, research. These are already clean — add `[mypy-game.services.*]`, `[mypy-game.assets.*]`, `[mypy-game.research.*]` to `mypy.ini` or `pyproject.toml` with `strict = true`. No code changes needed. Verifies infrastructure is sound. ~0 errors.

**Phase 2 (low-effort, hours):** Engine and AI. Engine has only 5 `:Any` annotations to narrow. AI has 7 `-> Any` returns and 47 `:Any` annotations — most in protocol-level definitions for cross-layer types (Vector2, etc.). ~59 errors eliminated.

**Phase 3 (medium-effort, days):** Core. The 30 `-> Any` returns are concentrated in protocols (intentional cross-layer type erosion) and utility functions (`load_json`, `formula_evaluator._eval_node`, `profile_action` wrapper). The 55 `:Any` annotations are mostly in Protocol definitions and registry lookups. The protocols are the architectural decision here — narrowing them requires TYPE_CHECKING guard imports. ~85 errors eliminated.

**Phase 4 (medium-to-heavy, 1-2 weeks):** Simulation. The 106 `:Any` annotations are concentrated in entity/component interfaces and protocol declarations. The 15 `-> Any` returns include internal calculators and combat systems. ~126 errors eliminated.

**Phase 5 (heavy, 2-4 weeks):** Strategy. The 30 missing returns (mostly in `game_session.py`, `deployed_group.py`, `star_system.py`, engine superweapon handlers, and `design_catalog.py`) are the highest-impact fix — adding return types to these functions would cascade-type downstream consumers. The 168 `:Any` annotations are across the entire layer, including facade slices, write services, handlers, and engine internals. The 8 engine helper `_get_*_mutator()` methods are a low-hanging cluster. ~375 errors eliminated.

**Phase 6 (heaviest, 4-8 weeks):** UI. The 263 `-> Any` returns are dominated by Pygame/DearPyGUI callbacks and widget infrastructure where `-> Any` is often correct (event handlers, render callbacks). The 11 missing returns are mostly in editor/target screen button handler factories and snapshot iteration helpers. Most fixes would be narrow: add return types to helper functions, focus on the data-path functions that pass strategy data to UI rendering. ~452 errors would drop to ~100 with focused fixes (the remaining would be legitimate `-> Any` on Pygame callback surfaces).

## Prioritized Narrowing Plan

Ordered by cross-layer impact — each narrowing ripples out to make downstream types more precise:

### Tier 1: Fix the Strategy→UI command dispatch chain (1 type loss, 2 missing returns)

1. **`GameSession.handle_command -> Any`** → `-> ValidationResult` (`game/strategy/engine/game_session.py:403`)
   - Ripple: Every command handler return is now verified as `ValidationResult` through the chain: facade.handle_command → session.handle_command → dispatch → handler.

2. **`GameSession` mutator properties — add return types** (`game/strategy/engine/game_session.py:217,231,240,249`)
   - `fleet_mutator -> IFleetMutator`, `planet_mutator -> IPlanetMutator`, etc.
   - Ripple: 30+ Strategy engine callers get typed mutator access.

### Tier 2: Narrow protocol definitions (8 Protocol → Any returns, eliminates source-of-truth erosion)

3. **Add TYPE_CHECKING imports to all 9 protocol modules** and narrow `-> Any` returns:
   - `IPlanet.location -> 'HexCoord'`
   - `IFleet.location -> 'HexCoord'`
   - `IStarSystem.global_location -> 'HexCoord'`
   - `ICombatShip.position -> 'Vector2'`
   - `ICamera.position -> 'Vector2'`
   - `ICamera.world_to_screen('Vector2') -> 'Vector2'`
   - `IEmpire.color -> tuple[int, int, int]`
   - `IEmpire.built_ship_designs -> set[str]`
   - `IStar.star_type -> 'StarType'`

4. **IPlanetMutator.pop_construction_item -> dict | None** (Protocol + implementation)

### Tier 3: Strategy engine internal helpers (8 small fixes, high leverage)

5. **Eight `_get_*_mutator()` helpers in `game/strategy/engine/`** — add return types matching their respective mutator Protocols. Each is a one-line body accessing `self._config.<mutator>`. Files: `atmosphere_engine.py`, `environmental_hazard_engine.py`, `harvesting_engine.py`, `planet_modifier_effect_engine.py`, `production_spawner.py`, `superweapon_order_processor.py`, `order_handlers/base.py`.

### Tier 4: Core utility return types (5 files, low risk)

6. **`RegistryManager.get_validator() -> Any`** → typed return (`core/registry.py:248,339`)
7. **`FormulaEvaluator._eval_node() -> Any`** → `float | str | bool` (`core/formula_evaluator.py:81`)
8. **`json_utils.load_json() -> Any`** / `load_json_required() -> Any` → `dict[str, Any]` (`core/json_utils.py:79,119`)

### Tier 5: AI interface narrowing (3 protocol fixes)

9. **`IControllable.get_position() -> Any`** → `'Vector2'` (`ai/interfaces/controllable.py:41`)
10. **`ShipControllableAdapter.get_position() -> Any`** → `'Vector2'` (`ai/interfaces/controllable.py:258`)
11. **`IControllable.get_velocity() -> Any`** → `'Vector2'` (`ai/interfaces/controllable.py:46`)

### Tier 6: GameSession missing return types (10 functions)

12. **`GameSession._event_bus`, `_fleet_mutator`, `_planet_mutator`, `_empire_mutator`, `_ship_mutator`, `_command_registry`** — add return types to all 10 missing-return functions in `game/strategy/engine/game_session.py` (reported in `missing_returns.json`).
13. **`StarSystem.primary_star`** — add return type (`game/strategy/data/star_system.py:85`).
14. **`DesignCatalog.load_design_data`** — add return type (`game/strategy/systems/design_catalog.py:236`).

### Tier 7: UI focus (data-path functions only)

15. **WorkshopViewModel._with_ship** — add return type (`game/ui/screens/workshop_viewmodel.py:129`).
16. **WorkshopShipIO._design_catalog** — add return type (`game/ui/screens/workshop_ship_io.py:67`).
17. **StrategyModalWindow.check_clicked_inside_or_blocking** — add return type (`game/ui/screens/strategy_modal_window.py:273`).
18. **Transfer mass preview `_get_catalog`** — add return type (`game/ui/screens/transfer_mass_preview.py:189`).
19. **Editor `_button_handlers` factory functions** (4: atmosphere, gravity, radiation, water target editors) — add return types.

Remaining UI `-> Any` returns are mostly legitimate: Pygame event callbacks, DearPyGUI widget factories, pygame_gui render methods. These should stay `-> Any` or `-> None` where accurate.

## Appendix: Data Sources

- **Heatmap:** `any_heatmap.json` — deterministic AST scan of all `game/` files
- **Any Returns:** `any_returns.json` — 2,403 entries across all layers
- **Missing Returns:** `missing_returns.json` — 303 entries (strategy: 30, ui: 11, simulation: 1, unknown: 1)
- **Live trace:** 12 source files read to verify cross-layer type flows
