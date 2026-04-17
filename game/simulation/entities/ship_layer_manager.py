"""Ship Layer Manager — delegate handling layer initialization and class changes.

Extracted from Ship (PROJ-260) to separate layer management concerns from
the Ship facade. Handles:
- Layer structure initialization from vehicle class definitions
- Default hull component equipping
- Ship class changes with optional component migration

The Ship class delegates to this manager for all layer-related operations
while retaining the public facade methods.
"""
import logging
import math
from typing import TYPE_CHECKING, Any, Dict

from game.core.constants import LayerType, LayerDefaults
from game.core.error_codes import ErrorCode
from game.core.exceptions import ValidationException
from game.simulation.entities.layer_data import LayerData
from game.simulation.components.component_loader import create_component
from game.simulation.physics_constants import DEFAULT_MAX_MASS

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship

logger = logging.getLogger(__name__)


class ShipLayerManager:
    """Manages ship layer structure, hull equipping, and class changes.

    Delegates:
        Ship._initialize_layers() → self.initialize_layers()
        Ship._equip_default_hull() → self.equip_default_hull()
        Ship.change_class() → self.change_class()
    """

    def __init__(self, ship: 'Ship'):
        self._ship = ship

    def initialize_layers(self) -> None:
        """Initialize or re-initialize layers based on current ship_class.

        Reads the vehicle class definition from registries, creates LayerData
        instances for each defined layer, forces HULL layer existence, and
        recalculates layer radii (area-proportional to mass capacity).
        """
        ship = self._ship
        class_def = ship._registries.vehicle_classes.get(ship.ship_class, {})
        ship.layers = {}
        layer_defs = class_def.get('layers', [])

        # Fallback if no layers defined in vehicle class
        if not layer_defs:
            layer_defs = [
                {"type": "CORE", "radius_pct": LayerDefaults.CORE_RADIUS_PCT, "max_mass_pct": 0.3, "restrictions": []},
                {"type": "INNER", "radius_pct": LayerDefaults.INNER_RADIUS_PCT, "max_mass_pct": 0.3, "restrictions": []},
                {"type": "OUTER", "radius_pct": LayerDefaults.OUTER_RADIUS_PCT, "max_mass_pct": 0.2, "restrictions": []},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.2, "restrictions": []},
            ]

        # Force HULL layer existence
        ship.layers[LayerType.HULL] = LayerData.create_hull()

        for l_def in layer_defs:
            l_type_str = l_def.get('type')
            try:
                l_type = LayerType[l_type_str]
                if l_type == LayerType.HULL:
                    continue
                ship.layers[l_type] = LayerData.from_definition(l_def)
            except KeyError:
                valid_layers = [lt.name for lt in LayerType]
                logger.warning(
                    f"Unknown LayerType '{l_type_str}' in ship class '{ship.ship_class}'. "
                    f"Valid types: {valid_layers}. Skipping layer."
                )

        # Recalculate layer radii (area-proportional to mass capacity)
        layer_order = [LayerType.HULL, LayerType.CORE, LayerType.INNER, LayerType.OUTER, LayerType.ARMOR]
        present_layers = [l for l in layer_order if l in ship.layers]
        total_capacity_pct = sum(
            ship.layers[l].max_mass_pct for l in present_layers if l != LayerType.HULL
        )

        if total_capacity_pct > 0:
            cumulative_mass_pct = 0.0
            for l_type in present_layers:
                if l_type == LayerType.HULL:
                    ship.layers[l_type].radius_pct = 0.0
                    continue
                cumulative_mass_pct += ship.layers[l_type].max_mass_pct
                ship.layers[l_type].radius_pct = math.sqrt(cumulative_mass_pct / total_capacity_pct)

    def equip_default_hull(self, class_def: dict) -> None:
        """Auto-equip the default hull component defined in the vehicle class.

        Args:
            class_def: Vehicle class definition dict (may contain 'default_hull_id')
        """
        ship = self._ship
        default_hull_id = class_def.get('default_hull_id')
        if default_hull_id:
            hull_component = create_component(default_hull_id, registries=ship._registries)
            if hull_component:
                ship.layers[LayerType.HULL].components.append(hull_component)
                hull_component.layer_assigned = LayerType.HULL
                hull_component.ship = ship
            else:
                logger.warning(f"Ship '{ship.name}': Failed to create default hull '{default_hull_id}'")

    def change_class(self, new_class: str, migrate_components: bool = False) -> None:
        """Change the ship class and optionally migrate components.

        Args:
            new_class: The new class name (e.g. "Cruiser")
            migrate_components: If True, attempts to keep components in new layers.
        """
        ship = self._ship

        if new_class not in ship._registries.vehicle_classes:
            logger.error(f"Unknown class {new_class}")
            return

        old_components = []
        if migrate_components:
            for l_type, layer_data in ship.layers.items():
                for comp in layer_data.components:
                    if l_type == LayerType.HULL or comp.id.startswith('hull_'):
                        continue
                    old_components.append((comp, l_type))

        # Update class identity
        ship.ship_class = new_class
        class_def = ship._registries.vehicle_classes.get(ship.ship_class)
        if class_def is None:
            raise ValidationException(
                f"Unknown vehicle class '{ship.ship_class}'",
                code=ErrorCode.VALIDATION_ERROR.value,
                context={"class": "Ship", "method": "change_class",
                         "ship_class": ship.ship_class}
            )
        ship.base_mass = 0.0
        ship.vehicle_type = class_def.get('type', "Ship")
        ship.max_mass_budget = class_def.get('max_mass', DEFAULT_MAX_MASS)

        # Re-initialize layers and hull
        self.initialize_layers()
        self.equip_default_hull(class_def)

        if migrate_components:
            for comp, old_layer in old_components:
                added = False
                if old_layer in ship.layers:
                    if ship.add_component(comp, old_layer):
                        added = True
                if not added:
                    for layer_type in ship.layers.keys():
                        if layer_type == old_layer:
                            continue
                        if ship.add_component(comp, layer_type):
                            added = True
                            break
                if not added:
                    logger.warning(f"Could not fit component {comp.name} during refit to {new_class}")

        ship.recalculate_stats()
