import subprocess
import os
import sys

def run_command(command):
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stdout, result.stderr
    return True, result.stdout, result.stderr

def get_all_untracked_and_modified_files():
    # We want a literal list of files, expanding directories
    success, stdout, stderr = run_command(["git", "status", "--porcelain"])
    if not success:
        return []
    
    initial_items = []
    for line in stdout.splitlines():
        if line.startswith("?? ") or line.startswith(" M ") or line.startswith("M "):
            filename = line[3:].strip()
            if filename.startswith('"') and filename.endswith('"'):
                filename = filename[1:-1]
            initial_items.append(filename)
    
    all_files = []
    for item in initial_items:
        if os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for f in files:
                    all_files.append(os.path.join(root, f))
        else:
            all_files.append(item)
    return all_files

def batch_sync(batch_size=50):
    files = get_all_untracked_and_modified_files()
    if not files:
        print("No files to sync.")
        return

    total_files = len(files)
    print(f"Total individual files to sync: {total_files}")

    for i in range(0, total_files, batch_size):
        batch = files[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_files + batch_size - 1) // batch_size
        
        print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} files)")
        
        # Add files
        # We use quotes for filenames in the command call via list form anyway
        add_cmd = ["git", "add"] + batch
        success, stdout, stderr = run_command(add_cmd)
        if not success:
            print(f"Failed to add batch {batch_num}. Error: {stderr}")
            continue
            
        # Commit
        commit_cmd = ["git", "commit", "-m", f"chore: batch sync assets {batch_num}/{total_batches}"]
        success, stdout, stderr = run_command(commit_cmd)
        if not success:
            # If nothing to commit (e.g. files already added in previous batch), just continue
            if "nothing to commit" in stdout or "nothing to commit" in stderr:
                 print(f"Batch {batch_num} has nothing to commit.")
                 continue
            print(f"Failed to commit batch {batch_num}. Error: {stderr}")
            continue
            
        # Push
        push_cmd = ["git", "push", "origin", "main"]
        success, stdout, stderr = run_command(push_cmd)
        if not success:
            print(f"Failed to push batch {batch_num}. Error: {stderr}")
            print("Stopping to avoid large backlog.")
            break
            
    print("\nSync process completed.")

if __name__ == "__main__":
    batch_sync(batch_size=50)
