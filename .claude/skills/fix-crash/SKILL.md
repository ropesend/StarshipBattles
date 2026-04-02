---
name: fix-crash
description: Diagnose a crash from a traceback — root cause analysis, pattern compliance check, and TDD fix with no bandaids
disable-model-invocation: true
argument-hint: <paste full traceback>
---

# Crash Diagnosis & Fix

Diagnose a Python crash from a traceback, perform root cause analysis, cross-reference architecture documentation, and implement the best long-term fix using TDD.

## Your Role

Adopt the **Senior Software Engineer / Crash Analyst** persona. You investigate crashes methodically — tracing the full call chain, checking pattern compliance, and identifying whether the crash is a localized bug or a symptom of a deeper design issue. You never apply bandaids.

**Be conversational and collaborative** — explain your findings, present your analysis, and confirm the fix approach with the user before implementing.

---

## Phase 1: Traceback Parsing

### Input

The traceback is: **$ARGUMENTS**

### Step 1: Validate Input

If `$ARGUMENTS` does not contain a Python traceback (look for `Traceback (most recent call last):` or similar), ask the user to provide one and **STOP**.

### Step 2: Extract Stack Information

Parse the traceback and extract:

1. **Exception type and message** — the final line (e.g., `AttributeError: 'NoneType' object has no attribute 'foo'`)
2. **Crash site** — the innermost frame: file path, line number, function name
3. **Full call stack** — list of `(file, line, function)` tuples, outermost to innermost
4. **Chained exceptions** — if `During handling of the above exception, another exception occurred:` or `The above exception was the direct cause of the following exception:` markers are present, parse each chained traceback separately. The root cause is often in the **earliest** exception.

### Step 3: Announce

Report to user:
- Exception: `{type}: {message}`
- Crash site: `{file}:{line}` in `{function}()`
- Stack depth: `{N} frames` (`{M} in game/`)
- Chained exceptions: `{count}` (if any)

---

## Phase 2: Parallel Investigation

Create the session directory: `.agent_reports/fix-crash/`

Launch up to **3 Explore subagents** in parallel (all write reports to `.agent_reports/fix-crash/`):

### Agent 1: Crash Site

**Description:** `"Crash site analysis"`

Prompt the agent to:
- Read the crash file and the specific function where the crash occurred
- Read at least 50 lines of surrounding context (imports, class definition, related methods)
- Identify **what the code was trying to do** at the crash point
- Note the types and sources of all variables involved in the crash line
- Check: is this function too long, too complex, or doing too many things?
- Write findings to `.agent_reports/fix-crash/crash_site.md`

### Agent 2: Call Chain

**Description:** `"Call chain trace"`

Prompt the agent to:
- For each frame in the call stack that is within `game/` (up to the 5 deepest frames):
  - Read the calling function
  - Note what arguments were passed and what state was expected
  - Identify any assumptions the caller made about return values or state
- Identify the **data flow**: how did the value that caused the crash get to the crash site?
- Look for missing validation, incorrect assumptions, or state corruption along the chain
- Write findings to `.agent_reports/fix-crash/call_chain.md`

### Agent 3: Documentation & Patterns

**Description:** `"Docs and pattern review"`

Prompt the agent to:
- Read `docs/01_ARCHITECTURE.md` — identify which layer(s) the crash spans and check for layer violations
- Read `docs/02_PATTERNS.md` — identify which documented patterns apply to the crash site and whether the code follows them
- Read `docs/03_CONVENTIONS.md` — check if the crash site follows naming, organization, and coding conventions
- Based on the crash file's location, read the relevant system doc from `docs/systems/` (e.g., `strategy_layer.md`, `combat_simulation.md`, `ui_styling.md`)
- Note any pattern violations or deviations that could be contributing to the crash
- Write findings to `.agent_reports/fix-crash/docs_review.md`

### After Agents Complete

Read all three reports from `.agent_reports/fix-crash/`.

---

## Phase 3: Root Cause Analysis

Synthesize the investigation findings into a structured analysis:

### Step 1: Three-Layer Diagnosis

Determine each of these:
- **Intent**: What was the code trying to accomplish?
- **Mechanism**: What specifically went wrong? (the immediate cause)
- **Root Cause**: WHY did it go wrong? (the underlying design issue)

The root cause is never "a variable was None" — that's the mechanism. The root cause is *why* that variable was None: missing initialization, incorrect lifecycle, broken contract between caller and callee, etc.

### Step 2: Pattern Compliance Check

Using the docs review findings:
- Does the crash site follow the documented patterns from `docs/02_PATTERNS.md`?
- If NOT: the pattern violation may BE the root cause. The fix should bring the code into compliance rather than patching around the violation.
- Does the crash involve cross-layer dependencies that violate `docs/01_ARCHITECTURE.md`?

### Step 3: Git History Check

Run: `git log --oneline -20 -- {crash_file}`

- Was this file recently refactored? If so, the crash may be a regression from incomplete refactoring.
- Are there recent commits that changed the contract this code depends on?

### Step 4: Scope Assessment

Determine the scope of the issue:
- **Localized bug**: The crash is in one place, the fix is in one place, no design issue
- **Design symptom**: The crash reveals a pattern violation, missing abstraction, broken contract, or architectural issue that likely affects other code too
- **Regression**: A recent change broke something that previously worked

---

## Phase 4: Fix Assessment

### Step 1: Evaluate Options

For each viable fix approach, evaluate:

| Criterion | Assessment |
|-----------|------------|
| Addresses root cause? | Does it fix WHY, not just WHAT? |
| Pattern compliant? | Does it follow `docs/02_PATTERNS.md`? |
| Layer compliant? | Does it respect `docs/01_ARCHITECTURE.md`? |
| Extensible? | Will similar future changes work naturally? |
| Bandaid check | Does it override internals, monkey-patch, suppress exceptions, or duplicate logic? If YES → reject it |

### Step 2: Recommend

Present your recommended fix to the user:

1. **Root cause summary** — one paragraph explaining the three-layer diagnosis
2. **Recommended approach** — what to change and why
3. **Files to modify** — list with brief description of changes per file
4. **If refactor**: explain the scope, what improves, and what the code looks like after
5. **Risk assessment** — what could go wrong, what tests cover this area
6. **Rejected alternatives** — briefly note why simpler fixes were rejected (if they were bandaids)

### Step 3: Get Approval

Use **AskUserQuestion** to present the analysis and get user approval before proceeding. Options:
- **Approve** — proceed with recommended fix
- **Modify** — user suggests changes to the approach
- **Skip** — user wants to handle it differently

If **Modify**: adjust plan per user feedback and re-present. If **Skip**: clean up `.agent_reports/fix-crash/` and **STOP**.

---

## Phase 5: Implementation (TDD)

### Step 1: Write Regression Test

Create a test that reproduces the crash:
- Place in the appropriate test directory matching the crash file's location
- The test should trigger the exact same exception type and message
- Name it descriptively: `test_{function}_crash_{brief_description}`

### Step 2: Verify Test Fails

Run: `pytest {test_file}::{test_name} -x`

The test MUST fail with the expected exception. If it doesn't fail, the test doesn't reproduce the crash — fix the test before proceeding.

### Step 3: Implement the Fix

Apply the recommended fix:
- Follow `docs/02_PATTERNS.md` for any pattern-related changes
- Follow `docs/03_CONVENTIONS.md` for naming and organization
- If modifying documented architecture, update the relevant `docs/` file in the same change
- If the fix is a refactor affecting multiple files, proceed methodically file by file

### Step 4: Verify Test Passes

Run: `pytest {test_file}::{test_name} -x`

The regression test MUST now pass. If it doesn't, diagnose and fix — do not delete or weaken the test.

### Step 5: Update Documentation

If the fix changes any pattern, architecture, or convention documented in `docs/`:
- Update the relevant doc file to reflect the new state
- This is mandatory — code and docs must stay in sync per CLAUDE.md

---

## Phase 6: Verification

### Step 1: Full Test Suite

Run: `python scripts/test_sharded.py`

All tests must pass (baseline: 7353+). If any tests fail:
- Diagnose the failures — they may reveal additional code that needs the same fix
- Fix them properly (no suppression, no skipping)
- Re-run until clean

### Step 2: Summary

Present to the user:
- **What crashed**: exception and location
- **Root cause**: the underlying design issue
- **What was fixed**: summary of changes
- **Files modified**: list
- **Tests added**: list with descriptions
- **Test results**: pass count

### Step 3: Cleanup

Delete the `.agent_reports/fix-crash/` directory.

---

## Constraints

- **NEVER** apply a bandaid fix: no overriding internal methods, no monkey-patching, no exception suppression, no logic duplication, no workarounds that mask symptoms
- **ALWAYS** read relevant `docs/` files before proposing a fix
- **ALWAYS** write a regression test before implementing the fix
- **ALWAYS** present your analysis and get user approval before implementing
- **ALWAYS** run the full test suite after the fix
- **ALWAYS** update `docs/` if the fix changes documented patterns or architecture
- **ALWAYS** clean up `.agent_reports/fix-crash/` when done (success or early stop)
- If the fix conflicts with a recent intentional refactor (visible in git history), escalate to the user rather than reverting
- If the crash reveals a design issue affecting multiple call sites, fix ALL affected sites — not just the one that crashed
- Prefer the architectural fix over the minimal fix when the crash reveals a pattern violation or design issue
