"""
ShipSerializer - Extracted serialization logic from Ship class.
Handles to_dict() and from_dict() operations for Ship entities.

PROJ-38: Added registries parameter for dependency injection.
"""
from typing import Dict, Any, Optional, TYPE_CHECKING

from game.simulation.components.component import create_component
from game.core.constants import LayerType
from game.core.registry import get_default_registry_provider, get_default_registries
from game.core.logger import log_warning

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
        from game.core.logger import log_debug, log_error

        try:
            log_debug(f"ShipSerializer.to_dict starting for ship: {ship.name}")

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
                    "armor_hp_pool": ship.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in ship.layers else 0,
                    "warp_max_tonnage": getattr(ship, 'warp_max_tonnage', 0),
                    "warp_energy_cost": getattr(ship, 'warp_energy_cost', 0),
                    "strategic_fuel_per_hex": getattr(ship, 'strategic_fuel_per_hex', 0),
                }
            }

            log_debug(f"  vehicle_type: {data['vehicle_type']}")

            log_debug(f"Basic ship data created. Processing {len(ship.layers)} layers...")

            for ltype, layer_data in ship.layers.items():
                log_debug(f"  Processing layer: {ltype.name}, type: {type(layer_data)}")

                # Skip HULL layer from explicit serialization
                if ltype == LayerType.HULL:
                    log_debug(f"    Skipping HULL layer")
                    continue

                if not isinstance(layer_data, dict):
                    log_error(f"    ERROR: layer_data is not a dict! Type: {type(layer_data)}, Value: {layer_data}")
                    continue

                components = layer_data.get('components', [])
                log_debug(f"    Layer has {len(components)} components")

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
                log_debug(f"    Serialized {len(filter_comps)} components for layer {ltype.name}")

            log_debug(f"ShipSerializer.to_dict completed successfully")
            return data

        except Exception as e:
            log_error(f"ShipSerializer.to_dict FAILED: {e}")
            import traceback
            log_error(traceback.format_exc())
            raise

    @staticmethod
    def from_dict(data: Dict[str, Any], *, registries: Optional['GameRegistries'] = None) -> 'Ship':
        """
        Create ship from dictionary.

        PROJ-38: Supports dependency injection via registries parameter.

        Args:
            data: Dictionary containing ship data
            registries: Optional GameRegistries for DI. If None, uses default registries.

        Returns:
            New Ship instance populated from the dictionary
        """
        # Import here to avoid circular dependency
        from game.simulation.entities.ship import Ship

        # PROJ-42 Phase 4: Check format version (v1.x had string component format, no longer supported)
        version = data.get("_format_version", "1.0")
        # Allow v1.x data that happens to use dict format (graceful migration)
        # Version check is informational - the dict check in component loading is the actual enforcement

        # PROJ-38: Resolve registries for component/modifier operations
        # PROJ-45: Also catches StateException for new exception hierarchy
        if registries is None:
            from game.core.exceptions import StateException
            try:
                registries = get_default_registries()
            except (RuntimeError, StateException):
                # Default registries not set - will use legacy functions below
                pass

        name = data.get("name", "Unnamed")
        color_val = data.get("color", (200, 200, 200))
        # Ensure color is tuple
        color: tuple
        if isinstance(color_val, list):
            color = tuple(color_val)
        else:
            color = color_val  # type: ignore

        # PROJ-38: Pass registries to Ship constructor
        s = Ship(name, 0, 0, color, data.get("team_id", 0),
                ship_class=data.get("ship_class", "Escort"),
                theme_id=data.get("theme_id", "Federation"),
                registries=registries)
        s.ai_strategy = data.get("ai_strategy", "standard_ranged")
        
        for l_name, comps_list in data.get("layers", {}).items():
            layer_type = None
            try:
                layer_type = LayerType[l_name]
            except KeyError:
                continue
                
            # Skip if this layer is not defined in the ship's class
            if layer_type not in s.layers:
                continue
            
            for c_entry in comps_list:
                # PROJ-42 Phase 4: Removed legacy string format support
                # Components must be dict format: {"id": "...", "modifiers": [...]}
                if not isinstance(c_entry, dict):
                    raise ValueError(f"Component entry must be dict, got {type(c_entry).__name__}")

                comp_id = c_entry.get("id", "")
                modifiers_data = c_entry.get("modifiers", [])

                # PROJ-38: Use injected registries if available, else provider
                if registries is not None:
                    comps = registries.components
                    mods = registries.modifiers
                else:
                    provider = get_default_registry_provider()
                    comps = provider.get_components()
                    mods = provider.get_modifiers()

                if comp_id in comps:
                    # PROJ-38: Clone component and ensure it has registries
                    new_comp = comps[comp_id].clone()
                    if registries is not None:
                        new_comp._registries = registries

                    # Apply Modifiers
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in mods:
                            new_comp.add_modifier(mid, mval)
                        else:
                            log_warning(f"ShipSerializer: Modifier '{mid}' not found in registry, skipping")

                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
    
        # Restore resource values if saved
        saved_resources = data.get('resources', {})
        if saved_resources:
            for resource_name, value in saved_resources.items():
                if value is not None:
                    s.resources.set_value(resource_name, value)
        
        # Verify loaded stats match expected stats (if saved)
        # PROJ-42 Phase 4: This is intentional data integrity verification, NOT a backward
        # compatibility fallback. Warnings indicate component definitions or formulas changed
        # since the ship was saved. The _loading_warnings attribute helps debugging.
        expected = data.get('expected_stats', {})
        if expected:
            mismatches = []
            if expected.get('max_hp') and abs(s.max_hp - expected['max_hp']) > 1:
                mismatches.append(f"max_hp: got {s.max_hp}, expected {expected['max_hp']}")
            
            val = s.resources.get_max_value("fuel")
            if expected.get('max_fuel') and abs(val - expected['max_fuel']) > 1:
                mismatches.append(f"max_fuel: got {val}, expected {expected['max_fuel']}")
            
            val = s.resources.get_max_value("energy")
            if expected.get('max_energy') and abs(val - expected['max_energy']) > 1:
                mismatches.append(f"max_energy: got {val}, expected {expected['max_energy']}")
            
            val = s.resources.get_max_value("ammo")
            if expected.get('max_ammo') and abs(val - expected['max_ammo']) > 1:
                mismatches.append(f"max_ammo: got {val}, expected {expected['max_ammo']}")
            if expected.get('max_speed') and abs(s.max_speed - expected['max_speed']) > 0.1:
                mismatches.append(f"max_speed: got {s.max_speed:.1f}, expected {expected['max_speed']:.1f}")
            if expected.get('acceleration_rate') and abs(s.acceleration_rate - expected['acceleration_rate']) > 0.001:
                mismatches.append(f"acceleration_rate: got {s.acceleration_rate:.3f}, expected {expected['acceleration_rate']:.3f}")
            if expected.get('turn_speed') and abs(s.turn_speed - expected['turn_speed']) > 0.1:
                mismatches.append(f"turn_speed: got {s.turn_speed:.1f}, expected {expected['turn_speed']:.1f}")
            if expected.get('total_thrust') and abs(s.total_thrust - expected['total_thrust']) > 1:
                mismatches.append(f"total_thrust: got {s.total_thrust}, expected {expected['total_thrust']}")
            if expected.get('mass') and abs(s.mass - expected['mass']) > 1:
                mismatches.append(f"mass: got {s.mass}, expected {expected['mass']}")
            armor_hp = s.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in s.layers else 0
            if expected.get('armor_hp_pool') and abs(armor_hp - expected['armor_hp_pool']) > 1:
                mismatches.append(f"armor_hp_pool: got {armor_hp}, expected {expected['armor_hp_pool']}")
            
            s._loading_warnings = mismatches
            
            if mismatches:
                log_warning(f"Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    log_warning(f"  - {m}")
        
        return s
