import os
import sys
from pathlib import Path
from PIL import Image, ImageChops


def _find_project_root():
    """Find project root by looking for game/ and data/ directories."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "game").is_dir() and (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


_PROJECT_ROOT = _find_project_root()
sys.path.insert(0, str(_PROJECT_ROOT))

from game.core.paths import Paths


def process_cursors():
    cursor_dir = os.path.join(Paths.ASSET_DIR, 'Images', 'Cursor')
    input_path = os.path.join(cursor_dir, '71wO8.jpg')
    output_base = cursor_dir
    
    # Ensure directories exist
    os.makedirs(os.path.join(output_base, '64x64'), exist_ok=True)
    os.makedirs(os.path.join(output_base, '32x32'), exist_ok=True)

    img = Image.open(input_path)
    width, height = img.size
    
    # 2x4 grid
    cols = 2
    rows = 4
    cell_w = width // cols
    cell_h = height // rows
    
    names = [
        "cursor_default", "cursor_add",
        "cursor_target", "cursor_info",
        "cursor_denied", "cursor_orbit",
        "cursor_planet", "cursor_scan"
    ]
    
    cells_data = []
    max_w = 0
    max_h = 0
    
    # First pass: process all cells and find the global max dimensions relative to their top-left bbox
    for i in range(8):
        col = i % cols
        row = i // cols
        
        left = col * cell_w
        top = row * cell_h
        right = left + cell_w
        bottom = top + cell_h
        
        cell = img.crop((left, top, right, bottom))
        cell = cell.convert("RGBA")
        
        # Apply transparency based on luminance
        datas = cell.getdata()
        new_data = []
        for item in datas:
            v = max(item[0], item[1], item[2])
            alpha = v if v >= 15 else 0
            new_data.append((item[0], item[1], item[2], alpha))
        cell.putdata(new_data)
        
        if i == 6: # Planet mask
            pixels = cell.load()
            for x in range(320, cell_w):
                for y in range(cell_h):
                    pixels[x, y] = (0, 0, 0, 0)
        
        bbox = cell.getbbox()
        if bbox:
            # We assume all cursors have the same arrow tip offset.
            # We crop from the top-left of the content to the bottom-right of the content.
            # We'll collect the content and keep track of the largest size.
            content = cell.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
            cells_data.append(content)
            max_w = max(max_w, content.width)
            max_h = max(max_h, content.height)
        else:
            cells_data.append(None)

    # Use a uniform square size for all icons
    uniform_size = max(max_w, max_h)

    # Second pass: Paste each into the same size canvas and resize
    for i, content in enumerate(cells_data):
        if content is None: continue
        
        # Create a uniform high-res frame
        final_hres = Image.new("RGBA", (uniform_size, uniform_size), (0, 0, 0, 0))
        # Pasting at (0,0) ensures the "tip" (which was the bbox top-left) is at (0,0)
        final_hres.paste(content, (0, 0))
        
        for size in [64, 32]:
            resized = final_hres.resize((size, size), Image.Resampling.LANCZOS)
            save_dir = os.path.join(output_base, f"{size}x{size}")
            resized.save(os.path.join(save_dir, f"{names[i]}.png"))
            print(f"Saved {names[i]} at {size}x{size}")

if __name__ == "__main__":
    process_cursors()
