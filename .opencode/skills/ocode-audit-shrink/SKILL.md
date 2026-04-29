---
name: ocode-audit-shrink
description: Run a comprehensive code shrinkage audit. Combines deterministic tools (vulture, radon, clone detector, orphans, dependency graph, LOC tracking) with 6 agents for deep review of all 4 shards, cross-shard duplication, and dead code validation. Produces a unified report with shrinkage estimates. Production code only.
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

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists from `shards.UI.files`, `shards.SIM.files`, `shards.STR.files`, `shards.FND.files` (all 4 shards are deep-reviewed every cycle)
2. Read `REVIEW_DIR/raw/clones.json` — clone detector clusters (get the full JSON content)
3. Read `REVIEW_DIR/raw/vulture_100.txt` — dead code candidates (get the full text)
4. Read `REVIEW_DIR/raw/vulture_80.txt` — high-likelihood dead code (get the full text)
5. Read `REVIEW_DIR/raw/radon.json` — complexity data (get the full JSON content)
6. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`

**Do NOT use orphans.txt or dead_deps.txt.** These tools are misconfigured/noisy (orphan detection uses wrong base path; dead_deps includes Projects/ and .agents/ which are not production code). Vulture output is the only reliable deterministic dead-code signal. All other dead code discovery must come from manual grep verification by agents.

### Step 3: Launch 6 Agents in Parallel

Create the findings directory:
```bash
mkdir -p REVIEW_DIR/findings
```

Launch **6 agents** in parallel using the Task tool with `subagent_type: general`:
- **1 cross-shard duplication agent** (scans all of game/)
- **4 in-shard deep review agents** (one per shard: UI, SIM, STR, FND)
- **1 dead code validator agent** (validates vulture/dead_deps/orphans)

Each agent receives EXACTLY the prompt template below with placeholder text replaced by actual data.

**Replace these placeholders in each template before sending:**
- `{REVIEW_DIR}` → the actual review directory (e.g., `Reviews/results/2026-04-27_133045_audit_shrink`)
- `{shard_id}` → the shard ID: `UI`, `SIM`, `STR`, or `FND`
- `{shard_label}` → from manifest.json `shards.{shard_id}.label` (e.g., "UI Layer", "Simulation Layer", "Strategy Layer", "Foundation Layer")
- `{shard_files}` → the files list from manifest.json `shards.{shard_id}.files`, formatted as markdown list
- `{clones_json}` → the full content of clones.json
- `{vulture_100}` → the full content of vulture_100.txt
- `{vulture_80}` → the full content of vulture_80.txt

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

#### Agents 2a–2d: In-Shard Deep Review (4 agents — one per shard)

Launch **4 agents** using the template below — one for each shard: UI, SIM, STR, FND. Replace `{shard_id}`, `{shard_label}`, and `{shard_files}` with the values from manifest.json for each shard. All 4 agents write to different output files: `deep_review_UI.md`, `deep_review_SIM.md`, `deep_review_STR.md`, `deep_review_FND.md`.

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
   - Functions/methods never called (check via grep in game/)
   - Classes never instantiated (check via grep in game/)
   - Unused imports
   - Unreachable branches (code after return/raise, always-true/false conditions)
3. **CRITICAL — Verify dead code before reporting it:**
   - After identifying something as potentially dead, grep tests/ for the symbol name
   - Grep docs/ for the symbol name
   - Check data/*.json for related configuration (e.g. data/group_policies.json might wire a "dead" group coordinator)
   - If the symbol is referenced in tests or docs, downgrade it to PRODUCT_DECISION — the code is unwired planned infrastructure, not truly dead
   - PRODUCT_DECISION means: the code exists, tests/docs reference it, but no production code path reaches it. A product decision is needed: wire it or remove all references
   - Only mark as CRITICAL dead code if neither tests, docs, data files, nor production code reference the symbol
4. **Check for internal duplication:**
   - Repeated code blocks within the same file
   - Methods that could be refactored into a helper
5. **Check for fragmentation:**
   - A single responsibility split across this file and others in the same shard
   - Related helper functions spread across unrelated modules
   - Partial implementations that should be consolidated
6. **Check for code quality issues that bloat LOC:**
   - Overly verbose patterns (if/elif chains where a dict lookup would work)
   - Repeated inline constants that should be module-level
   - Functions that could be simplified with stdlib (itertools, collections)

## What NOT to Report
- Unit tests (ignore tests/ completely)
- Comments/docstrings being too long
- Test fixtures or test-only code
- Code already marked for deprecation

## Severity Guide
- CRITICAL: True dead code — no references in production, tests, OR docs. Safe to delete.
- PRODUCT_DECISION: Appears dead in production, but tests, docs, or data files reference it. Needs product decision: wire it or remove all references.
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
- Critical: [N] | Product Decision: [N] | Major: [N] | Minor: [N] | Info: [N]

## Dead Code Findings
#### {SEVERITY}: [Title]
**ID:** DEEP-{shard_id}-[NUMBER]
**Location:** file.py:lines
**Issue:** [description]
**Estimated LOC:** [N]
**Tests reference?** [Yes/No — file:line if yes]
**Docs reference?** [Yes/No — file:line if yes]
**Recommendation:** [what to do]

## Product Decision Required
Items that appear dead in production but are referenced by tests/docs/data:
| ID | Item | LOC | Test Refs | Doc Refs | Data Refs | Recommendation |
|----|------|-----|-----------|----------|-----------|----------------|
| | | | | | | |

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

Validate dead code candidates from vulture's static analysis against actual usage
in the production codebase AND test/documentation references. Filter false positives,
confirm true positives, cross-reference against docs/tests/data, and produce a
prioritized dead code inventory.

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

NOTE: Do NOT use orphans.txt or dead_deps.txt. These tools are misconfigured
(orphan detection uses wrong base path; dead_deps includes Projects/ and
.agents/ which are not production code). Vulture is the only reliable
deterministic dead-code signal.

## Methodology

For EACH dead code candidate:

1. **Verify with grep**: Search game/ for references
2. **Check tests/**: Grep tests/ for the symbol. If referenced in tests, do NOT
   report as dead — downgrade to PRODUCT_DECISION.
3. **Check docs/**: Grep docs/ for the symbol. If referenced in docs, do NOT
   report as dead — downgrade to PRODUCT_DECISION.
4. **Check data/*.json**: Does a data file configure or expect this symbol?
   (e.g. data/group_policies.json for group targeting behavior)
5. **Check dynamic dispatch**: Registry lookups, string-based dispatch, getattr
6. **Check TYPE_CHECKING blocks**: Imported only under `if TYPE_CHECKING`?
7. **Check command/ability registries**: Classes instantiated via registry
8. **Check __init__.py re-exports**: Is it re-exported?

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
- Product Decision Required: [N]
- False Positives: [N]
- Documentation Discrepancies: [N]

## Confirmed Dead Code (no tests, docs, or production references)

### Tier 1: Dead Files (delete entire files)
| File | Source | LOC | Test refs? | Doc refs? | Verified? |
|------|--------|-----|------------|-----------|-----------|

### Tier 2: Dead Classes (remove from files)
| Class | File:Line | Source | LOC | Test refs? | Doc refs? | Verified? |
|-------|-----------|--------|-----|------------|-----------|-----------|

### Tier 3: Dead Functions/Methods
| Function | File:Line | Source | LOC | Test refs? | Doc refs? | Verified? |
|----------|-----------|--------|-----|------------|-----------|-----------|

### Tier 4: Dead Imports
| Import | File:Line | Source | Test refs? | Doc refs? | Verified? |
|--------|-----------|--------|------------|-----------|-----------|

## Product Decision Required
Items with zero production callers but referenced by tests or docs:
| Item | File:Line | Production refs | Test refs | Doc refs | Recommendation |
|------|-----------|-----------------|-----------|----------|----------------|

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

After all 6 agents complete, check that these 6 files exist and are non-empty:

- `REVIEW_DIR/findings/duplication_cross_shard.md`
- `REVIEW_DIR/findings/deep_review_UI.md`
- `REVIEW_DIR/findings/deep_review_SIM.md`
- `REVIEW_DIR/findings/deep_review_STR.md`
- `REVIEW_DIR/findings/deep_review_FND.md`
- `REVIEW_DIR/findings/dead_code_validation.md`

If any agent failed, note it in the report but continue with available data.

### Step 4b: Cross-Verification Round

Launch **1 verification agent** to cross-check all CRITICAL dead-code findings against tests/, docs/, and data/*.json. This agent reads all dead-code findings (CRITICAL items from deep review reports + Agent 3 findings) and verifies each one.

```
# Dead Code Cross-Verifier

Read these files:
1. REVIEW_DIR/findings/deep_review_UI.md
2. REVIEW_DIR/findings/deep_review_SIM.md
3. REVIEW_DIR/findings/deep_review_STR.md
4. REVIEW_DIR/findings/deep_review_FND.md
5. REVIEW_DIR/findings/dead_code_validation.md

For EVERY finding marked CRITICAL (should delete code):

1. Grep tests/ for the symbol/file name
2. Grep docs/ for the symbol/file name
3. Check data/*.json for related configuration
4. Check if the file is a "planned but unwired" system (referenced by docs/tests/data)

Downgrade findings based on evidence:
- No test/doc/data references → keep as CRITICAL
- Test references only → PRODUCT_DECISION (test-only infrastructure)
- Doc references only → PRODUCT_DECISION (documented but unwired)
- Test + doc references → PRODUCT_DECISION (planned feature, not dead)
- Data file configures it → PRODUCT_DECISION (infrastructure exists)

Output a verification report to:
REVIEW_DIR/findings/verification.md

# Cross-Verification Report
## Critical Finding Verification
| Finding ID | Symbol | Test refs? | Doc refs? | Data refs? | Verdict |
|------------|--------|------------|-----------|------------|---------|
| | | | | | |

## Downgraded to Product Decision
[List items that should NOT be deleted because tests/docs/data reference them]

## Confirmed Safe Deletions
[List items with zero references anywhere — truly dead code]
```

After the verification agent completes, use its report to adjust the severity of findings in the final report. Items downgraded to PRODUCT_DECISION should appear in a separate table, not in the dead-code inventory.

### Step 5: Compile Final Report

Read all agent reports and the verification report. Write `REVIEW_DIR/report.md` with these sections:

**1. Executive Summary**
- Date, review directory
- Total findings across all sources
- Trend comparison to previous run (use shrink_tracker.py)
- All 4 shards deep-reviewed every cycle

**2. Coverage Status**
| Shard | Files | LOC | Deep Review File | Status |
|-------|-------|-----|-----------------|--------|
| UI | [N] | [N] | `deep_review_UI.md` | ✓ |
| SIM | [N] | [N] | `deep_review_SIM.md` | ✓ |
| STR | [N] | [N] | `deep_review_STR.md` | ✓ |
| FND | [N] | [N] | `deep_review_FND.md` | ✓ |

**3. Dead Code Inventory**
Aggregate Agent 3's confirmed dead code by tier with LOC estimates.
Apply verification downgrades: items the verifier moved to PRODUCT_DECISION go in §3b, not here.

**3b. Product Decision Required**
Items that appear dead in production but are referenced by tests, docs, or data files:
| Item | File | LOC | Ref Type | Source | Recommendation |
|------|------|-----|----------|--------|----------------|

**4. Duplication Clusters**
Aggregate Agent 1's findings, grouped by severity.

**5. Complexity Hotspots**
From raw/radon.json, all functions with CC >= 20.

**6. In-Shard Deep Review Summary**
From all 4 deep review agent reports, summarize findings per shard + coverage verification.
Separate dead-code from product-decision findings.

**7. Shrinkage Scorecard**
| Category | Estimated Reclaimable LOC | Effort | Risk |
|----------|--------------------------|--------|------|
| Dead files (verified safe) | [N] | Simple | Safe |
| Dead classes/functions (verified safe) | [N] | Simple | Safe |
| Dead imports | [N] | Simple | Safe |
| Duplicate consolidation | [N] | Medium-High | Needs design |
| Complexity reduction | [N] | Medium-High | Needs care |
| In-shard cleanup (UI) | [N] | Low-Medium | Safe |
| In-shard cleanup (SIM) | [N] | Low-Medium | Safe |
| In-shard cleanup (STR) | [N] | Low-Medium | Safe |
| In-shard cleanup (FND) | [N] | Low-Medium | Safe |
| Product decision items (not counted yet) | [N] | — | Needs decision |
| **Total (safe items only)** | **[N]** | | |

**8. Prioritized Cleanup Plan**
Top 10 items ordered by impact/effort. Only include verified-safe items here.

**9. Trend Comparison**
Use shrink_tracker.py to compare with previous run.

**10. Appendices**
Paths to raw tool outputs, agent reports, and verification report.

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
    "deep_review_shards": ["UI", "SIM", "STR", "FND"],
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
2. Shrinkage scorecard totals (all 4 shards covered)
3. Trend arrow (improving / worsening / stable / first run)
4. Top 3 priority cleanup items
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
