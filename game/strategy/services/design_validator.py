"""DesignValidator — Validates ship/complex designs before build queue insertion.

Delegates to the simulation-layer ShipDesignValidator for comprehensive
validation (crew, life support, combat movement, command & control, mass
budgets, layer restrictions, etc.). This ensures the build queue enforces
the exact same rules as the Design Workshop.
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, TYPE_CHECKING

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

    @property
    def has_issues(self) -> bool:
        """True if there are any errors or warnings."""
        return bool(self.errors or self.warnings)


class DesignValidator:
    """Validates designs for correctness before they enter build queues.

    Delegates to the simulation-layer ShipDesignValidator which checks:
    - Command & control: RequiresCommandAndControl → CommandAndControl
    - Combat movement: RequiresCombatMovement → CombatPropulsion
    - Crew housing: CrewCapacity >= CrewRequired
    - Life support: LifeSupportCapacity >= CrewRequired
    - Mass budgets: total mass and per-layer mass within vehicle class limits
    - Resource dependencies: resource consumers have storage (warnings)
    """

    def __init__(self, registries: 'GameRegistries') -> None:
        self._registries = registries

    def validate(self, design_data: Dict[str, Any]) -> DesignValidationResult:
        """Validate a design by instantiating it and running simulation-layer rules.

        Args:
            design_data: The design dict with 'layers', 'ship_class', etc.

        Returns:
            DesignValidationResult with errors and warnings.
        """
        result = DesignValidationResult()

        if not design_data:
            result.add_error("Design data is empty.")
            return result

        # Check component existence (sim validator doesn't check this)
        self._check_components_exist(design_data, result)

        # Instantiate Ship to get accurate stats and run full validation
        try:
            from game.simulation.entities.ship import Ship
            ship = Ship.from_dict(design_data, registries=self._registries)
            ship.recalculate_stats()
        except Exception as e:  # Intentional broad catch: Ship.from_dict may raise various persistence/validation errors; collect as error string in result.
            result.add_error(f"Could not load design: {e}")
            return result

        # Run the simulation-layer design validator (C&C, combat movement, crew,
        # life support, resource dependencies, total mass budget)
        try:
            from game.simulation.validation.ship_validator import ShipDesignValidator
            sim_validator = ShipDesignValidator(registries=self._registries)
            sim_result = sim_validator.validate_design(ship)

            for error in sim_result.errors:
                result.add_error(error)
            for warning in sim_result.warnings:
                result.add_warning(warning)

        except Exception as e:  # Intentional broad catch: ShipDesignValidator may raise unexpected types; collect as result error rather than crash the validator.
            # PROJ-381 Phase 2 (ERR-03-004): previously logged a warning
            # and discarded the failure, leaving is_valid=True even when
            # sim validation crashed. Surface as a result error so
            # callers see the validation signal.
            logger.warning(f"Simulation validator failed: {e}")
            result.add_error(f"Sim validation failed: {e}")

        # Check per-layer mass budgets (sim validator only checks total mass,
        # not per-layer percentages during design validation)
        self._check_layer_mass(ship, design_data, result)

        return result

    def _check_layer_mass(self, ship, design_data: Dict, result: DesignValidationResult) -> None:
        """Check per-layer mass budgets using the instantiated Ship."""
        ship_class = design_data.get('ship_class', '')
        vehicle_classes = self._registries.vehicle_classes
        if not vehicle_classes:
            return

        class_def = vehicle_classes.get(ship_class)
        if not isinstance(class_def, dict):
            return

        class_max_mass = class_def.get('max_mass', 0)
        if class_max_mass <= 0:
            return

        class_layers = class_def.get('layers', [])

        # Build lookup: layer_type_name -> max_mass_pct
        layer_pct_limits = {}
        for layer_entry in class_layers:
            if isinstance(layer_entry, dict) and 'type' in layer_entry:
                layer_pct_limits[layer_entry['type']] = layer_entry.get('max_mass_pct', 1.0)

        for layer_type, layer_data in ship.layers.items():
            layer_name = layer_type.name
            max_pct = layer_pct_limits.get(layer_name)
            if max_pct is None:
                continue

            max_layer_mass = class_max_mass * max_pct
            layer_mass = sum(c.mass for c in layer_data.components)

            if layer_mass > max_layer_mass + 0.5:
                over = layer_mass - max_layer_mass
                pct = (layer_mass / class_max_mass * 100) if class_max_mass > 0 else 0
                result.add_warning(
                    f"{layer_name} layer over mass budget by {over:.0f}kg "
                    f"({layer_mass:.0f}/{max_layer_mass:.0f}, "
                    f"{pct:.0f}% of {max_pct * 100:.0f}% limit)."
                )

    def _check_components_exist(self, design_data: Dict, result: DesignValidationResult) -> None:
        """Check that all referenced components exist in the registry."""
        from game.core.patterns.layer_iterator import iter_components

        comp_registry = self._registries.components
        for comp in iter_components(design_data):
            comp_id = comp.get('id', '') if isinstance(comp, dict) else str(comp)
            if comp_id and comp_registry.get(comp_id) is None:
                result.add_error(f"Component '{comp_id}' not found in registry.")
