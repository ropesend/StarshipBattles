# PROTOCOL 09: Review Project (Interactive Plan Validation)
**Role:** Project Review Coordinator

**Goal:** Validate a project plan against the current codebase, identify discrepancies and gaps, and interactively update the plan with the user to ensure alignment before implementation.

**CRITICAL:** Be thorough but practical. The goal is to align the plan with reality, not to re-plan the project from scratch. Focus on what would actually block or misdirect implementation.

---

## When to Use This Protocol

Use this protocol when:
- A project has been idle and you want to verify the plan is still accurate before starting/resuming work
- Other projects completed that may have changed code this project depends on
- Significant time passed between planning and implementation
- The user suspects the plan may be out of date
- As a "preflight check" before a long automated implementation run (Protocol 08)

**Do NOT use this protocol for:**
- Post-implementation verification (use Protocol 04: Audit)
- Starting a brand new project (use Protocol 01: Initialize Project)
- Adding new features to a completed project (use Protocol 06: Revise Project)
- General codebase health checks (use Reviews system)

---

## Process Overview

```
1. Load project artifacts and extract scope
2. Launch 5 analysis agents to review code against plan
3. Synthesize agent findings into categorized issues
4. Walk through findings interactively with user (batched by category)
5. Apply approved changes to plan files
6. Update Current State and decisions log
```

---

## Phase 1: Load & Prepare

### 1.1: Load Project Artifacts

Load ALL project documents:
- `Projects/active_projects/PROJ-XX/plan.md` — Main project document
- All `phase_N_checklist.md` files — Detailed task breakdowns
- `design.md` — Architecture and design rationale
- `decisions.md` — Decision history

### 1.2: Get Project Status

```bash
python Projects/scripts/project_status.py PROJ-XX
```

Verify:
- Project is active (in `active_projects/`)
- Project has incomplete phases
- Note which phases are complete vs. in progress vs. not started

### 1.3: Extract Scope

From the plan, extract:
- **File paths** from the Key Files table and Scope section
- **In-scope boundaries** (what's included and excluded)
- **Goals** — The high-level objectives
- **All task references** — Every file path, line number, class name, and function name mentioned in any task or subtask

This extracted scope becomes the input context for the analysis agents.

---

## Phase 2: Deep Code Review (Agent Swarm)

Launch **5 `general-purpose` agents in parallel** (single message, multiple Task tool calls). Each agent receives the full plan content, all checklist contents, and design.md as context.

**IMPORTANT:**
- Use `subagent_type="general-purpose"` — NOT "Explore" (agents must write report files)
- **BEFORE launching agents**, the coordinator MUST pre-create the findings directory:
  ```bash
  mkdir -p Projects/active_projects/PROJ-XX/findings
  ```
- Each agent prompt MUST instruct the agent to use the **Write tool** (NOT Bash/echo/cat) to save its report
- Launch agents with `mode: "bypassPermissions"` to ensure Write tool access
- Verify all 5 report files exist and are non-empty before proceeding to Phase 3

### Report Naming Convention

Reports are written to: `Projects/active_projects/PROJ-XX/findings/`

Format: `review_YYYYMMDD_<role>_report.md`

Example: `review_20260227_alignment_report.md`

The timestamp prefix allows multiple reviews over time; the `review_` prefix distinguishes from other agent reports (Protocol 01 swarm, Protocol 04 investigations).

---

### Agent Roster

#### Agent 1: Plan-Code Alignment Analyst

**Focus:** Verify that every file path, line number, and code reference in the plan matches reality.

```markdown
# Project Review Agent: Plan-Code Alignment Analyst

## Your Task
For each task and subtask in the project plan, verify that the code references are accurate.

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Phase Checklists
{ALL_PHASE_CHECKLIST_CONTENTS}

## Verification Process
For each task/subtask that references code:
1. Open the file at the specified path — does it exist?
2. Check the referenced line numbers — do they point to the right code?
3. Verify referenced classes, functions, and variables still exist
4. Check if the code at that location matches the task description
5. Note any references that are wrong, shifted, or pointing to refactored code

## Finding Format
For each discrepancy:

### {FINDING_ID}: {Brief Title}
**Task:** {Task X.Y, Subtask description}
**Plan Reference:** `{file_path}:{line_numbers}` — {what plan says}
**Actual Code:** {what the code actually shows}
**Impact:** {Would this block implementation? Mislead the developer?}
**Proposed Fix:** {Updated reference, corrected description}

## Output
**CRITICAL:** You MUST use the **Write** tool (NOT Bash, NOT echo, NOT cat) to save your report to:
Projects/active_projects/PROJ-XX/findings/review_YYYYMMDD_alignment_report.md

Your analysis is LOST if you don't write the file.
```

---

#### Agent 2: Task Freshness Analyst

**Focus:** Identify tasks that are already completed, obsolete, or have changed prerequisites.

```markdown
# Project Review Agent: Task Freshness Analyst

## Your Task
Determine if any planned tasks are already done, obsolete, or have changed conditions.

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Phase Checklists
{ALL_PHASE_CHECKLIST_CONTENTS}

## Analysis Process
For each unchecked task/subtask:
1. Read the code at the target location
2. Determine if the desired change has ALREADY been made (by another project, hotfix, etc.)
3. Determine if the task is OBSOLETE (target code deleted, rewritten, or no longer relevant)
4. Check if PREREQUISITES changed (a dependency the task assumes may have been modified)
5. For tasks marked "Not Started" — is the starting state still as described?

## Status Categories
- **ALREADY_DONE** — Code already matches the task's desired end state
- **PARTIALLY_DONE** — Some subtasks are already completed, others remain
- **OBSOLETE** — Target code no longer exists or was completely rewritten
- **PREREQUISITE_CHANGED** — Task depends on something that changed
- **STILL_VALID** — Task is accurate and ready for implementation

## Finding Format
For each non-STILL_VALID task:

### {FINDING_ID}: {Brief Title}
**Task:** {Task X.Y}
**Status:** {ALREADY_DONE / PARTIALLY_DONE / OBSOLETE / PREREQUISITE_CHANGED}
**Evidence:** {What you found in the code}
**Impact:** {High/Medium/Low — how much does this affect implementation?}
**Proposed Resolution:** {Mark done, remove task, update description, etc.}

## Output
**CRITICAL:** You MUST use the **Write** tool (NOT Bash, NOT echo, NOT cat) to save your report to:
Projects/active_projects/PROJ-XX/findings/review_YYYYMMDD_freshness_report.md

Your analysis is LOST if you don't write the file.
```

---

#### Agent 3: Scope Gap Analyst

**Focus:** Find important code areas within the project's scope that the plan doesn't cover.

```markdown
# Project Review Agent: Scope Gap Analyst

## Your Task
Identify areas within the project's scope that should be addressed but aren't mentioned in any task.

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Phase Checklists
{ALL_PHASE_CHECKLIST_CONTENTS}

## Project Scope
**In-scope files/directories:**
{SCOPE_FILE_LIST}

**Project Goals:**
{GOALS_LIST}

## Analysis Process
1. Read code files that are IN SCOPE but NOT mentioned in any task
2. Read code files that ARE mentioned — look for issues adjacent to planned tasks
3. Cross-reference the Goals section — are there goals with no corresponding tasks?
4. Look for:
   - Related code that needs updating but isn't in the plan
   - Edge cases the plan doesn't address
   - Integration points that could break
   - Related tests that should be updated
   - Code patterns inconsistent with the plan's goals

## Finding Format
For each gap:

### {FINDING_ID}: {Brief Title}
**Location:** `{file_path}:{line_numbers}`
**Related Goal:** {Which project goal this relates to, or "None — new concern"}
**Gap Description:** {What the plan is missing}
**Impact:** {What could go wrong if this isn't addressed}
**Proposed Resolution:** {Add task to existing phase, create new phase, note for later}
**Effort:** {Simple/Medium/Complex}

## Output
**CRITICAL:** You MUST use the **Write** tool (NOT Bash, NOT echo, NOT cat) to save your report to:
Projects/active_projects/PROJ-XX/findings/review_YYYYMMDD_scope_gap_report.md

Your analysis is LOST if you don't write the file.
```

---

#### Agent 4: Design Pattern Analyst

**Focus:** Verify the plan's proposed approach still matches current codebase patterns and conventions **as documented in `docs/`**.

```markdown
# Project Review Agent: Design Pattern Analyst

## Your Task
Verify that the project plan's proposed implementation approach is consistent with the documented architecture, patterns, and conventions.

## CRITICAL: Read Documentation First
Before analyzing code, read these documentation files:
- `docs/01_ARCHITECTURE.md` — Layer structure and dependency rules
- `docs/02_PATTERNS.md` — Established design patterns
- `docs/03_CONVENTIONS.md` — Naming and coding conventions
- Any relevant system docs in `docs/systems/`

The `docs/` directory is the authoritative source for how the codebase should be structured.

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Design Document
{DESIGN_MD_CONTENT}

## Phase Checklists
{ALL_PHASE_CHECKLIST_CONTENTS}

## Analysis Process
1. Review the design.md for architectural decisions and proposed patterns
2. **Cross-reference against `docs/` documentation:**
   - Does the plan follow the patterns documented in `docs/02_PATTERNS.md`?
   - Does the plan follow conventions in `docs/03_CONVENTIONS.md`?
   - Does the plan respect layer boundaries in `docs/01_ARCHITECTURE.md`?
3. Check the current codebase for:
   - Has the codebase adopted new patterns since the plan was written?
   - Does the plan propose an approach that conflicts with current conventions?
   - Are there existing utilities or abstractions the plan should use but doesn't mention?
   - Has a dependency or API the plan relies on changed?
4. For each task that describes HOW to implement something:
   - Is the proposed approach still the best way?
   - Are there simpler alternatives available now?
   - Would the approach create inconsistency with recent codebase changes?

## Finding Format
For each concern:

### {FINDING_ID}: {Brief Title}
**Plan Assumption:** {What the plan/design expects}
**Current Reality:** {What the codebase actually shows}
**Impact:** {Would following the plan create problems?}
**Proposed Resolution:** {Update approach, use existing utility, align with new pattern}

## Output
**CRITICAL:** You MUST use the **Write** tool (NOT Bash, NOT echo, NOT cat) to save your report to:
Projects/active_projects/PROJ-XX/findings/review_YYYYMMDD_design_report.md

Your analysis is LOST if you don't write the file.
```

---

#### Agent 5: Completeness Auditor

**Focus:** Cross-reference Goals against Tasks bidirectionally. Ensure coherence.

```markdown
# Project Review Agent: Completeness Auditor

## Your Task
Verify that the project plan is internally consistent: every goal has tasks, every task traces to a goal, and the phase structure makes sense.

## Project Plan
{FULL_PLAN_MD_CONTENT}

## Phase Checklists
{ALL_PHASE_CHECKLIST_CONTENTS}

## Analysis Process

### Goal → Task Mapping
For each Goal in the plan:
1. Identify which tasks address this goal
2. Flag goals with NO corresponding tasks (unaddressed goals)
3. Flag goals where tasks seem insufficient to achieve the goal

### Task → Goal Mapping
For each Task:
1. Identify which goal it serves
2. Flag tasks that don't clearly trace back to any stated goal (orphaned work)
3. Flag tasks that seem out of scope

### Phase Coherence
1. Are phases ordered logically? (dependencies respected)
2. Are tasks in the right phases? (any tasks that should move)
3. Are complexity tags accurate? ([Simple] tasks with many subtasks, [Complex] without breakdown)
4. Are test commands specified and reasonable?

### Scope Consistency
1. Does the "In Scope" list match what's actually in the tasks?
2. Does the "Out of Scope" list conflict with any tasks?
3. Are all Key Files actually referenced by at least one task?

## Finding Format
For each issue:

### {FINDING_ID}: {Brief Title}
**Category:** {Unaddressed Goal / Orphaned Task / Phase Ordering / Scope Mismatch / Complexity Tag}
**Details:** {What's inconsistent}
**Impact:** {How this affects implementation}
**Proposed Resolution:** {Add tasks, remove tasks, reorder, update tags}

## Output
**CRITICAL:** You MUST use the **Write** tool (NOT Bash, NOT echo, NOT cat) to save your report to:
Projects/active_projects/PROJ-XX/findings/review_YYYYMMDD_completeness_report.md

Your analysis is LOST if you don't write the file.
```

---

## Phase 3: Synthesis

After all 5 agents complete, the coordinator:

### 3.1: Verify Agent Outputs

Check that all 5 report files exist in `findings/` and are non-empty (> 100 bytes).

**If any agent failed to write its report:**
- Re-launch the affected agent synchronously (without `run_in_background`)
- Wait for completion before proceeding

### 3.2: Read and Categorize Findings

Read all 5 reports and compile a unified findings list. Categorize each finding:

| Category | Description | Source Agents |
|----------|-------------|---------------|
| **Stale References** | File paths, line numbers, code references that are wrong | Alignment |
| **Already Done** | Tasks/subtasks that appear completed in current code | Freshness |
| **Obsolete** | Tasks targeting code that no longer exists | Freshness |
| **Scope Gaps** | Important areas the plan doesn't cover | Scope Gap |
| **Design Drift** | Plan's approach conflicts with current patterns | Design Pattern |
| **Unclear/Ambiguous** | Tasks that are vague or could be misinterpreted | Alignment, Completeness |
| **Goal Misalignment** | Goals without tasks, or tasks without goals | Completeness |
| **Phase Structure** | Ordering, complexity tags, or grouping issues | Completeness |

### 3.3: Prioritize

Assign impact levels:
- **High** — Would block or misdirect implementation (stale references to deleted files, obsolete tasks, major scope gaps)
- **Medium** — Would cause confusion or extra work (shifted line numbers, design drift, unclear tasks)
- **Low** — Minor corrections (slightly inaccurate references, minor scope additions, tag adjustments)

### 3.4: De-duplicate

Multiple agents may flag the same issue from different perspectives. Merge duplicates, keeping the most complete description.

---

## Phase 4: Interactive Discussion

Present findings to the user **batched by category**, starting with highest-impact items.

### Discussion Flow

For each category with findings:

1. **Present the batch:**
   ```
   ## Stale References (4 findings)

   1. Task 2.3 references `fleet.py:line 145` but that code moved to line 203
   2. Task 3.1 references `FleetOrderManager.dispatch()` which was renamed to `process()`
   3. Task 4.2 references `game/strategy/old_module.py` which was deleted
   4. Task 5.1 line range 50-75 now covers different code (was refactored)

   Proposed: Update references 1, 2, 4. Remove or rewrite task for #3.
   ```

2. **Get user input:**
   - Use `AskUserQuestion` for straightforward batch approvals
   - Discuss complex items in conversation (scope changes, design decisions)

3. **Apply approved changes immediately:**
   - Edit the relevant plan files (plan.md, phase checklists)
   - For new phases: create new `phase_N_checklist.md` files

4. **Move to next category**

### Modification Rules

**CAN modify:**
- `plan.md` — Scope, Key Files, Current State, phase status table
- `phase_N_checklist.md` — Task descriptions, file references, line numbers, add/remove tasks, mark tasks as done or obsolete
- `decisions.md` — Append new entries (append-only, never modify existing)
- `design.md` — Update assumptions, patterns, risks (with explicit user approval)

**CAN add:**
- New phases (numbered sequentially after existing phases)
- New tasks within existing phases
- New entries to decisions log

**CANNOT:**
- Uncheck completed tasks (completed work is historical record)
- Delete historical phases (mark as Obsolete instead)
- Change project Goals without explicit user approval
- Modify production code files (`*.py` in `game/`, `tests/`, etc.)

---

## Phase 5: Plan Update & Summary

### 5.0: Update File Manifest

If any changes were applied that affect which files the project touches (new tasks, new phases, updated file references):
- Regenerate `manifest.md` by scanning all phase checklists for `**File:**` fields
- Include all files from the Key Files table in `plan.md`
- Include all test files (new and existing) referenced in tasks
- If no `manifest.md` exists, create one now (required for `/claude-proj-parallel`)

### 5.1: Update Current State

Update `plan.md` `## Current State`:
```markdown
## Current State
**Last Updated:** [Now]
**Last Agent Action:** Project review completed — [N] findings addressed, [N] changes applied
**Next Action:** [Implementation of Phase X / User to review changes / etc.]
**Blockers:** [Any unresolved findings or None]
**Context for Next Agent:** Plan reviewed and updated on [date]. Key changes: [brief list]. All references verified against current codebase.
```

### 5.2: Update Decisions Log

Append to `decisions.md`:
```markdown
| [Date] | Project review (Protocol 09) conducted | [N] findings: [breakdown by category]. Changes: [brief list of what was updated]. |
```

### 5.3: Present Summary

```
## Review Complete: PROJ-XX

### Findings Summary
| Category | Count | High | Medium | Low |
|----------|-------|------|--------|-----|
| Stale References | X | X | X | X |
| Already Done | X | X | X | X |
| Obsolete | X | X | X | X |
| Scope Gaps | X | X | X | X |
| Design Drift | X | X | X | X |
| Unclear/Ambiguous | X | X | X | X |
| Goal Misalignment | X | X | X | X |

### Changes Applied
- [N] file references updated
- [N] tasks marked as already done
- [N] tasks marked as obsolete
- [N] new tasks added
- [N] new phases created
- [N] task descriptions clarified

### Plan Status
Plan is [aligned and ready for implementation / has unresolved items requiring follow-up]
```

### 5.4: Next Steps

Inform user:
- **If plan is ready:** "Use 'Continue Project' prompt to begin implementation."
- **If unresolved items:** List what needs attention before implementation can start.

---

## Key Principles

1. **Practical over exhaustive** — Focus on what would actually block implementation
2. **Current code is truth** — The codebase is authoritative; the plan must match it
3. **User decides** — Always get approval before making scope changes or adding work
4. **Preserve history** — Don't delete completed work; mark obsolete items clearly
5. **Agents write reports** — Use `general-purpose` agents that can persist their findings
6. **Batch discussions** — Group findings by category for efficient user interaction
