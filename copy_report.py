import os

source = r"c:\Dev\Starship Battles\scan_results.txt"
dest = r"C:\Users\rossr\.gemini\antigravity\brain\c9a6d1e6-f97f-4c7d-b983-5cfc0ea86e7a\duplication_report.md"

os.makedirs(os.path.dirname(dest), exist_ok=True)

with open(source, "r", encoding="utf-8") as f:
    text = f.read()

with open(dest, "w", encoding="utf-8") as f:
    f.write("# Duplication Report\n\n```text\n")
    f.write(text)
    f.write("\n```\n")

print("Report recreated properly.")
