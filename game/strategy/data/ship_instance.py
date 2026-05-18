"""
ShipInstance - Strategy layer representation of a ship.

Bridges between:
- Ship designs (templates from Ship Builder)
- Strategy fleet management
- Battle simulation

Each ShipInstance tracks the current state of a ship (damage, resources)
separate from its design template.

Delegates:
- ShipConsumableManager: resource tracking (fuel, energy, ammo)
- ShipCargoManager: cargo loading/unloading
- ShipDisplayFormatter: display string formatting
- ShipInstanceBridge: simulation bridge (to_ship, update_from_ship)
- ShipInstanceSerializer: serialization (to_dict, from_dict, clone)
- ShipStatsCache: stats calculation + cache rule (PROJ-425 Phase 1)
- ShipInstanceFactory: construction path (PROJ-425 Phase 3)
- component_inspector: per-instance layer views (PROJ-425 Phase 2)
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING

from game.core.protocols import IPostBattleShip
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import CarriedVehicle, VALID_VEHICLE_TYPES
from game.strategy.data.ship_consumable_manager import ShipConsumableManager
from game.strategy.data.ship_cargo_manager import ShipCargoManager
from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
from game.strategy.data.ship_instance_bridge import ShipInstanceBridge
from game.core.component_state import ComponentInstanceView, ComponentState

logger = logging.getLogger(__name__)

# Fallback if stats dict lacks max_hp (should not happen with proper DI)
_DEFAULT_MAX_HP = 100

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.core.registry import GameRegistries
    from game.strategy.data.container import Container


@dataclass
class ShipInstance:
    """
    Represents a ship in the strategy layer.

    Bridges between:
    - Ship designs (templates from Ship Builder)
    - Strategy fleet management
    - Battle simulation
    """

    instance_id: str  # Unique across game
    design_id: str    # Reference to ship design file/name
    name: str         # Instance name (may differ from design)
    owner_id: int     # Empire that owns this ship

    # Design data (full serialized ship template)
    design_data: Dict[str, Any] = field(default_factory=dict)

    # Current state (may differ from design defaults)
    # None values mean "use design default"
    current_hp: Optional[int] = None
    consumable_levels: Dict[str, float] = field(default_factory=dict)  # resource_name -> current
    component_toggles: Dict[str, bool] = field(default_factory=dict)  # component_id -> enabled
    activation_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # component_key -> activation state

    # Per-component-instance persistent state. Key format:
    # `component_state_key(component_id, instance_index)` =
    # `"{component_id}#{instance_index}"`. Authoritative source for
    # battle round-trip (BattleSpec.components / BattleOutcome.components)
    # and for per-instance HP in stat calculation. PROJ-269 Phase 2 +
    # PROJ-276 (closed the transition; removed the legacy `component_damage`
    # dict).
    components: Dict[str, ComponentState] = field(default_factory=dict)

    # Cargo contents (cargo_type -> current amount)
    cargo_contents: Dict[str, int] = field(default_factory=dict)

    # PROJ-431 Phase 1f: typed two-slot carried inventory replaces the
    # legacy ``carried_items: List[Dict[str, Any]]`` mixed-shape list.
    #
    # ``bay_inventory.bay`` holds homogeneous ``CarriedVehicle`` entries
    # (mines / fighters / satellites). ``bay_inventory.pods`` holds
    # ``DropPod`` entries. The previous runtime
    # ``CarriedVehicle.from_any(...)`` discriminator was needed only to
    # walk the mixed-shape list and is now removed.
    #
    # A backward-compatible ``carried_items`` *property* (NOT a dataclass
    # field) is kept below for test infrastructure that still pokes the
    # legacy dict-list shape — see ``carried_items`` property.
    bay_inventory: BayInventory = field(default_factory=BayInventory)

    # Status
    is_alive: bool = True
    is_derelict: bool = False
    is_operational: bool = True

    # Design role classification
    design_role: Optional[str] = None    # Auto-classified role (DesignRole value)
    role_override: Optional[str] = None  # Player override (DesignRole value)

    # Strategy tracking
    experience: int = 0           # For future crew/veteran system
    kills: int = 0
    battles_survived: int = 0

    # Serial number - unique per design within an empire
    serial: Optional[int] = None

    # Cached calculated stats (invalidated on damage change)
    _cached_stats: Optional[Dict[str, Any]] = field(default=None, repr=False)

    # PROJ-211: Injected registries for stats calculation (no global fallback)
    _registries: Optional['GameRegistries'] = field(default=None, repr=False, init=False)

    # Delegate managers (initialized in __post_init__).
    # PROJ-425 Phase 4: canonical names on the entity are `_resource_mgr`
    # / `_cargo_mgr` / `_display_fmt` / `_bridge`. The write service was
    # querying `_cargo_manager` / `_consumable_manager` (dead code, since
    # those attributes never existed); fixed in this phase to match the
    # entity instead of renaming ~50 callers across production + tests.
    _resource_mgr: Optional['ShipConsumableManager'] = field(default=None, repr=False, init=False)
    _cargo_mgr: Optional['ShipCargoManager'] = field(default=None, repr=False, init=False)
    _display_fmt: Optional['ShipDisplayFormatter'] = field(default=None, repr=False, init=False)
    _bridge: Optional['ShipInstanceBridge'] = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Initialize delegate managers after dataclass init."""
        self._resource_mgr = ShipConsumableManager(self)
        self._cargo_mgr = ShipCargoManager(self)
        self._display_fmt = ShipDisplayFormatter(self)
        self._bridge = ShipInstanceBridge(self)

    def set_registries(self, registries: 'GameRegistries') -> None:
        """
        Set the registries for stats calculation.

        PROJ-211: Allows setting registries after construction for objects
        created without registries (e.g., deserialization).

        Args:
            registries: GameRegistries instance for stats calculation.
        """
        self._registries = registries
        self.invalidate_stats_cache()

    # PROJ-193: Property aliases for IShipInstance Protocol compliance
    @property
    def design_name(self) -> str:
        """Design name from design_data (IShipInstance Protocol)."""
        return self.design_data.get('name', self.design_id)

    @property
    def hull_class(self) -> str:
        """Ship's hull class from design_data (IShipInstance Protocol)."""
        return self.design_data.get('ship_class', 'Unknown')

    @property
    def ship_name(self) -> str:
        """Instance name alias (IShipInstance Protocol)."""
        return self.name

    @property
    def serial_number(self) -> Optional[int]:
        """Serial number alias (IShipInstance Protocol)."""
        return self.serial

    @property
    def effective_role(self) -> Optional[str]:
        """The active role: role_override if set, else design_role."""
        if self.role_override is not None:
            return self.role_override
        return self.design_role

    def __hash__(self) -> int:
        return hash(self.instance_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ShipInstance):
            return NotImplemented
        return self.instance_id == other.instance_id

    @classmethod
    def create(
        cls,
        design_data: Dict[str, Any],
        owner_id: int,
        name: Optional[str] = None,
        design_id: Optional[str] = None,
        empire: Optional['Empire'] = None,
        registries: Optional['GameRegistries'] = None,
    ) -> 'ShipInstance':
        """Create a new ship instance from a design.

        Thin shim around `ShipInstanceFactory.create` (PROJ-425 Phase 3).
        The shim remains until grep shows no callers still using
        `ShipInstance.create(...)` directly.

        Args:
            design_data: Full ship design dictionary
                (from `ShipSerializer.to_dict()`).
            owner_id: Empire that owns this ship.
            name: Instance name (defaults to design name).
            design_id: Design identifier (defaults to design name).
            empire: Empire to draw the serial number from. If None, no
                serial is assigned and a warning is logged.
            registries: `GameRegistries` for stats calculation. Required
                for proper DI. Without it, `get_calculated_stats()` raises.

        Returns:
            New `ShipInstance` with unique `instance_id`.
        """
        from game.strategy.services.ship_instance_factory import ShipInstanceFactory
        return ShipInstanceFactory.create(
            design_data=design_data,
            owner_id=owner_id,
            name=name,
            design_id=design_id,
            empire=empire,
            registries=registries,
        )

    def is_damaged(self) -> bool:
        """Check if ship has any damage — hull, per-component, or derelict."""
        return (
            self.current_hp is not None or
            any(cs.is_damaged for cs in self.components.values()) or
            self.is_derelict
        )

    def is_combat_capable(self) -> bool:
        """Check if ship can participate in combat."""
        return self.is_alive and not self.is_derelict

    def get_activation_state(self, component_key: str) -> 'ComponentActivationState':
        """Get the activation state for a component."""
        from game.strategy.data.component_activation_state import ComponentActivationState
        data = self.activation_states.get(component_key)
        if data is None:
            return ComponentActivationState()
        if isinstance(data, dict):
            return ComponentActivationState.from_dict(data)
        return ComponentActivationState()

    def set_activation_state(self, component_key: str, state: 'ComponentActivationState') -> None:
        """Store the activation state for a component."""
        self.activation_states[component_key] = state.to_dict()

    def get_calculated_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get calculated stats from components, respecting damage state.

        Delegates to `ShipStatsCache` (PROJ-425 Phase 1): the helper owns
        the registry-DI calculation path and the cache rule. Storage of
        `_cached_stats` remains on this entity per TD-06 Guardrail #2.

        Args:
            force_refresh: If True, recalculate even if cached

        Returns:
            Dict with calculated stats (max_hp, mass, resource_storage, etc.)
        """
        from game.strategy.data.ship_stats_cache import ShipStatsCache
        return ShipStatsCache.get_or_compute(self, force_refresh=force_refresh)

    def invalidate_stats_cache(self) -> None:
        """
        Invalidate cached stats.

        Call this when component damage changes, after battle,
        or after repair operations.
        """
        from game.strategy.data.ship_stats_cache import ShipStatsCache
        ShipStatsCache.invalidate(self)

    def get_hp_percentage(self) -> float:
        """Get current HP as percentage of max."""
        if self.current_hp is None:
            return 1.0
        max_hp = self.get_calculated_stats().get('max_hp', _DEFAULT_MAX_HP)
        if max_hp <= 0:
            return 0.0
        return self.current_hp / max_hp

    def get_resource_percentage(self, resource_name: str) -> float:
        """Get current resource level as percentage of max."""
        return self._display_fmt.get_resource_percentage(resource_name)

    # --- Generic Resource Methods (PROJ-425 Phase 5b: thin shims) ---
    #
    # These remain as forwarders because too many tests mock them as
    # entity-level methods (e.g. `ship.consume_resource = Mock(...)`).
    # Migrating those mocks is a bigger change than the demolition saves.
    # The canonical implementations live on `ShipConsumableManager`.

    def get_resource_capacity(self, resource_type: str) -> float:
        """Get maximum capacity for a resource type (shim to `_resource_mgr`)."""
        return self._resource_mgr.get_resource_capacity(resource_type)

    def get_current_resource(self, resource_type: str) -> float:
        """Get current level of a resource type (shim to `_resource_mgr`)."""
        return self._resource_mgr.get_current_resource(resource_type)

    def consume_resource(self, resource_type: str, amount: float) -> bool:
        """Consume a resource amount (shim to `_resource_mgr`)."""
        return self._resource_mgr.consume_resource(resource_type, amount)

    def get_all_resource_costs_per_hex(self) -> Dict[str, float]:
        """Per-hex consumption costs (shim to `_resource_mgr`)."""
        return self._resource_mgr.get_all_resource_costs_per_hex()

    def get_all_resource_costs_per_turn(self) -> Dict[str, float]:
        """Per-turn consumption costs (shim to `_resource_mgr`)."""
        return self._resource_mgr.get_all_resource_costs_per_turn()

    # --- Cargo / carried-vehicle helpers ---
    #
    # PROJ-425 Phase 6 (TD-06 batch 5c): the method forwarders for
    # cargo queries / mutators, carried-vehicle queries, and pod-storage
    # helpers were demolished. Callers go through ``ship._cargo_mgr``
    # (see :class:`ShipCargoManager`). The ``bay_current_mass`` and
    # ``bay_capacity_mass`` *properties* below are kept as small
    # read-only entity attributes — they read naturally as
    # ship-instance state (parallel to ``design_name`` /
    # ``hull_class``) and are referenced by tests as such.

    @property
    def bay_current_mass(self) -> float:
        """PROJ-FMS-A: runtime vehicle-bay usage on this ship.

        Mirrors the ``bay_capacity_mass`` design stat. Computed at the
        strategy layer because it depends on the actual contents of
        ``bay_inventory.bay`` (simulation ``Ship`` cannot see those).
        """
        return self._cargo_mgr.get_carried_vehicle_mass()

    # ------------------------------------------------------------------
    # PROJ-436 Phase 3a — unified Container projections.
    # ------------------------------------------------------------------
    #
    # These are read-only snapshot views over the legacy
    # `consumable_levels` and `cargo_contents` dataclass fields. Later
    # sub-phases of Phase 3 migrate callers off the legacy fields; the
    # final cutover deletes both fields and these views become the
    # canonical read API. Until then, the views serve callers that
    # want to work in the unified Container abstraction without
    # forcing a wholesale migration.
    #
    # Snapshot semantics: mutations on the returned Container are NOT
    # propagated back to the ship. Treat as a read view.

    def consumable_container(self) -> 'Container':
        """Container snapshot of this ship's `consumable_levels`.

        Every entry in `consumable_levels` (resource_name -> amount)
        appears in the resource slice. Unknown resource ids (not in
        `ResourceCatalog`) raise via `Container.add_resource` —
        consumable_levels keys are assumed to be canonical resource ids
        per the existing component-driven loading code.
        """
        from game.strategy.data.container import (
            Container,
            ContainerPolicy,
        )
        from game.strategy.data.containable import (
            ContainableKind,
            ResourceContainable,
        )

        policy = ContainerPolicy(
            allowed_kinds=frozenset({ContainableKind.RESOURCE}),
            allowed_type_ids=None,
        )
        c = Container(capacity_mass=float("inf"), policy=policy)
        for resource_id, amount in self.consumable_levels.items():
            c.add(ResourceContainable(resource_id), amount)
        return c

    def cargo_container(self) -> 'Container':
        """Container snapshot of this ship's `cargo_contents`.

        Translation rules for cargo_contents keys:
        - "passengers" -> population slice (default species id).
        - Known resource ids (in `ResourceCatalog`) -> resource slice.
        - Other keys -> logged and skipped (no representation in the
          snapshot). The most common skipped keys are "drop_pod" and
          "vehicle" which live in `bay_inventory` instead.
        """
        from game.core.resources import ResourceCatalog
        from game.strategy.data.container import (
            Container,
            ContainerPolicy,
            _get_resource_catalog,
        )
        from game.strategy.data.containable import (
            ContainableKind,
            PopulationContainable,
            ResourceContainable,
        )

        catalog: ResourceCatalog = _get_resource_catalog()
        policy = ContainerPolicy(
            allowed_kinds=frozenset({
                ContainableKind.RESOURCE,
                ContainableKind.POPULATION,
            }),
            allowed_type_ids=None,
        )
        c = Container(capacity_mass=float("inf"), policy=policy)
        for key, amount in self.cargo_contents.items():
            if key == "passengers":
                c.add(PopulationContainable("default"), int(amount))
            elif catalog.has(key):
                c.add(ResourceContainable(key), float(amount))
            else:
                logger.debug(
                    "cargo_container: skipping cargo_contents key %r "
                    "(not a known resource id or 'passengers')",
                    key,
                )
        return c

    # ------------------------------------------------------------------
    # PROJ-431 Phase 1f: bay_inventory IS the canonical storage.
    # ------------------------------------------------------------------
    #
    # The typed :class:`BayInventory` (``bay: list[CarriedVehicle]`` +
    # ``pods: list[DropPod]``) is now a real dataclass field on this
    # entity, not a projection over the legacy mixed-shape list. The
    # earlier ``carried_items`` field was removed; what remains here is
    # a backward-compatible property/setter exposing the legacy
    # dict-list shape exclusively for **test infrastructure** that still
    # pokes ``ship.carried_items.append({...})`` directly. Production
    # code uses :attr:`bay_inventory` and :meth:`set_bay_inventory`.

    def set_bay_inventory(self, bay_inventory: 'BayInventory') -> None:
        """Replace this ship's typed bay inventory wholesale.

        Phase 1f: this is a thin attribute setter retained as a stable
        write surface for callers that produced a new
        :class:`BayInventory` value (e.g. ``ShipCargoManager`` loaders /
        unloaders, FMS handlers). Callers that just mutate the lists in
        place do not need to call this — the underlying field is now
        owned by this entity directly.
        """
        if not isinstance(bay_inventory, BayInventory):
            raise TypeError(
                f"set_bay_inventory expects BayInventory, got "
                f"{type(bay_inventory).__name__}"
            )
        self.bay_inventory = bay_inventory

    # --- Legacy-shim: ``carried_items`` property -----------------------
    #
    # PROJ-431 Phase 1f: ``carried_items`` is no longer a stored field.
    # This property exposes a write-through proxy list over the typed
    # ``bay_inventory`` slots so test infrastructure that does
    # ``ship.carried_items.append({...})`` / ``ship.carried_items =
    # [...]`` keeps working without each test having to migrate to the
    # typed API. Production code uses :attr:`bay_inventory` and
    # :meth:`set_bay_inventory` directly.

    @property
    def carried_items(self) -> '_CarriedItemsProxy':
        """Legacy mixed-shape dict-list write-through view (test shim).

        Returns a :class:`_CarriedItemsProxy` whose mutations
        (``append``, ``extend``, ``pop``, ``__setitem__``, slice
        replacement, ``clear``) write back into
        :attr:`bay_inventory`. Reads behave like the historical
        ``List[Dict[str, Any]]`` substrate.
        """
        return _CarriedItemsProxy(self)

    @carried_items.setter
    def carried_items(self, items: List[Any]) -> None:
        """Replace via legacy dict-list shape; routes into typed slots."""
        self.bay_inventory = _items_to_bay_inventory(items)

    @property
    def bay_capacity_mass(self) -> float:
        """PROJ-FMS-A: maximum vehicle-bay capacity from design stats."""
        _current, max_mass = self._cargo_mgr.get_vehicle_bay_capacity()
        return max_mass

    # PROJ-425 Phase 6 (TD-06 batch 5c): pod-storage helpers
    # (``get_pod_storage_capacity`` / ``get_pod_storage_used`` /
    # ``can_carry_pod``) were demolished; callers go through
    # ``ship._cargo_mgr`` directly.

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """Warp jump resource costs (shim to `_resource_mgr`)."""
        return self._resource_mgr.get_warp_resource_costs()

    # --- Component Toggle Methods ---

    def set_component_enabled(self, component_id: str, enabled: bool) -> None:
        """Enable or disable a component manually.

        Disabled components don't contribute abilities to stats but still
        contribute their mass. Useful for conserving resources or managing
        damage states.

        PROJ-425 Phase 4: write behavior owned by `ShipInstanceWriteService`.
        Cache invalidation is centralized there.
        """
        from game.strategy.services.ship_instance_write_service import ShipInstanceWriteService
        ShipInstanceWriteService().set_component_enabled(self, component_id, enabled)

    def is_component_enabled(self, component_id: str) -> bool:
        """
        Check if a component is enabled.

        Args:
            component_id: ID of the component to check

        Returns:
            True if component is enabled (or not in toggles dict), False if disabled.
        """
        return self.component_toggles.get(component_id, True)

    def get_damaged_component_count(self) -> int:
        """Get count of damaged component instances.

        Delegates to `component_inspector.count_damaged_components`
        (PROJ-425 Phase 2).
        """
        from game.strategy.services.component_inspector import count_damaged_components
        return count_damaged_components(self)

    def get_components_by_layer(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get components grouped by layer from design data.

        Returns:
            Dict mapping layer name (CORE, INNER, etc.) to list of component entries.
        """
        layers = self.design_data.get('layers', {})
        return {layer_name: list(comps) for layer_name, comps in layers.items()}

    def iter_all_components_by_layer(self) -> Dict[str, List[ComponentInstanceView]]:
        """Return every component on this ship grouped by layer.

        Delegates to `component_inspector.iter_components_by_layer`
        (PROJ-425 Phase 2). See that function for behavior.
        """
        from game.strategy.services.component_inspector import iter_components_by_layer
        return iter_components_by_layer(self)

    def get_damaged_components_by_layer(self) -> Dict[str, List[Tuple[str, int]]]:
        """Get damaged component instances grouped by layer.

        Delegates to `component_inspector.damaged_components_by_layer`
        (PROJ-425 Phase 2).
        """
        from game.strategy.services.component_inspector import damaged_components_by_layer
        return damaged_components_by_layer(self)

    # --- Bridge Methods (PROJ-425 Phase 5e: thin shims) ---
    #
    # These remain as forwarders because `to_ship` / `update_from_ship`
    # are TD-06 Weak-LLM Guardrail #1 high-value entry points with ~10
    # live production callers (`ship_materializer`, `replay_ship_builder`,
    # `simulation_adapter`, `minefield_resolver`, `fleet_battle_adapter`,
    # etc.) plus extensive test usage. Migrating in one batch would
    # exceed the slimming benefit.
    # The canonical implementations live on `ShipInstanceBridge`.
    # Removal condition: once all callers migrate to direct
    # `ship_instance._bridge.to_ship(...)` / `.update_from_ship(...)`
    # access. Tests under `tests/unit/strategy/ship_instance/` still
    # rely on these forwarders.

    def to_ship(
        self,
        position: Tuple[float, float],
        team_id: int,
        *,
        registries: 'GameRegistries'
    ) -> 'Ship':
        """
        Create a simulation Ship from this instance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
            registries: GameRegistries for DI (required).
        """
        return self._bridge.to_ship(position, team_id, registries=registries)

    def update_from_ship(self, ship: IPostBattleShip) -> None:
        """
        Update this instance from post-battle ship state.

        Called after strategy battle resolution to persist damage/resource changes.
        """
        self._bridge.update_from_ship(ship)

    def repair(self, amount: int) -> int:
        """Repair the ship by a certain amount.

        PROJ-425 Phase 4: write behavior owned by `ShipInstanceWriteService`.
        Returns the actual amount repaired.
        """
        from game.strategy.services.ship_instance_write_service import ShipInstanceWriteService
        return ShipInstanceWriteService().repair(self, amount)

    def resupply(self, resource_name: str, amount: float) -> float:
        """Resupply a resource (shim to `_resource_mgr`)."""
        return self._resource_mgr.resupply(resource_name, amount)

    # --- Serializer Methods (PROJ-425 Phase 5d: thin shims) ---
    #
    # These remain as forwarders because `to_dict` / `from_dict` /
    # `to_json` / `from_json` / `clone` are TD-06 Weak-LLM Guardrail #1
    # high-value entry points with ~18 live production + test callers
    # on `ShipInstance` directly. Migrating in one batch would force a
    # risky all-callers sweep across save/load, replay, and fleet
    # round-trip surfaces.
    # The canonical implementations live on `ShipInstanceSerializer`.
    # Removal condition: once all callers migrate to direct
    # `ShipInstanceSerializer.to_dict(ship)` / `.from_dict(data)` /
    # `.to_json(ship)` / `.from_json(s)` / `.clone(ship)` access. Tests
    # under `tests/unit/strategy/ship_instance/` still rely on these
    # forwarders.

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.to_dict(self)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'ShipInstance':
        """
        Deserialize from save game.

        Args:
            data: Dict with ship instance data
            registries: GameRegistries for stats calculation. Optional during
                       deserialization but must be set before calling
                       get_calculated_stats().

        Returns:
            Reconstructed ShipInstance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.from_dict(data, registries=registries)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.to_json(self, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'ShipInstance':
        """Deserialize from JSON string."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.from_json(json_str)

    def clone(self) -> 'ShipInstance':
        """Create a deep copy of this instance (for hypothetical battles)."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.clone(self)

    def __repr__(self) -> str:
        hp_status = f"{self.current_hp}HP" if self.current_hp is not None else "Full"
        status = "DESTROYED" if not self.is_alive else ("DERELICT" if self.is_derelict else "OK")
        return f"ShipInstance({self.name}, {hp_status}, {status})"


# ---------------------------------------------------------------------------
# PROJ-431 Phase 1f legacy-shim helpers
# ---------------------------------------------------------------------------


def _items_to_bay_inventory(items: List[Any]) -> BayInventory:
    """Split a legacy mixed-shape ``carried_items`` list into typed slots.

    Bay-bound (``CarriedVehicle``-shaped) entries land in
    :attr:`BayInventory.bay`; everything else lands in
    :attr:`BayInventory.pods`. Used by the legacy ``carried_items``
    setter on :class:`ShipInstance` and by the
    :class:`_CarriedItemsProxy` write paths.
    """
    new_bay: List[CarriedVehicle] = []
    new_pods: List[DropPod] = []
    for item in items or []:
        if isinstance(item, CarriedVehicle):
            new_bay.append(item)
            continue
        if isinstance(item, DropPod):
            new_pods.append(item)
            continue
        if not isinstance(item, dict):
            continue
        vt = str(item.get('vehicle_type', '')).lower()
        if vt in VALID_VEHICLE_TYPES:
            new_bay.append(CarriedVehicle.from_dict(item))
        else:
            new_pods.append(DropPod(
                design_id=str(item.get('design_id', '')),
                design_data=dict(item.get('design_data', {})),
                mass=float(item.get('mass', 0.0)),
                payload={
                    k: v for k, v in item.items()
                    if k not in {'design_id', 'design_data', 'mass'}
                },
            ))
    return BayInventory(bay=new_bay, pods=new_pods)


def _bay_inventory_to_items(bi: BayInventory) -> List[Dict[str, Any]]:
    """Project a typed :class:`BayInventory` back to the legacy dict-list."""
    items: List[Dict[str, Any]] = []
    for cv in bi.bay:
        items.append(cv.to_dict())
    for pod in bi.pods:
        entry: Dict[str, Any] = {
            'design_id': pod.design_id,
            'design_data': pod.design_data,
            'mass': pod.mass,
        }
        entry.update(pod.payload)
        items.append(entry)
    return items


class _CarriedItemsProxy:
    """Write-through dict-list proxy over :attr:`ShipInstance.bay_inventory`.

    Mutations rebuild the underlying typed :class:`BayInventory` so test
    code that pokes ``ship.carried_items.append({...})`` /
    ``ship.carried_items.pop(0)`` / ``ship.carried_items[i] = {...}`` /
    slice-replacement / ``clear()`` keeps working without a per-test
    migration.

    Reads behave like the legacy ``List[Dict[str, Any]]`` substrate:
    bay entries materialise via :meth:`CarriedVehicle.to_dict`; pods
    materialise via the historical drop-pod dict shape (``design_id`` +
    ``design_data`` + ``mass`` + ``payload`` flattened).
    """

    __slots__ = ('_ship',)

    def __init__(self, ship: 'ShipInstance') -> None:
        self._ship = ship

    def _snapshot(self) -> List[Dict[str, Any]]:
        return _bay_inventory_to_items(self._ship.bay_inventory)

    def _writeback(self, items: List[Any]) -> None:
        self._ship.bay_inventory = _items_to_bay_inventory(items)

    # --- read protocol ------------------------------------------------
    def __len__(self) -> int:
        return len(self._snapshot())

    def __iter__(self):
        return iter(self._snapshot())

    def __getitem__(self, index):
        return self._snapshot()[index]

    def __contains__(self, item) -> bool:
        return item in self._snapshot()

    def __eq__(self, other) -> bool:
        if isinstance(other, _CarriedItemsProxy):
            return self._snapshot() == other._snapshot()
        return self._snapshot() == other

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return repr(self._snapshot())

    def __bool__(self) -> bool:
        return bool(self._snapshot())

    # --- mutation protocol --------------------------------------------
    def append(self, item: Any) -> None:
        items = self._snapshot()
        items.append(item)
        self._writeback(items)

    def extend(self, more: Any) -> None:
        items = self._snapshot()
        items.extend(more)
        self._writeback(items)

    def insert(self, index: int, item: Any) -> None:
        items = self._snapshot()
        items.insert(index, item)
        self._writeback(items)

    def pop(self, index: int = -1) -> Any:
        items = self._snapshot()
        popped = items.pop(index)
        self._writeback(items)
        return popped

    def remove(self, item: Any) -> None:
        items = self._snapshot()
        items.remove(item)
        self._writeback(items)

    def clear(self) -> None:
        self._writeback([])

    def __setitem__(self, index, value) -> None:
        items = self._snapshot()
        items[index] = value
        self._writeback(items)

    def __delitem__(self, index) -> None:
        items = self._snapshot()
        del items[index]
        self._writeback(items)
