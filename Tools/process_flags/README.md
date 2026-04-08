# Process Flags

Splits composite flag images into individual flag shapes and exports them at multiple resolutions.

## Purpose

Flag artwork is generated as a single wide image containing three flag variants side by side (rectangle, shield, triangle) on a transparent background. This tool automatically detects the horizontal boundaries of each flag shape, extracts them, trims transparent edges, and produces a multi-resolution set suitable for in-game faction emblems, UI icons, and map markers.

## Requirements

- `Pillow` (PIL)

## Usage

```bash
python Tools/process_flags/process_flags.py
```

No command-line arguments. The tool processes all `.png` files in the input directory.

### Input/Output Directories

| Directory | Path |
|-----------|------|
| Input     | `assets/Images/Flags/Processed Flags/` |
| Output    | `assets/Images/Flags/Processed/`        |

Input filenames are expected to follow the pattern `Gemini_Generated_Image_*_no_bg.png`. The tool derives a folder name from each input file (e.g., `flag_abc123`).

## Output

For each input image, a folder is created containing:

```
assets/Images/Flags/Processed/flag_<id>/
  rectangle.png      # 1024x1024 master
  shield.png
  triangle.png
  1024/
    rectangle.png
    shield.png
    triangle.png
  512/
    ...
  256/
    ...
  128/
    ...
  64/
    ...
  32/
    ...
```

All images are centered on square canvases. The largest flag in each set defines the scale factor -- smaller shapes are proportionally scaled to maintain consistent relative sizing across the three variants.

### Resolution Tiers

1024, 512, 256, 128, 64, 32 pixels (square).
