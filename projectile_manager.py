import pygame
from typing import List, Set, Any, TYPE_CHECKING

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
                else:
                    t = -D0.dot(DV) / dv_sq
                    t_clamped = max(0, min(t, 1.0))
                    
                    p_at_t = p_start + p.velocity * t_clamped
                    s_at_t = s_prev_pos + s_vel * t_clamped
                    
                    if p_at_t.distance_to(s_at_t) < collision_radius:
                        hit = True
                
                if hit:
                    s.take_damage(p.damage)
                    hit_occurred = True
                    break
            
            # Check against Projectiles (Missile Interception)
            if not hit_occurred and p.type == 'missile' and p.target and isinstance(p.target, type(p)):
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
