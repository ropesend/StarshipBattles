---
name: audit-shrink
description: Run a comprehensive code shrinkage audit. Combines deterministic tools (vulture, radon, clone detector, orphans, dependency graph, LOC tracking) with 3 agents for semantic duplication and dead code review. Produces a unified report with shrinkage estimates. Production code only.
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

### Phase 1: Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/audit_shrink/audit_shrink.py
```

Capture the last line of stdout which prints the output directory path. This is `REVIEW_DIR`.

The script creates `REVIEW_DIR/raw/` with these outputs against `game/`:

1. `loc_baseline.txt` — baseline LOC by section
2. `vulture_100.txt` — dead code at 100% confidence
3. `vulture_80.txt` — dead code at 80% confidence
4. `orphans.txt` — modules nothing imports
5. `dead_deps.txt` — unreachable files from entry points
6. `radon.json` — complexity hotspots (CC >= 11)
7. `clones.json` — AST near-duplicate function clusters
8. `manifest.json` — file inventory + shard rotation

### Phase 2: Agent-Driven Semantic Review

Read the raw outputs into memory:

1. Read `raw/manifest.json` — note the `deep_review_shard` field (UI, SIM, STR, or FND) and the file list for that shard
2. Read `raw/clones.json` — clone detector clusters to hand to Agent 1
3. Read `raw/vulture_100.txt` and `raw/vulture_80.txt` — dead code candidates for Agent 3
4. Read `raw/orphans.txt` and `raw/dead_deps.txt` — orphan/unreachable modules for Agent 3
5. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`

Launch **3 agents** in parallel using the Task tool. Each agent uses EXACTLY the prompt template assigned below.

**Before launching**, replace these placeholders in each template:
- `{REVIEW_DIR}` → the actual review directory (e.g., `Reviews/results/2026-04-27_093015_audit_shrink`)
- `{shard_id}` → from manifest.json `deep_review_shard` (UI, SIM, STR, or FND)
- `{shard_label}` → from manifest.json `shards.{shard_id}.label`
- `{shard_files}` → from manifest.json `shards.{shard_id}.files` (formatted as a list)

Agents MUST use the Write tool to save their report.

#### Agent 1 Prompt: Cross-Shard Duplication

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
[Paste contents of raw/clones.json here]

## Scope
All files under game/ (ui/, simulation/, strategy/, core/, engine/, ai/, research/).

## Methodology

### Phase 1: Validate Clone Detector
- For each cluster in clones.json, read the implicated files
- Verify the functions are genuinely similar (not false positives from similar
  structural fingerprints with different semantics)
- Assess whether consolidation is feasible or if the similarity is superficial
- For confirmed clusters, estimate LOC savings from consolidation

### Phase 2: Hunt Cross-Shard Duplication
Scan for these patterns across shard boundaries:
- Same concept implemented differently in multiple layers (e.g., "find nearest
  hex" logic in both strategy/ and simulation/)
- Utility functions copy-pasted between ui/, strategy/, and simulation/
- Multiple serialization/deserialization approaches for the same data
- Multiple validation routines for the same kind of input
- Multiple distance/position calculations
- Multiple "find best" or "select by criteria" algorithms
- Multiple ways to format the same kind of display text

### Phase 3: Copy-Paste Drift
Find code that was clearly copy-pasted then diverged:
- Similar function bodies with slightly different variable names
- Methods sharing 80%+ structure but with small differences
- UI rendering functions repeating layout logic with different content
- Helper functions duplicated across modules with minor variations

## Severity Guide
- CRITICAL: Same business logic in 3+ places with active divergence (bugs likely hiding)
- MAJOR: Significant code blocks (>20 lines) duplicated in 2+ places
- MINOR: Small utility duplication or low-risk copy-paste patterns
- INFO: Observations about natural similarity that may not warrant consolidation

## Output
You MUST use the Write tool to save your report to:
Reviews/results/{REVIEW_DIR}/findings/duplication_cross_shard.md

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
**Layer:** [e.g., simulation -> strategy, or ui -> strategy]
**Issue:** [description]
**Impact:** [maintenance risk]
**Recommendation:** [how to consolidate]
**Estimated LOC Savings:** [N]
**Effort:** [Simple/Medium/Complex]

## Prioritized Consolidation Plan
[Ordered by impact/effort ratio]
```

#### Agent 2 Prompt: In-Shard Deep Review

```
# In-Shard Deep Review Agent

You are assigned ONE shard this run: **{shard_label}**.
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/02_PATTERNS.md and docs/03_CONVENTIONS.md.

## Scope
All files listed below MUST be read. If you skip any file, the coverage
guarantee is broken for this cycle.

Shard file list:
[Paste the files array from raw/manifest.json shards.{shard_id}.files here]

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
   - Overly verbose patterns (e.g., if/elif chains where a dict lookup would work)
   - Repeated inline constants that should be module-level
   - Functions that could be simplified with stdlib (e.g., itertools, collections)

## What NOT to Report
- Unit tests (ignore tests/ completely)
- Comments/docstrings being too long (those are fine)
- Test fixtures or test-only code
- Code already marked for deprecation (with clear comments)

## Severity Guide
- CRITICAL: True dead code that is importable and callable but never reached
- MAJOR: Significant internal duplication or fragmentation (>30 lines)
- MINOR: Small dead code (individual imports, short dead functions)
- INFO: Style suggestions that would reduce LOC without changing behavior

## Output
You MUST use the Write tool to save your report to:
Reviews/results/{REVIEW_DIR}/findings/deep_review_{shard_id}.md

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

#### Agent 3 Prompt: Dead Code Validator

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
[Paste contents of raw/vulture_100.txt here]

### Vulture 80% Confidence (high-likelihood):
[Paste contents of raw/vulture_80.txt here]

### Orphan Modules (no imports from other game/ modules):
[Paste contents of raw/orphans.txt here]

### Unreachable Files (not reachable from launcher.py or game/app.py):
[Paste contents of raw/dead_deps.txt here]

## Methodology

For EACH dead code candidate:

1. **Verify with grep**: Search the entire game/ directory for references to
   the flagged class/function/variable.
2. **Check dynamic dispatch**: Is the code used via registry lookup, string-based
   dispatch, or `getattr`? These won't be caught by static analysis.
3. **Check TYPE_CHECKING blocks**: Is it imported only under `if TYPE_CHECKING`?
   Flag as low-priority but still noted.
4. **Check command/ability registries**: Classes may be instantiated via
   `CommandHandlerRegistry`, component ability registries, or similar patterns.
5. **Check docs/**: Does any docs/ file reference this code? If yes, flag the
   documentation discrepancy.
6. **Check __init__.py re-exports**: Is it re-exported from an __init__.py?

## False Positive Patterns (do NOT report as dead)
- Pytest fixtures and test utilities (but we're scanning game/, not tests/)
- Protocol/ABC classes used in isinstance() checks or type annotations
- Command classes instantiated via registry dispatch
- Factory functions called from tests
- `__exit__` parameters (exc_type, exc_val, exc_tb)
- Signal/slot connections in UI code

## Output
You MUST use the Write tool to save your report to:
Reviews/results/{REVIEW_DIR}/findings/dead_code_validation.md

# Dead Code Validation Report
## Summary
- Total Candidates Reviewed: [N]
- Confirmed Dead: [N]
- False Positives: [N] (with explanation)
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

### Phase 3: Compile Final Report

After all 3 agents complete, verify their output files exist in `findings/`.

Read all findings and compile `report.md` at the review directory root. The report MUST contain these sections:

**1. Executive Summary**
- Date, run type, review directory path
- Total findings across all sources
- Trend comparison to previous run (use shrink_tracker.py)
- Shard rotation status (which shard got deep review, what % of cycle is complete)

**2. Coverage Status**

Reproduce the 4-shard table from manifest.json:
| Shard | Files | Last Deep Review | This Run |
|-------|-------|-----------------|----------|

**3. Dead Code Inventory**

Aggregate Agent 3's confirmed dead code by tier. Include LOC estimates.
Add a summary table:
| Tier | Count | Estimated LOC |
|------|-------|---------------|

**4. Duplication Clusters**

Aggregate Agent 1's findings. Group by severity. Include cross-shard pairs flagged.
Add a summary table:
| Severity | Cluster Count | Total Duplicated LOC |
|----------|---------------|---------------------|

**5. Complexity Hotspots**

From raw/radon.json, list all functions with CC >= 20. Note any that overlap with
duplication clusters (these are the highest priority — they're complex AND duplicated).

**6. In-Shard Deep Review Summary**

From Agent 2's report, summarize the top findings by category (dead code, internal
duplication, fragmentation, quality). Include coverage verification — confirm every
file in the shard was read.

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

Top 10 highest-impact items, ordered by `impact ÷ effort`, safest first:
| Rank | Category | Item | LOC | Effort | Risk |
|------|----------|------|-----|--------|------|

**9. Trend Comparison**

Use shrink_tracker.py compute_trend() to generate:
- Direction arrow
- Delta table for key metrics
- Run history summary

**10. Appendices**

- Paths to raw tool outputs
- Paths to agent reports
- Link to shrink_tracker.json

### Phase 4: Update Shrink Tracker

After the report is written, update the shrink tracker:

```python
from Tools.audit_shrink import shrink_tracker
import json

# Load manifest
with open("Reviews/results/{REVIEW_DIR}/raw/manifest.json") as f:
    manifest = json.load(f)

# Count dead code from Agent 3 report
# Count duplication clusters from Agent 1 report
# Read radon.json for complexity stats

run_data = {
    "date": "[YYYY-MM-DD]",
    "review_dir": "{REVIEW_DIR}",
    "deep_review_shard": manifest["deep_review_shard"],
    "rotation_index": manifest["rotation_index"],
    "production_loc": [read from loc_baseline],
    "dead_code_files": [count from Agent 3 Tier 1],
    "dead_code_functions": [count from Agent 3 Tier 2+3],
    "dead_code_imports": [count from Agent 3 Tier 4],
    "duplication_clusters": [count from Agent 1],
    "estimated_shrinkable_loc": [sum from scorecard],
    "top_hotspots": [top 5 files by finding count],
}

shrink_tracker.add_run("Reviews/results", run_data)
```

### After the Report

Present the user with:
1. Executive summary (3-4 sentences)
2. Shrinkage scorecard totals
3. Trend arrow
4. Top 3 priority cleanup items
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
