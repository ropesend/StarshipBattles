---
name: proj-audit
description: Perform a skeptical audit of a completed project to verify quality and correctness
---

# Audit Project

**Protocol:** `Projects/protocols/04_audit_project.md`

Adopt the **Skeptical Reviewer** persona. Find problems, don't just approve.

## Execution

1. **LOAD**: `Projects/active_projects/PROJ-[ID]/plan.md`.

2. **VALIDATE (REQUIRED)**:
   ```bash
   python Projects/scripts/validate_audit_ready.py PROJ-[ID] --run-tests
   ```
   Must pass before proceeding.

3. **In-Depth Review**:
   - Verify every task and subtask matches intent.
   - Check that tests pass and focus on the corrected behavior.
   - Document all concerns in the Audit Log section.

4. **Investigation**:
   Analyze any red flags with extreme scrutiny. Evaluate if they are confirmed problems or false positives.

5. **Decision**:
   - **Issues found**: Extend plan with a fix phase and return to implementation.
   - **Clean**: Mark audit as passed.
   - **Persistent issues**: Escalate to user if 3 audit cycles fail.
