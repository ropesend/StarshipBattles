import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = "C:\\Developer\\StarshipBattles"
COMPONENTS_JSON = os.path.join(REPO_ROOT, "data", "components.json")
METADATA_JSON = os.path.join(REPO_ROOT, "data", "image_metadata.json")
IMAGE_DIR = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 256")

# Static mounting
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/assets", StaticFiles(directory=IMAGE_DIR), name="assets")

class ComponentUpdate(BaseModel):
    component_id: str
    sprite_index: int

class TagUpdate(BaseModel):
    sprite_index: int
    tags: List[str]

class NewTag(BaseModel):
    tag: str

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

@app.get("/api/init")
async def get_init():
    try:
        components_data = load_json(COMPONENTS_JSON)
        metadata_data = load_json(METADATA_JSON)
        
        # List images
        images = []
        for f in sorted(os.listdir(IMAGE_DIR)):
            if f.lower().endswith((".jpg", ".png", ".jpeg")):
                images.append(f)
                
        return {
            "components": components_data["components"],
            "metadata": metadata_data,
            "images": images
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/component/image")
async def update_component_image(update: ComponentUpdate):
    try:
        data = load_json(COMPONENTS_JSON)
        found = False
        for c in data["components"]:
            if c["id"] == update.component_id:
                c["sprite_index"] = update.sprite_index
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="Component not found")
            
        save_json(COMPONENTS_JSON, data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/image/tags")
async def update_image_tags(update: TagUpdate):
    try:
        data = load_json(METADATA_JSON)
        idx_str = str(update.sprite_index)
        data["assignments"][idx_str] = update.tags
        save_json(METADATA_JSON, data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tags/create")
async def create_tag(new_tag: NewTag):
    try:
        data = load_json(METADATA_JSON)
        tag = new_tag.tag.lower().strip()
        if tag not in data["tags"]:
            data["tags"].append(tag)
            save_json(METADATA_JSON, data)
            return {"status": "success", "tags": data["tags"]}
        return {"status": "exists", "tags": data["tags"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
