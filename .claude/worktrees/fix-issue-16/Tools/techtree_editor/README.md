# Tech Tree Editor

Standalone visual editor for `data/techtree.json`. Built with Dear PyGui.

## Requirements

```
pip install dearpygui
```

Tested with Dear PyGui 1.11.1 on Python 3.11.

## Usage

From the project root:

```bash
# Load default techtree.json
py -m Tools.techtree_editor

# Load a specific file
py -m Tools.techtree_editor path/to/techtree.json
```

## Features

### Node Graph (Center Panel)
- **Pan**: Middle-mouse drag or right-click drag
- **Zoom**: Scroll wheel
- **Select**: Left-click a node or link
- **Multi-select**: Shift+click or box select
- **Minimap**: Bottom-right corner

### Node Editing (Right Panel)
When a node is selected, the properties panel shows:
- **Name** — display name
- **Max Levels** — 1-50
- **Base Decay** — chance decay per turn (0-1)
- **Volatility** — RP-to-chance conversion coefficient (0-1)
- **Price** — base RP cost multiplier
- **Price Curve** — flat, linear, quadratic, exponential, logarithmic, sqrt
- **Section** — branch assignment
- **Requirements** — with editable level ranges and negate toggles
- **Balance Preview** — estimated turns-to-breakthrough at various RP levels

### Connections
- **Create link**: Drag from an output pin (right side) to an input pin (left side)
- **Delete link**: Select the link and press Delete
- **OR-groups**: Edit > Add OR-Group to Selected (adds a new input pin)
- **Negated requirements**: Toggle via the "Negate" checkbox in the properties panel

### File Operations
- **Ctrl+S** — Save
- **File > Open** — Open a different tech tree file
- **File > Save As** — Save to a new location

### Undo/Redo
- **Ctrl+Z** — Undo
- **Ctrl+Y** — Redo

### Other
- **Edit > Add Node** — Create a new tech node
- **Delete** — Delete selected nodes/links
- **View > Reset Layout** — Auto-arrange all nodes by dependency depth
- **View > Validate** — Check for cycles, dangling references, orphans
- **View > Balance Preview** — Show balance metrics for selected node
- **View > Show Outliers** — Find nodes with extreme balance values
- **Sections > New Section** — Create a new branch/section

## File Format

The editor reads and writes standard `techtree.json` format. Node positions are stored in a separate sidecar file (`techtree_layout.json`) so the game's data file stays clean.

### Round-Trip Fidelity

Saving normalizes formatting (consistent indentation) but preserves all data exactly. The game's `TechTree.load_from_json()` reads the output identically.

## Architecture

```
__main__.py      → Entry point
app.py           → Controller (file ops, undo/redo, commands)
model.py         → EditorModel (TechTree wrapper + positions/sections)
commands.py      → Command pattern (undo/redo for all edit operations)
gui.py           → Dear PyGui window, menus, property panel
node_graph.py    → Node editor widget (nodes, pins, links)
layout.py        → Auto-layout algorithm
persistence.py   → JSON serialization (TechTree → JSON)
balance.py       → Balance preview (wraps ResearchService)
```

The editor imports game classes directly (`game.research.data.*`, `game.research.systems.*`) for data loading, validation, and balance estimation. No game code is modified.
