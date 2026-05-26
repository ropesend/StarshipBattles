import os
import sys
from pathlib import Path
from PIL import Image
import numpy as np


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths

def process_nebula(input_path, output_path, gamma_color=0.8, gamma_alpha=0.6):
    """
    Converts a nebula image on a black background to a transparent PNG.
    Uses pixel intensity as alpha and applies gamma correction to brighten midtones.
    """
    img = Image.open(input_path).convert("RGB")
    data = np.array(img).astype(np.float32) / 255.0
    
    # Calculate initial alpha based on pixel intensity
    alpha = np.max(data, axis=2)
    
    # Apply gamma correction to brighten midtones
    # Gamma < 1.0 brightens the image, especially in darker/mid areas.
    data = np.power(data, gamma_color)
    alpha = np.power(alpha, gamma_alpha)
    
    # Scale back to 0-255
    data = (data * 255.0).astype(np.uint8)
    alpha = (alpha * 255.0).astype(np.uint8)
    
    # Create the RGBA image
    rgba = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)
    rgba[..., :3] = data
    rgba[..., 3] = alpha
    
    result = Image.fromarray(rgba, "RGBA")
    result.save(output_path, "PNG")
    print(f"  Saved: {output_path.name} (Gamma: C={gamma_color}, A={gamma_alpha})")

if __name__ == "__main__":
    # Settings
    dir_path = Path(Paths.ASSET_DIR) / "Images" / "stellar_objects" / "Nebulae"
    
    print(f"Processing nebulae in: {dir_path}")
    
    # --- Run for Nebulae ---
    # We look for the original PNG files (without stars)
    png_files = list(dir_path.glob("Nebulae_*.png"))
    if not png_files:
        print("No Nebulae_*.png files found!")
    else:
        for img_file in png_files:
            if "_transparent" in img_file.name:
                continue
            output_file = dir_path / f"{img_file.stem}_transparent.png"
            print(f"Processing {img_file.name}...")
            process_nebula(img_file, output_file, gamma_color=0.7, gamma_alpha=0.5)
    
    # --- Run for system_backgrounds ---
    sys_dir_path = Path(Paths.ASSET_DIR) / "Images" / "system_backgrounds"
    print(f"\nProcessing system backgrounds in: {sys_dir_path}")
    
    jpg_files = list(sys_dir_path.glob("*.jpg"))
    if not jpg_files:
        print("No JPG files found in system_backgrounds!")
    else:
        for img_file in jpg_files:
            output_file = sys_dir_path / f"{img_file.stem}.png"
            print(f"Processing {img_file.name}...")
            process_nebula(img_file, output_file, gamma_color=0.7, gamma_alpha=0.5)
            
    # --- Run for warp_points ---
    warp_dir_path = Path(Paths.ASSET_DIR) / "Images" / "stellar_objects" / "warp_points"
    print(f"\nProcessing warp points in: {warp_dir_path}")
    
    jpg_files = list(warp_dir_path.glob("*.jpg"))
    if not jpg_files:
        print("No JPG files found in warp_points!")
    else:
        for img_file in jpg_files:
            output_file = warp_dir_path / f"{img_file.stem}.png"
            print(f"Processing {img_file.name}...")
            process_nebula(img_file, output_file, gamma_color=0.7, gamma_alpha=0.5)
    
    print("\nAll tasks done!")
