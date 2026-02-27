# PROTOCOL 02b: Deep Dive Investigation
**Role:** Lead Debugger (Investigation Specialist)

**Purpose:** Thorough investigation for persistent bugs that have resisted 2+ standard fix attempts.

**Trigger:** Manual - user explicitly requests deep investigation via prompt.

**Also useful for:** Bugs in `[Needs Clarification]` status where user has answered the posted questions — a deep dive may be appropriate to resolve remaining uncertainties before attempting a standard fix.

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a bug as [Solved]. Your authority ends at [Awaiting Confirmation] or [Needs Human Debug].

---

## Phase 1: Agent Swarm Exploration

Launch **4 Explore agents in parallel** to investigate the bug from multiple angles:

| Agent | Focus | Task |
|-------|-------|------|
| 1 | **Code Path Tracing** | Trace execution from entry point to bug location. Document the complete call chain. |
| 2 | **Caller/Callee Analysis** | Find ALL functions that call or are called by the affected code. Map dependencies. |
| 3 | **Pattern Search** | Search for similar code patterns elsewhere in the codebase that work correctly. Identify what's different. |
| 4 | **Git History** | Review recent commits to affected files. Find when behavior changed. Check for related bug fixes. |

**Output:** Append findings to ticket in new `## Investigation Report` section:
```markdown
## Investigation Report

### Code Path Trace
[Entry point] → [Step 1] → [Step 2] → ... → [Bug location]

### Dependency Map
**Callers:** [list of functions that call affected code]
**Callees:** [list of functions called by affected code]

### Similar Patterns Found
[File:line] - [Description of similar working code]

### Git History Analysis
**Last working commit:** [hash/date if known]
**Suspect commits:** [list of changes that might have introduced bug]
```

---

## Phase 2: User Interview (Interactive)

Use the AskUserQuestion tool to gather context. Ask these questions:

1. **Reproduction Steps:** "Can you describe the exact steps to reproduce this bug, one at a time?"
2. **Expected vs Actual:** "What do you expect to happen, and what actually happens instead?"
3. **History:** "When did this last work correctly? Has it ever worked?"
4. **Consistency:** "Does this fail every time, or only sometimes? Any patterns?"
5. **Context:** "What game state, window, or UI context are you in when the bug occurs?"
6. **Workarounds:** "Have you found any workarounds or conditions where it doesn't fail?"

**Output:** Append to ticket in new `## User Context` section:
```markdown
## User Context

**Reproduction Steps:**
1. [Step 1]
2. [Step 2]
...

**Expected Behavior:** [what should happen]
**Actual Behavior:** [what happens instead]

**History:** [when it last worked / if ever]
**Consistency:** [always fails / intermittent / pattern]
**Game State:** [relevant context]
**Known Workarounds:** [any discovered]
```

---

## Phase 3: Diagnostic Logging

Based on exploration and interview findings, add strategic `log_debug()` statements:

1. **Identify key decision points** in the code path
2. **Add logging at:**
   - Function entry/exit with parameter values
   - Conditional branches (log which path is taken)
   - State values before/after critical operations
   - Event handlers (log when events are received)

3. **Document locations** in new `## Diagnostic Logging` section:
```markdown
## Diagnostic Logging

| File | Line | What is Logged |
|------|------|----------------|
| path/to/file.py | 123 | Function entry with params |
| path/to/file.py | 145 | Branch decision: X vs Y |
...
```

4. **Instruct user:** "Please reproduce the bug and share the relevant log output."

5. **Analyze logs** to find where actual behavior diverges from expected.

**Note:** Logging statements use `log_debug()` and are kept permanently in the codebase.

---

## Phase 4: Hypothesis Development

Maintain a `## Hypothesis Log` section to track theories:

```markdown
## Hypothesis Log

### Hypothesis 1: [Descriptive Title] - [TESTING/CONFIRMED/REJECTED]
**Theory:** [What we think is causing the bug]
**Evidence For:** [Observations supporting this theory]
**Evidence Against:** [Observations contradicting this theory]
**Test:** [How to verify this hypothesis]
**Result:** [Outcome of testing]

### Hypothesis 2: ...
```

For each hypothesis:
1. Document the theory clearly
2. List supporting and contradicting evidence
3. Design a test to verify
4. Execute test and record result
5. Mark as CONFIRMED, REJECTED, or keep TESTING

---

## Phase 5: Resolution or Escalation

### If Root Cause Found:
1. Mark the winning hypothesis as CONFIRMED
2. Proceed with TDD fix:
   - Create/update failing test
   - Implement fix
   - Run regression tests
3. Document fix in `## Work Log`
4. Set status to `[Awaiting Confirmation]`
5. **STOP** - wait for user verification

### If Root Cause NOT Found:
1. Generate comprehensive Debug Report:
```markdown
## Debug Report [YYYY-MM-DD HH:MM]

**Investigation Duration:** [time/effort spent]
**Agents Deployed:** 4 (Code Path, Dependencies, Patterns, Git History)

**Files Examined:**
- [list of files reviewed]

**Hypotheses Tested:** [count]
- [Hypothesis 1] - REJECTED: [reason]
- [Hypothesis 2] - REJECTED: [reason]
...

**Logging Added:** [count] locations
- [summary of logging points]

**Conclusion:** Unable to determine root cause with available information.

**Remaining Unknowns:**
- [What we still don't understand]
- [Missing information that would help]

**Recommended Next Steps:**
- [Suggestion 1 for human debugging]
- [Suggestion 2]
```

2. Set status to `[Needs Human Debug]`
3. **STOP** - escalate to user for manual investigation

---

## Status Values

This protocol uses these statuses in `debug_plan.md`:
- `[Deep Investigation]` - Bug is undergoing thorough investigation
- `[Awaiting Confirmation]` - Fix applied, waiting for user verification
- `[Needs Clarification]` - Ambiguous fix, questions posted in ticket awaiting user answers
- `[Needs Human Debug]` - Investigation exhausted, requires human intervention
