---
name: claude-proj-start
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
   python Tools/test_sharded/test_sharded.py
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

### Phase D: 03c Phase-Aware Execution Setup

Each new project SHOULD opt into 03c phase-aware execution unless the user
explicitly requests legacy 03a flow. To opt in:

1. **Add the marker to `plan.md`:**
   ```markdown
   **Execution Protocol:** 03c-phase-aware-execution
   ```
   Without this marker, `claude-proj-continue` falls through to legacy 03a.

2. **Capture phase dependencies** in each `phase_<n>_checklist.md`:
   ```markdown
   # Phase 3: ...
   **Status:** Not Started
   **Depends on:** phase_1, phase_2
   **Review Mode:** standard       # or `lightweight` for trivial phases
   **Files (planned):** game/foo.py, tests/unit/test_foo.py
   **Objective:** ...
   ```
   Roots use `**Depends on:** none`. Multi-parent phases pause until ALL
   parents are `verified`. Single-parent phases follow `buffer_depth`
   (default 0; child waits for parent verified).

3. **Initialize `phase_state.json`** by running:
   ```bash
   python -c "
   import sys; sys.path.insert(0, 'Projects/scripts')
   from phase_workflow import state
   from pathlib import Path
   p = Path('Projects/active_projects/PROJ-XX/phase_state.json')
   s = state.initial_state('PROJ-XX')
   # Populate phases from the checklists you just authored:
   state.add_phase(s, 'phase_1', depends_on=[], planned_files=[...], review_mode='standard')
   # ...
   state.save_state(p, s)
   "
   ```
   See `Projects/protocols/03c_phase_aware_execution.md` for the full
   protocol. Coordinator owns this file; phase workers must NOT edit it.

4. **Initialize an empty `findings_ledger.md`** in the project directory:
   ```bash
   echo "# PROJ-XX — Findings Ledger\n\n_(Generated from phase_state.json. Do not edit by hand.)_" > Projects/active_projects/PROJ-XX/findings_ledger.md
   ```

5. **Don't create the project branch yet** — `claude-proj-continue` does
   that on first execution. Initial planning artifacts commit to `main`.

**Note:** If this project originates from a Code Review, use `review_to_project.py` instead:
```bash
python Reviews/scripts/review_to_project.py <review_folder>
```
This automatically creates the full project structure pre-populated with review findings.

## Project Description

$ARGUMENTS
