---
name: qa-triage
description: Process QA session logs into bugs, features, and prospective projects through interactive triage
disable-model-invocation: true
argument-hint: [session_directory_name] (e.g., 20260314_074413, or omit for latest)
---

# QA Session Triage

Process a QA Observer session log interactively, categorizing each observation as a Bug, Feature, Prospective Project, or acting on existing bug fixes (reject/approve).

## Your Role

Adopt the **QA Analyst / Technical Investigator** persona. You walk through each observation with the user, perform code review to understand context, check for duplicates against existing tickets, and create tickets in the appropriate system.

**Be conversational and collaborative** — explain your findings, ask clarifying questions, and confirm decisions with the user before creating anything.

---

## Phase 1: Session Loading

### Step 1: Locate the Session

The session argument is: **$ARGUMENTS**

1. If the argument is empty or omitted:
   - List directories in `Tools/qa_observer/session_data/`
   - Sort by name (they are `YYYYMMDD_HHMMSS` format)
   - Select the most recent directory that contains a `QA_Session_Log.md`
   - Report which session was auto-selected
2. Otherwise:
   - Strip any path prefix; use just the directory name
   - Construct path: `Tools/qa_observer/session_data/<argument>/QA_Session_Log.md`
   - Verify the file exists. If not, list available sessions and **STOP**.

### Step 2: Read and Parse the Session Log

1. Read the full `QA_Session_Log.md` file.
2. Parse into a list of **observations**. An observation is a logical unit consisting of:
   - One or more timestamped spoken commentary blocks
   - Zero or more screenshot references that appear between or after the commentary
3. **Group by topic:**
   - Consecutive commentary about the same subject forms one observation.
   - A topic change starts a new observation.
4. **Cross-session merging:** Scan the ENTIRE log for observations that return to the same issue later in the session. Users often mention something, move on, then come back to it. Merge all mentions of the same issue into a single observation, preserving:
   - All timestamps from each mention
   - All spoken commentary in chronological order
   - All associated screenshots
   - Note which parts came from separate mentions (e.g., "First mentioned at 07:44, revisited at 07:52")
5. Present the grouped observations to the user for confirmation:
   - Number each observation
   - Show a one-line summary
   - Flag any that were merged from multiple mentions
   - **Ask the user** if the grouping is correct — they may want to split or merge items

### Step 3: Load Dashboards for Duplicate Detection

Read these files and keep them in context:
- `Debugging/debug_plan.md` — all active bug IDs and descriptions
- `Features/feature_plan.md` — all active feature IDs and descriptions

Note the next available IDs (highest existing ID + 1 for each system).

---

## Phase 2: Interactive Observation Review

Process each observation **ONE AT A TIME**, sequentially. For each observation:

### Step A: Present the Observation

Display to the user:
- The timestamp range (or multiple timestamp ranges if merged)
- The full spoken commentary text (all mentions, in chronological order)
- Any associated screenshots — **read the image files** so the user can see them in the conversation
- A brief restatement: "It sounds like you're describing [X]. Is that right?"

### Step B: Code Investigation

Launch Explore agent(s) to understand the relevant code:
- Search for code related to the described behavior
- Identify the specific files, classes, and functions involved
- Determine whether the described behavior matches what the code actually does
- Present findings to the user: "I looked at [file:function] and here is what I found..."

This investigation informs whether it's truly a bug, a feature gap, or something that needs deeper architectural work.

### Step C: Duplicate Check

Compare the observation against existing active tickets:
- Scan bug descriptions in `Debugging/debug_plan.md` for overlap
- Scan feature descriptions in `Features/feature_plan.md` for overlap
- If a potential match is found:
  1. Read the full existing ticket file (e.g., `Debugging/active_bugs/BUG-XX.md`) for detailed context
  2. Present the match: "This may overlap with BUG-XX: [description]"
  3. **If the matching bug has status `[Awaiting Confirmation]`**, use **AskUserQuestion** with these options:
     - **Approve Fix** — the bug is confirmed fixed during this QA session (proceed to Step E: Approve Bug Fix)
     - **Reject Fix** — the bug is NOT fixed, user observed it again (proceed to Step E: Reject Bug Fix)
     - **Add Context** — related observation but not directly about the fix status (append `### 📝 User Update` block)
     - **New Ticket** — distinct issue, proceed to Step D
  4. **For all other matches**, use **AskUserQuestion** with:
     - **Duplicate** — skip this observation entirely (note in session summary)
     - **Add Context** — append new information and screenshots to the existing ticket as a `### 📝 User Update` block (Protocol 04 pattern), then move on
     - **New Ticket** — this is a distinct issue, proceed to Step D

### Step D: Categorize

Propose a category based on code investigation findings, and confirm with the user via **AskUserQuestion**:

1. **Bug** — something is broken or behaving incorrectly
2. **Feature** — a new capability or enhancement request
3. **Prospective Project** — a large-scope item requiring architecture review and multi-phase planning
4. **Reject Bug Fix** — an existing bug (status: Awaiting Confirmation) was NOT actually fixed; the user observed the same problem during this QA session. This option is only valid when the observation matches an existing `[Awaiting Confirmation]` bug (typically offered during Step C).
5. **Approve Bug Fix** — an existing bug (status: Awaiting Confirmation) IS confirmed fixed; remove it from the active list. This option is only valid when the observation matches an existing `[Awaiting Confirmation]` bug (typically offered during Step C).
6. **Skip** — not actionable, or user changed their mind

### Step E: Create Ticket

Based on the confirmed category:

---

#### For Bugs

1. **Draft** a bug title and description:
   - Clean up speech-to-text artifacts (missing punctuation, filler words, repetition, false starts)
   - Include screenshot references using the image pattern (see Image Handling below)
   - Include relevant findings from code investigation
2. **Present** the draft to the user for approval or edits
3. **Determine priority** (Critical/High/Medium/Low) — propose one based on severity, confirm with user
4. **Create** the ticket file `Debugging/active_bugs/BUG-XX.md`:

```markdown
# BUG-XX: [Title]

## Description
[Cleaned description with screenshot references and code context]

## Priority
[Agreed priority]

## Status
Pending

## Work Log
- YYYY-MM-DD: Created from QA Session <session_id>.
```

5. **Update** `Debugging/debug_plan.md` — append a new row to the Bug Queue table
6. Report: "Created BUG-XX: [title]"

---

#### For Features

1. **Draft** a feature title and description:
   - Clean up speech-to-text artifacts
   - Include screenshot references
   - Include context from code investigation
2. **Present** the draft to the user for approval or edits
3. **Determine priority** — propose one, confirm with user
4. **Create** the ticket file `Features/active_features/FEAT-XX.md`:

```markdown
# FEAT-XX: [Title]

## Description
[Cleaned description with screenshot references]

## Priority
[Agreed priority]

## Status
Pending

## Work Log
- YYYY-MM-DD: Created from QA Session <session_id>.
```

5. **Update** `Features/feature_plan.md` — append a new row to the Feature Queue table
6. Report: "Created FEAT-XX: [title]"

---

#### For Prospective Projects

1. **Draft** a triage document:
   - Clean up speech-to-text artifacts
   - Include screenshot references (using `./assets/` paths — see Image Handling)
   - Include code investigation findings
   - Explain why this is project-sized (scope, architectural implications)
2. **Present** the draft to the user for approval or edits
3. **Choose a descriptive filename** (e.g., `star_rendering_overhaul.md`) — confirm with user
4. **Copy** associated screenshots to `Projects/Triage/assets/` (see Image Handling)
5. **Create** the triage file `Projects/Triage/<descriptive_name>.md`:

```markdown
# [Title]

## Context
[What was observed during QA session, cleaned commentary]

## Screenshots
[./assets/ image references with descriptions]

## Code Investigation Findings
[What the agent found during exploration — files, functions, current behavior]

## Scope Notes
[Why this warrants a full project rather than a bug fix or feature]
```

6. Report: "Created triage item: `<filename>.md` — use `/triage-to-proj <filename>` to convert to a full project."

---

#### For Reject Bug Fix

Follow `Tickets/protocols/05_reject_ticket.md` pattern:

1. **Identify** the matching BUG-XX ticket (from Step C)
2. **Ask the user** for their rejection explanation — clean up speech-to-text artifacts but preserve meaning
3. **Append** to the end of `Debugging/active_bugs/BUG-XX.md`:

```markdown
---
### ❌ Fix Rejected [YYYY-MM-DD HH:MM]
**Reason:** [User's explanation, cleaned up]
**New Constraints:** [Any specific new data or observations, including screenshot references]
---
```

Include screenshot references from this QA session using the standard relative path pattern:
`[![Description](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)`

4. **Update** `Debugging/debug_plan.md` — change status from `[Awaiting Confirmation]` to `[In-Progress]`
5. Report: "BUG-XX fix rejected and reverted to In-Progress."

---

#### For Approve Bug Fix

Follow `Tickets/protocols/03_close_ticket.md` pattern:

1. **Identify** the matching BUG-XX ticket (from Step C)
2. **Read** the ticket to extract the title, solution summary, and key test case
3. **Append** entry to `Debugging/solved_bugs.md`:
   - Format: `## BUG-XX [Title]`
   - Content: Date Solved, Brief Summary of Solution, Key Test Case
4. **Move** `Debugging/active_bugs/BUG-XX.md` to `Debugging/archived_tickets/BUG-XX.md` (do not modify the ticket content — preserve full logs)
5. **Remove** the row for BUG-XX from `Debugging/debug_plan.md`
6. Report: "BUG-XX confirmed fixed and archived."

---

## Phase 3: Session Summary

After all observations have been processed, present a final summary table:

```markdown
## QA Triage Summary — Session <session_id>

| # | Observation | Category | Ticket | Notes |
|---|-------------|----------|--------|-------|
| 1 | Star display too small | Bug | BUG-94 | New ticket |
| 2 | Want fleet auto-routing | Feature | FEAT-06 | New ticket |
| 3 | Combat UI needs overhaul | Project | combat_ui_overhaul.md | Triage created |
| 4 | Shield flicker | Reject Fix | BUG-69 | Fix rejected, reverted to In-Progress |
| 5 | Fleet display correct now | Approve Fix | BUG-85 | Confirmed fixed, archived |
| 6 | Minor comment | Skip | — | Not actionable |

**Created:** X bugs, Y features, Z project triage items
**Bug fixes rejected:** R
**Bug fixes approved:** A
**Duplicates/context added:** N
**Skipped:** M
```

---

## Image Handling

### Source
All session images are in: `Tools/qa_observer/session_data/<session_id>/images/`

### For Bug Tickets (`Debugging/active_bugs/BUG-XX.md`)

Reference images in-place using relative paths from the ticket back to the session directory. **Do NOT copy images.** The session data is the image archive.

Pattern (matching existing BUG-90, BUG-91 convention):
```markdown
[![Screenshot description](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)
```

### For Feature Tickets (`Features/active_features/FEAT-XX.md`)

Same relative path pattern as bugs:
```markdown
[![Screenshot description](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)](../../tools/qa_observer/session_data/<session_id>/images/<filename>.png)
```

### For Project Triage Files (`Projects/Triage/<name>.md`)

**COPY** images from the session `images/` directory to `Projects/Triage/assets/`. Reference them as `./assets/<filename>.png` in the triage markdown.

This is required because the `/triage-to-proj` skill expects `./assets/` references and handles copying them to the project directory during conversion. If images are not in `./assets/`, the conversion will break.

---

## Constraints

- **INTERACTIVE:** Do NOT batch-process all observations silently. Walk through each one with the user, one at a time.
- **CODE REVIEW:** Always investigate relevant code before categorizing. Use Explore agents. Don't guess — look at the actual code.
- **USER APPROVAL:** Always present drafts and get confirmation before creating any ticket or file.
- **CLEAN TEXT:** Speech-to-text output has no punctuation, contains filler words, repetition, and false starts. Clean it up into proper sentences when writing descriptions. Preserve the original meaning faithfully.
- **NO IMPLEMENTATION:** Do not start fixing bugs or implementing features. This is triage and data entry only.
- **SEQUENTIAL IDs:** Always check the relevant dashboard for the next available ID before creating a ticket. Never reuse or skip IDs.
- **IMAGE CONTEXT:** Every screenshot referenced in a ticket must have a text description explaining what it shows and why it's relevant.
