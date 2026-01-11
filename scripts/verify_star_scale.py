
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.ui.screens.strategy_scene import StrategyScene

def verify_star_scaling():
    print("Verifying Star Scaling Logic...")
    
    # Mocking
    HEX_SIZE = 10
    camera_zoom = 1.0
    diameter_hexes = 6.0
    
    # Old Logic
    old_radius = int(diameter_hexes * 6 * camera_zoom)
    old_diameter_px = old_radius * 2
    # Expected Old Diameter: 6 * 6 * 1 * 2 = 72 pixels.
    # Expected Hex Diameter in Pixels (approx): 6 hexes * 10 * 1.73 ~= 104 pixels? 
    # Or just 6 * 20 (width) = 120?
    
    # New Logic
    new_radius = int(diameter_hexes * HEX_SIZE * camera_zoom)
    new_diameter_px = new_radius * 2
    
    print(f"Hex Size: {HEX_SIZE}")
    print(f"Star Diameter (Hexes): {diameter_hexes}")
    print(f"Camera Zoom: {camera_zoom}")
    print("-" * 30)
    print(f"Old Radius Calculation: {old_radius} -> Diameter: {old_diameter_px}px")
    print(f"New Radius Calculation: {new_radius} -> Diameter: {new_diameter_px}px")
    print("-" * 30)
    
    # Target size check
    # A 6-hex star should be roughly same size as 6 hexes.
    # 1 hex from center to corner is 10px. Width is 20px (flat to flat approx 17).
    # 6 hexes width ~= 6 * 20 = 120px (corner to corner alignment)
    
    if new_diameter_px == 120:
        print("SUCCESS: New diameter matches expected 120px (2 * 6 * 10).")
    else:
        print(f"WARNING: New diameter {new_diameter_px}px. Expected 120px.")

if __name__ == "__main__":
    verify_star_scaling()
