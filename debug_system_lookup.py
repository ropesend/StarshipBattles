
from game.core.hex_math import HexCoord
from game.strategy.data.galaxy import Galaxy, StarSystem
from game.strategy.data.planet import Planet, PlanetType

def debug_system_lookup():
    galaxy = Galaxy()
    
    # 1. Create System
    sys_loc = HexCoord(100, 100)
    system = StarSystem("Test System", sys_loc)
    
    # 2. Create Planet at local (1, 0)
    planet_loc = HexCoord(1, 0)
    planet = Planet(
        name="Test Planet",
        location=planet_loc,
        orbit_distance=1,
        mass=1e24,
        radius=6000e3,
        surface_area=4e14,
        density=5000,
        surface_gravity=9.8,
        surface_pressure=100000,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL
    )
    system.planets.append(planet)
    
    # 3. Add to Galaxy
    galaxy.add_system(system)
    
    # 4. Check Lookup
    global_hex = sys_loc + planet_loc
    print(f"System Loc: {sys_loc}")
    print(f"Planet Local: {planet_loc}")
    print(f"Global Hex: {global_hex}")
    
    found_system = galaxy.get_system_at_location(global_hex)
    
    if found_system:
        print(f"SUCCESS: Found system '{found_system.name}' at {global_hex}")
    else:
        print(f"FAILURE: Could not find system at {global_hex}")
        
    # debug deeper
    print("\nDebug loop:")
    for sys_location, sys in galaxy.systems.items():
        print(f"Checking System at {sys_location}")
        for p in sys.planets:
            calc_loc = sys_location + p.location
            print(f"  Planet {p.name} at local {p.location} -> global {calc_loc}")
            if calc_loc == global_hex:
                 print("    MATCH!")
            else:
                 print("    . . .")

if __name__ == "__main__":
    debug_system_lookup()
