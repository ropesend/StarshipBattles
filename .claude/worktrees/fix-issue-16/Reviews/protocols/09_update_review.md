# PROTOCOL 09: Update Review
**Role:** Code Review Coordinator
**Extends:** 00_review_core.md

**Purpose:** Re-evaluate findings from a previous review to track remediation progress, validate fixes, identify regressions, and discover new issues within the original scope.

---

## Overview

The Update Review provides a progress report on a previous review's findings. It validates whether issues have been addressed, identifies partial fixes, tracks regressions, and discovers new issues within the original scope.

**Best For:**
- Post-remediation validation
- Sprint-end progress tracking
- Pre-release quality gates
- Continuous improvement monitoring
- Project phase completion checkpoints

**Key Differentiator:** Unlike other reviews that start fresh, the Update Review uses an existing review as its baseline and focuses on change detection.

---

## Relationship to Original Review

### Linking Model
- Update reviews are linked to their parent via the `original_review` field in scope.md
- The index tracks the relationship in the "Update Reviews" section
- Multiple updates can reference the same original (creating a timeline)
- Updates can also reference other updates (chained updates)

### Scope Inheritance
- By default, Update Review uses the SAME scope as the original
- User can optionally narrow scope (but not expand beyond original)

---

## Validation Status Definitions

| Status | Code | Definition |
|--------|------|------------|
| FIXED | F | Issue no longer present, fully resolved |
| PARTIALLY_FIXED | PF | Issue reduced but not eliminated |
| STILL_PRESENT | SP | Issue unchanged from original review |
| WORSE | W | Issue has expanded or degraded since original |
| OBSOLETE | O | Location/code no longer exists |
| CANNOT_VERIFY | CV | Unable to determine status |

---

## Default Agent Configuration

### Required Agents (Always Include)
| Agent | Focus | Finding Prefix |
|-------|-------|----------------|
| Finding Validator | Validate status of each original finding | VAL |
| Progress Analyst | Summarize overall remediation progress | PROG |

### Recommended Agents (Always Include for Update Reviews)
| Agent | Focus | Finding Prefix |
|-------|-------|----------------|
| Regression Hunter | Check if fixed items regressed | REG |
| New Issue Scout | Discover new issues within original scope | NEW |
| Documentation Consistency Reviewer | Check if fixes updated `docs/` as needed | DOCC |

### Typical Agent Count: 4

---

## Phase A: Scope Definition (Extended)

### Step 1: Identify Original Review

Present available reviews to the user:
```
Available reviews for update:

Completed Reviews:
| # | Date | Type | Description | Findings |
|---|------|------|-------------|----------|
| 1 | 2026-01-24 | General | full-codebase-maintainability | 161 |
| 2 | 2026-01-23 | Test Coverage | full-codebase-coverage-gaps | 45 |

Select review to update (enter number or folder name):
```

### Step 2: Load Original Review Data
- Parse original scope.md for scope definition
- Parse original report.md for findings list
- Use `python validate_findings.py <original_folder>` to extract findings
- Load any previous updates to this review (for chained updates)

### Step 3: Confirm Update Scope

Use AskUserQuestion with these options:

1. **Validation Scope**
   - Full validation (all original findings)
   - Critical/Major only
   - Specific finding IDs

2. **Known Fixes**
   - Any specific findings you know were addressed?
   - Any areas where work was done?

3. **Regression Candidates**
   - Any areas of recent work that might have caused regressions?
   - Any files significantly modified since original review?

### Step 4: Create Update Review Folder
```bash
python Reviews/scripts/create_review.py update "<original-description>" --original <original_folder>
```
Creates: `YYYY-MM-DD_update_<original-description>/`

### Step 5: Document Update Scope
Write extended scope.md with:
- Link to original review
- Original scope (inherited)
- Validation configuration
- Original findings count
- Previous update chain (if any)

---

## Phase B: Agent Planning (Extended)

### Standard Configuration
Update reviews use a fixed agent set:
- 4 agents total
- Finding Validator (required)
- Progress Analyst (required)
- Regression Hunter (recommended)
- New Issue Scout (required - always discovers new issues)

### Present Configuration to User
```
Original review: {ORIGINAL_FOLDER}
Original date: {ORIGINAL_DATE}
Days since original: {N}
Original findings: {N}

Update review agents:
| Agent | Purpose |
|-------|---------|
| Finding Validator | Validate status of each original finding |
| Progress Analyst | Calculate fix rates and progress metrics |
| Regression Hunter | Check for regressions in fixed areas |
| New Issue Scout | Find new issues within original scope |

Confirm agent deployment?
```

---

## Phase C: Review Swarm Launch (Extended)

### Finding Validator Agent Instructions
```markdown
# Update Review Agent: Finding Validator

## Your Task
Validate the current status of each finding from the original review.

## Original Review
- Folder: {ORIGINAL_FOLDER}
- Date: {ORIGINAL_DATE}
- Total Findings: {FINDING_COUNT}

## Findings to Validate
{FORMATTED_FINDINGS_LIST}

## Validation Process
For each finding:
1. Navigate to the original location
2. Determine current status:
   - FIXED: Issue no longer present
   - PARTIALLY_FIXED: Issue reduced but not eliminated
   - STILL_PRESENT: Issue unchanged
   - WORSE: Issue has expanded or degraded
   - OBSOLETE: Location/code no longer exists
   - CANNOT_VERIFY: Unable to determine status

3. Document evidence for your determination
4. Note any related changes observed

## Output Format
Write to: Reviews/results/{UPDATE_FOLDER}/findings/validation_report.md

### Finding Status Summary
| ID | Original Severity | Status | Evidence |
|----|------------------|--------|----------|

### Detailed Validation
For each finding:

#### {ORIGINAL_ID}: {ORIGINAL_TITLE}
**Original Location:** `{LOCATION}`
**Original Severity:** {SEVERITY}
**Status:** {FIXED|PARTIALLY_FIXED|STILL_PRESENT|WORSE|OBSOLETE|CANNOT_VERIFY}
**Evidence:** {What you observed}
**Notes:** {Any relevant context}
```

### Regression Hunter Agent Instructions
```markdown
# Update Review Agent: Regression Hunter

## Your Task
Check for regressions - issues that were fixed but have returned, or areas where quality has degraded.

## Context
- This is an update to review: {ORIGINAL_FOLDER}
- Check areas where fixes were made
- Look for patterns suggesting incomplete fixes

## Focus Areas
1. Files modified since original review
2. Areas marked as "fixed" in any previous updates
3. Code paths related to original Critical/Major findings

## Output Format
Write to: Reviews/results/{UPDATE_FOLDER}/findings/regression_report.md

### Regression Summary
| ID | Related Original | Location | Description |
|----|-----------------|----------|-------------|

### Detailed Regressions
#### REG-{N}: {Title}
**Related Finding:** {ORIGINAL_ID}
**Location:** `{LOCATION}`
**Severity:** {Critical|Major|Minor|Info}
**Issue:** {What regressed}
**Evidence:** {How you identified the regression}
**Recommendation:** {How to fix}
**Effort:** {Simple|Medium|Complex}
```

### Progress Analyst Agent Instructions
```markdown
# Update Review Agent: Progress Analyst

## Your Task
Synthesize validation results into a progress report with metrics and insights.

## Analysis Required
1. Calculate fix rates by severity
2. Calculate fix rates by category/agent prefix
3. Identify patterns in what was/wasn't fixed
4. Assess overall remediation progress
5. Project remaining effort

## Output Format
Write to: Reviews/results/{UPDATE_FOLDER}/findings/progress_report.md

### Progress Summary
- Original Findings: {N}
- Fixed: {N} ({%})
- Partially Fixed: {N} ({%})
- Still Present: {N} ({%})
- Worse: {N} ({%})
- Obsolete: {N} ({%})

### Progress by Severity
| Severity | Original | Fixed | Remaining | Fix Rate |
|----------|----------|-------|-----------|----------|
| Critical | | | | |
| Major | | | | |
| Minor | | | | |
| Info | | | | |

### Progress by Category
| Category | Original | Fixed | Remaining | Fix Rate |
|----------|----------|-------|-----------|----------|
| Architecture (AR) | | | | |
| Code Quality (CQ) | | | | |
| [etc.] | | | | |

### Patterns Observed
- What types of issues were addressed?
- What types were ignored?
- Any correlation with effort level?

### Estimated Remaining Effort
- Simple fixes remaining: {N}
- Medium fixes remaining: {N}
- Complex fixes remaining: {N}
```

### New Issue Scout Agent Instructions
```markdown
# Update Review Agent: New Issue Scout

## Your Task
Identify NEW issues within the original review's scope that were not in the original findings.

## Original Scope
{ORIGINAL_SCOPE_DEFINITION}

## Constraints
- Only report issues NOT in the original findings
- Focus on areas likely to have changed since original review
- Use the same severity definitions as original
- Use the same finding format

## Focus Areas
1. Code added since original review
2. Code modified since original review
3. Areas adjacent to fixed issues (sometimes fixes introduce new issues)

## Output Format
Write to: Reviews/results/{UPDATE_FOLDER}/findings/new_issues_report.md

Use standard finding format with prefix NEW-:

### New Issues Summary
| ID | Severity | Title | Location | Effort |
|----|----------|-------|----------|--------|

### Detailed New Findings

#### {SEVERITY}: {Title}
**ID:** NEW-{NUMBER}
**Location:** `{LOCATION}`
**Issue:** {Description}
**Impact:** {Impact}
**Recommendation:** {Fix}
**Effort:** {Simple|Medium|Complex}
```

---

## Phase D: Findings Compilation (Extended)

### Step 1: Run compile_update_findings.py
```bash
python Reviews/scripts/compile_update_findings.py Reviews/results/{UPDATE_FOLDER}
```

This script:
1. Loads original review's findings
2. Parses validation results from validation_report.md
3. Calculates progress metrics
4. Identifies regressions from regression_report.md
5. Incorporates new findings from new_issues_report.md
6. Generates report.md with progress visualization

### Update Report Structure
```markdown
# Update Review Report: {UPDATE_FOLDER}

## Metadata
- **Date:** YYYY-MM-DD
- **Type:** Update Review
- **Original Review:** [{ORIGINAL_FOLDER}](../{ORIGINAL_FOLDER}/)
- **Original Date:** YYYY-MM-DD
- **Days Since Original:** {N}
- **Update Chain:** {1st update / 2nd update / etc.}

## Executive Summary

### Progress Overview
| Metric | Count | Percentage |
|--------|-------|------------|
| Original Findings | N | 100% |
| Fixed | N | X% |
| Partially Fixed | N | X% |
| Still Present | N | X% |
| Worse | N | X% |
| Obsolete | N | X% |

### Severity Progress
| Severity | Original | Fixed | Remaining | Fix Rate |
|----------|----------|-------|-----------|----------|

### Alerts
- Regressions Found: {N}
- Findings That Got Worse: {N}
- New Critical/Major Issues: {N}

---

## Progress Visualization

### Timeline (if chained updates)
| Update | Date | Fixed | Remaining | Fix Rate |
|--------|------|-------|-----------|----------|
| Original | YYYY-MM-DD | - | N | - |
| Update 1 | YYYY-MM-DD | N | N | X% |
| This Update | YYYY-MM-DD | N | N | X% |

---

## Detailed Finding Status

### Fixed Findings ({N})
### Partially Fixed Findings ({N})
### Still Present Findings ({N})
### Findings That Got Worse ({N})
### Obsolete Findings ({N})

---

## Regressions
[From regression_report.md]

---

## New Issues
[From new_issues_report.md]

---

## Recommendations

### Immediate Actions
1. Address regressions (REG-*)
2. Re-fix "worse" items
3. Continue work on remaining Critical findings

### For Next Update
- Schedule update for: {recommended date}
- Focus areas: {categories with low fix rates}

---

## Agent Reports
- [Validation Report](findings/validation_report.md)
- [Progress Report](findings/progress_report.md)
- [Regression Report](findings/regression_report.md)
- [New Issues Report](findings/new_issues_report.md)

## Links
- [Original Review](../{ORIGINAL_FOLDER}/)
- [Previous Update](../{PREVIOUS_UPDATE_FOLDER}/) (if exists)
```

---

## Phase E: User Summary (Extended)

### Present Progress Dashboard
```
Update Review Complete: {UPDATE_FOLDER}

PROGRESS SUMMARY
================
Original Findings: 161
Days Since Original: 4

Status Breakdown:
  Fixed:           45 (28%) ████████░░░░░░░░
  Partially Fixed: 12 (7%)  ██░░░░░░░░░░░░░░
  Still Present:   89 (55%) ████████████████
  Worse:           3  (2%)  █░░░░░░░░░░░░░░░
  Obsolete:        12 (7%)  ██░░░░░░░░░░░░░░

Critical Progress: 15/22 fixed (68%)
Major Progress:    20/71 fixed (28%)

ALERTS
======
! 3 findings got WORSE - requires attention
! 2 regressions detected
! 5 new Critical/Major issues found

TOP PRIORITIES
==============
1. Fix regressions REG-01, REG-02
2. Address "worse" findings
3. Review new Critical issues
4. Continue work on remaining Critical findings
```

### Discussion Topics
1. Review validation accuracy (any disagreements?)
2. Discuss findings marked "worse"
3. Explain "obsolete" items
4. Review new issues discovered
5. Plan next remediation sprint
6. Schedule follow-up update review

---

## Example Workflow

1. User runs "Update Review" prompt
2. Coordinator lists available reviews for update
3. User selects: "2026-01-24_general_full-codebase-maintainability"
4. Coordinator loads original findings (161 total)
5. Coordinator creates: `2026-01-28_update_full-codebase-maintainability/`
6. 4 agents launch:
   - Finding Validator checks each finding
   - Regression Hunter looks for regressions
   - Progress Analyst calculates metrics
   - New Issue Scout finds new issues
7. Coordinator runs compile_update_findings.py
8. Coordinator presents progress dashboard:
   - "45 of 161 findings fixed (28%)"
   - "2 regressions detected"
   - "8 new issues found"
9. User discusses progress, plans next sprint
10. Optionally schedules next update review

---

## Termination

After presenting summary:
1. Update `reviews_index.md` with update review in "Update Reviews" section
2. Link update to original in index
3. Ask user if they want to:
   - Create project from remaining findings
   - Schedule next update (add to calendar/notes)
   - Export progress report
   - Discuss specific findings further
