
import os
from PIL import Image

def prepare_inputs():
    source_dir = r"C:\Developer\StarshipBattles\assets\Images\Flags\Old Flags"
    staging_dir = r"C:\Developer\StarshipBattles\temp_enhancement_inputs"
    
    if os.path.exists(staging_dir):
        import shutil
        shutil.rmtree(staging_dir)
    os.makedirs(staging_dir)
    
    files = sorted([f for f in os.listdir(source_dir) if f.endswith(".bmp")])
    
    processed_bases = set()
    files_to_enhance = []
    
    for f in files:
        # Logic to identify unique types
        # We want: *Set.bmp and *Texture.bmp
        # We skip: *Texture_Fleet.bmp and *Texture_Ship.bmp
        
        if "_Texture_Fleet" in f or "_Texture_Ship" in f:
            continue
            
        name_part = os.path.splitext(f)[0]
        
        # Convert to PNG
        try:
            with Image.open(os.path.join(source_dir, f)) as img:
                out_name = name_part + ".png"
                out_path = os.path.join(staging_dir, out_name)
                img.save(out_path)
                files_to_enhance.append(out_path)
        except Exception as e:
            print(f"Error preparing {f}: {e}")
            
    print(f"Prepared {len(files_to_enhance)} images for enhancement.")
    for p in files_to_enhance:
        print(p)

if __name__ == "__main__":
    prepare_inputs()
