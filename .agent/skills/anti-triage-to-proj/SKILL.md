---
name: anti-triage-to-proj
description: Convert a triage item into a new project
disable-model-invocation: true
argument-hint: <triage_filename>
---

# Convert Triage Item to Project

**Protocol (after file operations):** `Projects/protocols/01_initialize_project.md`

## Your Role

Adopt the **Project Architect** persona. You will first assess the triage item, handle file operations, then follow the standard project initialization protocol.

---

## Phase 0: Triage Intake and File Operations

### Step 1: Locate and Read the Triage File

The triage filename is: **$ARGUMENTS**

1. Strip any `.md` extension from the argument if present.
2. Construct the full path: `Projects/Triage/<filename>.md`
3. **Verify the file exists.** If it does not exist:
   - List all `.md` files in `Projects/Triage/` and report them to the user
   - Say: "Could not find that triage file. The available triage items are listed above."
   - **STOP.** Do not proceed further.
4. Read the triage file contents in full.

### Step 2: Assess the Triage Item

1. Review the triage content: description, screenshots, context, and any notes.
2. **Determine if more context is needed.** Consider:
   - Is the problem or feature clearly described?
   - Is the scope understandable?
   - Are the reproduction steps or acceptance criteria clear?
   - Is there enough information to plan a project?
3. **If gaps exist:** Use AskUserQuestion to ask targeted questions. Incorporate the answers into your understanding.
4. **If the triage item is clear:** Proceed directly.

### Step 3: Determine Project Title

Based on the triage content and any user answers, determine an appropriate project title:
- Keep it concise (3-8 words)
- Describe the work to be done, not the symptom
- Use action-oriented language (e.g., "Fix Star Measurement Radius Logic", "Add Hex Ownership Highlights")

Present the proposed title to the user and confirm before proceeding.

### Step 4: Create the Project

Run the project creation script:
```bash
python Projects/scripts/create_project.py "Your Project Title"
```

Note the PROJ-XX identifier from the script output. Use this project ID for all subsequent steps.

### Step 5: Parse Image References

Extract all image file references from the triage markdown. Look for these patterns:
- Markdown images: `![alt](path)` or `[![alt](path)](path)`
- Any path ending in an image extension (`.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`)

Categorize each referenced image as:
- **Local asset**: Path starts with `./assets/`
- **External path**: Any other relative or absolute path

### Step 6: Copy Images to the New Project

1. Create the findings assets directory:
   ```bash
   mkdir -p Projects/active_projects/PROJ-XX/findings/assets
   ```
   (On Windows use `mkdir` without `-p`; the `findings/` directory already exists from the create script.)

2. **For local asset references** (`./assets/filename.png`):
   - Copy from `Projects/Triage/assets/filename.png` to `Projects/active_projects/PROJ-XX/findings/assets/filename.png`
   - No path rewriting needed (the `./assets/` relative path works from both locations)

3. **For external path references** (e.g., `../../tools/qa_observer/.../filename.png`):
   - Resolve the full path relative to `Projects/Triage/`
   - Copy the image file to `Projects/active_projects/PROJ-XX/findings/assets/filename.png`
   - **If the source file does not exist:** Warn the user and continue. Do NOT fail.
   - The markdown paths will be rewritten in Step 7

### Step 7: Move and Update the Triage Markdown

1. Copy the triage `.md` file to `Projects/active_projects/PROJ-XX/findings/<original_filename>.md`

2. **Rewrite external image paths** in the copied file only:
   - Replace any non-`./assets/` image paths with `./assets/<filename>.png`
   - Do NOT modify local `./assets/` references (they already work correctly)

3. Verify the copied file reads correctly and image paths are consistent.

### Step 8: Clean Up Triage Originals

1. **Delete the original triage `.md` file** from `Projects/Triage/`.

2. **Delete referenced local images** from `Projects/Triage/assets/`, but ONLY if safe:
   - For each `./assets/filename.png` referenced by this triage file:
     - Search ALL remaining `.md` files in `Projects/Triage/` for references to that filename
     - **If no other triage file references the image:** Delete it from `Projects/Triage/assets/`
     - **If another triage file also references the image:** Keep it (it was copied, not moved)
   - Do NOT delete images from external paths. Those belong to other systems.

3. Report what was cleaned up.

### Step 9: Summary

Present a summary to the user:
- Project ID created (PROJ-XX)
- Triage file moved to: `PROJ-XX/findings/<filename>.md`
- Images copied to: `PROJ-XX/findings/assets/`
- Files cleaned from Triage
- Any warnings (missing images, shared images retained, etc.)

---

## Phases A-C: Standard Project Initialization

Now follow the standard project initialization protocol.

**Read and execute** `Projects/protocols/01_initialize_project.md` with these modifications:

- **SKIP** the "Create project structure" step (already done in Step 4 above).
- **Use the triage content** (read in Step 1) as the project description.
- **Include the triage findings file** (`Projects/active_projects/PROJ-XX/findings/<filename>.md`) in the project plan's Key Files table.
- Execute all other steps as written: establish test baseline, deep code review, clarifying questions, swarm review, plan refinement, and user approval.
