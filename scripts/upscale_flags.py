
import os
from PIL import Image

def upscale_flags():
    source_dir = r"C:\Developer\StarshipBattles\assets\Images\Flags\Old Flags"
    target_dir = r"C:\Developer\StarshipBattles\assets\Images\Flags"
    
    # Ensure target directory exists (though it should already)
    os.makedirs(target_dir, exist_ok=True)
    
    files = [f for f in os.listdir(source_dir) if f.lower().endswith('.bmp')]
    total_files = len(files)
    print(f"Found {total_files} BMP files to upscale.")
    
    for i, file_name in enumerate(files):
        source_path = os.path.join(source_dir, file_name)
        target_path = os.path.join(target_dir, file_name)
        
        try:
            with Image.open(source_path) as img:
                # Calculate new size (4x)
                new_width = img.width * 4
                new_height = img.height * 4
                
                # Upscale using Lanczos for high quality
                upscaled_img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
                
                # Save to target directory
                upscaled_img.save(target_path)
                print(f"[{i+1}/{total_files}] Upscaled {file_name} from {img.size} to {upscaled_img.size}")
                
        except Exception as e:
            print(f"Failed to process {file_name}: {e}")

if __name__ == "__main__":
    upscale_flags()
