# PROJ-372: Design — Galaxy/Planet/Star God-Class Decomposition

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md` item #5 — Galaxy/Star/Planet God-Classes (2,126 LOC total). Quoted impact statements:
- "Tests must construct full graphs; can't stub query layer."
- "Planet.get_habitability_multiplier() hardcoded; mod by patching at runtime."
- "Modders can't inject custom habitability calculators."

PROJ-86/87/88/89 (deep_archive/PROJ-051-100/) decomposed adjacent god classes (UI screens, ShipInstance, Fleet, GameSession, Ship, Component) and **explicitly listed Galaxy/Planet/Star as Out-of-scope** — those projects ended without touching them. PROJ-372 closes that gap; it does NOT supersede the four predecessors.

---

## Initial Analysis: per-class method tables

### Galaxy (`game/strategy/data/galaxy.py:176-689`, 514 LOC of class body, 31 methods)

The file also contains `WarpPoint` (`:34-80`, 47 LOC, 3 methods) and `StarSystem` (`:82-174`, 93 LOC, 6 methods + 1 property) — both small, focused, **kept in place**.

Inventory of `Galaxy` methods + categories:

| # | Method | LOC | Category | Notes |
|---|--------|----:|----------|-------|
| 1 | `__init__` | 46 | lifecycle | Wires 4 generators + 4 delegates; instantiates 9 indexes. Heavy — see Risk R5. |
| 2 | `add_system` | 8 | mutation | Calls `_register_zones_from_system` + `_rebuild_warp_point_index`. |
| 3 | `_register_zones_from_system` | 12 | mutation | PROJ-204 dedup. |
| 4 | `_rebuild_warp_point_index` | 12 | mutation | PROJ-204 dedup. |
| 5 | `_rebuild_all_warp_point_indices` | 9 | mutation | Bulk rebuild after warp gen. |
| 6 | `get_system_by_name` | 1 | query | Trivial dict lookup. |
| 7 | `get_system_of_object` | 1 | facade | Delegates to `_spatial`. |
| 8 | `register_planet` | 1 | facade | Delegates to `_registry`. |
| 9 | `get_planet_by_id` | 1 | facade | Delegates to `_registry`. |
| 10 | `get_system_of_planet` | 1 | facade | Delegates to `_spatial`. |
| 11 | `get_planets_at_global_hex` | 1 | facade | Delegates to `_spatial`. |
| 12 | `get_planet_global_hex` | 1 | facade | Delegates to `_spatial`. |
| 13 | `register_zone` | 1 | facade | Delegates to `_registry`. |
| 14 | `unregister_zone` | 1 | facade | Delegates to `_registry`. |
| 15 | `get_zones_at_global_hex` | 1 | facade | Delegates to `_spatial`. |
| 16 | `get_next_fleet_id` | 4 | mutation | ID counter — should live on state. |
| 17 | `register_fleet` | 1 | facade | Delegates to `_registry`. |
| 18 | `unregister_fleet` | 1 | facade | Delegates to `_registry`. |
| 19 | `get_fleet_by_id` | 1 | facade | Delegates to `_registry`. |
| 20 | `unregister_planet` | 1 | facade | Delegates to `_registry`. |
| 21 | `remove_warp_link` | 27 | logic | Two-system warp removal — should move to a `WarpLinkService` or `_warp_gen`. |
| 22 | `get_system_at_location` | 1 | facade | Delegates to `_spatial`. |
| 23 | `get_all_fleets_in_system` | 1 | facade | Delegates to `_spatial`. |
| 24 | `generate_planets` | 1 | facade | Delegates to `_sys_gen`. |
| 25 | `generate_systems` | 4 | facade | Delegates to `_sys_gen`. |
| 26 | `create_vars_link` (sic, typo) | 19 | mixed | Calls `_warp_gen.create_warp_link` BUT also rebuilds warp indexes inline. Should be in `_warp_gen` + service callback. |
| 27 | `generate_warp_lanes` | 9 | mixed | Calls `_warp_gen.generate_warp_lanes` + `_rebuild_all_warp_point_indices`. |
| 28 | `to_dict` | 13 | serde | Stays. |
| 29 | `from_dict` (cls) | 51 | serde | Stays — but `restore_planet` per-planet loop is the right shape. |

**Counts:** 4 lifecycle/serde, 1 trivial query, 16 1-line facades, 8 logic-bearing or mutation methods. **The facade pattern is 50% in place.** Closing the gap means moving methods 3–5, 16, 21, 26, 27 onto services and routing them through 1-line wrappers.

### Planet (`game/strategy/data/planet.py:44-624`, 580 LOC of class body, 20 methods + 5 @property + 47 dataclass fields)

| # | Method | LOC | Category | Notes |
|---|--------|----:|----------|-------|
| 1 | `__eq__` | 8 | identity | Stays. |
| 2 | `__hash__` | 1 | identity | Stays. |
| 3 | `active_abilities` (@property) | 9 | query/calc | Scans facility component_states. → `PlanetQueryService`. |
| 4 | `is_ability_active` | 1 | query | Reads `active_abilities`. → 1-line facade. |
| 5 | `occupied_hexes` (@property) | 4 | calc | Calls `hex_circle_filled`. → `PlanetQueryService`. |
| 6 | `total_pressure_atm` (@property) | 2 | calc | `sum(self.atmosphere.values()) / 101325`. → `PlanetQueryService` or stay (trivial). |
| 7 | `max_population` (@property) | 1 | calc | Trivial formula. → stay (single expression). |
| 8 | `total_population` (@property) | 1 | calc | `sum(p.count for p in self.populations)`. → stay. |
| 9 | `has_space_shipyard` (@property) | 1 | query | `any(f.is_shipyard for f in self.facilities)`. → stay (1-line). |
| 10 | `get_cached_habitability_multiplier` | 17 | calc + cache | **The hot one** — late-imports `planet_habitability_multiplier` from `colony_output`. **Becomes a 1-line facade** to `PlanetHabitabilityService.get_cached(planet, race_registry, turn)`. The transient cache fields stay on the dataclass (saving the cache itself per `planet.py:152-161`). |
| 11 | `get_species_config` | 4 | mutation | Lazy-creates `ColonySpeciesConfig`. → stay (trivial, not enough logic to extract). |
| 12 | `context_type` (@property) | 1 | identity | `return "planet"`. Stays. |
| 13 | `add_to_stockpile` | 8 | mutation | Cap-aware add. → stay (small) but conform to `IStockpileHolder` protocol (Phase 2). |
| 14 | `consume_from_stockpile` | 5 | mutation | Stay; conform to protocol. |
| 15 | `has_stockpile` | 4 | query | Stay; conform to protocol. |
| 16 | `get_stockpile` | 1 | query | Stay; conform to protocol. |
| 17 | `get_staging_mass` | 1 | query | Stay; conform to `IStagingYardHolder` protocol. |
| 18 | `add_to_staging_yard` | 5 | mutation | Stay; conform to protocol. |
| 19 | `remove_from_staging_yard` | 4 | mutation | Stay; conform to protocol. |
| 20 | `can_build_type` | 9 | query | Mostly logic — switch on `vehicle_type.lower()`. → `PlanetQueryService.can_build_type(planet, vehicle_type)`. |
| 21 | `get_current_order` | 1 | query | Stay (PROJ-238 IOrderable contract). |
| 22 | `pop_order` | 1 | mutation | Stay. |
| 23 | `add_order` | 5 | mutation | Stay. |
| 24 | `clear_orders` | 1 | mutation | Stay. |
| 25 | `add_production` | 7 | mutation | Stay (PROJ-238). |
| 26 | `to_dict` | 60 | serde | Stays — but the function-level helper `_deserialize_planet_orders` at `:626-667` is the right shape. |
| 27 | `from_dict` (cls) | 119 | serde | Stays — heavy because of all 47 fields. |

**Counts:** 4 identity, 8 calc/query (5 stay 1-line, 3 move), 11 mutation (stay; protocol-shaped), 2 serde. **Removing the 3 logic-bearing query methods (`active_abilities`, `occupied_hexes`, `can_build_type`) and routing `get_cached_habitability_multiplier` through a service drops `planet.py` by ~40 LOC; preserving but reformatting `from_dict` to use shared helpers from PROJ-251 saves another ~50.** Target ≤ 350 is achievable.

### Star (`game/strategy/data/stars.py`, 770 LOC total)

The file mixes:

| Region | Lines | LOC | Content |
|--------|------:|----:|---------|
| Constants | 14-49 | 35 | Solar refs, Kelvin/Wien constants, `_WAVELENGTHS` dict, hex radius coeffs |
| `class StarType(Enum)` | 51-59 | 9 | 8 enum values |
| `@dataclass class Spectrum` | 61-130 | 70 | 9 fields + `get_total_output` + serde |
| `@dataclass class Star` | 132-251 | 120 | 13 fields + `occupied_hexes` (4 LOC) + serde |
| `class StarGenerator` | 253-770 | 517 | `_generate_mass`, `_determine_type_and_radius`, `_compute_stefan_boltzmann_type`, `_roll_star_type`, `_kelvin_to_rgb`, `_map_solar_radius_to_hex_radius`, `_generate_spectrum`, `generate_system_stars`, `_generate_companions`, `generate_from_blueprint`, `_generate_random_stars`, `_generate_mass_constrained` (12 methods) |

**Inventory of `StarGenerator` methods + categories:**

| # | Method | LOC | Category |
|---|--------|----:|----------|
| 1 | `__init__` | 7 | lifecycle |
| 2 | `_get_image_id` | 6 | helper |
| 3 | `_generate_mass` | 25 | gen |
| 4 | `_determine_type_and_radius` | 58 | gen + math |
| 5 | `_compute_stefan_boltzmann_type` | 47 | gen + math |
| 6 | `_roll_star_type` | 11 | gen |
| 7 | `_kelvin_to_rgb` | 38 | **pure math** — belongs in `core/spectrum_math.py` |
| 8 | `_map_solar_radius_to_hex_radius` | 24 | **pure math** — could move to `core/spectrum_math.py` (knows about hex radius enum) |
| 9 | `_generate_spectrum` | 35 | gen + math (Wien's law) |
| 10 | `generate_system_stars` | 14 | public API |
| 11 | `_generate_companions` | 67 | gen |
| 12 | `generate_from_blueprint` | 80 | gen |
| 13 | `_generate_random_stars` | 50 | gen |
| 14 | `_generate_mass_constrained` | 23 | gen |

**Reorganization:**
- Move `Spectrum` to `game/strategy/data/spectrum.py` (≤ 80 LOC).
- Move `_kelvin_to_rgb` + Wien's law constants + `_map_solar_radius_to_hex_radius` (debatable — see Decision D6) + `_WAVELENGTHS` to `game/core/spectrum_math.py` (≤ 200 LOC).
- Move `StarGenerator` to `game/strategy/generation/star_generator.py` (≤ 500 LOC).
- `stars.py` shrinks to: constants used ONLY by `Star.from_dict` validation + `StarType` enum + `Star` dataclass + serde = ~250-280 LOC.

External readers of `Star` properties (67 occurrences across 15 files, per `\.luminosity|\.spectrum|\.temperature|\.star_type|\.intrinsic_abilities` grep): mostly UI (`star_list_window`, `star_list_filters`, `strategy_detail_fmt`, `strategy_panel_manager`, `strategy_render`, `galaxy_test/system_mode`) plus `system_dto.py`. All read the dataclass fields directly. **Preserve all 13 fields verbatim**; only move helper math.

---

## External reader inventory (load-bearing for facade design)

| Surface | External readers | Implication |
|---------|-----------------|-------------|
| `galaxy.systems` (dict[HexCoord, StarSystem]) | 19 files, 45 occurrences | Must remain accessible — keep as a property forwarding to `state.systems`, NOT remove. |
| `galaxy.name_map` (dict[str, StarSystem]) | within galaxy.py, pathfinding.py | Property forwarding to `state.name_map`. |
| `galaxy.planets_by_id`, `fleets_by_id` | 4 files | Property forwarding. |
| `planet.populations`, `planet.facilities`, `planet.stockpile`, `planet.deposits` | 20 files, 57 occurrences | Cannot wrap; PROJ-370 will replace direct access with protocols. PROJ-372 leaves them as direct dataclass field access. |
| `planet.atmosphere`, `planet.energy`, `planet.species_configs` | included above | Same. |
| `star.luminosity`, `star.spectrum`, `star.temperature`, `star.star_type`, `star.intrinsic_abilities` | 15 files, 67 occurrences | Direct dataclass access — preserve verbatim. |

The facade rule: anywhere external code reads a public attribute today, the post-decomposition class **must still expose it** at the same name (as a `@property` or as a forwarded dataclass field, no behavior change).

---

## Current vs. target architecture

**Current state ownership** (today, on `Galaxy`):

```
Galaxy attributes:
  systems: dict[HexCoord, StarSystem]     ← read by 19 files
  name_map: dict[str, StarSystem]
  planets_by_id: dict[int, Planet]
  fleets_by_id: dict[int, Fleet]
  _planet_to_system: dict[Planet, StarSystem]
  _global_hex_planets: dict[HexCoord, list[Planet]]
  _global_hex_zones: dict[HexCoord, list]
  _zone_to_system: dict[id, StarSystem]
  _global_hex_warp_points: dict[HexCoord, StarSystem]
  _next_planet_id: int
  _next_fleet_id: int
  radius: int
  naming, star_image_registry, image_registry, planet_generator, star_generator,
  storm_generator, _warp_gen, _sys_gen, _registry, _spatial: services/registries
```

**Target state ownership** (after PROJ-372):

```python
# game/strategy/data/galaxy_state.py  (new, ≤ 150 LOC)
@dataclass
class GalaxyState:
    radius: int
    systems: dict[HexCoord, StarSystem] = field(default_factory=dict)
    name_map: dict[str, StarSystem] = field(default_factory=dict)
    planets_by_id: dict[int, Planet] = field(default_factory=dict)
    fleets_by_id: dict[int, Fleet] = field(default_factory=dict)
    planet_to_system: dict[Planet, StarSystem] = field(default_factory=dict)   # was _planet_to_system
    global_hex_planets: dict[HexCoord, list[Planet]] = field(default_factory=dict)
    global_hex_zones: dict[HexCoord, list] = field(default_factory=dict)
    zone_to_system: dict[int, StarSystem] = field(default_factory=dict)
    global_hex_warp_points: dict[HexCoord, StarSystem] = field(default_factory=dict)
    next_planet_id: int = 1
    next_fleet_id: int = 1
```

```python
# game/strategy/data/galaxy.py  (≤ 350 LOC)
class Galaxy:
    """Facade. All algorithmic / spatial / generation logic delegates."""
    def __init__(self, radius: int = 100):
        self._state = GalaxyState(radius=radius)
        # Generators (data-loaded; share the registries)
        self.naming = NameRegistry(...)
        self.star_image_registry = StarImageRegistry()
        self.star_generator = StarGenerator(image_registry=self.star_image_registry)
        # ... (unchanged constructor body, just stores into _state instead of self)
        # Services
        self._registry = GalaxyEntityRegistry(self._state)
        self._spatial = GalaxySpatialIndex(self._state)
        self._warp_gen = GalaxyWarpGenerator()
        self._sys_gen = GalaxySystemGenerator(...)
        self._pathfinder = GalaxyPathfindingService(self._spatial, self._state)

    # 1-line attribute forwarders (preserves external API):
    @property
    def systems(self): return self._state.systems
    @property
    def name_map(self): return self._state.name_map
    # ... etc

    # 1-line method facades (every previous method becomes one of these):
    def add_system(self, system): return self._registry.add_system(system)
    def remove_warp_link(self, a, b): return self._warp_gen.remove_warp_link(self._state, a, b)
    def generate_warp_lanes(self, **kw): return self._warp_gen.generate_warp_lanes(self._state, **kw)
    def to_dict(self): return GalaxySerializer.to_dict(self._state)
    @classmethod
    def from_dict(cls, data): galaxy = cls(...); GalaxySerializer.populate(galaxy, data); return galaxy
```

**Planet target:**

```python
# game/strategy/data/planet.py  (≤ 350 LOC)
@dataclass
class Planet:
    # 47 fields unchanged ↓ (preserve save format exactly)
    name: str; location: HexCoord; orbit_distance: int; ...

    # Identity / dataclass plumbing stays
    def __eq__(self, other): ...
    def __hash__(self): ...

    # Thin facades — delegate to services
    @property
    def active_abilities(self): return PlanetQueryService.active_abilities(self)
    def is_ability_active(self, key): return PlanetQueryService.is_ability_active(self, key)
    @property
    def occupied_hexes(self): return PlanetQueryService.occupied_hexes(self)
    def can_build_type(self, vt): return PlanetQueryService.can_build_type(self, vt)
    def get_cached_habitability_multiplier(self, race_registry, turn):
        from game.context import get_default_planet_habitability_service
        return get_default_planet_habitability_service().get_cached(self, race_registry, turn)

    # Stockpile / staging / orders stay (trivial — < 10 LOC each)
    # Serde stays
```

`Planet.get_cached_habitability_multiplier` keeps its existing transient cache fields (`_cached_habitability_multiplier`, `_cached_multiplier_turn`); the service reads/writes them. Modders inject by setting `set_default_planet_habitability_service(MyService())` before galaxy init.

**Star target:**

```python
# game/strategy/data/stars.py  (≤ 280 LOC)
class StarType(Enum): ...    # 8 values

@dataclass
class Star:
    # 13 fields unchanged
    @property
    def occupied_hexes(self): return hex_circle_filled(self.location, max(0, self.radius_hexes - 1))
    def to_dict(self): ...
    @classmethod
    def from_dict(cls, data): ...

# game/strategy/data/spectrum.py  (≤ 80 LOC)  [new]
@dataclass
class Spectrum:
    # 9 fields + get_total_output + to_dict + from_dict

# game/strategy/generation/star_generator.py  (≤ 500 LOC)  [moved]
class StarGenerator:
    # All 14 methods relocated; uses spectrum_math helpers

# game/core/spectrum_math.py  (≤ 200 LOC)  [moved]
def kelvin_to_rgb(temp_k: float) -> tuple[int, int, int]: ...
def stefan_boltzmann_luminosity(radius_solar: float, temp_k: float) -> float: ...
def wien_peak_wavelength(temp_k: float) -> float: ...
SOLAR_TEMP_K = 5778
SOLAR_LUMINOSITY_W = 3.828e26
# etc — all `_KELVIN_*` / `WIEN_*` constants
```

---

## Per-class extraction map

### Galaxy → 6 services + 1 state object

1. **`GalaxyState`** (new, `galaxy_state.py`, ≤ 150 LOC) — owns the 11 mutable indexes + 2 ID counters + radius.
2. **`GalaxyEntityRegistry`** (existing at `galaxy_entity_registry.py:188`) — refactor to take `GalaxyState` not `Galaxy`. Receives method 16 `get_next_fleet_id` (move from Galaxy).
3. **`GalaxySpatialIndex`** (existing at `galaxy_spatial_index.py:192`) — refactor to take `GalaxyState`. Receives methods 3, 4, 5 (zone registration / warp index rebuild).
4. **`GalaxyWarpGenerator`** (existing at `galaxy_warp_generator.py:421`) — receives method 21 `remove_warp_link` and the post-create-link warp-point indexing currently inline in method 26.
5. **`GalaxySystemGenerator`** (existing at `galaxy_system_generator.py:354`) — no significant churn (already focused).
6. **`GalaxyPathfindingService`** (new, `services/galaxy_pathfinding_service.py`, ≤ 350 LOC) — owns the 5 module-level functions in `pathfinding.py:51-296`: `find_path_deep_space`, `find_path_interstellar`, `find_hybrid_path`, `find_nearest_system`, `get_system_at_hex`, plus `strip_start_hex`. Accepts `IGalaxySystemGraph` protocol.
7. **`InterceptCalculator`** (new, `services/intercept_calculator.py`, ≤ 150 LOC) — owns `pathfinding.py:297-503`: `project_fleet_path`, `calculate_intercept_point`, `_evaluate_intercept_candidates`, `_extract_chaser_info`, `_ChaserProxy`, `_ChaserProxyCapabilities`. Holds a `GalaxyPathfindingService` reference.

### Planet → 2 services + protocol-conforming dataclass

1. **`PlanetQueryService`** (new, `services/planet_query_service.py`, ≤ 250 LOC) — owns: `active_abilities` derivation, `is_ability_active`, `occupied_hexes`, `can_build_type`, optionally `total_pressure_atm`. Pure functions taking a `Planet` (no instantiation needed, but a class for future-proofing).
2. **`PlanetHabitabilityService`** (new, `services/planet_habitability_service.py`, ≤ 200 LOC) — implements `IHabitabilityCalculator`. Wraps `planet_habitability_multiplier` from `colony_output.py`, manages the per-turn cache on `Planet._cached_habitability_multiplier`. Injectable via `ApplicationContext`.
3. **Protocols** — `IStockpileHolder`, `IStagingYardHolder` exposed for tests / mods that want to mock planet stockpiles. `Planet` satisfies them structurally; existing methods stay.

### Star / stars.py → 4 destination files

1. **`game/strategy/data/stars.py`** — `StarType` enum + `Star` dataclass + serde. Target ≤ 280 LOC.
2. **`game/strategy/data/spectrum.py`** (new) — `Spectrum` dataclass + serde. Target ≤ 80 LOC.
3. **`game/strategy/generation/star_generator.py`** (relocated) — `StarGenerator` class. Target ≤ 500 LOC.
4. **`game/core/spectrum_math.py`** (new in `core/`) — `kelvin_to_rgb`, Wien's law helpers, Stefan-Boltzmann helpers, all `_KELVIN_*` and `WIEN_*` constants, `_WAVELENGTHS`. Target ≤ 200 LOC.

The reason `spectrum_math` lives in `core/` not `strategy/`: the Tanner Helland Kelvin→RGB algorithm and Wien's displacement law are pure math with zero domain knowledge — exactly what `core/` is for (per `docs/01_ARCHITECTURE.md` layer rules; mirrors PROJ-257 placement of `FormulaEvaluator` in `core/`).

---

## Alternatives considered

### A. Leave as-is
- Pro: zero churn.
- Con: Tests still need 100-system universes; habitability still un-swappable; `stars.py` still 770 LOC. The review report ranked this #5 on the strategy tech-debt list — leaving it bumps the next planning cycle straight back here.
- **Rejected.**

### B. Partial extraction — habitability service only
- Pro: smallest possible scope; closes the user-visible "modders can't inject" complaint.
- Con: doesn't reduce LOC ceilings; doesn't fix pathfinding test pain; doesn't break the `_galaxy: Galaxy` back-reference on the four existing delegates. Half a refactor.
- **Rejected** — the goal is closing the god-class status, not just the highest-friction surface.

### C. Full split into separate packages (`game/strategy/galaxy/`, `game/strategy/planet/`, `game/strategy/star/`)
- Pro: maximal separation; obvious physical boundary.
- Con: 80+ files to relocate; every external import in 19 + 20 + 15 = 54 reader files breaks. Massive churn for marginal architectural benefit. Existing layout is already by-system enough.
- **Rejected** — the facade pattern preserves the existing import surface.

### D. Dataclass-only models with services everywhere (true ECS)
- Pro: fully decoupled; tests trivial; modders inject anything.
- Con: 100+ external readers that today call `planet.has_space_shipyard` or `galaxy.add_system(...)` would need to switch to `query_service.has_space_shipyard(planet)` / `entity_registry.add_system(state, system)`. 200+ call-site changes; semantic break with the `Galaxy.systems` attribute. Same blast as C.
- **Rejected** — facade pattern keeps the existing call-site surface.

### E. Move `StarSystem` and `WarpPoint` to their own files
- Pro: cleanest possible `galaxy.py`.
- Con: 7 files import from `galaxy.py` for `StarSystem` (verified via grep). Splitting them adds churn for ~150 LOC of saving.
- **Deferred** — phase 3 implementer decides based on whether `galaxy.py` is fitting under ≤ 350 LOC after services are extracted.

### F. Move `StarGenerator` to `services/` instead of `generation/`
- Pro: matches `services/` neighborhood for other "does work" classes.
- Con: `StarGenerator` is a generator, and `game/strategy/generation/` already exists with `placement_strategies.py`, `region_classifier.py`, `planet_image_registry.py`, `star_image_registry.py`, `storm_generator.py`. Putting the star generator there matches established convention.
- **Rejected** — `generation/` is the right home.

### G. Make `_kelvin_to_rgb` stay in `stars.py` (don't move to `core/`)
- Pro: smaller change.
- Con: it's pure math, used only at star generation time, and the `_KELVIN_*` constants take 30 LOC by themselves. Architecturally `core/` is correct.
- **Rejected** — move to `core/spectrum_math.py`.

### H. Skip the `GalaxyState` dataclass; keep state on `Galaxy`
- Pro: smaller change.
- Con: each delegate still holds `_galaxy: Galaxy` back-reference, which forces the `if TYPE_CHECKING: from galaxy import Galaxy` dance in 4 files (verified) and makes unit-testing a delegate require constructing a real `Galaxy()` (which loads naming registries from disk). `GalaxyState` is a 5-minute extraction that pays for itself in test cleanliness.
- **Rejected** — `GalaxyState` is mandatory.

### I. Run after PROJ-370 (data boundary protocols)
- Pro: PROJ-370 defines the strategy mutator surface first; PROJ-372's protocol extractions land on top of a stable mutation contract.
- Con: PROJ-370's wiring rewrite must complete before any PROJ-372 work can claim a stable target.
- **Accepted (resolved 2026-05-06 Codex+Claude joint review)** — PROJ-370 first; all of PROJ-372 follows. PROJ-372 Phase 0 creates `game/strategy/data/galaxy_protocols.py` (`IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`, `IGalaxySystemGraph`, `IGalaxySpatialQuery`) and modifies `game/context.py` habitability accessors — those are exactly the contract surfaces PROJ-370 should own. Splitting Phase 0 to enable Star (Phase 1) parallelism with PROJ-370 was rejected as marginal benefit.

---

## Risks

- **R1: Save format drift.** `Planet.from_dict` validates 47 fields; missing one breaks saves. Mitigation: Phase 5 tests include a "load 5 fixture saves" round-trip equality check (`to_dict() == loaded.to_dict()`); Phase 0 captures the baseline.
- **R2: Pickle stability for `_cached_habitability_multiplier`.** PROJ-285 added two transient fields with `init=False, repr=False, compare=False`. The dataclass `from_dict` doesn't pass them, so they default. **Verified safe** — any future service relocation must preserve `init=False`.
- **R3: Perf regression from indirection.** Galaxy spatial queries are O(1) dict lookups today; adding `_state.global_hex_planets` instead of `_global_hex_planets` is one extra attribute access per call. Worst case: 1000 `get_system_at_location` per turn × 1.5x cost = negligible. Mitigation: Phase 0 captures baseline; Phase 5 reasserts within ±5%.
- **R4: Hidden state on `Planet`.** Two cached transient fields (`_cached_habitability_multiplier`, `_cached_multiplier_turn`) are mutated by `get_cached_habitability_multiplier`. Moving the logic to a service requires passing the planet by reference and mutating these fields **on the planet** — same as today. Mitigation: service holds no cache state of its own; cache lives where it always has.
- **R5: `Galaxy.__init__` is heavy** (loads JSON, instantiates 4 generators, 4 services). Tests that construct `Galaxy()` pay this cost. Mitigation: PROJ-372 doesn't change this in scope; future work could add a `Galaxy.empty()` factory that lazy-loads, but that's out of scope. Document, don't fix.
- **R6: AI / UI callers reach into `galaxy.systems[loc]` directly.** Verified in 19 files. Keeping `systems` as a `@property` returning `_state.systems` preserves the surface. Mitigation: facade-pattern strict adherence; AST guard in Phase 5.
- **R7: PROJ-285 cache invariants.** `_cached_multiplier_turn != turn` is the only invalidation. If turn order changes between test setup and test assertion, the cache may stick. Mitigation: existing pattern, not introducing new bugs.
- **R8: Scope creep.** Splitting Planet protocols (R-stockpile, R-staging) is tempting but the contract testing is PROJ-370's job. PROJ-372 only **defines** protocols and asserts `Planet` satisfies them structurally; it does NOT add invariant checks (capacity ≥ 0 etc.) — that's PROJ-370.
- **R9: External tests over-mocking.** Existing tests mock `galaxy.systems` directly (verified 33 occurrences in `tests/`). The `@property` on Galaxy facade cannot be mocked the same way as a plain attribute. Mitigation: in Phase 0, sweep test files; convert any `mock.systems = {...}` to `mock._state.systems = {...}`. Most tests use real `Galaxy()` constructors (32 of 33 occurrences are in test_*.py files reading galaxy.systems, not mocking it).
- **R10: Circular imports.** `Planet.get_cached_habitability_multiplier` already late-imports to dodge `planet.py ← colony_output.py ← habitability.py` (per `planet.py:257-258`). Moving to a service in `services/` either preserves the late import or restructures imports. Mitigation: place `PlanetHabitabilityService` in `services/` (already a leaf for circular purposes — verified by `Empire`, `Fleet`, etc. using `services/` without circularity).

---

## Dependencies

- **PROJ-370 (Strategy: Data Layer Boundary Protocols)** — has a five-phase mutator plan (Fleet, Planet, Empire, ShipInstance, plus foundation). Sequencing **resolved 2026-05-06 (Codex+Claude joint review): PROJ-370 first; all of PROJ-372 follows.** PROJ-372 Phase 0 creates `game/strategy/data/galaxy_protocols.py` (`IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`, `IGalaxySystemGraph`, `IGalaxySpatialQuery`) and modifies `game/context.py` habitability accessors that PROJ-370 must define first.
- **PROJ-86/87/88/89** — predecessors, all complete and archived in `Projects/deep_archive/PROJ-051-100/`. Each scoped god-class decomposition to specific classes that did NOT include Galaxy/Planet/Star (verified in their plan.md "Out:" sections). PROJ-372 is **not superseding** them; it's the bounded follow-up for the three classes they deliberately deferred.
- **PROJ-173 Phase 2** — created `galaxy_entity_registry.py`, `galaxy_spatial_index.py`, `galaxy_warp_generator.py`, `galaxy_system_generator.py`. PROJ-372 builds on this; the four files are kept and refactored in place to take `GalaxyState` instead of `Galaxy`.
- **PROJ-210** — extracted `PlanetaryFacility` and `SpeciesPopulation` from `Planet`. PROJ-372 preserves these.
- **PROJ-285** — added per-turn habitability cache. PROJ-372 preserves the cache fields and routes the calculation through a service.
- **PROJ-258 (DI Migration)** — pattern for `ApplicationContext` access. PROJ-372 follows exactly: `get_default_planet_habitability_service()` / `set_default_planet_habitability_service(svc)`.

---

## Open questions

1. **Q1: Sequencing relative to PROJ-370.** Should PROJ-372 wait for PROJ-370 to complete its planning, then consume PROJ-370's protocols? Or run independently first and ship its own protocols? **Recommendation: independent, PROJ-372 first.** PROJ-370 currently has no plan body. PROJ-372's protocols are useful inputs to PROJ-370.

   **Resolved 2026-05-06 (Codex+Claude joint review):** PROJ-370 first. All of PROJ-372 follows. Phase 0 creates Planet/Galaxy protocol surfaces (`IHabitabilityCalculator`, `IStockpileHolder`, `IStagingYardHolder`, `IGalaxySystemGraph`, `IGalaxySpatialQuery`) and `game/context.py` habitability accessors that are PROJ-370's contract space; splitting Phase 0 to enable Star parallelism was rejected as marginal benefit.
2. **Q2: Move `StarSystem` and `WarpPoint` to their own file?** Saves ~150 LOC from `galaxy.py` if needed. **Recommendation: defer to Phase 3 implementer based on actual LOC budget.**
3. **Q3: Should `GalaxyState` be frozen / immutable in any way?** Today the indexes are mutated freely. Making `GalaxyState` a `@dataclass` with mutable fields is consistent with PROJ-371 (`StatAccumulator`). Any consideration of frozen-ness is PROJ-370's territory.
4. **Q4: Should `_kelvin_to_rgb` move to `core/spectrum_math.py` or stay in `generation/star_generator.py`?** The function is pure math; `core/` is the architectural home. **Recommendation: move to `core/`** (Decision D6).
5. **Q5: `_map_solar_radius_to_hex_radius` — `core/` or `generation/`?** It maps solar radius to a hex radius (1-6) using thresholds. Hex-radius is a game-domain concept (multi-hex zones); solar radius is physics. Borderline. **Recommendation: keep in `generation/star_generator.py` as a private helper** — it encodes a game design choice (compact remnants → 1, supergiant → 6), not pure math.
6. **Q6: AST-guard test technology.** Use `radon` (already added in PROJ-297) or a custom AST walker? **Recommendation: custom AST walker for this specific check** (LOC + non-facade-method-body-LOC); `radon` is for cyclomatic complexity, not what we want here.
7. **Q7: Do we relocate `pathfinding.py`'s function-level shims (`strip_start_hex`, `find_path_deep_space`, `find_path_interstellar`, `find_hybrid_path`, `project_fleet_path`, `calculate_intercept_point`, `find_nearest_system`, `get_system_at_hex`) or only re-implement them inside services?** **Recommendation: keep 1-line wrappers in `pathfinding.py` (deprecated, marked for deletion), delete at Phase 5 close** — there are 82 call sites across 15 files, and a phased deprecation lets the migration happen in chunks.
8. **Q8: Naming — `PlanetQueryService` vs `PlanetQueries` vs `PlanetService`?** The codebase uses `*_service.py` for `services/` modules (verified — `planet_economy_projector.py`, `cargo_transfer_service.py`, etc.). **Recommendation: `planet_query_service.py` containing class `PlanetQueryService`** (matches `EmpireEconomyService`, `CargoTransferService`).
