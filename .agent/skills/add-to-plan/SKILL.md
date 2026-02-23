---
name: add-to-plan
description: Add one or more existing projects to the refactor plan
---

# Add Projects to Refactor Plan

Add existing projects from `Projects/active_projects/` to the master task list in `Projects/refactor_loop/refactor_plan.md`.

## Execution

1. **Parse Input**: Parse the arguments as a space-separated list of project numbers (e.g. 57 58). For each number N, the project ID is **PROJ-N**. Process each project in order.

2. **Validate**: For each project, check that `Projects/active_projects/PROJ-N/plan.md` exists. If not, report and skip.

3. **Check Duplicate**: Search `Projects/refactor_loop/refactor_plan.md` for `PROJ-N`. If present, skip.

4. **Extract Metadata**: From `Projects/active_projects/PROJ-N/plan.md`, extract:
   - **Title**: From `# PROJ-N: <Title>`
   - **Phase Count**: Count rows in `## Quick Status` table.
   - **Status**: 
     - If any phase is "In Progress" or "Complete" -> `In Progress`
     - If all "Not Started" -> `Ready`
     - If all "Complete" -> `Complete`

5. **Generate Entry**: 
   ```markdown
   - [ ] **PROJ-N: <Title>**
     - **Phases:** <count> | **Status:** <status> | **Priority:** Medium
     - **Plan:** [Projects/active_projects/PROJ-N/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-N/plan.md)
     - **Audit:** Not Started | **Cycles:** 0/5
     - **Dependencies:** None

   ---
   ```

6. **Insert**: Append entry to the end of the Master Task List section in `Projects/refactor_loop/refactor_plan.md`.

7. **Report**: Summarize projects added and any skipped.
