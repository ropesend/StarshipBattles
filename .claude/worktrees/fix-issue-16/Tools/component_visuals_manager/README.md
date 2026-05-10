# Component Visuals Manager

Web UI for assigning sprite images to game components and managing image metadata tags.

## Purpose

Provides an interactive browser-based tool for mapping component IDs in `components.json` to their sprite sheet indices, and for organizing component images with a tagging system stored in `image_metadata.json`. This is the primary tool for visual asset management during component art production.

## Requirements

- `fastapi`
- `uvicorn`

## Usage

### Web UI (server.py)

```bash
python Tools/component_visuals_manager/server.py
```

Then open `http://localhost:8000` in a browser.

### Prompt Generator (generate_alternates.py)

```bash
python Tools/component_visuals_manager/generate_alternates.py
```

This is a standalone script that reads component image descriptions from a text file and generates engineered prompts for AI image generation (e.g., for creating alternate component art with consistent styling).

## How It Works

### Server

The server loads component data from `data/components.json` and image metadata from `assets/Images/Components/image_metadata.json`. It serves component sprite images from multiple resolution directories (64px through 2048px) and provides the following API:

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/init` | GET | Returns components, image metadata, and image file listing |
| `/api/component/image` | POST | Updates a component's `sprite_index` in `components.json` |
| `/api/image/bulk-tags` | POST | Adds or removes a tag from multiple sprite indices at once |
| `/api/tags/create` | POST | Creates a new tag in the global tag list |
| `/api/tags/delete` | POST | Deletes a tag globally and removes it from all assignments |
| `/api/shutdown` | POST | Gracefully shuts down the server |

### Prompt Generator

Reads `descriptions.txt` from the alt-components directory, parses per-image descriptions, and applies prompt engineering transformations (e.g., converting interior scene descriptions to isolated floating-object compositions). Outputs engineered prompts for component IDs 004-014.

## Output

- **Server**: Modifies `components.json` (sprite index assignments) and `image_metadata.json` (tag assignments) in place.
- **Prompt Generator**: Prints engineered prompts to stdout.

## File Structure

```
component_visuals_manager/
  server.py               # FastAPI server
  generate_alternates.py   # AI prompt generator
  static/
    index.html             # Main UI page
    app.js                 # Frontend logic
    styles.css             # Styling
```
