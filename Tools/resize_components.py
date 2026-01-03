import os
import sys
try:
    from PIL import Image
except ImportError:
    print("Pillow (PIL) not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def resize_and_populate():
    base_dir = r"C:\Dev\Starship Battles\assets\Images\Components"
    source_dir = os.path.join(base_dir, "Components 2048")
    
    targets = {
        256: os.path.join(base_dir, "Components 256"),
        512: os.path.join(base_dir, "Components 512"),
        1024: os.path.join(base_dir, "Components 1024"),
        64: os.path.join(base_dir, "Tiles") # Tiles at 64x64
    }
    
    # Verify source
    if not os.path.exists(source_dir):
        print(f"ERROR: Source directory not found: {source_dir}")
        return

    # 1. Clear directories
    for size, path in targets.items():
        if os.path.exists(path):
            print(f"Clearing {path}...")
            # Delete all files in the directory
            for f in os.listdir(path):
                file_path = os.path.join(path, f)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
        else:
            print(f"Creating {path}...")
            os.makedirs(path)

    # 2. Process images
    files = [f for f in os.listdir(source_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    print(f"Found {len(files)} images in source. Processing...")

    processed_count = 0
    for filename in files:
        # Strict checking for the naming convention to avoid processing garbage
        # Convention: 2048Portrait_Comp_XXX.jpg
        if not filename.startswith("2048Portrait_Comp_"):
            print(f"Skipping {filename} (does not match 2048Portrait_Comp_XXX convention)")
            continue

        source_path = os.path.join(source_dir, filename)
        
        try:
            with Image.open(source_path) as img:
                for size, target_path in targets.items():
                    # Resize
                    resized_img = img.resize((size, size), Image.Resampling.LANCZOS)
                    
                    # Save - Keeping the SAME filename as requested/implied (repopulate)
                    # Although typical convention might be 256Portrait_..., user didn't specify renaming.
                    save_path = os.path.join(target_path, filename)
                    resized_img.save(save_path, quality=90)
                
                processed_count += 1
                if processed_count % 10 == 0:
                    print(f"Processed {processed_count} images...")
                    
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print(f"Done. Resized and populated {processed_count} images.")

if __name__ == "__main__":
    resize_and_populate()
