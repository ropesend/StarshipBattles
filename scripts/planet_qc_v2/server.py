from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os
from pathlib import Path
from typing import Dict

app = FastAPI()

# Enable CORS for React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(r"C:\Developer\StarshipBattles")
IMAGE_DIR = BASE_DIR / "assets" / "Images" / "Stellar Objects" / "Planets" / "Planets_V3"
JSON_PATH = BASE_DIR / "scripts" / "planet_qc" / "partial_classifications.json"

# Mount images
# Mount images
if IMAGE_DIR.exists():
    app.mount("/images", StaticFiles(directory=str(IMAGE_DIR)), name="images")

class ClassificationUpdate(BaseModel):
    filename: str
    new_type: str

@app.get("/api/planets")
def get_planets():
    if not JSON_PATH.exists():
        return {}
    with open(JSON_PATH, "r") as f:
        return json.load(f)

@app.post("/api/update")
def update_classification(update: ClassificationUpdate):
    if not JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="Classification file not found")
    
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    
    data[update.filename] = update.new_type
    
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=4)
    
    return {"status": "success", "filename": update.filename, "new_type": update.new_type}

# Mount UI static files at root last
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="ui")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
