# PROTOCOL 02: Test Coverage Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Analyze test completeness and quality across the codebase or a specific module. Identify coverage gaps, weak tests, and untested critical paths.

---

## Overview

The Test Coverage Review focuses specifically on the testing dimension of code quality. It examines not just whether tests exist, but whether they're effective, well-structured, and cover the right scenarios.

**Best For:**
- Pre-release quality gates
- Understanding test health of a module
- Identifying where to add tests
- Evaluating test quality, not just quantity
- Reviewing test architecture

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Test Coverage Analyst | Missing tests, coverage gaps, untested paths |
| Test Behavior Analyst | Test patterns, assertion quality, test isolation |

### Scaled Agents (Based on Scope Size)
| Agent | Focus | When to Include |
|-------|-------|-----------------|
| Module Specialist (x N) | Deep dive on specific modules | Large codebases - one per major module |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Architecture Reviewer | Test architecture, fixture design | Testing patterns are a concern |
| Code Quality Analyst | Test code quality | Test maintainability is a priority |
| Documentation Consistency Reviewer | Test patterns vs `docs/guides/testing_infrastructure.md` | Testing docs may be stale |

### Typical Agent Count: 4-15 (scales significantly with test count)

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - All tests in codebase
   - Tests for specific module (specify path)
   - Tests for specific feature area
   - Only unit tests / Only integration tests / Both

2. **Focus Area**
   - Missing tests (coverage gaps)
   - Weak tests (poor assertions, can't fail)
   - Both missing and weak tests
   - Test architecture and patterns

3. **Coverage Priorities**
   - Which modules are most critical to have well-tested?
   - Any known undertested areas?

4. **Test Quality Concerns**
   - Any known flaky tests?
   - Any tests that seem to pass but shouldn't?
   - Concerns about test maintainability?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Test Coverage Review

| Test Count | Recommended Configuration |
|------------|--------------------------|
| Small (<100 tests) | 4 agents: TC, TB, 2 Module Specialists |
| Medium (100-500 tests) | 6-8 agents: TC, TB, 4-6 Module Specialists |
| Large (500-1500 tests) | 10-12 agents: TC, TB, 8-10 Module Specialists |
| Comprehensive (1500+ tests) | 15-20+ agents: Scale Module Specialists to coverage |

### Module Specialist Assignment
- Assign one Module Specialist per major module or test directory
- Each specialist does deep analysis of their assigned area
- Prevents superficial coverage of large test suites

### Present to User
```
Based on test suite analysis:
- Total test files: {N}
- Total test functions: {N}
- Major test directories: {list}

Recommended configuration:
- Agent count: {N}
- Core agents: Test Coverage Analyst, Test Behavior Analyst
- Module Specialists: {N} (one per: {list of modules})

Would you like to adjust agent count or module assignments?
```

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Test Coverage Analyst
```markdown
Focus on:
- Public methods without corresponding tests
- Code paths not exercised by tests
- Edge cases not tested (null, empty, boundary values)
- Error conditions not tested
- Integration points without integration tests
- Critical business logic without tests

For each gap, note:
- What's untested
- Why it matters (criticality)
- Suggested test approach
```

#### Test Behavior Analyst
```markdown
Focus on:
- Tests without meaningful assertions
- Tests that can never fail (always pass)
- Tests with multiple unrelated assertions
- Poor test isolation (tests affecting each other)
- Overuse of mocks hiding real bugs
- Flaky test indicators (timing, ordering)
- Test names that don't describe behavior
- Missing setup/teardown
- Duplicate test logic

For each issue, note:
- The specific problem
- Example test(s) affected
- How to improve
```

#### Module Specialist (Assigned Module)
```markdown
You are assigned to review: {MODULE_PATH}

Perform deep analysis:
1. List all public interfaces in this module
2. Map each interface to its tests
3. Identify gaps in coverage
4. Assess test quality for existing tests
5. Note any module-specific testing challenges

Produce a module-specific report including:
- Coverage map (what's tested, what's not)
- Quality assessment of existing tests
- Priority recommendations for this module
```

---

## Phase E: User Summary (Extended)

### Test Coverage Review Report Structure

Present findings in this order:

1. **Coverage Overview**
   - Estimated coverage percentage (if calculable)
   - Number of untested public interfaces
   - Critical paths without tests

2. **Coverage Gaps by Priority**
   - Critical: Business logic, security, data integrity
   - High: Core functionality, common paths
   - Medium: Edge cases, error handling
   - Low: Utilities, helpers

3. **Test Quality Issues**
   - Tests that can't fail
   - Weak assertions
   - Poor isolation
   - Flaky test indicators

4. **Module-by-Module Summary**
   | Module | Coverage | Quality | Priority Issues |
   |--------|----------|---------|-----------------|

5. **Recommendations**
   - Tests to add (prioritized list)
   - Tests to fix/improve
   - Testing patterns to adopt
   - Testing patterns to avoid

6. **Quick Wins**
   - Simple tests that would add significant coverage
   - Easy fixes for weak tests

---

## Special Considerations

### When Reviewing Large Test Suites (1000+ tests)
- Use more Module Specialists for parallel coverage
- Focus on breadth first, depth second
- Prioritize critical modules
- Consider sampling strategies for very large suites

### When Test Framework Varies
- Note different testing patterns used
- Identify framework-specific issues
- Recommend standardization where beneficial

### When Coverage Tools Available
- Integrate with existing coverage reports if available
- Use coverage data to guide agent focus
- Validate coverage tool findings with manual review

---

## Example Workflow

1. User runs "Test Coverage Review" prompt
2. Coordinator asks scope questions
3. User: "Review all unit tests, focus on the fleet module specifically"
4. Coordinator creates: `2026-01-23_test-coverage_fleet-module/`
5. Coordinator analyzes test structure, recommends 6 agents
6. User confirms
7. Agents launch: TC, TB, 4 Module Specialists (fleet, combat, strategy, base)
8. Each agent writes to `findings/`
9. Coordinator compiles `report.md`
10. Summary: "Fleet module has 45% estimated coverage with 12 untested public methods. Found 8 tests with weak assertions."
11. User discusses, decides to create project for fleet test improvements

---

## Termination

After presenting findings:
1. Update `reviews_index.md`
2. Offer user options:
   - Generate test addition recommendations
   - Create project for systematic test improvements
   - Export prioritized list of tests to write
   - Save for reference
