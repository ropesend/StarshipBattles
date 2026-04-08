# Visual Test Galaxy

Interactive Pygame visualizer for galaxy generation with zoom, pan, and detail levels.

## Purpose

Provides a real-time interactive window for visually inspecting generated galaxies. Supports zooming from full-galaxy overview down to individual system detail (planets, warp points, companion stars). Use this for hands-on exploration of galaxy layouts, warp lane connectivity, and system internals during development.

## Requirements

- `pygame` (included in the base project)

## Usage

```bash
python Tools/visual_test_galaxy/visual_test_galaxy.py
```

A 1600x900 resizable Pygame window opens showing the generated galaxy.

## Controls

| Input | Action |
|---|---|
| Mouse scroll | Zoom in/out |
| WASD / Arrow keys | Pan the camera |
| R | Regenerate the galaxy with a new random seed |
| Window resize | Adapts to new window size |
| Close window | Exit |

## Detail Levels

The visualizer renders progressively more detail as you zoom in:

| Zoom Level | What Is Shown |
|---|---|
| < 0.8 | Star dots only (color = star color) |
| 0.8+ | System name labels |
| 1.5+ | Hex grid overlay, warp point markers (purple dots) |
| 3.0+ | Planet dots at their hex locations (colored by planet type) |
| 5.0+ | Planet name labels, companion star labels |

## Output

Interactive window only. No files are written.

## Generation Parameters

The default configuration generates a galaxy with:
- Radius: 4000 hex units
- System count: 80
- Minimum distance: 400 hex units between systems
- Warp lanes auto-generated

These are hardcoded in `main()`. Edit the source to change them.
