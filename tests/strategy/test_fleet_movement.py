import pytest
from game.strategy.data.galaxy import Galaxy, StarSystem, WarpPoint
from game.strategy.data.hex_math import HexCoord
from game.strategy.data.pathfinding import find_path_interstellar
from game.strategy.data.fleet import Fleet

def test_fleet_initialization():
    loc = HexCoord(0, 0)
    fleet = Fleet(1, 0, loc)
    assert fleet.location == loc
    assert fleet.ships == []

def test_interstellar_pathfinding():
    # Setup Mini Galaxy
    # Sys A (0,0) <-> Sys B (10,0)
    # Sys B <-> Sys C (20,0)
    # Sys A NOT connected to C directly
    
    galaxy = Galaxy()
    
    sys_a = StarSystem("Alpha", HexCoord(0, 0))
    sys_b = StarSystem("Beta", HexCoord(10, 0))
    sys_c = StarSystem("Gamma", HexCoord(20, 0))
    
    galaxy.add_system(sys_a)
    galaxy.add_system(sys_b)
    galaxy.add_system(sys_c)
    
    # Manual Warp Link
    # A <-> B
    galaxy.create_vars_link(sys_a, sys_b)
    # B <-> C
    galaxy.create_vars_link(sys_b, sys_c)
    
    # Test Path A -> B
    path_ab = find_path_interstellar(sys_a, sys_b, galaxy)
    assert path_ab is not None
    assert len(path_ab) == 2
    assert path_ab[0] == sys_a
    assert path_ab[1] == sys_b
    
    # Test Path A -> C (should go via B)
    path_ac = find_path_interstellar(sys_a, sys_c, galaxy)
    assert path_ac is not None
    assert len(path_ac) == 3
    assert path_ac[0] == sys_a
    assert path_ac[1] == sys_b
    assert path_ac[2] == sys_c

def test_no_path():
    galaxy = Galaxy()
    sys_a = StarSystem("Alpha", HexCoord(0, 0))
    sys_b = StarSystem("Beta", HexCoord(100, 0)) # Far away, no link
    
    galaxy.add_system(sys_a)
    galaxy.add_system(sys_b)
    
    path = find_path_interstellar(sys_a, sys_b, galaxy)
    assert path is None
