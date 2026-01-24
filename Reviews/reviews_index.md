# Reviews Index

This index tracks all code reviews conducted on the Starship Battles codebase.

## Status Legend
- **In Progress** - Review currently being conducted
- **Completed** - Review finished, findings documented
- **Archived** - Review findings addressed or superseded
- **Led to Project** - Review resulted in a PROJ-XX project

---

## Active Reviews
| Date | Type | Description | Status | Link |
|------|------|-------------|--------|------|
| 2026-01-23 | Test Coverage Review | full-codebase-coverage-gaps | In Progress | [2026-01-23_test-coverage_full-codebase-coverage-gaps](results/2026-01-23_test-coverage_full-codebase-coverage-gaps/) |

---

## Completed Reviews
| Date | Type | Description | Key Findings | Link |
|------|------|-------------|--------------|------|

---

## Reviews Leading to Projects
| Review | Project | Description |
|--------|---------|-------------|

---

## Review Types Available

| Type | Protocol | Description |
|------|----------|-------------|
| General | [01_general_review.md](protocols/01_general_review.md) | Broad codebase health check |
| Test Coverage | [02_test_coverage_review.md](protocols/02_test_coverage_review.md) | Test completeness and quality |
| Focused Question | [03_focused_question_review.md](protocols/03_focused_question_review.md) | Answer specific questions |
| Migration | [04_migration_review.md](protocols/04_migration_review.md) | System conversion analysis |
| Security | [05_security_review.md](protocols/05_security_review.md) | Security audit |
| Performance | [06_performance_review.md](protocols/06_performance_review.md) | Performance analysis |
| Technical Debt | [07_technical_debt_review.md](protocols/07_technical_debt_review.md) | Debt assessment |
| Consistency | [08_consistency_review.md](protocols/08_consistency_review.md) | Pattern consistency |

---

## Quick Start

1. Choose a review type from the prompts in `Reviews/Prompts/`
2. Run the prompt to start the review
3. Results will be saved to `Reviews/results/<timestamp>_<type>_<description>/`

### Scripts Available

| Script | Purpose |
|--------|---------|
| `create_review.py` | Create new review folder |
| `calculate_agents.py` | Recommend agent count for scope |
| `compile_findings.py` | Generate report from agent findings |
| `review_to_project.py` | Create project handoff from findings |

---

*Next Review ID: Determined by timestamp*
