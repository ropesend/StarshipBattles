"""
Component Test Logger - Structured event logging for simulation-based tests.

This logger outputs events in a standardized format that can be parsed
to verify component behavior.
"""
import os
from typing import Optional, List, Dict, Any
from enum import Enum


class TestEventType(Enum):
    """Enumeration of all log event types for component tests."""
    SHIP_SPAWN = "SHIP_SPAWN"
    TICK = "TICK"
    SHIP_VELOCITY = "SHIP_VELOCITY"
    SHIP_POSITION = "SHIP_POSITION"
    WEAPON_FIRE = "WEAPON_FIRE"
    PROJECTILE_SPAWN = "PROJECTILE_SPAWN"
    HIT = "HIT"
    MISS = "MISS"
    SEEKER_LAUNCH = "SEEKER_LAUNCH"
    SEEKER_IMPACT = "SEEKER_IMPACT"
    SEEKER_EXPIRE = "SEEKER_EXPIRE"
    SEEKER_DESTROYED = "SEEKER_DESTROYED"
    SIM_START = "SIM_START"
    SIM_END = "SIM_END"



# Global flag to enable/disable test logging
TEST_LOGGING_ENABLED = False

# Global reference to active logger
ACTIVE_LOGGER = None

# Default log directory
TEST_LOG_DIR = "tests/simulation/output/logs/"


class ComponentTestLogger:
    """
    Structured logger for component simulation tests.
    
    Outputs events in a parseable format:
    [TICK:N] EVENT_TYPE | key=value | key=value | ...
    
    Usage:
        logger = ComponentTestLogger("ENG-001.log", enabled=True)
        logger.start()
        logger.log_event(TestEventType.SHIP_SPAWN, name="TestShip", pos="(0,0)")
        logger.close()
    """
    
    def __init__(self, filename: str, enabled: bool = None, log_dir: str = None):
        """
        Initialize the logger.
        
        Args:
            filename: Name of the log file (e.g., "ENG-001.log")
            enabled: Override global TEST_LOGGING_ENABLED if set
            log_dir: Override TEST_LOG_DIR if set
        """
        self.filename = filename
        self.enabled = enabled if enabled is not None else TEST_LOGGING_ENABLED
        self.log_dir = log_dir if log_dir else TEST_LOG_DIR
        self.file = None
        self.current_tick = 0
        
    def start(self) -> None:
        """Start a new logging session."""
        global ACTIVE_LOGGER
        if not self.enabled:
            return
            
        # Ensure directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        filepath = os.path.join(self.log_dir, self.filename)
        try:
            self.file = open(filepath, 'w', encoding='utf-8')
            ACTIVE_LOGGER = self
            
            # Register with core logger
            from game.core import logger
            logger.set_event_handler(self.log_event)
            
        except IOError as e:
            print(f"Warning: Could not open test log file: {e}")
            self.enabled = False
    
    def close(self) -> None:
        """Close the log file."""
        global ACTIVE_LOGGER
        
        # Unregister from core logger
        from game.core import logger
        logger.set_event_handler(None)
        
        if self.file:
            try:
                self.file.close()
            except IOError:
                pass
            finally:
                self.file = None
                if ACTIVE_LOGGER == self:
                    ACTIVE_LOGGER = None
    
    def set_tick(self, tick: int) -> None:
        """Update the current tick for subsequent log entries."""
        self.current_tick = tick
    
    def log_event(self, event_type: TestEventType, **kwargs) -> None:
        """
        Log a structured event.
        
        Args:
            event_type: The type of event (from TestEventType enum)
            **kwargs: Key-value pairs to include in the log entry
        """
        if not self.enabled or not self.file:
            return
        
        # Format for console/log
        # To make it easiest for the parser, ensure we use its pattern
        # [TICK:N] | EVENT_TYPE | key=value | ...
        
        # Note: Previous implementation used 'pipe' delimited but parser uses regex
        # Pattern: r'\[TICK:(\d+)\]\s*\|\s*(\w+)(?:\s*\|(.*))?'
        
        parts = [f"[TICK:{self.current_tick}]"]
        
        # Use simple string for event type if it's an Enum
        etype_str = event_type.value if isinstance(event_type, TestEventType) else str(event_type)
        parts.append(etype_str)
        
        kv_parts = []
        for key, value in kwargs.items():
            kv_parts.append(f"{key}={value}")
        
        if kv_parts:
            parts.append(" | ".join(kv_parts))
        else:
            parts.append("") # Empty data part
            
        line = " | ".join(parts)
        try:
            self.file.write(line + "\n")
            self.file.flush()
        except IOError:
            pass
    
    def log_sim_start(self, test_id: str, ships: List[str]) -> None:
        """Log simulation start event."""
        self.log_event(TestEventType.SIM_START, 
                      test_id=test_id, 
                      ships=",".join(ships))
    
    def log_sim_end(self, ships_remaining: int) -> None:
        """Log simulation end event."""
        self.log_event(TestEventType.SIM_END, 
                      final_tick=self.current_tick,
                      ships_remaining=ships_remaining)
    
    def log_ship_spawn(self, name: str, x: float, y: float, 
                       ship_class: str, mass: float, thrust: float) -> None:
        """Log ship spawn event."""
        self.log_event(TestEventType.SHIP_SPAWN,
                      name=name,
                      pos=f"({x:.1f},{y:.1f})",
                      ship_class=ship_class,
                      mass=f"{mass:.1f}",
                      thrust=f"{thrust:.1f}")
    
    def log_ship_velocity(self, name: str, vx: float, vy: float, 
                          speed: float, heading: float) -> None:
        """Log ship velocity event."""
        self.log_event(TestEventType.SHIP_VELOCITY,
                      name=name,
                      vx=f"{float(vx):.2f}",
                      vy=f"{float(vy):.2f}",
                      speed=f"{float(speed):.2f}",
                      heading=f"{float(heading):.1f}")
    
    def log_ship_position(self, name: str, x: float, y: float) -> None:
        """Log ship position event."""
        self.log_event(TestEventType.SHIP_POSITION,
                      name=name,
                      x=f"{float(x):.1f}",
                      y=f"{float(y):.1f}")
    
    def log_weapon_fire(self, ship_name: str, weapon_id: str, 
                        target: str, weapon_type: str) -> None:
        """Log weapon fire event."""
        self.log_event(TestEventType.WEAPON_FIRE,
                      ship=ship_name,
                      weapon=weapon_id,
                      target=target,
                      type=weapon_type)
    
    def log_hit(self, attacker: str, target: str, weapon: str, 
                damage: float) -> None:
        """Log hit event."""
        self.log_event(TestEventType.HIT,
                      attacker=attacker,
                      target=target,
                      weapon=weapon,
                      damage=f"{damage:.1f}")
    
    def log_miss(self, attacker: str, target: str, weapon: str, 
                 reason: str) -> None:
        """Log miss event."""
        self.log_event(TestEventType.MISS,
                      attacker=attacker,
                      target=target,
                      weapon=weapon,
                      reason=reason)
    
    def log_seeker_launch(self, seeker_id: str, origin: str, 
                          target: str) -> None:
        """Log seeker launch event."""
        self.log_event(TestEventType.SEEKER_LAUNCH,
                      seeker_id=seeker_id,
                      origin=origin,
                      target=target)
    
    def log_seeker_impact(self, seeker_id: str, target: str) -> None:
        """Log seeker impact event."""
        self.log_event(TestEventType.SEEKER_IMPACT,
                      seeker_id=seeker_id,
                      target=target)
    
    def log_seeker_expire(self, seeker_id: str, reason: str) -> None:
        """Log seeker expiration event."""
        self.log_event(TestEventType.SEEKER_EXPIRE,
                      seeker_id=seeker_id,
                      reason=reason)
    
    def log_seeker_destroyed(self, seeker_id: str, destroyed_by: str) -> None:
        """Log seeker destroyed by point defense."""
        self.log_event(TestEventType.SEEKER_DESTROYED,
                      seeker_id=seeker_id,
                      destroyed_by=destroyed_by)


def enable_test_logging(enabled: bool = True) -> None:
    """Enable or disable test logging globally."""
    global TEST_LOGGING_ENABLED
    TEST_LOGGING_ENABLED = enabled


def set_test_log_dir(directory: str) -> None:
    """Set the test log output directory."""
    global TEST_LOG_DIR
    TEST_LOG_DIR = directory

def reset_logging() -> None:
    """Reset the global logging state. For testing use only."""
    global TEST_LOGGING_ENABLED, ACTIVE_LOGGER, TEST_LOG_DIR
    TEST_LOGGING_ENABLED = False
    if ACTIVE_LOGGER:
        ACTIVE_LOGGER.close()
    ACTIVE_LOGGER = None
    TEST_LOG_DIR = "tests/simulation/output/logs/"

def log_event(event_type_str: str, **kwargs):
    """
    Global helper to log an event to the active logger.
    
    Args:
        event_type_str: String or Enum for event type
        **kwargs: Log data
    """
    if str(event_type_str).startswith("TestEventType."):
         # It's an enum, use it
         pass
    else:
        # It's a string, try to find it in Enum or use raw
        try:
             # If it's a raw string like "WEAPON_FIRE", checking enum might be good but not strictly required
             pass
        except:
             pass
             
    if ACTIVE_LOGGER:
        ACTIVE_LOGGER.log_event(event_type_str, **kwargs)
