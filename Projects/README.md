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
| **Report a bug** | `/claude-gi-add` | `/claude-gi-add bug Ship doesn't move after turn 5` |
| **Request a feature** | `/claude-gi-add` | `/claude-gi-add feature Add zoom to galaxy map` |
| **Fix a specific issue** | `/claude-gi-work` | `/claude-gi-work 42` |
| **Auto-fix next issue** | `/claude-gi-next` | `/claude-gi-next bug` |
| **Batch fix issues** | `/claude-gi-continue` | `/claude-gi-continue bug` |
| **Deep investigate an issue** | `/claude-gi-deep-dive` | `/claude-gi-deep-dive 42` |
| **Parallel deep dive across issues** | `/claude-gi-deep-dive-parallel` | `/claude-gi-deep-dive-parallel` |
| **Close a resolved issue** | `/claude-gi-close` | `/claude-gi-close 42` |
| **Batch close issues** | `/claude-gi-batch-close` | `/claude-gi-batch-close 46 49 50` |
| **Reject a fix** | `/claude-gi-reject` | `/claude-gi-reject 42 Still crashes on turn 3` |
| **Answer issue questions** | `/claude-gi-answer` | `/claude-gi-answer 42 Only happens in 4K mode` |
| **Update issue with new info** | `/claude-gi-update` | `/claude-gi-update 42 Also affects fleet view` |
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

gi-add ─────────────────► (no shared protocol — skill is self-contained)
gi-work ────────────────► AgentCoordination/protocols/ticket_workflow.md
gi-deep-dive ───────────► AgentCoordination/protocols/ticket_deep_dive.md
gi-deep-dive-parallel ──► (self-contained)
gi-continue, gi-next, gi-close, gi-batch-close,
gi-update, gi-reject, gi-answer ──► (each self-contained, ~50 lines)

Issues live on GitHub:                   https://github.com/ropesend/StarshipBattles/issues
Evidence (screenshots/logs):             tracking-assets/screenshots/, tracking-assets/logs/

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

Tickets live on **GitHub Issues**: https://github.com/ropesend/StarshipBattles/issues.
Skills are `/claude-gi-*`. The first argument to `/claude-gi-add` is the type
(`bug` or `feature`); other commands take the issue number directly.

### Bug-specific behavior
- **Anti-reversion rules**: Fixes must not undo recent refactors (checked via git history)
- **Documentation discrepancy checks**: Code vs docs consistency verification
- **Phase 2.5 integrity gate**: Post-fix verification of layer boundaries and conventions
- **Deep dive**: Root cause investigation with diagnostic logging and hypothesis testing

### Feature-specific behavior
- **Ambiguity check**: Requirements clarity verification before implementation
- **Refactor flag**: Can escalate to a project if structural issues are found
- **Deep dive**: Scope assessment and complexity rating (Simple/Moderate/Complex/Project-Scale)

### Storage
- Issues: GitHub (state, labels, comments, parent/sub-issue links)
- Evidence: `tracking-assets/screenshots/<YYYY-MM>/` and `tracking-assets/logs/issue-N/`
- Historical (read-only) archives from the retired `Tracking/` system: `AgentCoordination/legacy_tickets/`
- Dashboard equivalent: `gh issue list --label "type:bug" --label "status:pending"` (and variants)

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

### Ticket Protocols (`AgentCoordination/protocols/`)

| File | Purpose |
|------|---------|
| `ticket_workflow.md` | TDD work loop: reproduce → failing test → root-cause → fix → verify → doc-sync. Used by `/claude-gi-work` (and codex-side equivalents). |
| `ticket_deep_dive.md` | Investigation-only mode for issues resisting quick fixes or with unclear scope. Used by `/claude-gi-deep-dive`. |

Other ticket workflows (`gi-add`, `gi-continue`, `gi-close`, `gi-batch-close`,
`gi-update`, `gi-reject`, `gi-answer`, `gi-next`, `gi-deep-dive-parallel`)
are self-contained in their SKILL.md — no shared protocol file.

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
                                            Projects/gp_protocols/*.md
                                            AgentCoordination/protocols/ticket_*.md
Loop WORKER.md files        ──references──►  Projects/protocols/WORKER_TEMPLATE.md
                                            Projects/protocols/08_automated_loop_protocol.md
```

### Verification checklist
After any structural change:
- [ ] `grep -r "old_name" .claude/skills/ Projects/ AgentCoordination/protocols/` finds no stale references
- [ ] All skills in Quick Reference table match actual `.claude/skills/` directories
- [ ] All protocols in Protocol Reference tables match actual files on disk
- [ ] README accurately describes the current system
