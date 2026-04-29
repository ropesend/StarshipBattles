---
name: claude-proj-review
description: Review and validate a project plan against the current codebase, then interactively update it
disable-model-invocation: true
argument-hint: <project-number>
---

# Review Project PROJ-$0

**Protocol:** `Projects/protocols/09_review_project.md`

Read and follow the full protocol file `Projects/protocols/09_review_project.md`.

## Your Role

Adopt the **Project Review Coordinator** persona. Your goal is to align the project plan with the current codebase reality — not to re-plan the project from scratch.

## Execution

### Phase 1: Load & Prepare

1. **READ** relevant `docs/` files (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`) as the authoritative reference for how the codebase should be structured.
2. **LOAD** the project plan: `Projects/active_projects/PROJ-$0/plan.md`
3. **LOAD** all phase checklists, `design.md`, and `decisions.md`
3. **RUN** project status:
   ```bash
   python Projects/scripts/project_status.py PROJ-$0
   ```
4. **EXTRACT** scope: file paths from Key Files table and Scope section

### Phase 2: Deep Code Review

**BEFORE launching agents**, pre-create the output directory:
```bash
mkdir -p Projects/active_projects/PROJ-$0/findings
```

Launch **5 general-purpose agents in parallel** with `mode: "bypassPermissions"` (NOT Explore — agents must write report files using the **Write tool**, NOT Bash).

Each agent receives the full plan content, all checklist contents, and design.md as context.

| Agent | Focus | Output |
|-------|-------|--------|
| Plan-Code Alignment Analyst | Verify file paths, line numbers, code references are accurate | `review_YYYYMMDD_alignment_report.md` |
| Task Freshness Analyst | Find already-done, obsolete, or prerequisite-changed tasks | `review_YYYYMMDD_freshness_report.md` |
| Scope Gap Analyst | Identify areas in scope the plan doesn't cover | `review_YYYYMMDD_scope_gap_report.md` |
| Design Pattern Analyst | Validate plan's approach matches `docs/` patterns and conventions | `review_YYYYMMDD_design_report.md` |
| Completeness Auditor | Cross-reference Goals vs Tasks, check phase structure | `review_YYYYMMDD_completeness_report.md` |

Reports go to: `Projects/active_projects/PROJ-$0/findings/`

**VERIFY** all 5 reports exist and are non-empty before proceeding.

### Phase 3: Synthesis

- Read all agent reports
- Categorize findings: Stale References, Already Done, Obsolete, Scope Gaps, Design Drift, Unclear/Ambiguous, Goal Misalignment
- Prioritize by implementation impact (High/Medium/Low)
- De-duplicate findings from multiple agents

### Phase 4: Interactive Discussion

- Walk through findings **batched by category**, highest impact first
- Propose resolutions, get user approval via AskUserQuestion
- Apply approved changes to plan files immediately
- Add new phases if scope gaps warrant it (numbered sequentially)

**CAN modify:** plan.md, phase checklists, decisions.md (append), design.md (with user approval)
**CAN add:** new phases, new tasks
**CANNOT:** uncheck completed tasks, delete phases, change Goals without user approval

### Phase 5: Plan Update & Summary

- Update `## Current State` with review results
- Append review decisions to `decisions.md`
- Present summary: findings by category, changes applied, plan readiness

**MINDSET:** Be thorough but practical. Focus on what would actually block or misdirect implementation.
