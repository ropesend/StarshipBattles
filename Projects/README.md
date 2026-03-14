# Projects & Tickets System

This directory contains the infrastructure for managing multi-file refactoring projects, bug fixes, and feature implementations in the Starship Battles codebase.

---

## Quick Reference

| I want to... | Skill | Example |
|---|---|---|
| **Start a new refactoring project** | `/proj-start` | `/proj-start Refactor ship combat engine` |
| **Continue working on a project** | `/proj-continue` | `/proj-continue 87` |
| **Review a project plan** | `/proj-review` | `/proj-review 87` |
| **Audit a completed project** | `/proj-audit` | `/proj-audit 87` |
| **Close/archive a project** | `/proj-close` | `/proj-close 87` or `/proj-close 87 88 89` |
| **Revise a completed project** | `/proj-revise` | `/proj-revise 87 Add error handling` |
| **Extract a phase to sub-project** | `/proj-extract-phase` | `/proj-extract-phase 87 3` |
| **Report a bug** | `/ticket-add` | `/ticket-add bug Ship doesn't move after turn 5` |
| **Request a feature** | `/ticket-add` | `/ticket-add feature Add zoom to galaxy map` |
| **Fix a specific bug** | `/ticket-work` | `/ticket-work bug 42` |
| **Implement a feature** | `/ticket-work` | `/ticket-work feature 7` |
| **Auto-fix next bug** | `/ticket-next` | `/ticket-next bug` |
| **Auto-implement next feature** | `/ticket-next` | `/ticket-next feature` |
| **Batch fix bugs** | `/ticket-continue` | `/ticket-continue bug` |
| **Deep investigate a bug** | `/ticket-deep-dive` | `/ticket-deep-dive bug 42` |
| **Close a resolved ticket** | `/ticket-close` | `/ticket-close bug 42` |
| **Batch close tickets** | `/ticket-batch-close` | `/ticket-batch-close bug 46 49 50` |
| **Reject a fix/implementation** | `/ticket-reject` | `/ticket-reject bug 42 Still crashes on turn 3` |
| **Answer ticket questions** | `/ticket-answer` | `/ticket-answer bug 42 Only happens in 4K mode` |
| **Update ticket with new info** | `/ticket-update` | `/ticket-update bug 42 Also affects fleet view` |
| **Run QA triage session** | `/qa-triage` | `/qa-triage` |
| **Convert triage to project** | `/triage-to-proj` | `/triage-to-proj star_rendering` |
| **Manage refactor plan** | `/proj-manage-plan` | `/proj-manage-plan ADD 87` |
| **Add projects to refactor plan** | `/proj-add-to-plan` | `/proj-add-to-plan 87 88` |
| **Reset loop baseline** | `/proj-reset-baseline` | `/proj-reset-baseline` |
| **Archive from refactor plan** | `/proj-archive` | `/proj-archive 87 88` |

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

ticket-add ─────────────► Tickets/protocols/01_ingest...     Debugging/active_bugs/BUG-XX.md
ticket-work ────────────► Tickets/protocols/02_work...       Features/active_features/FEAT-XX.md
ticket-continue ────────► Tickets/protocols/02a_batch...
ticket-deep-dive ───────► Tickets/protocols/02b_deep...
ticket-close ───────────► Tickets/protocols/03_close...
ticket-batch-close ─────► Tickets/protocols/03a_batch...
ticket-update ──────────► Tickets/protocols/04_update...
ticket-reject ──────────► Tickets/protocols/05_reject...
ticket-answer ──────────► Tickets/protocols/06_answer...

Loop Workers ───────────► Projects/protocols/WORKER_TEMPLATE.md
  refactor_loop/WORKER.md
  continuous_loop/CYCLE_WORKER.md
  complexity_loop/REFACTOR_WORKER.md
```

**Key principle:** Skills are thin entry points that set configuration and reference protocols. Protocols contain the detailed workflow logic. This means changes to workflow behavior only need to be made in one place (the protocol).

---

## Project Lifecycle

```
/proj-start ──► Planning ──► /proj-continue ──► Implementation ──► /proj-audit ──► /proj-close
                   │              │ (repeat)           │                  │
                   │              └──────────────────────┘                  │
                   │                                                       │
                   └─── /proj-review (validate plan mid-project)           │
                                                                           │
                   /proj-revise (add phases to completed project) ◄────────┘
```

1. **Start** (`/proj-start`): Deep code review, swarm analysis, create plan. Planning only — no implementation.
2. **Continue** (`/proj-continue N`): Autonomous TDD work loop. Executes tasks, updates plan, provides handoff context.
3. **Review** (`/proj-review N`): Validate plan against codebase. 5 parallel review agents check alignment, freshness, gaps.
4. **Audit** (`/proj-audit N`): Skeptical post-completion review. Up to 5 cycles of audit → fix → re-audit.
5. **Close** (`/proj-close N`): Archive to `archived_projects/`. No validation — user has already accepted.

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
- Bug tickets: `Debugging/active_bugs/BUG-XX.md` → `Debugging/archived_tickets/`
- Bug dashboard: `Debugging/debug_plan.md`
- Bug index: `Debugging/solved_bugs.md`
- Feature tickets: `Features/active_features/FEAT-XX.md` → `Features/archived_features/`
- Feature dashboard: `Features/feature_plan.md`
- Feature index: `Features/completed_features.md`

---

## Loop Systems

Three automated loop systems execute work without human interaction. Each uses a thin WORKER.md that references the shared `Projects/protocols/WORKER_TEMPLATE.md`.

| Loop | Purpose | Plan File | When to Use |
|------|---------|-----------|-------------|
| **refactor_loop** | Execute queued refactoring projects | `refactor_loop/refactor_plan.md` | User-curated list of projects to execute sequentially |
| **continuous_loop** | Autonomous improvement cycles | `continuous_loop/cycle_plan.md` | Sweep → find issues → create projects → execute → repeat |
| **complexity_loop** | Reduce cyclomatic complexity | `complexity_loop/cycle_plan.md` | Target high-complexity functions for automated refactoring |

### Running a loop
```bash
# Refactor loop
./Projects/refactor_loop/loop_runner.sh    # or .ps1 on Windows

# Continuous loop
powershell ./Projects/continuous_loop/continuous_loop.ps1

# Complexity loop
powershell ./Projects/complexity_loop/complexity_loop.ps1
```

Each loop iteration: reads plan → finds next incomplete item → executes one phase or audit → updates plan → commits → exits. The shell script restarts for the next iteration.

---

## Protocol Reference

### Project Protocols (`Projects/protocols/`)

| # | File | Purpose |
|---|------|---------|
| 01 | `01_initialize_project.md` | Create new project with swarm analysis |
| 02 | `02_plan_protocol.md` | How to read and use project plans |
| 03a | `03a_continue_working.md` | Autonomous multi-task TDD work loop |
| 04 | `04_audit_project.md` | Skeptical post-completion audit |
| 05 | `05_close_project.md` | Archive completed project |
| 06 | `06_revise_project.md` | Add phases to completed project |
| 07 | `07_extract_phase.md` | Extract phase into sub-project |
| 08 | `08_automated_loop_protocol.md` | Stateless loop execution |
| 09 | `09_review_project.md` | Interactive plan validation |
| 10 | `10_manage_refactor_plan.md` | Master refactor plan management |
| — | `WORKER_TEMPLATE.md` | Shared worker protocol for all loops |

### Ticket Protocols (`Tickets/protocols/`)

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
                                            Tickets/protocols/*.md
Loop WORKER.md files        ──references──►  Projects/protocols/WORKER_TEMPLATE.md
                                            Projects/protocols/08_automated_loop_protocol.md
```

### Verification checklist
After any structural change:
- [ ] `grep -r "old_name" .claude/skills/ Projects/ Tickets/` finds no stale references
- [ ] All skills in Quick Reference table match actual `.claude/skills/` directories
- [ ] All protocols in Protocol Reference tables match actual files on disk
- [ ] README accurately describes the current system
