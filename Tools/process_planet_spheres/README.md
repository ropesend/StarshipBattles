# Process Planet Spheres

Detects the circular boundary of a planet in an image and applies a transparency mask to isolate the sphere.

## Purpose

Planet artwork often includes background artifacts, glow halos, or rectangular canvas edges that need to be removed before use as in-game sprites. This tool uses circle detection (Hough transform with contour-based fallback) on a downscaled version of each image for performance, then creates a precise circular alpha mask at full resolution to cleanly isolate the planet sphere.

## Requirements

- `opencv-python` (`cv2`)
- `numpy`

## Usage

```bash
python Tools/process_planet_spheres/process_planet_spheres.py --input <input_dir> --output <output_dir> [--sample N]
```

### Arguments

| Argument   | Required | Default | Description                                          |
|------------|----------|---------|------------------------------------------------------|
| `--input`  | Yes      |         | Directory containing source planet images             |
| `--output` | Yes      |         | Directory for output transparent PNGs (created if missing) |
| `--sample` | No       | 0       | Process only the first N images (0 = all)             |

### Detection Strategy

1. **Downscale** the image to 512x512 for fast detection.
2. **Hough circle detection** (`cv2.HoughCircles`) -- selects the circle closest to the image center.
3. **Fallback** -- if Hough fails, uses `minEnclosingCircle` on the largest thresholded contour.
4. **Scale up** the detected circle parameters to full resolution and apply the mask with 2px padding.

Supported input formats: `.png`, `.jpg`, `.jpeg`.

## Output

RGBA `.png` files in the output directory, one per input image. Pixels outside the detected planet sphere are fully transparent. Progress is reported every 10 images with average processing time and ETA.
