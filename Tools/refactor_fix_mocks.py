import os
import re

ROOT_DIR = r"c:\Dev\Starship Battles\unit_tests"

# String replacements for mock paths
REPLACEMENTS = {
    # Phase 2
    "'ship.": "'game.simulation.entities.ship.",
    '"ship.': '"game.simulation.entities.ship.',
    "'ship_io.": "'game.simulation.systems.persistence.",
    '"ship_io.': '"game.simulation.systems.persistence.',
    "'components.": "'game.simulation.components.component.",
    '"components.': '"game.simulation.components.component.',
    "'abilities.": "'game.simulation.components.abilities.",
    '"abilities.': '"game.simulation.components.abilities.',
    "'projectiles.": "'game.simulation.entities.projectile.",
    '"projectiles.': '"game.simulation.entities.projectile.',
    "'battle_engine.": "'game.simulation.systems.battle_engine.",
    '"battle_engine.': '"game.simulation.systems.battle_engine.',
    "'resources.": "'game.simulation.systems.resource_manager.",
    '"resources.': '"game.simulation.systems.resource_manager.',
    
    # Phase 4
    "'ai.": "'game.ai.controller.",
    '"ai.': '"game.ai.controller.',
    "'ai_behaviors.": "'game.ai.behaviors.",
    '"ai_behaviors.': '"game.ai.behaviors.',
}

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        return

    original_content = content
    
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
        
    if content != original_content:
        print(f"Fixing mocks in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
             if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
