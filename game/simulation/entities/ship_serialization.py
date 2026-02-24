"""
ShipSerializer - Extracted serialization logic from Ship class.
Handles to_dict() and from_dict() operations for Ship entities.

PROJ-38: Added registries parameter for dependency injection.
"""
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING

from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode
from game.simulation.components.component import create_component
from game.core.constants import LayerType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries


class ShipSerializer:
    """Handles serialization and deserialization of Ship objects."""
    
    @staticmethod
    def to_dict(ship: 'Ship') -> Dict[str, Any]:
        """
        Serialize ship to dictionary.

        Args:
            ship: The Ship instance to serialize

        Returns:
            Dictionary representation of the ship
        """
        # logger.debug and logger.error are available from module-level logger

        try:
            logger.debug(f"ShipSerializer.to_dict starting for ship: {ship.name}")

            data = {
                "_format_version": "2.0",  # PROJ-42 Phase 4: Explicit format version
                "name": ship.name,
                "ship_class": ship.ship_class,
                "vehicle_type": ship.vehicle_type,  # Always set in Ship.__init__
                "theme_id": ship.theme_id,
                "team_id": ship.team_id,
                "color": ship.color,
                "ai_strategy": ship.ai_strategy,
                "layers": {},
                "resources": {
                    "fuel": ship.resources.get_value("fuel"),
                    "energy": ship.resources.get_value("energy"),
                    "ammo": ship.resources.get_value("ammo"),
                },
                "expected_stats": {
                    "max_hp": ship.max_hp,
                    "max_fuel": ship.resources.get_max_value("fuel"),
                    "max_energy": ship.resources.get_max_value("energy"),
                    "max_ammo": ship.resources.get_max_value("ammo"),
                    "max_speed": ship.max_speed,
                    "acceleration_rate": ship.acceleration_rate,
                    "turn_speed": ship.turn_speed,
                    "total_thrust": ship.total_thrust,
                    # PROJ-42 Phase 4: Strategic stats use getattr because they're set during
                    # recalculate_stats(), not in __init__. Default 0 is correct for uncalculated ships.
                    "strategic_movement": getattr(ship, 'total_strategic_movement', 0),
                    "mass": ship.mass,
                    "armor_hp_pool": ship.layers[LayerType.ARMOR].max_hp_pool if LayerType.ARMOR in ship.layers else 0,
                    "warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
                    "warp_energy_cost": getattr(ship, 'warp_energy_cost', 0),
                }
            }

            logger.debug(f"  vehicle_type: {data['vehicle_type']}")

            logger.debug(f"Basic ship data created. Processing {len(ship.layers)} layers...")

            for ltype, layer_data in ship.layers.items():
                logger.debug(f"  Processing layer: {ltype.name}, type: {type(layer_data)}")

                # Skip HULL layer from explicit serialization
                if ltype == LayerType.HULL:
                    logger.debug(f"    Skipping HULL layer")
                    continue

                components = layer_data.components
                logger.debug(f"    Layer has {len(components)} components")

                filter_comps = []
                for comp in components:
                    # Skip Hull components as safety (HULL layer already skipped)
                    if comp.id.startswith('hull_'):
                        continue
                    # Save as dict with modifiers
                    c_obj = {"id": comp.id}
                    if comp.modifiers:
                        c_obj["modifiers"] = [{"id": m.definition.id, "value": m.value} for m in comp.modifiers]
                    filter_comps.append(c_obj)

                data["layers"][ltype.name] = filter_comps
                logger.debug(f"    Serialized {len(filter_comps)} components for layer {ltype.name}")

            logger.debug(f"ShipSerializer.to_dict completed successfully")
            return data

        except Exception as e:  # Intentional broad catch: diagnostic logging before re-raise
            logger.error(f"ShipSerializer.to_dict FAILED: {e}")
            logger.exception("Ship serialization error")
            raise

    # Data-driven stat verification table: (key, getter, tolerance)
    _STAT_CHECKS = [
        ('max_hp',            lambda s: s.max_hp,                                                       1),
        ('max_fuel',          lambda s: s.resources.get_max_value("fuel"),                               1),
        ('max_energy',        lambda s: s.resources.get_max_value("energy"),                             1),
        ('max_ammo',          lambda s: s.resources.get_max_value("ammo"),                               1),
        ('max_speed',         lambda s: s.max_speed,                                                     0.1),
        ('acceleration_rate', lambda s: s.acceleration_rate,                                             0.001),
        ('turn_speed',        lambda s: s.turn_speed,                                                    0.1),
        ('total_thrust',      lambda s: s.total_thrust,                                                  1),
        ('mass',              lambda s: s.mass,                                                          1),
        ('armor_hp_pool',     lambda s: s.layers[LayerType.ARMOR].max_hp_pool if LayerType.ARMOR in s.layers else 0, 1),
    ]

    @staticmethod
    def from_dict(data: Dict[str, Any], *, registries: 'GameRegistries') -> 'Ship':
        """
        Create ship from dictionary.

        PROJ-50: Strict DI - registries is required.

        Args:
            data: Dictionary containing ship data
            registries: GameRegistries for DI (required).

        Returns:
            New Ship instance populated from the dictionary

        Raises:
            ValidationException: If registries is None
        """
        if registries is None:
            raise ValidationException(
                "registries is required for ShipSerializer.from_dict",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "ShipSerializer", "method": "from_dict", "parameter": "registries"}
            )
        # MUST remain a runtime import — ship.py imports ShipSerializer at module level
        from game.simulation.entities.ship import Ship

        name = data.get("name", "Unnamed")
        color_val = data.get("color", (200, 200, 200))
        color = tuple(color_val) if isinstance(color_val, list) else color_val

        # PROJ-38: Pass registries to Ship constructor
        s = Ship(name, 0, 0, color, data.get("team_id", 0),
                ship_class=data.get("ship_class", "Escort"),
                theme_id=data.get("theme_id", "Federation"),
                registries=registries)
        s.ai_strategy = data.get("ai_strategy", "standard_ranged")

        ShipSerializer._load_components(s, data, registries)
        s.recalculate_stats()
        ShipSerializer._restore_resources(s, data.get('resources', {}))
        ShipSerializer._verify_stats(s, data.get('expected_stats', {}))

        return s

    @staticmethod
    def _load_components(ship: 'Ship', data: Dict[str, Any], registries: 'GameRegistries') -> None:
        """Load and configure all components from serialized layer data."""
        comps = registries.components
        mods = registries.modifiers

        for l_name, comps_list in data.get("layers", {}).items():
            try:
                layer_type = LayerType[l_name]
            except KeyError:
                continue

            if layer_type not in ship.layers:
                continue

            for c_entry in comps_list:
                if not isinstance(c_entry, dict):
                    raise ValidationException(
                        f"Component entry must be dict, got {type(c_entry).__name__}",
                        code=ErrorCode.SCHEMA_VALIDATION_ERROR.value,
                        context={"expected_type": "dict", "actual_type": type(c_entry).__name__}
                    )

                comp_id = c_entry.get("id", "")
                if comp_id not in comps:
                    continue

                new_comp = comps[comp_id].clone()
                new_comp._registries = registries

                for m_dat in c_entry.get("modifiers", []):
                    mid = m_dat['id']
                    if mid in mods:
                        new_comp.add_modifier(mid, m_dat['value'])
                    else:
                        logger.warning(f"ShipSerializer: Modifier '{mid}' not found in registry, skipping")

                ship.add_component(new_comp, layer_type)

    @staticmethod
    def _restore_resources(ship: 'Ship', saved_resources: Dict[str, Any]) -> None:
        """Restore resource values from saved data."""
        if not saved_resources:
            return
        for resource_name, value in saved_resources.items():
            if value is not None:
                ship.resources.set_value(resource_name, value)

    @staticmethod
    def _verify_stats(ship: 'Ship', expected: Dict[str, Any]) -> None:
        """Verify loaded stats match expected stats and log mismatches.

        Uses the data-driven _STAT_CHECKS table instead of per-stat if-blocks.
        """
        if not expected:
            return

        mismatches = []
        for key, getter, tolerance in ShipSerializer._STAT_CHECKS:
            exp_val = expected.get(key)
            if exp_val:
                actual = getter(ship)
                if abs(actual - exp_val) > tolerance:
                    mismatches.append(f"{key}: got {actual}, expected {exp_val}")

        ship._loading_warnings = mismatches

        if mismatches:
            logger.warning(f"Ship '{ship.name}' stats mismatch after loading!")
            for m in mismatches:
                logger.warning(f"  - {m}")
