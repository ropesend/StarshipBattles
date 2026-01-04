
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from game.simulation.components.component import Component, LayerType  # Phase 7: Removed unused Weapon import

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
            elif r.startswith("block_id:"):
                blocked_id = r.split(":")[1]
                if component.id == blocked_id:
                     result.add_error(f"Component '{blocked_id}' blocked in this layer")
            elif r.startswith("deny_ability:"):
                denied_ability = r.split(":")[1]
                if component.has_ability(denied_ability):
                    result.add_error(f"Ability '{denied_ability}' blocked in this layer")

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
                elif r.startswith("allow_id:"):
                    target = r.split(":")[1]
                    if component.id == target:
                        allowed = True
                        break
                elif r.startswith("allow_ability:"):
                    target_ability = r.split(":")[1]
                    if component.has_ability(target_ability):
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
        from game.simulation.entities.ship import VEHICLE_CLASSES
        from ship_stats import ShipStatsCalculator
        
        class_def = VEHICLE_CLASSES.get(ship.ship_class, {})
        requirements = class_def.get('requirements', {})
        
        all_components = [c for layer in ship.layers.values() for c in layer['components']]
        if component:
            all_components.append(component)
            
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
        
        
        # legacy_req removed in Phase 9
        pass
        
        if crew_capacity < crew_required:
             result.add_error(f"Need {crew_required - crew_capacity} more crew housing")

        if crew_required > 0 and life_support < crew_required:
            result.add_error(f"Need {crew_required - life_support} more life support")
            
        return result


class ResourceDependencyRule(ValidationRule):
    def validate(self, ship, component: Optional[Component] = None, layer_type: Optional[LayerType] = None) -> ValidationResult:
        result = ValidationResult(True)
        # Scan all components to determine needs vs sources
        needed_resources = set()
        stored_resources = set()
        
        all_components = []
        for l in ship.layers.values():
            all_components.extend(l['components'])
            
        from game.simulation.systems.resource_manager import ResourceConsumption, ResourceStorage
            
        for c in all_components:
            # Use V2 Ability Instances for robust state checking
            if hasattr(c, 'ability_instances'):
                for ab in c.ability_instances:
                    # Check Consumption
                    if isinstance(ab, ResourceConsumption):
                        res_name = ab.resource_name
                        if res_name:
                            needed_resources.add(res_name)
                            
                    # Check Storage
                    elif isinstance(ab, ResourceStorage):
                        res_name = getattr(ab, 'resource_type', getattr(ab, 'resource_name', None))
                        # Use max_amount for capacity check (V2 standard)
                        capacity = getattr(ab, 'max_amount', 0)
                        
                        if capacity > 0 and res_name:
                            stored_resources.add(res_name)
            else:
                # Fallback for raw data or uninitialized components
                abilities = getattr(c, 'abilities', {})
                if 'ResourceConsumption' in abilities:
                    for cons in abilities['ResourceConsumption']:
                        if not isinstance(cons, dict): continue
                        res_name = cons.get('resource')
                        if res_name:
                            needed_resources.add(res_name)
                        
                if 'ResourceStorage' in abilities:
                    for store in abilities['ResourceStorage']:
                        if not isinstance(store, dict): continue
                        res_name = store.get('resource')
                        capacity = store.get('amount', 0)
                        if capacity > 0 and res_name:
                            stored_resources.add(res_name)
            
        # Warnings
        # Check specific resources we care about for UI consistency
        # Or just generic:
        missing = needed_resources - stored_resources
        
        # We can implement a filter if we only want to warn about specific ones, 
        # but generic is better for extensibility.
        # However, to preserve exact output format:
        
        for res in sorted(missing):
            # Format nicely
            name = res.title()
            result.add_warning(f"Needs {name} Storage")
              
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

