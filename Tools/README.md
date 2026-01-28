# Tools Directory

This directory contains standalone tools and utilities for development and asset management.

## Active Tools

### Game Integration

- **formation_editor.py** - Formation editor scene integrated into the game. Allows designing and editing ship formation patterns.

### Asset Management

- **component_manager.py** - GUI tool for managing component image assets. Allows tagging, organizing, and exporting component graphics.

- **component_graphic_picker.py** - GUI tool for assigning graphic images to components in components.json.

- **process_planet_images.py** - Batch processing tool for planet image assets.

- **resize_components.py** - Batch tool for resizing component images to standard sizes.

### Verification Utilities

- **verify_accuracy_formula.py** - Verifies weapon accuracy calculations against expected formulas.

- **verify_resources.py** - Verifies resource system configuration and component resource usage.

- **verify_cache.py** - Verifies caching behavior in the system.

### Utility

- **cleanup_pygame.py** - Utility for cleaning up pygame resources properly.

## Usage

Most tools can be run directly with Python:

```bash
python Tools/component_manager.py
python Tools/verify_resources.py
```

The formation_editor is integrated into the game and accessed through the main application.

## Legacy Tools

One-time migration and refactoring scripts have been moved to `_legacy_docs/Tools/` for historical reference.
