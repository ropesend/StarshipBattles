import os

ROOT_DIR = r"c:\Dev\Starship Battles"
EXCLUDES = {'.git', '.vscode', '__pycache__', '.pytest_cache', 'assets'} # assets is the new dir, good to skip traversing it if it was big, but replacing content in it is fine if needed.

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"Skipping binary file: {filepath}")
        return

    new_content = content.replace('"assets"', '"assets"')
    new_content = new_content.replace("'assets'", "'assets'")
    new_content = new_content.replace("assets/", "assets/")
    new_content = new_content.replace("assets\\", "assets\\")

    if new_content != content:
        print(f"Updating {filepath}")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def main():
    for root, dirs, files in os.walk(ROOT_DIR):
        # Modify dirs in-place to skip excludes
        dirs[:] = [d for d in dirs if d not in EXCLUDES]
        
        for file in files:
            if file.endswith(('.py', '.md', '.json', '.txt')):
                process_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
