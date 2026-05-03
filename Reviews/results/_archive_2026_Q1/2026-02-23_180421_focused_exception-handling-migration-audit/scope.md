# Focused Review: Exception Handling Migration Audit

## Question
What is the exact gap between the custom exception infrastructure (PROJ-45) and actual codebase adoption, and what specific changes are needed to achieve full migration?

## Classification
- **Type:** Migration Mapping / Impact Analysis
- **Scope:** All production code in `game/` (excludes tests/ and scripts/)
- **Prior Work:** PROJ-45 (exception hierarchy), Previous review findings IH-005, ERR-001 through ERR-012

## Agents (7 total)

| # | Role | Focus | Finding Prefix |
|---|------|-------|----------------|
| 1 | ValueError Migration Mapper | Every ValueError raise in game/ | EXC-V |
| 2 | RuntimeError & Generic Exception Mapper | RuntimeError, TypeError, Exception(), KeyError raises | EXC-G |
| 3 | Caller Impact Analyzer | except blocks that catch generic exceptions | EXC-C |
| 4 | Error Code Gap Analyzer | Missing error codes, coverage gaps | EXC-EC |
| 5 | Exception Catch Quality Auditor | All try/except blocks for quality | EXC-Q |
| 6 | Deserialization Validation Auditor | from_dict/to_dict methods | EXC-D |
| 7 | Test Impact Analyzer | Tests asserting generic exceptions | EXC-T |

## Success Criteria
- Complete catalog of every raise that needs migration
- Caller impact map for breaking changes
- Error code gap analysis with proposals
- Effort estimates per file and per module
- Output structured for direct conversion to PROJ-XX project phases

## Output Format
Per-finding format with: ID, file:line, function, current raise, proposed replacement, callers affected, breaking change flag, effort, priority.
