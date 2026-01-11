"""
ShipSerializer - Extracted serialization logic from Ship class.
Handles to_dict() and from_dict() operations for Ship entities.
"""
from typing import Dict, Any, TYPE_CHECKING

from game.simulation.components.component import LayerType, create_component
from game.core.registry import get_component_registry, get_modifier_registry

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


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
        data = {
            "name": ship.name,
            "ship_class": ship.ship_class,
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
                "mass": ship.mass,
                "armor_hp_pool": ship.layers[LayerType.ARMOR]['max_hp_pool'] if LayerType.ARMOR in ship.layers else 0
            }
        }
        
        for ltype, layer_data in ship.layers.items():
            # Skip HULL layer from explicit serialization
            if ltype == LayerType.HULL:
                continue
                
            filter_comps = []
            for comp in layer_data['components']:
                # Skip Hull components as safety (HULL layer already skipped)
                if comp.id.startswith('hull_'):
                    continue
                # Save as dict with modifiers
                c_obj = {"id": comp.id}
                if comp.modifiers:
                    c_obj["modifiers"] = [{"id": m.definition.id, "value": m.value} for m in comp.modifiers]
                filter_comps.append(c_obj)
                
            data["layers"][ltype.name] = filter_comps
        return data

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Ship':
        """
        Create ship from dictionary.
        
        Args:
            data: Dictionary containing ship data
            
        Returns:
            New Ship instance populated from the dictionary
        """
        # Import here to avoid circular dependency
        from game.simulation.entities.ship import Ship
        
        name = data.get("name", "Unnamed")
        color_val = data.get("color", (200, 200, 200))
        # Ensure color is tuple
        color: tuple
        if isinstance(color_val, list): 
            color = tuple(color_val)
        else:
            color = color_val  # type: ignore
        
        s = Ship(name, 0, 0, color, data.get("team_id", 0), 
                ship_class=data.get("ship_class", "Escort"), 
                theme_id=data.get("theme_id", "Federation"))
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
                comp_id = ""
                modifiers_data = []
                
                if isinstance(c_entry, str):
                    comp_id = c_entry
                elif isinstance(c_entry, dict):
                    comp_id = c_entry.get("id", "")
                    modifiers_data = c_entry.get("modifiers", [])
                
                comps = get_component_registry()
                if comp_id in comps:
                    new_comp = comps[comp_id].clone()
                    
                    # Apply Modifiers
                    mods = get_modifier_registry()
                    for m_dat in modifiers_data:
                        mid = m_dat['id']
                        mval = m_dat['value']
                        if mid in mods:
                            new_comp.add_modifier(mid, mval)

                    s.add_component(new_comp, layer_type)
        
        s.recalculate_stats()
    
        # Restore resource values if saved
        saved_resources = data.get('resources', {})
        if saved_resources:
            for resource_name, value in saved_resources.items():
                if value is not None:
                    s.resources.set_value(resource_name, value)
        
        # Verify loaded stats match expected stats (if saved)
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
                print(f"WARNING: Ship '{s.name}' stats mismatch after loading!")
                for m in mismatches:
                    print(f"  - {m}")
        
        return s
