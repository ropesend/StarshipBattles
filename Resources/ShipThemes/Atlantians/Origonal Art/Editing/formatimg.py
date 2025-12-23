import os
from PIL import Image

def process_images():
    # --- CONFIGURATION ---
    # Increase this if you still see speckles. Decrease if it eats into the ship.
    # 30 is a good starting point for JPEGs.
    BLACK_THRESHOLD = 30 
    TARGET_SIZE = (2048, 2048)
    
    # 1. Setup folders
    current_folder = os.getcwd()
    output_folder = os.path.join(current_folder, "processed_output")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Files to ignore
    excluded_files = ["process_assets.py", "process_assets_v2.py", ".DS_Store"] 
    
    # 2. Get list of files
    files = [f for f in os.listdir(current_folder) if os.path.isfile(f)]

    print(f"Found {len(files)} files. Starting processing with Threshold={BLACK_THRESHOLD}...")

    for filename in files:
        if filename in excluded_files:
            continue

        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff')):
            continue

        try:
            print(f"Processing: {filename}...")
            
            img = Image.open(filename).convert("RGBA")
            
            # --- STEP A: Remove Background with Tolerance ---
            datas = img.getdata()
            new_data = []
            
            for item in datas:
                # item is (R, G, B, A)
                # Check if R, G, and B are all lower than our threshold
                if item[0] <= BLACK_THRESHOLD and item[1] <= BLACK_THRESHOLD and item[2] <= BLACK_THRESHOLD:
                    new_data.append((255, 255, 255, 0)) # Turn Transparent
                else:
                    new_data.append(item) # Keep original pixel

            img.putdata(new_data)

            # --- STEP B: Find the Asset (Crop) ---
            bbox = img.getbbox()
            
            if bbox:
                cropped_img = img.crop(bbox)
            else:
                print(f"  Warning: {filename} resulted in a blank image. Threshold might be too high.")
                continue

            # --- STEP C: Center on New Canvas ---
            final_img = Image.new("RGBA", TARGET_SIZE, (0, 0, 0, 0))
            
            # Math to center the cropped asset
            x_offset = (TARGET_SIZE[0] - cropped_img.width) // 2
            y_offset = (TARGET_SIZE[1] - cropped_img.height) // 2
            
            final_img.paste(cropped_img, (x_offset, y_offset))

            # --- STEP D: Save ---
            save_name = os.path.splitext(filename)[0] + ".png"
            final_img.save(os.path.join(output_folder, save_name), "PNG")
            
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

    print("------------------------------------------------")
    print(f"Done! Check the '{output_folder}' folder.")

if __name__ == "__main__":
    process_images()