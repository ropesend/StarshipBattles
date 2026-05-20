# Cross-Layer Type Flow Report

## Summary
- Cross-layer type flows traced: 343 `-> Any` returns across all layers
- Type-loss boundaries found: 44 (strategy engine lazy-defaults + GameSession mutator properties + protocol Any gaps)
- Protocol conformance gaps: 9 (Core protocol `Any` params/returns, GameSession untyped mutator properties)

---

## Type-Loss Analysis

### Flow 1: Strategy Engine Mutator Lazy-Default Pattern (7 identical sites)

Seven strategy engine classes share a lazy-default pattern where `_get_planet_mutator()` / `_get_ship_mutator()` / `_get_empire_mutator()` return `-> Any`, when their concrete types are known:

| Engine | Function | Return Declared | Actual Type |
|--------|----------|----------------|-------------|
| `AtmosphereEngine` (`game/strategy/engine/atmosphere_engine.py:30`) | `_get_planet_mutator()` | `-> Any` | `PlanetWriteService` (implements `IPlanetMutator`) |
| `HarvestingEngine` (`game/strategy/engine/harvesting_engine.py:196`) | `_get_planet_mutator()` | `-> Any` | `PlanetWriteService` (implements `IPlanetMutator`) |
| `HarvestingEngine` (`game/strategy/engine/harvesting_engine.py:205`) | `_get_empire_mutator()` | `-> Any` | `EmpireWriteService` (implements `IEmpireMutator`) |
| `PlanetModifierEffectEngine` (`game/strategy/engine/planet_modifier_effect_engine.py:34`) | `_get_planet_mutator()` | `-> Any` | `PlanetWriteService` (implements `IPlanetMutator`) |
| `ProductionSpawner` (`game/strategy/engine/production_spawner.py:103`) | `_get_planet_mutator()` | `-> Any` | `PlanetWriteService` (implements `IPlanetMutator`) |
| `SuperweaponOrderProcessor` (`game/strategy/engine/superweapon_order_processor.py:77`) | `_get_empire_mutator()` | `-> Any` | `EmpireWriteService` (implements `IEmpireMutator`) |
| `BaseOrderHandler` (`game/strategy/engine/order_handlers/base.py:143`) | `_get_planet_mutator()` | `-> Any` | `PlanetWriteService` (implements `IPlanetMutator`) |
| `BaseOrderHandler` (`game/strategy/engine/order_handlers/base.py:152`) | `_get_ship_mutator()` | `-> Any` | `ShipInstanceWriteService` (implements `IShipInstanceMutator`) |
| `EnvironmentalHazardEngine` (`game/strategy/engine/environmental_hazard_engine.py:65`) | `_get_ship_mutator()` | `-> Any` | `ShipInstanceWriteService` (implements `IShipInstanceMutator`) |

**Fix:** Replace `-> Any` with `IPlanetMutator`, `IEmpireMutator`, or `IShipInstanceMutator` respectively.

### Flow 2: GameSession Mutator Properties (9 properties — type: ignore suppression)

`GameSession` in `game/strategy/engine/game_session.py` defines 9 properties that return mutators and other services with **no return type annotation**, each suppressed with `# type: ignore[no-untyped-def]`:

| Property | Line | Implicit Return |
|----------|------|----------------|
| `_event_bus` | 202 | `EventBus` |
| `fleet_mutator` | 217 | `IFleetMutator` |
| `_fleet_mutator` | 227 | `IFleetMutator` |
| `planet_mutator` | 231 | `IPlanetMutator` |
| `_planet_mutator` | 236 | `IPlanetMutator` |
| `empire_mutator` | 240 | `IEmpireMutator` |
| `_empire_mutator` | 245 | `IEmpireMutator` |
| `ship_mutator` | 249 | `IShipInstanceMutator` |
| `_ship_mutator` | 254 | `IShipInstanceMutator` |
| `_command_registry` | 258 | `CommandRegistry` |

Combined with the `_get_*_mutator()` lazy-defaults in engines (Flow 1), these create a cascade: **Strategy Engine -> Any -> Order Handler -> Any -> UI**. Every caller that dereferences `session.fleet_mutator` loses type information.

**Fix:** Replace `# type: ignore[no-untyped-def]` with explicit `-> IFleetMutator`, `-> IPlanetMutator`, `-> IEmpireMutator`, `-> IShipInstanceMutator`, `-> EventBus`, and `-> CommandRegistry` return types.

### Flow 3: GameSession.handle_command — facade entry point

`GameSession.handle_command(command: Any) -> Any` at `game/strategy/engine/game_session.py:403` is the primary command-handling entry point. It is called by `StrategySessionFacade.handle_command`, which is the UI's sole write boundary to the strategy layer. Both `command` and the return are `Any`.

```python
# game/strategy/engine/game_session.py:403
def handle_command(self, command: Any) -> Any:
    return self._command_registry.dispatch(command.name, self, command)
```

The actual return is always `ValidationResult` (from `game/core/validation.py`).

**Fix:** Type the command parameter as `Command` (from `game/strategy/engine/commands`) and the return as `ValidationResult`.

### Flow 4: TurnEngine._time_phase -> Any

`TurnEngine._time_phase()` at `game/strategy/engine/turn_engine.py:286` returns `-> Any`. This is a central orchestration method that feeds into every sub-engine's processing. The return leaks upward through `process_turn()` to the facade and ultimately to the UI.

### Flow 5: Core Protocol Definitions Use `Any` in Root Contracts

The Core protocol layer defines 30 properties/methods returning `Any`, polluting the root of the type system:

| Protocol | Method/Property | Should Be |
|----------|----------------|-----------|
| `IStarSystem.global_location` | `-> Any` | `-> HexCoord` |
| `IStarSystem.stars` | `-> list[Any]` | `-> list[Star]` |
| `IStarSystem.planets` | `-> list[Any]` | `-> list[Planet]` |
| `IStarSystem.warp_points` | `-> list[Any]` | `-> list[WarpPoint]` |
| `IStarSystem.storms` | `-> list[Any]` | `-> list[Storm]` |
| `IPlanet.planet_type` | `-> Any` | `-> str` |
| `IPlanet.location` | `-> Any` | `-> HexCoord` |
| `IFleet.location` | `-> Any` | `-> HexCoord` |
| `IFleet.capabilities` | `-> Any` | `-> FleetCapabilities` (or proper type) |
| `IFleet.resources` | `-> Any` | `-> dict[str, float]` |
| `IFleet.battle` | `-> Any` | `-> FleetBattleConfig` (or proper type) |
| `IWarpPoint.location` | `-> Any` | `-> HexCoord` |
| `ISectorEnvironment.local_hex` | `-> Any` | `-> HexCoord` |
| `ISectorEnvironment.system` | `-> Any` | `-> StarSystem` |
| `IEmpire.color` | `-> Any` | `-> tuple[int, int, int]` |
| `IEmpire.built_ship_designs` | `-> Any` | `-> list[str]` |
| `ICombatant.position` | `-> Any` | `-> Vector2` |
| `ICombatShip.position` | `-> Any` | `-> Vector2` |
| `ILocatable.location` | `-> Any` | `-> HexCoord` |

### Flow 6: Strategy -> UI via StrategyScreen / StrategyRenderer

The UI layer has 263 `-> Any` returns. The heaviest concentration is in `StrategyScreen` (15 `-> Any` returns, getting references like `galaxy`, `empires`, `systems`, `active_empire`, `facade`, `session`, etc.) and `StrategyRenderer` (13 `-> Any` returns, for `camera`, `galaxy`, `systems`, `empires`, `hex_size`, `screen_width`, `screen_height`, `SIDEBAR_WIDTH`, `TOP_BAR_HEIGHT`, `empire_assets`, etc.).

These properties retrieve well-typed objects from the strategy layer but the UI declares them as untyped properties:

```python
# game/ui/screens/strategy_screen.py:161
@property
def galaxy(self) -> Any:  # should be Galaxy
    ...
```

**Fix:** Annotate the 15+ strategy screen properties with concrete types (`Galaxy`, `list[Empire]`, `list[StarSystem]`, `StrategySessionFacade`, `GameSession`, etc.).

### Flow 7: Simulation Internal Protocols

Simulation interfaces also use `Any` in their protocols:

| Protocol | Method | Should Be |
|----------|--------|-----------|
| `ICombatShip.position` (simulation) | `-> Any` | `-> Vector2` |
| `ICombatShip.velocity` | `-> Any` | `-> Vector2` |
| `ICombatShip.resources` | `-> Any` | `-> dict[str, float]` |
| `ICombatShip.combat_engine` | `-> Any` | `-> ShipCombatEngine` (or Protocol) |
| `IProjectile.position` | `-> Any` | `-> Vector2` |
| `IProjectile.velocity` | `-> Any` | `-> Vector2` |
| `IProjectile.type` | `-> Any` | `-> str` |
| `IAIController.ship` | `-> Any` | `-> Ship` (or ICombatShip) |

---

## Protocol Conformance Gaps

### Gap 1: `IPlanetMutator` uses `Any` for well-known types

Core protocol `game/core/protocols/strategy_mutators.py` defines:

```python
def append_construction_item(self, planet: "Planet", item: Any) -> None: ...
def pop_construction_item(self, planet: "Planet", index: int = 0) -> Any: ...
def set_owner_id(self, planet: "Planet", owner_id: Any) -> None: ...
def set_atmosphere(self, planet: "Planet", value: Any) -> None: ...
def set_atmosphere_target(self, planet: "Planet", value: Any) -> None: ...
def set_gravity_target(self, planet: "Planet", value: Any) -> None: ...
def set_water_target(self, planet: "Planet", value: Any) -> None: ...
```

The implementation (`PlanetWriteService`) mirrors these signatures exactly, so there is no *mismatch*, but the protocol is unnecessarily loose. `owner_id` should be `int | None`, `atmosphere`/`atmosphere_target` should be `dict[str, float]`, `gravity_target` should be `float`, `water_target` should be `float`.

### Gap 2: `IFleetMutator` uses `Any` for ship/fleet/policy

```python
def add_ship(self, fleet: "Fleet", ship: Any) -> None: ...
def remove_ship(self, fleet: "Fleet", ship: Any) -> bool: ...
def add_task_force(self, fleet: "Fleet", tf: Any) -> None: ...
def remove_task_force(self, fleet: "Fleet", tf: Any) -> bool: ...
def set_fleet_policy(self, fleet: "Fleet", policy: Any) -> None: ...
```

These should reference `ShipInstance`, `TaskForce`, and `CombatPolicy` respectively.

### Gap 3: `IEmpireMutator` uses `Any` for `event_bus` parameter

```python
def remove_fleet(self, empire: "Empire", fleet: "Fleet", *, event_bus: Any = None) -> bool: ...
def prune_empty_fleets(self, ..., *, event_bus: Any = None) -> list: ...
```

`event_bus` should be `EventBus | None`.

### Gap 4: `IShipInstanceMutator.set_activation_state` uses `Any`

```python
def set_activation_state(self, instance: "ShipInstance", component_id: str, state: Any) -> None: ...
```

`state` should be `str` or a specific enum.

### Gap 5: `GameSession` property overrides without return types

The `GameSession` class has 9 properties with `# type: ignore[no-untyped-def]` (see Flow 2). These are the concrete implementation of the strategy session and serve as the source of all mutator references for engines and the facade. Without proper return types, mypy cannot verify that `session.fleet_mutator` actually satisfies `IFleetMutator`.

---

## Mypy Strict-Mode Migration Path

Error density computed from `mypy --strict` report (2,108 real errors, 273 notes; total 2,423 entries). Error counts exclude `combat_lab/` files.

### Per-Layer Error Density (real mypy errors only)

| Layer | Real Errors | Notes | Files | Errors/File | Strict Readiness |
|-------|------------|-------|-------|-------------|-----------------|
| research | 0 | 0 | 4 | 0.0 | **Ready now** |
| services | 1 | 3 | 7 | 0.1 | **Ready now** |
| strategy | 452 | 82 | 264 | 1.7 | Moderate effort |
| ai | 40 | 5 | 20 | 2.0 | Moderate effort |
| core | 77 | 15 | 35 | 2.2 | Needs fixes |
| unknown/top-level | 16 | 5 | 6 | 2.7 | Needs fixes |
| simulation | 417 | 44 | 120 | 3.5 | Significant effort |
| ui | 1084 | 119 | 308 | 3.5 | Significant effort |
| engine | 11 | 0 | 3 | 3.7 | Small files, impactful |
| assets | 10 | 0 | 2 | 5.0 | Small files, impactful |

### Recommended Adoption Order

Based on error density (lowest first, respecting layer dependencies):

| Rank | Layer | Errors/File | Files | Estimated Reduction | Rationale |
|------|-------|-------------|-------|--------------------|-----------|
| **1** | **research** | 0.0 | 4 | N/A (clean) | Zero errors — adopt strict immediately |
| **2** | **services** | 0.1 | 7 | ~~1 error (`import-untyped` for `requests`) | Single stub-install fix needed |
| **3** | **assets** | 5.0 | 2 | ~~10 errors (mostly `no-any-return`, `var-annotated`) | Only 2 files — quick win despite density |
| **4** | **engine** | 3.7 | 3 | ~~11 errors (4 `has-type`, 4 `union-attr`, 2 `no-any-return`, 1 `assignment`) | Only 3 files — `PhysicsBody` Vector2 typing root cause |
| **5** | **core** | 2.2 | 35 | ~~77 errors (50 `has-type`, 16 `no-any-return`, 8 `assignment`) | Foundation layer — fixing here benefits ALL higher layers. `Vector2` `has-type` errors are the #1 blocker |
| **6** | **ai** | 2.0 | 20 | ~~40 errors (28 `no-any-return`, 6 `assignment`) | `controllable.py` adapter contributes 16 `no-any-return` errors |
| **7** | **simulation** | 3.5 | 120 | ~~417 errors (130 `attr-defined`, 65 `has-type`, 63 `union-attr`, 62 `no-any-return`) | Largest simulation body — `Ship` multi-inheritance/mixin causes most `attr-defined` errors. Fixing Core `Vector2` would resolve the `has-type` cluster |
| **8** | **strategy** | 1.7 | 264 | ~~452 errors (131 `no-any-return`, 77 `arg-type`, 65 `union-attr`, 50 `attr-defined`) | `GameSession` untyped properties + engine lazy-defaults account for ~~30% of errors |
| **9** | **unknown/top-level** | 2.7 | 6 | ~~16 errors | `app.py` scene-accessor properties (9 `-> Any` returns) |
| **10** | **ui** | 3.5 | 308 | ~~1,084 errors (491 `attr-defined`, 181 `assignment`, 144 `arg-type`, 76 `no-any-return`) | `pygame_gui` external library untyped — majority of `attr-defined` and `assignment` errors from `pygame_gui.widgets` |

### Error Reduction Cascade

If each layer went strict in the proposed order, fixing `no-any-return` and add type annotations:

| Step | Layer Adopted | Errors Resolved (est.) | Cumulative Remaining | Primary Fixes Needed |
|------|--------------|----------------------|---------------------|---------------------|
| 1 | research | 0 | 2,108 | None |
| 2 | services | ~1 | 2,107 | `pip install types-requests` |
| 3 | assets | ~10 | 2,097 | Add `-> Surface`, `-> str`, `-> dict[str, Surface]` return types |
| 4 | engine | ~11 | 2,086 | Type `PhysicsBody.x`, `.y` as `float` not `int` |
| 5 | core | ~77 | 2,009 | Fix `Vector2.x`/`.y` `has-type` (50 errors); add 16 missing return types. **This also resolves `has-type` errors in simulation (65) and boundary (10+) downstream** |
| 6 | ai | ~28 | 1,981 | Add return types to `ShipControllableAdapter` methods |
| 7 | simulation | ~200 | 1,781 | Fix `Ship` mixin attr-defined errors; remaining `has-type` already resolved by step 5 |
| 8 | strategy | ~160 | 1,621 | Annotate `GameSession` mutator properties; type engine lazy-defaults |
| 9 | unknown | ~9 | 1,612 | Annotate `Game` scene accessor properties |
| 10 | ui | ~100 | 1,512 | Fix `no-any-return` sites (76); proper pygame_gui typing |

The **cross-layer domino effect** is strongest from Fixing Core: resolving `Vector2` `has-type` errors (50 in core alone) also eliminates 65 `has-type` errors in simulation, ~10 in engine, and ~6 in AI. This single fix accounts for ~130 mypy errors across 4 layers.

---

## Prioritized Narrowing Plan (ordered by cross-layer impact)

### Tier 1 — Foundation (unblocks entire codebase)

1. **Fix `Vector2` `has-type` errors in `game/core/math.py`** — The `Vector2` class uses `replace()` and `__getattr__` patterns that mypy cannot type. Adding `@dataclass_transform` or explicit `x: float`, `y: float` annotations with `__init__` resolves 50 core + ~65 simulation + ~10 engine `has-type` errors. **Impact: ~130 errors across 4 layers.**

2. **Annotate Core Protocol `-> Any` returns with concrete types** (18 sites in `strategy_entities.py`, 3 in `combat.py`, 3 in `ui.py`, 2 in `boundary.py`, 1 in `common.py`, 2 in `strategy_domain.py`). This fixes the root contract pollution — every protocol consumer benefits.

3. **Tighten Core Protocol `Any` parameters** in `strategy_mutators.py`: `set_owner_id(owner_id: Any)` -> `set_owner_id(owner_id: int | None)`, `set_atmosphere(value: Any)` -> `set_atmosphere(value: dict[str, float])`, etc.

### Tier 2 — Strategy Layer (fixes the engine->facade->UI chain)

4. **Annotate `GameSession` mutator properties** — Replace the 9 `# type: ignore[no-untyped-def]` sites with explicit `-> IPlanetMutator`, `-> IFleetMutator`, `-> IEmpireMutator`, `-> IShipInstanceMutator` return types. **This is the single highest-impact type-loss fix:** it directly affects every engine that reads `session.fleet_mutator`.

5. **Fix engine lazy-default `_get_*_mutator()` methods** (9 sites across 6 files) — Replace `-> Any` with the appropriate mutator protocol. These are the bridge between GameSession and the individual sub-engines.

6. **Type `GameSession.handle_command`** — Change `(command: Any) -> Any` to `(command: Command) -> ValidationResult`.

### Tier 3 — UI Layer (top of the chain)

7. **Annotate `StrategyScreen` and `StrategyRenderer` property returns** — The 15+ `-> Any` properties that return `Galaxy`, `list[Empire]`, `list[StarSystem]`, `StrategySessionFacade`, etc. should use their concrete types.

8. **Type `Game.scene` accessor properties** in `game/app.py` — 9 properties (`battle_scene`, `strategy_scene`, `builder_scene`, etc.) all return `-> Any`; these should return specific scene types or `IScene`.

### Tier 4 — Simulation and AI

9. **Annotate simulation protocols** — `ICombatShip`, `IProjectile`, `IAIController` in `game/simulation/interfaces/` use `-> Any` for `position`, `velocity`, `resources`, `ship`, etc. (7 sites).

10. **Annotate AI adapter** — `ShipControllableAdapter` in `game/ai/interfaces/controllable.py` has 16 methods returning `-> Any`; these delegate to well-typed `Ship` methods.

---

## Appendix: Error Code Distribution by Layer (Top 3)

| Layer | #1 Error Type | Count | #2 Error Type | Count | #3 Error Type | Count |
|-------|---------------|-------|---------------|-------|---------------|-------|
| core | `has-type` (Vector2) | 50 | `no-any-return` | 16 | `assignment` (implicit Optional) | 8 |
| services | `import-untyped` | 1 | — | — | — | — |
| assets | `no-any-return` | 6 | `var-annotated` | 3 | `assignment` | 1 |
| engine | `has-type` | 4 | `union-attr` | 4 | `no-any-return` | 2 |
| simulation | `attr-defined` (Ship mixins) | 130 | `has-type` | 65 | `union-attr` | 63 |
| strategy | `no-any-return` | 131 | `arg-type` | 77 | `union-attr` | 65 |
| ai | `no-any-return` | 28 | `assignment` | 6 | `has-type` | 4 |
| ui | `attr-defined` (pygame_gui) | 491 | `assignment` | 181 | `arg-type` | 144 |
| unknown | `no-any-return` | 6 | `arg-type` | 6 | `assignment` | 2 |
