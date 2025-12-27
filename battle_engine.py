import math
import random
import time
import pygame

from ai import AIController
from spatial import SpatialGrid

class BattleLogger:
    """Toggleable logger that writes battle events to file."""
    
    def __init__(self, filename="battle_log.txt", enabled=True):
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
    
    def log(self, message):
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

# Global battle logger instance
BATTLE_LOG = BattleLogger(enabled=True)

class BattleEngine:
    """Core combat simulation engine."""
    
    def __init__(self):
        self.ships = []
        self.ai_controllers = []
        # Projectiles are now managed by ProjectileManager
        from projectile_manager import ProjectileManager
        from collision_system import CollisionSystem
        
        self.projectile_manager = ProjectileManager()
        self.collision_system = CollisionSystem()
        
        self.recent_beams = [] 
        self.grid = SpatialGrid(cell_size=2000)
        self.tick_counter = 0
        self.winner = None

    @property
    def projectiles(self):
        return self.projectile_manager.projectiles

    def start(self, team1_ships, team2_ships, seed=None):
        """Initialize battle state."""
        if seed is not None:
            random.seed(seed)
        
        self.ships = []
        self.ai_controllers = []
        self.projectile_manager.clear()
        self.recent_beams = []
        self.tick_counter = 0
        self.winner = None
        
        # Handle single ship args
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
        BATTLE_LOG.start_session()
        BATTLE_LOG.log(f"Battle started: {len(team1_ships)} vs {len(team2_ships)} ships")
        
        self._log_initial_status()

    def _log_initial_status(self):
        for s in self.ships:
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={s.current_fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f} Derelict={s.is_derelict}"
            BATTLE_LOG.log(status_msg)
            # We avoid print here to keep engine quiet, let caller handle IO if needed
            
            if s.is_derelict:
                BATTLE_LOG.log(f"WARNING: {s.name} is DERELICT at start!")
            if s.total_thrust <= 0:
                BATTLE_LOG.log(f"WARNING: {s.name} has NO THRUST!")
            if s.turn_speed <= 0.01:
                BATTLE_LOG.log(f"WARNING: {s.name} has LOW/NO TURN SPEED ({s.turn_speed:.4f})!")

    def update(self):
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
            is_dict = isinstance(attack, dict)
            attack_type = attack.get('type') if is_dict else attack.type
            
            if attack_type == 'projectile' or attack_type == 'missile':
                if not is_dict:
                    self.projectile_manager.add_projectile(attack)
                    if attack_type == 'projectile':
                        BATTLE_LOG.log(f"Projectile fired at {attack.position}")
                    else:
                        BATTLE_LOG.log(f"Missile fired at {getattr(attack, 'target', 'unknown')}")
            elif attack_type == 'beam':
                self.collision_system.process_beam_attack(attack, self.recent_beams)

        # 4. Ship-to-Ship Collisions
        self.collision_system.process_ramming(self.ships, BATTLE_LOG)
        
        # 5. Update Projectiles
        self.projectile_manager.update(self.grid)

    def is_battle_over(self):
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        return team1_alive == 0 or team2_alive == 0

    def get_winner(self):
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive and not getattr(s, 'is_derelict', False))
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive and not getattr(s, 'is_derelict', False))
        if team1_alive > 0 and team2_alive == 0:
            return 0
        elif team2_alive > 0 and team1_alive == 0:
            return 1
        return -1
    
    def shutdown(self):
        BATTLE_LOG.close()
