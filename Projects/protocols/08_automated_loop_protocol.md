# PROTOCOL 08: Automated Loop Execution

**Role:** Autonomous Loop Agent

**Goal:** Execute refactoring work in a stateless loop, integrating seamlessly with the audit system and maintaining long-term code quality.

---

## Overview

This protocol defines how Claude CLI operates in automated loop mode, executing phases from the master plan, triggering audits when projects complete, and handling the full lifecycle from implementation through verification.

---

## Core Principles

1. **Stateless Operation** - Each agent instance is independent
2. **Long-term Focus** - Always choose maintainability over convenience
3. **Quality First** - Never compromise on tests or code quality
4. **Audit Integration** - Automatic verification of all completed work
5. **Clear Handoffs** - Comprehensive context for next agent

---

## Execution Workflow

### Phase 1: Initialization

**On every loop iteration:**

1. **Read Master Plan**
   ```bash
   # File: refactor_plan.md
   ```
   - Check Agent Context for current state
   - Identify current project (or find next incomplete project)
   - Note audit status and cycle count

2. **Load Project Context**
   ```bash
   # File: Projects/active_projects/PROJ-XX/plan.md
   ```
   - Read Current State section
   - Identify current phase or next incomplete phase
   - Check for any blockers

3. **Load Phase Details**
   ```bash
   # File: Projects/active_projects/PROJ-XX/phase_N_checklist.md
   ```
   - Review task list
   - Check completion status
   - Note any implementation notes from previous agents

---

### Phase 2: Work Execution

**Execute ONE of the following per iteration:**

#### Option A: Execute Phase Tasks

If project has incomplete phases:

1. **Follow Protocol 03a** (Continue Working)
   - Execute tasks using strict TDD
   - Write tests before implementation
   - Run `pytest tests/ --testmon` incrementally
   - Update phase checklist as you work
   - Add implementation notes

2. **Verify Completion**
   ```bash
   python Projects/scripts/validate_phase.py PROJ-XX [phase_num]
   ```
   - Only proceed if validation passes
   - Fix any issues before marking complete

3. **Git Commit**
   ```bash
   python Projects/scripts/commit_phase.py . PROJ-XX [phase_num] "[phase_name]" "[test_status]"
   ```
   - Format: `[PROJ-XX] Phase N: <description> - Automated`
   - Include test status in commit body

4. **Update Project Plan**
   - Mark phase complete in plan.md Quick Status table
   - Update Current State section
   - Note files modified and decisions made

5. **Check Project Status**
   ```bash
   python Projects/scripts/check_project_status.py PROJ-XX
   ```
   - If phases remain: Update Agent Context and exit
   - If all complete: Proceed to Option B (Audit)

#### Option B: Execute Audit

If all project phases are complete:

1. **Pre-Audit Commit**
   ```bash
   git add -A
   git commit -m "[PROJ-XX] Pre-audit checkpoint - All phases complete"
   ```

2. **Run Audit** (Follow Protocol 04)
   - Comprehensive checklist review
   - Launch investigation agents for concerns
   - Compile findings
   - Document in project's Audit Log

3. **Process Audit Results**

   **If Audit Passes:**
   - Update refactor_plan.md:
     - Mark project `[x]` complete
     - Update Audit status: "Passed (Cycle N)"
     - Add entry to Execution Log
   - Update Agent Context to point to next project
   - Git commit:
     ```bash
     git commit -m "[PROJ-XX] Audit passed (Cycle N) - Project complete"
     ```
   - Exit (next iteration will start new project)

   **If Audit Fails:**
   - Check audit cycle count in refactor_plan.md
   - If cycles < 5:
     - Add fix phases to project plan.md (Protocol 04, Phase 4)
     - Update refactor_plan.md Audit status: "In Progress (Cycle N)"
     - Update Agent Context to point to fix phases
     - Git commit:
       ```bash
       git commit -m "[PROJ-XX] Audit cycle N - Added fix phases"
       ```
     - Exit (next iteration will execute fixes)
   - If cycles >= 5:
     - Update refactor_plan.md:
       - Mark project `[~]` (complete with issues)
       - Update Audit status: "Failed after 5 cycles"
       - Add detailed note about persistent issues
     - Update Agent Context to point to next project
     - Git commit:
       ```bash
       git commit -m "[PROJ-XX] Audit limit reached - Moving to next project"
       ```
     - Exit (next iteration will start new project)

---

### Phase 3: Context Handoff

**Before exiting, ALWAYS update Agent Context in refactor_plan.md:**

```markdown
## Agent Context

**Last Session:** [Timestamp]
**Last Completed:** [What was just finished]
**Current Status:** [Current state]
**Current Project:** PROJ-XX
**Current Phase:** Phase N of M (or "Audit Cycle N" or "Complete")
**Test Status:** [Test results]
**Active Blockers:** [Any blockers or "None"]

**Handoff Notes:**
- [Specific context for next agent]
- [Files modified in this session]
- [Decisions made]
- [Next specific action to take]
```

---

## Audit Integration Details

### Audit Trigger Conditions

Audit is triggered when:
- All phases in project plan.md are marked complete
- No blockers exist
- All tests passing

### Audit Cycle Management

**Cycle Tracking:**
- Stored in refactor_plan.md: `**Audit:** [Status] | **Cycles:** N/5`
- Incremented after each audit attempt
- Maximum 5 cycles per project

**Cycle States:**
- `Not Started` - No audit run yet
- `In Progress (Cycle N)` - Audit failed, fixes in progress
- `Passed (Cycle N)` - Audit successful
- `Failed after 5 cycles` - Maximum attempts reached

### Fix Phase Naming

When audit finds issues, add phases to project plan:

```markdown
### Phase N+1: Audit Fixes (Cycle M)
**Objective:** Address issues found in audit cycle M
**Status:** Not Started
**Checklist:** [phase_N+1_checklist.md](phase_N+1_checklist.md)
```

---

## Decision Framework

When faced with implementation choices:

### Always Choose Long-term Quality

| Short-term Option | Long-term Option | Choose |
|-------------------|------------------|--------|
| Quick fix | Proper refactor | ✅ Refactor |
| Workaround | Root cause fix | ✅ Root cause |
| TODO comment | Immediate implementation | ✅ Implement |
| Skip test | Write comprehensive test | ✅ Write test |
| Copy-paste | Extract abstraction | ✅ Abstract |
| Magic number | Named constant | ✅ Constant |
| Broad exception | Specific exception | ✅ Specific |

### Maintainability Checklist

Before completing any task:
- [ ] Code is self-documenting with clear names
- [ ] Complex logic has explanatory comments
- [ ] No magic numbers or strings
- [ ] Proper error handling with specific exceptions
- [ ] Comprehensive test coverage
- [ ] No code duplication
- [ ] Follows existing patterns and conventions
- [ ] Type hints where appropriate
- [ ] Docstrings for public APIs

---

## Error Handling

### Test Failures

**If tests fail:**
1. Analyze the failure - is it the test or the code?
2. If test is invalid: Fix or delete test, document why
3. If code is wrong: Fix the code
4. Never proceed with failing tests
5. If stuck: Update Agent Context with analysis and exit

### Context Exhaustion

**If approaching context limit (80%):**
1. Finish current subtask if close to completion
2. Update Agent Context with detailed handoff
3. Mark current task `[/]` (in progress) in checklist
4. Add specific notes about what's incomplete
5. Exit cleanly - next agent will continue

### Blockers

**If blocked on user decision:**
1. Document the blocker in Agent Context
2. Provide analysis and options
3. Update project plan Current State
4. Exit - user will provide guidance

---

## Integration with Existing Protocols

### Protocol 03a (Continue Working)
- Used for phase execution
- Provides TDD workflow
- Defines stopping conditions

### Protocol 04 (Audit Project)
- Used when all phases complete
- Provides audit methodology
- Defines fix phase creation

### Protocol 05 (Close Project)
- NOT used in automated loop
- Projects marked complete but not archived
- User archives manually after reviewing all work

---

## Loop Runner Integration

The bash script `loop_runner.sh` orchestrates the loop:

1. Checks for incomplete projects
2. Runs Claude CLI with this protocol
3. Waits between iterations
4. Continues until all projects complete

**Agent responsibility:**
- Execute work correctly
- Update files properly
- Exit cleanly
- Provide clear handoff

**Loop script responsibility:**
- Restart agent for next iteration
- Monitor completion status
- Handle script-level errors

---

## Quality Standards

### Code Quality

- Follow existing code patterns
- Use type hints consistently
- Add docstrings to new functions/classes
- Keep functions focused and small (<50 lines preferred)
- Avoid deep nesting (max 3 levels)
- Use descriptive variable names

### Test Quality

- Test behavior, not implementation
- Cover happy path and edge cases
- Test error conditions
- Use meaningful test names
- Keep tests independent
- Use fixtures for common setup

### Documentation Quality

- Update docstrings when changing behavior
- Add comments for non-obvious logic
- Document decisions in decisions.md
- Keep README files current
- Update protocol docs if workflow changes

---

## Metrics and Tracking

### Per-Session Metrics

Track in Execution Log:
- Project and action taken
- Test status
- Commit hash
- Any issues encountered

### Per-Project Metrics

Track in project plan.md:
- Phases completed
- Audit cycles used
- Total time/iterations
- Key decisions made

---

## Success Criteria

A successful loop iteration:
- ✅ One phase executed OR one audit cycle completed
- ✅ All tests passing
- ✅ Git commit created
- ✅ Agent Context updated with clear handoff
- ✅ Files properly updated
- ✅ Long-term quality maintained

---

## Key Reminders

1. **Stateless** - Don't assume anything from previous sessions
2. **One thing at a time** - One phase or one audit per iteration
3. **Quality over speed** - Take time to do it right
4. **Test first** - Strict TDD, always
5. **Clear handoffs** - Next agent should know exactly what to do
6. **Long-term thinking** - Minimize tech debt, maximize maintainability
7. **Exit cleanly** - Update everything before exiting
