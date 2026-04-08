# Development Tools

> **Audience:** Developers and LLM agents working on Starship Battles.
>
> All non-game development utilities live here: asset processors, editors, test runners, diagnostics, and analysis tools. Each tool has its own subfolder with a README.

---

## Quick Reference

| Tool | Purpose | Type |
|------|---------|------|
| [analyze_dependency_graph](analyze_dependency_graph/) | Import dependency graph from entry points | Analysis |
| [background_eraser](background_eraser/) | Remove image backgrounds via FastAPI server | Asset Processing |
| [check_orphans](check_orphans/) | Find orphaned modules in game/ | Analysis |
| [component_visuals_manager](component_visuals_manager/) | Web UI for managing component visual assets | GUI Editor |
| [diagnose_blueprints](diagnose_blueprints/) | Verify star system blueprints produce expected results | Diagnostics |
| [find_orphaned_tests](find_orphaned_tests/) | Find test files without matching source modules | Testing |
| [fix_designs](fix_designs/) | Auto-fix ship designs (crew housing, life support, stats) | Testing |
| [galaxy_screenshot](galaxy_screenshot/) | Headless galaxy screenshot generator (PIL) | Visualization |
| [image_comparator](image_comparator/) | Compare original vs recreated component images | QA |
| [inspect_galaxy](inspect_galaxy/) | Galaxy generation stats inspector (JSON + console) | Visualization |
| [loc](loc/) | Lines of code counter with section breakdowns | Analysis |
| [nebula_to_alpha](nebula_to_alpha/) | Convert nebula/background images to transparent PNGs | Asset Processing |
| [process_cursors](process_cursors/) | Process cursor sprite sheets into individual files | Asset Processing |
| [process_flags](process_flags/) | Process flag images into multi-resolution variants | Asset Processing |
| [process_planet_spheres](process_planet_spheres/) | Detect and mask planet spheres (OpenCV) | Asset Processing |
| [qa_observer](qa_observer/) | QA session recorder (audio + screenshots) | QA |
| [ship_background_remover](ship_background_remover/) | Remove black backgrounds from ship images | Asset Processing |
| [star_mask_tool](star_mask_tool/) | Star masking via FastAPI server | Asset Processing |
| [techtree_editor](techtree_editor/) | Visual tech tree editor (Dear PyGui) | GUI Editor |
| [test_sharded](test_sharded/) | Sharded parallel test runner | Testing |
| [validate_designs](validate_designs/) | Validate ship designs against component registry | Testing |
| [visual_test_galaxy](visual_test_galaxy/) | Interactive galaxy visualizer (Pygame) | Visualization |

---

## Tools by Category

### Testing

- **[test_sharded](test_sharded/)** -- Sharded parallel test runner. Auto-detects CPU cores, uses greedy load balancing from prior timing data. **This is the primary way to run the full test suite.**
- **[validate_designs](validate_designs/)** -- Validates ship/complex designs against the component registry. Checks crew housing, life support, layer mass budgets, and mass consistency.
- **[fix_designs](fix_designs/)** -- Auto-fixes quickstart designs: adds missing crew housing/life support, recalculates expected_stats.
- **[find_orphaned_tests](find_orphaned_tests/)** -- Finds test files in `tests/unit/` that have no matching source file in `game/`.

### Asset Processing

- **[background_eraser](background_eraser/)** -- FastAPI web server for interactively removing image backgrounds.
- **[nebula_to_alpha](nebula_to_alpha/)** -- Batch converts nebula/system background/warp point images from opaque to transparent PNGs using luminance-based alpha with gamma correction.
- **[process_cursors](process_cursors/)** -- Splits cursor sprite sheet into individual cursor files at 64x64 and 32x32.
- **[process_flags](process_flags/)** -- Extracts flags from composite images, trims, and generates multi-resolution variants (1024 down to 32).
- **[process_planet_spheres](process_planet_spheres/)** -- Detects circular planet bounds using Hough circles (OpenCV) and applies transparency masks.
- **[ship_background_remover](ship_background_remover/)** -- Removes black backgrounds from ship images with configurable threshold, trims, and centers on square canvas.
- **[star_mask_tool](star_mask_tool/)** -- FastAPI server for configuring star masking parameters.

### GUI Editors

- **[techtree_editor](techtree_editor/)** -- Standalone visual editor for `data/techtree.json`. Built with Dear PyGui. Full undo/redo, node graph, auto-layout, balance preview.
- **[component_visuals_manager](component_visuals_manager/)** -- Web UI for managing and tagging component visual assets.

### Diagnostics & Analysis

- **[check_orphans](check_orphans/)** -- Scans `game/` for modules that aren't imported by anything. Helps identify dead code.
- **[diagnose_blueprints](diagnose_blueprints/)** -- Generates star systems from each blueprint and verifies they match expected characteristics.
- **[analyze_dependency_graph](analyze_dependency_graph/)** -- Parses Python imports from entry points to build a dependency graph. Identifies unreachable modules.
- **[loc](loc/)** -- Counts lines of code by section (production, tests, simulation tests, extras). Supports JSON output for tracking.

### Visualization

- **[galaxy_screenshot](galaxy_screenshot/)** -- Generates galaxy layout screenshots headlessly using PIL. Supports batch mode across galaxy types and system counts.
- **[inspect_galaxy](inspect_galaxy/)** -- Generates galaxies and outputs comprehensive stats as structured JSON (for AI-agent parsing) plus human-readable summaries. Supports batch comparison and chart generation.
- **[visual_test_galaxy](visual_test_galaxy/)** -- Interactive Pygame-based galaxy visualization with camera controls and hex snapping.

### QA

- **[qa_observer](qa_observer/)** -- Passive QA session helper. Records microphone audio and Windows Snipping Tool screenshots, aligns them into unified Markdown logs for agent review. Uses Google Cloud Speech-to-Text.
- **[image_comparator](image_comparator/)** -- FastAPI web tool for side-by-side comparison of original vs recreated component images.

---

## Creating a New Tool

### Structure

Every tool lives in its own subfolder under `Tools/`:

```
Tools/
  my_new_tool/
    my_new_tool.py    # Main entry point (or server.py for web tools)
    README.md         # Required -- see template below
    requirements.txt  # Only if tool has dependencies beyond the base project
    static/           # Only if tool serves web content
```

### Rules

1. **Own subfolder** -- never add loose files to `Tools/` root
2. **README.md** -- every tool must have one (see template below)
3. **Self-contained** -- tools must not import from other tools
4. **Not imported by game** -- nothing in `game/` should import from `Tools/`

### Path Resolution

Tools that need to import from `game.*` must bootstrap `sys.path` using the project root finder pattern:

```python
import sys
from pathlib import Path


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths  # Now available for asset/data paths
```

Use `Paths.*` constants (from `game.core.paths`) for all asset and data file references. Never hardcode absolute paths.

### README Template

```markdown
# Tool Name

One-line description of what this tool does.

## Purpose

Why this tool exists and when you would use it. 2-3 sentences.

## Requirements

Extra pip dependencies beyond the base project, or "No additional dependencies."

## Usage

    python Tools/tool_name/tool_name.py [arguments]

### Arguments (if applicable)

- `--flag` -- description (default: X)
- `[positional]` -- description

## Output

What the tool produces: console output, files, web pages, etc.
```

Expand beyond the template for complex tools (see [qa_observer](qa_observer/README.md) and [techtree_editor](techtree_editor/README.md) for examples).
