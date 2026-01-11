import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.strategy.data.galaxy import Galaxy, StarSystem

def verify():
    print("Generating Galaxy...")
    galaxy = Galaxy(radius=100)
    systems = galaxy.generate_systems(count=5, min_dist=10)
    
    print(f"\nGenerated {len(systems)} systems. Checking planet names...\n")
    
    for sys in systems:
        print(f"System: {sys.name} (Star: {sys.star_type.name})")
        if not sys.planets:
            print("  (No planets)")
            continue
            
        for i, p in enumerate(sys.planets):
            print(f"  Planet {i+1}: Name='{p.name}', Dist={p.orbit_distance}, Type={p.planet_type.name}")
            
        print("-" * 30)

if __name__ == "__main__":
    verify()
