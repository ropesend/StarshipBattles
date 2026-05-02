---
name: claude-proj-extract-phase
description: Extract a complex phase from a project into its own independent project
disable-model-invocation: true
argument-hint: <project-number> <phase-number>
---

# Extract Phase $1 from PROJ-$0

**Protocol:** `Projects/protocols/07_extract_phase.md`

Read and follow the full protocol file `Projects/protocols/07_extract_phase.md`.

## When to Use

- A phase has grown too complex for single-phase handling
- A phase requires fundamentally different expertise or timeline
- Parallel development would benefit the overall project
- Agent judgment determines the phase scope exceeds expectations

## Execution

### Step 1: Preview the Extraction

Run the extraction script in dry-run mode to preview changes:

```bash
python Projects/scripts/extract_phase.py PROJ-$0 $1 --dry-run
```

Review the preview output:
- New project ID that will be created
- Files that will be modified
- Confirm the extraction is appropriate

### Step 2: Execute Extraction

If the preview looks correct, run the actual extraction:

```bash
python Projects/scripts/extract_phase.py PROJ-$0 $1
```

Optional flags:
- `--title "Custom Title"` - Provide a custom title for the new project
- `--reason "Detailed reason"` - Document the extraction reason

### Step 3: Start Planning the New Project

After extraction:
1. The script outputs the new project ID (e.g., PROJ-55)
2. Run `/anti-proj-start` on the new project
3. The extraction context in `findings/extraction_context.md` provides background
4. Plan the new project fresh - not constrained by original phase structure

### Step 4: Verify Original Project

Confirm the original project was updated correctly:
1. Check `plan.md` Quick Status table shows "Extracted -> PROJ-XX"
2. Check the phase checklist shows "Status: Extracted"
3. Check `decisions.md` has the extraction entry

## What Happens to the Original Phase

- The phase status becomes "Extracted"
- The phase checklist preserves original tasks as "Archived for Reference"
- The phase will auto-complete when the sub-project is archived
- This is detected during the Audit protocol (Protocol 04)
