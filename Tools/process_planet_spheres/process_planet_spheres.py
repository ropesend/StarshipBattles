import cv2
import numpy as np
import os
from pathlib import Path
import argparse
import time

def process_planet_image(input_path, output_path, padding=2):
    """
    Detects the circular bound of a planet (including the shaded side)
    and applies a transparency mask. Optimized with downscaled detection.
    """
    # Load image
    img = cv2.imread(str(input_path))
    if img is None:
        print(f"Error: Could not read {input_path}")
        return False

    h, w = img.shape[:2]
    
    # 1. Downscale for detection
    detect_size = 512
    scale = h / detect_size
    small = cv2.resize(img, (detect_size, detect_size), interpolation=cv2.INTER_AREA)
    gray_small = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    
    # Threshold for fallback
    _, thresh = cv2.threshold(gray_small, 2, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Detection logic
    cx, cy, r = None, None, None

    # Try Hough on small image
    blurred = cv2.medianBlur(gray_small, 5)
    min_r = int(detect_size * 0.1)
    max_r = int(detect_size * 0.6)
    
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=detect_size//4,
                               param1=50, param2=30, minRadius=min_r, maxRadius=max_r)

    if circles is not None:
        circles = circles[0, :]
        img_center = np.array([detect_size/2, detect_size/2])
        best_circle = min(circles, key=lambda c: np.linalg.norm(c[:2] - img_center))
        cx_s, cy_s, r_s = best_circle
        
        # Scale back up
        cx, cy, r = int(cx_s * scale), int(cy_s * scale), int(r_s * scale)
        # print(f"  Detected (Hough): Center=({cx}, {cy}), Radius={r}")
    elif contours:
        # Fallback: minEnclosingCircle on small image
        cnt = max(contours, key=cv2.contourArea)
        (cx_fs, cy_fs), r_fs = cv2.minEnclosingCircle(cnt)
        cx, cy, r = int(cx_fs * scale), int(cy_fs * scale), int(r_fs * scale)
        # print(f"  Warning: HoughCircles failed, using enclosing circle. Center=({cx}, {cy}), Radius={r}")
    else:
        print(f"No planet detected in {input_path}")
        return False

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
    parser = argparse.ArgumentParser(description="Process planet images with sphere-preservation mask (Optimized).")
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
    
    start_time = time.time()
    success_count = 0
    for i, f in enumerate(files):
        out_f = output_dir / f"{f.stem}.png"
        if process_planet_image(f, out_f):
            success_count += 1
        
        if (i + 1) % 10 == 0:
            elapsed = time.time() - start_time
            avg = elapsed / (i + 1)
            eta = avg * (len(files) - (i + 1))
            print(f"[{i+1}/{len(files)}] Processed... Avg: {avg:.2f}s, ETA: {eta/60:.1f}m")
            
    print(f"Done! Successfully processed {success_count} images in {time.time() - start_time:.1f}s.")

if __name__ == "__main__":
    main()
