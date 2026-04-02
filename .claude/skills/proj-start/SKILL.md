---
name: proj-start
description: Initialize a new refactoring/addition project with deep code review and planning
disable-model-invocation: true
argument-hint: <project description>
---

# Start New Project

**Protocol:** `Projects/protocols/01_initialize_project.md`

Read and follow the full protocol file `Projects/protocols/01_initialize_project.md`.

## Your Role

Adopt the **Project Architect** persona.

## Execution

### Phase A: Initial Understanding

1. **MANDATORY FIRST STEP:** Read project documentation:
   - `docs/README.md` (documentation index)
   - `docs/01_ARCHITECTURE.md` (layers, APIs, protocols)
   - `docs/02_PATTERNS.md` (established design patterns)
   - `docs/03_CONVENTIONS.md` (naming, coding style)
   - Any task-specific docs from `docs/systems/` or `docs/guides/`
   The `docs/` directory is the authoritative source for architecture and patterns.
   Your plan MUST be consistent with documented patterns and conventions.
2. Read the project description provided below
3. **MANDATORY:** Create project structure using the helper script:
   ```bash
   python Projects/scripts/create_project.py "Project Title"
   ```
   Do NOT create project files manually. The script ensures proper directory structure.
4. **MANDATORY:** Run full test suite to establish baseline:
   ```bash
   python scripts/test_sharded.py
   ```
   All tests must pass before proceeding.
5. Perform deep code review of relevant areas
6. **Cross-reference code against `docs/` — flag any discrepancies to the user**
7. Ask clarifying questions
8. Make suggestions based on findings

### Phase B: Deep Dive Swarm Review

- Launch 6-8 Explore agents with appropriate roles
- Document findings in the `design.md` file

### Phase C: Plan Refinement

- Process swarm findings
- Ask follow-up questions if needed
- Create detailed plan with phases, tasks, subtasks in the phase checklist files
- Get user approval on the plan

**Note:** If this project originates from a Code Review, use `review_to_project.py` instead:
```bash
python Reviews/scripts/review_to_project.py <review_folder>
```
This automatically creates the full project structure pre-populated with review findings.

## Project Description

$ARGUMENTS
