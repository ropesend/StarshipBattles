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
        self.projectiles = []
        # We don't store beams persistently for simulation, but we return them as events
        self.recent_beams = [] 
        self.grid = SpatialGrid(cell_size=2000)
        self.tick_counter = 0
        self.winner = None

    def start(self, team1_ships, team2_ships, seed=None):
        """Initialize battle state."""
        if seed is not None:
            random.seed(seed)
        
        self.ships = []
        self.ai_controllers = []
        self.projectiles = []
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
                    self.projectiles.append(attack)
                    if attack_type == 'projectile':
                        BATTLE_LOG.log(f"Projectile fired at {attack.position}")
                    else:
                        BATTLE_LOG.log(f"Missile fired at {getattr(attack, 'target', 'unknown')}")
            elif attack_type == 'beam':
                self._process_beam_attack(attack)

        # 4. Ship-to-Ship Collisions
        self._process_ramming()
        
        # 5. Update Projectiles
        self._update_projectiles()

    def _process_beam_attack(self, attack):
        """Process a beam weapon attack."""
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
                        target.take_damage(attack['damage'])
                        end_pos = start_pos + direction * hit_dist
        
        # Store for visualization
        self.recent_beams.append({
            'start': start_pos,
            'end': end_pos,
            'color': (100, 255, 255) # Could be derived from weapon type
        })

    def _process_ramming(self):
        """Process ship-to-ship ramming collisions."""
        for s in self.ships:
            if not s.is_alive: continue
            if getattr(s, 'ai_strategy', '') != 'kamikaze': continue
            
            target = s.current_target
            if not target or not target.is_alive: continue
            
            collision_radius = s.radius + target.radius
            
            if s.position.distance_to(target.position) < collision_radius:
                hp_rammer = s.hp
                hp_target = target.hp
                
                if hp_rammer < hp_target:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_rammer * 0.5)
                    BATTLE_LOG.log(f"Ramming: {s.name} destroyed by {target.name}!")
                elif hp_target < hp_rammer:
                    target.take_damage(hp_target + 9999)
                    s.take_damage(hp_target * 0.5)
                    BATTLE_LOG.log(f"Ramming: {target.name} destroyed by {s.name}!")
                else:
                    s.take_damage(hp_rammer + 9999)
                    target.take_damage(hp_target + 9999)
                    BATTLE_LOG.log(f"Ramming: Mutual destruction!")

    def _update_projectiles(self):
        """Update projectile positions and check collisions."""
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
            nearby_ships = self.grid.query_radius(p_pos, query_radius)
            
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
