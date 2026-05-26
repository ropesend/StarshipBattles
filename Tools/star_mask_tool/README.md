# Star Mask Tool

Interactive web application for defining transparency masks on star images with live preview and batch workflow.

## Purpose

Star images on black backgrounds need carefully tuned transparency to look correct when composited in-game. Unlike nebulae (which can be auto-processed), stars require manual control over the opaque core radius and the corona falloff region. This tool provides a visual editor where you can position concentric circles (core and corona), see a live preview of the resulting transparency on both black and white backgrounds, then save the processed image and advance to the next star.

## Requirements

- `fastapi`
- `uvicorn`
- `Pillow` (PIL)
- `numpy`
- `pydantic`

## Usage

```bash
python Tools/star_mask_tool/server.py
```

Then open `http://127.0.0.1:8000` in a browser.

**Note:** The `BASE_DIR` path in `server.py` is hardcoded and may need to be updated to match your local project layout. It expects star source images in `assets/images/stellar_objects/Stars/BlackBackground/`.

### Web Interface

The interface has three panels:

1. **Editor** -- drag to position the mask center; adjust core and corona radii with sliders, text inputs, or keyboard shortcuts.
2. **Preview on Black** -- live SVG-masked preview showing how the star will look composited on a dark background.
3. **Preview on White** -- same preview on white, making it easy to spot transparency issues in the corona.

A sidebar lists all star images with checkmarks indicating which have been processed.

### Keyboard Shortcuts

| Key              | Action                        |
|------------------|-------------------------------|
| Arrow keys       | Move center (1px)             |
| Shift + arrows   | Move center (10px)            |
| `[` / `]`        | Decrease / increase core radius (1px) |
| `{` / `}`        | Decrease / increase corona radius (1px) |
| `r`              | Auto-center on brightness centroid |
| `1` `2` `3` `4`  | Set outline color (white, yellow, red, blue) |
| `Ctrl+Enter`     | Save and advance to next star |

### API Endpoints

| Method | Endpoint                  | Description                          |
|--------|---------------------------|--------------------------------------|
| GET    | `/api/stars`              | List all star images and their status |
| GET    | `/api/centroid/{filename}`| Calculate brightness centroid         |
| POST   | `/api/save`               | Process and save a star image         |

### Files

| File               | Description                                           |
|--------------------|-------------------------------------------------------|
| `server.py`        | FastAPI backend with image processing logic            |
| `mask_configs.json`| Persistent storage of per-star mask configurations     |
| `static/index.html`| Single-page web UI with SVG mask preview               |

## Output

Processed star images are saved as transparent PNGs to `assets/images/stellar_objects/Stars/`. The transparency is computed using:

- **Power-law curve** (`alpha = luminance^0.152`) as the base transparency from pixel brightness.
- **Radial falloff** -- full opacity within the core radius, linear falloff to zero at the corona radius.
- **Core override** -- all pixels inside the core radius are forced to 100% opacity.

Mask configurations are persisted in `mask_configs.json` so stars can be reprocessed with the same settings.
