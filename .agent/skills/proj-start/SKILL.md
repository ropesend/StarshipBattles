---
name: proj-start
description: Initialize a new refactoring/addition project with deep code review and planning
---

# Start New Project

**Protocol:** `Projects/protocols/01_initialize_project.md`

Adopt the **Project Architect** persona.

## Phase A: Initial Understanding

1. **Read Request**: Read the user's project description or review findings.
2. **MANDATORY Script**: Create project structure using the helper script:
   ```bash
   python Projects/scripts/create_project.py "Project Title"
   ```
   Do NOT create project files manually.
3. **MANDATORY Baseline**: Run full test suite:
   ```bash
   pytest tests/
   ```
   All tests must pass before proceeding.
4. **Deep Dive**: Perform a comprehensive review of relevant code areas.
5. **Interview**: Ask clarifying questions and make suggestions.

## Phase B: Architectural Analysis (Deep Dive)

Instead of launching subagents, you (as the Architect) will perform a holistic analysis of the codebase, covering:
- **Architecture**: Overall structure, module boundaries, coupling.
- **Dependencies**: Import chains, circular dependencies, ripple effects.
- **Testing**: Impact on existing tests, new tests needed.
- **Patterns**: Existing patterns to follow vs anti-patterns to avoid.
- **Risks**: Edge cases, race conditions, data integrity.

Document these findings in the `design.md` file within the project folder.

## Phase C: Plan Refinement

1. **Synthesize**: Process findings and update the detailed plan in the project directory.
2. **Detailed Phases**: Create a structured plan with specific file paths, tasks, and subtasks.
3. **Approval**: Present the complete plan to the user for approval.

**Note**: If this project originates from a Code Review, use `review_to_project.py` instead.
