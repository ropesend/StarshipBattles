import os
import re

directory = r"c:\Dev\Starship Battles\tests\unit"
files = [
    "test_weapons_report_layout.py",
    "test_ui_dynamic_update.py",
    "test_stats_render.py",
    "test_shields.py",
    "test_selection_refinements.py",
    "test_multi_selection_logic.py",
    "test_modifier_row.py",
    "test_mandatory_modifiers.py",
    "test_crash_regressions.py",
    "test_builder_structure_features.py",
    "test_builder_improvements.py"
]

for filename in files:
    path = os.path.join(directory, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove pygame.quit() calls
        new_content = content.replace("pygame.quit()", "pass # pygame.quit() removed for session isolation")
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
        else:
            print(f"No changes for {filename}")
