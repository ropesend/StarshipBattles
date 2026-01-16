import pygame
import random
import math
import typing
from typing import List, Dict, Tuple, Optional, Any, Union, Set, Iterator

from game.engine.physics import PhysicsBody
from game.simulation.components.component import (
    Component, LayerType, create_component
)
from game.core.logger import log_debug, log_info, log_warning, log_error
from game.core.registry import get_vehicle_classes, get_component_registry, get_modifier_registry
from game.simulation.ship_validator import ValidationResult
from .ship_stats import ShipStatsCalculator
from .ship_physics import ShipPhysicsMixin
from .ship_combat import ShipCombatMixin
from .ship_formation import ShipFormation
from game.simulation.systems.resource_manager import ResourceRegistry

# Re-export from ship_loader for backward compatibility
from .ship_loader import (
    get_or_create_validator,
    load_vehicle_classes,
    initialize_ship_data,
)


class Ship(PhysicsBody, ShipPhysicsMixin, ShipCombatMixin):
    def __init__(self, name: str, x: float, y: float, color: Union[Tuple[int, int, int], List[int]], 
                 team_id: int = 0, ship_class: str = "Escort", theme_id: str = "Federation"):
        super().__init__(x, y)
        self.name: str = name
        self.color: Union[Tuple[int, int, int], List[int]] = color
        self.team_id: int = team_id
        self.current_target: Optional[Any] = None
        self.secondary_targets: List[Any] = []  # List of additional targets
        self.max_targets: int = 1         # Default 1 target (primary only)
        self.ship_class: str = ship_class
        self.theme_id: str = theme_id
        
        # Get class definition (no fallback - data must be present)
        class_def = get_vehicle_classes().get(self.ship_class, {})

        # Initialize Layers dynamically from class definition
        self._initialize_layers()
        
        # Auto-equip default Hull component if defined for this class
        default_hull_id = class_def.get('default_hull_id')
        hull_equipped = False
        if default_hull_id:
            hull_component = create_component(default_hull_id)
            if hull_component:
                # Direct append to avoid validation during init
                self.layers[LayerType.HULL]['components'].append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = self
                hull_equipped = True
        
        # Stats - Cached values (populated by ShipStatsCalculator.calculate())
        self._cached_mass: float = 0.0
        self._cached_max_hp: int = 0
        self._cached_hp: int = 0
        # base_mass is always 0.0 - Hull component provides all base mass via ShipStatsCalculator
        self.base_mass: float = 0.0
        self.vehicle_type: str = class_def.get('type', "Ship")
        self.total_thrust: float = 0.0
        self.max_speed: float = 0.0
        self.turn_speed: float = 0.0
        self.target_speed: float = 0.0 # New Target Speed Control
        
        # Budget
        self.max_mass_budget: float = class_def.get('max_mass', 1000)
        
        # Stats initialized to 0.0 - Recalculate will populate these
        self.current_mass: float = 0.0 
        self.radius: float = 0.0 
        
        # Resources (New System)
        from game.simulation.systems.resource_manager import ResourceRegistry
        self.resources = ResourceRegistry()
        
        # Resource initialization tracking
        self._resources_initialized: bool = False
        
        # To-Hit stats
        self.total_defense_score = 0.0 # Score (Size + Maneuver + ECM)
        self.emissive_armor = 0
        self.crystalline_armor = 0
        
        # Shield Stats (Still specific for now)
        self.max_shields: int = 0
        self.current_shields: float = 0.0
        self.shield_regen_rate: float = 0.0
        self.shield_regen_cost: float = 0.0
        self.repair_rate: float = 0.0
        
        # New Stats
        self.mass_limits_ok: bool = True
        self.layer_status: Dict[LayerType, Dict[str, Any]] = {}
        self._cached_summary = {}  # Performance optimization for UI
        self._loading_warnings: List[str] = []
        
        self.is_alive: bool = True
        self.is_derelict: bool = False
        self.bridge_destroyed: bool = False
        
        # AI Strategy
        self.ai_strategy: str = "standard_ranged"
        self.source_file: Optional[str] = None
        
        # Formation (Composition - delegates to ShipFormation)
        self.formation = ShipFormation(self)
        self.turn_throttle: float = 1.0          # Multiplier for max speed (0.0 to 1.0)
        self.engine_throttle: float = 1.0        # Multiplier for max speed (0.0 to 1.0)
        
        # Arcade Physics
        self.current_speed: float = 0.0
        self.acceleration_rate: float = 0.0
        self.is_thrusting: bool = False
        self.comp_trigger_pulled: bool = False
        
        # Aiming
        self.aim_point: Optional[Any] = None
        self.just_fired_projectiles: List[Any] = []
        self.total_shots_fired: int = 0
        
        # To-Hit Calculation Stats
        self.to_hit_profile: float = 1.0       # Defensive Multiplier
        self.baseline_to_hit_offense: float = 1.0 # Offensive Multiplier
        
        # Initialize helper (lazy or eager)
        self.stats_calculator: Optional[ShipStatsCalculator] = None



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
    # Formation Delegation Properties (backward compatibility)
    # =========================================================================
    
    @property
    def formation_master(self) -> Optional[Any]:
        """Reference to formation leader (delegates to formation.master)."""
        return self.formation.master
    
    @formation_master.setter
    def formation_master(self, value: Optional[Any]) -> None:
        self.formation.master = value
    
    @property
    def formation_offset(self) -> Optional[Any]:
        """Position offset relative to master (delegates to formation.offset)."""
        return self.formation.offset
    
    @formation_offset.setter
    def formation_offset(self, value: Optional[Any]) -> None:
        self.formation.offset = value
    
    @property
    def formation_rotation_mode(self) -> str:
        """Rotation mode: 'relative' or 'fixed' (delegates to formation.rotation_mode)."""
        return self.formation.rotation_mode
    
    @formation_rotation_mode.setter
    def formation_rotation_mode(self, value: str) -> None:
        self.formation.rotation_mode = value
    
    @property
    def formation_members(self) -> List[Any]:
        """List of followers (delegates to formation.members)."""
        return self.formation.members
    
    @formation_members.setter
    def formation_members(self, value: List[Any]) -> None:
        self.formation.members = value
    
    @property
    def in_formation(self) -> bool:
        """Whether ship is holding formation (delegates to formation.active)."""
        return self.formation.active
    
    @in_formation.setter
    def in_formation(self, value: bool) -> None:
        self.formation.active = value

    @property
    def max_weapon_range(self) -> float:
        """Calculate maximum range of all equipped weapons."""
        from game.simulation.components.abilities import SeekerWeaponAbility, WeaponAbility
        max_rng = 0.0
        for comp in self.get_all_components():
            for ab in comp.ability_instances:
                # Polymorphic check using isinstance (Phase 2 Task 2.5)
                if not isinstance(ab, WeaponAbility):
                    continue

                rng = getattr(ab, 'range', 0.0)
                # For SeekerWeapons, calculate range from endurance if not set
                if isinstance(ab, SeekerWeaponAbility):
                    if rng <= 0 and hasattr(ab, 'projectile_speed') and hasattr(ab, 'endurance'):
                        rng = ab.projectile_speed * ab.endurance

                if rng > max_rng:
                    max_rng = rng

        return max_rng if max_rng > 0 else 0.0

    def update(self, dt: float = 0.01, context: Optional[dict] = None) -> None:
        """
        Update ship state (physics, combat, resources).
        """
        if not self.is_alive:
            return

        # 1. Update Resources (Regeneration) - Tick-based
        if self.resources:
             self.resources.update()

        # 2. Update Components (Consumption, Cooldowns) - Tick-based
        for comp in self.get_all_components():
            if comp.is_active:
                comp.update()
        
        # 3. Physics (Thrust calc handling operational engines)
        self.update_physics_movement()
        
        # PhysicsBody.update() (Applies velocity to position)
        super().update(dt)
        
        # 4. Combat Cooldowns (Shields/Repair/Custom Logic)
        self.update_combat_cooldowns()

        # 5. Firing Logic (Link AI trigger to Combat System)
        if self.comp_trigger_pulled:
            new_attacks = self.fire_weapons(context)
            if new_attacks:
                self.just_fired_projectiles.extend(new_attacks)

    def update_derelict_status(self) -> None:
        """
        Update derelict status based on component requirements.

        Ship becomes derelict when declared requirements are not met:
        1. If ANY component has RequiresCommandAndControl ability:
           → Must have operational CommandAndControl component
        2. If ANY component has CrewRequired ability:
           → Must have sufficient CrewCapacity

        Ships without requirements (e.g., autonomous drones, test ships)
        operate normally regardless of available components.
        """
        # Check 1: CommandAndControl requirement (conditional)
        # Only check if ANY component declares this requirement
        requires_command = self.get_total_ability_value('RequiresCommandAndControl') > 0

        if requires_command:
            # Use get_components_by_ability with operational_only=True
            has_command = len(self.get_components_by_ability('CommandAndControl', operational_only=True)) > 0

            if not has_command:
                if not self.is_derelict:
                    log_info(f"{self.name} has become DERELICT (Command and Control lost)")
                self.is_derelict = True
                self.bridge_destroyed = True
                return

        # Check 2: Crew capacity requirement (conditional)
        # Only check if ANY component declares crew requirement
        crew_required = self.get_total_ability_value('CrewRequired')

        if crew_required > 0:
            crew_capacity = self.get_total_ability_value('CrewCapacity')

            if crew_required > crew_capacity:
                if not self.is_derelict:
                    log_info(f"{self.name} has become DERELICT (Insufficient crew capacity)")
                self.is_derelict = True
                return

        # All checks passed - ship is operational
        self.is_derelict = False
        self.bridge_destroyed = False

    def _initialize_layers(self) -> None:
        """Initialize or Re-initialize layers based on current ship_class."""
        class_def = get_vehicle_classes().get(self.ship_class, {})
        self.layers = {}
        layer_defs = class_def.get('layers', [])
        
        # Fallback if no layers defined in vehicle class
        if not layer_defs:
            layer_defs = [
                { "type": "CORE", "radius_pct": 0.2, "restrictions": [] },
                { "type": "INNER", "radius_pct": 0.5, "restrictions": [] },
                { "type": "OUTER", "radius_pct": 0.8, "restrictions": [] },
                { "type": "ARMOR", "radius_pct": 1.0, "restrictions": [] }
            ]
            
        # [NEW] Force HULL layer existence (Index 0)
        self.layers[LayerType.HULL] = {
            'components': [],
            'radius_pct': 0.0,
            'restrictions': ['HullOnly'],
            'max_mass_pct': 100.0,
            'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
        }

        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                # Avoid overwriting HULL if it was somehow in data
                if l_type == LayerType.HULL: continue
                
                self.layers[l_type] = {
                    'components': [],
                    'radius_pct': l_def.get('radius_pct', 0.5),
                    'restrictions': l_def.get('restrictions', []),
                    'max_mass_pct': l_def.get('max_mass_pct', 1.0),
                    'hp_pool': 0, 'max_hp_pool': 0, 'mass': 0, 'hp': 0
                }
            except KeyError:
                log_warning(f"Unknown LayerType {l_type_str} in class {self.ship_class}")

        # Recalculate layer radii based on max_mass_pct (Area proportional to mass capacity)
        # Sort layers: HULL -> CORE -> INNER -> OUTER -> ARMOR
        layer_order = [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        
        # Filter layers present in this ship
        present_layers = [l for l in layer_order if l in self.layers]
        
        # Calculate total mass capacity (sum of max_mass_pct)
        # HULL is structural (radius 0), so excluded from area-proportional calculation
        total_capacity_pct = sum(self.layers[l]['max_mass_pct'] for l in present_layers if l != LayerType.HULL)
        
        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                if l_type == LayerType.HULL:
                    self.layers[l_type]['radius_pct'] = 0.0
                    continue
                cumulative_mass_pct += self.layers[l_type]['max_mass_pct']
                # Area = pi * r^2. Mass proportional to Area.
                self.layers[l_type]['radius_pct'] = math.sqrt(cumulative_mass_pct / total_capacity_pct)
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
        if new_class not in get_vehicle_classes():
            log_error(f"Unknown class {new_class}")
            return

        old_components = []
        if migrate_components:
            # Flatten all components with their original layer
            for l_type, data in self.layers.items():
                for comp in data['components']:
                    # DON'T migrate the hull! New class gets its own new hull.
                    # This matches the to_dict() logic and Task 2.1 intent.
                    if l_type == LayerType.HULL or comp.id.startswith('hull_'):
                        continue
                    old_components.append((comp, l_type))
        
        # Update Class
        self.ship_class = new_class
        class_def = get_vehicle_classes()[self.ship_class]
        self.base_mass = 0.0  # Hull component provides mass via ShipStatsCalculator
        self.vehicle_type = class_def.get('type', "Ship")
        self.max_mass_budget = class_def.get('max_mass', 1000)
        
        # Re-initialize Layers (clears self.layers)
        self._initialize_layers()
        
        # Auto-equip default Hull component for the NEW class (BUG-11 Fix)
        default_hull_id = class_def.get('default_hull_id')
        if default_hull_id:
            hull_component = create_component(default_hull_id)
            if hull_component:
                # Direct append to avoid validation during class change
                self.layers[LayerType.HULL]['components'].append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = self
        
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
                    log_warning(f"Could not fit component {comp.name} during refit to {new_class}")
        
        # Finally recalculate stats
        self.recalculate_stats()

    def add_component(self, component: Component, layer_type: LayerType) -> bool:
        """Validate and add a component to the specified layer."""
        if component is None:
            log_error("Attempted to add None component to ship")
            return False

        result = get_or_create_validator().validate_addition(self, component, layer_type)

        if not result.is_valid:
            for err in result.errors:
                log_error(err)
            return False

        self.layers[layer_type]['components'].append(component)
        component.layer_assigned = layer_type
        component.ship = self
        component.recalculate_stats()
        # Apply mandatory modifiers (e.g., size mount) immediately upon addition
        from game.simulation.services.modifier_service import ModifierService
        ModifierService.ensure_mandatory_modifiers(component)
        self._cached_summary = {}  # Invalidate cache
        
        # Update Stats
        self.recalculate_stats()
        return True

    @property
    def cached_summary(self):
        """Cached dictionary of high-level ship stats (DPS, Speed, etc)."""
        return self._cached_summary

    def add_components_bulk(self, component: Component, layer_type: LayerType, count: int) -> int:
        """
        Add multiple copies of a component to the specified layer.
        Performs validation for each addition but defers full ship stat recalculation until the end.
        Returns the number of components successfully added.
        """
        added_count = 0
        
        # Loop to add
        for _ in range(count):
            # Must clone for each new instance
            new_comp = component.clone()
            
            # Use the global validator
            result = get_or_create_validator().validate_addition(self, new_comp, layer_type)
            if not result.is_valid:
                # Stop adding if we hit a limit
                if added_count == 0:
                    # If the very first one fails, log errors
                    for err in result.errors:
                        log_error(err)
                break
                
            self.layers[layer_type]['components'].append(new_comp)
            new_comp.layer_assigned = layer_type
            new_comp.ship = self
            new_comp.recalculate_stats()
            # Apply mandatory modifiers (e.g., size mount) immediately upon addition
            from game.simulation.services.modifier_service import ModifierService
            ModifierService.ensure_mandatory_modifiers(new_comp)
            added_count += 1
            
        if added_count > 0:
            self.recalculate_stats()
            
        return added_count

    def remove_component(self, layer_type: LayerType, index: int) -> Optional[Component]:
        """Remove a component from the specified layer by index."""
        if 0 <= index < len(self.layers[layer_type]['components']):
            comp = self.layers[layer_type]['components'].pop(index)
            self.recalculate_stats()
            return comp
        return None

    def recalculate_stats(self) -> None:
        """
        Recalculates derived stats. Delegates to ShipStatsCalculator.
        """
        # 1. Update components with current ship context
        for layer_data in self.layers.values():
            for comp in layer_data['components']:
                # Ensure ship ref is set
                if not getattr(comp, 'ship', None): comp.ship = self
                comp.recalculate_stats()

        if not self.stats_calculator:
             from .ship_stats import ShipStatsCalculator
             self.stats_calculator = ShipStatsCalculator(get_vehicle_classes())
        
        self.stats_calculator.calculate(self)

    def get_missing_requirements(self) -> List[str]:
        """Check class requirements and return list of missing items based on abilities."""
        # Use centralized validator
        result = get_or_create_validator().validate_design(self)
        if result.is_valid:
            return []
        # Return all errors as list of strings
        return [f"⚠ {err}" for err in result.errors]

    def get_validation_warnings(self) -> List[str]:
        """Check class requirements and return list of warnings (soft requirements)."""
        result = get_or_create_validator().validate_design(self)
        return result.warnings
    
    def _format_ability_name(self, ability_name: str) -> str:
        """Convert ability ID to readable name."""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)
    
    def get_ability_total(self, ability_name: str) -> Union[float, int, bool]:
        """Get total value of a specific ability across all components."""
        all_components = self.get_all_components()

        if not self.stats_calculator:
             self.stats_calculator = ShipStatsCalculator(get_vehicle_classes())
             
        totals = self.stats_calculator.calculate_ability_totals(all_components)
        return totals.get(ability_name, 0)
    
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
        total = 0.0
        for comp in self.get_all_components():
            if operational_only and not comp.is_operational:
                continue
            for ab in comp.get_abilities(ability_name):
                total += ab.get_primary_value()
        return total
    
    def get_total_sensor_score(self) -> float:
        """Calculate total Targeting Score from all active sensors.
        
        Uses stack_group rules:
        - Same stack_group: MAX (redundancy)
        - Different stack_groups: MULTIPLY (stacking)
        """
        result = self.get_ability_total('ToHitAttackModifier')
        return float(result) if isinstance(result, (int, float)) else 0.0

    def get_total_ecm_score(self) -> float:
        """Calculate total Evasion/Defense Score from all active ECM/Electronics.
        
        Uses stack_group rules:
        - Same stack_group: MAX (redundancy)
        - Different stack_groups: MULTIPLY (stacking)
        """
        result = self.get_ability_total('ToHitDefenseModifier')
        return float(result) if isinstance(result, (int, float)) else 0.0

    # =========================================================================
    # Component Access Helper Methods (Phase 2 Consolidation)
    # =========================================================================

    def get_all_components(self) -> List[Component]:
        """
        Return a list of all components across all layers.

        Returns:
            List of Component instances from all layers (HULL, CORE, INNER, OUTER, ARMOR).
            Returns a fresh list each call (not a reference to internal storage).
        """
        result = []
        for layer_data in self.layers.values():
            result.extend(layer_data['components'])
        return result

    def iter_components(self) -> Iterator[Tuple[LayerType, Component]]:
        """
        Iterate through (layer_type, component) tuples for all components.

        Yields:
            Tuple of (LayerType, Component) for each component in the ship.
            Iterates through layers in dictionary order.
        """
        for layer_type, layer_data in self.layers.items():
            for component in layer_data['components']:
                yield layer_type, component

    def get_components_by_ability(
        self,
        ability_name: str,
        operational_only: bool = True
    ) -> List[Component]:
        """
        Return all components that have a specific ability.

        Args:
            ability_name: Name of the ability to search for (e.g., 'WeaponAbility').
            operational_only: If True (default), only return operational components.
                            If False, return all components with the ability.

        Returns:
            List of Component instances that have the specified ability.
        """
        result = []
        for layer_data in self.layers.values():
            for comp in layer_data['components']:
                if operational_only and not comp.is_operational:
                    continue
                if comp.has_ability(ability_name):
                    result.append(comp)
        return result

    def get_components_by_layer(self, layer_type: LayerType) -> List[Component]:
        """
        Return all components in a specific layer.

        Args:
            layer_type: The LayerType to get components from.

        Returns:
            List of Component instances in the specified layer.
            Returns empty list if layer doesn't exist or has no components.
            Returns a fresh list each call (not a reference to internal storage).
        """
        layer_data = self.layers.get(layer_type)
        if layer_data is None:
            return []
        return list(layer_data['components'])

    def has_components(self) -> bool:
        """
        Check if ship has any components.

        Returns:
            True if ship has at least one component in any layer, False otherwise.
        """
        for layer_data in self.layers.values():
            if layer_data['components']:
                return True
        return False

    def check_validity(self) -> bool:
        """Check if the current ship design is valid."""
        self.recalculate_stats()
        result = get_or_create_validator().validate_design(self)
        # Check for mass errors specifically for UI feedback flag
        self.mass_limits_ok = not any("Mass budget exceeded" in e for e in result.errors)
        return result.is_valid

    @property
    def layers_dict(self) -> Dict[str, List[Any]]:
        """Helper for JSON serialization."""
        d = {}
        for l_type, data in self.layers.items():
            d[l_type.name] = []
            for comp in data['components']:
                # Minimal serialization: ID + Modifiers
                c_data = {
                    "id": comp.id,
                    "modifiers": []
                }
                for m in comp.modifiers:
                    c_data["modifiers"].append({"id": m.definition.id, "value": m.value})
                d[l_type.name].append(c_data)
        return d

    def to_dict(self) -> Dict[str, Any]:
        """Serialize ship to dictionary."""
        from .ship_serialization import ShipSerializer
        return ShipSerializer.to_dict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ship':
        """Create ship from dictionary."""
        from .ship_serialization import ShipSerializer
        return ShipSerializer.from_dict(data)




    

