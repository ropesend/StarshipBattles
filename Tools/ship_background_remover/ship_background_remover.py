import os
import argparse
from PIL import Image
from pathlib import Path

def trim(im):
    """Trims transparent edges from an image."""
    bbox = im.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

def remove_background(img, threshold=30):
    """
    Removes black background with a given threshold.
    Returns an RGBA image with alpha=0 for pixels below the threshold.
    """
    img = img.convert("RGBA")
    data = img.getdata()
    new_data = []
    for item in data:
        # item is (R, G, B, A)
        if item[0] <= threshold and item[1] <= threshold and item[2] <= threshold:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def process_ship_image(input_path, output_path, threshold=30, size=2048):
    """
    Processes a single ship image: remoes background, trims, and centers in a square canvas.
    """
    print(f"Processing: {input_path.name}...")
    img = Image.open(input_path)
    
    # 1. Remove background
    img = remove_background(img, threshold)
    
    # 2. Trim to bounding box
    img = trim(img)
    
    if img.width == 0 or img.height == 0:
        print(f"  Warning: {input_path.name} resulted in a blank image. Threshold might be too high.")
        return False

    # 3. Center on square canvas
    final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    
    # Scale to fit if larger than target size (upholding 2048 standard)
    if img.width > size or img.height > size:
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
    
    x_offset = (size - img.width) // 2
    y_offset = (size - img.height) // 2
    final_img.paste(img, (x_offset, y_offset))

    # 4. Save
    final_img.save(output_path, "PNG")
    return True

def main():
    parser = argparse.ArgumentParser(description="Process generated ship images into transparent game skins.")
    parser.add_argument("--input", required=True, help="Input directory containing JPG/PNG images.")
    parser.add_argument("--output", required=True, help="Output directory for transparent PNGs.")
    parser.add_argument("--threshold", type=int, default=30, help="Black threshold for background removal.")
    parser.add_argument("--size", type=int, default=2048, help="Target square canvas size (default 2048).")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in input_dir.iterdir() if f.suffix.lower() in extensions]
    
    print(f"Found {len(files)} files in {input_dir}")
    
    success_count = 0
    for file_path in files:
        output_path = output_dir / f"{file_path.stem}.png"
        if process_ship_image(file_path, output_path, args.threshold, args.size):
            success_count += 1
            
    print(f"\nDone! Processed {success_count} / {len(files)} images.")
    print(f"Results saved to: {output_dir}")

if __name__ == "__main__":
    main()
