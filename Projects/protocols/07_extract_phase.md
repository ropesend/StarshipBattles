# PROTOCOL 07: Extract Phase to Project
**Role:** Project Architect

**Goal:** Safely extract a complex phase into its own independent project while maintaining traceability.

---

## When to Extract

Extract a phase when ANY of these conditions apply:

### Complexity Indicators
- Phase has grown beyond 10+ tasks
- Phase has 40+ subtasks total
- Phase objectives have expanded significantly from original scope
- Phase requires fundamentally different expertise

### Timeline/Resource Indicators
- Phase is blocking other project work
- Phase could benefit from parallel development
- Phase timeline exceeds the original project timeline

### Architectural Indicators
- Phase has become a distinct subsystem
- Phase requires independent testing infrastructure
- Phase involves significant architectural decisions

## Agent Judgment

Agents should use their judgment to identify extraction candidates. This is NOT purely threshold-based - context matters:

- A phase with 8 tasks that are all interconnected may not need extraction
- A phase with 5 tasks that has become architecturally distinct may benefit from extraction

**When in doubt:** Ask the user for guidance.

---

## Extraction Workflow

### Step 1: Validation

Run dry-run to preview extraction:
```bash
python Projects/scripts/extract_phase.py PROJ-XX [N] --dry-run
```

Verify:
- Phase exists and is not already extracted or complete
- The preview output looks correct
- User approval (if agent-initiated)

### Step 2: Execute Extraction

```bash
python Projects/scripts/extract_phase.py PROJ-XX [N] --reason "Your reason here"
```

The script will:
1. Create new project with standard directory structure
2. Write `findings/extraction_context.md` with original phase content
3. Update original phase checklist to "Extracted" status
4. Update original `plan.md` Quick Status table
5. Add decisions.md entries to both projects

### Step 3: Initialize New Project

1. Note the new project ID from script output
2. Run **Start Project** prompt for the new project
3. The `findings/extraction_context.md` provides original context
4. Plan the new project fresh - NOT constrained by original phase structure

The original phase is context, not constraint. The new project may:
- Reorganize tasks differently
- Add phases not in the original
- Approach the problem from a different angle

### Step 4: Update Original Project Manifest

If the original project has a `manifest.md` (required for `/proj-parallel`):
1. Regenerate `manifest.md` by scanning all **remaining** (non-extracted) phase checklists
2. Remove files that were ONLY referenced in the extracted phase
3. Keep files that are referenced by both the extracted phase AND other phases

The new sub-project will get its own `manifest.md` during `/proj-start` (Protocol 01, Step 5).

### Step 5: Verify Original Project

Check that the original project was updated:
1. `plan.md` Quick Status shows "Extracted -> PROJ-XX"
2. Phase checklist shows "Status: Extracted"
3. `decisions.md` has the extraction entry
4. `manifest.md` no longer lists files exclusive to the extracted phase

### Step 6: Continue Work

- Original project can continue with other phases
- New project follows normal lifecycle (Start → Continue → Audit → Close)
- Audit of original project will detect when sub-project is archived

---

## Auto-Completion During Audit

When auditing a project with extracted phases (Protocol 04):

### Sub-Project Dependency Check

For each extracted phase:
1. Identify the linked sub-project ID
2. Check if sub-project exists in `archived_projects/`

| Sub-Project Status | Audit Action |
|-------------------|--------------|
| **Archived** | Mark phase as "Extracted (Complete)" |
| **Active** | Note as "pending sub-project completion" |
| **Not Found** | ERROR - escalate to user |

### Updating Extracted Phase Status

If sub-project is archived:
```markdown
**Status:** Extracted (Complete)
```

Add to Audit Log:
```
Phase N auto-completed: sub-project PROJ-XX archived on YYYY-MM-DD
```

---

## Agent-Initiated Extraction

Agents MAY recommend extraction during implementation:

### Process

1. **Observe:** Identify that phase complexity exceeds expectations
2. **Document:** Note observation in Current State:
   ```markdown
   **Context:** Phase N has grown to 15 tasks with 50+ subtasks.
   Recommend extraction to sub-project.
   ```
3. **Ask:** Request user approval:
   ```
   Phase N has become complex:
   - 15 tasks, 50+ subtasks
   - Estimated effort exceeds original scope
   - Blocking other phases

   Recommend extracting to independent project. Proceed?
   ```
4. **Execute:** If approved, run extraction workflow
5. **Document:** If declined, note decision:
   ```markdown
   | Date | Decision | Rationale |
   | 2026-01-28 | Keep Phase N in project | User preference to maintain single project |
   ```

### What NOT to Do

- Do NOT extract without user approval
- Do NOT extract phases that are nearly complete
- Do NOT extract just to meet arbitrary thresholds

---

## Extracted Phase Lifecycle

```
Original Project                    Sub-Project
       |                                 |
   Phase N: Extracted  <--------->  PROJ-XX Created
       |                                 |
   Continue other phases           Start Project prompt
       |                                 |
   Audit checks status  <----------  Implementation
       |                                 |
   (waiting)                         Audit
       |                                 |
   Auto-complete Phase N  <--------  Archive PROJ-XX
       |                                 |
   Complete audit                    DONE
```

---

## Key Principles

1. **Independence:** New project is fully independent - no complex parent-child tracking
2. **Fresh Planning:** New project gets full planning treatment, not just copied tasks
3. **History Preserved:** Original tasks archived in extracted phase for reference
4. **Automatic Completion:** Audit handles auto-completion when sub-project archived
5. **User Control:** Extraction requires user approval when agent-initiated
