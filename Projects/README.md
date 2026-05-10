# Projects & Tickets System

This directory contains the infrastructure for managing multi-file refactoring projects, bug fixes, and feature implementations in the Starship Battles codebase.

---

## Quick Reference

| I want to... | Skill | Example |
|---|---|---|
| **Start a new refactoring project** | `/claude-proj-start` | `/claude-proj-start Refactor ship combat engine` |
| **Continue working on a project** | `/claude-proj-continue` | `/claude-proj-continue 87` |
| **Review a project plan** | `/claude-proj-review` | `/claude-proj-review 87` |
| **Audit a completed project** | `/claude-proj-audit` | `/claude-proj-audit 87` |
| **Close/archive a project** | `/claude-proj-archive` | `/claude-proj-archive 87` or `/claude-proj-archive 87 88 89` |
| **Revise a completed project** | `/claude-proj-revise` | `/claude-proj-revise 87 Add error handling` |
| **Extract a phase to sub-project** | `/claude-proj-extract-phase` | `/claude-proj-extract-phase 87 3` |
| **Report a bug** | `/claude-ticket-add` | `/claude-ticket-add bug Ship doesn't move after turn 5` |
| **Request a feature** | `/claude-ticket-add` | `/claude-ticket-add feature Add zoom to galaxy map` |
| **Fix a specific bug** | `/claude-ticket-work` | `/claude-ticket-work bug 42` |
| **Implement a feature** | `/claude-ticket-work` | `/claude-ticket-work feature 7` |
| **Auto-fix next bug** | `/claude-ticket-next` | `/claude-ticket-next bug` |
| **Auto-implement next feature** | `/claude-ticket-next` | `/claude-ticket-next feature` |
| **Batch fix bugs** | `/claude-ticket-continue` | `/claude-ticket-continue bug` |
| **Deep investigate a bug** | `/claude-ticket-deep-dive` | `/claude-ticket-deep-dive bug 42` |
| **Close a resolved ticket** | `/claude-ticket-close` | `/claude-ticket-close bug 42` |
| **Batch close tickets** | `/claude-ticket-batch-close` | `/claude-ticket-batch-close bug 46 49 50` |
| **Reject a fix/implementation** | `/claude-ticket-reject` | `/claude-ticket-reject bug 42 Still crashes on turn 3` |
| **Answer ticket questions** | `/claude-ticket-answer` | `/claude-ticket-answer bug 42 Only happens in 4K mode` |
| **Update ticket with new info** | `/claude-ticket-update` | `/claude-ticket-update bug 42 Also affects fleet view` |
| **Run QA triage session** | `/claude-qa-triage` | `/claude-qa-triage` |
| **Convert triage to project** | `/claude-triage-to-proj` | `/claude-triage-to-proj star_rendering` |
| **Manage refactor plan** | `/claude-proj-manage-plan` | `/claude-proj-manage-plan ADD 87` |
| **Add projects to refactor plan** | `/claude-proj-add-to-plan` | `/claude-proj-add-to-plan 87 88` |
| **Reset loop baseline** | `/claude-proj-reset-baseline` | `/claude-proj-reset-baseline` |
| **Archive from refactor plan** | `/claude-proj-archive` | `/claude-proj-archive 87 88` |

---

## Architecture

```
Skills (.claude/skills/)          Protocols                    Data
========================         ==========                   ====

proj-start ─────────────► Projects/protocols/01_init...      Projects/active_projects/PROJ-XX/
proj-continue ──────────► Projects/protocols/03a_cont...       ├── plan.md
proj-review ────────────► Projects/protocols/09_review        ├── design.md
proj-audit ─────────────► Projects/protocols/04_audit         ├── decisions.md
proj-close ─────────────► Projects/protocols/05_close         └── phase_N_checklist.md
proj-revise ────────────► Projects/protocols/06_revise
proj-extract-phase ─────► Projects/protocols/07_extract

ticket-add ─────────────► Tracking/protocols/01_ingest...     Tracking/bugs/active/BUG-XX.md
ticket-work ────────────► Tracking/protocols/02_work...       Tracking/features/active/FEAT-XX.md
ticket-continue ────────► Tracking/protocols/02a_batch...
ticket-deep-dive ───────► Tracking/protocols/02b_deep...
ticket-close ───────────► Tracking/protocols/03_close...
ticket-batch-close ─────► Tracking/protocols/03a_batch...
ticket-update ──────────► Tracking/protocols/04_update...
ticket-reject ──────────► Tracking/protocols/05_reject...
ticket-answer ──────────► Tracking/protocols/06_answer...

Loop Workers (retired) ─► see _marked_for_deletion_2026-05-29/Projects/
```

**Key principle:** Skills are thin entry points that set configuration and reference protocols. Protocols contain the detailed workflow logic. This means changes to workflow behavior only need to be made in one place (the protocol).

---

## Project Lifecycle

```
/claude-proj-start ──► Planning ──► /claude-proj-continue ──► Implementation ──► /claude-proj-audit ──► /claude-proj-archive
                   │              │ (repeat)           │                  │
                   │              └──────────────────────┘                  │
                   │                                                       │
                   └─── /claude-proj-review (validate plan mid-project)           │
                                                                           │
                   /claude-proj-revise (add phases to completed project) ◄────────┘
```

1. **Start** (`/claude-proj-start`): Deep code review, swarm analysis, create plan. Planning only — no implementation.
2. **Continue** (`/claude-proj-continue N`): Autonomous TDD work loop. Executes tasks, updates plan, provides handoff context.
3. **Review** (`/claude-proj-review N`): Validate plan against codebase. 5 parallel review agents check alignment, freshness, gaps.
4. **Audit** (`/claude-proj-audit N`): Skeptical post-completion review. Up to 5 cycles of audit → fix → re-audit.
5. **Close** (`/claude-proj-archive N`): Archive to `archived_projects/`. No validation — user has already accepted.

---

## Ticket System (Bugs & Features)

The ticket system uses unified skills and protocols that handle both bugs and features. The first argument to any `/ticket-*` command is always the type: `bug` or `feature`.

### Bug-specific behavior
- **Anti-reversion rules**: Fixes must not undo recent refactors (checked via git history)
- **Documentation discrepancy checks**: Code vs docs consistency verification
- **Phase 2.5 integrity gate**: Post-fix verification of layer boundaries and conventions
- **Deep dive**: Root cause investigation with diagnostic logging and hypothesis testing

### Feature-specific behavior
- **Ambiguity check**: Requirements clarity verification before implementation
- **Refactor flag**: Can escalate to `[Needs Refactor]` if structural issues found
- **Deep dive**: Scope assessment and complexity rating (Simple/Moderate/Complex/Project-Scale)

### Data locations
- Bug tickets: `Tracking/bugs/active/BUG-XX.md` → `Tracking/bugs/archived/`
- Bug dashboard: `Tracking/debug_plan.md`
- Bug index: `Tracking/solved_bugs.md`
- Feature tickets: `Tracking/features/active/FEAT-XX.md` → `Tracking/features/archived/`
- Feature dashboard: `Tracking/feature_plan.md`
- Feature index: `Tracking/completed_features.md`

---

## Loop Systems (retired 2026-04-29)

Three CLI loop systems (`refactor_loop`, `complexity_loop`, `continuous_loop`)
were built between January and March 2026 but are no longer in use. The last
activity across all three was between 2026-02-13 and 2026-03-01. They have
been staged for deletion at `_marked_for_deletion_2026-05-29/Projects/`;
permanent deletion happens after the 30-day cooling-off period ends.

The active project workflow operates without them. To restart automated work
in the future, decide whether to revive one of the staged loops (the
critical-review report has the rationale for archival) or build a new
automation layer with the lessons from those three.

If you were directed to this section by an old WORKER.md path, the
WORKER.md files now live in the staging directory:
`_marked_for_deletion_2026-05-29/Projects/<loop>/WORKER.md`.

---

## Protocol Reference

### Project Protocols (`Projects/protocols/`)

| # | File | Purpose |
|---|------|---------|
| 01 | `01_initialize_project.md` | Create new project with swarm analysis |
| 02 | `02_plan_protocol.md` | How to read and use project plans |
| 03a | `03a_continue_working.md` | Autonomous multi-task TDD work loop (legacy single-branch) |
| 03b | `03b_parallel_projects.md` | Inter-project parallelism (multiple projects in worktrees) |
| 03c | `03c_phase_aware_execution.md` | Phase DAG, SHA-pinned cumulative reviews, intra-project parallelism |
| 04 | `04_audit_project.md` | Skeptical post-completion audit (final cumulative gate for 03c projects) |
| 05 | `05_close_project.md` | Archive completed project |
| 06 | `06_revise_project.md` | Add phases to completed project |
| 07 | `07_extract_phase.md` | Extract phase into sub-project |
| 08 | `08_automated_loop_protocol.md` | Stateless loop execution |
| 09 | `09_review_project.md` | Interactive plan validation |
| 10 | `10_manage_refactor_plan.md` | Master refactor plan management |
| — | `WORKER_TEMPLATE.md` | Shared worker protocol for all loops |

### Ticket Protocols (`Tracking/protocols/`)

| # | File | Purpose |
|---|------|---------|
| 01 | `01_ingest_ticket.md` | Create new bug/feature ticket |
| 02 | `02_work_ticket.md` | Fix bug or implement feature (TDD) |
| 02a | `02a_batch_work.md` | Autonomous batch processing |
| 02b | `02b_deep_dive.md` | Deep investigation (bug) or scope assessment (feature) |
| 03 | `03_close_ticket.md` | Archive confirmed ticket |
| 03a | `03a_batch_close.md` | Batch archive tickets |
| 04 | `04_update_ticket.md` | Append context to ticket |
| 05 | `05_reject_ticket.md` | Reject fix/implementation |
| 06 | `06_answer_questions.md` | Log answers to clarification questions |

---

## Script Reference (`Projects/scripts/`)

| Script | Purpose |
|--------|---------|
| `create_project.py` | Create new PROJ-XX directory structure |
| `project_status.py` | Show detailed project status |
| `current_task.py` | Identify next task to work on |
| `list_incomplete.py` | List all incomplete tasks |
| `validate_phase.py` | Validate phase completion |
| `validate_audit_ready.py` | Pre-audit validation |
| `validate_close_ready.py` | Pre-archival validation |
| `check_completion.py` | Check if all projects in plan are complete |
| `archive_project.py` | Archive project to `archived_projects/` |
| `batch_archive_projects.py` | Batch archival |
| `deep_archive_manager.py` | Move overflow to `deep_archive/` |
| `commit_phase.py` | Create standardized git commits |
| `update_plan.py` | Programmatic plan file updates |
| `sync_index.py` | Sync `projects_index.md` with filesystem |
| `sync_current_state.py` | Update Current State across projects |

---

## Keeping Things in Sync

When modifying this system, follow these rules to prevent drift:

1. **Changing workflow behavior** → Edit the **protocol** file. Skills reference protocols, so the change propagates automatically.
2. **Changing skill arguments or configuration** → Edit the **skill** SKILL.md file. Update this README's Quick Reference table.
3. **Changing loop worker behavior** → Edit `Projects/protocols/WORKER_TEMPLATE.md`. All three loop workers inherit from it.
4. **Adding a new protocol** → Create the file, add it to the Protocol Reference table in this README.
5. **Adding a new skill** → Create the skill directory, add it to the Quick Reference table in this README.
6. **Renaming/removing a skill or protocol** → Search all `.claude/skills/` and `Projects/protocols/` for references to update.

### File relationships
```
.claude/skills/*/SKILL.md  ──references──►  Projects/protocols/*.md
                                            Tracking/protocols/*.md
Loop WORKER.md files        ──references──►  Projects/protocols/WORKER_TEMPLATE.md
                                            Projects/protocols/08_automated_loop_protocol.md
```

### Verification checklist
After any structural change:
- [ ] `grep -r "old_name" .claude/skills/ Projects/ Tracking/` finds no stale references
- [ ] All skills in Quick Reference table match actual `.claude/skills/` directories
- [ ] All protocols in Protocol Reference tables match actual files on disk
- [ ] README accurately describes the current system
