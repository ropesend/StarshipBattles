---
name: audit-shrink
description: Run a comprehensive code shrinkage audit. Combines deterministic tools (vulture, radon, clone detector, orphans, dependency graph, LOC tracking) with 3 agents for semantic duplication and dead code review. Produces a unified report with shrinkage estimates. Production code only.
argument-hint: [optional: --skip-phase1 to reuse existing raw results]
---

# Code Shrinkage Audit

Run a two-phase audit of the production codebase to find dead code, near-duplicate code, and complexity hotspots. Produces a unified report with estimated LOC savings and a prioritized cleanup order.

Does NOT change any code. Targets `game/` only (not tests).

## Execution

This skill is a single-command workflow. The user loads it and you handle everything.

### Step 0: Pre-Flight Checks

Ensure vulture and radon are installed:

```bash
pip show vulture || pip install vulture
pip show radon || pip install radon
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/audit_shrink/audit_shrink.py
```

Capture the last few lines of stdout. Look for the line that prints the output directory path:
```
Output directory: Reviews/results/2026-04-27_133045_audit_shrink
```

Store this as `REVIEW_DIR`. The script also prints status for each tool step — note any FAILED steps.

If `$0` is `--skip-phase1`, skip this step and use the most recent review directory from `Reviews/results/`.

The script creates `REVIEW_DIR/raw/` with these outputs against `game/`:

1. `loc_baseline.txt` — baseline LOC by section
2. `vulture_100.txt` — dead code at 100% confidence
3. `vulture_80.txt` — dead code at 80% confidence
4. `orphans.txt` — modules nothing imports
5. `dead_deps.txt` — unreachable files from entry points
6. `radon.json` — complexity hotspots (CC >= 11)
7. `clones.json` — AST near-duplicate function clusters
8. `manifest.json` — file inventory + shard rotation

### Step 2: Read Phase 1 Outputs

Read these files into memory for use in agent prompts:

1. Read `REVIEW_DIR/raw/manifest.json` — note `deep_review_shard` field (UI, SIM, STR, or FND), `deep_review_label`, and the file list for that shard at `shards.{shard_id}.files`
2. Read `REVIEW_DIR/raw/clones.json` — clone detector clusters (get the full JSON content)
3. Read `REVIEW_DIR/raw/vulture_100.txt` — dead code candidates for Agent 3 (get the full text)
4. Read `REVIEW_DIR/raw/vulture_80.txt` — high-likelihood dead code (get the full text)
5. Read `REVIEW_DIR/raw/orphans.txt` — orphan modules (get the full text)
6. Read `REVIEW_DIR/raw/dead_deps.txt` — unreachable files (get the full text)
7. Read `REVIEW_DIR/raw/radon.json` — complexity data (get the full JSON content)
8. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`

### Step 3: Launch 3 Agents in Parallel

Create the findings directory:
```bash
mkdir -p REVIEW_DIR/findings
```

Launch **3 agents** in parallel using the Task tool with `subagent_type: general`. Each agent receives EXACTLY the prompt template below with placeholder text replaced by actual data.

**Replace these placeholders in each template before sending:**
- `{REVIEW_DIR}` → the actual review directory (e.g., `Reviews/results/2026-04-27_133045_audit_shrink`)
- `{shard_id}` → from manifest.json `deep_review_shard`
- `{shard_label}` → from manifest.json `shards.{shard_id}.label`
- `{shard_files}` → the files list from manifest.json `shards.{shard_id}.files`, formatted as markdown list
- `{clones_json}` → the full content of clones.json
- `{vulture_100}` → the full content of vulture_100.txt
- `{vulture_80}` → the full content of vulture_80.txt
- `{orphans}` → the full content of orphans.txt
- `{dead_deps}` → the full content of dead_deps.txt

#### Agent 1: Cross-Shard Duplication

```
# Cross-Shard Duplication Hunter

Scan the ENTIRE game/ directory for structural and semantic duplication with NO
shard restrictions. Your primary input is a clone detector JSON report — validate
its findings, then hunt for what the tool missed.

## Documentation Reference
Read docs/02_PATTERNS.md. If duplicated code contradicts a documented pattern
(e.g., reimplements something that should use a registry, strategy, or factory
pattern), escalate severity — it's both duplication AND architectural drift.

## Clone Detector Results
The deterministic clone detector found these near-duplicate clusters:

{clones_json}

## Scope
All files under game/ (ui/, simulation/, strategy/, core/, engine/, ai/, research/).

## Methodology

### Phase 1: Validate Clone Detector
- For each cluster in clones.json, read the implicated files
- Verify the functions are genuinely similar (not false positives)
- Assess whether consolidation is feasible
- For confirmed clusters, estimate LOC savings from consolidation

### Phase 2: Hunt Cross-Shard Duplication
Scan for these patterns across shard boundaries:
- Same concept implemented differently in multiple layers
- Utility functions copy-pasted between ui/, strategy/, and simulation/
- Multiple serialization/deserialization approaches for the same data
- Multiple validation routines for the same kind of input
- Multiple distance/position calculations
- Multiple "find best" or "select by criteria" algorithms

### Phase 3: Copy-Paste Drift
- Similar function bodies with slightly different variable names
- Methods sharing 80%+ structure but with small differences
- UI rendering functions repeating layout logic with different content
- Helper functions duplicated across modules with minor variations

## Severity Guide
- CRITICAL: Same business logic in 3+ places with active divergence
- MAJOR: Significant code blocks (>20 lines) duplicated in 2+ places
- MINOR: Small utility duplication or low-risk copy-paste patterns
- INFO: Observations that may not warrant consolidation

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/duplication_cross_shard.md

Use EXACTLY this structure:
# Cross-Shard Duplication Report
## Summary
- Files Scanned: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N] | Info: [N]

## Clone Detector Validation
[For each cluster: confirmed / false-positive / downrated, with explanation]

## Cross-Shard Findings
#### CRITICAL: [Title]
**ID:** DUP-X-[NUMBER]
**Location:** file1.py:lines AND file2.py:lines
**Layer:** [e.g., simulation -> strategy]
**Issue:** [description]
**Impact:** [maintenance risk]
**Recommendation:** [how to consolidate]
**Estimated LOC Savings:** [N]
**Effort:** [Simple/Medium/Complex]

## Prioritized Consolidation Plan
[Ordered by impact/effort ratio]
```

#### Agent 2: In-Shard Deep Review

```
# In-Shard Deep Review Agent

You are assigned ONE shard this run: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/02_PATTERNS.md and docs/03_CONVENTIONS.md.

## Scope
All files listed below MUST be read. If you skip any file, the coverage
guarantee is broken for this cycle.

Shard file list:
{shard_files}

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Check for dead code within the file:**
   - Functions/methods never called (check via grep)
   - Classes never instantiated (check via grep)
   - Unused imports
   - Unreachable branches (code after return/raise, always-true/false conditions)
3. **Check for internal duplication:**
   - Repeated code blocks within the same file
   - Methods that could be refactored into a helper
4. **Check for fragmentation:**
   - A single responsibility split across this file and others in the same shard
   - Related helper functions spread across unrelated modules
   - Partial implementations that should be consolidated
5. **Check for code quality issues that bloat LOC:**
   - Overly verbose patterns (if/elif chains where a dict lookup would work)
   - Repeated inline constants that should be module-level
   - Functions that could be simplified with stdlib (itertools, collections)

## What NOT to Report
- Unit tests (ignore tests/ completely)
- Comments/docstrings being too long
- Test fixtures or test-only code
- Code already marked for deprecation

## Severity Guide
- CRITICAL: True dead code that is importable/callable but never reached
- MAJOR: Significant internal duplication or fragmentation (>30 lines)
- MINOR: Small dead code (individual imports, short dead functions)
- INFO: Style suggestions that would reduce LOC without changing behavior

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/deep_review_{shard_id}.md

# Deep Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count] (MUST equal the scope count)
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N] | Info: [N]

## Dead Code Findings
#### {SEVERITY}: [Title]
**ID:** DEEP-{shard_id}-[NUMBER]
**Location:** file.py:lines
**Issue:** [description]
**Estimated LOC:** [N]
**Recommendation:** [what to do]

## Internal Duplication Findings
#### {SEVERITY}: [Title]
**ID:** DEEP-{shard_id}-[NUMBER]
...

## Fragmentation Findings
...

## Quality / LOC Reduction Findings
...

## File Coverage Verification
| File | Status |
|------|--------|
| [reproduce the full file list with "Read ✓" for each] |
```

#### Agent 3: Dead Code Validator

```
# Dead Code Validator

Validate dead code candidates from deterministic tools against actual usage in
the production codebase. Filter false positives, confirm true positives,
cross-reference against docs, and produce a prioritized dead code inventory.

## Documentation Reference
Read docs/01_ARCHITECTURE.md and docs/02_PATTERNS.md.
If docs/ still reference code flagged as dead, note it as a documentation
discrepancy. If dead code implements a pattern REMOVED from docs, it confirms
the code should be removed.

## Input Data

### Vulture 100% Confidence (confirmed dead by static analysis):
{vulture_100}

### Vulture 80% Confidence (high-likelihood):
{vulture_80}

### Orphan Modules (no imports from other game/ modules):
{orphans}

### Unreachable Files (not reachable from launcher.py or game/app.py):
{dead_deps}

## Methodology

For EACH dead code candidate:

1. **Verify with grep**: Search the entire game/ directory for references
2. **Check dynamic dispatch**: Registry lookups, string-based dispatch, getattr
3. **Check TYPE_CHECKING blocks**: Imported only under `if TYPE_CHECKING`?
4. **Check command/ability registries**: Classes instantiated via registry
5. **Check docs/**: Does any docs/ file reference this code?
6. **Check __init__.py re-exports**: Is it re-exported?

## False Positive Patterns (do NOT report as dead)
- Pytest fixtures and test utilities
- Protocol/ABC classes used in isinstance() checks or type annotations
- Command classes instantiated via registry dispatch
- Factory functions called from tests
- `__exit__` parameters (exc_type, exc_val, exc_tb)
- Signal/slot connections in UI code

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/dead_code_validation.md

# Dead Code Validation Report
## Summary
- Total Candidates Reviewed: [N]
- Confirmed Dead: [N]
- False Positives: [N]
- Documentation Discrepancies: [N]

## Confirmed Dead Code

### Tier 1: Dead Files (delete entire files)
| File | Source | LOC | Verified? |
|------|--------|-----|-----------|

### Tier 2: Dead Classes (remove from files)
| Class | File:Line | Source | LOC | Verified? |
|-------|-----------|--------|-----|-----------|

### Tier 3: Dead Functions/Methods
| Function | File:Line | Source | LOC | Verified? |
|----------|-----------|--------|-----|-----------|

### Tier 4: Dead Imports
| Import | File:Line | Source | Verified? |
|--------|-----------|--------|-----------|

## False Positives (Not Dead)
| Item | Reason It's Actually Used |
|------|--------------------------|

## Documentation Discrepancies
| Dead Code Item | docs/ File | What docs say | Recommendation |
|----------------|------------|---------------|----------------|

## Prioritized Cleanup Order
[Ordered by safety (dead files first) then by LOC savings]
```

### Step 4: Verify Agent Outputs

After all 3 agents complete, check that these files exist and are non-empty:

- `REVIEW_DIR/findings/duplication_cross_shard.md`
- `REVIEW_DIR/findings/deep_review_{shard_id}.md`
- `REVIEW_DIR/findings/dead_code_validation.md`

If any agent failed, note it in the report but continue with available data.

### Step 5: Compile Final Report

Read all agent reports and raw tool outputs. Write `REVIEW_DIR/report.md` with these sections:

**1. Executive Summary**
- Date, review directory
- Total findings across all sources
- Trend comparison to previous run (use shrink_tracker.py)
- Shard rotation status

**2. Coverage Status**
| Shard | Files | Last Deep Review | This Run |
|-------|-------|-----------------|----------|

**3. Dead Code Inventory**
Aggregate Agent 3's confirmed dead code by tier with LOC estimates.

**4. Duplication Clusters**
Aggregate Agent 1's findings, grouped by severity.

**5. Complexity Hotspots**
From raw/radon.json, all functions with CC >= 20.

**6. In-Shard Deep Review Summary**
From Agent 2's report, summarize findings + coverage verification.

**7. Shrinkage Scorecard**
| Category | Estimated Reclaimable LOC | Effort | Risk |
|----------|--------------------------|--------|------|
| Dead files | [N] | Low | Safe |
| Dead classes/functions | [N] | Low-Medium | Safe |
| Duplicate consolidation | [N] | Medium-High | Needs design |
| Complexity reduction | [N] | Medium-High | Needs care |
| In-shard cleanup | [N] | Low-Medium | Safe |
| **Total** | **[N]** | | |

**8. Prioritized Cleanup Plan**
Top 10 items ordered by impact/effort.

**9. Trend Comparison**
Use shrink_tracker.py to compare with previous run.

**10. Appendices**
Paths to raw tool outputs and agent reports.

### Step 6: Update Shrink Tracker

Run this Python code (replace placeholders):

```python
from Tools.audit_shrink import shrink_tracker
import json

with open("{REVIEW_DIR}/raw/manifest.json") as f:
    manifest = json.load(f)

run_data = {
    "date": "{REVIEW_DIR}".split("/")[1].split("_")[0],
    "review_dir": "{REVIEW_DIR}",
    "deep_review_shard": manifest["deep_review_shard"],
    "rotation_index": manifest["rotation_index"],
    "production_loc": ...,  # from loc_baseline.txt
    "dead_code_files": ...,  # count from Agent 3 Tier 1
    "dead_code_functions": ...,  # count from Agent 3 Tier 2+3
    "dead_code_imports": ...,  # count from Agent 3 Tier 4
    "duplication_clusters": ...,  # count from Agent 1
    "estimated_shrinkable_loc": ...,  # sum from scorecard
    "top_hotspots": ...,  # top 5 files by finding count
}

shrink_tracker.add_run("Reviews/results", run_data)
```

### Step 7: Present to User

Show the user:
1. Executive summary (3-4 sentences)
2. Shrinkage scorecard totals
3. Trend arrow (improving / worsening / stable / first run)
4. Top 3 priority cleanup items
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
