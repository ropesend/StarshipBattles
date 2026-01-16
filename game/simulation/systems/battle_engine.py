import math
import random
import time
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING
import pygame

from game.core.logger import log_warning, log_info
from game.ai.controller import AIController
from game.engine.spatial import SpatialGrid
from game.core.constants import AttackType
from game.simulation.projectile_manager import ProjectileManager
from game.engine.collision import CollisionSystem
from game.simulation.systems.battle_end_conditions import BattleEndCondition, BattleEndMode

from game.simulation.entities.projectile import Projectile
from game.simulation.entities.ship import Ship

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
                log_warning(f"Could not open battle log: {e}")
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

        # Battle end condition (default: HP-based)
        self.end_condition: BattleEndCondition = BattleEndCondition(mode=BattleEndMode.HP_BASED)

        # Use provided logger or create a default one (disabled by default to avoid side effects unless requested)
        self.logger = logger if logger else BattleLogger(enabled=False)

    @property
    def projectiles(self) -> List[Any]:
        return self.projectile_manager.projectiles

    def start(
        self,
        team1_ships: List['Ship'],
        team2_ships: List['Ship'],
        seed: Optional[int] = None,
        end_condition: Optional[BattleEndCondition] = None
    ) -> None:
        """
        Initialize battle state with configurable end condition.

        Args:
            team1_ships: List of ships for team 0
            team2_ships: List of ships for team 1
            seed: Random seed for deterministic battles
            end_condition: Battle end condition (default: HP_BASED)
        """
        if seed is not None:
            random.seed(seed)

        self.ships = []
        self.ai_controllers = []
        self.projectile_manager.clear()
        self.recent_beams = []
        self.tick_counter = 0
        self.winner = None

        # Set end condition (default to HP_BASED if not provided)
        if end_condition is not None:
            self.end_condition = end_condition
        else:
            self.end_condition = BattleEndCondition(mode=BattleEndMode.HP_BASED)
        
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
            fuel = s.resources.get_value("fuel")
            status_msg = f"Ship '{s.name}' (Team {s.team_id}): HP={s.hp}/{s.max_hp} Mass={s.mass} Thrust={s.total_thrust} Fuel={fuel} TurnSpeed={s.turn_speed:.2f} MaxSpeed={s.max_speed:.2f}"
            self.logger.log(status_msg)
            log_info(status_msg)
            # Removed Derelict Warning
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
            elif attack_type == AttackType.LAUNCH:
                # Handle Fighter Launch
                source_ship = attack.get('source')
                hangar = attack.get('hangar')
                fighter_class = attack.get('fighter_class', 'Fighter (Small)')
                origin = attack.get('origin', pygame.math.Vector2(0,0))
                
                # Create the new ship
                # We need a unique name
                count = len([s for s in self.ships if s.team_id == source_ship.team_id])
                new_name = f"{source_ship.name} Wing {count+1}"
                
                # Offset position slightly
                offset = pygame.math.Vector2(random.uniform(-10, 10), random.uniform(-10, 10))
                spawn_pos = origin + offset
                
                new_ship = Ship(
                    name=new_name,
                    x=spawn_pos.x,
                    y=spawn_pos.y,
                    color=source_ship.color,
                    team_id=source_ship.team_id,
                    ship_class=fighter_class,
                    theme_id=source_ship.theme_id
                )
                
                # Inherit some properties or init velocity
                new_ship.velocity = pygame.math.Vector2(source_ship.velocity)
                # Maybe boost it forward?
                launch_dir = pygame.math.Vector2(1, 0).rotate(source_ship.angle)
                new_ship.velocity += launch_dir * 100 # Initial push
                new_ship.angle = source_ship.angle
                
                # Add to battle
                self.ships.append(new_ship)
                # Create AI
                # Fighters use 'attack_run' usually? Defined in class?
                # Using 1-source.team_id as enemy team logic from start()
                # Should be dynamic based on teams?
                # Assuming 2 teams: 0 and 1. Enemy is 1 - team_id.
                enemy_team = 1 - new_ship.team_id
                self.ai_controllers.append(AIController(new_ship, self.grid, enemy_team))
                
                self.logger.log(f"LAUNCH: {new_name} launched from {source_ship.name}")

        # 4. Ship-to-Ship Collisions
        self.collision_system.process_ramming(self.ships, self.logger)
        
        # 5. Update Projectiles
        self.projectile_manager.update(self.grid)

    def is_battle_over(self) -> bool:
        """
        Check if battle should end based on configured end condition.

        Returns:
            True if battle should end, False otherwise

        End Condition Modes:
            TIME_BASED: End after max_ticks reached
            HP_BASED: End when any team has 0 alive ships
            CAPABILITY_BASED: End when any team can't fight/move
            MANUAL: Never end automatically
        """

        # TIME_BASED: Check tick count
        if self.end_condition.mode == BattleEndMode.TIME_BASED:
            if self.end_condition.max_ticks is not None:
                return self.tick_counter >= self.end_condition.max_ticks
            return False  # No max_ticks set, never end

        # MANUAL: Never end automatically
        if self.end_condition.mode == BattleEndMode.MANUAL:
            return False

        # HP_BASED: Check alive ships (optionally excluding derelict)
        if self.end_condition.mode == BattleEndMode.HP_BASED:
            team1_alive = sum(
                1 for s in self.ships
                if s.team_id == 0 and s.is_alive
                and (not self.end_condition.check_derelict or not s.is_derelict)
            )
            team2_alive = sum(
                1 for s in self.ships
                if s.team_id == 1 and s.is_alive
                and (not self.end_condition.check_derelict or not s.is_derelict)
            )
            return team1_alive == 0 or team2_alive == 0

        # CAPABILITY_BASED: Check if any team can't fight
        if self.end_condition.mode == BattleEndMode.CAPABILITY_BASED:
            team1_capable = self._team_has_combat_capability(0)
            team2_capable = self._team_has_combat_capability(1)
            return not team1_capable or not team2_capable

        # Fallback (should never reach here)
        return False

    def _team_has_combat_capability(self, team_id: int) -> bool:
        """
        Check if team has any ships that can fight or move.

        A team has combat capability if ANY ship on that team:
        - Is alive AND
        - Has operational weapons OR movement capability

        Args:
            team_id: Team to check (0 or 1)

        Returns:
            True if team has at least one capable ship, False otherwise
        """
        for ship in self.ships:
            if ship.team_id != team_id or not ship.is_alive:
                continue

            # Check for operational weapons
            has_weapons = any(
                comp.is_operational and comp.type == "Weapon"
                for comp in ship.get_all_components()
            )

            # Check for movement capability
            has_engines = ship.total_thrust > 0
            has_thrusters = ship.turn_speed > 0

            # If ship has weapons OR movement, team is still capable
            if has_weapons or has_engines or has_thrusters:
                return True

        return False

    def get_winner(self) -> int:
        team1_alive = sum(1 for s in self.ships if s.team_id == 0 and s.is_alive)
        team2_alive = sum(1 for s in self.ships if s.team_id == 1 and s.is_alive)
        if team1_alive > 0 and team2_alive == 0:
            return 0
        elif team2_alive > 0 and team1_alive == 0:
            return 1
        return -1
    
    def shutdown(self) -> None:
        self.logger.close()
