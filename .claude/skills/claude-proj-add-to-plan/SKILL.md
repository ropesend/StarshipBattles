---
name: claude-proj-add-to-plan
description: Add one or more existing projects to the refactor plan
disable-model-invocation: true
argument-hint: <project-numbers...> (e.g. 57 58)
---

# Add Projects to Refactor Plan

Add existing projects from `Projects/active_projects/` to the master task list in `Projects/refactor_loop/refactor_plan.md`.

**Projects to add:** $ARGUMENTS

Parse the arguments as a space-separated list of project numbers. For each number N, the project ID is **PROJ-N**. Process each project in order.

## For each project, execute these steps:

### Step 1: Validate the project exists

Check that `Projects/active_projects/PROJ-N/plan.md` exists. If not, report "PROJ-N not found in active_projects/" and **skip to the next project**.

### Step 2: Check it's not already in the plan

Read `Projects/refactor_loop/refactor_plan.md` and search for `PROJ-N` in the Master Task List. If it's already present, report "PROJ-N is already in the refactor plan" and **skip to the next project**.

### Step 3: Extract metadata from plan.md

Read `Projects/active_projects/PROJ-N/plan.md` and extract:

1. **Title** — from the first line heading: `# PROJ-N: <Title>` → extract `<Title>`
2. **Phase count** — count the rows in the `## Quick Status` table (exclude the header row and separator row). Each `|` row with a phase name is one phase.
3. **Status** — derive from the Quick Status table:
   - If any phase is "In Progress" or "Complete" → `In Progress`
   - If all phases are "Not Started" → `Ready`
   - If all phases are "Complete" → `Complete`

### Step 4: Generate the entry block

Use this exact template (substitute the extracted values):

```markdown
- [ ] **PROJ-N: <Title>**
  - **Phases:** <count> | **Status:** <status> | **Priority:** Medium
  - **Plan:** [Projects/active_projects/PROJ-N/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-N/plan.md)
  - **Audit:** Not Started | **Cycles:** 0/5
  - **Dependencies:** None

---
```

Default priority is **Medium**. The user can adjust later via `/anti-proj-manage-plan`.

### Step 5: Insert into refactor_plan.md

Append the entry block at the **end of the Master Task List** section — just before the `## Execution Log` section. Ensure the `---` separator is maintained.

## After all projects are processed, report a summary:

- List each project added with its title and phase count
- Note any projects skipped (with reason)
- Remind: "Use `/anti-proj-manage-plan REORDER` to adjust priority or ordering"
