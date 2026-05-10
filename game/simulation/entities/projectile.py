import logging
from typing import Any, Callable
from game.core.math import Vector2, signed_angle_between
from game.engine.physics import PhysicsBody
from game.core.constants import AttackType


def _default_event_logger(event_type: str, **kwargs: Any) -> None:  # noqa: ARG001 — no-op default; signature kept for callback contract
    """PROJ-390: no-op default event-log dispatcher.

    The default is deliberately silent.  PROJ-382 Phase 2 (Pattern #10)
    introduced the injectable ``event_logger=`` constructor parameter so
    callers that care about projectile telemetry — `BattleEngine`,
    tests, replay tools — pass a closure that routes through their
    session-scoped ``EventBus``.  The previous default lazy-imported the
    module-level ``log_event`` shim; PROJ-390 retired that shim and
    replaced this default with a no-op so untouched callers do not
    silently fall back to a process-global handler.
    """
    return

logger = logging.getLogger(__name__)
from game.core.config import PhysicsConfig
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode

# Guidance system constants
# When the target is within this angle of 180° (directly behind), commit to turn direction
# to prevent oscillation. Value of 45 means commit when target is >135° off-boresight.
TURN_COMMITMENT_THRESHOLD_DEG = 45


class Projectile(PhysicsBody):
    def __init__(self, owner, position, velocity, damage, range_val, endurance, proj_type, source_weapon=None, **kwargs):
        super().__init__(position.x, position.y)
        # PROJ-382 Phase 2 (Pattern #10): event_logger is the injected callable
        # for telemetry emission.  Defaults to module-level dispatcher so
        # untouched call sites preserve behavior; tests + cross-layer callers
        # may pass a closure.
        self._event_logger: Callable[..., None] = kwargs.get(
            "event_logger", _default_event_logger
        )
        self.id: str = str(id(self))
        self.velocity = velocity
        self.owner = owner
        # Owner may be None for orphaned projectiles, default team_id to -1
        self.team_id = owner.team_id if owner is not None else -1
        self.damage = damage
        self.max_range = range_val
        self.endurance = endurance # in seconds
        self.max_endurance = endurance  # Store initial value for UI

        # ERR-009: Validate required parameters
        if damage is None or damage < 0:
            raise ValidationException(
                f"Invalid projectile damage: {damage}",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"damage": damage, "owner": str(owner)}
            )
        if range_val is None or range_val <= 0:
            raise ValidationException(
                f"Invalid projectile range: {range_val}",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"range": range_val, "owner": str(owner)}
            )
        # Note: endurance can be None for range-limited projectiles (non-seeking)
        if endurance is not None and endurance <= 0:
            raise ValidationException(
                f"Invalid projectile endurance: {endurance}",
                code=ErrorCode.OUT_OF_RANGE.value,
                context={"endurance": endurance, "owner": str(owner)}
            )

        # Ensure type is AttackType (accept string for deserialization)
        if isinstance(proj_type, str):
            self.type = AttackType(proj_type)
        else:
            self.type = proj_type
        
        # Optional args
        self.turn_rate = kwargs.get('turn_rate', 0)
        self.max_speed = kwargs.get('max_speed', 0)
        self.target = kwargs.get('target', None)
        self.hp = kwargs.get('hp', 1) # Missiles can be shot down
        self.max_hp = self.hp  # Store initial value for UI
        self.radius = kwargs.get('radius', 3)
        # PROJ-113: Removed color property - visual properties belong in UI layer
        # Color is now determined by BattleUIService based on projectile type
        self.source_weapon = source_weapon
        
        # Turn direction commitment for stable guidance (prevents oscillation)
        self.last_turn_direction = 0  # -1 for clockwise, +1 for counter-clockwise
        
        self.distance_traveled = 0
        self.is_alive = True
        
        # Defense score for PDC beam hit-chance calculation (from seeker's to_hit_defense)
        self.total_defense_score = kwargs.get('to_hit_defense', 0.0)

        # Flag for targeting systems
        self.is_derelict = False # Projectiles aren't ships, but this helps unified filtering
        
        # Status for UI tracking
        self.status = 'active' # active, hit, miss, destroyed
        
    def update(self) -> None:
        if not self.is_alive: return

        dt = PhysicsConfig.TICK_RATE

        # Endurance check
        if self.endurance is not None:
             self.endurance -= dt
             if self.endurance <= 0:
                 self.is_alive = False
                 self.status = 'miss'
                 # Log Expiration (Seeker or Timed Projectile)
                 if self.type == AttackType.MISSILE:
                     self._event_logger("SEEKER_EXPIRE",
                               seeker_id=str(id(self)),
                               reason="lifetime",
                               tick=0)
                 return

        # Guidance Logic (if missile)
        if (self.type == AttackType.MISSILE) and self.target and self.target.is_alive:
            self._update_guidance(dt)
            
        # Physics Update (from PhysicsBody)
        self.position += self.velocity
        
        self.distance_traveled += self.velocity.length()
        if self.max_range and self.distance_traveled > self.max_range:
            self.is_alive = False
            self.status = 'miss'
            # Log Range Expiration
            if self.type == AttackType.MISSILE:
                self._event_logger("SEEKER_EXPIRE",
                          seeker_id=str(id(self)),
                          reason="max_range",
                          tick=0)

    def _update_guidance(self, dt: float) -> None:
        target = self.target
        p_pos = self.position
        p_vel = self.velocity
        
        # Calculate lead
        # Assume owner has solve_lead or we implement a static one?
        # Owner might be dead, so careful.
        # We can implement a simplified intercept here.
        
        # Simple intercept logic:
        # We want to hit target.
        rel_pos = target.position - p_pos
        dist = rel_pos.length()
        
        if dist > 0:
            # Desired velocity vector
            # Predict target position?
            # t = dist / self.max_speed
            # predicted_pos = target.position + target.velocity * t
            
            # Use strict pursuit for now or a simple lead if possible
            # Replicating existing logic from battle.py:
            # t = owner.solve_lead(...)
            
            # Let's try to use the owner's solver if available, else direct
            # Ship.combat_engine is a property (lazy initialized, always accessible)
            t = 0
            if self.owner is not None and self.owner.combat_engine is not None:
                 t = self.owner.combat_engine.solve_lead(p_pos, Vector2(0,0), target.position, target.velocity, self.max_speed)
            
            aim_pos = target.position
            if t > 0:
                aim_pos = target.position + target.velocity * t
                
            desired_vec = aim_pos - p_pos
            if desired_vec.length_squared() > 0:
                desired_dir = desired_vec.normalize()
                current_dir = p_vel.normalize() if p_vel.length() > 0 else Vector2(1, 0)
                
                angle_diff = signed_angle_between(current_dir, desired_dir)
                    
                # Turn rate is degrees per second, convert to degrees per tick
                max_turn_step = self.turn_rate * PhysicsConfig.TICK_RATE
                
                if abs(angle_diff) > max_turn_step:
                    rotation = max_turn_step if angle_diff > 0 else -max_turn_step
                else:
                    rotation = angle_diff
                
                # Safety net: commit to turn direction near ±180° to prevent
                # floating-point sign flips. signed_angle_between is stable,
                # but at exactly 180° tiny perturbations could flip the sign.
                if abs(abs(angle_diff) - 180) < TURN_COMMITMENT_THRESHOLD_DEG:
                    if self.last_turn_direction != 0:
                        rotation = abs(rotation) * self.last_turn_direction
                
                # Store turn direction for next frame
                if rotation != 0:
                    self.last_turn_direction = 1 if rotation > 0 else -1
                
                new_vel = current_dir.rotate(rotation) * self.max_speed
                self.velocity = new_vel

    def take_damage(self, amount: float) -> None:
        self.hp -= amount
        if self.hp <= 0:
            self.is_alive = False
            self.status = 'destroyed'
            logger.debug(f"Projectile {self} destroyed by point defense!")
