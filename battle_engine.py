import math
import random
import time
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
import pygame

from ai import AIController
from spatial import SpatialGrid
from game_constants import AttackType
from projectile_manager import ProjectileManager
from collision_system import CollisionSystem

if TYPE_CHECKING:
    from ship_combat import Projectile
    from ship import Ship

class BattleLogger:
    """Toggleable logger that writes battle events to file."""
    
    def __init__(self, filename: str = "battle_log.txt", enabled: bool = True):
        self.enabled = enabled
        self.filename = filename
        self.file = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start_session()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures file is closed."""
        self.close()
        return False
    
    def __del__(self):
        """Destructor - ensures file is closed on garbage collection."""
        self.close()
        
    def start_session(self):
        """Start a new logging session."""
        if self.enabled:
            self.close() # Ensure existing file is closed before opening new one
            try:
                self.file = open(self.filename, 'w', encoding='utf-8')
                self.log("=== BATTLE LOG STARTED ===")
            except IOError as e:
                print(f"Warning: Could not open battle log: {e}")
                self.enabled = False
    
    def log(self, message: str):
        """Log a message if logging is enabled."""
        if self.enabled and self.file:
            try:
                self.file.write(f"{message}\n")

            except IOError:
                pass  # Silently ignore write errors
    
    def close(self):
        """Close the log file."""
        if self.file:
            try:
                self.log("=== BATTLE LOG ENDED ===")
                self.file.close()
            except IOError:
                pass  # Silently ignore close errors
            finally:
                self.file = None

class BattleEngine:
    """Core combat simulation engine."""
    
    def __init__(self, logger: Optional[BattleLogger] = None):
        self.ships: List['Ship'] = []
        self.ai_controllers: List[AIController] = []
        
        self.projectile_manager = ProjectileManager()
        self.collision_system = CollisionSystem()
        
        self.recent_beams: List[Dict[str, Any]] = [] 
        self.grid = SpatialGrid(cell_size=2000)
        self.tick_counter: int = 0
        self.winner: Optional[int] = None
        
        # Use provided logger or create a default one (disabled by default to avoid side effects unless requested)
        self.logger = logger if logger else BattleLogger(enabled=False)

    @property
    def projectiles(self) -> List[Any]:
        return self.projectile_manager.projectiles

    def start(self, team1_ships: List['Ship'], team2_ships: List['Ship'], seed: Optional[int] = None) -> None:
        """Initialize battle state."""
        if seed is not None:
            random.seed(seed)
        
        self.ships = []
        self.ai_controllers = []
        self.projectile_manager.clear()
        self.recent_beams = []
        self.tick_counter = 0
        self.winner = None
        
        # Handle single ship args (though type hint implies lists)
        if not isinstance(team1_ships, list): team1_ships = [team1_ships]
        if not isinstance(team2_ships, list): team2_ships = [team2_ships]
        
        # Setup Team 1
        for s in team1_ships:
            s.team_id = 0
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 1))
        
        # Setup Team 2
        for s in team2_ships:
            s.team_id = 1
            self.ships.append(s)
            self.ai_controllers.append(AIController(s, self.grid, 0))
            
        # Logging
        self.logger.start_session()
        self.logger.log(f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships")
        
        self._log_initial_status()

    def _log_initial_status(self) -> None:
        for s in self.ships:
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={s.current_fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f} Derelict={s.is_derelict}"
            self.logger.log(status_msg)
            
            if s.is_derelict:
                self.logger.log(f"WARNING: {s.name} is DERELICT at start!")
            if s.total_thrust <= 0:
                self.logger.log(f"WARNING: {s.name} has NO THRUST!")
            if s.turn_speed <= 0.01:
                self.logger.log(f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})!")

    def update(self) -> None:
        """Run one simulation tick."""
        if self.is_battle_over():
            return
            
        self.tick_counter += 1
        self.recent_beams = [] # Clear previous beams
        
        # 1. Update Grid
        self.grid.clear()
        alive_ships = [s for s in self.ships if s.is_alive]
        for s in alive_ships:
            self.grid.insert(s)
            
        for p in self.projectiles:
            if p.is_alive:
                self.grid.insert(p)
                
        # 2. Update AI & Ships
        combat_context = {
            'projectiles': self.projectiles,
            'grid': self.grid
        }
        
        for ai in self.ai_controllers:
            ai.update()
        for s in self.ships:
            s.update(context=combat_context)
            
        # 3. Process Attacks
        new_attacks = []
        for s in alive_ships:
            if hasattr(s, 'just_fired_projectiles') and s.just_fired_projectiles:
                new_attacks.extend(s.just_fired_projectiles)
                s.just_fired_projectiles = []
        
        for attack in new_attacks:
            # Normalize access to type
            is_dict = isinstance(attack, dict)
            raw_type = attack.get('type') if is_dict else attack.type
            
            # Map string types to Enum if necessary (migration support)
            attack_type = raw_type
            if isinstance(raw_type, str):
                 try:
                     attack_type = AttackType(raw_type)
                 except ValueError:
                     pass # Unknown type string, keep as is
            
            if attack_type == AttackType.PROJECTILE or attack_type == AttackType.MISSILE:
                if not is_dict:
                    self.projectile_manager.add_projectile(attack)
                    if attack_type == AttackType.PROJECTILE:
                        self.logger.log(f"Projectile fired at {attack.position}")
                    else:
                        self.logger.log(f"Missile fired at {getattr(attack, 'target', 'unknown')}")
            elif attack_type == AttackType.BEAM:
                self.collision_system.process_beam_attack(attack, self.recent_beams)

        # 4. Ship-to-Ship Collisions
        self.collision_system.process_ramming(self.ships, self.logger)
        
        # 5. Update Projectiles
        self.projectile_manager.update(self.grid)

    def is_battle_over(self) -> bool:
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        return team1_alive == 0 or team2_alive == 0

    def get_winner(self) -> int:
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        if team1_alive > 0 and team2_alive == 0:
            return 0
        elif team2_alive > 0 and team1_alive == 0:
            return 1
        return -1
    
    def shutdown(self) -> None:
        self.logger.close()
