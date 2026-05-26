# Image Comparator

Side-by-side comparison viewer for original vs. recreated component art assets.

## Purpose

Provides a browser-based tool for visually auditing AI-recreated component images against their originals. Automatically matches images by their component ID (e.g., `Comp_004`) and displays them in a scrollable comparison grid. Use this during asset recreation workflows to verify visual quality and consistency.

## Requirements

- `fastapi`
- `uvicorn`

## Usage

```bash
python Tools/image_comparator/server.py
```

Then open `http://localhost:8001` in a browser.

## How It Works

The server scans two directories for images:

- **Original**: `assets/images/components/1024/`
- **Recreated**: `assets/images/altcomponents/Recreated/`

It extracts the 3-digit component ID from each filename (e.g., `Comp_007`), matches originals to recreations, and presents them side-by-side in rows.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/images` | GET | Returns a list of matched image pairs with their component IDs |
| `/` | GET | Serves the comparison UI (`index.html`) |

## Output

Browser-based comparison grid. The header shows a progress counter (e.g., "15 / 42 Recreated (36%)"). Missing recreations show a "Recreation pending..." placeholder. No files are written.

## Configuration

The `REPO_ROOT`, `RECREATED_DIR`, and `ORIGINAL_DIR` variables in `server.py` are hardcoded. Update them if your repo root differs.
