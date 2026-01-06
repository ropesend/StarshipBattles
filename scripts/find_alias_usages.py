
import os
import re

ALIASES = [
    "Bridge", "Weapon", "ProjectileWeapon", "BeamWeapon", "SeekerWeapon", 
    "Engine", "Thruster", "ManeuveringThruster", "Shield", "ShieldRegenerator", 
    "Generator", "Hangar", "Armor", "Sensor", "Electronics", "Tank", 
    "CrewQuarters", "LifeSupport"
]

def check_files():
    found_count = 0
    for root, dirs, files in os.walk("."):
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
                
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Look for "from game.simulation.components.component import ... Alias"
                for line in content.splitlines():
                    # Strip comment
                    if '#' in line:
                         line = line.split('#')[0]
                    
                    if "import" not in line: continue
                    
                    for alias in ALIASES:
                        # Regex to match import of alias
                        # Matches: from game.simulation.components.component import ..., Alias, ...
                        pattern = r"from game\.simulation\.components\.component import.*(\b" + alias + r"\b)"
                        if re.search(pattern, line):
                            print(f"{path}: Importing {alias}")
                            found_count += 1
                        
            except Exception as e:
                # Ignore verify errors
                pass
                
    print(f"Found {found_count} files importing legacy aliases.")

if __name__ == "__main__":
    check_files()
