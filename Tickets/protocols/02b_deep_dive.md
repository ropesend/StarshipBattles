# PROTOCOL 02b: Deep Dive Analysis
**Role:** Lead Analyst (Investigation & Scope Specialist)

## Configuration

This protocol is parameterized by ticket type. The calling skill sets these values:

| Variable | Bug | Feature |
|----------|-----|---------|
| TYPE | Bug | Feature |
| PREFIX | BUG | FEAT |
| ACTIVE_DIR | Debugging/active_bugs | Features/active_features |
| ARCHIVE_DIR | Debugging/archived_tickets | Features/archived_features |
| DASHBOARD | Debugging/debug_plan.md | Features/feature_plan.md |
| INDEX | Debugging/solved_bugs.md | Features/completed_features.md |

---

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a {TYPE} as [Solved]/[Completed]. You do NOT have the authority to move files to `{ARCHIVE_DIR}/`.

- **Bug:** Your authority ends at [Awaiting Confirmation] or [Needs Human Debug].
- **Feature:** Your authority ends at [Awaiting Confirmation] or [Needs Project].

**Trigger:** Manual -- user explicitly requests deep dive for a specific {PREFIX}-ID.

---

This protocol has TWO distinct workflows depending on ticket type. Follow the section that matches your ticket type.

---
---

## Bug Deep Dive: Root Cause Investigation

**Purpose:** Thorough investigation for persistent bugs that have resisted 2+ standard fix attempts.

**Also useful for:** Bugs in `[Needs Clarification]` status where user has answered the posted questions -- a deep dive may be appropriate to resolve remaining uncertainties before attempting a standard fix.

### Phase 0: Documentation Context (MANDATORY)

Before launching the investigation, read the relevant `docs/` files for the affected code area:
- `docs/01_ARCHITECTURE.md` -- Layer structure and dependency rules
- `docs/02_PATTERNS.md` -- Established design patterns
- `docs/03_CONVENTIONS.md` -- Naming and coding conventions
- Any relevant `docs/systems/` doc for the affected system

The `docs/` directory is the authoritative source for architecture and patterns. Understanding the documented design intent is critical for root-cause analysis -- the bug may be caused by code that violates documented patterns.

**Documentation discrepancy check:** Compare the affected code against what `docs/` describes. If the code contradicts documented patterns or conventions, this discrepancy may itself be the root cause or a contributing factor. Note all discrepancies for investigation. Use the context-dependent truth rules from Protocol 02: check git dates to determine whether docs or code are more recent. If unclear, escalate to user via `## Questions for User`.

### Phase 1: Agent Swarm Exploration

Launch **4 Explore agents in parallel** to investigate the bug from multiple angles:

| Agent | Focus | Task |
|-------|-------|------|
| 1 | **Code Path Tracing** | Trace execution from entry point to bug location. Document the complete call chain. |
| 2 | **Caller/Callee Analysis** | Find ALL functions that call or are called by the affected code. Map dependencies. |
| 3 | **Pattern Search** | Search for similar code patterns elsewhere in the codebase that work correctly. Also compare the affected code against `docs/02_PATTERNS.md` -- does it follow the documented pattern? Identify what's different. |
| 4 | **Git History & Docs** | Review recent commits to affected files. Find when behavior changed. Check for related bug fixes. **Also check `git log` on relevant `docs/` files** -- was the documentation updated after the code? Flag any discrepancies between documented and actual patterns. |

**Output:** Append findings to ticket in new `## Investigation Report` section:
```markdown
## Investigation Report

### Code Path Trace
[Entry point] -> [Step 1] -> [Step 2] -> ... -> [Bug location]

### Dependency Map
**Callers:** [list of functions that call affected code]
**Callees:** [list of functions called by affected code]

### Similar Patterns Found
[File:line] - [Description of similar working code]

### Git History Analysis
**Last working commit:** [hash/date if known]
**Suspect commits:** [list of changes that might have introduced bug]

### Documentation Discrepancies
**Code vs docs mismatches:** [list any cases where code doesn't follow documented patterns, or "None -- code matches docs"]
**Docs last updated:** [date of last commit to relevant docs/ file]
**Code last updated:** [date of last commit to affected code file]
```

### Phase 2: User Interview (Interactive)

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

### Phase 3: Diagnostic Logging

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

### Phase 4: Hypothesis Development

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

### Phase 5: Resolution or Escalation

**If Root Cause Found:**
1. Mark the winning hypothesis as CONFIRMED
2. Proceed with TDD fix:
   - Create/update failing test
   - Implement fix (following patterns in `docs/02_PATTERNS.md` and conventions in `docs/03_CONVENTIONS.md`)
   - Run regression tests
3. Document fix in `## Work Log`
4. **Documentation sync (MANDATORY):**
   - If the fix changed architecture, patterns, or conventions -- update the relevant `docs/` file
   - If the root cause was a code-docs discrepancy -- update whichever was wrong (use git dates to determine; if unclear, ask user)
   - If the root cause involved an undocumented pattern -- add it to the relevant `docs/` file
   - List all `docs/` files updated in the Work Log
5. Set status to `[Awaiting Confirmation]`
6. **STOP** -- wait for user verification

**If Root Cause NOT Found:**
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

**Documentation Discrepancies Found:**
- [list any code-vs-docs mismatches discovered, or "None"]

**Conclusion:** Unable to determine root cause with available information.

**Remaining Unknowns:**
- [What we still don't understand]
- [Missing information that would help]

**Recommended Next Steps:**
- [Suggestion 1 for human debugging]
- [Suggestion 2]
```

2. Set status to `[Needs Human Debug]`
3. **STOP** -- escalate to user for manual investigation

### Bug Deep Dive Status Values

This protocol uses these statuses in `{DASHBOARD}`:
- `[Deep Investigation]` -- Bug is undergoing thorough investigation
- `[Awaiting Confirmation]` -- Fix applied, waiting for user verification
- `[Needs Clarification]` -- Ambiguous fix, questions posted in ticket awaiting user answers
- `[Needs Human Debug]` -- Investigation exhausted, requires human intervention

---
---

## Feature Deep Dive: Scope Assessment

**Purpose:** Thorough analysis of a feature that has turned out to be more complex than expected, or has been rejected 2+ times. Determine whether it can be implemented within the feature track or should be escalated to a formal Project.

### Phase 0: Documentation Context (MANDATORY)

Before launching the investigation, read the relevant `docs/` files for the area where the feature would be implemented:
- `docs/01_ARCHITECTURE.md` — Layer structure and dependency rules
- `docs/02_PATTERNS.md` — Established design patterns
- `docs/03_CONVENTIONS.md` — Naming and coding conventions
- Any relevant `docs/systems/` doc for the affected system

The `docs/` directory is the authoritative source for architecture and patterns. The feature implementation must follow documented patterns. If existing code in the target area contradicts the docs, note the discrepancy — it may affect the implementation strategy or explain why previous attempts failed.

### Phase 1: Agent Swarm Exploration

Launch **4 Explore agents IN PARALLEL**, each focused on a different dimension:

**Agent 1 -- Architecture Impact Analysis:**
* Trace which systems/layers would be affected by this feature.
* Map the module boundaries (core, simulation, strategy, ui, ai).
* Identify cross-layer dependencies that the feature would introduce.
* Output: List of affected systems and their relationships.

**Agent 2 -- Dependency Mapping:**
* Find all code that depends on the systems identified by the feature scope.
* Assess blast radius: how many files/tests would need changes.
* Identify potential regression risks.
* Output: Dependency graph and blast radius estimate.

**Agent 3 -- Similar Pattern Search & Docs Check:**
* Look for similar features/patterns already implemented in the codebase.
* **Compare the target area against `docs/02_PATTERNS.md`** — does the existing code follow documented patterns? Would the feature need to follow or extend a documented pattern?
* Identify reusable abstractions, utilities, or patterns.
* Note any prior attempts that succeeded or failed.
* **Flag any discrepancies** between documented patterns and actual code in the target area.
* Output: Reusable code references, pattern recommendations, and any docs discrepancies found.

**Agent 4 -- Scope Assessment & Architecture Alignment:**
* Review the feature request against the codebase architecture.
* **Verify the proposed feature respects layer boundaries in `docs/01_ARCHITECTURE.md`** and follows conventions in `docs/03_CONVENTIONS.md`.
* Determine if this is truly a "feature" (small, isolated change) or a "project" (multi-phase, cross-cutting refactor).
* Compare to the definition: features are minor additions/changes that don't need a full project.
* Output: Feature vs Project recommendation with justification, and any architectural concerns.

**After all agents complete:**
* Append findings to the ticket as `## Analysis Report` with subsections:
  - Architecture Impact
  - Dependency Map
  - Similar Patterns Found
  - Scope Assessment

### Phase 2: User Interview (Interactive)

Use AskUserQuestion to gather detailed requirements context:

1. "Can you describe the exact expected behavior for this feature?"
2. "Are there any edge cases or special scenarios this should handle?"
3. "What priority is this relative to other pending features?"
4. "Is this feature purely additive, or does it change existing behavior?"
5. "Are there any UI/UX requirements or mockups?"
6. "Would you accept a simplified version of this feature as a first iteration?"

**After gathering answers:**
* Append to ticket as `## Requirements Context` section.

### Phase 3: Complexity Assessment

Perform a structured complexity evaluation:

* **Lines of Code Affected:** Estimate new + modified LOC.
* **Files Requiring Changes:** Count and list.
* **New Abstractions Needed:** Any new classes, patterns, or utilities required?
* **Test Infrastructure:** Does existing test coverage support this area, or does new infrastructure need to be built?
* **Cross-Layer Changes:** Does this touch multiple architectural layers?

**Assign Complexity Rating:**

| Rating | Criteria |
| :--- | :--- |
| Simple | 1-3 files, single layer, existing patterns, <100 LOC |
| Moderate | 4-8 files, 1-2 layers, minor new abstractions, 100-300 LOC |
| Complex | 9+ files, 2-3 layers, new patterns needed, 300+ LOC |
| Project-Scale | Multiple layers, new architecture needed, significant test infrastructure, 500+ LOC |

**Append to ticket as `## Complexity Assessment` section.**

### Phase 4: Implementation Strategy

Based on the complexity rating:

**If Simple or Moderate:**
* Write a detailed implementation plan with:
  - Ordered file modification list
  - Test strategy (which tests to write first)
  - Reusable code identified in Phase 1
* Append to ticket as `## Implementation Strategy`.

**If Complex:**
* Break into smaller sub-tasks, each independently testable.
* Number sub-tasks in implementation order.
* Identify which sub-tasks could be separate feature tickets.
* Append to ticket as `## Implementation Strategy`.

**If Project-Scale:**
* Draft a Project Proposal:
```markdown
## Project Proposal [YYYY-MM-DD HH:MM]
**Feature:** [FEAT-ID]
**Reason:** Feature exceeds "small change" scope
**Estimated Systems Affected:** [count]
**Files Requiring Changes:** [list]
**Suggested Project Phases:** [numbered list]
**Recommendation:** Create Project in Projects/active_projects/
```
* Append to ticket as `## Implementation Strategy`.

### Phase 5: Resolution or Escalation

**If implementable (Simple, Moderate, or Complex):**
1. Proceed with TDD implementation (Phase 2-4 of Protocol 02).
2. **Documentation sync:** If the implementation introduced a new pattern, convention, or architectural element — update the relevant `docs/` file. If a code-docs discrepancy was found and resolved — update whichever was wrong. List all `docs/` files updated in the Work Log.
3. Update `{DASHBOARD}`: Set status to `[Awaiting Confirmation]`.
4. **STOP.** Inform the user: "Feature analyzed and implemented. Status set to Awaiting Confirmation. Please verify."

**If Project-Scale:**
1. Update `{DASHBOARD}`: Set status to `[Needs Project]`.
2. **STOP.** Inform the user: "Feature exceeds the scope of the feature track. A Project Proposal has been added to the ticket. Recommend creating a formal Project in Projects/active_projects/."

### Feature Deep Dive Status Values

This protocol uses these statuses in `{DASHBOARD}`:
- `[Deep Analysis]` -- Feature is undergoing thorough scope assessment
- `[Awaiting Confirmation]` -- Feature implemented, waiting for user verification
- `[Needs Project]` -- Feature exceeds feature track scope, needs formal Project
