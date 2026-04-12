---
name: debug-sequential
description: Fix multiple bugs sequentially without parallel tracking (e.g., /debug-sequential 85 86 87 or /debug-sequential all)
argument-hint: <bug numbers or "all">
---

# Sequential Bug Resolution

**Protocol:** `Tracking/protocols/02c_parallel_debug.md` (Adapted for sequential)

## Your Role

You are a Senior Software Engineer debugging multiple tickets in a single sequence. You do the research, propose the fix to the user, wait for approval, implement the fix, run tests, and move on to the next item.

## Arguments

Parse `$ARGUMENTS` as either:
- Space-separated bug numbers (e.g., `85 86 87`)
- The word `all` (targets all `[Pending]` and `[In-Progress]` bugs)

## Session Setup

1. **Read** `Tracking/debug_plan.md` to identify target bugs based on `$ARGUMENTS`.
2. **Build your queue**. If any specific bug is not in a valid state, announce that it will be skipped.

## Sequential Execution Loop

For each bug in the queue, execute the following steps ONE AT A TIME:

### Phase 1: Research
1. Read the bug ticket from `Tracking/bugs/active/BUG-{ID}.md`.
2. Analyze the codebase to find the source of the issue.
3. Formulate a hypothesis and identify the files to edit.

### Phase 2: User Approval
1. Present your findings to the user.
2. Clearly state your intended fix plan.
3. Use `ask_question` or pause execution to explicitly request approval before making changes.
4. If the user suggests modifications, adapt your plan. If they skip, move to the next bug.

### Phase 3: Implementation
1. Fix the code following TDD principles (write/update tests if necessary).
2. Run standard local tests to verify your fix.
3. Run the full suite if the change impacts broader systems (`python Tools/test_sharded/test_sharded.py`).

### Phase 4: Ticket Update
1. Once successful, update `Tracking/bugs/active/BUG-{ID}.md` status to `[Awaiting Confirmation]`.
2. Update `Tracking/debug_plan.md` to reflect the new state.
3. Automatically move to the next bug in your queue. (No background workers needed!)

## Constraints
- **NEVER** edit files before securing user approval on your research.
- **ALWAYS** update `debug_plan.md` after successfully finishing a bug.
- Since this runs sequentially in one context, you do not need file conflict matrices or worktree isolations!
