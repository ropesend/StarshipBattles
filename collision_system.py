import math
import random
from typing import List, Dict, Any, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from ship import Ship

class CollisionSystem:
    """
    Stateless system for handling collisions and raycasting.
    """

    def process_beam_attack(self, attack: Dict[str, Any], recent_beams: List[Dict[str, Any]]) -> None:
        """
        Process a beam weapon attack using raycasting.
        
        Args:
            attack: Dictionary containing beam parameters
            recent_beams: List to append beam visualization data to
        """
        start_pos = attack['origin']
        direction = attack['direction']
        max_range = attack['range']
        target = attack.get('target')
        
        end_pos = start_pos + direction * max_range
        
        if target and target.is_alive:
            f = start_pos - target.position
            a = direction.dot(direction)
            b = 2 * f.dot(direction)
            c = f.dot(f) - target.radius**2
            
            discriminant = b*b - 4*a*c
            
            if discriminant >= 0:
                # Avoid division by zero if direction length is 0 (shouldn't happen with valid direction)
                if a == 0:
                     t1 = t2 = 0
                else:
                    t1 = (-b - math.sqrt(discriminant)) / (2*a)
                    t2 = (-b + math.sqrt(discriminant)) / (2*a)
                
                valid_t = []
                if 0 <= t1 <= max_range: valid_t.append(t1)
                if 0 <= t2 <= max_range: valid_t.append(t2)
                
                if valid_t:
                    hit_dist = min(valid_t)
                    beam_comp = attack['component']
                    chance = beam_comp.calculate_hit_chance(hit_dist)
                    
                    if random.random() < chance:
                        # Evaluate damage at hit distance
                        damage = beam_comp.get_damage(hit_dist)
                        target.take_damage(damage)
                        end_pos = start_pos + direction * hit_dist
        
        # Store for visualization
        recent_beams.append({
            'start': start_pos,
            'end': end_pos,
            'color': (100, 255, 255) # Could be derived from weapon type
        })

    def process_ramming(self, ships: List['Ship'], logger: Any = None) -> None:
        """
        Process ship-to-ship ramming collisions.
        
        Args:
            ships: List of Ship objects to check
            logger: Optional logger for events
        """
        for s in ships:
            if not s.is_alive: continue
            if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
            
            target = s.current_target
            if not target or not target.is_alive: continue
            
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                hp_rammer = s.hp
                hp_target = target.hp
                
                msg = ""
                if hp_rammer < hp_target:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_rammer * 0.5)
                    msg = f"Ramming: {s.name} destroyed by {target.name}!"
                elif hp_target < hp_rammer:
                    target.take_damage(hp_target + 9999)
                    s.take_damage(hp_target * 0.5)
                    msg = f"Ramming: {target.name} destroyed by {s.name}!"
                else:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_target + 9999)
                    msg = f"Ramming: Mutual destruction!"
                
                if logger:
                    logger.log(msg)
