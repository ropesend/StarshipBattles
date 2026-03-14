# PROTOCOL 01: General Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Conduct a broad codebase health check to find the most obvious problems across multiple dimensions: code quality, architecture, testing, error handling, and dead code.

---

## Overview

The General Review is the "go-to" review type when you want a comprehensive health assessment of your codebase or a specific area. It deploys multiple agents with different perspectives to identify issues across various categories.

**Best For:**
- Regular codebase health checks
- Onboarding to an unfamiliar codebase
- Post-milestone quality assessment
- Identifying "low-hanging fruit" for improvement

---

## Default Agent Configuration

### Required Agents (Always Include)
| Agent | Focus |
|-------|-------|
| Code Quality Analyst | Readability, complexity, SOLID, DRY violations |
| Architecture Reviewer | Coupling, layering, dependencies, design |
| Test Coverage Analyst | Missing tests, coverage gaps |

### Recommended Agents (Include for Thorough Review)
| Agent | Focus |
|-------|-------|
| Error Handling Auditor | Exception handling, logging, validation |
| Documentation Consistency Reviewer | Code-docs discrepancies, stale docs, undocumented patterns |
| Dead Code Hunter | Unused imports, unreachable code, orphaned files |

### Optional Agents (Based on Scope/Priorities)
| Agent | Focus | Include When |
|-------|-------|--------------|
| Documentation Reviewer | Docstrings, comments, types | Documentation is a priority |
| Security Auditor | Basic security issues | Security is a concern |
| Performance Profiler | Obvious performance issues | Performance is a concern |

### Typical Agent Count: 5-8

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - Entire codebase
   - Specific directory/module (specify path)
   - Recent changes (since date/commit)

2. **Priority Focus** (optional, can select multiple)
   - Code quality and readability
   - Architecture and design
   - Test coverage
   - Error handling
   - Dead code cleanup
   - Documentation
   - Security basics
   - Performance basics

3. **Known Problem Areas**
   - Any specific files or modules suspected to have issues?
   - Any recent bugs that might indicate systemic problems?

4. **Exclusions**
   - Any areas to explicitly exclude from review?
   - Third-party code, generated files, etc.?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for General Review

| Scope Size | Recommended Agents |
|------------|-------------------|
| Small (1-20 files) | 5 agents: CQ, AR, TC, ERR, DC |
| Medium (20-100 files) | 6-7 agents: Add DOC or SEC based on priority |
| Large (100-500 files) | 7-8 agents: Full recommended set |
| Comprehensive (500+ files) | 8+ agents: Add Module Specialists for key areas |

### Present to User
```
Based on scope analysis:
- Files in scope: {N}
- Lines of code: {N}

Recommended configuration:
- Agent count: {N}
- Agents: {list}

Would you like to:
[ ] Use recommended configuration
[ ] Add more agents for deeper analysis
[ ] Use fewer agents for faster review
[ ] Customize agent selection
```

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Code Quality Analyst
```markdown
Focus on:
- Long methods (>50 lines)
- Deep nesting (>3 levels)
- Magic numbers/strings
- Copy-paste code (DRY violations)
- Poor naming (single letters, misleading names)
- SOLID principle violations
- God classes/methods
- Complex conditionals
- Unused parameters
```

#### Architecture Reviewer
```markdown
Focus on:
- Circular dependencies
- Layer violations (e.g., UI calling DB directly)
- Tight coupling between modules
- Missing abstractions
- Inappropriate intimacy between classes
- Feature envy
- Shotgun surgery indicators
- Module boundary violations
```

#### Test Coverage Analyst
```markdown
Focus on:
- Untested public methods
- Missing edge case tests
- Critical paths without tests
- Low coverage areas
- Integration test gaps
```

#### Error Handling Auditor
```markdown
Focus on:
- Bare except clauses
- Swallowed exceptions
- Missing error messages
- No logging on failures
- Incomplete cleanup in finally
- User-facing stack traces
- Missing input validation
```

#### Dead Code Hunter
```markdown
Focus on:
- Unused imports
- Unreachable code
- Commented-out code
- Deprecated method usage
- Orphaned files
- Unused variables/parameters
- Dead feature flags
```

---

## Phase E: User Summary (Extended)

### General Review Report Structure

Present findings organized by category:

1. **Overall Health Score**
   - Subjective assessment: Healthy / Needs Attention / Problematic
   - Rationale for score

2. **Top Issues by Impact**
   - Critical issues first
   - Focus on items with highest business/technical impact

3. **Quick Wins**
   - Low-effort, high-impact fixes
   - Dead code removal opportunities
   - Simple refactoring wins

4. **Systemic Issues**
   - Patterns of problems (not just individual issues)
   - Root causes if identifiable

5. **Recommendations**
   - Immediate actions (Critical/Major)
   - Short-term improvements
   - Long-term considerations

---

## Example Workflow

1. User runs "General Review" prompt
2. Coordinator asks scope questions
3. User: "Review the game/strategy/ folder, focus on code quality and architecture"
4. Coordinator creates review folder: `2026-01-23_general_strategy-module/`
5. Coordinator recommends 6 agents based on scope
6. User confirms agent selection
7. 6 agents launch in parallel, write to `findings/`
8. Coordinator compiles `report.md`
9. Coordinator presents summary:
   - "Found 3 Critical, 8 Major, 15 Minor issues"
   - "Top concern: Circular dependency between strategy and combat modules"
   - "Quick wins: 12 unused imports can be removed"
10. User discusses findings, decides next steps

---

## Termination

After presenting findings:
1. Update `reviews_index.md` with review status
2. Ask user if they want to:
   - Create a project from findings
   - Save review for reference
   - Discuss specific findings further
3. Archive review or initiate project handoff as requested
