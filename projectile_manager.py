import pygame
from typing import List, Set, Any, TYPE_CHECKING
from game_constants import AttackType
from logger import log_debug

if TYPE_CHECKING:
    from spatial import SpatialGrid
    from projectiles import Projectile

class ProjectileManager:
    """
    Manages projectile updates, lifetimes, and collisions.
    """
    def __init__(self):
        self.projectiles = []

    def get_active_projectiles(self) -> List[Any]:
        return self.projectiles

    def add_projectile(self, projectile: Any):
        self.projectiles.append(projectile)

    def clear(self):
        self.projectiles = []

    def update(self, grid: 'SpatialGrid') -> None:
        """
        Update projectile positions and check collisions.
        
        Args:
            grid: SpatialGrid for spatial queries
        """
        projectiles_to_remove = set()
        
        for idx, p in enumerate(self.projectiles):
            if idx in projectiles_to_remove:
                continue
            
            p.update() 
            
            if not p.is_alive:
                projectiles_to_remove.add(idx)
                continue
                
            p_pos = p.position 
            
            query_radius = p.velocity.length() + 100
            nearby_ships = grid.query_radius(p_pos, query_radius)
            
            hit_occurred = False
            
            p_start = p_pos - p.velocity
            
            # Check against Ships
            for s in nearby_ships:
                if not s.is_alive: continue
                if s.team_id == p.team_id: continue
                
                s_vel = s.velocity
                s_pos = s.position
                s_prev_pos = s_pos - s_vel
                
                D0 = p_start - s_prev_pos
                DV = p.velocity - s_vel
                
                dv_sq = DV.dot(DV)
                collision_radius = s.radius + 5
                
                hit = False
                
                if dv_sq == 0:
                    if D0.length() < collision_radius:
                        hit = True
                        log_debug(f"Hit (Static)! D0={D0.length()} Rad={collision_radius}")
                else:
                    t = -D0.dot(DV) / dv_sq
                    t_clamped = max(0, min(t, 1.0))
                    
                    p_at_t = p_start + p.velocity * t_clamped
                    s_at_t = s_prev_pos + s_vel * t_clamped
                    
                    dist = p_at_t.distance_to(s_at_t)
                    
                    # LOGGING
                    # log_debug(f"Check {s.name}: P_start={p_start} P_vel={p.velocity} S_pos={s_prev_pos} S_vel={s_vel}")
                    # log_debug(f"Math: t={t:.4f} t_clamped={t_clamped:.4f} Dist={dist:.2f} ColRad={collision_radius}")
                    
                    if dist < collision_radius:
                        hit = True
                        log_debug(f"HIT! Ship={s.name} Dist={dist:.2f} < Rad={collision_radius} t={t_clamped:.4f}")
                    else:
                        # log_debug(f"MISS Ship={s.name} Dist={dist:.2f} > Rad={collision_radius}")
                        pass
                
                if hit:
                    # Calculate hit distance from projectile origin
                    hit_dist = p.distance_traveled
                    
                    # Evaluate damage at hit distance if source weapon has ability with formula
                    damage = p.damage
                    if hasattr(p, 'source_weapon') and p.source_weapon:
                        weapon_ab = p.source_weapon.get_ability('WeaponAbility')
                        if weapon_ab and hasattr(weapon_ab, 'get_damage'):
                            damage = weapon_ab.get_damage(hit_dist)
                    
                    s.take_damage(damage)
                    hit_occurred = True
                    break
            
            # Check against Projectiles (Missile Interception)
            # Use strict type check or equality to Enum member
            is_missile = (p.type == AttackType.MISSILE) or (p.type == 'missile')
            
            if not hit_occurred and is_missile and p.target and isinstance(p.target, type(p)):
                 t_missile = p.target
                 if t_missile.is_alive:
                     dist = p.position.distance_to(t_missile.position)
                     if dist < (p.radius + t_missile.radius + 10):
                         t_missile.take_damage(p.damage)
                         hit_occurred = True
                         if not t_missile.is_alive:
                             t_missile.status = 'destroyed'
            
            if hit_occurred:
                p.is_alive = False
                p.status = 'hit'
                if hasattr(p, 'source_weapon') and p.source_weapon:
                    p.source_weapon.shots_hit += 1
                projectiles_to_remove.add(idx)
        
        if projectiles_to_remove:
            self.projectiles = [p for i, p in enumerate(self.projectiles) if i not in projectiles_to_remove]
