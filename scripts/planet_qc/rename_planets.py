import os
import json
import re
from pathlib import Path

# Configuration
DIRECTORIES = [
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02_Processed"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Needs_Reprocessing"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Planets_V3"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Jupiter"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Neptune"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Earth"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Mars"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Moon"),
    Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Pluto"),
]
STATUS_FILE = Path(r"C:\Developer\StarshipBattles\scripts\planet_qc\qc_status.json")

# Regex to find the ID part: matches everything from the first _[digit]_ onwards
# Example: inspired_extracted_tiled_planets_4_016... -> _4_016...
RENAME_PATTERN = re.compile(r'^.*?(_\d+_.*\.png)$')

def rename_files():
    rename_map = {} # old_name -> new_name

    # 1. First, identify all unique filenames across all directories and determine their new names
    for directory in DIRECTORIES:
        if not directory.exists():
            continue
        
        for file in directory.glob("*.png"):
            if file.name in rename_map:
                continue
            
            match = RENAME_PATTERN.match(file.name)
            if match:
                new_name = f"planet{match.group(1)}"
                if new_name != file.name:
                    rename_map[file.name] = new_name
            else:
                print(f"Skipping {file.name}: Does not match ID pattern.")

    if not rename_map:
        print("No files to rename.")
        return

    print(f"Proposed renames for {len(rename_map)} unique filenames.")

    # 2. Perform the actual renaming on the file system
    for directory in DIRECTORIES:
        if not directory.exists():
            continue
        
        print(f"Processing directory: {directory.name}")
        for file in directory.glob("*.png"):
            if file.name in rename_map:
                new_name = rename_map[file.name]
                new_path = directory / new_name
                try:
                    os.rename(file, new_path)
                except Exception as e:
                    print(f"Error renaming {file.name} to {new_name}: {e}")

    # 3. Update the qc_status.json file
    if STATUS_FILE.exists():
        print("Updating qc_status.json...")
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
        
        new_status = {}
        for old_name, val in status.items():
            if old_name in rename_map:
                new_status[rename_map[old_name]] = val
            else:
                new_status[old_name] = val
        
        with open(STATUS_FILE, "w") as f:
            json.dump(new_status, f, indent=4)
        print("qc_status.json updated.")

    print("Renaming complete.")

if __name__ == "__main__":
    rename_files()
