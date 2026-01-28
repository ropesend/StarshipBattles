
import os
import re

MAPPINGS = [
    ("import main", "import game.app as main"),
    ("from main import", "from game.app import"),
    ("'main'", "'game.app'"),
    ("import battle", "import game.ui.screens.battle as battle"),
    ("from battle import", "from game.ui.screens.battle import"),
    ("'battle'", "'game.ui.screens.battle'"),
]
# Note: 'main' string replacement is risky if it matches other strings.
# But in test_main_integration.py context it is sys.modules['main'].
# I should be careful.
# Maybe target ONLY test_main_integration.py?
# Or use word boundary?

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Skipping {filepath}: {e}")
        return

    original_content = content
    
    # Specific safe replacements
    content = re.sub(r'\bimport main\b', 'import game.app as main', content)
    content = re.sub(r'\bfrom main import\b', 'from game.app import', content)
    content = re.sub(r'\bsys\.modules\[[\'"]main[\'"]\]', "sys.modules['game.app']", content)
    
    content = re.sub(r'\bimport battle\b', 'import game.ui.screens.battle as battle', content)
    content = re.sub(r'\bfrom battle import\b', 'from game.ui.screens.battle import', content)
    content = re.sub(r'\bsys\.modules\[[\'"]battle[\'"]\]', "sys.modules['game.ui.screens.battle']", content)

    if content != original_content:
        print(f"Updating imports in {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def main():
    target_dir = r"c:\Dev\Starship Battles\tests\unit"
    for root, dirs, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.py'):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
