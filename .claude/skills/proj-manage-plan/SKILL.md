---
name: proj-manage-plan
description: Add, remove, update, or reorder projects in the master Projects/refactor_loop/refactor_plan.md
disable-model-invocation: true
argument-hint: <ADD|REMOVE|UPDATE|REORDER> <project-number> [details]
---

# Manage Refactor Plan

**Protocol:** `Projects/protocols/10_manage_refactor_plan.md`

Read and follow the full protocol file `Projects/protocols/10_manage_refactor_plan.md`.

## Execution

Manage the projects in `Projects/refactor_loop/refactor_plan.md`.

**Action requested:** $ARGUMENTS

### Available Actions

- **ADD** - Add a new project to the plan. Specify: Project Title, Priority (High/Med/Low)
- **REMOVE** - Remove or archive a project. Specify: Delete / Archive / Skip
- **UPDATE** - Update project details from its source plan
- **REORDER** - Move a project. Specify: target position or "after PROJ-XX"

### Verification

After making changes, verify:
- [ ] Markdown syntax valid
- [ ] File paths valid
- [ ] Separators `---` present between projects
- [ ] No orphan text
- [ ] First empty checkbox is intended next project
- [ ] No project appears above its dependencies
