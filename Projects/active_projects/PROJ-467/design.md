# PROJ-467: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-20_073330_docs-audit/`
- **Bundle counts:** Audit verified (this run): 40 | This bundle: 18 verified, 0 uncertain (resolved), 0 deferred | Project siblings: PROJ-468 (systems + guides), PROJ-469 (cross-doc consistency)
- **Doc-cluster coverage:** root agent docs (`AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`), architecture/core docs (`docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/README.md`), procedural protocol docs (`Projects/protocols/`, `Reviews/protocols/`).
- **Severity breakdown:** 2 CRITICAL / 4 MAJOR / 12 MINOR.

### Mislead Risk Notes
This bundle holds 2 CRITICAL items that actively mislead developers reading current docs. `AGENTS.md:52` — the canonical non-negotiable-rules file — declares "Python 3.14" as an absolute baseline; the real project minimum is 3.13+ (`pyproject.toml` `requires-python = ">=3.13"`), so an agent reading AGENTS.md first may assume a stricter requirement than the project actually targets. `docs/02_PATTERNS.md:819,824` cites two deleted files (`test_run_details.py` removed by PROJ-417, `race_setup_screen.py` removed by PROJ-416) as live pattern examples; a developer following those examples would look for code that no longer exists.

## Initial Analysis
[Findings from Phase A code review - what was discovered about the codebase]

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
