# Process Cursors

Extracts individual cursor sprites from a 2x4 grid sprite sheet and exports them at 64x64 and 32x32 resolutions.

## Purpose

The game's cursor set is authored as a single 2x4 sprite sheet image. This tool splits the sheet into 8 individual cursor images, applies luminance-based transparency to remove the background, normalizes all cursors to a uniform square size (preserving the arrow tip at the top-left origin), and exports them at two resolutions for use in the game UI.

## Requirements

- `Pillow` (PIL)

## Usage

```bash
python Tools/process_cursors/process_cursors.py
```

No command-line arguments. The tool reads its source image from `Tools/process_cursors/source/71wO8.jpg` (kept with the tool, not under the runtime asset tree) and writes processed cursor sprites into `assets/images/cursor/32x32/` and `assets/images/cursor/64x64/`.

### Extracted Cursors

| Index | Name             | Notes                                      |
|-------|------------------|--------------------------------------------|
| 0     | cursor_default   |                                            |
| 1     | cursor_add       |                                            |
| 2     | cursor_target    |                                            |
| 3     | cursor_info      |                                            |
| 4     | cursor_denied    |                                            |
| 5     | cursor_orbit     |                                            |
| 6     | cursor_planet    | Right side of cell is masked out (x > 320) |
| 7     | cursor_scan      |                                            |

## Output

```
assets/images/cursor/
  64x64/
    cursor_default.png
    cursor_add.png
    ...
  32x32/
    cursor_default.png
    cursor_add.png
    ...
```

Each cursor is a transparent PNG, uniformly sized within each resolution tier, with the pointer tip aligned to the top-left corner.
