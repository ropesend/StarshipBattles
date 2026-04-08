import os
import re
from PIL import Image

SOURCE_DIR = r"C:\Developer\StarshipBattles\assets\Images\altcomponents\Recreated"
TARGET_DIR = r"C:\Developer\StarshipBattles\assets\Images\Components\Components 2048"
START_INDEX = 243
TARGET_SIZE = (2048, 2048)
# JPG_QUALITY = 95  # No longer used for PNG

def get_index_from_filename(filename):
    """Extracts the index XXX from 2048Portrait_Comp_XXX_recreated.png"""
    match = re.search(r"Comp_(\d+)", filename)
    if match:
        return int(match.group(1))
    return None

def main():
    if not os.path.exists(TARGET_DIR):
        print(f"Creating target directory: {TARGET_DIR}")
        os.makedirs(TARGET_DIR)

    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".png") and "Comp_" in f]
    files.sort(key=get_index_from_filename)

    print(f"Found {len(files)} source files.")

    count = 0
    for filename in files:
        source_idx = get_index_from_filename(filename)
        if source_idx is None:
            continue

        target_idx = source_idx + START_INDEX
        target_filename = f"2048Portrait_Comp_{target_idx:03d}.png"
        
        source_path = os.path.join(SOURCE_DIR, filename)
        target_path = os.path.join(TARGET_DIR, target_filename)

        try:
            with Image.open(source_path) as img:
                # Rescale using high-quality sampler
                img_rescaled = img.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
                
                # Save as PNG
                img_rescaled.save(target_path, "PNG")
                print(f"[{count+1}/{len(files)}] Processed: {filename} -> {target_filename}")
                count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"Operation complete. Processed {count} images.")

if __name__ == "__main__":
    main()
