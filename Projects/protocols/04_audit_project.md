# PROTOCOL 04: Audit Project (Skeptical Review)
**Role:** Skeptical Reviewer

**Goal:** Thoroughly verify that all aspects of the plan have been properly and completely implemented. Use investigation agents with different perspectives to verify concerns.

**CRITICAL:** Be genuinely skeptical. Your job is to find problems, not rubber-stamp completion.

---

## REQUIRED: Pre-Audit Validation

**BEFORE STARTING AUDIT, run this script:**
```bash
python Projects/scripts/validate_audit_ready.py PROJ-XX
```

If this returns **FAILED**, do NOT proceed with audit. Instead:
- Report the validation failures to the user
- Return the project to implementation phase to fix issues

Only proceed with audit if validation **PASSED**.

---

## Audit Process Overview

```
1. Comprehensive checklist review of ALL tasks
2. For each concern found → Launch investigation agent
3. Compile findings
4. If issues found → Extend plan with fix phase
5. Repeat until clean OR 3 cycles reached
6. After 3 cycles → Escalate to user
```

---

## Phase 1: Comprehensive Checklist Review

Go through EVERY task and subtask in the plan. For each one:

### Verification Checklist

| Check | Question |
|-------|----------|
| **Completion** | Is every subtask actually checked off? |
| **Tests Exist** | Does the Tests: line point to real, existing tests? |
| **Tests Pass** | Do those tests actually pass when run? |
| **Code Matches Intent** | Does the implementation match what the task described? |
| **No Shortcuts** | Was the full requirement met, not a partial solution? |
| **No Regressions** | Do existing tests still pass? |
| **Notes Present** | Are implementation notes filled in? |

### Document Concerns

For each potential issue found, document it:
```markdown
### Concern: [Brief Title]
**Task:** [Task X.Y]
**Issue:** [What seems wrong]
**Severity:** [Critical/Major/Minor]
**Evidence:** [What you observed]
```

---

## Phase 2: Investigation Agents

For each concern, launch an investigation agent with a **different perspective** than the original check.

### Investigation Perspectives

| If Original Check Was... | Use This Perspective |
|--------------------------|---------------------|
| Tests exist | **Code Review**: Does the code actually implement the tested behavior? |
| Code looks complete | **Test Verification**: Do tests cover edge cases and error paths? |
| Implementation matches description | **Integration Check**: Does it work with the rest of the system? |
| Tests pass | **Quality Review**: Are the tests meaningful or trivial? |

### Investigation Agent Instructions

Launch Explore agents with specific focus:
```
Investigate concern for PROJ-XX Task X.Y:
- Original concern: [What was flagged]
- Your perspective: [Code Review / Test Verification / Integration Check / Quality Review]
- Questions to answer:
  1. Is this actually a problem?
  2. If yes, what exactly is wrong?
  3. What would be needed to fix it?
```

### Evaluating Investigation Results

- **Confirmed Problem:** Add to findings, will need plan extension
- **False Positive:** Note as resolved, explain why it's not an issue
- **Unclear:** Escalate to user for decision

---

## Phase 3: Compile Findings

After all investigations complete, compile the results:

```markdown
## Audit Cycle [N] - [Date]

### Confirmed Issues
| Task | Issue | Severity | Fix Required |
|------|-------|----------|--------------|
| 2.3 | Cache invalidation missing edge case | Major | Add handling for null keys |
| 3.1 | Test doesn't verify error message | Minor | Improve assertion |

### Resolved Concerns (False Positives)
| Task | Original Concern | Resolution |
|------|------------------|------------|
| 2.1 | Thought tests were missing | Tests are in different file, found them |

### Items Requiring User Decision
| Task | Question |
|------|----------|
| 2.4 | Should we handle the legacy format or require migration? |
```

---

## Phase 4: Plan Extension (If Issues Found)

If confirmed issues exist:

1. **Add New Phase to Plan**
   ```markdown
   ### Phase N+1: Audit Fixes (Cycle [N])
   **Objective:** Address issues found in audit cycle [N]

   #### Task N.1: [Fix description] [Simple/Medium]
   **Tests:** [Where to add/modify tests]
   - [ ] [Specific fix subtask]
   - [ ] [Verify fix works]
   **Notes:**
   ```

2. **Update Audit Log**
   ```markdown
   ## Audit Log
   | Cycle | Date | Findings | Resolution |
   |-------|------|----------|------------|
   | 1 | 2026-01-20 | 2 major, 1 minor issues | Added Phase 4 for fixes |
   ```

3. **Return to Implementation**
   - Set `## Current State` to point to the new fix phase
   - Implementation agents will pick up the fixes

---

## Phase 5: Escalation (After 3 Cycles)

If issues persist after 3 audit cycles:

1. **Generate Escalation Report**
   ```markdown
   ## Audit Escalation Report

   **Project:** PROJ-XX
   **Audit Cycles Completed:** 3
   **Status:** Escalating to user

   ### Persistent Issues
   | Issue | Attempts to Fix | Current State |
   |-------|-----------------|---------------|
   | [Issue 1] | 3 | Still failing |

   ### Summary
   [Why these issues are proving difficult]

   ### Recommendation
   [What we think should happen]

   ### Questions for User
   1. [Specific question about how to proceed]
   2. [Decision needed]
   ```

2. **Ask User**
   - Use AskUserQuestion to present options
   - Options might include:
     - Accept current state with known limitations
     - Provide additional guidance for fixes
     - Descope the problematic feature
     - Manual intervention required

---

## Audit Completion

When audit passes with no significant issues:

1. **Update Audit Log**
   ```markdown
   | Cycle | Date | Findings | Resolution |
   |-------|------|----------|------------|
   | [N] | [Date] | No significant issues | PASSED |
   ```

2. **Update Completion Checklist**
   ```markdown
   ## Completion Checklist
   - [x] All tasks checked off
   - [x] All tests passing
   - [x] Regression tests passing
   - [x] Audit passed (no significant issues)
   - [ ] User verified
   ```

3. **Update Current State**
   ```markdown
   ## Current State
   **Last Updated:** [Now]
   **Last Agent Action:** Audit cycle [N] passed with no significant issues
   **Next Action:** User verification required
   **Blockers:** None
   **Context for Next Agent:** Project is audit-complete. User needs to verify and close.
   ```

4. **Report to User**
   ```
   Audit complete for PROJ-XX.
   - [N] audit cycles completed
   - All tasks verified
   - All tests passing
   - Ready for user verification

   Use 'Close Project' prompt after verification to archive.
   ```

---

## Key Principles

1. **Be genuinely skeptical** - Your job is to find problems
2. **Different perspectives** - Investigation agents use different viewpoints
3. **Document everything** - Clear audit trail in Audit Log
4. **Don't get stuck** - Escalate after 3 cycles
5. **Severity matters** - Minor issues might be acceptable, major issues must be fixed
