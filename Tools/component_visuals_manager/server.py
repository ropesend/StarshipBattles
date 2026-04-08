import os
import json
import signal
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
METADATA_JSON = os.path.join(REPO_ROOT, "assets", "Images", "Components", "image_metadata.json")
IMAGE_DIR_64 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 64")
IMAGE_DIR_128 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 128")
IMAGE_DIR_256 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 256")
IMAGE_DIR_512 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 512")
IMAGE_DIR_1024 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 1024")
IMAGE_DIR_2048 = os.path.join(REPO_ROOT, "assets", "Images", "Components", "Components 2048")
# Using 128 as the primary source of truth for indices/filenames
IMAGE_DIR = IMAGE_DIR_128

# Static mounting
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/assets/64", StaticFiles(directory=IMAGE_DIR_64), name="assets_64")
app.mount("/assets/128", StaticFiles(directory=IMAGE_DIR_128), name="assets_128")
app.mount("/assets/256", StaticFiles(directory=IMAGE_DIR_256), name="assets_256")
app.mount("/assets/512", StaticFiles(directory=IMAGE_DIR_512), name="assets_512")
app.mount("/assets/1024", StaticFiles(directory=IMAGE_DIR_1024), name="assets_1024")
app.mount("/assets/2048", StaticFiles(directory=IMAGE_DIR_2048), name="assets_2048")

class ComponentUpdate(BaseModel):
    component_id: str
    sprite_index: int

class TagBulkUpdate(BaseModel):
    sprite_indices: List[int]
    tag: str
    action: str  # "add" or "remove"

class NewTag(BaseModel):
    tag: str

class TagDelete(BaseModel):
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
        
        # List images: Strictly only PNGs from the whitelisted IMAGE_DIR (Components 128)
        # Any images in "New Component images" or "Tiles" will be ignored by this scan.
        images = []
        if os.path.exists(IMAGE_DIR):
            for f in sorted(os.listdir(IMAGE_DIR)):
                if f.lower().endswith(".png"):
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

@app.post("/api/image/bulk-tags")
async def update_image_tags_bulk(update: TagBulkUpdate):
    try:
        data = load_json(METADATA_JSON)
        for idx in update.sprite_indices:
            idx_str = str(idx)
            if idx_str not in data["assignments"]:
                data["assignments"][idx_str] = []
            
            tags = data["assignments"][idx_str]
            if update.action == "add":
                if update.tag not in tags:
                    tags.append(update.tag)
            elif update.action == "remove":
                if update.tag in tags:
                    tags.remove(update.tag)
        
        save_json(METADATA_JSON, data)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tags/delete")
async def delete_tag(update: TagDelete):
    try:
        data = load_json(METADATA_JSON)
        tag = update.tag.lower().strip()
        
        # Remove from global tags
        if tag in data["tags"]:
            data["tags"].remove(tag)
        
        # Remove from all assignments
        count = 0
        for idx_str in data["assignments"]:
            if tag in data["assignments"][idx_str]:
                data["assignments"][idx_str].remove(tag)
                count += 1
        
        save_json(METADATA_JSON, data)
        return {"status": "success", "count": count}
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

@app.post("/api/shutdown")
async def shutdown_server():
    try:
        # Graceful shutdown for Windows uvicorn
        os.kill(os.getpid(), signal.SIGTERM)
        return {"status": "shutting down"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_index():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
