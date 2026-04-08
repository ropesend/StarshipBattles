# Background Eraser

Web-based tool for viewing and working with system background images.

## Purpose

Provides a FastAPI server with a browser UI for browsing the star system background images stored in the assets directory. Useful for reviewing background art assets and preparing them for background removal or editing workflows.

## Requirements

- `fastapi`
- `uvicorn`

## Usage

```bash
python Tools/background_eraser/server.py
```

Then open `http://127.0.0.1:8000` in a browser.

## How It Works

The server exposes a REST API that lists and serves images from the `assets/Images/System Backgrounds` directory. The browser-based frontend (in `static/index.html`) provides a visual interface for browsing the images.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/images` | GET | Lists all JPEG/PNG images in the backgrounds directory |
| `/api/image/{filename}` | GET | Returns a specific image as a base64-encoded data URI |
| `/` | GET | Serves the static frontend |

## Output

Browser-based UI for viewing system background images. No files are written.

## Configuration

The `ASSETS_DIR` variable in `server.py` is hardcoded to the backgrounds path. Update it if your repo root differs.
