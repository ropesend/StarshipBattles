"""
Entry point for the Tech Tree Editor.

Usage:
    py -m Tools.techtree_editor              # Auto-loads data/techtree.json
    py -m Tools.techtree_editor path/to.json  # Load specific file
"""
import sys
import os

# Ensure project root is on sys.path for game imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from Tools.techtree_editor.app import App
from Tools.techtree_editor.gui import EditorGUI


def main():
    app = App()

    # Determine file to load
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = app.get_default_file_path()

    # Load the tech tree
    print(f"Loading: {file_path}")
    errors = app.load_file(file_path)
    print(f"Loaded {len(app.model.nodes)} nodes in {len(app.model.sections)} sections")
    if errors:
        print(f"Validation warnings: {len(errors)}")
        for e in errors:
            print(f"  - {e}")

    # Launch GUI
    gui = EditorGUI(app)
    gui.setup()
    gui.graph.rebuild()
    gui.run()


if __name__ == "__main__":
    main()
