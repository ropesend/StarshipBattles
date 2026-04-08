import os
import re
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

app = FastAPI(title="Image Comparison Tool")

# Configuration
REPO_ROOT = r"C:\Developer\StarshipBattles"
RECREATED_DIR = os.path.join(REPO_ROOT, "assets", "Images", "altcomponents", "Recreated")
ORIGINAL_DIR = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 1024")

# Mount directories for static serving
if os.path.exists(RECREATED_DIR):
    app.mount("/recreated", StaticFiles(directory=RECREATED_DIR), name="recreated")
if os.path.exists(ORIGINAL_DIR):
    app.mount("/original", StaticFiles(directory=ORIGINAL_DIR), name="original")

def extract_id(filename: str) -> Optional[str]:
    """Extracts a 3-digit ID from the filename."""
    # Look for ID preceded by Comp_ to avoid matching '204' in '2048'
    match = re.search(r"Comp_(\d{3})", filename)
    return match.group(1) if match else None

@app.get("/api/images")
async def list_images():
    """Returns a matched list of images by ID, sorted numerically."""
    recreated_files = os.listdir(RECREATED_DIR) if os.path.exists(RECREATED_DIR) else []
    original_files = os.listdir(ORIGINAL_DIR) if os.path.exists(ORIGINAL_DIR) else []

    # Map ID -> filename
    recreated_map = {}
    for f in recreated_files:
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            img_id = extract_id(f)
            if img_id:
                recreated_map[img_id] = f

    original_map = {}
    for f in original_files:
        if f.lower().endswith((".png", ".jpg", ".jpeg")):
            img_id = extract_id(f)
            if img_id:
                original_map[img_id] = f

    # Get all unique IDs
    all_ids = sorted(list(set(recreated_map.keys()) | set(original_map.keys())))

    # Create pairs
    pairs = []
    for img_id in all_ids:
        pairs.append({
            "id": img_id,
            "recreated": recreated_map.get(img_id),
            "original": original_map.get(img_id)
        })

    return pairs

@app.get("/")
async def get_index():
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
