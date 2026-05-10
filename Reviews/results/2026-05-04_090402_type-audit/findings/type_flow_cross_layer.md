# Cross-Layer Type Flow Report

## Summary
- Cross-layer type flows traced: 14
- Type-loss boundaries found: 12
- Protocol conformance gaps: 9 (plus 4 design-level Any-leaks in protocols that cascade downstream)

---

## Type-Loss Analysis

### Flow 1: simulation -> strategy -> ui (Facade Read Path)
- **Origin type:** `StarSystem` (concrete) with `global_location: HexCoord`, `stars: List[Star]`, `planets: List[Planet]`
- **Strategy receives:** `get_all_systems() -> List[SystemInfo]` (DTO, well-typed) — NO LOSS
- **UI strategy_screen.py properties:** `systems -> Any` (line 171), `galaxy -> Any` (line 163), `empires -> Any` (line 167)
- **Loss at:** `StrategyScreen.galaxy` line 163 — delegates to `self.session.galaxy` which is `Galaxy | None`, but declares `-> Any`
- **Fix:** Annotate each property with its actual concrete type: `galaxy -> Galaxy | None`, `systems -> dict[str, StarSystem]`, `empires -> dict[int, Empire]`. This affects 10 properties in `strategy_screen.py` and similar patterns in `StrategyRenderer`, `FleetOperations`, `ColonizationSystem`, `SuperweaponOperations`, `CameraNavigator`.

### Flow 2: simulation -> strategy (Battle Resolution)
- **Origin type:** `run_battle(spec) -> BattleOutcome` (frozen DTO, well-typed)
- **Strategy resolves:** `SimulationBattleResolver.resolve_battle() -> BattleResult` (well-typed) — NO LOSS
- **Strategy internals:** `_build_capture_context() -> Any` (line 334) returns a `dict[str, ...]`
- **Loss at:** `SimulationBattleResolver._build_capture_context` line 334 — should be `-> dict`
- **Fix:** Annotate as `-> dict[str, Any]` (its actual return type).

### Flow 3: engine -> simulation (PhysicsBody inheritance)
- **Origin type:** `PhysicsBody` with `position: Vector2`, `velocity: Vector2`
- **Simulation mixin:** `ShipPhysicsMixin` — mypy reports 22+ attr-defined errors because `ShipPhysicsMixin` is a mixin without proper protocol typing. `self.position` is accessed but defined on a sibling class in MRO.
- **Loss at:** `ShipPhysicsMixin` `game/simulation/entities/ship_physics.py` — mixin pattern with untyped `self.*` attribute access
- **Fix:** Document ShipPhysicsMixin's required attributes via a Protocol or abstract properties.

### Flow 4: simulation -> ai (ShipControllableAdapter)
- **Origin type:** `Ship` class with concrete typed properties (e.g., `position: Vector2`, `angle: float`)
- **AI adapter:** `ShipControllableAdapter.get_position() -> Any` (line 258), `get_velocity() -> Any` (line 262)
- **AI receives:** Every adapter method returns `-> Any` despite `self._ship` having concrete return types
- **Loss at:** All 18+ accessor methods in `ShipControllableAdapter` (lines 258-392)
- **Fix:** Replace `-> Any` with concrete types. `get_position() -> Vector2`, `get_velocity() -> Vector2`, `get_rotation() -> float`, etc. The "avoid pygame dependency" comment at line 18 is obsolete — Vector2 is from `game.core.math` not pygame.

### Flow 5: core protocols -> strategy entities (Strategy Entity Protocols)
- **Origin type:** Protocols in `game/core/protocols/strategy_entities.py` declare many properties as `-> Any`
- **Concrete entities:** Fleet, Planet, StarSystem, Empire have concrete types (e.g., `Fleet.location: HexCoord`)
- **Loss at:** Protocol definitions themselves. 24 properties return `-> Any` across `IStarSystem`, `IStar`, `IPlanet`, `IFleet`, `IWarpPoint`, `ISectorEnvironment`, `IEmpire`.
- **Fix:** Narrow protocol annotations. Example: `IFleet.location -> HexCoord` instead of `-> Any`, `IPlanet.planet_type -> PlanetType` instead of `-> Any`, `IEmpire.color -> tuple[int, int, int]` instead of `-> Any`.

### Flow 6: core protocols -> combat (Combat Protocols)
- **Origin type:** `ICombatant.position -> Any`, `ICombatShip.position -> Any`
- **Concrete:** `Ship.position: Vector2` (typed in `game/core/math.py`)
- **Loss at:** `game/core/protocols/combat.py` lines 21, 82
- **Fix:** Replace `-> Any` with `-> 'Vector2'` (string literal for forward ref or import).

### Flow 7: core protocols -> ui (Camera Protocol)
- **Origin type:** `ICamera.position -> Any`, `world_to_screen(Any) -> Any`, `screen_to_world(Any) -> Any`
- **Concrete:** `Camera.position: Vector2`, methods return `Vector2`
- **Loss at:** `game/core/protocols/ui.py` lines 62, 66, 78
- **Fix:** Use `Vector2` import from `game.core.math` (Core depends on nothing; Vector2 is Core's own type).

### Flow 8: core -> all layers (JSON loading)
- **Origin:** `json_utils.load_json() -> Any` (line 79), `load_json_required() -> Any` (line 119)
- **All callers:** receive `Any` from JSON loading — architecturally unavoidable
- **Status:** ACCEPTABLE. This is a genuine unavoidable-Any boundary (dynamic deserialization). Callers should cast/narrow at call sites, not in json_utils.

### Flow 9: core -> simulation (Formula Evaluator)
- **Origin:** `formula_evaluator._eval_node() -> Any` (line 81)
- **Declared:** `evaluate() -> int | float` (line 289)
- **Loss at:** Internal helper `_eval_node` returns Any, triggering `no-any-return` in `evaluate`.
- **Fix:** Annotate `_eval_node` as `-> int | float` (its actual return type).

### Flow 10: core -> ai (Protocol cross-layer)
- **Origin:** `game/ai/protocols.py` — `IGridEntity.position -> Any` (line 42), `IProjectile.type -> Any` (line 75)
- **AI internals:** Concrete implementations return typed values
- **Loss at:** Protocol definition itself
- **Fix:** Use `Vector2` from Core, or keep as Any with explicit comment about why (e.g., "position type varies per simulation backend").

### Flow 11: strategy -> ui (Renderer delegates)
- **Origin:** `StrategyRenderer` properties: `camera -> Any` (line 146), `galaxy -> Any` (line 150), `systems -> Any` (line 154), `empires -> Any` (line 158)
- **All assigned:** From `StrategyScreen` which has concrete types from the session
- **Loss at:** `StrategyRenderer` property definitions — all `-> Any`
- **Fix:** Same pattern as StrategyScreen — annotate with actual types.

### Flow 12: strategy engine internals
- **Origin:** `OrderSerializer._deserialize_target() -> Any` (line 99)
- **Loss at:** Returns mixed types depending on order type — HexCoord, Planet, etc.
- **Fix:** Annotate as `-> HexCoord | str | None` or use a union type that covers all order targets.

---

## Protocol Conformance Gaps

### Protocol: IStarSystem (`game/core/protocols/strategy_entities.py`)
| Property | Protocol Type | Concrete (StarSystem) | Gap |
|----------|-------------|----------------------|-----|
| `stars` | `List[Any]` | `List[Star]` | MINOR — Any leaks to consumers |
| `planets` | `List[Any]` | `List[Planet]` | MINOR |
| `warp_points` | `List[Any]` | `List[WarpPoint]` | MINOR |
| `global_location` | `Any` | `HexCoord` | **MAJOR** — Any cascades to all consumers |
| `storms` | `List[Any]` | `List[Storm]` | MINOR |

**Status:** Protocol-to-implementation match is correct structurally; the problem is the Protocol itself uses `Any` where concrete types exist. The protocol sits in `core/` so it can import `HexCoord` from `game.core.hex_math` without violating layer rules. Recommended: narrow all 5 properties.

### Protocol: IFleet (`game/core/protocols/strategy_entities.py`)
| Property | Protocol Type | Concrete (Fleet) | Gap |
|----------|-------------|-----------------|-----|
| `ships` | `List[Any]` | `List[ShipInstance]` | MINOR |
| `orders` | `List[Any]` | `List[Order]` | MINOR |
| `location` | `Any` | `HexCoord` | **MAJOR** |
| `path` | `List[Any]` | `List[HexCoord]` | MINOR |
| `construction_queue` | `List[Any]` | `List[dict[str, Any]]` | MINOR |
| `capabilities` | `Any` | `FleetCapabilityCalculator` | **MAJOR** — delegate ref |
| `resources` | `Any` | `FleetConsumableAggregator` | **MAJOR** — delegate ref |
| `battle` | `Any` | `FleetBattleAdapter` | **MAJOR** — delegate ref |

**Status:** 4 MAJOR Any leaks. Delegates (capabilities/resources/battle) were intentionally typed as `Any` to avoid cross-layer imports (PROJ-210). A solution is to define `IFleetCapabilityCalculator`, `IFleetConsumableAggregator`, `IFleetBattleAdapter` protocols in Core.

### Protocol: IPlanet (`game/core/protocols/strategy_entities.py`)
| Property | Protocol Type | Concrete (Planet) | Gap |
|----------|-------------|-----------------|-----|
| `planet_type` | `Any` | `PlanetType` enum | **MAJOR** |
| `deposits` | `Dict[str, Any]` | `Dict[str, float]` | MINOR (values are float) |
| `location` | `Any` | `HexCoord` | **MAJOR** |
| `populations` | `List[Any]` | `List[SpeciesPopulation]` | MINOR |
| `facilities` | `List[Any]` | `List[PlanetaryFacility]` | MINOR |

**Status:** `HexCoord` is importable from Core. `PlanetType` lives in `game/strategy/data/planet.py` and cannot be imported from Core without violating layer rules. Options: (a) move `PlanetType` to `game/core/constants.py`, or (b) accept `Any` for the enum type and document it as a layer-boundary compromise.

### Protocol: IEmpire (`game/core/protocols/strategy_domain.py`)
| Property | Protocol Type | Concrete (Empire) | Gap |
|----------|-------------|-----------------|-----|
| `color` | `Any` | `tuple[int, int, int]` | **MAJOR** |
| `race_config` | `Optional[Any]` | `Optional[RaceConfig]` | MINOR — TYPE_CHECKING only |
| `colonies` | `List[Any]` | `List[Planet]` | MINOR |
| `fleets` | `List[Any]` | `List[Fleet]` | MINOR |
| `built_ship_designs` | `Any` | `Set[str]` | **MAJOR** |

**Status:** `color: Any` could be `tuple[int, int, int]` with zero import cost. `built_ship_designs` could be `Set[str]`.

### Protocol: ICombatant / ICombatShip (`game/core/protocols/combat.py`)
| Property | Protocol Type | Concrete | Gap |
|----------|-------------|----------|-----|
| `ICombatant.position` | `Any` | `Vector2` | **MAJOR** |
| `ICombatShip.position` | `Any` | `Vector2` | **MAJOR** |
| `ICombatShip.layers` | `Dict[Any, Any]` | `Dict[LayerType, LayerData]` | MINOR |
| `ICombatShip.resources` | `Optional[Any]` | `Optional[ResourceRegistry]` | MINOR |
| `ICombatShip.current_target` | `Optional[Any]` | `Optional[Ship]` | MINOR |
| `ICombatShip.secondary_targets` | `List[Any]` | `List[Ship]` | MINOR |

**Status:** `Vector2` is in `game/core/math.py` — zero-import-cost fix for `position`.

### Protocol: IResourceHolder (`game/core/protocols/boundary.py`)
| Property | Protocol Type | Intentional Reason | Gap |
|----------|-------------|-------------------|-----|
| `resources` | `Any` | "typed as Any to avoid cross-layer import" (line 91) | **DOCUMENTED** |

**Status:** The comment makes this an intentional design choice, not a gap. This is a legitimate cross-layer seam where the type system can't express "ResourceRegistry without importing it."

### Protocol: ICamera (`game/core/protocols/ui.py`)
| Method/Property | Protocol Type | Concrete (Camera) | Gap |
|----------------|-------------|-------------------|-----|
| `position` | `Any` | `Vector2` | **MAJOR** |
| `world_to_screen(Any)` | `-> Any` | `-> Vector2` | **MAJOR** |
| `screen_to_world(Any)` | `-> Any` | `-> Vector2` | **MAJOR** |

**Status:** `Vector2` is available in `game.core.math`. Three trivial fixes with zero import cost.

### Protocol: IOrderable (`game/core/protocols/strategy_entities.py`)
| Method/Property | Protocol Type | Gap |
|----------------|-------------|-----|
| `orders` | `List[Any]` | Should be `List[Order]` but Order lives in strategy |
| `get_current_order()` | `Optional[Any]` | Same constraint |
| `add_order(order: Any)` | — | Same constraint |
| `pop_order()` | `Optional[Any]` | Same constraint |

**Status:** The Order type lives in `game/strategy/data/order_types.py` and cannot be imported from Core. This is an irreducible seam — keep as Any with an explanatory comment.

### Protocol: IAbilitySource (`game/core/protocols/strategy_entities.py`)
| Method/Property | Protocol Type | Gap |
|----------------|-------------|-----|
| `get_abilities()` | `Dict[str, Any]` | Acceptable — abilities dict shape varies |
| `affects_hex(hex_coord: Any)` | `-> bool` | Should accept `HexCoord` |
| `affects_system(system: Any)` | `-> bool` | Should accept `IStarSystem` |
| `get_activation_state(name: str)` | `Optional[Any]` | Acceptable — activation state is polymorphic |

**Status:** `HexCoord` and `IStarSystem` are both importable from Core. Two narrowable params.

---

## Mypy Strict-Mode Migration Path

The Phase 1 deterministic scan found **2103 total mypy strict-mode errors**. Here's the recommended adoption order with error estimates:

| Layer | Current Errors (est) | Error Categories | Strict Readiness | First to Adopt? | Estimated Effort |
|-------|---------------------|-----------------|-----------------|-----------------|------------------|
| **core** | ~50 | `no-any-return` (15), `has-type`/`attr-defined` (30), `implicit-optional` (5) | MEDIUM | **1st** | ~1 day |
| **services** | ~3 | `import-untyped` (stubs: requests) | HIGH | **2nd** | ~5 min (pip install stub) |
| engine | ~5 | `no-any-return` (2), `implicit-optional` (3) | HIGH | 3rd | ~30 min |
| research | ~7 | `implicit-optional` (5), `annotation-unchecked` (2) | HIGH | 4th | ~30 min |
| simulation | ~60 | `no-any-return` (30), `has-type` (10), `attr-defined` (15), misc (5) | MEDIUM | 5th | ~2 days |
| strategy | ~25 | `no-any-return` (10), `implicit-optional` (8), misc (7) | MEDIUM | 6th | ~1 day |
| assets | ~4 | `import-not-found` (PIL), `no-any-return` (2) | HIGH | 7th | ~5 min (pip install stub) |
| ai | ~15 | `no-any-return` (12), `has-type` (2), misc (1) | MEDIUM | 8th | ~1 day |
| ui | ~1900+ | `annotation-unchecked` (~1500), `no-any-return` (~200), misc (~200) | LOW | **LAST** | ~2-4 weeks |

**Proposed adoption sequence:**
1. **Core** — Fix 50 errors. This requires: proper Vector2 typing in math.py, explicit `-> float | None` on Vector2 constructor, formula_evaluator._eval_node return type, json_utils implicit optional, profiling no-any-return. This unlocks 50+ downstream errors that currently cascade from core.
2. **Services** — Install `types-requests`. 3 errors vanish.
3. **Engine** — Fix implicit optionals + no-any-return in physics.py. 5 errors vanish.
4. **Research** — Fix implicit optionals. 7 errors vanish.
5. **Simulation** — This is the hardest non-UI layer. Two main problem areas: (a) planetary.py abilities — 25 `no-any-return` from formula evaluation returning Any, (b) ship_physics.py mixin pattern — 15 `attr-defined` errors requiring a Protocol. These are fixable with volume work.
6. **Strategy** — Fix no-any-return in loaders/generation, implicit optionals. 25 errors.
7. **Assets** — Install `Pillow-stubs`. 4 errors vanish.
8. **AI** — Fix ShipControllableAdapter (18 `no-any-return` from Ship property delegation). 15 errors.
9. **UI** — The 1900 errors are mostly `annotation-unchecked` (mypy refusing to check untyped function bodies) and are a long-tail issue. After layers 1-8 go strict, ~200 `no-any-return` in UI remain. These can be narrowed iteratively.

**Error reduction estimate if each layer went strict:**
- Core strict: resolves ~85 errors (50 direct + ~35 cascade)
- Services strict: resolves ~3 errors
- Engine strict: resolves ~8 errors (5 direct + ~3 cascade)
- Research strict: resolves ~10 errors (7 direct + ~3 cascade)
- Simulation strict: resolves ~90 errors (60 direct + ~30 cascade)
- Strategy strict: resolves ~40 errors (25 direct + ~15 cascade)
- AI strict: resolves ~20 errors (15 direct + ~5 cascade)
- Assets strict: resolves ~4 errors
- After layers 1-8 go strict: ~260 remaining UI errors (down from ~1900)

---

## Prioritized Narrowing Plan

Ordered by cross-layer impact (most impactful first):

### Priority 1 — Protocol Any Narrowing (no code churn, maximum downstream benefit)
1. **`ICamera.position -> Vector2`** (`game/core/protocols/ui.py:62`): Narrow from `Any` to `Vector2`. Affects all Strategy renderer camera delegation, Research layer visualization, ~50+ call sites. **Cost: 1 line.**
2. **`ICamera.world_to_screen -> Vector2`** + **`screen_to_world -> Vector2`** (`ui.py:66,78`): Same fix. **Cost: 2 lines.**
3. **`ICombatant.position -> Vector2`** + **`ICombatShip.position -> Vector2`** (`combat.py:21,82`): Narrow from Any. Affects all AI targeting, damage calculator, collision. **Cost: 2 lines.**
4. **`IFleet.location -> HexCoord`** + **`IPlanet.location -> HexCoord`** (`strategy_entities.py:249,103`): Narrow from Any. Affects all strategy rendering, pathfinding, system lookups. **Cost: 2 lines.**
5. **`IStarSystem.global_location -> HexCoord`** (`strategy_entities.py:29`): Narrow from Any. **Cost: 1 line.**
6. **`IEmpire.color -> tuple[int, int, int]`** (`strategy_domain.py:30`): Narrow from Any. **Cost: 1 line.**

### Priority 2 — StrategyScreen/Renderer Property Narrowing (high UI impact)
7. **StrategyScreen properties** (`strategy_screen.py:163-210`): 10 properties returning `-> Any`. Narrow `galaxy`, `empires`, `systems`, `active_empire`, `enemy_empire`, `facade`, `input_mode`, `current_empire`, `human_player_ids` to their concrete types. **Cost: ~20 lines, affects 100+ downstream call sites.**
8. **StrategyRenderer properties** (`strategy_renderer.py:109-241`): ~10 properties returning `-> Any`. Same narrowing. **Cost: ~20 lines.**
9. **FleetOperations/CameraNavigator/ColonizationSystem/SuperweaponOperations** delegate properties: ~15 properties returning `-> Any`. **Cost: ~30 lines.**

### Priority 3 — AI Adapter Narrowing
10. **ShipControllableAdapter** (`controllable.py:258-392`): 18 methods returning `-> Any` from concrete Ship properties. Replace with actual types: `get_position() -> Vector2`, `get_velocity() -> Vector2`, `get_rotation() -> float`, etc. **Cost: ~18 lines, resolves 15 mypy errors.**
11. **IControllable abstract methods** (`controllable.py:41-46`): Narrow `get_position`, `get_velocity` protocol signatures. **Cost: 2 lines.**

### Priority 4 — Simulation Layer Narrowing
12. **Formula evaluation chain:** `_eval_node() -> int | float` in `formula_evaluator.py:81`. This resolves ~30 `no-any-return` cascades in abilities (planetary.py, weapons.py, harvester.py, etc.). **Cost: 1 line + verifying all return paths.**
13. **ShipPhysicsMixin Protocol:** Define a Protocol for what mixin expects from `self` (position, angle, mass, etc.). Resolves 15 `attr-defined` errors in `ship_physics.py`. **Cost: ~20 lines (new Protocol class).**

### Priority 5 — Strategy Internals
14. **SimulationBattleResolver._build_capture_context**: `-> dict[str, Any]` (line 334). **Cost: 1 line.**
15. **System blueprints / galaxy layouts / astrophysics loaders**: 8 `no-any-return` in JSON loading helpers. Add explicit `-> dict[str, Any]` | `-> str` annotations. **Cost: ~8 lines.**
16. **OrderSerializer._deserialize_target**: `-> HexCoord | str | None`. **Cost: 1 line.**

### Total Estimated Cost
| Priority | Lines of Change | Mypy Errors Resolved | Downstream Impact |
|----------|----------------|---------------------|-------------------|
| P1 (Protocol Any) | ~15 lines | ~15 direct + ~50 cascade | HIGH |
| P2 (UI properties) | ~70 lines | ~60 direct + ~100 cascade | HIGH |
| P3 (AI adapter) | ~20 lines | ~15 direct | MEDIUM |
| P4 (Simulation) | ~25 lines | ~45 direct | HIGH |
| P5 (Strategy internals) | ~10 lines | ~10 direct | LOW |
| **Total** | **~140 lines** | **~145 direct + ~150 cascade** | — |

---

## Appendix: Unavoidable Any Boundaries

These Any usages are architecturally justified and should NOT be changed:

1. **`json_utils.load_json() -> Any`** — Dynamic JSON deserialization. Unavoidable.
2. **`IOrderable.orders -> List[Any]`** — The Order class lives in Strategy; Core can't import it. Accept as irreducible seam.
3. **`IResourceHolder.resources -> Any`** — ResourceRegistry is simulation-level; explicitly documented as avoiding cross-layer import.
4. **`IScene.handle_event(event: Any)`** — Pygame event type; Core can't import pygame.
5. **`IScene.draw(screen: Any)`** — Pygame Surface type; same constraint.
6. **Game scene routing (`app.py:184-237`)** — Scene objects stored in a dict with string keys; unavoidable dict lookup pattern.
7. **UI `pygame_gui` callbacks** — Third-party library conventions.
8. **`RegistryManager.get_validator() -> Any`** + `get_validator() -> Any` (top-level) — Registry pattern where validators are type-parameterized generics.
9. **`ScreenStateMachine.state -> Any`** + `pop_and_return -> Any` — State pattern with heterogeneous state types.
