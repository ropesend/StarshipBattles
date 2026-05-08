---
name: ocode-docs-audit
description: Documentation freshness & accuracy audit. Cross-references all docs/ file references against live code, PROJ statuses against projects_index.md, and doc "Last verified" timestamps against staleness thresholds. Finds dead references, stale PROJ mentions, undocumented modules, and stale docs. Produces a doc health scorecard with prioritized update plan. Read-only.
argument-hint: "[--skip-phase1 to reuse existing raw results]"
---

## Invocation

- **Slash command (interactive):** `/ocode-docs-audit`
- **CLI (non-interactive):** `opencode run "Load the ocode-docs-audit skill and execute it. Args: [optional --skip-phase1]"`

The skill is identical in both modes. CLI mode skips any user-prompt confirmations.

# Documentation Freshness & Accuracy Audit

Run a comprehensive audit of documentation quality across the entire `docs/` tree plus `AGENTS.md`, `CLAUDE.md`, and `.agents/CODEX.md`. Cross-references file paths, PROJ identifiers, and API mentions against live code to find stale references, dead documentation, and undocumented code. Produces a doc health scorecard with prioritized update plan.

Does NOT change any code or docs. Read-only audit.

## Pre-Flight Safeguards

Before starting any work:
1. **Run from repo root.** All paths are relative to the repository root.
2. **Check `git status --short`** and do NOT revert unrelated changes.
3. **Never read `docs/_ignore/`.** It is not documentation.
4. **Write only under `Reviews/results/`** and explicitly named `AgentCoordination/` paths.
5. **This is a read-only audit.** Do not edit source code, test code, or docs.

## Execution

This skill is a single-command workflow. The user loads it and you handle everything.

### Step 0: Pre-Flight Checks

Ensure the docs audit scanner exists:

```bash
python -c "import os; assert os.path.exists('Tools/docs_audit/docs_audit.py'), 'docs_audit.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself:**

```bash
python Tools/docs_audit/docs_audit.py
```

Capture `REVIEW_DIR` from stdout.

If the user passed `--skip-phase1`, find the most recent `Reviews/results/*_docs-audit/`.

The script creates `REVIEW_DIR/raw/` with these outputs:

1. `doc_file_refs.json` — every code/file path reference in docs (`game/*`, `Tools/*`, `Projects/protocols/*`, `Reviews/protocols/*`, `data/*`, `tests/*`) validated against filesystem
2. `stale_proj_refs.json` — PROJ references cross-referenced against projects_index.md
3. `doc_staleness.json` — "Last verified" timestamps with staleness scores
4. `undocumented_modules.json` — production modules > 50 LOC with no doc mention
5. `doc_inventory.json` — full doc file listing with headings for agent sharding

### Step 2: Read Phase 1 Outputs

Read these files into memory:

1. Read `REVIEW_DIR/raw/doc_file_refs.json`
2. Read `REVIEW_DIR/raw/stale_proj_refs.json`
3. Read `REVIEW_DIR/raw/doc_staleness.json`
4. Read `REVIEW_DIR/raw/undocumented_modules.json`
5. Read `REVIEW_DIR/raw/doc_inventory.json`

### Step 3: Launch 8 Agents in Parallel

Launch **8 agents**:
- **6 doc-group reviewers** (architecture docs, system docs, guides, root agent docs, project protocols, review protocols)
- **1 cross-doc consistency validator**
- **1 code-base accuracy validator**

**Doc-group assignments:**

| Group | Agent | Docs |
|-------|-------|------|
| G1 | Reviewer | `docs/README.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/04_SERVICES.md`, `docs/05_ERROR_HANDLING.md`, `docs/06_UI_STYLE_GUIDE.md` |
| G2 | Reviewer | `docs/systems/` (all 8 files: ability, ai, combat, orders, production, research, resource, strategy) |
| G3 | Reviewer | `docs/guides/` (all 8 files: adding abilities, modifiers, component system, testing, performance, etc.) |
| G4 | Reviewer | Root agent docs: `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md` |
| G5 | Reviewer | Project protocols: `Projects/protocols/` (all files) |
| G6 | Reviewer | Review protocols: `Reviews/protocols/` (all 11 protocol files) |

**Replace placeholders for each agent:**
- `{REVIEW_DIR}` → actual review directory
- `{group_id}` → `"G1"`, `"G2"`, ... `"G6"`
- `{group_label}` → group description
- `{doc_list}` → markdown list of doc files in this group
- `{dead_refs_path}` → `REVIEW_DIR/raw/dead_refs_{group_id}.json` (per-group filtered)
- `{stale_proj_refs_path}` → `REVIEW_DIR/raw/stale_proj_refs_{group_id}.json` (per-group filtered)
- `{stale_docs_path}` → `REVIEW_DIR/raw/stale_docs_{group_id}.json` (per-group filtered)
- `{undocumented_modules_path}` → `REVIEW_DIR/raw/undocumented_modules.json`

#### Agents 1-6: Doc-Group Reviewers

```
# Documentation Audit — Group {group_id}: {group_label}

You are reviewing ONE doc group: **{group_label}**.
You MUST read EVERY doc file assigned to this group.

## Your Doc Files
{doc_list}

## Deterministic Scan Results (per-group filtered files — read these yourself)

Read each of the following JSON files; they contain only entries scoped to your group:

- Dead file references (paths that don't exist): `{dead_refs_path}`
- Stale PROJ references (projects already completed/archived): `{stale_proj_refs_path}`
- Stale docs (last verified > 60 days ago): `{stale_docs_path}`
- Undocumented modules (>50 LOC, no doc mention; shared across groups): `{undocumented_modules_path}`

## Methodology
For EACH doc file in your group:

1. **Read the doc file** completely.
2. **Validate dead file references:**
   - For each dead `game/*` path: was the file renamed? Removed?
   - Check if the doc just needs the path updated, or if the referenced
     functionality was actually removed.
3. **Validate stale PROJ references:**
   - For each PROJ marked Complete/Archived but still referenced as
     "in progress" or "planned":
     - Should the doc section be marked as implemented?
     - Should the PROJ reference just be updated to show its final status?
4. **Check content accuracy against live code:**
   - For API/function signatures described in the doc: read the actual
     source file and compare.
   - For system behavior descriptions: spot-check against the actual
     implementation.
   - Flag any doc claim that contradicts the current code.
5. **Check for code examples that don't compile/run:**
   - If the doc contains Python code blocks, verify referenced functions,
     classes, and imports exist.
6. **Check for missing documentation:**
   - From the undocumented_modules list, identify which modules genuinely
     need documentation (public API surface > 50 LOC, or architectural
     surface modules that cross layer boundaries).
   - Focus on public API modules and architectural surface — do NOT flag
     every >50 LOC implementation detail.
7. **Assess scope gaps:**
   - Are there major game subsystems with no corresponding doc file?
   - Are there features added after the last doc update that never got
     documented?
8. **Validate `Last verified` line:**
   - Every doc file with an H1 should have a `> **Last verified:**` line
     under it per `docs/03_CONVENTIONS.md`. Flag missing or unparseable
     dates.
9. **Validate the deterministic reference extraction:**
   - Phase 1 has now extracted references from all known prefixes (`game/`,
     `Tools/`, `Projects/protocols/`, `Reviews/protocols/`, `data/`, `tests/`).
     Agents validate the deterministic findings rather than re-extracting.
   - For PROJ references: completed or archived PROJ refs are NOT stale if
     the surrounding text clearly states the feature is already implemented
     or the reference is historical context. Only flag PROJ refs that
     describe the feature as "planned" or "in progress" when the PROJ is
     already completed or archived.

## What NOT to Report
- Minor typos or grammar issues (unless they cause factual confusion)
- Formatting preferences (heading levels, list styles)
- "This doc should be split into multiple files" (out of scope)
- Missing examples for well-documented features

## Severity Guide
- CRITICAL: Doc describes behavior that NO LONGER EXISTS (will mislead
  developers); Dead reference to a core system file; PROJ reference that
  claims a feature is "planned" when it was completed months ago
- MAJOR: Stale API signature (function renamed/params changed); Doc
  last verified > 120 days ago; Undocumented major subsystem
- MINOR: Dead reference to a utility file; PROJ reference with slightly
  stale status; Doc last verified > 60 days but < 120 days

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/docs_review_{group_id}.md

# Documentation Review: {group_label}
## Summary
- Group: {group_label}
- Docs in Scope: [count]
- Docs Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Dead Reference Findings
#### {SEVERITY}: [Title]
**ID:** DOC-{group_id}-[NUMBER]
**Location:** doc_file.md:line
**Reference:** game/path/to/file.py
**Issue:** [what happened — renamed? removed?]
**Recommendation:** [update path to X / remove reference / mark as historical]
**LOC affected (doc):** N

## Stale PROJ Reference Findings
...

## Content Accuracy Findings
...

## Code Example Issues
...

## Missing Documentation
...

## Doc File Coverage Verification
| Doc File | Status | Findings |
|----------|--------|----------|
| [full doc file list with "Read ✓"] |
```

#### Agent 7: Cross-Doc Consistency Validator

```
# Cross-Doc Consistency Validator

Check for terminology drift, contradictory guidance, and inconsistent
cross-references between documentation files. Ensure the same concept
is described the same way everywhere.

## Scope
All docs/ files + AGENTS.md + CLAUDE.md.

## Methodology

1. **Terminology consistency:**
   - Extract key terms from each doc (e.g., "System", "Sector", "hex",
     "fleet", "formation", "battle", "combat").
   - Check that spatial terminology matches the AGENTS.md definitions:
     "System" = star system (~8000 hexes, radius 50), "Sector" = single hex.
   - Flag any doc that uses "System" to mean "Sector" or vice versa.
   - Check that "System scope" vs "Sector scope" is used consistently.

2. **Contradictory guidance:**
   - Compare conventions between AGENTS.md and docs/03_CONVENTIONS.md.
   - Compare pattern descriptions between docs/02_PATTERNS.md and
     docs/01_ARCHITECTURE.md (cross-references should agree).
   - Check that guides don't contradict reference docs.

3. **Cross-reference validation:**
   - When doc A says "see doc B for details", verify:
     a. Doc B exists
     b. The section/heading referenced in doc B actually exists
     c. The information in doc B is consistent with doc A's claim

4. **Duplicate documentation:**
   - Same concept documented in multiple places with different detail levels.
   - Recommend canonical location and cross-referencing strategy.

## Severity Guide
- CRITICAL: Contradictory guidance (e.g., one doc says "do X", another
  says "never do X"); Spatial terminology misuse that would cause bugs
- MAJOR: Cross-reference to non-existent section; same concept described
  with conflicting detail in two places
- MINOR: Minor terminology inconsistency; cross-reference that could be
  more specific

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/docs_consistency_cross.md

# Cross-Doc Consistency Report
## Summary
- Doc files analyzed: [N]
- Consistency issues found: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Terminology Issues
...

## Contradictory Guidance
...

## Cross-Reference Problems
...

## Duplicate Documentation
...

## Terminology Normalization Recommendations
[Canonical term table]
```

#### Agent 8: Code-Base Accuracy Validator

```
# Code-Base Accuracy Validator

Spot-check documentation claims against the actual source code. Read the
code to verify (or falsify) what the docs say.

## Scope
Sample-based. Read doc claims from the 6 reviewer reports, then verify
a representative sample against game/ source code.

## Methodology

1. **Collect all "content accuracy" claims** from the 6 doc-group reports.
2. **For each claim marked CRITICAL or MAJOR:**
   - Read the doc section referenced
   - Read the source code the doc describes
   - Verify: does the code match the doc's description?
3. **For claims marked MINOR:**
   - Sample every 3rd claim and verify.
4. **Rate each claim:**
   - CONFIRMED — the doc is indeed wrong/outdated
   - DISPUTED — the doc is actually correct (the reviewer misread either
     the doc or the code)
   - INCONCLUSIVE — cannot determine (code is too complex or ambiguous)

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/docs_accuracy_code.md

# Code-Base Accuracy Validation Report
## Summary
- Claims Reviewed: [N]
- Confirmed (doc wrong): [N]
- Disputed (doc correct): [N]
- Inconclusive: [N]

## Verified Accuracy Issues
### FILE: doc.md → game/path/file.py
**Claim:** [what the doc says]
**Actual:** [what the code actually does]
**Mismatch:** [description]
**Verified:** CONFIRMED

## Disputed Claims (Doc is Correct)
| Claim ID | Doc | Code | Why Disputed |
|----------|-----|------|-------------|

## Prioritized Doc Fixes
[Ordered by impact: dead references first, then content errors,
 then stale PROJ updates, then term normalization]
```

### Step 4: Verify Agent Outputs

Check that these 8 files exist:
- `REVIEW_DIR/findings/docs_review_G1.md`
- `REVIEW_DIR/findings/docs_review_G2.md`
- `REVIEW_DIR/findings/docs_review_G3.md`
- `REVIEW_DIR/findings/docs_review_G4.md`
- `REVIEW_DIR/findings/docs_review_G5.md`
- `REVIEW_DIR/findings/docs_review_G6.md`
- `REVIEW_DIR/findings/docs_consistency_cross.md`
- `REVIEW_DIR/findings/docs_accuracy_code.md`

### Step 5: Compile Final Report

Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Doc health score
- Dead references found (total), content errors (total)

**2. Doc Health Scorecard**
| Group | Docs | Dead Refs | Stale PROJs | Content Errors | Health |
|-------|------|-----------|-------------|---------------|--------|
| Architecture | 7 | | | | |
| Systems | 8 | | | | |
| Guides | 8 | | | | |
| Root Agent Docs | 3 | | | | |
| Project Protocols | * | | | | |
| Review Protocols | 11 | | | | |

**3. Dead Reference Register**
All confirmed dead file references with remediation.

**4. Stale PROJ Reference Register**

**5. Doc Staleness Register**
Docs past the 60-day verification threshold.

**6. Undocumented Modules**
Modules > 50 LOC with zero doc coverage.

**7. Cross-Doc Consistency Issues**

**8. Prioritized Documentation Update Plan**
Ordered by impact: dead references → content errors → stale PROJs → missing docs → terminology.
Sort dead refs and content errors first; within each, rank by doc importance
(root agent docs > architecture/conventions > systems > guides > protocols).
All findings still appear in the per-group registers above; this is ordering only.

**9. Trend Comparison**

Use the shared run tracker to compare this run against history and append a
trend table to the report:

```python
from Tools._audit_common import run_tracker
trend = run_tracker.compute_trend("Reviews/results", "docs", current_summary)
# Append run_tracker.render_trend_markdown(trend) here.
run_tracker.add_run("Reviews/results", "docs", current_summary)
```

**10. Appendices**
Paths to all raw and findings files.

### Step 6: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-docs-audit
```

### Step 7: Present to User

Show the user:
1. Doc health scorecard by group
2. Dead reference count + top 3 most critical
3. Content accuracy summary (confirmed vs disputed)
4. Undocumented module count
5. Stalest docs (longest since "Last verified")
6. Path to the full report

Do NOT start making code changes or doc edits. This is a read-only audit.
