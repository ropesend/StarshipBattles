import os
import json
import shutil
from PIL import Image

# Configuration
BASE_DIR = r"C:\Developer\StarshipBattles"
STARS_ROOT_DIR = os.path.join(BASE_DIR, "assets", "Images", "Stellar Objects", "Stars")
MASK_CONFIG_FILE = os.path.join(BASE_DIR, "scripts", "star_mask_tool", "mask_configs.json")
METADATA_OUTPUT_FILE = os.path.join(BASE_DIR, "assets", "star_metadata.json")

# Target Tier Directories
TIERS = {
    1024: os.path.join(STARS_ROOT_DIR, "Stars_1024"),
    512: os.path.join(STARS_ROOT_DIR, "Stars_512"),
    256: os.path.join(STARS_ROOT_DIR, "Stars_256"),
    128: os.path.join(STARS_ROOT_DIR, "Stars_128")
}

def ensure_dirs():
    for d in TIERS.values():
        os.makedirs(d, exist_ok=True)

def orchestrate_stars():
    if not os.path.exists(MASK_CONFIG_FILE):
        print(f"Error: {MASK_CONFIG_FILE} not found.")
        return
    
    with open(MASK_CONFIG_FILE, "r") as f:
        configs = json.load(f)
        
    metadata = {}
    
    print(f"Orchestrating {len(configs)} stars...")
    
    for filename, config in configs.items():
        # 1. Source 1024 Master Path
        source_master = os.path.join(STARS_ROOT_DIR, filename)
        if not os.path.exists(source_master):
            # Try to see if it's already in Stars_1024
            source_master_fallback = os.path.join(TIERS[1024], filename)
            if os.path.exists(source_master_fallback):
                source_master = source_master_fallback
            else:
                print(f"Warning: {filename} not found in root or 1024 dir. Skipping.")
                continue
        
        # 2. Open Master to get dimensions
        img = Image.open(source_master)
        width, height = img.size
        
        # 3. Normalized Metadata
        # We normalize relative to the 1024 width/height (usually 1024x1024)
        metadata[filename] = {
            "centerX": config["centerX"] / width,
            "centerY": config["centerY"] / height,
            "radiusCore": config["radius"] / width,
            "radiusCorona": config.get("radiusCorona", config["radius"] + 50) / width
        }
        
        # 4. Generate Tiers
        for size, tier_dir in TIERS.items():
            tier_path = os.path.join(tier_dir, filename)
            
            # Master (1024) Tier logic
            if size == width:
                # If master is already there, don't re-copy
                if os.path.abspath(source_master) != os.path.abspath(tier_path):
                    shutil.copy2(source_master, tier_path)
            else:
                # Downsample using Lanczos
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                resized.save(tier_path, "PNG", optimize=True)
        
        # 5. Cleanup root (move to 1024 if not there)
        if os.path.dirname(source_master) == STARS_ROOT_DIR:
             # Just to be safe, we skip if the filename is already handled above
             # This loop is sequential so copy/remove is fine
             pass

        print(f"  [TIERED] {filename}")

    # Write Metadata
    with open(METADATA_OUTPUT_FILE, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Workflow Complete. Metadata saved to {METADATA_OUTPUT_FILE}")

if __name__ == "__main__":
    ensure_dirs()
    orchestrate_stars()
