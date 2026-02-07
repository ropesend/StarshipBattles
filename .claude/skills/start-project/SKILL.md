---
name: start-project
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

1. Read the project description provided below
2. **MANDATORY:** Create project structure using the helper script:
   ```bash
   python Projects/scripts/create_project.py "Project Title"
   ```
   Do NOT create project files manually. The script ensures proper directory structure.
3. **MANDATORY:** Run full test suite to establish baseline:
   ```bash
   pytest tests/
   ```
   All tests must pass before proceeding. This also initializes testmon.
4. Perform deep code review of relevant areas
5. Ask clarifying questions
6. Make suggestions based on findings

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
