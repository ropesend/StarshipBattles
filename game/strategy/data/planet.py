"""
Planet data class.

PROJ-372 Phase 2: query/calc methods (active_abilities, is_ability_active,
occupied_hexes, can_build_type) routed through `PlanetQueryService`;
habitability calculator made injectable via `ApplicationContext`.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Any
from typing import TYPE_CHECKING as _TC
from game.core.hex_math import HexCoord

if _TC:
    from game.strategy.data.order_types import Order
    from game.strategy.data.planetary_facility import PlanetaryFacility
    from game.strategy.data.species_population import SpeciesPopulation

# PROJ-284: per-colony per-species config (food allocation slider, etc.).
# Runtime dependency: dataclass field at line 107, return annotation at
# line 187, constructor call at line 190.
from game.strategy.data.colony_species_config import ColonySpeciesConfig

# PROJ-450 Phase 1: dict ↔ typed staging-yard helpers were lifted from
# ``game/strategy/engine/order_handlers/transfer_branches.py`` into this
# module so the conversion lives on the Planet boundary. The substrate
# stays ``List[Dict[str, Any]]`` for Phase 1; Phase 2 widens the type.
from game.strategy.data.bay_inventory import DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle, VALID_VEHICLE_TYPES


def _is_carried_vehicle_dict(item: Any) -> bool:
    """Return True iff ``item`` is a staging-yard dict shaped like a
    :class:`CarriedVehicle` (mine/fighter/satellite). PROJ-431 Phase 1d:
    explicit dict-shape probe that replaces the legacy runtime
    ``CarriedVehicle.from_any()`` discriminator at the staging-yard
    boundary, which still holds dicts.
    """
    if isinstance(item, CarriedVehicle):
        return True
    if not isinstance(item, dict):
        return False
    return str(item.get("vehicle_type", "")).lower() in VALID_VEHICLE_TYPES


def _pod_from_dict(item: Any) -> DropPod:
    """Promote a drop-pod-shaped dict to a typed :class:`DropPod`.

    Two shapes are supported:

    * Save-shape (Phase 2+): ``{design_id, design_data, mass,
      payload: {...}}`` — matches :meth:`DropPod.to_dict`. The
      ``payload`` value is used as-is.
    * Legacy flat shape (pre-Phase-2 staging-yard substrate, fixtures,
      direct dict callers): any other keys (``name``, ``vehicle_type``,
      ``owner_id`` etc.) land in :attr:`DropPod.payload`.
    """
    if isinstance(item, DropPod):
        return item
    if not isinstance(item, dict):
        return DropPod(design_id="", design_data={}, mass=0.0, payload={})
    if "payload" in item and isinstance(item["payload"], dict):
        return DropPod.from_dict(item)
    return DropPod(
        design_id=str(item.get("design_id", "")),
        design_data=dict(item.get("design_data", {})),
        mass=float(item.get("mass", 0.0)),
        payload={
            k: v for k, v in item.items()
            if k not in {"design_id", "design_data", "mass"}
        },
    )


def _staging_yard_carried_vehicle(item: Any) -> Optional[CarriedVehicle]:
    """Promote a staging-yard dict to a typed :class:`CarriedVehicle`
    when it is shaped like one. Returns ``None`` for drop-pod-shaped
    entries (which lack a recognised ``vehicle_type``).
    """
    if isinstance(item, CarriedVehicle):
        return item
    if not isinstance(item, dict):
        return None
    if str(item.get("vehicle_type", "")).lower() not in VALID_VEHICLE_TYPES:
        return None
    return CarriedVehicle.from_dict(item)

class PlanetType(Enum):
    """
    Broad classification of planetary bodies.
    Derived from physical properties.
    """
    CONTINENTAL = auto() # Earth-like
    ARID = auto()        # Desert
    PELAGIC = auto()     # Ocean World
    MAGMA = auto()       # Volcanic / Lava
    CRYOPLANET = auto()  # Ice Surface
    BARREN = auto()      # Rock / Scorched
    JOVIAN = auto()      # Gas Giant
    ICE_GIANT = auto()   # Uranus/Neptune type
    CHTHONIAN = auto()   # Stripped Giant Core
    ICE_DWARF = auto()   # Pluto type
    PLANETOID = auto()   # Ceres / Large Asteroid
    DYSON_SPHERE = auto()  # Artificial megastructure enclosing a star

@dataclass
class Planet:
    """Represents a planetary body (Planet or Moon). SI units throughout.

    47 dataclass fields preserved verbatim for save-format compatibility
    (PROJ-372 Risk R1). PROJ-285 transient cache fields use
    ``init=False, repr=False, compare=False`` and are NOT serialized.
    """
    # Required (no defaults)
    name: str
    location: HexCoord  # Local system coords
    orbit_distance: int  # Ring number
    # Physical
    mass: float  # kg
    radius: float  # meters
    surface_area: float  # m^2
    density: float  # kg/m^3
    surface_gravity: float  # m/s^2
    # Surface conditions
    surface_pressure: float  # Pa (1 atm = 101325 Pa)
    surface_temperature: float  # K
    surface_water: float  # 0.0 - 1.0 surface coverage fraction
    # Internal
    tectonic_activity: float  # 0.0 (dead) - 1.0 (volcanic)
    magnetic_field: float  # relative to Earth

    # Fields with defaults
    atmosphere: Dict[str, float] = field(default_factory=dict)  # gas -> partial pressure (Pa)
    planet_type: PlanetType = PlanetType.BARREN
    orbit_parent_name: Optional[str] = None
    owner_id: Optional[int] = None
    construction_queue: list = field(default_factory=list)
    # FEAT-17: when True, ProductionEngine skips this colony's planetary-yard
    # base queue. Currently-progressing item retains `resources_consumed`.
    construction_queue_paused: bool = False
    deposits: Dict[str, dict] = field(default_factory=dict)  # res_id -> {quantity, quality}

    # PROJ-436 Phase 4f: ``stockpile`` / ``max_stockpile`` / ``staging_yard``
    # are no longer dataclass fields. They survive as backward-compatible
    # ``@property`` accessors over the renamed private dataclass fields
    # below — preserving test infrastructure that pokes
    # ``planet.stockpile[rid] = v`` and write paths that mutate the
    # underlying dict / list in place. Production writers route through
    # ``IPlanetMutator`` (``set_stockpile_amount`` / ``set_max_stockpile``
    # / ``add_staging_item`` / ``pop_staging_item``) or through Planet's
    # own ``add_to_stockpile`` / ``consume_from_stockpile`` /
    # ``add_to_staging_yard`` / ``remove_from_staging_yard`` helpers.
    # The AST guards at
    # ``tests/static_guards/test_no_legacy_storage_fields.py`` pin the
    # absence of the dataclass field names. Per CLAUDE.md "no save-file
    # migration" rule the durable shape stays ``Dict[str, float]`` /
    # ``List[Dict[str, Any]]`` for now; the broader Container substrate
    # is the longer-arc goal addressed by Phases 5-9.
    _stockpile: Dict[str, float] = field(default_factory=dict)
    _max_stockpile: Dict[str, float] = field(default_factory=dict)
    # PROJ-450 Phase 2: substrate widened from ``List[Dict[str, Any]]``
    # to ``List[CarriedVehicle | DropPod]``. Save shape on disk stays
    # dict-shaped via per-entry ``.to_dict()`` in ``planet_to_dict``.
    _staging_yard: "List[CarriedVehicle | DropPod]" = field(default_factory=list)
    max_staging_mass: float = 0.0
    facilities: List['PlanetaryFacility'] = field(default_factory=list)
    populations: List['SpeciesPopulation'] = field(default_factory=list)
    id: int = -1  # -1 = unregistered with Galaxy
    image_id: str = ""
    image_rotation: float = 0.0
    radius_hexes: int = 0  # PROJ-139: > 0 = multi-hex object (Dyson Sphere)
    # PROJ-237: Energy
    energy: float = 0.0
    energy_capacity: float = 0.0
    energy_generation: float = 0.0
    atmosphere_target: Dict[str, float] = field(default_factory=dict)
    # Planet modifier targets — None = no modification active
    gravity_target: Optional[float] = None
    gravity_original: Optional[float] = None
    water_target: Optional[float] = None
    radiation_shielding: float = 0.0
    radiation_shielding_target: Optional[float] = None
    # PROJ-238: order queue (unified with Fleet.orders)
    orders: List['Order'] = field(default_factory=list)
    # PROJ-301: planet intrinsic abilities (rolled at galaxy gen).
    intrinsic_abilities: Dict[str, Any] = field(default_factory=dict)
    # PROJ-284: per-colony per-species sliders (food allocation etc.).
    species_configs: Dict[str, ColonySpeciesConfig] = field(default_factory=dict)
    # PROJ-285: per-turn cache. NOT serialized — populations shift across
    # save load; cache re-warms on the next turn's first read.
    _cached_habitability_multiplier: Optional[float] = field(
        default=None, init=False, repr=False, compare=False,
    )
    _cached_multiplier_turn: int = field(
        default=-1, init=False, repr=False, compare=False,
    )

    def __post_init__(self) -> None:
        # PROJ-450 Phase 2: when the dataclass is constructed with a
        # raw dict list (e.g. via ``Planet.from_dict`` -> serde, or via
        # direct kwarg construction in tests), promote each entry to
        # the typed substrate so the invariant
        # ``_staging_yard: List[CarriedVehicle | DropPod]`` holds.
        if self._staging_yard:
            normalised: list[CarriedVehicle | DropPod] = []
            for item in self._staging_yard:
                if isinstance(item, (CarriedVehicle, DropPod)):
                    normalised.append(item)
                    continue
                cv = _staging_yard_carried_vehicle(item)
                if cv is not None:
                    normalised.append(cv)
                    continue
                normalised.append(_pod_from_dict(item))
            self._staging_yard = normalised

    def __eq__(self, other):
        if not isinstance(other, Planet):
            return False
        return (self.name == other.name
                and self.location == other.location
                and self.orbit_distance == other.orbit_distance)

    def __hash__(self):
        return hash((self.name, self.location, self.orbit_distance))

    @property
    def active_abilities(self) -> Dict[str, bool]:
        """ability_name -> True for any facility component in 'active' phase.

        PROJ-372 Phase 2: 1-line facade delegating to PlanetQueryService.
        """
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.active_abilities(self)

    def is_ability_active(self, ability_key: str) -> bool:
        """Check if an activatable strategic ability is active on this planet."""
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.is_ability_active(self, ability_key)

    @property
    def occupied_hexes(self) -> FrozenSet[HexCoord]:
        """Return all hexes occupied by this planet (PROJ-139 IZoneOccupant)."""
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.occupied_hexes(self)

    @property
    def total_pressure_atm(self) -> float:
        total_pa = sum(self.atmosphere.values())
        return total_pa / 101325.0

    @property
    def max_population(self) -> int:
        """Pop capacity from surface area: m^2 / 1e6 * 100 / 1000 = units of 1000 people.
        Earth (~5.1e14 m^2) -> ~51M units (~51B people)."""
        return int(self.surface_area / 1_000_000 * 100 / 1000)

    @property
    def total_population(self) -> int:
        """Total population across all species on this planet."""
        return sum(p.count for p in self.populations)

    @property
    def has_space_shipyard(self) -> bool:
        """True iff any facility is an operational shipyard."""
        return any(facility.is_shipyard for facility in self.facilities)

    def get_cached_habitability_multiplier(self, race_registry, turn: int) -> float:
        """Population-weighted habitability multiplier, cached per turn.

        PROJ-285 cache invariant preserved: cache fields stay on the planet.
        PROJ-372 Phase 2: 1-line facade delegating to the
        ``IHabitabilityCalculator`` registered on ApplicationContext —
        modders inject custom calculators via
        ``set_default_planet_habitability_service``. Falls back to a
        default ``PlanetHabitabilityService`` when none is registered.
        """
        from game.context import get_default_planet_habitability_service
        svc = get_default_planet_habitability_service()
        if svc is None:
            from game.strategy.services.planet_habitability_service import (
                PlanetHabitabilityService,
            )
            svc = PlanetHabitabilityService()
        return svc.get_cached(self, race_registry, turn)

    def get_species_config(self, race_id: str) -> ColonySpeciesConfig:
        """PROJ-284: lazy-create + return per-species config for `race_id`."""
        if race_id not in self.species_configs:
            self.species_configs[race_id] = ColonySpeciesConfig()
        return self.species_configs[race_id]

    @property
    def context_type(self) -> str:
        """BuildContext protocol: returns 'planet'."""
        return "planet"

    # --- Read-only attribute views over private storage ---
    #
    # PROJ-449 Phase 3 deleted the @property/@setter shim cluster's
    # **setters** (which allowed `planet.stockpile = {...}` rebinding)
    # and the legacy-kwarg constructor wrapper. The getters survive as
    # read-only attribute views over the private fields so existing
    # readers in production and tests (`planet.stockpile.get(k)`,
    # `len(planet.staging_yard)`, etc.) keep working without a
    # cross-cutting sweep. Mutation must route through the stockpile /
    # staging-yard helper methods or `IPlanetMutator`. PROJ-450 widens
    # the `staging_yard` view to a typed `List[CarriedVehicle |
    # DropPod]` return signature.

    @property
    def stockpile(self) -> Dict[str, float]:
        """Read-only view over private stockpile storage.

        Writes must route through ``add_to_stockpile`` /
        ``consume_from_stockpile`` / ``IPlanetMutator.set_stockpile_amount``.
        """
        return self._stockpile

    @property
    def max_stockpile(self) -> Dict[str, float]:
        """Read-only view over private max-stockpile storage.

        Writes must route through ``IPlanetMutator.set_max_stockpile``.
        """
        return self._max_stockpile

    @property
    def staging_yard(self) -> List[Dict[str, Any]]:
        """TEMPORARY dict-projection bridge (Phase 2 → Phase 3).

        PROJ-450 Phase 2: internal ``_staging_yard`` is now typed
        (``List[CarriedVehicle | DropPod]``). This property returns a
        fresh list of dict views so the UI reader at
        ``game/ui/screens/strategy_detail_fmt.py:285-297`` and the
        existing peek sites in ``transfer_branches.py`` still work
        during the one-phase migration window. **Phase 3 deletes this
        property** and migrates the UI reader to typed attribute
        access.

        In-place mutation through this projection (``.clear()``,
        ``.append()``) silently no-ops against ``_staging_yard``;
        callers must route writes through ``add_to_staging_yard`` /
        ``remove_from_staging_yard`` / ``IPlanetMutator``.

        Defensive against substrate dict-leak: if a caller has bypassed
        the mutators and assigned dicts to ``_staging_yard`` directly
        (test fixtures, in-place rewrites), pass those through
        unchanged so the bridge remains stable while the dict-leak is
        chased down.
        """
        result: list[dict[str, Any]] = []
        for item in self._staging_yard:
            if isinstance(item, dict):
                result.append(item)
            else:
                result.append(item.to_dict())
        return result

    # --- IStockpileHolder protocol (PROJ-372) ---

    def add_to_stockpile(self, resource_type: str, amount: float) -> float:
        """Add resources to the local stockpile; return overflow."""
        current = self._stockpile.get(resource_type, 0.0)
        max_cap = self._max_stockpile.get(resource_type, float('inf'))
        new_total = current + amount
        if new_total > max_cap:
            self._stockpile[resource_type] = max_cap
            return new_total - max_cap
        self._stockpile[resource_type] = new_total
        return 0.0

    def consume_from_stockpile(self, resource_type: str, amount: float) -> bool:
        """All-or-nothing consume. Return True iff sufficient stockpile."""
        current = self._stockpile.get(resource_type, 0.0)
        if current >= amount:
            self._stockpile[resource_type] = current - amount
            return True
        return False

    def has_stockpile(self, costs: dict) -> bool:
        """True iff every resource->amount in `costs` is satisfied."""
        return all(
            self._stockpile.get(rt, 0.0) >= amt for rt, amt in costs.items()
        )

    def get_stockpile(self, resource_type: str) -> float:
        """Current stockpiled amount, 0.0 if absent."""
        return self._stockpile.get(resource_type, 0.0)

    # --- IProductionResourceSource (PROJ-436 Phase 8) ---
    # Delegators over the stockpile API above so ProductionEngine reads
    # through one uniform protocol satisfied by both Planet and Fleet
    # — no context_type dispatch. Stockpile API above stays as the
    # public surface for transfer_branches.py / IStockpileHolder.

    def production_has_resources(self, costs: Dict[str, float]) -> bool:
        return self.has_stockpile(costs)

    def production_get_resource(self, resource_type: str) -> float:
        return self.get_stockpile(resource_type)

    def production_consume_resource(self, resource_type: str, amount: float) -> bool:
        return self.consume_from_stockpile(resource_type, amount)

    # --- IStagingYardHolder protocol (PROJ-372) ---

    def get_staging_mass(self) -> float:
        """Total mass of items currently in the staging yard.

        PROJ-450 Phase 2: substrate holds typed entries; mass attribute
        access replaces the prior ``.get('mass', 0.0)`` dict-shape read.
        Defensive ``getattr`` keeps the helper resilient to a dict
        slipping in via direct ``_staging_yard`` assignment.
        """
        return sum(
            (item.get('mass', 0.0) if isinstance(item, dict)
             else getattr(item, 'mass', 0.0))
            for item in self._staging_yard
        )

    def add_to_staging_yard(
        self, item: "Dict[str, Any] | CarriedVehicle | DropPod"
    ) -> bool:
        """Add an item; return False on insufficient capacity.

        PROJ-450 Phase 2: substrate is typed
        ``List[CarriedVehicle | DropPod]``. Dict inputs (save-load,
        rollback paths) are promoted to typed entries BEFORE append.
        Typed inputs land directly.
        """
        if isinstance(item, dict):
            cv = _staging_yard_carried_vehicle(item)
            typed_item: "CarriedVehicle | DropPod" = (
                cv if cv is not None else _pod_from_dict(item)
            )
        else:
            typed_item = item
        item_mass = getattr(typed_item, 'mass', 0.0)
        if self.max_staging_mass > 0 and self.get_staging_mass() + item_mass > self.max_staging_mass:
            return False
        self._staging_yard.append(typed_item)
        return True

    def remove_from_staging_yard(
        self, index: int
    ) -> "CarriedVehicle | DropPod | None":
        """Remove and return the item at ``index``, or None if out of range.

        PROJ-450 Phase 2: returns the typed entry directly. The
        substrate is now typed, so no dict promotion is required.
        """
        if 0 <= index < len(self._staging_yard):
            return self._staging_yard.pop(index)
        return None

    def pop_staging_yard_typed(
        self, index: int
    ) -> "CarriedVehicle | DropPod | None":
        """Pop and return the item at ``index`` as a typed
        :class:`CarriedVehicle` or :class:`DropPod`.

        PROJ-450 Phase 2: the substrate is typed, so this is a thin
        alias over :meth:`remove_from_staging_yard`. Defensive: if a
        dict slipped into the substrate via direct assignment, promote
        on the way out via the same helpers ``__post_init__`` uses.
        """
        raw = self.remove_from_staging_yard(index)
        if raw is None or isinstance(raw, (CarriedVehicle, DropPod)):
            return raw
        cv = _staging_yard_carried_vehicle(raw)
        return cv if cv is not None else _pod_from_dict(raw)

    def can_build_type(self, vehicle_type: str) -> bool:
        """Check if this planet can build the given vehicle type.

        PROJ-372 Phase 2: 1-line facade delegating to PlanetQueryService.
        """
        from game.strategy.services.planet_query_service import PlanetQueryService
        return PlanetQueryService.can_build_type(self, vehicle_type)

    # --- IOrderable (PROJ-238 — unified with Fleet) ---

    def get_current_order(self) -> Optional['Order']:
        """First order in the queue, or None."""
        return self.orders[0] if self.orders else None

    def pop_order(self) -> Optional['Order']:
        """Pop and return the first order, or None."""
        return self.orders.pop(0) if self.orders else None

    def add_order(self, order: 'Order', index: Optional[int] = None) -> None:
        """Add `order` at `index` (or append if None)."""
        if index is not None:
            self.orders.insert(index, order)
        else:
            self.orders.append(order)

    def clear_orders(self) -> None:
        """Remove all orders from the planet's queue."""
        self.orders.clear()

    def add_production(self, design_id: str, turns: int, vehicle_type: str = "ship") -> None:
        """Add a build item; vehicle_type in {ship, fighter, satellite, complex}."""
        self.construction_queue.append({
            "design_id": design_id,
            "type": vehicle_type,
            "turns_remaining": turns,
        })

    def to_dict(self) -> Dict[str, Any]:
        """Serialize planet to dict for save system. PROJ-372 Phase 2: facade
        delegating to ``planet_serde.planet_to_dict``."""
        from game.strategy.data.planet_serde import planet_to_dict
        return planet_to_dict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Planet':
        """Deserialize planet from save data. PROJ-372 Phase 2: facade
        delegating to ``planet_serde.planet_from_dict_kwargs``."""
        from game.strategy.data.planet_serde import planet_from_dict_kwargs
        return cls(**planet_from_dict_kwargs(data))
