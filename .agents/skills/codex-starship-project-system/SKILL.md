---
name: codex-starship-project-system
description: Manage Starship Battles PROJ-XX workflows. Use for starting, continuing, reviewing, auditing, revising, extracting phases from, adding to the plan, resetting baselines for, archiving, or closing projects under Projects/active_projects using Projects/protocols and strict TDD.
---

# Codex Starship Project System

Use the shared project protocols and scripts. Skills are entry points; protocol files are authoritative.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `Projects/README.md`.
3. Read `docs/README.md`, then `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, and task-specific docs.
4. For an existing project, read related code and tests before reading the project plan when the protocol says to orient first.

## Protocol Routing

- Start a new project: `Projects/protocols/01_initialize_project.md`.
- Read/use project plans: `Projects/protocols/02_plan_protocol.md`.
- Continue autonomous project work: `Projects/protocols/03a_continue_working.md` (the canonical TDD inner loop).
- Phase-aware execution with cumulative reviews: `Projects/protocols/03c_phase_aware_execution.md`. Used when the project's `plan.md` carries the `**Execution Protocol:** 03c-phase-aware-execution` marker. 03c wraps 03a as the inner loop and adds project-branch lifecycle, phase DAG eligibility, SHA-pinned cumulative reviews via `phase_complete.py`, and `phase_state.json` as authoritative state. Phase workers may write only their own phase checklist, code, tests, and `.agent_reports/proj-phase-session/{PROJ-ID}/{phase-id}/`; coordinator owns `plan.md`, `manifest.md`, `phase_state.json`, `findings_ledger.md`.
- Coordinate parallel project work: `Projects/protocols/03b_parallel_projects.md` only when the user explicitly asks for parallel/delegated agent work and the current Codex client supports it. 03b is inter-project parallelism; 03c handles intra-project phase parallelism inside a single 03b worker's worktree.
- Audit a project: `Projects/protocols/04_audit_project.md`. For 03c projects, this is the **rigorous final cumulative gate** (no merge to `main` until clean) — see the audit-readiness rules in `validate_audit_ready.py`.
- Close/archive a project: `Projects/protocols/05_close_project.md`.
- Revise a completed project: `Projects/protocols/06_revise_project.md`.
- Extract a phase into a new project: `Projects/protocols/07_extract_phase.md`.
- Follow automated loop behavior: `Projects/protocols/08_automated_loop_protocol.md`.
- Review a project plan against the codebase: `Projects/protocols/09_review_project.md`.
- Manage the refactor plan: `Projects/protocols/10_manage_refactor_plan.md`.
- Use handoff rules from `Projects/protocols/context_config.md`.

## Rules

- Keep `plan.md`, `design.md`, `decisions.md`, `manifest.md`, and phase checklists synchronized.
- Update `## Current State` before stopping project work.
- Log meaningful design decisions in `decisions.md`.
- Update `manifest.md` whenever project work touches a file not already listed.
- Run project scripts such as `Projects/scripts/project_status.py`, `current_task.py`, `validate_phase.py`, and audit/close validators when the protocol calls for them.
- Use strict TDD for implementation tasks.
- Run `python Tools/test_sharded/test_sharded.py` at the required project checkpoints.
