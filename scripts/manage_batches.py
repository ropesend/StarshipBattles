import os
import argparse

# Configuration
INSPIRATION_DIR = r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\inspiration"
OUTPUT_DIR = r"C:\Developer\StarshipBattles\assets\Images\Stellar Objects\Planets\Inspiration_Batch_02"
LOG_FILE = os.path.join(INSPIRATION_DIR, "processed_generation_log.txt")

def get_all_candidates():
    # Return all png files, sorted, no size filter as per new request
    return sorted([f for f in os.listdir(INSPIRATION_DIR) if f.endswith('.png')])

def load_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, 'r') as f:
        return set(line.strip() for line in f if line.strip())

def update_log():
    """Scans the OUTPUT directory to see what has been finished and updates the log."""
    # We look at the actual output folder to confirm generation + processing is done
    if not os.path.exists(OUTPUT_DIR):
        print("Output directory does not exist yet.")
        return

    processed_files = set()
    generated = os.listdir(OUTPUT_DIR)
    
    candidates = get_all_candidates()
    current_log = load_log()
    
    new_entries = 0
    
    for c in candidates:
        base = c.rsplit('.', 1)[0]
        # Our naming convention: inspired_BASE_TIMESTAMP.png
        # Check if any file in output starts with inspired_BASE
        if any(g.startswith(f"inspired_{base}") for g in generated):
            processed_files.add(c)
    
    # Write updated log
    with open(LOG_FILE, 'w') as f:
        for p in sorted(list(processed_files)):
            f.write(f"{p}\n")
            
    print(f"Log updated. Total processed: {len(processed_files)}")

def get_next_batch(batch_size=50):
    candidates = get_all_candidates()
    processed = load_log()
    
    remaining = [c for c in candidates if c not in processed]
    
    print(f"Total Candidates: {len(candidates)}")
    print(f"Processed: {len(processed)}")
    print(f"Remaining: {len(remaining)}")
    
    batch = remaining[:batch_size]
    print(f"Next Batch ({len(batch)}):")
    print(batch)
    return batch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=["update", "next"], required=True, help="Action to perform")
    parser.add_argument("--size", type=int, default=50, help="Batch size for 'next'")
    args = parser.parse_args()
    
    if args.action == "update":
        update_log()
    elif args.action == "next":
        get_next_batch(args.size)
