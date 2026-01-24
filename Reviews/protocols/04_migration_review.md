# PROTOCOL 04: Migration Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Analyze feasibility and planning for converting one system/pattern to another. Assess risks, map required changes, identify breaking changes, and recommend migration phases.

---

## Overview

The Migration Review helps plan significant architectural changes. It assesses what's involved in moving from a current state to a desired state, identifying risks and providing a roadmap.

**Best For:**
- Technology migrations (callbacks to async/await, framework changes)
- Pattern migrations (hardcoded to data-driven, singleton to DI)
- Architecture changes (monolith to modules, restructuring)
- API/interface changes
- Data model migrations

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Migration Analyst | Core analysis: compatibility, conversion paths, breaking changes |
| Architecture Reviewer | System design, module boundaries, coupling impact |
| Dependency Mapper | Import chains, ripple effects, circular dependencies |
| Test Impact Analyst | Which tests break, new tests needed |

### Recommended Agents
| Agent | Focus |
|-------|-------|
| Code Quality Analyst | Identify code that's hard to migrate |
| Data Flow Tracer | How data moves through affected areas |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Performance Profiler | Performance implications | Migration may affect performance |
| Security Auditor | Security implications | Migration touches security-sensitive code |
| Module Specialist (x N) | Deep dive on affected modules | Large-scale migration |

### Typical Agent Count: 6-10

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Migration Definition**
   - **FROM:** What is the current system/pattern?
   - **TO:** What is the target system/pattern?
   - Provide examples of each if helpful

2. **Migration Scope**
   - Entire codebase
   - Specific modules/directories
   - Specific feature area

3. **Constraints**
   - Must maintain backwards compatibility? (Yes/No/Partial)
   - Incremental migration possible? (Or big-bang only)
   - Any modules that MUST NOT be touched?
   - Timeline pressures?

4. **Risk Tolerance**
   - Conservative (minimize risk, accept more effort)
   - Balanced (reasonable risk for reasonable effort)
   - Aggressive (accept higher risk for faster completion)

5. **Known Challenges**
   - Any areas you know will be difficult?
   - Previous migration attempts?
   - Dependencies on external systems?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Migration Review

| Migration Scope | Recommended Configuration |
|-----------------|--------------------------|
| Single module | 6 agents: Core 4 + CQ + DFT |
| Feature area | 7-8 agents: Core 4 + CQ + DFT + 1-2 Module Specialists |
| Large system | 8-10 agents: Core 4 + CQ + DFT + 3-4 Module Specialists |
| Full codebase | 10+ agents: Scale Module Specialists to coverage |

### Present Migration Scope to User
```
Migration Analysis:
- FROM: {current_system}
- TO: {target_system}
- Affected files (estimated): {N}
- Affected modules: {list}

Recommended configuration:
- Agent count: {N}
- Core agents: Migration Analyst, Architecture Reviewer, Dependency Mapper, Test Impact Analyst
- Additional: {list}

Proceed with analysis?
```

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Migration Analyst
```markdown
# Migration Analysis Task

## Migration Definition
- **FROM:** {current_system}
- **TO:** {target_system}
- **Scope:** {affected_areas}

## Your Analysis Tasks

### 1. Current State Inventory
- List all instances of the current pattern/system
- Categorize by complexity (Simple/Medium/Complex to migrate)
- Note any variations in current implementation

### 2. Compatibility Analysis
For each instance:
- Can it be migrated directly?
- Are there blockers?
- What's the migration path?

### 3. Breaking Changes
- What public interfaces change?
- What behavior changes?
- What data format changes?

### 4. Migration Phases
Recommend phases:
- Phase 1: [lowest risk, foundational]
- Phase 2: [core migration]
- Phase 3: [edge cases, cleanup]

### 5. Rollback Strategy
- Can changes be rolled back?
- What's the point of no return?
- Recommended checkpoints?

## Report Structure
Provide findings in these categories:
- INVENTORY: What needs to migrate
- COMPATIBILITY: What migrates easily vs. with difficulty
- BREAKING: What will break
- PHASES: Recommended migration order
- RISKS: What could go wrong
- RECOMMENDATIONS: How to proceed
```

#### Architecture Reviewer (Migration Focus)
```markdown
# Architecture Analysis for Migration

## Focus Areas

### 1. Module Boundaries
- How does migration affect module boundaries?
- Will new dependencies be created?
- Will coupling increase or decrease?

### 2. Interface Changes
- What interfaces need to change?
- Can old and new coexist temporarily?
- Adapter/facade patterns needed?

### 3. Design Patterns
- Does target pattern fit the existing architecture?
- Any conflicts with current patterns?
- Opportunities to improve during migration?

### 4. Integration Points
- External system integrations affected?
- API changes required?
- Versioning considerations?
```

#### Dependency Mapper (Migration Focus)
```markdown
# Dependency Analysis for Migration

## Focus Areas

### 1. Dependency Graph
- Map all dependencies of code being migrated
- Identify what depends ON the code being migrated
- Note circular dependencies

### 2. Ripple Effect Analysis
For each piece being migrated:
- What else must change?
- Transitive dependencies?
- Cross-module impacts?

### 3. Migration Order
Based on dependencies:
- What MUST be migrated first?
- What can be migrated in parallel?
- What must wait until the end?

### 4. Risk Zones
- Areas where changes cascade widely
- Tightly coupled sections
- Import chain bottlenecks
```

#### Test Impact Analyst (Migration Focus)
```markdown
# Test Impact Analysis for Migration

## Focus Areas

### 1. Broken Tests
- Which tests will break due to migration?
- Why will they break? (interface change, behavior change, etc.)
- How to update them?

### 2. Coverage Gaps
- New code paths that need tests
- Behaviors that tests should verify post-migration
- Edge cases specific to the new pattern

### 3. Test Strategy
- Test migration order
- Temporary test scaffolding needed?
- Regression test suite for migration

### 4. Validation Approach
- How to verify migration success?
- Smoke tests, integration tests?
- Performance benchmarks?
```

---

## Phase D: Findings Compilation (Extended)

### Migration Report Structure

```markdown
# Migration Review: {FROM} to {TO}

## Executive Summary
- **Feasibility:** [Feasible / Feasible with Caveats / High Risk / Not Recommended]
- **Estimated Scope:** {N} files, {N} modules
- **Recommended Approach:** [Incremental / Big-bang / Hybrid]
- **Major Risks:** [Top 3 risks]

## Current State Inventory
| Category | Count | Complexity | Notes |
|----------|-------|------------|-------|
| {category} | {N} | {Simple/Medium/Complex} | {notes} |

## Breaking Changes
### Public Interface Changes
- {Change 1}: {impact}
- {Change 2}: {impact}

### Behavior Changes
- {Change 1}: {what changes}

### Data Format Changes
- {Change 1}: {migration needed}

## Dependency Impact
- **Direct dependencies affected:** {N}
- **Transitive impact:** {N} files
- **Critical paths:** {list}

## Recommended Migration Phases

### Phase 1: {Name} [Foundation]
**Objective:** {goal}
**Changes:**
- {change 1}
- {change 2}
**Risks:** {risks}
**Validation:** {how to verify}

### Phase 2: {Name} [Core Migration]
...

### Phase 3: {Name} [Cleanup]
...

## Test Impact
- **Tests that will break:** {N}
- **New tests needed:** {N}
- **Test migration strategy:** {summary}

## Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {risk} | High/Med/Low | High/Med/Low | {mitigation} |

## Recommendations
1. {Recommendation 1}
2. {Recommendation 2}
3. {Recommendation 3}

## Alternatives Considered
- {Alternative 1}: {why not recommended}

## Decision Points
Questions for stakeholder decision:
1. {Question 1}
2. {Question 2}
```

---

## Phase E: User Summary (Extended)

### Presenting Migration Analysis

1. **Lead with Feasibility Assessment**
   - Is this migration feasible?
   - What's the recommended approach?

2. **Show the Scope**
   - What needs to change?
   - How much effort is involved?

3. **Highlight Risks**
   - What could go wrong?
   - How to mitigate?

4. **Present Phased Approach**
   - Recommended phases
   - Order and dependencies

5. **Discuss Breaking Changes**
   - What will break?
   - How to handle?

6. **Answer Questions**
   - User may need clarification
   - May identify constraints not previously mentioned

---

## Special Considerations

### Backwards Compatibility Required
- Design adapter/facade patterns
- Plan coexistence period
- Define deprecation timeline

### Big-Bang Migration
- Requires comprehensive testing
- Plan rollback strategy
- Consider feature flags

### Incremental Migration
- Define stable intermediate states
- Both patterns may coexist temporarily
- More testing overhead but lower risk

### External Dependencies
- May constrain migration options
- Coordinate with external teams
- Version compatibility requirements

---

## Example Workflow

**Question:** "Migrate from callback-based events to async/await"

1. Coordinator gathers migration details
2. User specifies: game/events/ module, must maintain backwards compatibility temporarily
3. Agents: Migration Analyst, Architecture Reviewer, Dependency Mapper, Test Impact Analyst, Code Quality Analyst, Module Specialist
4. Review folder: `2026-01-23_migration_callback-to-async/`
5. Agents analyze current callback usage, async compatibility, dependencies
6. Findings:
   - 47 callback registrations across 12 modules
   - 8 can migrate directly, 39 need adapter patterns
   - 3 circular callback chains need redesign
7. Report recommends 4-phase approach:
   - Phase 1: Create async infrastructure
   - Phase 2: Add adapters for backwards compatibility
   - Phase 3: Migrate module by module
   - Phase 4: Remove adapters and legacy code
8. User decides to create project from findings

---

## Termination

After presenting analysis:
1. Confirm user understands the assessment
2. Address any questions or concerns
3. Offer options:
   - Create migration project from this analysis
   - Request deeper analysis of specific areas
   - Save analysis for future reference
4. Update `reviews_index.md`
5. If project created, this review becomes the project's design foundation
