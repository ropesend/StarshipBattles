---
name: debug-triage-qa
description: Interactively parse a QA Session Log to extract and categorize bugs and standalone projects
---

# Triage QA Session Log

**Context:** The user has just finished playing the game using the `qa_launcher.py`. Their spoken voice notes and screenshots were compiled into a Markdown file. 

Adopt the **QA Coordinator** persona. Your job is to translate disorganized spoken feedback into clean, distinct, actionable tasks, and then route them to the appropriate system.

## Execution

### Phase 1: Locate and Read
1. Look in the `tools/qa_observer/session_data/` directory. Find the most recently created subfolder.
2. Read the `QA_Session_Log.md` file located inside that folder using the `view_file` tool.
   - *Note: If the user provides a specific path or session ID in their request, use that instead.*

### Phase 2: Extraction and Classification
1. **Analyze** the log chronologically. Identify distinct issues or ideas being discussed.
2. **Translate** colloquial spoken feedback (e.g., "Ugh the laser just fired backwards why is it doing that") into professional, concise technical summaries (e.g., "Laser projectile trajectory reversed during intense combat").
3. **Categorize** each distinct item as a **Bug**, **Feature**, or **Project**.
   - **Bug**: An existing feature, mechanic, or UI element that is visibly broken, throwing an error, or not behaving according to its established design.
   - **Feature**: Minor changes, QoL improvements, UI tweaks, or small additions that do not significantly alter the game architecture.
   - **Project**: A significant new subsystem, major refactor, or substantial structural change to the game loop.
4. Link the included `![Screenshot]` links correctly to each categorized issue based on the `[HH:MM:SS]` timestamps. 

### Phase 3: Interactive Verification
1. Create a formatted summary of your findings and save it as a Markdown file named `QA_Triage_Summary.md` in the same `tools/qa_observer/session_data/<session_id>/` directory as the original log. 
   - Use a numbered list. For each item, clearly display:
     - Your proposed Category (Bug, Feature, or Project)
     - A short generic title
     - Your cleaned-up technical translation of the issue
     - The localized image path of any screenshots associated with that moment, formatted as a clickable embedded image `[![Screenshot](...)](...)`. **Crucially, you must append a specific descriptive comment to each individual image link explaining exactly what that specific screenshot demonstrates (do not just lump them together with the general topic).**
2. Use the `notify_user` tool to request review of the generated file. You MUST provide the absolute path to this `QA_Triage_Summary.md` file in the `PathsToReview` argument.
3. Explicitly ask the user in your message: *"Please review the generated `QA_Triage_Summary.md` file. Do you approve of these classifications? If yes, I will route them to your systems immediately. Should I modify, merge, or remove any?"*
4. **WAIT** for the user's response. The `notify_user` block will pause execution.

### Phase 4: Routing and Handoff
Once the user approves the list, you must natively route the data into their system by invoking their existing Agent Skills. Do not manually write files if a skill exists to do it for you.

1. **For Bugs:**
   Follow the instructions in the `debug-add-bug` skill (`.agent/skills/debug-add-bug/SKILL.md`). You will provide the cleaned-up descriptions and image links as the "raw description" to this skill so it can generate the `BUG-XX.md` tickets.
2. **For Features:**
   Follow the instructions in the `feature-add` skill (`.agent/skills/feature-add/SKILL.md`). Provide the cleaned-up descriptions and image links as the argument or "raw description" to this skill so it can generate the `FEAT-XX.md` tickets.
3. **For Projects:**
   Do NOT use the `/proj-start` skill automatically. Creating a project is a heavy cognitive task that the user handles manually.
   Instead, create a single Markdown file in `Projects/Triage/` (e.g., `Projects/Triage/project_name.md`).
   Write out the cleaned-up requirements and format the `![Screenshot]` links inside this file so the user has all the context ready for when they decide to start the project.

## Constraints
- **Do not** write code to fix bugs or implement features during this workflow. Your job is triage only.
