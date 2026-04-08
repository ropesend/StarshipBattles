import os
from PIL import Image

SOURCE_DIR = r"C:\Developer\StarshipBattles\assets\Images\Components\Components 2048"
PARENT_DIR = r"C:\Developer\StarshipBattles\assets\Images\Components"

TIERS = [256, 128, 64]

def main():
    source_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".png") and "Comp_" in f]
    print(f"Found {len(source_files)} source PNG files.\n")

    for tier in TIERS:
        target_dir = os.path.join(PARENT_DIR, f"Components {tier}")
        if not os.path.exists(target_dir):
            print(f"Creating target directory: {target_dir}")
            os.makedirs(target_dir)

        # 1. Cleanup Target Folder
        legacy_files = os.listdir(target_dir)
        print(f"[{tier}px] Cleaning up {len(legacy_files)} files in target...")
        for f in legacy_files:
            try:
                os.remove(os.path.join(target_dir, f))
            except Exception as e:
                print(f"  Error deleting {f}: {e}")

        # 2. Downscale and Migrate PNGs
        count = 0
        for filename in source_files:
            # 2048Portrait_Comp_XXX.png -> [Tier]Portrait_Comp_XXX.png
            target_filename = filename.replace("2048Portrait_", f"{tier}Portrait_")
            
            source_path = os.path.join(SOURCE_DIR, filename)
            target_path = os.path.join(target_dir, target_filename)

            try:
                with Image.open(source_path) as img:
                    # Downscale using high-quality sampler
                    img_rescaled = img.resize((tier, tier), Image.Resampling.LANCZOS)
                    
                    # Save as PNG
                    img_rescaled.save(target_path, "PNG")
                    count += 1
            except Exception as e:
                print(f"Error processing {filename} for {tier}px: {e}")
        
        print(f"[{tier}px] Operation complete. Successfully processed {count} images.\n")

    print("\nAll low-resolution libraries generated.")

if __name__ == "__main__":
    main()
