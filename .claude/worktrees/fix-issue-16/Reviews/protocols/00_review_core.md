# PROTOCOL 00: Review Core Infrastructure
**Role:** Code Review Coordinator

**Purpose:** This document defines the shared infrastructure, phases, agent roles, and templates used by all review protocols. Individual review protocols (01-08) extend this core with their specific focus areas.

---

## Common Phases (All Reviews Use These)

### Phase A: Scope Definition
**Goal:** Understand what to review and user priorities

1. **Read Documentation Reference (MANDATORY)**
   - Read `docs/README.md` to understand the documentation structure
   - Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
   - Read any `docs/systems/` or `docs/guides/` files relevant to the review scope
   - These are the authoritative references for how the codebase should be structured. All review agents should compare code against these documented standards.

2. **Gather Review Target**
   - Use AskUserQuestion to clarify:
     - Target scope (entire codebase, specific directories, specific modules)
     - Priority areas of concern
     - Known problem areas (optional)
     - Any constraints or exclusions

3. **Create Review Folder**
   ```bash
   python Reviews/scripts/create_review.py <type> "<description>"
   ```
   - Creates: `Reviews/results/YYYY-MM-DD_<type>_<description>/`
   - Initializes: `scope.md`, `findings/` directory
   - Updates: `Reviews/reviews_index.md`

4. **Document Scope**
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
   - Use Task tool with **subagent_type="general-purpose"** (NOT "Explore" — Explore agents cannot write files)
   - Launch all selected agents in parallel (single message, multiple tool calls)
   - Each agent writes findings to `findings/<agent_role>_report.md`
   - The agent prompt MUST explicitly instruct the agent to use the Write tool to persist its report

**IMPORTANT - Agent Launch Recommendations:**
- **Synchronous launches (default):** For reviews with < 6 agents, launch synchronously (without `run_in_background`) to ensure outputs are captured reliably.
- **Background launches:** Only use `run_in_background=true` for large reviews (8+ agents) when parallel execution is critical. Always verify outputs afterward.
- **Verification:** After agents complete, check that all output files exist and contain content before proceeding to Phase D.
- **If agents fail to write files:** This typically means they were launched with `subagent_type=Explore` instead of `general-purpose`. Re-launch with the correct agent type.

2. **Agent Prompt Template**
   Each agent receives:
   ```markdown
   # Code Review Agent: {ROLE_NAME}

   ## Your Focus
   {ROLE_FOCUS_DESCRIPTION}

   ## Documentation Reference (MANDATORY)
   The `docs/` directory is the authoritative source for architecture, patterns, and conventions.
   Before analyzing code, read the relevant docs:
   - `docs/01_ARCHITECTURE.md` — Layer structure and dependency rules
   - `docs/02_PATTERNS.md` — Established design patterns
   - `docs/03_CONVENTIONS.md` — Naming and coding conventions
   - Any relevant `docs/systems/` or `docs/guides/` files for the area being reviewed

   When you find code that contradicts `docs/`, flag it as a finding. Use the `DOC` prefix
   for documentation-specific discrepancies (e.g., DOC-01). If the documentation itself
   appears wrong (code universally disagrees), note it as an INFO-level finding.

   ## Review Scope
   {SCOPE_FROM_PHASE_A}

   ## Your Task
   1. Analyze the codebase through the lens of your focus area
   2. **Compare code against documented patterns in `docs/` — flag discrepancies**
   3. Identify issues, rate their severity, and suggest remediation
   4. Produce a structured report
   5. **CRITICAL: Use the Write tool to save your report to the output file below. Your analysis is lost if you don't write the file.**

   ## Output Format
   You MUST use the Write tool to save your report to: Reviews/results/{REVIEW_FOLDER}/findings/{ROLE_NAME}_report.md

   Use this structure:

   ### Summary
   - Total issues found: [N]
   - Critical: [N], Major: [N], Minor: [N], Info: [N]

   ### Findings
   For each finding use EXACTLY this heading format — the automated parser
   depends on it:

   #### {SEVERITY}: {Brief Title}
   **ID:** {CATEGORY_CODE}-{NUMBER} (e.g., CQ-01, SEC-03)
   **Location:** `file/path.py:lines`
   **Issue:** [What's wrong]
   **Impact:** [Why it matters]
   **Recommendation:** [How to fix]
   **Effort:** [Simple/Medium/Complex]

   **HEADING FORMAT RULES (the report parser will fail if these are violated):**
   - The heading MUST be exactly `####` (h4) — not `###` or `#####`
   - The heading MUST start with the severity word: `#### CRITICAL:`, `#### MAJOR:`, `#### MINOR:`, or `#### INFO:`
   - Do NOT put the finding ID in the heading — the ID goes on the **ID:** line below
   - Valid severity words: CRITICAL, MAJOR, MINOR, INFO
   - Example of CORRECT format:
     ```
     #### MAJOR: Duplicate Protocol Definitions
     **ID:** AR-001
     **Location:** `game/core/protocols.py:601`
     ```
   - Example of WRONG format (DO NOT USE):
     ```
     ### MAJOR: Title              ← wrong: ### instead of ####
     #### AR-001: MAJOR - Title    ← wrong: ID before severity
     ### CE-01 -- CRITICAL: Title  ← wrong: both ### and ID prefix
     ```

   ### Top 5 Priority Issues
   [Ranked list of your most important findings]
   ```

---

### Phase D: Findings Compilation
**Goal:** Aggregate agent reports into unified review document

1. **Verify Agent Outputs (Critical Step)**
   Before compiling, verify all expected agent outputs exist:
   - Check that each expected agent has a file in `findings/`
   - Verify files are non-empty (> 100 bytes minimum)
   - The compile script now warns about empty/missing outputs automatically

   **If agents produced empty outputs:**
   - This typically means agents launched with `run_in_background=true` failed to persist their work
   - Re-run the affected agents synchronously (without background flag)
   - Wait for agents to complete before proceeding

2. **Compile Findings**
   ```bash
   python Reviews/scripts/compile_findings.py Reviews/results/<review_folder>
   ```
   - Reads all `findings/*.md` files
   - Parses structured findings
   - De-duplicates by location
   - Calculates aggregate statistics
   - Generates `report.md`
   - **New:** Warns about empty or missing agent files

3. **Manual Review**
   - Review compiled report for accuracy
   - Merge any duplicate findings
   - Verify severity classifications

---

### Phase D.5: Findings Verification
**Goal:** Skeptically validate all findings against actual source code before presenting to user

This phase is **mandatory** for all reviews. Validator agents independently verify each finding by reading the actual source code, checking whether the issue exists as described, and rendering a verdict.

1. **Extract Findings for Validation**
   ```bash
   python Reviews/scripts/validate_findings.py <review_folder> --format markdown
   ```
   This outputs all findings in a format suitable for validator agents.

2. **Determine Validator Count**
   | Finding Count | Validators |
   |---------------|------------|
   | 1-15          | 2          |
   | 16-40         | 3          |
   | 41+           | 4          |

   Split findings evenly across validators. Each validator gets a numbered slice.

3. **Launch Validator Agents**
   - Use Task tool with **subagent_type="general-purpose"** (validators must write files)
   - Each validator writes to: `findings/validation/validator_N_report.md`
   - Use the **Validator Prompt Template** below

4. **Apply Verdicts**
   ```bash
   python Reviews/scripts/filter_validated_findings.py <review_folder>
   ```
   - Saves original report as `report_unvalidated.md`
   - Writes filtered `report.md` with only verified findings
   - Writes `findings/validation/validation_summary.json`
   - Warnings are emitted for shards with >90% rejection rate (validator may be too aggressive)

5. **Validator Prompt Template**
   Each validator receives:
   ```markdown
   # Finding Validator {N}

   ## Your Mindset
   Be **skeptical but fair**. Assume every finding is wrong until you verify it yourself.
   Your goal is to catch false positives, not to reject everything. A well-described issue
   that genuinely exists in the code should be CONFIRMED.

   ## Your Assigned Findings
   {FINDINGS_SLICE — subset of findings assigned to this validator}

   ## Validation Methodology

   For EACH finding, follow these steps:

   ### Step 1: Read the Source Code
   - Open the file at the **Location** specified in the finding
   - Read the relevant lines and surrounding context
   - If the file does not exist → automatically **REJECTED**
   - If the location is "Unknown" or empty → automatically **REJECTED**

   ### Step 2: Verify the Claim
   - Does the code at this location actually exhibit the described issue?
   - Is the description accurate?
   - Is the "Impact" statement realistic or exaggerated?
   - Is the "Recommendation" feasible and correct?
   - **For documentation findings (DOC/DOCC prefix):** Read BOTH the referenced `docs/` file AND the code. Verify the discrepancy actually exists.

   ### Step 3: Check If Already Fixed
   - Look for signs the issue was addressed (refactoring, TODO comments, recent changes)
   - If clearly fixed → **REJECTED** with explanation

   ### Step 4: Assess Severity
   - Is the assigned severity appropriate?
   - Severity inflation is common — downgrade liberally if warranted
   - Critical = genuine architectural violation, security issue, or crash risk
   - Major = real bug or significant maintainability problem
   - Minor = code smell, low-risk issue
   - Info = observation, not actionable

   ### Step 5: Check for Common False Positive Patterns
   - TYPE_CHECKING imports flagged as Critical/Major (should be Minor at most)
   - Findings about classes with active decomposition projects in Projects/active_projects/
   - Duplicate findings (same issue reported by multiple agents)
   - Info-level observations that are not actionable issues
   - Style/formatting issues with no functional impact

   ### Step 6: Render Verdict
   One of:
   - **CONFIRMED** — Issue exists as described at stated severity
   - **DOWNGRADED({new_severity})** — Issue exists but severity is wrong
     (e.g., `DOWNGRADED(Minor)` for an inflated Critical)
   - **REJECTED** — Issue does not exist, is already fixed, is a duplicate,
     or cannot be verified

   When in doubt: prefer DOWNGRADED over REJECTED (keep real issues, even if overrated).

   ## Output Format
   You MUST use the Write tool to save your report to:
   Reviews/results/{REVIEW_FOLDER}/findings/validation/validator_{N}_report.md

   Use EXACTLY this structure:

   # Validation Report: Validator {N}

   ## Summary
   - **Findings Reviewed:** [N]
   - **Confirmed:** [N]
   - **Downgraded:** [N]
   - **Rejected:** [N]
   - **Rejection Rate:** [percentage]%

   ## Verdicts

   #### Finding: {FINDING_ID}
   **Original Severity:** {severity}
   **Verdict:** CONFIRMED
   **Reason:** Verified — [brief explanation of what you found in the code].

   #### Finding: {FINDING_ID}
   **Original Severity:** Critical
   **Verdict:** DOWNGRADED(Minor)
   **New Severity:** Minor
   **Reason:** [1-2 sentence explanation].

   #### Finding: {FINDING_ID}
   **Original Severity:** Major
   **Verdict:** REJECTED
   **Reason:** [1-2 sentence explanation].

   ## Constraints
   - You MUST review EVERY finding assigned to you
   - You MUST read the actual source code — do not rely on the finding description alone
   - Keep reasons concise (1-2 sentences)
   - Do NOT modify any source files — this is read-only validation
   - Spend more time on Critical/Major findings; Info findings can be validated quickly
   ```

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
| Documentation Consistency Reviewer | Code-docs discrepancies, stale docs, undocumented patterns | DOCC | General, Consistency, Migration |
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

### Documentation Discrepancies
```markdown
## Documentation Discrepancies

Any findings where code contradicts `docs/` documentation:

| Finding ID | docs/ File | What docs say | What code does | Recommendation |
|------------|-----------|---------------|----------------|----------------|
| {ID} | `docs/{file}.md` | {documented behavior} | {actual behavior} | Update docs / Fix code |
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

## Project Handoff (Review → Project)

### When to Consider a Project
- Critical or Major findings that need systematic remediation
- User expresses intent to address findings
- Findings reveal a larger systemic issue

### Automated Project Creation (Recommended)

The `review_to_project.py` script now automatically creates the full project structure:

```bash
# Verify parsing before creating (recommended first step)
python Reviews/scripts/review_to_project.py <review_folder> --dry-run

# Create project with all Critical and Major findings (default)
python Reviews/scripts/review_to_project.py <review_folder>

# Create project with custom title
python Reviews/scripts/review_to_project.py <review_folder> --title "Security Fixes"

# Create project with specific findings only
python Reviews/scripts/review_to_project.py <review_folder> --findings SEC-01,SEC-02,IV-01
```

**IMPORTANT - Always use `--dry-run` first:**
The `--dry-run` flag shows what would be parsed without creating files. This helps verify:
- All expected findings are being parsed
- Severities are correctly assigned
- The right number of findings will be included

**What this creates:**
- `Projects/active_projects/PROJ-XX/` directory
- `plan.md` - Main project document with overview, goals, scope
- `design.md` - Pre-populated with review findings summary
- `decisions.md` - Initialized with project creation decision
- `phase_N_checklist.md` - One per severity level (Critical → Phase 1, Major → Phase 2, etc.)
- `findings/` - Directory for additional agent reports
- Updates `projects_index.md` automatically

### Legacy Handoff-Only Mode

To generate a handoff document without creating the project (for manual review first):

```bash
python Reviews/scripts/review_to_project.py <review_folder> --no-create-project
```

This creates `project_handoff.md` in the review folder, which can then be used with
the "Start Project" prompt.

### Handoff Workflow

1. **Review Completes** - `report.md` generated with findings
2. **User Decides** - Which findings to address (default: all Critical + Major)
3. **Run Script** - `review_to_project.py` creates project structure
4. **Refine Plan** - User/agent reviews generated plan, adds detail to tasks
5. **Continue** - Use "Continue Project" prompt to begin implementation

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
7. Execute Phase D.5 (Findings Verification)
8. Execute Phase E (User Summary)

### Key Scripts
| Script | Purpose |
|--------|---------|
| `create_review.py` | Initialize review folder and index |
| `calculate_agents.py` | Recommend agent count for scope |
| `compile_findings.py` | Aggregate agent reports into final report |
| `validate_findings.py` | Extract findings for validation agents |
| `filter_validated_findings.py` | Apply validation verdicts to filter report |
| `review_to_project.py` | **Create full project structure from findings** (or handoff doc with `--no-create-project`) |

### Key Files Per Review
| File | Purpose |
|------|---------|
| `scope.md` | Review scope definition and agent selection |
| `findings/*.md` | Individual agent reports |
| `findings/validation/*.md` | Validator reports with verdicts |
| `findings/validation/validation_summary.json` | Machine-readable validation stats |
| `report.md` | Final compiled review report (post-validation) |
| `report_unvalidated.md` | Original report before validation filtering |
