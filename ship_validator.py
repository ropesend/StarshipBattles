
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from components import Component, LayerType, Weapon

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)

class ValidationRule(ABC):
    @abstractmethod
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        """
        Validate a specific component addition or the entire ship state.
        If component and layer_type are provided, validates the addition.
        Otherwise, validates the ship state.
        """
        pass

class LayerConstraintRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        if not component or not layer_type:
            return result

        if layer_type not in ship.layers:
             result.add_error(f"Layer {layer_type.name} does not exist on {ship.ship_class}")
             return result

        if ship.vehicle_type not in component.allowed_vehicle_types:
            result.add_error(f"Component {component.name} not allowed on {ship.vehicle_type}")
            
        return result

class UniqueComponentRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        if not component: 
            return result # This rule only checks addition for now, or could check full ship for duplicates

        if component.data.get('is_unique', False):
             for layer in ship.layers.values():
                 for c in layer['components']:
                     if c.id == component.id:
                         result.add_error(f"Usage limit exceeded for unique component {component.name}")
                         return result
        return result

class ExclusiveGroupRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        if not component:
            return result
        
        ex_group = component.data.get('exclusive_group')
        if ex_group:
             for layer in ship.layers.values():
                 for c in layer['components']:
                     if c.data.get('exclusive_group') == ex_group:
                         result.add_error(f"Key component conflict: {ex_group}")
                         return result
        return result

class MountDependencyRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        if not component or not layer_type:
            return result # TODO: Implement full ship scan for missing mounts

        req_mount = component.data.get('required_mount')
        if req_mount:
             # Count mounts vs existing users in THIS layer
             mount_count = 0
             user_count = 0
             
             target_layer_comps = ship.layers[layer_type]['components']
             for c in target_layer_comps:
                 if c.data.get('mount_type') == req_mount:
                     mount_count += 1
                 if c.data.get('required_mount') == req_mount:
                     user_count += 1
             
             if mount_count < (user_count + 1):
                 result.add_error(f"Missing required mount: {req_mount} in {layer_type.name}")
                 
        return result

class LayerRestrictionDefinitionRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        if not component or not layer_type:
            return result

        restrictions = ship.layers[layer_type]['restrictions']
        
        # 1. Process "Block" Rules (Blacklist)
        for r in restrictions:
            if r.startswith("block_classification:"):
                blocked_class = r.split(":")[1]
                if component.data.get('major_classification') == blocked_class:
                    result.add_error(f"Classification '{blocked_class}' blocked in this layer")
            elif r.startswith("block_type:"):
                blocked_type = r.split(":")[1]
                if component.type_str == blocked_type:
                     result.add_error(f"Type '{blocked_type}' blocked in this layer")
            elif r.startswith("block_id:"):
                blocked_id = r.split(":")[1]
                if component.id == blocked_id:
                     result.add_error(f"Component '{blocked_id}' blocked in this layer")

        # 2. Process "Allow" Rules (Whitelist)
        # Logic: If ANY allow rule exists, the component MUST match at least one of them.
        # If NO allow rules exist, everything is allowed (unless blocked above).
        
        allow_rules = [r for r in restrictions if r.startswith("allow_")]
        
        if allow_rules:
            allowed = False
            for r in allow_rules:
                if r.startswith("allow_classification:"):
                    target = r.split(":")[1]
                    if component.data.get('major_classification') == target:
                        allowed = True
                        break
                elif r.startswith("allow_type:"):
                    target = r.split(":")[1]
                    if component.type_str == target:
                        allowed = True
                        break
                elif r.startswith("allow_id:"):
                    target = r.split(":")[1]
                    if component.id == target:
                        allowed = True
                        break
            
            if not allowed:
                 result.add_error(f"Layer restricts components to specific types/classes only.")

        return result

class MassBudgetRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        
        # Check overall ship mass
        current_total = ship.current_mass
        if component:
             current_total += component.mass
             
        if current_total > ship.max_mass_budget:
            result.add_error(f"Mass budget exceeded for {ship.name}")

        # Check layer mass
        if component and layer_type:
             if layer_type in ship.layers:
                layer_data = ship.layers[layer_type]
                current_layer_mass = sum(c.mass for c in layer_data['components'])
                max_layer_mass = ship.max_mass_budget * layer_data.get('max_mass_pct', 1.0)
                
                if current_layer_mass + component.mass > max_layer_mass:
                    result.add_error(f"Mass budget exceeded for {layer_type.name}")

        return result


class ClassRequirementsRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        # This rule validates the whole design
        
        # Import internally to avoid circular imports
        from ship import VEHICLE_CLASSES
        from ship_stats import ShipStatsCalculator
        
        class_def = VEHICLE_CLASSES.get(ship.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        all_components = [c for layer in ship.layers.values() for c in layer['components']]
        
        stats_calculator = ShipStatsCalculator(VEHICLE_CLASSES)
        ability_totals = stats_calculator.calculate_ability_totals(all_components)
        
        for req_name, req_def in requirements.items():
            ability_name = req_def.get('ability', '')
            min_value = req_def.get('min_value', 0)
            
            if not ability_name:
                continue
            
            current_value = ability_totals.get(ability_name, 0)
            
            # Format name helper (duplicated from ship.py or we can move it)
            import re
            nice_name = re.sub(r'(?<!^)(?=[A-Z])', ' ', ability_name)

            if isinstance(min_value, bool):
                if min_value and not current_value:
                    result.add_error(f"Needs {nice_name}")
            elif isinstance(min_value, (int, float)):
                if current_value < min_value:
                    result.add_error(f"Needs {nice_name}")

        # Crew & Life Support
        crew_capacity = ability_totals.get('CrewCapacity', 0)
        if crew_capacity < 0: crew_capacity = 0
        
        life_support = ability_totals.get('LifeSupportCapacity', 0)
        crew_required = ability_totals.get('CrewRequired', 0)
        
        legacy_req = abs(min(0, ability_totals.get('CrewCapacity', 0)))
        crew_required += legacy_req
        
        if crew_capacity < crew_required:
             result.add_error(f"Need {crew_required - crew_capacity} more crew housing")

        if crew_required > 0 and life_support < crew_required:
            result.add_error(f"Need {crew_required - life_support} more life support")
            
        return result


class ResourceDependencyRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        # Scan all components to determine needs vs sources
        needs_fuel = False
        needs_ammo = False
        needs_energy_storage = False 
        
        has_fuel_storage = False
        has_ammo_storage = False
        has_energy_storage = False # Battery
        
        all_components = []
        for l in ship.layers.values():
            all_components.extend(l['components'])
            
        for c in all_components:
            # Check Needs
            # Check attributes first (runtime values), then data (definition values)
            # Fuel
            if getattr(c, 'fuel_cost', 0) > 0 or getattr(c, 'fuel_cost_per_sec', 0) > 0 or c.data.get('fuel_cost', 0) > 0:
                needs_fuel = True
                
            # Ammo
            if getattr(c, 'ammo_cost', 0) > 0 or c.data.get('ammo_cost', 0) > 0:
                needs_ammo = True
                
            # Energy
            if getattr(c, 'energy_cost', 0) > 0 or c.data.get('energy_cost', 0) > 0:
                needs_energy_storage = True
            
            # Check Abilities for invisible costs
            abilities = getattr(c, 'abilities', {})
            if 'EnergyConsumption' in abilities:
                 val = abilities['EnergyConsumption']
                 if isinstance(val, (int, float)) and val > 0:
                     needs_energy_storage = True
            
            # Check Sources (by type or capability)
            # resource_type might be an attribute on Tank, or just in data for others
            resource_type = getattr(c, 'resource_type', None)
            if not resource_type:
                resource_type = c.data.get('resource_type')
            
            # Fuel
            if resource_type == 'fuel': has_fuel_storage = True
            # Ammo
            if resource_type == 'ammo': has_ammo_storage = True
            # Energy
            if resource_type == 'energy': has_energy_storage = True
            
        # Warnings
        if needs_fuel and not has_fuel_storage:
             result.add_warning("Needs Fuel Storage")
             
        if needs_ammo and not has_ammo_storage:
             result.add_warning("Needs Ammo Storage")
             
        if needs_energy_storage and not has_energy_storage:
             result.add_warning("Needs Energy Storage")
             
        return result

class ShipDesignValidator:
    def __init__(self):
        self.addition_rules: List[ValidationRule] = [
            LayerConstraintRule(),
            UniqueComponentRule(),
            ExclusiveGroupRule(),
            MountDependencyRule(),
            LayerRestrictionDefinitionRule(),
            MassBudgetRule()
        ]
        self.design_rules: List[ValidationRule] = [
             ClassRequirementsRule(),

             ResourceDependencyRule(),
             # MassBudgetRule() could also apply here for final check
             MassBudgetRule() 
        ]

    def validate_addition(self, ship, component: Component, layer_type: LayerType) -> ValidationResult:
        final_result = ValidationResult(True)
        for rule in self.addition_rules:
            res = rule.validate(ship, component, layer_type)
            if not res.is_valid:
                final_result.is_valid = False
                final_result.errors.extend(res.errors)
        return final_result

    def validate_design(self, ship) -> ValidationResult:
        final_result = ValidationResult(True)
        for rule in self.design_rules:
            res = rule.validate(ship)
            # Accumulate errors but don't stop? Or stop on critical?
            # Usually accumulation is better for reporting.
            if not res.is_valid:
                final_result.is_valid = False
                final_result.errors.extend(res.errors)
            final_result.warnings.extend(res.warnings)
        return final_result

