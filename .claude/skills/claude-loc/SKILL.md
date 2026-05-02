---
name: claude-loc
description: Count lines of code across the project with breakdowns by section and file type
disable-model-invocation: true
---

# Lines of Code Report

Count and report lines of code across the Starship Battles project using the `Tools/loc/loc.py` counter.

## Steps

1. **Run the counter script** to get per-section, per-file-type breakdowns:
   ```bash
   python Tools/loc/loc.py --detailed
   ```
   This outputs JSON with the structure:
   ```json
   {
     "production": {
       "game/ui": {"py": [lines, files], "json": [lines, files], "other": [lines, files]},
       ...
     },
     "tests": { ... }
   }
   ```

2. **Build three markdown tables** from the JSON data:

   **Table 1 — Grand Summary:**
   | Category | Python | JSON | Other | Total | Files |
   Sum all production sections into one row, all test sections into another, then a total row.

   **Table 2 — Production Breakdown:**
   One row per production section. Sort by Python LOC descending (largest first). Include a **Total** row. Columns: Section, Python, JSON, Other, Total, Files.

   **Table 3 — Test Breakdown:**
   One row per test section. Sort by Python LOC descending (largest first). Include a **Total** row. Same columns.

3. **Format all numbers with commas** (e.g., 63,244 not 63244). Right-align numeric columns.

4. **Add a footer line** with the test:source ratio (total test Python lines / total production Python lines).

5. **Print all three tables** directly to the console as markdown. Do not save to a file.

## Notes

- The script handles all exclusions (\_\_pycache\_\_, .pyc, test_history.json, output dirs).
- The script counts all file types accurately using Python's file I/O (no wc -l batching issues).
- `python Tools/loc/loc.py` (without --detailed) prints the original simple summary if needed.
