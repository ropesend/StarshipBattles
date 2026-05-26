import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64

app = FastAPI(title="Background Eraser API")

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
ASSETS_DIR = r"C:\Developer\StarshipBattles\assets\Images\system_backgrounds"

@app.get("/api/images")
async def list_images():
    """List all JPEG/PNG images in the backgrounds directory."""
    if not os.path.exists(ASSETS_DIR):
        return []
    
    files = [f for f in os.listdir(ASSETS_DIR) 
             if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    return sorted(files)

@app.get("/api/image/{filename}")
async def get_image(filename: str):
    """Serve a specific image file."""
    file_path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(file_path, "rb") as f:
        content = f.read()
        
    mime_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
    encoded = base64.b64encode(content).decode()
    return JSONResponse({"data": f"data:{mime_type};base64,{encoded}"})

# Mount static files
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    print(f"Starting Background Eraser Tool...")
    print(f"Targeting: {ASSETS_DIR}")
    uvicorn.run(app, host="127.0.0.1", port=8000)
