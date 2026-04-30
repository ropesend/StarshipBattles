# Tracking — Unified Ticket System

Unified system for tracking and resolving bugs and features via TDD workflows.

## Directory Structure

| Path | Purpose |
|------|---------|
| `bugs/active/BUG-XX.md` | Active bug tickets being worked on |
| `bugs/archived/BUG-XX.md` | Resolved and archived bug tickets |
| `bugs/logs/BUG-XX_logs/` | Debug logs for active investigations |
| `features/active/FEAT-XX.md` | Active feature tickets being worked on |
| `features/archived/FEAT-XX.md` | Completed and archived feature tickets |
| `protocols/` | Shared ticket workflow protocols (11 files) |
| `scripts/` | Python utilities for archiving and confirming tickets |
| `debug_plan.md` | Bug queue dashboard with status tracking |
| `feature_plan.md` | Feature queue dashboard with status tracking |
| `solved_bugs.md` | Index of solved bugs (date, summary, test case) |
| `completed_features.md` | Index of completed features (date, summary, test case) |

## How It Works

Bugs and features share the same protocols but store data in separate subdirectories:

| | Bugs | Features |
|--|------|----------|
| **Active tickets** | `Tracking/bugs/active/BUG-XX.md` | `Tracking/features/active/FEAT-XX.md` |
| **Archived tickets** | `Tracking/bugs/archived/` | `Tracking/features/archived/` |
| **Dashboard** | `Tracking/debug_plan.md` | `Tracking/feature_plan.md` |
| **Completion index** | `Tracking/solved_bugs.md` | `Tracking/completed_features.md` |
| **Protocols** | `Tracking/protocols/` (shared) | `Tracking/protocols/` (shared) |

## Ticket Lifecycle

```
[Pending] → [In-Progress] → [Awaiting Confirmation] → (user verifies) → archived
                ↓                       ↓
        [Needs Clarification]    [Rejected → In-Progress]
                ↓
        (user answers → Pending)
```

**Bug-only statuses:** `[Deep Investigation]`, `[Needs Human Debug]`, `[Blocked]`
**Feature-only statuses:** `[Needs Refactor]`, `[Needs Project]`, `[Analysis]`

## Skills (slash commands)

| Skill | What it does |
|-------|-------------|
| `/claude-ticket-add bug <desc>` | Create new bug ticket(s) |
| `/claude-ticket-add feature <desc>` | Create new feature ticket(s) |
| `/claude-ticket-work bug 42` | Fix a specific bug by ID (TDD) |
| `/claude-ticket-work feature 7` | Implement a specific feature by ID (TDD) |
| `/claude-ticket-next bug` | Pick highest-priority pending bug and start working |
| `/claude-ticket-next feature` | Pick highest-priority pending feature and start working |
| `/claude-ticket-continue bug` | Autonomous batch: fix bugs until context limit |
| `/claude-ticket-continue feature` | Autonomous batch: implement features until context limit |
| `/claude-ticket-deep-dive bug 42` | Deep investigation for persistent bugs |
| `/claude-ticket-deep-dive feature 7` | Scope assessment for complex features |
| `/claude-ticket-close bug 42` | Archive a confirmed fix |
| `/claude-ticket-close feature 7` | Archive a confirmed feature |
| `/claude-ticket-batch-close bug 46 49` | Archive multiple confirmed tickets |
| `/claude-ticket-reject bug 42 <reason>` | Reject a fix, revert to In-Progress |
| `/claude-ticket-update bug 42 <text>` | Append context to a ticket (no analysis) |
| `/claude-ticket-answer bug 42 <answers>` | Log answers to clarification questions |

## Protocols

All protocols are in `Tracking/protocols/`:

| Protocol | Purpose |
|----------|---------|
| `01_ingest_ticket.md` | Create tickets from user descriptions (data entry only) |
| `02_work_ticket.md` | Full TDD resolution workflow (single ticket) |
| `02a_batch_work.md` | Autonomous batch resolution (multiple tickets) |
| `02b_deep_dive.md` | Deep investigation (bugs) or scope assessment (features) |
| `02c_parallel_debug.md` | Parallel debugging with multiple agents |
| `02d_parallel_deep_dive.md` | Parallel deep dive investigation |
| `03_close_ticket.md` | Archive a single confirmed ticket |
| `03a_batch_close.md` | Archive multiple confirmed tickets |
| `04_update_ticket.md` | Append context (data entry only) |
| `05_reject_ticket.md` | Reject and revert status (record-keeping only) |
| `06_answer_questions.md` | Log user answers and re-queue (record-keeping only) |

## Documentation Rules

All ticket resolution protocols enforce these rules:

1. **Read `docs/` before working.** Relevant architecture, pattern, and convention docs must be read before fixing bugs or implementing features.
2. **Check for discrepancies.** Compare the affected code against `docs/`. If code contradicts documented patterns, check git dates to determine which is correct.
3. **Update `docs/` inline.** If a fix/implementation changes architecture, patterns, or conventions, update the relevant `docs/` file in the same session.
4. **Always document discrepancies** in the ticket's `## Work Log`, regardless of resolution.

## Authority Limits

Agents working tickets can set status to `[Awaiting Confirmation]` but **cannot**:
- Mark tickets as `[Solved]` or `[Completed]`
- Move files to archive directories
- Those actions require the user to invoke `/claude-ticket-close`
