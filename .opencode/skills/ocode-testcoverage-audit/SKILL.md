---
name: ocode-testcoverage-audit
description: Comprehensive test coverage audit across the entire production codebase. Phase 1 deterministic AST scanner precomputes coverage tiers and shards. Phase 2 launches one-per-shard discovery agents that read every production file + corresponding unit tests, verifying coverage and identifying untested branches, error paths, and corner cases. Phase 3 launches one-per-shard skeptical verification agents that exhaustively verify CRITICAL/MAJOR claims and sample MINOR/ADVISORY claims. Phase 4 compiles a final report with prioritized test case suggestions. Production code only.
argument-hint: "[optional: --skip-phase1 to reuse existing raw results]"
---

# Test Coverage Audit

Run a comprehensive, line-by-line audit of unit test coverage across every production file in `game/`. Combines a deterministic Phase 1 AST scanner (to precompute coverage tiers and shard files) with one-per-shard discovery agents that read every production file and its unit tests to identify untested code paths, and one-per-shard skeptical verification agents that exhaustively verify CRITICAL/MAJOR claims and sample MINOR/ADVISORY claims. Produces a prioritized test case catalog with specific test descriptions for every verified gap.

Does NOT change any code. Targets `game/` only (not tests, not tools). Only `tests/unit/` counts as coverage.

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

Log skill usage first (advisory counter, should reflect invocation even on failure):

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-testcoverage-audit
```

Ensure the Phase 1 script exists:

```bash
python -c "import os; assert os.path.exists('Tools/testcoverage_audit/testcoverage_audit.py'), 'testcoverage_audit.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
python -c "from pathlib import Path; Path('Reviews/results').mkdir(parents=True, exist_ok=True)"
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/testcoverage_audit/testcoverage_audit.py --shards 18 --max-loc-per-shard 10000
```

The `--shards` value is a TARGET — the script may auto-increase shard count (up to 40) if `--max-loc-per-shard` is exceeded. Always read the actual shard count from the manifest after the run.

Capture the last few lines of stdout. Look for the line that prints the output directory path:
```
Output directory: Reviews/results/2026-05-04_175101_testcoverage-audit
```

Store this as `REVIEW_DIR`. Also capture the actual shard count as `{SHARD_COUNT}` from the manifest output line:
```
  18 shards (target: 18, max LOC/shard: 10000)
```

Future extension point: a later scanner CLI may add `--coverage-json <path>` to consume `coverage.py` output as an additional baseline. This is not currently implemented or required — the import-based + name-grep heuristic is the default.

If the user passed `--skip-phase1`, find the most recent review directory:
- Glob: `Reviews/results/*_testcoverage-audit/`
- Sort by directory name, take the newest
- Use that as `REVIEW_DIR`
- Validate the raw output schema before continuing. `coverage_matrix.json` entries
  must contain `candidate_test_files`, and each `symbol_coverage` entry must contain
  `heuristic_match`. If the newest directory uses the old `test_files`/`mentioned`
  schema, rerun Phase 1 instead of reusing it.

The script creates `REVIEW_DIR/raw/` with these outputs:

1. `coverage_matrix.json` — per-production-file: `candidate_test_files` (import-based, heuristic), `symbol_coverage` with `heuristic_match` flags, `coverage_tier` (0-3)
2. `layer_summary.json` — coverage statistics by architectural layer
3. `file_inventory.json` — full production file inventory
4. `manifest.json` — shard file assignments for agent distribution; `shard_count` is the authoritative count

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory for use in agent prompts:

1. Read `REVIEW_DIR/raw/manifest.json` — extract `shard_count` and ALL shard file lists from `shards.01.files` through `shards.{SHARD_COUNT}.files`
2. Read `REVIEW_DIR/raw/coverage_matrix.json` — the full coverage data for every production file (note: all Phase 1 evidence is heuristic — `candidate_test_files` are import-based matches, `heuristic_match` is name-grep, NOT proof of coverage)
3. Read `REVIEW_DIR/raw/layer_summary.json` — layer-level statistics
4. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`

### Step 3: Launch Phase 2 — Discovery Agents (batches of up to 6)

Create the findings directory:

```bash
python -c "from pathlib import Path; Path(r'{REVIEW_DIR}').joinpath('findings').mkdir(parents=True, exist_ok=True)"
```

Launch **one agent per shard** using the Task tool with `subagent_type: general`. Batch agents in groups of up to 6, launching each batch in parallel and waiting for all to complete before starting the next batch.

```
BATCH_COUNT = ceil(SHARD_COUNT / 6)
For each batch:
    launch min(6, SHARD_COUNT - batch*6) agents in parallel
    wait for all to complete
```

**Replace these placeholders** in the template below for each agent:
- `{SHARD_ID}` → `"01"`, `"02"`, … `"{SHARD_COUNT:02d}"`
- `{SHARD_LABEL}` → from manifest.json `shards.{SHARD_ID}.label` (e.g., "Shard 01")
- `{FILE_COUNT}` → from manifest.json `shards.{SHARD_ID}.file_count`
- `{LOC_ESTIMATE}` → from manifest.json `shards.{SHARD_ID}.loc_estimate`
- `{FILE_LIST}` → the files list from manifest.json `shards.{SHARD_ID}.files`, formatted as a markdown bullet list with coverage tier annotations
- `{COVERAGE_MATRIX_SHARD}` → from coverage_matrix.json, ONLY the entries for files in this shard
- `{REVIEW_DIR}` → the actual review directory path

#### Discovery Agent Template

```
# Test Coverage Audit — Shard {SHARD_ID} Discovery Agent

You are auditing unit test coverage for ONE shard of production code.
You MUST exhaustively read EVERY production file in this shard, then read
their corresponding unit test files. For every function, method, and class,
verify that adequate unit testing exists. Report every gap in detail.

## Documentation Reference
Read docs/01_ARCHITECTURE.md, docs/02_PATTERNS.md, and docs/03_CONVENTIONS.md.
Pay special attention to registry patterns, CQRS-lite patterns, and two-phase
ability aggregation — code following these patterns may be exercised through
indirect paths that the Phase 1 scanner cannot detect.

## Your Shard: {SHARD_LABEL}

**Files in scope**: {FILE_COUNT} production files, ~{LOC_ESTIMATE} LOC

You MUST read EVERY file below. Do not skip any.

{FILE_LIST}

## Pre-Computed Coverage Data

The Phase 1 deterministic scanner mapped imports and performed name-grep
symbol matching. **All Phase 1 data is heuristic — it is NOT proof of
coverage.** Fields are:
- `candidate_test_files`: test files that import this module (import-based match)
- `heuristic_match`: symbol name appears in a candidate test file (name-grep)

This data is a STARTING POINT — you must VERIFY it, not blindly trust it.

Coverage matrix for your shard (abbreviated — agents should read the full
coverage_matrix.json entries for each file they are assigned):

{COVERAGE_MATRIX_SHARD}

## Methodology

For EACH production file in your shard:

### Step A: Read the Production File
Read the file completely. Understand what it does and how it interacts
with other modules.

### Step B: Read the Corresponding Unit Tests
For each test file listed in the coverage matrix as a candidate (importing this
module), read it completely. If the coverage matrix lists NO candidate test files
(Tier 0), note this as a CRITICAL gap and move to the next file.

### Step C: Verify Coverage Claims
For each callable definition (function, method, class) in the production
file, check:
1. Does at least one unit test exercise this symbol?
2. Does the test actually verify behavior (not just import/instantiate)?
3. Does the test exercise the MAIN code paths, or only trivial paths?

Correct the Phase 1 data where you find false positives or negatives.

### Step D: Deep Code Path Analysis
For each function/method that HAS tests, trace all code paths:

1. **Branch coverage**: Every `if/elif/else` branch tested?
2. **Loop coverage**: Empty iterables tested? Single-element? Multi-element?
3. **Error paths**: Exception-raising paths exercised?
4. **Null/None handling**: `None` inputs tested where relevant?
5. **Boundary values**: Edge cases tested (0, -1, max, empty string)?
6. **Default parameters**: Different combinations of defaults vs explicit args tested?
7. **Return types**: All possible return types/paths verified?
8. **Side effects**: Mutations, state changes verified?

### Step E: Identify Untested Corner Cases
For each gap found, describe specifically what is untested and what kind
of test is needed. Be precise — name the function, the untested path, and
suggest a test description.

### Step F: UI Layer Special Handling
For files under `game/ui/`:
- **Pygame rendering/event code**: Flag as `ADVISORY` severity with a note
  that UI rendering and event handlers are conventionally tested via
  manual/integration testing, not unit tests
- **UI business logic**: Calculations, data transforms, validation logic
  in UI files should be flagged at standard severity — this IS testable
- **Layout/positioning code**: `ADVISORY` severity

## What NOT to Report
- Test quality issues (this is a coverage audit, not test quality)
- Files you couldn't read due to context constraints (note them in coverage
  verification table but don't fabricate findings)
- `__init__.py` files that only re-export symbols (note them as LOW_PRIORITY)
- Dunder methods (`__str__`, `__repr__`) unless they contain non-trivial logic

## Severity Guide
- **CRITICAL**: Tier 0 file (zero unit tests import this module) in any non-UI layer
  (Core, Engine, Simulation, Strategy, AI, Research, Services, Assets, Game Root).
  Core business logic with zero coverage. Allowed downgrades: generated code, glue
  files, `__init__.py` re-exports, simple data classes with no logic.
- **MAJOR**: Tier 1 file (imported but no symbols tested). Function with untested
  error paths or missing boundary condition tests that could hide production bugs.
- **MINOR**: Partially tested function missing some branches. Minor corner case
  not covered but unlikely to cause production issues.
- **ADVISORY**: UI rendering/event code (files under `game/ui/` where the code is
  pygame drawing, event handling, or layout). `__init__.py` re-exports. Code that
  is inherently hard to unit test and conventionally verified via other means.
  Note: UI files that contain testable business logic (calculations, data transforms,
  validation) should be flagged at standard severity — only the rendering/event
  portions get ADVISORY.

## Output — Save to: {REVIEW_DIR}/findings/SHARD_{SHARD_ID}.md

You MUST use the Write tool to save your report.

Use EXACTLY this structure:

```
# Shard {SHARD_ID} — Test Coverage Audit

## Summary
- Shard: {SHARD_ID}
- Production files in scope: {FILE_COUNT}
- Production files actually read: [COUNT — MUST equal scope]
- Unit test files read: [COUNT]
- Total findings: [N]
- Critical: [N] | Major: [N] | Minor: [N] | Advisory: [N]

## Tier 0 — Zero Unit Tests (CRITICAL for non-UI, ADVISORY for UI)

### game/path/to/file.py (~N LOC, layer: X)
- **Status**: No unit test file imports this module
- **Key symbols**: [list of untested functions/classes]
- **Risk**: [what could break without detection]
- **Suggested tests**:
  1. `test_<function>` — [specific description of what to test]
  2. ...

## Tier 1-2 — Partial Coverage

### game/path/to/file.py (~N LOC, layer: X)

#### [CRITICAL] `function_name` — Completely untested
- **Location**: file.py:line_range
- **Issue**: Function imported by test files but no test exercises it
- **Suggested test**: [specific description]

#### [MAJOR] `function_name` — Missing error-path test
- **Location**: file.py:line_range
- **Issue**: Happy path tested but `try/except` branch never triggered
- **Untested path**: [specific code path, conditions]
- **Suggested test**: [specific description with input values]

#### [MINOR] `function_name` — Missing boundary test
- **Location**: file.py:line_range
- **Issue**: Normal inputs tested but empty list not handled
- **Suggested test**: [specific description]

### game/ui/path/to/file.py (~N LOC, layer: ui)

#### [ADVISORY] `render_method` — UI rendering code
- **Location**: file.py:line_range
- **Issue**: pygame rendering code — conventionally tested via manual/integration
- **Note**: [if any business logic within the method is also untested, flag it]

## Tier 3 — Verified Coverage (no new gaps)

### game/path/to/file.py (~N LOC, layer: X)
- **Status**: Phase 1 indicated full coverage. Verified: [CONFIRMED / PARTIAL — found N gaps]
- [List any gaps found that Phase 1 missed]

## File Coverage Verification
| File | Layer | Tier | Status | Findings |
|------|-------|------|--------|----------|
| game/path/to/file.py | core | 0 | Read ✓ | N |
| [every assigned file with Read ✓ and finding count] |

## Context Usage Estimate
- Total production LOC read: [N]
- Total test LOC read: [N]
- Approximate headroom: High (>500K) | Medium (200-500K) | Low (<200K)
- Partially-read files (if any): [list with reason]
```

## Rules
1. Read EVERY production file in your shard — no exceptions
2. For each production file, read the test files listed in the coverage matrix
3. If a file has zero findings, still list it in File Coverage Verification
4. Be specific with line ranges — cite actual line numbers
5. Do NOT skip UI files because they're "hard to test" — read them and apply
   the ADVISORY severity where appropriate
6. If context becomes constrained, prioritize Tier 0 and Tier 1 files over
   Tier 2/3 files. Note any partially-read files in the coverage table.
7. Phase 1 data is a STARTING POINT — you are the authority. Correct it.
```

### Step 4: Verify Phase 2 Completion

After all batches complete, check that all shard report files exist and are non-empty:

- `REVIEW_DIR/findings/SHARD_01.md` through `REVIEW_DIR/findings/SHARD_{SHARD_COUNT:02d}.md`

Use Read with limit=1 to verify each file exists and has content. If any agent failed, note which shard and proceed with available data. Re-launch failed shards if feasible.

### Step 5: Launch Phase 3 — Skeptical Verification (batches of up to 6)

Launch **one verification agent per shard** using the Task tool with `subagent_type: general`. Batch in groups of up to 6, same as Phase 2. Each verifier gets its shard's Phase 2 report and must independently verify every CRITICAL and MAJOR claim, then sample MINOR and ADVISORY claims.

**Replace these placeholders** for each agent:
- `{SHARD_ID}` → `"01"`, `"02"`, … `"{SHARD_COUNT:02d}"`
- `{REVIEW_DIR}` → the actual review directory path

#### Verification Agent Template

```
# Test Coverage Audit — Shard {SHARD_ID} Skeptical Verifier

You are the SKEPTICAL VERIFIER for Shard {SHARD_ID}. Your job is to
independently verify every CRITICAL and MAJOR claim made by the Phase 2
discovery agent, then verify sampled MINOR and ADVISORY claims.
You must read the cited production code AND test code before confirming.

You are skeptical. If a claim is overstated, false, or unverifiable,
DISPUTE it with a specific reason drawn from the source code.

## Inputs You Must Read
1. **Phase 2 report**: {REVIEW_DIR}/findings/SHARD_{SHARD_ID}.md — all
   CRITICAL/MAJOR claims plus sampled MINOR/ADVISORY claims
2. **The actual production files** cited in each claim — read the cited line
   ranges PLUS at least 10 lines of surrounding context
3. **The actual test files** cited in each claim — read enough to verify
   whether the test actually exercises (or fails to exercise) the claimed code

## Verification Methodology

For each claim selected for verification from the Phase 2 shard report:

### For CRITICAL claims (Tier 0 — zero unit tests):
1. **Read the production file** at the cited lines
2. **Grep tests/unit/ for the production module name** — could the Phase 1
   scanner have missed an indirect import (e.g., via parent package)?
3. **Check if the module is tested via a sibling module's tests** — e.g.,
   `game/core/math.py` might be tested via `tests/unit/core/test_hex_math.py`
   if the latter imports from `game.core.math`
4. **Rate**: CONFIRMED (truly untested) / DISPUTED (found tests) / INCONCLUSIVE

### For MAJOR/MINOR claims (untested branches/paths/corners):
1. **Read the production code** at the cited line range. Read at least
   10 lines above and below for context.
2. **Read the cited test file(s)**. Read the specific test functions that
   supposedly exercise the production code.
3. **Trace the code path**: Does the test ACTUALLY exercise the claimed
   code path? Or did the discovery agent misinterpret the code?
4. **Check for indirect coverage**: Is the untested path actually exercised
   through a higher-level test that calls a wrapper function?
5. **Rate**: CONFIRMED (gap is real) / DISPUTED (gap doesn't exist or is
   already covered) / INCONCLUSIVE

### For ADVISORY claims (UI code):
1. Verify the code is genuinely UI rendering/event code
2. Check if the file also contains business logic that the discovery agent
   may have under-severity flagged
3. **Rate**: CONFIRMED / DISPUTED / INCONCLUSIVE
4. You may UPGRADE an ADVISORY to MAJOR if the code contains testable
   business logic with no coverage

### Severity Adjustments
- You may **DOWNGRADE** severity (CRITICAL→MAJOR, MAJOR→MINOR, etc.)
- You may **UPGRADE ADVISORY→MAJOR** for UI business logic gaps
- You may NOT upgrade CRITICAL or MAJOR — only the discovery agent sets
  the upper bound

## What NOT to Do
- Do NOT create new claims — only verify or dispute existing claims
- Do NOT re-read every file from scratch (use cited line ranges)
- Do NOT skip claims because they seem "obvious" — read the code
- Do NOT default to CONFIRMED when uncertain — use INCONCLUSIVE

## Output — Save to: {REVIEW_DIR}/findings/VERIFIED_SHARD_{SHARD_ID}.md

You MUST use the Write tool to save your report.

Use EXACTLY this structure:

```
# Shard {SHARD_ID} — Verified Coverage Findings

## Summary
- Shard: {SHARD_ID}
- Claims reviewed: [N]
- CONFIRMED: [N] | DISPUTED: [N] | INCONCLUSIVE: [N]
- Severity downgrades: [N]
- Severity upgrades (ADVISORY→MAJOR): [N]

## CONFIRMED Gaps

### game/path/to/file.py

#### [CRITICAL] Zero unit test coverage
- **Location**: file.py (entire file, N LOC)
- **Layer**: [layer]
- **Issue**: [verified — no unit tests anywhere import this module]
- **Key symbols untested**: [list]
- **Suggested tests**:
  1. test_<name> — [specific description]
- **Verified**: CONFIRMED (severity kept / downgraded from X — reason)

#### [MAJOR] `function_name` — Missing error-path test
- **Location**: file.py:line_range
- **Untested path**: [verified description of the specific untested path]
- **Suggested test**: [specific description]
- **Verified**: CONFIRMED (severity kept / downgraded from X — reason)

#### [ADVISORY] `render_method` — UI rendering code
- **Location**: file.py:line_range
- **Verified**: CONFIRMED — genuine pygame rendering code
- **Note**: [any testable business logic nearby?]

(Repeat for ALL CONFIRMED claims)

## Disputed & Inconclusive Claims

| Original Finding | File | Severity | Verdict | Reason |
|-----------------|------|----------|---------|--------|
| `function_name` missing error test | path/file.py:50 | MAJOR | DISPUTED | `test_error_path` in test_file.py:120 already tests ValueError path |
| ... | | | INCONCLUSIVE | Cannot determine without reading additional dependency files |

## Discovery Agent Errors
[List any systematic errors the discovery agent made:
- False positives (claimed untested but tests exist)
- Missed actual gaps (tests exist but are trivial)
- Incorrect severity assignments (overstated or understated)]
```

## Rules
1. Be skeptical — it's better to DISPUTE a borderline claim than confirm a false one
2. Always cite specific code and test evidence to justify DISPUTED claims
3. A claim stays INCONCLUSIVE if you need more context than reasonably readable
4. Only CONFIRMED claims appear in the final summary — your report is authoritative
5. Verify 100% of CRITICAL and MAJOR claims (these drive implementation work). Sample
   MINOR and ADVISORY claims at your discretion — the final report must label sampled
   severities as "sampled (X% verified)" and unverified sampled-out claims are
   excluded from "verified confirmed" counts.
```

### Step 6: Verify Phase 3 Completion

After all batches complete, check that all verified shard report files exist and are non-empty:

- `REVIEW_DIR/findings/VERIFIED_SHARD_01.md` through `REVIEW_DIR/findings/VERIFIED_SHARD_{SHARD_COUNT:02d}.md`

### Step 7: Compile Final Report (Phase 4)

Read all {SHARD_COUNT} VERIFIED shard reports. Extract ONLY CONFIRMED claims. Do NOT include DISPUTED or INCONCLUSIVE claims.

Write `REVIEW_DIR/SUMMARY.md` and `REVIEW_DIR/SUMMARY.json`.

**SUMMARY.json** with structured data — all run_info values populated from raw JSON (`manifest.json`, `layer_summary.json`, `file_inventory.json`):

```json
{
  "run_info": {
    "date": "<populated from REVIEW_DIR timestamp>",
    "seed": "<populated from manifest.json.seed>",
    "shard_count": <populated from manifest.json.shard_count>,
    "total_prod_files": <populated from file_inventory.json.total_files>,
    "total_prod_loc": <populated from manifest.json.total_loc_estimate>,
    "total_symbols": <populated from layer_summary.json.totals.total_symbols>
  },
  "phase1_coverage": {
    "overall_pct": <populated from layer_summary.json.totals.overall_coverage_pct>,
    "by_layer": <populated from layer_summary.json.layers — per-layer coverage_pct>
  },
  "phase2_claims": <total claims from all SHARD_*.md>,
  "verified_confirmed": <total CONFIRMED from all VERIFIED_SHARD_*.md>,
  "disputed": <total DISPUTED from all VERIFIED_SHARD_*.md>,
  "inconclusive": <total INCONCLUSIVE from all VERIFIED_SHARD_*.md>,
  "findings": [ ... ]
}
```

**SUMMARY.md** structure:

```markdown
# Test Coverage Audit — Final Summary (Verified Claims Only)

## Run Info
- Date: <populated from REVIEW_DIR>
- Seed: <populated from manifest.json.seed>
- Shards: <populated from manifest.json.shard_count>
- Total production files: <populated from file_inventory.json.total_files> (~<loc>K LOC)
- Total symbols (functions/methods/classes): <populated from layer_summary.json.totals.total_symbols>
- Phase 1 estimated coverage: <overall_coverage_pct>% (heuristic name-grep — NOT authoritative)
- Phase 2 claims: N → Verified: N | Disputed: N | Inconclusive: N

## Coverage Scorecard (Phase 1 heuristic baseline — NOT authoritative)

Populate from `layer_summary.json`:

| Layer | Files | Symbols | Tested | Coverage % | Tier 0 | Tier 1 | Tier 2 | Tier 3 |
|-------|-------|---------|--------|------------|--------|--------|--------|--------|
| <for each layer in layer_summary.json.layers> |
| **Totals** | <from layer_summary.json.totals> |

The Phase 1 scorecard is a heuristic starting point. All numbers are derived
from import-based candidate matching and name-grep — they are NOT proof of
coverage. The verified findings below are the authoritative output.

## Verified Gap Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | N | Zero unit tests for non-UI module |
| MAJOR | N | Significant untested code paths, error handling, or functions |
| MINOR | N | Missing corner cases, boundary tests, minor branches |
| ADVISORY | N | UI rendering/event code — conventionally tested via integration |

## P0 — Critical Gaps (Immediate Attention)

Files/modules with ZERO unit test coverage in any non-UI layer
(Core, Engine, Simulation, Strategy, AI, Research, Services, Assets, Game Root).

[Per-file listing with suggested tests]

## P1 — Major Gaps (Address Before Next Feature)

Functions with untested error paths, missing boundary conditions, or
completely untested functions within partially tested modules.

[Per-function listing with suggested tests]

## P2 — Minor Gaps (Improve Opportunistically)

Corner cases and minor branches not covered.

[Per-function listing with suggested tests]

## UI Advisory Gaps

[Per-file listing, lower detail]

## Shard Verification Summary

| Shard | Phase 2 Claims | Verified | Disputed | Inconclusive |
|-------|---------------|----------|----------|--------------|
| 01 | N | N | N | N |
| ... | | | | |

## Priority Action Plan

Ordered by: (severity × LOC affected × layer importance)
Top 20 items.

## Estimated Test Effort

- CRITICAL gaps: ~N new test functions needed
- MAJOR gaps: ~N new test functions needed
- MINOR gaps: ~N new test functions needed
- ADVISORY: N items — no unit test action required

## Full Report Paths
- Phase 1 raw data: `{REVIEW_DIR}/raw/`
- Phase 2 shard reports: `{REVIEW_DIR}/findings/SHARD_*.md`
- Phase 3 verified reports: `{REVIEW_DIR}/findings/VERIFIED_SHARD_*.md`
- Final summary: `{REVIEW_DIR}/SUMMARY.md`
- Structured data: `{REVIEW_DIR}/SUMMARY.json`
```

### Step 8: Present to User

Show the user:
1. Run info: date, shards, files reviewed
2. Phase 1 heuristic coverage by layer
3. Verified gaps: CRITICAL / MAJOR / MINOR / ADVISORY counts
4. Layer with worst coverage (verified)
5. Top 5 highest-impact confirmed gaps
6. P0/P1/P2 counts (verified only)
7. Path to final summary: `{REVIEW_DIR}/SUMMARY.md`

Do NOT start making code changes. This is a read-only audit. All findings in the summary are verified — they can be acted upon.
