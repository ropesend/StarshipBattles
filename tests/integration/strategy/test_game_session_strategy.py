import pytest
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig

def test_game_session_initialization():
    """Test that GameSession initializes galaxy and empires correctly."""
    config = GameConfig(system_count=5)
    session = GameSession(config=config)
    
    assert session.galaxy is not None
    assert len(session.empires) == 2
    assert len(session.systems) == 5
    assert session.turn_number == 1
    assert session.turn_engine is not None
    
    # Check start scenario
    # Player @ System 0
    assert session.active_empire.colonies
    assert session.systems[0].planets[0].owner_id == session.active_empire.id
    
    # Enemy @ System -1
    assert session.enemy_empire.colonies
    assert session.systems[-1].planets[0].owner_id == session.enemy_empire.id

def test_process_turn_advancement():
    """Test that process_turn increments turn counter and calls engine."""
    config = GameConfig(system_count=5)
    session = GameSession(config=config)
    current_turn = session.turn_number
    
    session.process_turn()
    
    assert session.turn_number == current_turn + 1
