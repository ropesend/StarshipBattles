import os

ROOT_DIR = r"c:\Dev\Starship Battles\unit_tests"

REPLACEMENTS = {
    '"game.simulation.components.component.json"': '"components.json"',
    "'game.simulation.components.component.json'": "'components.json'",
    '"game.simulation.components.abilities.json"': '"abilities.json"',
    "'game.simulation.components.abilities.json'": "'abilities.json'",
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
        print(f"Fixing JSON paths in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
             if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
