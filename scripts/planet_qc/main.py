from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
import shutil
from pathlib import Path

app = FastAPI()

# Configuration
ORIGINAL_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02")
PROCESSED_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02_Processed")
NEEDS_REPRO_DIR = Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Needs_Reprocessing")
STATUS_FILE = Path(r"C:\Developer\StarshipBattles\scripts\planet_qc\qc_status.json")

CLASSIFICATIONS = {
    "good": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Planets_V3"),
    "repro": NEEDS_REPRO_DIR,
    "jupiter": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Jupiter"),
    "neptune": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Neptune"),
    "earth": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Earth"),
    "mars": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Mars"),
    "moon": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Moon"),
    "pluto": Path(r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Pluto"),
}

# Ensure directories exist
for folder in CLASSIFICATIONS.values():
    folder.mkdir(parents=True, exist_ok=True)
NEEDS_REPRO_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files for images
app.mount("/original", StaticFiles(directory=str(ORIGINAL_DIR)), name="original")
app.mount("/processed", StaticFiles(directory=str(PROCESSED_DIR)), name="processed")

templates = Jinja2Templates(directory="scripts/planet_qc/templates")

def load_status():
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_status(status):
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=4)

def sync_folders(filename, status_val):
    # Determine the source for copying:
    # repro -> Original DIR (black background)
    # class -> Processed DIR (high-res masked)
    
    # 1. Remove from all possible classification folders first
    for folder in CLASSIFICATIONS.values():
        target = folder / filename
        if target.exists():
            os.remove(target)
            
    # 2. Add to the new designated folder
    if status_val in CLASSIFICATIONS:
        dest_folder = CLASSIFICATIONS[status_val]
        # logic for source selection
        if status_val == "repro":
            src = ORIGINAL_DIR / filename
        else:
            src = PROCESSED_DIR / filename
            
        if src.exists():
            shutil.copy2(src, dest_folder / filename)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request, filter: str = "all"):
    status = load_status()
    all_images = sorted([f.name for f in PROCESSED_DIR.glob("*.png")])
    
    filtered_images = []
    for img in all_images:
        # User requested default to "good"
        s = status.get(img, "good")
        if filter == "all":
            filtered_images.append({"name": img, "status": s})
        elif filter == s:
            filtered_images.append({"name": img, "status": s})
            
    # Stats logic needs to respect default "good" for accounting
    stats = {
        "total": len(all_images),
        "good": sum(1 for img in all_images if status.get(img, "good") == "good"),
        "repro": sum(1 for s in status.values() if s == "repro"),
        "special": sum(1 for s in status.values() if s in ["jupiter", "neptune", "earth", "mars", "moon", "pluto"])
    }
    
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "images": filtered_images, 
        "filter": filter,
        "stats": stats
    })

@app.post("/update")
async def update_status(filename: str = Form(...), action: str = Form(...)):
    status = load_status()
    status[filename] = action
    save_status(status)
    sync_folders(filename, action)
    return JSONResponse({"status": "ok", "new_status": action})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
