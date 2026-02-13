from typing import List, Optional, Set, Any, TYPE_CHECKING
from game.core.math import Vector2
from game.core.constants import AttackType
from game.core.config import BattleConfig
from game.core.logger import log_debug

if TYPE_CHECKING:
    from game.engine.spatial import SpatialGrid
    from game.simulation.entities.projectile import Projectile

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

            # Ensure we use our Vector2 for all calculations (handles pygame Vector2 from mocks)
            p_pos = Vector2(p.position.x, p.position.y)
            p_vel = Vector2(p.velocity.x, p.velocity.y)

            query_radius = p_vel.length() + BattleConfig.PROJECTILE_QUERY_BUFFER
            nearby_ships = grid.query_radius(p_pos, query_radius)

            hit_occurred = False

            target_ship = self._check_ship_collisions(p, p_pos, p_vel, nearby_ships)
            if target_ship:
                self._apply_hit(p, target_ship)
                hit_occurred = True

            if not hit_occurred:
                hit_occurred = self._check_missile_interception(p)

            if hit_occurred:
                self._record_hit(p)
                projectiles_to_remove.add(idx)

        # In-place mark-and-sweep removal (avoids list reconstruction)
        if projectiles_to_remove:
            write_idx = 0
            for read_idx, p in enumerate(self.projectiles):
                if read_idx not in projectiles_to_remove:
                    self.projectiles[write_idx] = p
                    write_idx += 1
            del self.projectiles[write_idx:]

    def _check_ship_collisions(self, p, p_pos: Vector2, p_vel: Vector2,
                               nearby_ships) -> Optional[Any]:
        """
        Check projectile against nearby ships using static and dynamic collision detection.

        Returns the first hit ship, or None if no collision.
        """
        p_start = p_pos - p_vel

        for s in nearby_ships:
            if not s.is_alive:
                continue
            if s.team_id == p.team_id:
                continue

            # Convert ship vectors to our Vector2 as well
            s_vel = Vector2(s.velocity.x, s.velocity.y)
            s_pos = Vector2(s.position.x, s.position.y)
            s_prev_pos = s_pos - s_vel

            D0 = p_start - s_prev_pos
            DV = p_vel - s_vel

            dv_sq = DV.dot(DV)
            collision_radius = s.radius + BattleConfig.PROJECTILE_HIT_TOLERANCE

            hit = False

            if dv_sq == 0:
                if D0.length() < collision_radius:
                    hit = True
                    log_debug(f"Hit (Static)! D0={D0.length()} Rad={collision_radius}")
            else:
                t = -D0.dot(DV) / dv_sq
                t_clamped = max(0, min(t, 1.0))

                p_at_t = p_start + p_vel * t_clamped
                s_at_t = s_prev_pos + s_vel * t_clamped

                dist = p_at_t.distance_to(s_at_t)

                if dist < collision_radius:
                    hit = True
                    log_debug(f"HIT! Ship={s.name} Dist={dist:.2f} < Rad={collision_radius} t={t_clamped:.4f}")

            if hit:
                return s

        return None

    def _apply_hit(self, p, target_ship) -> None:
        """
        Calculate and apply damage from a projectile hit on a ship.

        Evaluates distance-based damage from source weapon if available,
        otherwise uses the projectile's static damage value.
        """
        hit_dist = p.distance_traveled

        # Evaluate damage at hit distance if source weapon has ability with formula
        damage = p.damage
        if hasattr(p, 'source_weapon') and p.source_weapon:
            weapon_ab = p.source_weapon.get_ability('WeaponAbility')
            if weapon_ab and hasattr(weapon_ab, 'get_damage'):
                damage = weapon_ab.get_damage(hit_dist)

        target_ship.combat_engine.take_damage(damage)

    def _check_missile_interception(self, p) -> bool:
        """
        Check if a missile-type projectile intercepts its target missile.

        Returns True if interception occurred.
        """
        is_missile = p.type == AttackType.MISSILE

        if not is_missile or not p.target or not isinstance(p.target, type(p)):
            return False

        t_missile = p.target
        if not t_missile.is_alive:
            return False

        dist = p.position.distance_to(t_missile.position)
        if dist < (p.radius + t_missile.radius + BattleConfig.MISSILE_INTERCEPT_BUFFER):
            t_missile.take_damage(p.damage)
            if not t_missile.is_alive:
                t_missile.status = 'destroyed'
            return True

        return False

    def _record_hit(self, p) -> None:
        """Mark projectile as hit and update source weapon stats."""
        p.is_alive = False
        p.status = 'hit'
        if hasattr(p, 'source_weapon') and p.source_weapon:
            # shots_hit initialized in Component.__init__
            p.source_weapon.shots_hit += 1
