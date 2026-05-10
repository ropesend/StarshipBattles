# PROTOCOL 08: Consistency Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Check for inconsistent patterns across the codebase. Identify where the same problem is solved in multiple different ways, catalog patterns in use, and recommend standardization.

---

## Overview

The Consistency Review helps identify where the codebase has evolved inconsistently. When multiple developers or multiple phases of development result in different approaches to the same problem, the codebase becomes harder to understand, maintain, and extend.

**Best For:**
- Preparing coding standards
- Post-growth consolidation
- Onboarding documentation
- Refactoring planning
- Reducing cognitive load
- Establishing "the one right way"

---

## Default Agent Configuration

### Required Agents
| Agent | Focus |
|-------|-------|
| Pattern Cataloguer | Document all patterns in use across the codebase |
| Inconsistency Hunter | Find deviations from common patterns |
| Documentation Consistency Reviewer | Code vs `docs/` discrepancies — `docs/` is the authoritative reference for patterns |

### Recommended Agents
| Agent | Focus |
|-------|-------|
| Style Analyzer | Coding style consistency (naming, formatting, idioms) |
| Convention Enforcer | Structural conventions (file layout, module organization) |

### Optional Agents
| Agent | Focus | Include When |
|-------|-------|--------------|
| Code Quality Analyst | Quality implications of inconsistencies | Understanding impact |
| Architecture Reviewer | Architectural pattern consistency | System-level review |
| Module Specialist (x N) | Deep dive on specific areas | Large codebases |

### Typical Agent Count: 4-6

---

## Phase A: Scope Definition (Extended)

### Questions to Ask User

Use AskUserQuestion with these options:

1. **Review Scope**
   - Entire codebase
   - Specific module/area
   - Specific pattern type (see below)

2. **Pattern Categories to Check**
   - Error handling patterns
   - Logging patterns
   - Data access patterns
   - API/interface patterns
   - Naming conventions
   - File/module organization
   - Testing patterns
   - Configuration patterns
   - All categories

3. **Known Reference Points**
   - Any files/modules that represent the "correct" way?
   - Established patterns to use as reference?
   - Style guides or conventions already documented?

4. **Areas of Concern**
   - Any known inconsistencies?
   - Areas that feel "different" from the rest?
   - Recent additions vs. legacy code?

5. **Standardization Intent**
   - Looking to establish new standards?
   - Enforcing existing standards?
   - Just documenting current state?

---

## Phase B: Agent Planning (Extended)

### Scaling Guidelines for Consistency Review

| Scope | Recommended Configuration |
|-------|--------------------------|
| Single pattern type | 4 agents: PC, IH, SA, CE |
| Module-level | 4-5 agents: Core set |
| System-wide | 5-6 agents: Add Code Quality or Architecture |
| Full codebase | 6+ agents: Add Module Specialists |

### Focus Area Selection
Based on user priorities, agents focus on:
- Structural patterns (how code is organized)
- Behavioral patterns (how code does things)
- Naming patterns (what things are called)
- Style patterns (how code looks)

---

## Phase C: Review Swarm Launch (Extended)

### Agent-Specific Instructions

#### Pattern Cataloguer (Primary)
```markdown
# Pattern Cataloguing Task

## Scope
{SCOPE_FROM_PHASE_A}

## Categories to Catalogue

### 1. Error Handling Patterns
Document all approaches used for:
- Exception handling (try/except styles)
- Error return patterns
- Error propagation
- Error logging
- User error messages

### 2. Logging Patterns
Document all approaches used for:
- Log level usage
- Log message formatting
- What gets logged
- Logger initialization
- Structured vs. unstructured logging

### 3. Data Access Patterns
Document all approaches used for:
- Database queries
- File reading/writing
- Configuration access
- Cache usage
- External API calls

### 4. API/Interface Patterns
Document all approaches used for:
- Method signatures (parameter order, naming)
- Return value patterns
- Callback vs. return vs. exception
- Public interface design

### 5. Naming Conventions
Document variations in:
- Class naming
- Method naming
- Variable naming
- File naming
- Constant naming

### 6. Structural Patterns
Document variations in:
- File organization within modules
- Import organization
- Class structure
- Module organization

### 7. Testing Patterns
Document variations in:
- Test file organization
- Test naming
- Fixture usage
- Assert styles
- Mock usage

## Output Format
For each pattern category:
| Pattern Variant | Location Examples | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Variant A | file1.py, file2.py | 45 uses | {notes} |
| Variant B | file3.py | 12 uses | {notes} |
```

#### Inconsistency Hunter
```markdown
# Inconsistency Detection Task

## Focus Areas

### 1. Same Problem, Different Solutions
Find where:
- Similar functionality is implemented differently
- Same operation has different error handling
- Same data is accessed differently
- Same operation has different names

### 2. Newer vs. Older Code
Compare:
- Recent additions vs. legacy code
- Different modules doing similar things
- Evolution of patterns over time

### 3. Developer Fingerprints
Identify:
- Stylistic differences suggesting different authors
- Inconsistent idioms
- Mixed conventions

### 4. Partial Migrations
Find:
- Patterns that were started but not completed
- Mixed old and new approaches
- Abandoned refactoring attempts

### 5. Copy-Paste Variants
Find:
- Similar code that diverged
- Templates applied inconsistently
- Near-duplicates with small differences

## For Each Inconsistency
Report:
- What's inconsistent
- Locations of different variants
- Which appears to be "newer" or "better"
- Impact of the inconsistency
```

#### Style Analyzer
```markdown
# Style Consistency Analysis

## Focus Areas

### 1. Naming Style
Check consistency of:
- Case conventions (snake_case, camelCase, PascalCase)
- Abbreviations vs. full words
- Prefix/suffix patterns
- Boolean naming (is_, has_, can_)

### 2. Code Formatting
Check consistency of:
- Indentation
- Line length
- Blank lines usage
- Import ordering
- Quote styles (single vs. double)

### 3. Language Idioms
Check consistency of:
- Comprehensions vs. loops
- Context managers usage
- Type hints presence
- Docstring formats

### 4. Comment Style
Check consistency of:
- Comment frequency
- Comment format
- TODO/FIXME format
- Inline vs. block comments

## Output
| Style Aspect | Variants Found | Dominant | Recommendation |
|--------------|----------------|----------|----------------|
```

#### Convention Enforcer
```markdown
# Structural Convention Analysis

## Focus Areas

### 1. File Organization
Check:
- Standard file layout (imports, constants, classes, functions)
- File naming conventions
- Test file naming and location
- Config file placement

### 2. Module Organization
Check:
- __init__.py patterns
- Public vs. private organization
- Submodule structure
- Cross-module imports

### 3. Class Organization
Check:
- Method ordering (lifecycle, public, private)
- Property placement
- Static method usage
- Class vs. instance method patterns

### 4. Package Structure
Check:
- Top-level organization
- Feature vs. layer organization
- Shared/common code location
- Test organization

## Output
| Convention | Expected | Violations | Locations |
|------------|----------|------------|-----------|
```

---

## Phase D: Findings Compilation (Extended)

### Consistency Report Structure

```markdown
# Consistency Review Report

## Executive Summary
- **Overall Consistency:** [High / Moderate / Low / Chaotic]
- **Pattern Categories Analyzed:** {N}
- **Inconsistencies Found:** {N}
- **Top Recommendation:** {summary}

## Pattern Inventory

### Error Handling
| Pattern | Frequency | Locations | Notes |
|---------|-----------|-----------|-------|
| Try/except with logging | 65% | game/, tests/ | Most common |
| Return error codes | 20% | legacy/ | Legacy pattern |
| Silent failures | 15% | utils/ | Problematic |

**Recommended Standard:** {description}

### Logging
[Same format]

### Naming Conventions
[Same format]

### [Other Categories]
[Same format]

## Key Inconsistencies

### INC-01: {Title}
**Category:** {category}
**Description:** {what's inconsistent}
**Variants:**
1. {Variant A}: {description} - {locations}
2. {Variant B}: {description} - {locations}
**Impact:** {how this affects development}
**Recommended Resolution:** {which variant to standardize on}
**Effort:** {Simple/Medium/Complex}

## Consistency Scores by Module
| Module | Error Handling | Naming | Structure | Overall |
|--------|---------------|--------|-----------|---------|
| game/ | High | Medium | High | High |
| utils/ | Low | Medium | Low | Low |
| tests/ | Medium | High | Medium | Medium |

## Standardization Recommendations

### Quick Wins (Mechanical Changes)
| # | Change | Locations | Effort |
|---|--------|-----------|--------|
| 1 | Standardize import order | 23 files | Simple |
| 2 | Unify error message format | 15 files | Simple |

### Standard Patterns to Establish
For each category, recommend THE pattern to use:

#### Error Handling Standard
```python
# Recommended pattern
try:
    result = operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
```

#### Logging Standard
```python
# Recommended pattern
logger = logging.getLogger(__name__)
logger.info("Action completed", extra={"key": value})
```

[Continue for each category]

## Implementation Roadmap

### Phase 1: Document Standards
- Create/update coding standards document
- Document "the one right way" for each category

### Phase 2: New Code
- All new code follows standards
- Code review enforcement

### Phase 3: Incremental Cleanup
- Fix inconsistencies during regular work
- Dedicated cleanup sprints for worst areas

## Appendix: Full Pattern Catalog
[Detailed pattern inventory from agents]
```

---

## Phase E: User Summary (Extended)

### Presenting Consistency Findings

1. **Show the Variety**
   - How many ways are things done?
   - Which areas are most inconsistent?

2. **Identify the "Winner"**
   - Which pattern should be standard?
   - Based on frequency, quality, or preference?

3. **Quantify the Inconsistency**
   - Scores by area
   - Relative consistency

4. **Recommend Standards**
   - Clear "do it this way" for each category
   - Code examples

5. **Propose Consolidation Plan**
   - How to get to consistency
   - Phased approach

---

## Special Considerations

### Don't Boil the Ocean
- Complete consistency is rarely achievable
- Focus on high-impact areas
- Accept some variation in stable legacy code

### The "Correct" Pattern
- May be most common
- May be newest/best practice
- May be what team prefers
- Get user input on which to standardize

### Automation Opportunities
- Many style issues can be fixed automatically
- Recommend tooling (formatters, linters)
- Document what can be automated

### Cultural Change
- Standards need team buy-in
- Document rationale, not just rules
- Make it easy to do the right thing

---

## Example Workflow

1. User runs "Consistency Review" prompt
2. Coordinator asks scope questions
3. User: "Review error handling and logging patterns across the codebase"
4. Review folder: `2026-01-23_consistency_error-logging-patterns/`
5. Agents: Pattern Cataloguer, Inconsistency Hunter, Style Analyzer, Convention Enforcer
6. Agents analyze patterns
7. Findings:
   - 4 different error handling approaches found
   - 3 logging styles in use
   - Newest modules use approach A, legacy uses B and C
   - 12 files have mixed approaches internally
8. Recommendations:
   - Standardize on approach A (newest, cleanest)
   - Create error handling guide
   - Fix internal inconsistencies (12 files)
9. User creates project for standardization

---

## Termination

After presenting findings:
1. Discuss which patterns to standardize on
2. Get user agreement on "the right way"
3. Offer options:
   - Create standards document
   - Create consistency enforcement project
   - Export pattern inventory
4. Update `reviews_index.md`
