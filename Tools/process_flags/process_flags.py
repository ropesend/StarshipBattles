import os
import sys
import glob
import shutil
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

# Configuration
INPUT_DIR = os.path.join(Paths.ASSET_DIR, "Images", "Flags", "Processed Flags")
OUTPUT_BASE_DIR = os.path.join(Paths.ASSET_DIR, "Images", "flags")
SIZES = [1024, 512, 256, 128, 64, 32]
FLAG_TYPES = ["rectangle", "shield", "triangle"]

def trim(im):
    """Trims transparent edges from an image."""
    bbox = im.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def find_item_boundaries(im):
    """Finds horizontal boundaries using a two-pass merging strategy to handle noise."""
    alpha = im.getchannel("A")
    width, height = alpha.size
    
    # Analyze columns to find raw active blocks
    column_activity = []
    data = list(alpha.getdata())
    for x in range(width):
        active_count = 0
        for y in range(height):
            if data[y * width + x] > 0:
                active_count += 1
        column_activity.append(active_count > 2)
    
    raw_blocks = []
    in_block = False
    start = 0
    for i, active in enumerate(column_activity):
        if active and not in_block:
            start = i
            in_block = True
        elif not active and in_block:
            raw_blocks.append((start, i))
            in_block = False
    if in_block:
        raw_blocks.append((start, width))
    
    if not raw_blocks:
        return []
        
    # Pass 1: Filter out tiny blocks
    clean_blocks = [b for b in raw_blocks if (b[1] - b[0]) > 20]
    
    if not clean_blocks:
        return []
        
    # Pass 2: Merge cleaned blocks that are close to each other
    merged_blocks = []
    curr_start, curr_end = clean_blocks[0]
    
    for next_start, next_end in clean_blocks[1:]:
        gap = next_start - curr_end
        if gap < 40:
            curr_end = next_end
        else:
            merged_blocks.append((curr_start, curr_end))
            curr_start, curr_end = next_start, next_end
    merged_blocks.append((curr_start, curr_end))
    
    # Final filter for substantial flag bodies
    final_boundaries = [b for b in merged_blocks if (b[1] - b[0]) > 500]
    
    return final_boundaries

def process_image(file_path):
    print(f"Processing {file_path}...")
    try:
        img = Image.open(file_path).convert("RGBA")
    except Exception as e:
        print(f"Error opening {file_path}: {e}")
        return

    base_name = os.path.basename(file_path)
    folder_name = base_name.replace("Gemini_Generated_Image_", "flag_").replace("_no_bg.png", "")
    
    target_dir = os.path.join(OUTPUT_BASE_DIR, folder_name)
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    os.makedirs(target_dir, exist_ok=True)
    
    boundaries = find_item_boundaries(img)
    if len(boundaries) < 3:
        print(f"  Warning: Only found {len(boundaries)} items in {file_path}. Expected 3.")
    
    boundaries.sort()

    # 1. Extract and Trim all flags first
    extracted_flags = []
    for i, (start, end) in enumerate(boundaries[:3]):
        type_name = FLAG_TYPES[i]
        item_img = img.crop((start, 0, end, img.height))
        item_final = trim(item_img)
        if item_final.width > 0 and item_final.height > 0:
            extracted_flags.append((type_name, item_final))

    if not extracted_flags:
        print(f"  Warning: No flags extracted from {file_path}.")
        return

    # 2. Determine Scale Factor based on the largest flag (usually Rectangle)
    # The user wants the rectangle (largest) to define the scale for the set.
    # We find which flag has the largest dimension and scale it to 1024.
    max_dim = 0
    for name, f_img in extracted_flags:
        max_dim = max(max_dim, f_img.width, f_img.height)
    
    # scale_to_1024 = 1024 / max_dim
    # Actually, let's just use 1024 as the container size.
    # We scale so the LARGEST flag in the group fits within 1024x1024.
    
    resampling_method = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS

    for name, f_img in extracted_flags:
        # Save master (as square 1024x1024)
        master_scale = 1024 / max_dim
        sw = max(1, int(f_img.width * master_scale))
        sh = max(1, int(f_img.height * master_scale))
        
        # Center in square
        scaled_f = f_img.resize((sw, sh), resampling_method)
        master_square = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
        px = (1024 - sw) // 2
        py = (1024 - sh) // 2
        master_square.paste(scaled_f, (px, py))
        
        master_name = f"{name}.png"
        master_square.save(os.path.join(target_dir, master_name))
        
        # Save resized versions
        for size in SIZES:
            size_dir = os.path.join(target_dir, str(size))
            os.makedirs(size_dir, exist_ok=True)
            
            # Scale proportionally to the master
            # Each resized version is a square 'size x size'
            scale_factor = size / 1024
            sw_sz = max(1, int(sw * scale_factor))
            sh_sz = max(1, int(sh * scale_factor))
            
            scaled_sz = scaled_f.resize((sw_sz, sh_sz), resampling_method)
            square_sz = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            px_sz = (size - sw_sz) // 2
            py_sz = (size - sh_sz) // 2
            square_sz.paste(scaled_sz, (px_sz, py_sz))
            
            square_sz.save(os.path.join(size_dir, master_name))

def main():
    if not os.path.exists(OUTPUT_BASE_DIR):
        os.makedirs(OUTPUT_BASE_DIR)
        
    files = glob.glob(os.path.join(INPUT_DIR, "*.png"))
    if not files:
        print(f"No PNG files found in {INPUT_DIR}")
        return
    
    print(f"Found {len(files)} files to process.")
    
    for file in files:
        process_image(file)
    
    print("Done!")

if __name__ == "__main__":
    main()
