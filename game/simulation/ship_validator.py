"""Ship design validation rules.

Phase 12: Refactored to use template method pattern from validation.base module.
Rules extend AdditionValidationRule or DesignValidationRule to reduce guard clause duplication.
"""
from typing import List, Optional

from game.simulation.components.component import Component, LayerType

# Import base classes from validation module (Phase 12 refactoring)
from game.simulation.validation.base import (
    ValidationResult,
    ValidationRule,
    DesignValidationRule,
    AdditionValidationRule
)


class LayerConstraintRule(AdditionValidationRule):
    """Validates that a component can be placed in the target layer."""

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        if layer_type not in ship.layers:
            result.add_error(f"Layer {layer_type.name} does not exist on {ship.ship_class}")
            return result

        if ship.vehicle_type not in component.allowed_vehicle_types:
            result.add_error(f"Component {component.name} not allowed on {ship.vehicle_type}")

        return result


class UniqueComponentRule(AdditionValidationRule):
    """Validates that unique components are not duplicated."""

    def _should_validate(self, component, layer_type) -> bool:
        """Only validate if component is present (layer not required for uniqueness check)."""
        return component is not None

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        if component.data.get('is_unique', False):
            for c in ship.get_all_components():
                if c.id == component.id:
                    result.add_error(f"Usage limit exceeded for unique component {component.name}")
                    return result
        return result


class ExclusiveGroupRule(AdditionValidationRule):
    """Validates that only one component from an exclusive group is present."""

    def _should_validate(self, component, layer_type) -> bool:
        """Only validate if component is present (layer not required)."""
        return component is not None

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        ex_group = component.data.get('exclusive_group')
        if ex_group:
            for c in ship.get_all_components():
                if c.data.get('exclusive_group') == ex_group:
                    result.add_error(f"Key component conflict: {ex_group}")
                    return result
        return result


class MountDependencyRule(AdditionValidationRule):
    """Validates that required mounts are available for components."""

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

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


class LayerRestrictionDefinitionRule(AdditionValidationRule):
    """Validates layer-specific restrictions (block/allow rules)."""

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        restrictions = ship.layers[layer_type]['restrictions']

        # [FIX for BUG-12] Handle HullOnly restriction
        if "HullOnly" in restrictions:
            if not component.id.startswith("hull_"):
                result.add_error(f"Layer {layer_type.name} only allows Hull components.")
                return result

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


class MassBudgetRule(DesignValidationRule):
    """Validates mass constraints for ship and layers.

    This rule can validate both addition (with component/layer) and design (without).
    Uses DesignValidationRule to always run, then checks for component/layer internally.
    """

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        # Check overall ship mass
        current_total = ship.current_mass
        if component:
            current_total += component.mass

        if current_total > ship.max_mass_budget:
            result.add_error(f"Mass budget exceeded for {ship.name}")

        # Check layer mass (only if component and layer provided)
        if component and layer_type:
            if layer_type in ship.layers:
                layer_data = ship.layers[layer_type]
                current_layer_mass = sum(c.mass for c in layer_data['components'])
                max_layer_mass = ship.max_mass_budget * layer_data.get('max_mass_pct', 1.0)

                if current_layer_mass + component.mass > max_layer_mass:
                    result.add_error(f"Mass budget exceeded for {layer_type.name}")

        return result


class ClassRequirementsRule(DesignValidationRule):
    """Validates class-specific requirements (crew, life support, etc.)."""

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)

        # Import internally to avoid circular imports
        from game.core.registry import RegistryManager
        from game.simulation.entities.ship_stats import ShipStatsCalculator

        classes = RegistryManager.instance().vehicle_classes
        class_def = classes.get(ship.ship_class, {})

        all_components = ship.get_all_components()
        if component:
            all_components = all_components + [component]

        stats_calculator = ShipStatsCalculator(classes)
        ability_totals = stats_calculator.calculate_ability_totals(all_components)

        # Ability-Based Requirements (Dynamic)
        if ability_totals.get('RequiresCommandAndControl', 0) > 0:
            if not ability_totals.get('CommandAndControl', 0):
                result.add_error("Needs Command capability")

        if ability_totals.get('RequiresCombatMovement', 0) > 0:
            if not ability_totals.get('CombatPropulsion', 0):
                result.add_error("Needs Combat propulsion")

        # Crew & Life Support
        crew_capacity = ability_totals.get('CrewCapacity', 0)
        if crew_capacity < 0:
            crew_capacity = 0

        life_support = ability_totals.get('LifeSupportCapacity', 0)
        crew_required = ability_totals.get('CrewRequired', 0)

        if crew_capacity < crew_required:
            result.add_error(f"Need {crew_required - crew_capacity} more crew housing")

        if crew_required > 0 and life_support < crew_required:
            result.add_error(f"Need {crew_required - life_support} more life support")

        return result


class ResourceDependencyRule(DesignValidationRule):
    """Validates that resource consumers have corresponding storage."""

    def _do_validate(self, ship, component: Optional[Component], layer_type: Optional[LayerType]) -> ValidationResult:
        result = ValidationResult(True)
        # Scan all components to determine needs vs sources
        needed_resources = set()
        stored_resources = set()

        all_components = ship.get_all_components()

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
                        if not isinstance(cons, dict):
                            continue
                        res_name = cons.get('resource')
                        if res_name:
                            needed_resources.add(res_name)

                if 'ResourceStorage' in abilities:
                    for store in abilities['ResourceStorage']:
                        if not isinstance(store, dict):
                            continue
                        res_name = store.get('resource')
                        capacity = store.get('amount', 0)
                        if capacity > 0 and res_name:
                            stored_resources.add(res_name)

        # Warnings for missing storage
        missing = needed_resources - stored_resources

        for res in sorted(missing):
            # Format nicely
            name = res.title()
            result.add_warning(f"Needs {name} Storage")

        return result


class ShipDesignValidator:
    """Validates ship designs using a set of rules."""

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
        """Validate adding a component to a ship."""
        final_result = ValidationResult(True)
        for rule in self.addition_rules:
            res = rule.validate(ship, component, layer_type)
            if not res.is_valid:
                final_result.is_valid = False
                final_result.errors.extend(res.errors)
        return final_result

    def validate_design(self, ship) -> ValidationResult:
        """Validate the complete ship design."""
        final_result = ValidationResult(True)
        for rule in self.design_rules:
            res = rule.validate(ship)
            # Accumulate errors (don't stop on first)
            if not res.is_valid:
                final_result.is_valid = False
                final_result.errors.extend(res.errors)
            final_result.warnings.extend(res.warnings)
        return final_result
