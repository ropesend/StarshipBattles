---
name: codex-starship-analysis-review
description: Run Starship Battles analysis and review workflows. Use for cyclomatic complexity audits, Vulture dead-code scans, architecture drift reviews, codebase sweeps, project reviews, skeptical audits, focused reviews, and review-to-project triage using Reviews/, Projects/protocols, docs/, radon, and vulture.
---

# Codex Starship Analysis Review

Use this skill for review, audit, and analysis tasks that may produce findings rather than immediate implementation.

## Required Context

1. Read `AGENTS.md` and `.agents/CODEX.md`.
2. Read `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, and `docs/03_CONVENTIONS.md`.
3. Read task-specific docs for the reviewed area.
4. For project reviews or audits, read the relevant `Projects/active_projects/PROJ-XX/` files and the protocol selected below.

## Workflows

### Complexity

- Use `radon` as described by the legacy Claude `analysis-complexity` skill.
- Check whether high-complexity functions violate documented project patterns.
- Report file, function, grade, reason, and recommended action.

### Dead Code

- Use `vulture game/ tests/ --min-confidence 100` for confirmed candidates, then lower confidence only when requested.
- Cross-reference docs before recommending deletion.
- Treat docs that still reference dead code as documentation discrepancies.
- Do not delete code unless the user asked for cleanup, and then use TDD plus relevant regression tests.

### Codebase Sweep

- Use `Reviews/prompts/Sweep - *.txt` and `Reviews/scripts/create_review.py` when running formal sweeps.
- Exclude generated output, archives, `.agent_reports/`, `.claude/worktrees/`, and `docs/_ignore/`.
- Organize findings by category: duplication, legacy holdovers, consistency, architecture drift, and test coverage.

### Project Review Or Audit

- Use `Projects/protocols/09_review_project.md` for interactive plan validation.
- Use `Projects/protocols/04_audit_project.md` for skeptical completion audits.
- If subagents are unavailable or not explicitly requested, run the review perspectives sequentially and state that limitation.

## Finding Rules

- Lead with concrete findings and file references.
- Distinguish confirmed issues from risks and questions.
- Do not treat stale docs, stale tests, or legacy compatibility code as acceptable without calling it out.
- Recommend project/ticket creation when a finding is too large for an immediate fix.
