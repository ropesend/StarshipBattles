import os
import uvicorn
import numpy as np
import json
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI(title="Star Masking Tool v2.3")

# Paths
BASE_DIR = r"C:\Developer\StarshipBattles"
BLACK_BG_DIR = os.path.join(BASE_DIR, "assets", "Images", "Stellar Objects", "Stars", "BlackBackground")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "Images", "Stellar Objects", "Stars")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "mask_configs.json")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files and images
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/images", StaticFiles(directory=BLACK_BG_DIR), name="images")

class MaskConfig(BaseModel):
    centerX: float
    centerY: float
    radius: float # Core Radius
    radiusCorona: Optional[float] = None # Corona Radius
    outlineColor: Optional[str] = "white"

class StarInfo(BaseModel):
    name: str
    processed: bool
    config: Optional[MaskConfig] = None

class SaveRequest(BaseModel):
    filename: str
    centerX: float
    centerY: float
    radius: float # Core Radius
    radiusCorona: float # Corona Radius
    outlineColor: Optional[str] = "white"

def load_configs() -> Dict[str, dict]:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading configs: {e}")
    return {}

def save_configs(configs: Dict[str, dict]):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(configs, f, indent=2)
    except Exception as e:
        print(f"Error saving configs: {e}")

@app.get("/api/stars", response_model=List[StarInfo])
def list_stars():
    if not os.path.exists(BLACK_BG_DIR):
        return []
    
    configs = load_configs()
    stars = []
    for f in os.listdir(BLACK_BG_DIR):
        if f.lower().endswith(".png"):
            processed = os.path.exists(os.path.join(OUTPUT_DIR, f))
            star_cfg = configs.get(f)
            stars.append(StarInfo(
                name=f, 
                processed=processed, 
                config=MaskConfig(**star_cfg) if star_cfg else None
            ))
    return sorted(stars, key=lambda s: s.name)

@app.get("/api/centroid/{filename}")
def get_centroid(filename: str):
    path = os.path.join(BLACK_BG_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    try:
        img = Image.open(path).convert("L")
        data = np.array(img)
        
        # Simple thresholding to find bright pixels (top 20%)
        threshold = np.max(data) * 0.2
        y, x = np.where(data > threshold)
        
        if len(x) > 0 and len(y) > 0:
            return {"x": float(np.mean(x)), "y": float(np.mean(y))}
        return {"x": data.shape[1] / 2, "y": data.shape[0] / 2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save")
def save_star(req: SaveRequest):
    input_path = os.path.join(BLACK_BG_DIR, req.filename)
    output_path = os.path.join(OUTPUT_DIR, req.filename)
    
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Source image not found")
    
    try:
        # 1. Update Persistent Config
        configs = load_configs()
        configs[req.filename] = req.model_dump()
        save_configs(configs)

        # 2. Process Image
        img = Image.open(input_path).convert("RGBA")
        data = np.array(img)
        
        r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
        
        # Luminance calculation (standard ITU-R 601-2)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        
        # Power-Law Transparency Curve: Alpha = Brightness^0.152
        new_alpha_base = np.power(luminance / 255.0, 0.152) * 255.0
        
        # Calculate Radial Falloff Multiplier (v2.3)
        height, width = luminance.shape
        y, x = np.ogrid[:height, :width]
        dist = np.sqrt((x - req.centerX)**2 + (y - req.centerY)**2)
        
        # Factor is 1.0 at RadiusCore, 0.0 at RadiusCorona
        if req.radiusCorona > req.radius:
             multiplier = np.clip((req.radiusCorona - dist) / (req.radiusCorona - req.radius), 0, 1)
        else:
             # If corona is set same as core, it's a hard edge
             multiplier = (dist <= req.radius).astype(float)
             
        final_alpha = (new_alpha_base * multiplier).astype(np.uint8)
        
        # Masking Core: Always 100% Opaque (v2.1)
        mask_core = dist <= req.radius
        final_alpha[mask_core] = 255
            
        data[:,:,3] = final_alpha
        
        final_img = Image.fromarray(data)
        final_img.save(output_path, "PNG", optimize=True)
        
        return {"status": "success", "file": output_path}
    except Exception as e:
        print(f"Error processing {req.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
