---
name: extract-phase
description: Extract a complex phase from a project into its own independent project
---

# Extract Phase

**Protocol:** `Projects/protocols/07_extract_phase.md`

Use this when a project phase becomes too large or needs a separate track.

## Execution

1. **PREVIEW**:
   ```bash
   python Projects/scripts/extract_phase.py PROJ-[ID] [Phase#] --dry-run
   ```
   Check the output for the new project ID and file impact.

2. **EXECUTE**:
   If the preview is correct, run:
   ```bash
   python Projects/scripts/extract_phase.py PROJ-[ID] [Phase#]
   ```
   Optional: `--title "New Title"` or `--reason "Why"`.

3. **START NEW**: Run `start-project` (or equivalent) on the newly created project ID.

4. **VERIFY ORIGINAL**: Ensure the source project's `plan.md` reflects the extraction in the Quick Status and Decisions Log.
