import cv2
import numpy as np
import os
from pathlib import Path
import argparse

def process_planet_image(input_path, output_path, padding=2):
    """
    Detects the circular bound of a planet (including the shaded side)
    and applies a transparency mask. Full resolution for maximum accuracy.
    """
    # Load image
    img = cv2.imread(str(input_path))
    if img is None:
        print(f"Error: Could not read {input_path}")
        return False

    h, w = img.shape[:2]
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to find lit area (fallback)
    _, thresh = cv2.threshold(gray, 2, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print(f"No planet detected in {input_path}")
        return False
    cnt = max(contours, key=cv2.contourArea)

    # --- High Quality Detection (Full Resolution) ---
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Parameters for HoughCircles (Full Resolution)
    min_r = int(h * 0.1)
    max_r = int(h * 0.6)
    
    # We use a finer dp and more sensitive param2 for high-res detection
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.0, minDist=100,
                               param1=50, param2=30, minRadius=min_r, maxRadius=max_r)

    if circles is not None:
        circles = circles[0, :]
        # Pick the circle closest to the center of the image
        img_center = np.array([w/2, h/2])
        best_circle = min(circles, key=lambda c: np.linalg.norm(c[:2] - img_center))
        
        cx, cy, r = int(best_circle[0]), int(best_circle[1]), int(best_circle[2])
        print(f"  Detected (Hough): Center=({cx}, {cy}), Radius={r} for {input_path.name}")
    else:
        # Fallback: minEnclosingCircle
        (cx_f, cy_f), r_f = cv2.minEnclosingCircle(cnt)
        cx, cy, r = int(cx_f), int(cy_f), int(r_f)
        print(f"  Warning: HoughCircles failed for {input_path.name}, falling back to enclosing circle. Center=({cx}, {cy}), Radius={r}")

    # Create mask at full resolution
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.circle(mask, (cx, cy), r + padding, 255, -1)
    
    # Create RGBA
    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = mask
    
    # Save output
    cv2.imwrite(str(output_path), rgba)
    return True

def main():
    parser = argparse.ArgumentParser(description="Process planet images with sphere-preservation mask (High Quality).")
    parser.add_argument("--input", required=True, help="Input directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--sample", type=int, default=0, help="Process only first N images (0 for all)")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    extensions = ('.png', '.jpg', '.jpeg')
    files = sorted([f for f in input_dir.iterdir() if f.suffix.lower() in extensions])
    
    if args.sample > 0:
        files = files[:args.sample]
        
    print(f"Found {len(files)} files to process in {input_dir}")
    
    success_count = 0
    for f in files:
        out_f = output_dir / f"{f.stem}.png"
        if process_planet_image(f, out_f):
            success_count += 1
        else:
            print(f"Failed: {f.name}")
            
    print(f"Done! Successfully processed {success_count} images.")

if __name__ == "__main__":
    main()
