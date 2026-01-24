# PROTOCOL 07: Technical Debt Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Quantify and prioritize accumulated technical debt. Identify areas where shortcuts, quick fixes, or outdated patterns are creating ongoing maintenance burden and slowing development.

---

## Overview

The Technical Debt Review treats code quality issues as "debt" with ongoing "interest" - the extra effort required for every future change. It helps prioritize where to invest refactoring effort for the best return.

**Best For:**
- Planning refactoring sprints
- Understanding maintenance burden
- Prioritizing tech debt payoff
- Making the case for refactoring time
- Assessing legacy code quality
- Planning modernization efforts

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Debt Cataloguer | Identify and categorize all technical debt |
| Complexity Analyst | Measure code complexity and its implications |
| Maintenance Cost Estimator | Estimate ongoing burden of each debt item |

### Recommended Agents
| Agent | Focus |
|-------|-------|
| Refactoring Opportunity Finder | Identify high-value refactoring targets |
| Code Quality Analyst | Detailed code quality assessment |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Architecture Reviewer | Architectural debt | System-level concerns |
| Test Coverage Analyst | Testing debt | Test quality is a concern |
| Module Specialist (x N) | Deep dive on specific modules | Large codebases |

### Typical Agent Count: 5-8

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - Entire codebase
   - Specific module/area
   - Areas with most frequent changes
   - Areas known to be problematic

2. **Debt Categories of Interest**
   - Code complexity (hard to understand/modify)
   - Outdated patterns (legacy approaches)
   - Missing abstractions (copy-paste code)
   - Test debt (missing/weak tests)
   - Documentation debt (missing/outdated docs)
   - Architectural debt (design issues)
   - All categories

3. **Business Context**
   - Which areas are most important to keep working?
   - Which areas see most frequent changes?
   - Any planned major features in these areas?

4. **Effort Constraints**
   - How much refactoring effort is feasible?
   - Any areas that can't be touched?
   - Appetite for large vs. incremental changes?

5. **Known Pain Points**
   - Areas developers avoid touching?
   - Features that always have bugs?
   - Code that's hard to onboard to?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Technical Debt Review

| Scope | Recommended Configuration |
|-------|--------------------------|
| Single module | 5 agents: Core 3 + ROF + CQ |
| Feature area | 6 agents: Core 3 + ROF + CQ + Test Coverage |
| System-wide | 7-8 agents: Add Architecture + specialists |
| Full codebase | 8+ agents: Scale with Module Specialists |

### Priority Area Identification
Focus on areas with:
- Highest change frequency (from git history)
- Most bug fixes (from git history)
- Developer complaints
- Longest development times

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Debt Cataloguer (Primary)
```markdown
# Technical Debt Cataloguing Task

## Scope
{SCOPE_FROM_PHASE_A}

## Debt Categories to Identify

### 1. Code Debt
- Duplicated code (copy-paste)
- Magic numbers/strings
- Long methods (>50 lines)
- Deep nesting (>3 levels)
- Poor naming
- Dead code
- Commented-out code
- TODO/FIXME/HACK comments

### 2. Design Debt
- Missing abstractions
- God classes/modules
- Tight coupling
- Missing interfaces
- Inappropriate intimacy
- Feature envy
- Shotgun surgery indicators

### 3. Architectural Debt
- Layer violations
- Circular dependencies
- Missing service boundaries
- Monolithic components that should be split
- Outdated architectural patterns

### 4. Test Debt
- Missing tests for critical code
- Weak/brittle tests
- Tests that are hard to maintain
- Missing integration tests

### 5. Documentation Debt
- Missing/outdated documentation
- Misleading comments
- Missing API documentation
- Outdated README

### 6. Infrastructure Debt
- Outdated dependencies
- Missing build automation
- Manual deployment steps
- Missing CI/CD

## For Each Debt Item
Catalog:
- What: Description of the debt
- Where: File(s) and lines affected
- Category: Which type of debt
- Size: Small/Medium/Large
- Impact: How it affects development
- Origin: Why it exists (if determinable)
```

#### Complexity Analyst
```markdown
# Code Complexity Analysis

## Focus Areas

### 1. Cyclomatic Complexity
Identify:
- Methods with high cyclomatic complexity (>10)
- Classes with many branches
- Deeply nested conditionals
- Complex boolean expressions

### 2. Cognitive Complexity
Identify:
- Code that's hard to understand at a glance
- Non-linear control flow
- Many levels of abstraction in one place
- Implicit behavior

### 3. Coupling Metrics
Identify:
- Classes with many dependencies
- Methods with many parameters
- Modules that know too much about each other
- Central bottleneck classes

### 4. Change Impact
Identify:
- Changes that require updates in many places
- Tightly connected components
- Missing encapsulation

## Complexity Ratings
For each complex area:
- Complexity score (if measurable)
- Why it's complex
- Impact on maintenance
- Simplification opportunity
```

#### Maintenance Cost Estimator
```markdown
# Maintenance Cost Analysis

## Focus Areas

### 1. "Interest" Calculation
For each debt item, estimate ongoing cost:
- Time added to understand code
- Time added to make changes
- Risk of introducing bugs
- Testing overhead

### 2. Change Frequency Impact
Cross-reference with change patterns:
- How often does this code change?
- How much debt is in high-change areas?
- Interest rate = debt × change frequency

### 3. Developer Friction
Estimate:
- How many developers touch this code?
- How much time is lost to the debt?
- Onboarding overhead

### 4. Risk Assessment
Estimate:
- Bug risk from debt
- Incident risk
- Knowledge loss risk (bus factor)

## Output: Interest Payment Table
| Debt Item | Location | Interest Rate | Monthly Cost Est. |
|-----------|----------|---------------|-------------------|
```

#### Refactoring Opportunity Finder
```markdown
# Refactoring Opportunity Analysis

## Focus Areas

### 1. High-Value Targets
Identify refactorings that:
- Pay off debt in high-traffic areas
- Reduce multiple debt items at once
- Enable future development
- Reduce risk significantly

### 2. Quick Wins
Identify:
- Simple refactorings with good payoff
- Low-risk changes
- Single-file improvements
- Extract method/class opportunities

### 3. Strategic Refactorings
Identify:
- Larger refactorings with high payoff
- Architectural improvements
- Pattern introductions
- Module restructuring

### 4. Dependencies
For each refactoring:
- What must happen first?
- What does this enable?
- Order of operations

## Prioritized List
| Priority | Refactoring | Effort | Payoff | Risk |
|----------|-------------|--------|--------|------|
```

---

## Phase D: Findings Compilation (Extended)

### Technical Debt Report Structure

```markdown
# Technical Debt Review Report

## Executive Summary
- **Overall Debt Level:** [Low / Moderate / High / Critical]
- **Total Debt Items:** {N}
- **Estimated Monthly Interest:** {time estimate}
- **Top Recommendation:** {summary}

## Debt Overview by Category
| Category | Items | High Impact | Est. Interest |
|----------|-------|-------------|---------------|
| Code | {N} | {N} | {time} |
| Design | {N} | {N} | {time} |
| Architecture | {N} | {N} | {time} |
| Test | {N} | {N} | {time} |
| Documentation | {N} | {N} | {time} |

## Debt Heat Map
[By module/area - where is debt concentrated?]

| Module | Debt Score | Change Freq | Priority |
|--------|------------|-------------|----------|

## High-Interest Debt (Pay These First)

### TD-01: {Title}
**Category:** {category}
**Location:** `file:lines`
**Debt Size:** {Small/Medium/Large}
**Change Frequency:** {High/Medium/Low}
**Interest Rate:** {High/Medium/Low}
**Description:** {what the debt is}
**Cost:** {how it impacts development}
**Payoff Approach:** {how to address it}
**Effort:** {Simple/Medium/Complex}

## Refactoring Recommendations

### Priority 1: Quick Wins (High ROI, Low Effort)
| # | Refactoring | Location | Effort | Payoff |
|---|-------------|----------|--------|--------|
| 1 | {refactoring} | {loc} | {effort} | {payoff} |

### Priority 2: Strategic Improvements (High ROI, Higher Effort)
| # | Refactoring | Location | Effort | Payoff |
|---|-------------|----------|--------|--------|

### Priority 3: Long-term Architecture (Foundational)
| # | Refactoring | Location | Effort | Payoff |
|---|-------------|----------|--------|--------|

## Debt Payoff Roadmap
If addressing debt systematically:

### Sprint 1: Quick Wins
- {item 1}
- {item 2}
Expected outcome: {benefit}

### Sprint 2-3: Core Improvements
- {item 1}
- {item 2}
Expected outcome: {benefit}

### Ongoing: Maintenance
- {practices to prevent new debt}

## Technical Debt Prevention
Recommendations to avoid new debt:
1. {recommendation}
2. {recommendation}
```

---

## Phase E: User Summary (Extended)

### Presenting Technical Debt Findings

1. **Lead with Business Impact**
   - How much time is debt costing?
   - What's being slowed down?

2. **Show the Heat Map**
   - Where is debt concentrated?
   - What areas need attention?

3. **Present the Investment Case**
   - Cost of paying off debt vs. interest cost
   - ROI of refactoring

4. **Prioritize Clearly**
   - What to fix first and why
   - Quick wins vs. strategic investments

5. **Provide a Roadmap**
   - Phased approach
   - Dependencies between items

---

## Special Considerations

### Not All Debt is Bad
- Some debt is intentional and acceptable
- Focus on debt with high interest
- Document accepted debt

### Context Matters
- Debt in stable, rarely-changed code is less urgent
- Debt in rapidly-evolving areas compounds quickly
- Consider business priorities

### Measurement Challenges
- Debt is often subjective
- Be clear about assumptions
- Use relative, not absolute measures

### Prevention
- Include recommendations for preventing new debt
- Code review practices
- Definition of done updates

---

## Example Workflow

1. User runs "Technical Debt Review" prompt
2. Coordinator asks scope questions
3. User: "Review the strategy layer, we're about to add major features there"
4. Review folder: `2026-01-23_tech-debt_strategy-layer/`
5. Agents: Debt Cataloguer, Complexity Analyst, Maintenance Cost Estimator, Refactoring Opportunity Finder, Code Quality Analyst
6. Agents analyze strategy code
7. Findings:
   - 23 debt items catalogued
   - 5 high-interest items in frequently-changed code
   - Top issue: God class handling all strategy calculations
   - Quick wins: 8 simple extractions would reduce complexity
8. Roadmap: 2-sprint plan to address high-interest debt before feature work
9. User creates project for sprint 1 debt payoff

---

## Termination

After presenting findings:
1. Discuss prioritization with user
2. Align on acceptable debt vs. must-fix
3. Offer options:
   - Create debt payoff project (phased)
   - Export debt inventory for tracking
   - Create specific refactoring project
4. Update `reviews_index.md`
