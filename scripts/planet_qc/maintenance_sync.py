import os
import json
import shutil
from pathlib import Path

# Configuration (Mirrored from main.py)
ORIGINAL_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02")
PROCESSED_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02_Processed")
NEEDS_REPRO_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Needs_Reprocessing")
STATUS_FILE = Path(r"C:\Developer\StarshipBattles\scripts\planet_qc\qc_status.json")

CLASSIFICATIONS = {
    "good": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Planets_V3"),
    "repro": NEEDS_REPRO_DIR,
    "jupiter": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Jupiter"),
    "neptune": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Neptune"),
    "earth": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Earth"),
    "mars": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Mars"),
    "moon": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Moon"),
    "pluto": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Pluto"),
}

def maintenance_sync():
    # 1. Load status
    status = {}
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)

    # 2. Get all images from PROCESSED_DIR
    all_images = [f.name for f in PROCESSED_DIR.glob("*.png")]
    print(f"Scanning {len(all_images)} images for sync...")

    for filename in all_images:
        status_val = status.get(filename, "good")
        
        # Determine the source for copying
        if status_val == "repro":
            src = ORIGINAL_DIR / filename
        else:
            src = PROCESSED_DIR / filename

        # target folder
        if status_val in CLASSIFICATIONS:
            dest_folder = CLASSIFICATIONS[status_val]
            dest_folder.mkdir(parents=True, exist_ok=True)
            target_path = dest_folder / filename
            
            # Clean up other folders
            for other_val, other_folder in CLASSIFICATIONS.items():
                if other_val != status_val:
                    other_path = other_folder / filename
                    if other_path.exists():
                        os.remove(other_path)

            # Copy if missing
            if src.exists() and not target_path.exists():
                print(f"Syncing [{status_val}] {filename}...")
                shutil.copy2(src, target_path)

    print("Sync complete.")

if __name__ == "__main__":
    maintenance_sync()
