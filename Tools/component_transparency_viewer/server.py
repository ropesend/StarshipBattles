import json
import os
import signal
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "assets").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


PROJECT_ROOT = find_project_root()
BASE_DIR = Path(__file__).resolve().parent
COMPONENTS_ROOT = PROJECT_ROOT / "assets" / "Images" / "Components"
SOURCE_DIR = COMPONENTS_ROOT / "1024"
STAGING_ROOT = Path(
    os.environ.get(
        "COMPONENT_TRANSPARENCY_STAGING",
        str(COMPONENTS_ROOT / "_processed_preview"),
    )
)
STAGED_1024 = STAGING_ROOT / "1024"
MANIFEST_PATH = STAGING_ROOT / "review_manifest.json"

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/originals", StaticFiles(directory=SOURCE_DIR), name="originals")
if STAGED_1024.exists():
    app.mount("/processed", StaticFiles(directory=STAGED_1024), name="processed")


class ReviewUpdate(BaseModel):
    filename: str
    review_status: str
    notes: str = ""


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Review manifest not found. Run Tools/process_components/process_components.py first.",
        )
    with MANIFEST_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_manifest(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


@app.get("/")
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/init")
async def init():
    manifest = load_manifest()
    images = []
    for filename, entry in sorted(manifest.get("images", {}).items()):
        processed_path = STAGED_1024 / filename
        original_path = SOURCE_DIR / filename
        if processed_path.exists() and original_path.exists():
            images.append(
                {
                    "filename": filename,
                    "original_url": f"/originals/{filename}",
                    "processed_url": f"/processed/{filename}",
                    **entry,
                }
            )
    return {
        "manifest_path": str(MANIFEST_PATH),
        "source_dir": str(SOURCE_DIR),
        "staging_dir": str(STAGED_1024),
        "images": images,
    }


@app.post("/api/review")
async def update_review(update: ReviewUpdate):
    if update.review_status not in {"unreviewed", "accepted", "rejected", "manual_cleanup", "recreate"}:
        raise HTTPException(status_code=400, detail="Invalid review status")

    manifest = load_manifest()
    images = manifest.setdefault("images", {})
    if update.filename not in images:
        raise HTTPException(status_code=404, detail="Image not found in manifest")

    images[update.filename]["review_status"] = update.review_status
    images[update.filename]["notes"] = update.notes
    save_manifest(manifest)
    return {"status": "success", "image": images[update.filename]}


@app.get("/api/export/recreate")
async def export_recreate():
    manifest = load_manifest()
    recreate = [
        {"filename": filename, **entry}
        for filename, entry in sorted(manifest.get("images", {}).items())
        if entry.get("review_status") == "recreate"
    ]
    export_path = STAGING_ROOT / "recreate_queue.json"
    export_path.write_text(json.dumps(recreate, indent=2), encoding="utf-8")
    return {"count": len(recreate), "path": str(export_path), "images": recreate}


@app.post("/api/shutdown")
async def shutdown_server():
    os.kill(os.getpid(), signal.SIGTERM)
    return {"status": "shutting down"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8011)
