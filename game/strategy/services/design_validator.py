"""DesignValidator — Validates ship/complex designs before build queue insertion.

Single source of truth for design validation at the strategy layer.
Uses ShipStatsCalculator for stats and the component registry for ability checks.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import extract_abilities_from_component

if TYPE_CHECKING:
    from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)


@dataclass
class DesignValidationResult:
    """Result of design validation."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)


class DesignValidator:
    """Validates designs for correctness before they enter build queues.

    Checks:
    - Crew housing: total CrewCapacity >= total CrewRequired
    - Life support: total LifeSupportCapacity >= total crew required
    - Layer mass budgets: each layer within vehicle class limits
    - Components exist in registry
    """

    def __init__(self, registries: 'GameRegistries') -> None:
        self._registries = registries

    def validate(self, design_data: Dict[str, Any]) -> DesignValidationResult:
        """Validate a design.

        Args:
            design_data: The design dict with 'layers', 'ship_class', etc.

        Returns:
            DesignValidationResult with errors and warnings.
        """
        result = DesignValidationResult()

        if not design_data:
            result.add_error("Design data is empty.")
            return result

        # Validate components exist
        self._check_components_exist(design_data, result)

        # Validate crew and life support
        self._check_crew_and_life_support(design_data, result)

        # Validate layer mass budgets
        self._check_layer_mass(design_data, result)

        return result

    def _check_components_exist(self, design_data: Dict, result: DesignValidationResult) -> None:
        """Check that all referenced components exist in the registry."""
        comp_registry = self._registries.components
        for comp in iter_components(design_data):
            comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
            if comp_id and comp_registry.get(comp_id) is None:
                result.add_error(f"Component '{comp_id}' not found in registry.")

    def _check_crew_and_life_support(self, design_data: Dict, result: DesignValidationResult) -> None:
        """Check crew housing and life support requirements."""
        from game.simulation.formula_system import FormulaEvaluator

        total_crew_required = 0.0
        total_crew_capacity = 0.0
        total_life_support = 0.0

        comp_registry = self._registries.components
        modifier_registry = self._registries.modifiers

        for comp in iter_components(design_data):
            if not isinstance(comp, dict):
                continue
            comp_id = comp.get('id', '')
            comp_def = comp_registry.get(comp_id)
            if comp_def is None:
                continue

            abilities = extract_abilities_from_component(comp, self._registries)

            # Get modifier multipliers for capacity scaling
            modifier_entries = comp.get('modifiers', [])
            from game.simulation.components.modifiers import calculate_stat_multipliers
            multipliers = calculate_stat_multipliers(modifier_entries, modifier_registry)
            crew_cap_mult = multipliers.get('crew_capacity_mult', 1.0)
            ls_cap_mult = multipliers.get('life_support_capacity_mult', 1.0)
            crew_req_mult = multipliers.get('crew_req_mult', 1.0)

            # CrewRequired — evaluate formulas if needed, apply crew_req_mult
            crew_req = abilities.get('CrewRequired', 0)
            if isinstance(crew_req, (int, float)):
                total_crew_required += crew_req * crew_req_mult
            elif isinstance(crew_req, str) and crew_req.startswith('='):
                val = float(FormulaEvaluator.safe_evaluate(crew_req[1:], {}, default=0))
                total_crew_required += val * crew_req_mult

            # CrewCapacity — scaled by crew_capacity_mult
            crew_cap = abilities.get('CrewCapacity', 0)
            if isinstance(crew_cap, (int, float)):
                total_crew_capacity += crew_cap * crew_cap_mult

            # LifeSupportCapacity — scaled by life_support_capacity_mult
            ls_cap = abilities.get('LifeSupportCapacity', 0)
            if isinstance(ls_cap, (int, float)):
                total_life_support += ls_cap * ls_cap_mult

        crew_deficit = total_crew_required - total_crew_capacity
        if crew_deficit > 0:
            result.add_error(f"Need {crew_deficit:.0f} more crew housing "
                           f"(required: {total_crew_required:.0f}, capacity: {total_crew_capacity:.0f}).")

        ls_deficit = total_crew_required - total_life_support
        if ls_deficit > 0:
            result.add_error(f"Need {ls_deficit:.0f} more life support "
                           f"(crew: {total_crew_required:.0f}, life support: {total_life_support:.0f}).")

    def _check_layer_mass(self, design_data: Dict, result: DesignValidationResult) -> None:
        """Check that each layer's component mass is within budget."""
        from game.simulation.components.modifiers import calculate_stat_multipliers

        ship_class = design_data.get('ship_class', '')
        vehicle_classes = self._registries.vehicle_classes
        comp_registry = self._registries.components
        modifier_registry = self._registries.modifiers

        # Find vehicle class definition for mass limits
        class_def = vehicle_classes.get(ship_class) if vehicle_classes else None
        if class_def is None:
            return  # Can't validate without class definition

        # Extract layer mass limits from vehicle class definition
        # Vehicle classes store layers as list of dicts or as a dict — handle both
        layer_limits = {}
        class_layers = None
        if hasattr(class_def, 'layers'):
            class_layers = class_def.layers
        elif isinstance(class_def, dict):
            class_layers = class_def.get('layers', {})

        if isinstance(class_layers, dict):
            layer_limits = class_layers
        elif isinstance(class_layers, list):
            for layer_entry in class_layers:
                if isinstance(layer_entry, dict) and 'name' in layer_entry:
                    layer_limits[layer_entry['name']] = layer_entry

        layers = design_data.get('layers', {})
        for layer_name, components in layers.items():
            if not isinstance(components, list):
                continue

            layer_def = layer_limits.get(layer_name, {})
            max_mass = layer_def.get('max_mass', 0) if isinstance(layer_def, dict) else 0
            if max_mass <= 0:
                continue  # No limit defined

            layer_mass = 0.0
            for comp in components:
                if not isinstance(comp, dict):
                    continue
                comp_id = comp.get('id', '')
                comp_def = comp_registry.get(comp_id)
                if comp_def is None:
                    continue

                raw_mass = comp_def.get('mass', 0) if isinstance(comp_def, dict) else getattr(comp_def, 'mass', 0)
                base_mass = float(raw_mass) if isinstance(raw_mass, (int, float)) else 0
                modifier_entries = comp.get('modifiers', [])
                multipliers = calculate_stat_multipliers(modifier_entries, modifier_registry)
                comp_mass = (base_mass + multipliers.get('mass_add', 0.0)) * multipliers.get('mass_mult', 1.0)
                layer_mass += comp_mass

            if layer_mass > max_mass:
                over = layer_mass - max_mass
                result.add_warning(f"{layer_name} layer over mass budget by {over:.0f}kg "
                                 f"({layer_mass:.0f}/{max_mass:.0f}).")
