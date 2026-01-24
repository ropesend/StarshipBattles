# PROTOCOL 00: Review Core Infrastructure
**Role:** Code Review Coordinator

**Purpose:** This document defines the shared infrastructure, phases, agent roles, and templates used by all review protocols. Individual review protocols (01-08) extend this core with their specific focus areas.

---

## Common Phases (All Reviews Use These)

### Phase A: Scope Definition
**Goal:** Understand what to review and user priorities

1. **Gather Review Target**
   - Use AskUserQuestion to clarify:
     - Target scope (entire codebase, specific directories, specific modules)
     - Priority areas of concern
     - Known problem areas (optional)
     - Any constraints or exclusions

2. **Create Review Folder**
   ```bash
   python Reviews/scripts/create_review.py <type> "<description>"
   ```
   - Creates: `Reviews/results/YYYY-MM-DD_<type>_<description>/`
   - Initializes: `scope.md`, `findings/` directory
   - Updates: `Reviews/reviews_index.md`

3. **Document Scope**
   - Write scope definition to `scope.md` in the review folder

---

### Phase B: Agent Planning
**Goal:** Determine appropriate agent count and roles

1. **Calculate Recommended Agents**
   ```bash
   python Reviews/scripts/calculate_agents.py <scope_path> <review_type>
   ```

2. **Present Recommendation to User**
   - Show recommended agent count
   - Show recommended agent roles
   - Allow user to adjust up/down

3. **Finalize Agent Assignment**
   - Document selected agents in `scope.md`
   - Prepare agent prompts from templates

---

### Phase C: Review Swarm Launch
**Goal:** Deploy review agents in parallel

1. **Launch Agents**
   - Use Task tool with subagent_type=Explore
   - Launch all selected agents in parallel (single message, multiple tool calls)
   - Each agent writes findings to `findings/<agent_role>_report.md`

2. **Agent Prompt Template**
   Each agent receives:
   ```markdown
   # Code Review Agent: {ROLE_NAME}

   ## Your Focus
   {ROLE_FOCUS_DESCRIPTION}

   ## Review Scope
   {SCOPE_FROM_PHASE_A}

   ## Your Task
   1. Analyze the codebase through the lens of your focus area
   2. Identify issues, rate their severity, and suggest remediation
   3. Produce a structured report

   ## Output Format
   Write your findings to: Reviews/results/{REVIEW_FOLDER}/findings/{ROLE_NAME}_report.md

   Use this structure:

   ### Summary
   - Total issues found: [N]
   - Critical: [N], Major: [N], Minor: [N], Info: [N]

   ### Findings
   For each finding use:

   #### {SEVERITY}: {Brief Title}
   **ID:** {CATEGORY_CODE}-{NUMBER} (e.g., CQ-01, SEC-03)
   **Location:** `file/path.py:lines`
   **Issue:** [What's wrong]
   **Impact:** [Why it matters]
   **Recommendation:** [How to fix]
   **Effort:** [Simple/Medium/Complex]

   ### Top 5 Priority Issues
   [Ranked list of your most important findings]
   ```

---

### Phase D: Findings Compilation
**Goal:** Aggregate agent reports into unified review document

1. **Compile Findings**
   ```bash
   python Reviews/scripts/compile_findings.py Reviews/results/<review_folder>
   ```
   - Reads all `findings/*.md` files
   - Parses structured findings
   - De-duplicates by location
   - Calculates aggregate statistics
   - Generates `report.md`

2. **Manual Review**
   - Review compiled report for accuracy
   - Merge any duplicate findings
   - Verify severity classifications

---

### Phase E: User Summary
**Goal:** Present findings and discuss implications

1. **Present Executive Summary**
   - Total findings by severity
   - Top 10 priority issues
   - Patterns/themes identified

2. **Discuss with User**
   - Answer questions about findings
   - Clarify any confusing items
   - Discuss potential next steps

3. **Optional: Project Handoff**
   - If user wants to address findings as a project:
   - Use `review_to_project.py` or collaborate on project definition
   - Hand off to Projects/protocols/01_initialize_project.md

---

## Agent Role Catalog

Select agents based on review type and user priorities.

### Core Agents (Used by Multiple Review Types)

| Role | Focus | Finding Prefix | Default For |
|------|-------|----------------|-------------|
| Code Quality Analyst | Readability, complexity, SOLID, DRY violations | CQ | General, Migration |
| Test Coverage Analyst | Missing tests, weak assertions, coverage gaps | TC | Test Coverage, General |
| Architecture Reviewer | Coupling, layering, dependencies, design | AR | General, Migration |
| Security Auditor | Vulnerabilities, injection, auth, data exposure | SEC | Security, General |
| Performance Profiler | Algorithms, queries, memory, caching | PERF | Performance, General |
| Error Handling Auditor | Exceptions, logging, validation, recovery | ERR | General |
| Documentation Reviewer | Docstrings, comments, types, README | DOC | General |
| Dead Code Hunter | Unused imports, unreachable code, orphaned files | DC | General |

### Specialized Agents

| Role | Focus | Finding Prefix | Default For |
|------|-------|----------------|-------------|
| Test Behavior Analyst | Test patterns, assertion quality, test isolation | TB | Test Coverage |
| Module Specialist | Deep dive on specific module | MOD | Any (scaled) |
| Migration Analyst | Compatibility, conversion paths, breaking changes | MIG | Migration |
| Question Investigator | Focused research on specific topic | QI | Focused Question |
| Debt Cataloguer | Identify and categorize technical debt | TD | Technical Debt |
| Complexity Analyst | Measure and assess code complexity metrics | CX | Technical Debt |
| Pattern Cataloguer | Document patterns in use across codebase | PC | Consistency |
| Inconsistency Hunter | Find deviations from established patterns | IH | Consistency |

### Additional Specialized Agents (As Needed)

| Role | Focus | Finding Prefix | When to Use |
|------|-------|----------------|-------------|
| Input Validation Analyst | Input sanitization, boundary checks | IV | Security reviews |
| Auth/Access Reviewer | Authentication, authorization, permissions | AUTH | Security reviews |
| Data Flow Tracer | How data moves through the system | DF | Security, Migration |
| Algorithm Analyst | Algorithm efficiency, Big-O analysis | ALG | Performance reviews |
| Memory/Resource Analyst | Memory leaks, resource management | MEM | Performance reviews |
| Hot Path Identifier | Frequently executed code paths | HP | Performance reviews |
| Maintenance Cost Estimator | Ongoing burden of technical debt | MCE | Technical Debt |
| Refactoring Opportunity Finder | High-value refactoring targets | ROF | Technical Debt |
| Style Analyzer | Coding style consistency | SA | Consistency |
| Convention Enforcer | Naming and structural conventions | CE | Consistency |

---

## Dynamic Agent Scaling

### Recommended Agent Counts by Scope Size

| Scope Size | File Count | Agent Count | Notes |
|------------|------------|-------------|-------|
| Small | 1-20 files | 4-6 agents | Single module or focused area |
| Medium | 20-100 files | 6-10 agents | Feature area or subsystem |
| Large | 100-500 files | 10-15 agents | Major system or multiple subsystems |
| Comprehensive | 500+ files | 15-25+ agents | Full codebase or all tests |

### Calculation Factors
- File count in scope
- Line count in scope
- Number of priority areas selected by user
- Complexity indicators (imports, class count)
- Review type requirements

### User Adjustment
- User can increase for more thorough coverage
- User can decrease for faster, lighter review
- Agent role selection also presented for user input

---

## Severity Definitions

| Severity | Code | Definition | Typical Action |
|----------|------|------------|----------------|
| Critical | C | Security vulnerability, data loss risk, crashes in production | Fix immediately |
| Major | M | Significant bugs, performance issues, maintainability blockers | Address soon |
| Minor | m | Code smells, minor inefficiencies, style issues | Fix when convenient |
| Info | i | Observations, potential improvements, discussion points | Awareness only |

---

## Report Template Structure

### Executive Summary
```markdown
# Code Review Report: {REVIEW_FOLDER}

## Metadata
- **Date:** YYYY-MM-DD
- **Type:** {review_type}
- **Scope:** {scope_description}
- **Agents Used:** {list_of_agents}

## Executive Summary
- **Total Findings:** {N}
- **Critical:** {N} | **Major:** {N} | **Minor:** {N} | **Info:** {N}
- **Estimated Total Effort:** {Simple/Medium/Complex}
- **Overall Assessment:** {Brief health summary}
```

### Findings Sections
```markdown
## Priority Findings (Top 10)

### 1. {SEVERITY}: {Title}
**ID:** {PREFIX}-{NUM}
**Agent:** {Which agent found this}
**Location:** `file/path.py:lines`
**Issue:** {Description}
**Impact:** {Business/technical impact}
**Recommendation:** {Fix approach}
**Effort:** {Simple/Medium/Complex}

---

## Findings by Category

### {Category Name}
| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|
| {ID} | {Sev} | {Title} | `{path}` | {Effort} |

{Detailed descriptions follow}
```

### Appendices
```markdown
## Agent Reports
- [{Agent 1} Report](findings/{agent1}_report.md)
- [{Agent 2} Report](findings/{agent2}_report.md)

## Scope Details
{Full scope definition from Phase A}

## Statistics
{Detailed counts and metrics}
```

---

## Result Folder Naming Convention

Format: `YYYY-MM-DD_[review-type]_[brief-description]/`

### Type Codes
| Review Type | Code |
|-------------|------|
| General Review | general |
| Test Coverage Review | test-coverage |
| Focused Question Review | focused |
| Migration Review | migration |
| Security Review | security |
| Performance Review | performance |
| Technical Debt Review | tech-debt |
| Consistency Review | consistency |

### Examples
- `2026-01-23_general_game-logic-health/`
- `2026-01-23_test-coverage_fleet-module/`
- `2026-01-23_focused_error-handling-patterns/`
- `2026-01-23_migration_callback-to-async/`
- `2026-01-23_security_api-endpoints/`
- `2026-01-23_performance_combat-system/`
- `2026-01-23_tech-debt_strategy-layer/`
- `2026-01-23_consistency_naming-conventions/`

---

## Optional Project Handoff

### When to Consider a Project
- Critical or Major findings that need systematic remediation
- User expresses intent to address findings
- Findings reveal a larger systemic issue

### Handoff Process
1. **User Decides** - User indicates which findings to address
2. **Refine Scope** - Use AskUserQuestion to clarify project goals
3. **Generate Handoff Document**
   ```bash
   python Reviews/scripts/review_to_project.py <review_folder> --findings ID1,ID2,ID3
   ```
4. **Create Project** - User runs "Start Project" prompt with review context
5. **Protocol 01 Integration** - Review findings pre-populate exploration phase

### Not All Reviews Become Projects
- General health checks may be informational only
- Focused question reviews answer questions - done
- User may defer action to later
- Findings may not warrant a full project (quick fixes instead)

---

## Quick Reference

### Starting a Review
1. User runs appropriate review prompt
2. Load this core protocol + specific review protocol
3. Execute Phase A (Scope Definition)
4. Execute Phase B (Agent Planning)
5. Execute Phase C (Review Swarm Launch)
6. Execute Phase D (Findings Compilation)
7. Execute Phase E (User Summary)

### Key Scripts
| Script | Purpose |
|--------|---------|
| `create_review.py` | Initialize review folder and index |
| `calculate_agents.py` | Recommend agent count for scope |
| `compile_findings.py` | Aggregate agent reports into final report |
| `review_to_project.py` | Generate project handoff from findings |

### Key Files Per Review
| File | Purpose |
|------|---------|
| `scope.md` | Review scope definition and agent selection |
| `findings/*.md` | Individual agent reports |
| `report.md` | Final compiled review report |
