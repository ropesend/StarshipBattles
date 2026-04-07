import logging
import math
import uuid
from typing import Callable, List, Dict, Tuple, Optional, Any, Union, Iterator

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.engine.physics import PhysicsBody
from game.simulation.components.component import Component, create_component
from game.core.constants import LayerType
from game.simulation.entities.layer_data import LayerData
from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)

# Re-export for backward compatibility and convenient access
from game.simulation.physics_constants import DEFAULT_MAX_MASS
from game.core.constants import LayerDefaults, CombatConstants

from .ship_stats import ShipStatsCalculator
from .ship_physics import ShipPhysicsMixin
from .ship_formation import ShipFormation
from .ship_stat_querier import ShipStatQuerier
from .ship_validator_helper import ShipValidatorHelper
from game.simulation.systems.resource_manager import ResourceRegistry

# Internal imports
from .ship_serialization import ShipSerializer

class Ship(PhysicsBody, ShipPhysicsMixin):
    """Ship entity -- facade over extracted subsystem delegates.

    Inheritance:
        PhysicsBody: Provides position, velocity, angle, forward_vector().
            __init__(x, y) called via super() in Ship.__init__.
        ShipPhysicsMixin: Provides update_physics_movement(), thrust_forward(),
            rotate(). No __init__ -- relies on Ship attributes being set first.

    Delegates:
        ShipComponentManager: Component lifecycle, caching, queries (PROJ-240)
        ShipCombatManager: Combat orchestration, derelict, death, firing (PROJ-240)
        ShipCombatEngine: Weapon firing, targeting, damage, shield regen
        ShipStatsCalculator: 5-phase stat aggregation
        ShipSerializer: to_dict / from_dict
        ShipStatQuerier: Ability totals, sensor/ECM scores
        ShipValidatorHelper: Design validation
        ShipFormation: Formation data
    """

    def __init__(self, name: str, x: float, y: float, color: Union[Tuple[int, int, int], List[int]],
                 team_id: int = 0, ship_class: str = "Escort", theme_id: str = "Federation",
                 *, registries: GameRegistries):
        """
        Initialize Ship with properties and registries.

        PROJ-50: Strict DI - registries is required.

        Args:
            name: Ship name
            x, y: Initial position
            color: RGB tuple for ship color
            team_id: Team identifier
            ship_class: Vehicle class name (e.g., "frigate", "cruiser")
            theme_id: Visual theme identifier
            registries: GameRegistries for DI (required).

        Raises:
            ValidationException: If registries is None
        """
        if registries is None:
            raise ValidationException(
                "registries is required for Ship initialization",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "Ship", "parameter": "registries"}
            )
        super().__init__(x, y)

        # === Identity ===
        self.id: str = str(uuid.uuid4())
        self.instance_id: Optional[str] = None  # PROJ-254: Set by strategy layer for battle reconciliation
        self.name: str = name
        self.color: Union[Tuple[int, int, int], List[int]] = color
        self.team_id: int = team_id
        self.ship_class: str = ship_class
        self.theme_id: str = theme_id

        # === Registries (DI) ===
        self._registries = registries
        class_def = self._registries.vehicle_classes.get(self.ship_class, {})

        # === Layers & Hull ===
        self._initialize_layers()
        self._equip_default_hull(class_def)

        # === Stats (populated by ShipStatsCalculator) ===
        self._cached_mass: float = 0.0
        self._cached_max_hp: int = 0
        self._cached_hp: int = 0
        self.base_mass: float = 0.0
        self.vehicle_type: str = class_def.get('type', "Ship")
        self.total_thrust: float = 0.0
        self.max_speed: float = 0.0
        self.turn_speed: float = 0.0
        self.target_speed: float = 0.0
        self.current_mass: float = 0.0
        self.radius: float = 0.0

        # === Budget & Validation ===
        self.max_mass_budget: float = class_def.get('max_mass', DEFAULT_MAX_MASS)
        self.mass_limits_ok: bool = True
        self.layer_status: Dict[LayerType, Dict[str, Any]] = {}
        self.construction_cost: Dict[str, int] = {}
        self._cached_summary = {}
        self._loading_warnings: List[str] = []

        # === Stat Dirty Flag (PROJ-253) ===
        self._stats_dirty: bool = True

        # === Resources ===
        self.resources = ResourceRegistry()
        self._resources_initialized: bool = False
        self._prev_max_resources: dict = {}
        self._prev_max_shields: int = 0

        # === Combat Stats (populated by ShipStatsCalculator) ===
        self.emissive_armor = 0
        self.shield_regenerating_armor = 0
        self.max_shields: int = 0
        self.current_shields: float = 0.0
        self.shield_regen_rate: float = 0.0
        self.shield_regen_cost: float = 0.0
        self.repair_rate: float = 0.0
        self.total_defense_score: float = 0.0
        self.baseline_to_hit_offense: float = 0.0
        self.fleet_attack_bonus: float = 0.0   # Set by FleetAuraManager._recalculate()
        self.fleet_defense_bonus: float = 0.0  # Set by FleetAuraManager._recalculate()
        self.total_maneuver_points: int = 0

        # === Strategic Stats (populated by ShipStatsCalculator) ===
        self.total_strategic_movement: float = 0.0
        self.warp_max_tonnage: float = 0.0
        self.warp_energy_cost: float = 0.0
        self.warp_resource_costs: Dict[str, float] = {}
        self.cargo_storage: Dict[str, float] = {}
        self.pod_storage_mass: float = 0.0

        # === Resource Consumption (populated by combat_endurance.py) ===
        self.fuel_consumption: float = 0.0
        self.ammo_consumption: float = 0.0
        self.energy_consumption: float = 0.0
        self.potential_fuel_consumption: float = 0.0
        self.potential_ammo_consumption: float = 0.0
        self.potential_energy_consumption: float = 0.0

        # === Crew Stats (populated by ShipStatsCalculator) ===
        self.crew_onboard: int = 0
        self.crew_required: int = 0

        # === Combat State ===
        self.is_alive: bool = True
        self.is_derelict: bool = False
        self.bridge_destroyed: bool = False
        self.retreat_status: Optional[str] = None

        # === AI & Targeting ===
        self.ai_strategy: str = "standard_ranged"
        self.source_file: Optional[str] = None
        self.current_target: Optional[Any] = None
        self.secondary_targets: List[Any] = []
        self.max_targets: int = CombatConstants.DEFAULT_MAX_TARGETS

        # === Formation & Physics ===
        self.formation = ShipFormation(self)
        self.turn_throttle: float = 1.0
        self.engine_throttle: float = 1.0
        self.current_speed: float = 0.0
        self.acceleration_rate: float = 0.0
        self.is_thrusting: bool = False

        # === Delegates (lazy init) ===
        self._component_manager = None
        self._combat_manager = None
        self.stats_calculator: Optional[ShipStatsCalculator] = None
        self._stat_querier: Optional[ShipStatQuerier] = None
        self._validator_helper: Optional[ShipValidatorHelper] = None



    def _equip_default_hull(self, class_def: dict) -> None:
        """Auto-equip the default hull component defined in the vehicle class.

        PROJ-225: Extracted from duplicated logic in __init__ and change_class.

        Args:
            class_def: Vehicle class definition dict (may contain 'default_hull_id')
        """
        default_hull_id = class_def.get('default_hull_id')
        if default_hull_id:
            hull_component = create_component(default_hull_id, registries=self._registries)
            if hull_component:
                # Direct append to avoid validation during init/class change
                self.layers[LayerType.HULL].components.append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = self
            else:
                logger.warning(f"Ship '{self.name}': Failed to create default hull '{default_hull_id}'")

    @property
    def registries(self) -> GameRegistries:
        """Get the registries instance (read-only access)."""
        return self._registries

    @property
    def mass(self) -> float:
        """Total mass (cached, updated by recalculate_stats)."""
        return self._cached_mass
    
    @mass.setter
    def mass(self, value: float) -> None:
        """Set cached mass value (used by ShipStatsCalculator and tests)."""
        self._cached_mass = value

    @property
    def max_hp(self) -> int:
        """Total HP of all components (cached, updated by recalculate_stats)."""
        return self._cached_max_hp
    
    @max_hp.setter
    def max_hp(self, value: int) -> None:
        """Set cached max_hp value."""
        self._cached_max_hp = value

    @property
    def hp(self) -> int:
        """Current HP of all components (cached, updated by recalculate_stats)."""
        return self._cached_hp
    
    @hp.setter
    def hp(self, value: int) -> None:
        """Set cached hp value."""
        self._cached_hp = value

    # =========================================================================
    # Component Manager (PROJ-240: extracted component lifecycle delegate)
    # =========================================================================

    @property
    def component_manager(self):
        """Get or create the ShipComponentManager for this ship.

        Lazy initialization avoids circular import issues.
        """
        if self._component_manager is None:
            from .ship_component_manager import ShipComponentManager
            self._component_manager = ShipComponentManager(self)
        return self._component_manager

    # =========================================================================
    # Combat Manager (PROJ-240: extracted combat orchestration delegate)
    # =========================================================================

    @property
    def combat_manager(self):
        """Get or create the ShipCombatManager for this ship.

        Lazy initialization avoids circular import issues.
        """
        if self._combat_manager is None:
            from .ship_combat_manager import ShipCombatManager
            self._combat_manager = ShipCombatManager(self)
        return self._combat_manager

    @property
    def combat_engine(self):
        """Get or create the ShipCombatEngine for this ship.

        Delegates to ShipCombatManager for lazy initialization.
        """
        return self.combat_manager.combat_engine

    def set_event_bus(self, bus: Any) -> None:
        """Set the event bus on the combat engine.

        PROJ-240: Facade to avoid 3-level delegation chain.
        """
        self.combat_manager.set_event_bus(bus)

    @property
    def just_fired_projectiles(self) -> List[Any]:
        """Firing results from last update tick."""
        return self.combat_manager.just_fired_projectiles

    @just_fired_projectiles.setter
    def just_fired_projectiles(self, value: List[Any]) -> None:
        self.combat_manager.just_fired_projectiles = value

    @property
    def comp_trigger_pulled(self) -> bool:
        """Whether the AI/player is requesting weapons fire."""
        return self.combat_manager.comp_trigger_pulled

    @comp_trigger_pulled.setter
    def comp_trigger_pulled(self, value: bool) -> None:
        self.combat_manager.comp_trigger_pulled = value

    @property
    def aim_point(self) -> Optional[Any]:
        """Current aiming point for weapons."""
        return self.combat_manager.aim_point

    @aim_point.setter
    def aim_point(self, value: Optional[Any]) -> None:
        self.combat_manager.aim_point = value

    @property
    def total_shots_fired(self) -> int:
        """Total shots fired across all weapons."""
        return self.combat_manager.total_shots_fired

    @total_shots_fired.setter
    def total_shots_fired(self, value: int) -> None:
        self.combat_manager.total_shots_fired = value

    def die(self) -> None:
        """Handle ship destruction."""
        self.combat_manager.die()

    # =========================================================================
    # Component Cache Management (PROJ-49 Phase 3)
    # =========================================================================

    def _invalidate_components_cache(self) -> None:
        """Mark component cache as dirty for lazy recalculation."""
        self.component_manager._invalidate_components_cache()
        self._stats_dirty = True  # PROJ-253: component change implies stat change

    @property
    def stat_querier(self) -> ShipStatQuerier:
        """Lazy-initialized stat querier for aggregation methods."""
        if self._stat_querier is None:
            self._stat_querier = ShipStatQuerier(self)
        return self._stat_querier

    @property
    def validator_helper(self) -> ShipValidatorHelper:
        """Lazy-initialized validator helper for validation methods."""
        if self._validator_helper is None:
            self._validator_helper = ShipValidatorHelper(self)
        return self._validator_helper

    @property
    def max_weapon_range(self) -> float:
        """Calculate maximum range of all equipped weapons."""
        return self.stat_querier.max_weapon_range

    def update(self, dt: float = 0.01, context: Optional[dict] = None) -> None:
        """Update ship state (physics, combat, resources)."""
        self.combat_manager.update(dt, context)

    def update_derelict_status(self) -> None:
        """Update derelict status based on functional capability."""
        self.combat_manager.update_derelict_status()

    def _initialize_layers(self) -> None:
        """Initialize or Re-initialize layers based on current ship_class."""
        # PROJ-42: Use registries (always set via fallback in __init__)
        class_def = self._registries.vehicle_classes.get(self.ship_class, {})
        self.layers: Dict[LayerType, LayerData] = {}
        layer_defs = class_def.get('layers', [])

        # Fallback if no layers defined in vehicle class
        if not layer_defs:
            layer_defs = [
                { "type": "CORE", "radius_pct": LayerDefaults.CORE_RADIUS_PCT, "restrictions": [] },
                { "type": "INNER", "radius_pct": LayerDefaults.INNER_RADIUS_PCT, "restrictions": [] },
                { "type": "OUTER", "radius_pct": LayerDefaults.OUTER_RADIUS_PCT, "restrictions": [] },
                { "type": "ARMOR", "radius_pct": 1.0, "restrictions": [] }
            ]

        # PROJ-84: Force HULL layer existence using LayerData factory
        self.layers[LayerType.HULL] = LayerData.create_hull()

        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                # Avoid overwriting HULL if it was somehow in data
                if l_type == LayerType.HULL: continue

                # PROJ-84: Use LayerData.from_definition() factory
                self.layers[l_type] = LayerData.from_definition(l_def)
            except KeyError:
                # PROJ-45: Enhanced logging with context for unknown layer types
                valid_layers = [lt.name for lt in LayerType]
                logger.warning(
                    f"Unknown LayerType '{l_type_str}' in ship class '{self.ship_class}'. "
                    f"Valid types: {valid_layers}. Skipping layer."
                )

        # Recalculate layer radii based on max_mass_pct (Area proportional to mass capacity)
        # Sort layers: HULL -> CORE -> INNER -> OUTER -> ARMOR
        layer_order = [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]

        # Filter layers present in this ship
        present_layers = [l for l in layer_order if l in self.layers]

        # Calculate total mass capacity (sum of max_mass_pct)
        # HULL is structural (radius 0), so excluded from area-proportional calculation
        total_capacity_pct = sum(self.layers[l].max_mass_pct for l in present_layers if l != LayerType.HULL)

        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                if l_type == LayerType.HULL:
                    self.layers[l_type].radius_pct = 0.0
                    continue
                cumulative_mass_pct += self.layers[l_type].max_mass_pct
                # Area = pi * r^2. Mass proportional to Area.
                self.layers[l_type].radius_pct = math.sqrt(cumulative_mass_pct / total_capacity_pct)
        else:
            # Fallback if no mass limits defined
            pass

    def change_class(self, new_class: str, migrate_components: bool = False) -> None:
        """
        Change the ship class and optionally migrate components.

        Args:
            new_class: The new class name (e.g. "Cruiser")
            migrate_components: If True, attempts to keep components and fit them into new layers.
                                If False, clears all components.
        """
        # PROJ-42: Use registries instead of provider
        if new_class not in self._registries.vehicle_classes:
            logger.error(f"Unknown class {new_class}")
            return

        old_components = []
        if migrate_components:
            # Flatten all components with their original layer
            for l_type, layer_data in self.layers.items():
                for comp in layer_data.components:
                    # DON'T migrate the hull! New class gets its own new hull.
                    # This matches the to_dict() logic and Task 2.1 intent.
                    if l_type == LayerType.HULL or comp.id.startswith('hull_'):
                        continue
                    old_components.append((comp, l_type))

        # Update Class
        self.ship_class = new_class
        class_def = self._registries.vehicle_classes.get(self.ship_class)
        if class_def is None:
            raise ValidationException(
                f"Unknown vehicle class '{self.ship_class}'",
                code=ErrorCode.VALIDATION_ERROR.value,
                context={"class": "Ship", "method": "change_class",
                         "ship_class": self.ship_class}
            )
        self.base_mass = 0.0  # Hull component provides mass via ShipStatsCalculator
        self.vehicle_type = class_def.get('type', "Ship")
        self.max_mass_budget = class_def.get('max_mass', DEFAULT_MAX_MASS)

        # Re-initialize Layers (clears self.layers)
        self._initialize_layers()

        # Auto-equip default Hull component for the NEW class (BUG-11 Fix)
        self._equip_default_hull(class_def)
        
        if migrate_components:
            # Attempt to restore components
            for comp, old_layer in old_components:
                added = False
                
                # 1. Try original layer
                if old_layer in self.layers:
                    if self.add_component(comp, old_layer):
                         added = True
                
                # 2. If failed, try all other layers in the new ship
                if not added:
                    for layer_type in self.layers.keys():
                        if layer_type == old_layer: continue 
                        
                        if self.add_component(comp, layer_type):
                            added = True
                            break
                
                if not added:
                    logger.warning(f"Could not fit component {comp.name} during refit to {new_class}")
        
        # Finally recalculate stats
        self.recalculate_stats()

    def _attach_component(self, component: Component, layer_type: LayerType, modifier_service=None) -> None:
        """Attach a validated component to a layer and apply mandatory modifiers.

        Delegates to ShipComponentManager.
        """
        self.component_manager._attach_component(component, layer_type, modifier_service)

    def add_component(self, component: Component, layer_type: LayerType) -> bool:
        """Validate and add a component to the specified layer."""
        return self.component_manager.add_component(component, layer_type)

    @property
    def cached_summary(self):
        """Cached dictionary of high-level ship stats (DPS, Speed, etc)."""
        return self._cached_summary

    def add_components_bulk(self, component: Component, layer_type: LayerType, count: int) -> int:
        """Add multiple copies of a component to the specified layer.

        Returns the number of components successfully added.
        """
        return self.component_manager.add_components_bulk(component, layer_type, count)

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """Remove a component from the specified layer by index."""
        return self.component_manager.remove_component(layer_type, index)

    def mark_stats_dirty(self) -> None:
        """Mark that ship stats need recalculation (PROJ-253).

        Called when component state changes (HP, operational status, toggle).
        """
        self._stats_dirty = True

    def recalculate_stats_if_dirty(self) -> None:
        """Recalculate stats only if dirty (PROJ-253).

        Used by the combat tick loop to avoid redundant recalculation.
        External callers should use recalculate_stats() which always runs.
        """
        if not self._stats_dirty:
            return
        self.recalculate_stats()

    def recalculate_stats(self) -> None:
        """
        Recalculates derived stats. Delegates to ShipStatsCalculator.
        Always runs the full pipeline (use recalculate_stats_if_dirty for conditional).
        """

        # PROJ-49: Invalidate component cache when stats recalculated
        self._invalidate_components_cache()

        # 1. Update components with current ship context
        for layer_data in self.layers.values():
            for comp in layer_data.components:
                # Ensure ship ref is set (Component.ship is always initialized, may be None)
                if comp.ship is None:
                    comp.ship = self
                comp.recalculate_stats()

        if not self.stats_calculator:
            # PROJ-42: Use registries instead of provider
            self.stats_calculator = ShipStatsCalculator(
                self._registries.vehicle_classes,
                resource_catalog=self._registries.resource_catalog,
            )

        self.stats_calculator.calculate(self)
        self._stats_dirty = False

    def get_missing_requirements(self) -> List[str]:
        """Check class requirements and return list of missing items based on abilities."""
        return self.validator_helper.get_missing_requirements()

    def get_validation_warnings(self) -> List[str]:
        """Check class requirements and return list of warnings (soft requirements)."""
        return self.validator_helper.get_validation_warnings()
    
    def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
        """Get total value of a specific ability across all components."""
        return self.stat_querier.get_ability_total(ability_name)

    def get_total_ability_value(self, ability_name: str, operational_only: bool = True) -> float:
        """
        Sum values from all matching abilities across all components.
        Uses polymorphic get_primary_value() interface for extensibility.

        Args:
            ability_name: Name of ability class to sum (e.g., 'CombatPropulsion')
            operational_only: If True, only count abilities from operational components

        Returns:
            Sum of primary value attribute from all matching abilities
        """
        return self.stat_querier.get_total_ability_value(ability_name, operational_only)

    def get_total_sensor_score(self) -> float:
        """Calculate total Targeting Score from all active sensors."""
        return self.stat_querier.get_total_sensor_score()

    def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
        """Get a resource-related stat by name and type.

        Provides typed accessor for dynamic resource attributes (e.g., fuel_consumption,
        ammo_endurance). This method replaces direct f-string getattr patterns for
        portability to statically-typed languages (C#/Rust).

        Args:
            resource_name: Resource name (e.g., 'fuel', 'ammo', 'energy')
            stat_type: Stat suffix (e.g., 'consumption', 'endurance', 'recharge',
                       'potential_consumption', 'net', 'max_usage')

        Returns:
            The stat value, or 0.0 if the attribute doesn't exist.
        """
        attr_name = f'{resource_name}_{stat_type}'
        return getattr(self, attr_name, 0.0)

    def get_total_ecm_score(self) -> float:
        """Calculate total Evasion/Defense Score from all active ECM/Electronics."""
        return self.stat_querier.get_total_ecm_score()

    # =========================================================================
    # Component Access Helper Methods (PROJ-240: delegates to ShipComponentManager)
    # =========================================================================

    def get_all_components(self) -> List[Component]:
        """Return a cached list of all components across all layers.

        PROJ-240: Returns defensive copy -- callers cannot corrupt internal cache.
        """
        return self.component_manager.get_all_components()

    def iter_components(self) -> Iterator[Tuple[LayerType, Component]]:
        """Iterate through (layer_type, component) tuples for all components."""
        return self.component_manager.iter_components()

    def get_components_by_ability(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> List[Component]:
        """Return all components that have a specific ability."""
        return self.component_manager.get_components_by_ability(ability_name, operational_only)

    def get_weapon_components_cached(self) -> List[Component]:
        """Get weapon components, cached until invalidated.

        PROJ-240: Uses dirty-flag invalidation instead of tick parameter.
        """
        return self.component_manager.get_weapon_components_cached()

    def get_components_by_layer(self, layer_type: LayerType) -> List[Component]:
        """Return all components in a specific layer."""
        return self.component_manager.get_components_by_layer(layer_type)

    def has_components(self) -> bool:
        """Check if ship has any components."""
        return self.component_manager.has_components()

    def find_component_with_index(
        self,
        predicate: Callable[[Component], bool]
    ) -> Optional[Tuple[LayerType, int, Component]]:
        """Find first component matching predicate, with its location."""
        return self.component_manager.find_component_with_index(predicate)

    def clear_non_hull_components(self) -> None:
        """Remove all components except hull."""
        self.component_manager.clear_non_hull_components()

    def check_validity(self) -> bool:
        """Check if the current ship design is valid."""
        return self.validator_helper.check_validity()

    # PROJ-225: Removed unused layers_dict property (DUP-SIM-010).
    # Ship serialization uses ShipSerializer.to_dict() exclusively.

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ship to dictionary.

        Returns:
            Dictionary representation of the ship including all layers,
            components, modifiers, and metadata.

        Raises:
            ValidationException: If component data cannot be serialized to JSON-compatible types.
        """
        return ShipSerializer.to_dict(self)

    @staticmethod
    def from_dict(
        data: Dict[str, Any],
        *,
        registries: Optional['GameRegistries'] = None
    ) -> 'Ship':
        """Create ship from dictionary.

        PROJ-50: Supports optional registries parameter for strict DI.

        Args:
            data: Dictionary containing serialized ship data including name,
                  ship_class, theme_id, layers, and component definitions.
            registries: Optional GameRegistries for DI (keyword-only).
                       Required for strict DI mode.

        Returns:
            Reconstructed Ship instance with all components and stats.

        Raises:
            ValidationException: If required fields are missing, data types are invalid,
                or component/modifier IDs are invalid.
        """
        return ShipSerializer.from_dict(data, registries=registries)


    

