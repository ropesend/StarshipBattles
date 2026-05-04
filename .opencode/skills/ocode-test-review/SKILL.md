---
name: ocode-test-review
description: Exhaustive test suite audit across 12 quality categories. Seeded file-shuffle sharding for cross-run randomization. Includes skeptical verification stage — only verified claims appear in final report. Read-only — produces findings documents, no code changes.
argument-hint: "[--seed STR] [--shards N] [--max-loc-per-shard N] [--skip-generate to reuse existing SHARD_CONFIG.json]"
---

# Test Suite Audit

Run an exhaustive review of the test suite (`tests/`) for 12 categories of quality issues. Uses randomized seeded sharding so each run reviews tests in different groupings, increasing the chance of detecting cross-file duplicates.

**Four-phase workflow**: Phase 1 (shard reviewers) → Phase 2 (cross-shard dedup) → Phase 3 (skeptical verification) → Phase 4 (final summary, verified claims only).

Does NOT change any code. Produces per-shard findings reports, verification reports, and a unified summary.
Excludes: `tests/unit/combat_lab/`, `__init__.py`, `__pycache__/`, `tests/infrastructure/`.
All other test directories are in scope. `conftest.py` files are NOT excluded — they must be read by shard reviewers because CAT-5 fixture bloat and test isolation issues often originate there.
Regression/snapshot tests in `tests/regression/` are in scope but CAT-11 does not apply to them (snapshot assertions are intentional).

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

Verify the shard generator exists:

```bash
python -c "import os; assert os.path.exists('Tools/test_review/generate_shards.py'), 'generate_shards.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Generate Shards

Run the shard generator. Use `--seed` if the user provided one, otherwise let it default (current date). Prefer `--max-loc-per-shard N` (recommended starting value: 25k) to auto-adjust shard count as the test suite grows; fall back to `--shards 12` only when you need a fixed shard count.

```bash
python Tools/test_review/generate_shards.py --seed {seed} --max-loc-per-shard {max_loc_per_shard}
```

If the user passed `--skip-generate`, find the most recent existing `SHARD_CONFIG.json` instead:
- Glob: `Reviews/results/*_test-review/SHARD_CONFIG.json`
- Sort by directory name (timestamped prefix), take the newest
- Read it and use its `REVIEW_DIR`

Capture the output directory path from the script's stdout:
```
Output directory: Reviews/results/2026-05-02_143021_test-review
```

Store this as `REVIEW_DIR`. Also store values for `{SEED}` and `{SHARD_COUNT}`.

Read the generated config:

```
Read REVIEW_DIR/SHARD_CONFIG.json
```

Extract from it:
- `{SEED}` — the seed used
- `{SHARD_COUNT}` — number of shards (may be higher than requested if `--max-loc-per-shard` triggered)
- For each shard `"01"` through `"{SHARD_COUNT}"`: its `"files"` list and `"loc_estimate"`
- `{TOTAL_FILES}` and `{TOTAL_LOC}` from top-level keys

> **Tuning for growth**: As the test suite grows, use `--max-loc-per-shard N` instead of manually bumping `--shards`. Example: `--max-loc-per-shard 25000` auto-calculates the minimum shard count needed. The coordinator always launches one agent per shard.

### Step 2: Launch Phase 1 — Shard Reviewers ({SHARD_COUNT} agents in parallel)

Launch **one agent per shard** in parallel using the Task tool with `subagent_type: general`.

**Replace these placeholders** in the template below for each agent:
- `{SHARD_ID}` → `"01"`, `"02"`, ... `"{SHARD_COUNT}"`
- `{FILE_COUNT}` → from `SHARD_CONFIG.json`
- `{LOC_ESTIMATE}` → from `SHARD_CONFIG.json`
- `{FILE_LIST}` → the `files` array for the shard, formatted as a markdown bullet list: `- tests/path/to/file.py (~N LOC)`
- `{REVIEW_DIR}` → the actual review directory path

```
# Test Suite Audit — Shard {SHARD_ID} Reviewer

You are reviewing ONE shard of the test suite for 12 categories of quality issues.
You MUST read every assigned test file thoroughly. You may read any production
code under game/ that those tests exercise, plus conftest files and test fixtures
they depend on.

If context becomes constrained, prioritize reading tests that import from
game.* (real production tests) over utility/scaffold files. Note any
partially-read files in the coverage verification table.

## Your File List ({FILE_COUNT} files, ~{LOC_ESTIMATE} LOC)

Read EVERY file below. Do not skip any.

{FILE_LIST}

## The 12-Category Rubric

For EVERY test function in EVERY file, evaluate against these categories.
Report only tests that HAVE an issue — do not report tests that are fine.
One test can have multiple findings in different categories.

Agents may DOWNGRADE severity when blast radius is small. A CAT-2 finding
in an unused helper file under tests/fixtures/ is MAJOR, not CRITICAL.
If downgrading, note the reason in the Issue field.

### CRITICAL severity categories

**CAT-1 — Trivial Pass**: Test that cannot fail if the module imports succeed.
Signals: `assert len(X) > 0`, `assert True`, no assertions after setup, `assert X is not None` where X is always not-None. Does NOT include: constants validation (e.g., checking all RGB values are in [0,255]), or registry hydration sanity checks that verify data loaded correctly.

**CAT-2 — Tests Nothing Real**: Exercises only mocked constructs or local reimplementations, never touches production code paths. Zero regression protection.
Signals: No imports from `game.*`; reimplements game functions locally with copied logic; every dependency including the SUT is MagicMock; `inspect.getsource()` assertions that check source text rather than behavior; tests a local copy of production code. A test that mocks SOME dependencies (like file I/O or pygame display) but exercises the REAL SUT is NOT CAT-2.

**CAT-3 — Dead Test Code**: Test for removed functionality, unused test helpers, or tests targeting deleted modules/classes.
Signals: `pytest.raises(ImportError)` for classes that were removed; test helper functions defined in the file but never called by any test; test files containing only imports/constants with no `def test_` functions; tests that import from modules that no longer exist. Standalone repro scripts that are covered by proper tests elsewhere are CAT-3.

### MAJOR severity categories

**CAT-4 — Duplicate Testing**: Two or more tests verify the exact same production code path with the same or near-identical assertions.
Signals: Copy-pasted test body with only the function name changed; same SUT method called with identical or trivially-different inputs; identical assertion patterns across different test files within your shard. Does NOT include: same SUT method tested with legitimately different edge cases or boundary values.

**CAT-5 — Fixture Bloat**: `function`-scoped fixtures that rebuild expensive state when `class` or `session` scope would work.
Signals: Fixture involving file I/O, registry hydration, or pygame.font.init(), scoped `function` (or default scope), and used by 10+ tests in the same class. `function` scope on cheap fixtures (dict construction, simple object creation) is fine. Unnecessarily re-computing identical values across parameterized tests is also CAT-5.

**CAT-6 — Mocking Brittleness**: Mocks internal implementation details rather than behavioral contract. Test passes when code is broken, fails when code is refactored but still works ("change-detector" anti-pattern).
Signals: `patch.object(target, '_private_method')`; asserts on `mock.call_args_list` exact order; mocks `__init__` of a dependency; mock setup that encodes the internal call chain. Does NOT include: mocking external I/O boundaries (file system, network, pygame display, image loading) which is appropriate.

**CAT-7 — Sleep / Latency**: Arbitrary blocking delays that make tests slow and flaky.
Signals: `time.sleep(N)`, `pygame.time.delay(N)`, `pygame.time.wait(N)`, arbitrary timeout values in polling/wait loops. Does NOT include: `pygame.time.get_ticks()` used for elapsed-time measurement (non-blocking), or `clock.tick()` for frame-rate limiting in integration tests.

### MINOR severity categories

**CAT-8 — Needless Complexity**: Setup exceeds what is being tested; deeply nested patching.
Signals: 5+ nested `with patch()` blocks in a single test; 10+ MagicMock fixtures each with attribute chains for a single assertion; setup code exceeding 50% of the total test function body when only a simple assertion follows.

**CAT-9 — Simplification Opportunity**: Fewer lines without losing coverage.
Signals: Repeated `from module import X` inside every test method instead of once at module level; common setup repeated across tests that could be a shared fixture or helper; 5 identical mock constructions that could be replaced with a single helper function.

**CAT-10 — Parameterize Opportunity**: Cluster of tests with identical logic, different data. Should be `@pytest.mark.parametrize`.
Signals: 3+ test methods with identical body, differing only in input values or expected output constants. Flag the entire cluster as one finding, listing all test names. The parametrized version would be one test function with a decorator.

**CAT-11 — Fragile Assertion**: Over-assertion that makes tests fail for irrelevant reasons.
Signals: Exact dict/JSON match when only 1-2 keys matter; asserts on unordered collection ordering; snapshot comparison of unstable string output; checking internal implementation state that isn't part of the public API contract. Does NOT include: snapshot tests in `tests/regression/` which intentionally validate exact outputs.

**CAT-12 — Logic-Heavy Test**: Test itself contains branching or complex computation.
Signals: `if`/`else` in the test body; `for` loops with nested assertions inside; arithmetic or computation before the expected-value comparison. The expected value should be pre-computed or hardcoded — the test should not need its own tests.

## What NOT to Report
- Tests that are working fine with no quality issues
- Test naming or style preferences (underscore count, docstring format)
- "This test should also test X" — adding new tests is out of scope
- General code review of production code under game/ — only evaluate the test code itself
- Import ordering or PEP8 formatting

## Output — Save to: {REVIEW_DIR}/SHARD_{SHARD_ID}.md

You MUST use the Write tool to save your report.

Use EXACTLY this structure:

```
# Shard {SHARD_ID} — Test Audit Report

## Summary
- Shard: {SHARD_ID}
- Files assigned: {FILE_COUNT}
- Files actually read: [COUNT — MUST equal assigned]
- Total findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Findings

### tests/path/to/test_file.py (~N LOC)

#### CAT-N: test_function_name  [CRITICAL]
- **Location**: test_file.py:line_range
- **Issue**: [1-2 sentence description]
- **Suggestion**: [concrete action: remove / parametrize / refactor / rescope / merge]
- **LOC affected**: N

#### CAT-N: test_another_function  [MAJOR]
- **Location**: test_file.py:line_range
- **Issue**: [description]
- **Suggestion**: [concrete action]
- **LOC affected**: N

### tests/path/to/another_test_file.py (~N LOC)
...

## File Coverage Verification
| File | Status | Findings |
|------|--------|----------|
| tests/path/to/file.py | Read ✓ | N |
| [every assigned file with Read ✓ and finding count] |

## Context Usage Estimate
- Total LOC read (test files + production code): [approximate estimate]
- Approximate headroom: High (>500K remaining) | Medium (200-500K) | Low (<200K)
```

## Rules
1. Read EVERY file in your list — no exceptions
2. If a file has zero findings, still list it in File Coverage Verification with findings=0
3. If a test matches multiple categories, report all of them
4. Be specific with line ranges — cite actual line numbers from the files you read
5. Do NOT skip files because they "look similar to another file" — duplicate detection across shards happens in Phase 2
6. Downgrade severity when blast radius is small — note the reason in the Issue field
```

### Step 3: Verify Phase 1 Completion

After all agents complete, check that all shard report files exist and are non-empty (one per shard: `SHARD_01.md` through `SHARD_{SHARD_COUNT}.md`).

Use Read with limit=1 to verify each file exists and has content. If any agent failed, note which shard and proceed with available data.

### Step 4: Launch Phase 2 — Cross-Shard Dedup (1 agent)

```
# Cross-Shard Duplicate Detection

Read ALL shard reports from {REVIEW_DIR}/ (one per shard: SHARD_01.md through
SHARD_{SHARD_COUNT}.md).

Your task: find CAT-4 (Duplicate Testing) that SPANS shards — tests in different
shards that verify the same production code path with the same assertions.

## Methodology

1. Extract all CAT-4 findings from each shard report.
2. For each SUT (system under test) named in those findings, search across
   ALL shard reports for tests targeting the same SUT method or class.
3. Read the actual test files from both shards to verify the duplication.
4. Report only confirmed cross-shard duplicates — do not re-report duplicates
   already noted within a single shard (Phase 1 agents handled those).

Also scan for:
- Identical test helper functions defined in different test directories
  (e.g., `make_mock_ship()` in `tests/unit/entities/conftest.py` and
  `tests/unit/simulation/entities/conftest.py`)
- Same assertion pattern appearing in tests for different modules that
  actually exercise the same underlying code

## Output — Save to: {REVIEW_DIR}/CROSS_SHARD.md

You MUST use the Write tool to save your report.

```
# Cross-Shard Duplicate Report

## Summary
- Shard reports analyzed: {SHARD_COUNT}
- Cross-shard duplicates found: [N]
- Helper duplications found: [N]

## Cross-Shard Duplicates

### DUP-001: [Brief description]
- **SUT**: game.module.ClassName.method_name
- **Shard {X}**: tests/path/file1.py::test_name1 (line N)
- **Shard {Y}**: tests/path/file2.py::test_name2 (line N)
- **Similarity**: [identical assertions / near-identical / same helper called]
- **Recommendation**: [keep test_name1, remove test_name2, or merge into parametrized]
- **Estimated LOC savings**: N

### DUP-002: ...
...

## Cross-Shard Helper Duplication

### HLP-001: helper_function_name
- **Defined in**:
  - tests/path/dir1/conftest.py:line
  - tests/path/dir2/conftest.py:line
- **Recommendation**: [move to shared location / keep separate if domain-different]
```
```

### Step 5: Verify Phase 2 Completion

Check that `CROSS_SHARD.md` exists and is non-empty.

### Step 6: Launch Phase 3 — Skeptical Verification ({SHARD_COUNT} agents in parallel)

Launch **one verification agent per shard** in parallel using the Task tool with `subagent_type: general`.

Each verifier receives:
1. Its shard's Phase 1 report (`SHARD_{SHARD_ID}.md`) — ALL claims from that shard
2. The cross-shard report (`CROSS_SHARD.md`) — cross-shard duplicate claims involving this shard's files
3. Instructions to independently read cited line ranges and verify each claim

**Replace these placeholders** in the template below for each agent:
- `{SHARD_ID}` → `"01"`, `"02"`, ... `"{SHARD_COUNT}"`
- `{REVIEW_DIR}` → the actual review directory path

```
# Test Suite Audit — Shard {SHARD_ID} Verifier

You are the SKEPTICAL VERIFIER for Shard {SHARD_ID}. Your job is to independently
verify every claim made by the Phase 1 shard reviewer and any cross-shard claims
involving your shard's files.

You are skeptical. You must read the cited code before confirming. If a claim is
overstated, false, or unverifiable, DISPUTE it with a specific reason drawn from
the source code.

## Inputs You Must Read

1. **Phase 1 report**: {REVIEW_DIR}/SHARD_{SHARD_ID}.md — every claim for this shard
2. **Cross-shard report**: {REVIEW_DIR}/CROSS_SHARD.md — claims involving this shard's files
3. **The actual test files** cited in each claim — read the cited line ranges PLUS
   at least 10 lines of surrounding context above and below. If after reading the
   cited sections you still have reason to be suspicious, read more of the file.

## Verification Methodology

For each claim in the Phase 1 shard report:

1. **Read the cited code**: Open the test file at the cited line range. Read at
   least 10 lines above and below for context.
2. **Validate the category**: Does the code actually match the category signals?
   (e.g., for CAT-1: does the test genuinely have no meaningful assertion? For CAT-6:
   is this truly mocking internals or is it mocking an I/O boundary?)
3. **Check severity**: Is the severity appropriate? You may DOWNGRADE (e.g., CRITICAL
   → MAJOR, MAJOR → MINOR) if the blast radius is small or the original was overstated.
   You may NOT upgrade severity — only the Phase 1 agent has that authority.
4. **Rate confidence**:
   - **CONFIRMED** — The claim is accurate. The code has the issue described, at
     the stated (or downgraded) severity.
   - **DISPUTED** — The claim is false or overstated. Provide a specific falsification
     reason citing the actual code you read. (e.g., "The test asserts `result == 42`,
     not `assert True`; it exercises a real code path.")
   - **INCONCLUSIVE** — You cannot determine with confidence after reading the cited
     code. Do not default to CONFIRMED or DISPUTED.

For cross-shard duplicate claims involving your files:
1. Read both files at the cited lines.
2. Verify the duplication is genuinely the same code path with same assertions.
3. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE.

## What NOT to Do
- Do NOT create new claims — only verify or dispute existing claims
- Do NOT re-read every file from scratch (use cited line ranges as starting points)
- Do NOT invent additional findings
- Do NOT skip claims because they seem "obvious" — read the code

## Output — Save to: {REVIEW_DIR}/VERIFIED_SHARD_{SHARD_ID}.md

You MUST use the Write tool to save your report.

Use EXACTLY this structure:

```
# Shard {SHARD_ID} — Verified Findings

## Summary
- Shard: {SHARD_ID}
- Claims reviewed: [N] (Phase 1: N, Cross-shard: N)
- CONFIRMED: [N] | DISPUTED: [N] | INCONCLUSIVE: [N]
- Severity downgrades: [N]

## Verified Findings (CONFIRMED only)

### tests/path/to/test_file.py

#### CAT-N: test_function_name  [CRITICAL]
- **Location**: test_file.py:line_range
- **Issue**: [verified description]
- **Suggestion**: [action]
- **LOC affected**: N
- **Verified**: CONFIRMED (severity kept / downgraded from MAJOR — reason)

#### CAT-N: test_another_function  [MAJOR]
- **Location**: test_file.py:line_range
- **Issue**: [verified description]
- **Suggestion**: [action]
- **LOC affected**: N
- **Verified**: CONFIRMED

(Repeat for all CONFIRMED claims, including cross-shard duplications involving this shard)

## Disputed & Inconclusive Claims (for transparency)

| Original ID | File | CAT | Original Severity | Verdict | Reason |
|-------------|------|-----|-------------------|---------|--------|
| test_xyz | path/file.py:50 | CAT-1 | CRITICAL | DISPUTED | Test asserts result == 42, not a trivial pass |
| ... | | | | INCONCLUSIVE | ... |
```

## Rules
1. Be skeptical — it's better to DISPUTE a borderline claim than confirm a false one
2. Always cite specific code to justify DISPUTED claims
3. A claim stays INCONCLUSIVE if you need more context than you can reasonably read
4. Cross-shard claims involving this shard's files appear inline in the verified findings
5. Only CONFIRMED claims appear in the final summary — your report is the authoritative source
```

### Step 7: Verify Phase 3 Completion

Check that all verified shard report files exist and are non-empty (one per shard: `VERIFIED_SHARD_01.md` through `VERIFIED_SHARD_{SHARD_COUNT}.md`).

### Step 8: Compile Phase 4 — Final Summary (verified claims only)

Read all VERIFIED shard reports (CONFIRMED claims only) plus the cross-shard report. Produce `SUMMARY.md` and a `SUMMARY.json` sidecar.

Only include CONFIRMED claims from `VERIFIED_SHARD_*.md`. Do NOT include DISPUTED or INCONCLUSIVE claims.

Write `SUMMARY.json` with a structured findings array so downstream consumers do not need to parse loose prose:

```json
{
  "run_info": { "date": "...", "seed": "...", "shard_count": 0, "total_files": 0, "total_loc": 0 },
  "phase1_claims": 0, "verified": 0, "disputed": 0, "inconclusive": 0,
  "findings": [
    {
      "id": "...", "category": "CAT-1",
      "severity": "CRITICAL", "file": "tests/path/test.py",
      "line": 42, "title": "test_name",
      "suggestion": "concrete action",
      "loc_affected": 5
    }
  ]
}
```

**SUMMARY.md structure:**

```markdown
# Test Suite Audit — Summary (Verified)

## Run Info
- Date: {timestamp}
- Seed: {seed}
- Shards: {shard_count}
- Total test files reviewed: {total_files}
- Total LOC reviewed (est): {total_loc}
- Phase 1 claims: {N} → Verified: {N} | Disputed: {N} | Inconclusive: {N}

## Verified Findings by Category
| Category | Critical | Major | Minor | Total |
|----------|----------|-------|-------|-------|
| CAT-1 Trivial Pass | | - | - | |
| CAT-2 Tests Nothing Real | | - | - | |
| CAT-3 Dead Test Code | | - | - | |
| CAT-4 Duplicate Testing | - | | - | |
| CAT-5 Fixture Bloat | - | | - | |
| CAT-6 Mocking Brittleness | - | | - | |
| CAT-7 Sleep/Latency | - | | - | |
| CAT-8 Needless Complexity | - | - | | |
| CAT-9 Simplification | - | - | | |
| CAT-10 Parameterize | - | - | | |
| CAT-11 Fragile Assertion | - | - | | |
| CAT-12 Logic-Heavy | - | - | | |
| **Totals** | | | | |

## Top 20 Highest-Impact Verified Findings
Ordered by estimated LOC affected × severity weight (CRITICAL=10, MAJOR=5, MINOR=1).
List: finding ID, file, category, severity, LOC affected, brief description.

## Shard Verification Summary
| Shard | Phase 1 Claims | Verified | Disputed | Inconclusive |
|-------|---------------|----------|----------|--------------|
| 01 | N | N | N | N |
| ... | | | | |

## Cross-Shard Duplicates
Summary from CROSS_SHARD.md — N cross-shard duplicates found, N confirmed by verifiers.

## Priority Action Plan

### P0 — Immediate Attention (CAT-1, CAT-2, CAT-3)
Verified findings where tests provide zero or negative value.

### P1 — Address Before Next Major Feature (CAT-4, CAT-5, CAT-6, CAT-7)
Verified quality and performance debt that slows development velocity.

### P2 — Improve Opportunistically (CAT-8, CAT-9, CAT-10, CAT-11, CAT-12)
Verified nice-to-have improvements.

## Estimated Impact (Verified Only)
- Tests removable with zero coverage loss: [N]
- Tests mergeable via parametrize: [N clusters → N resulting tests]
- Fixture rescoping candidates: [N]
- Estimated total LOC reduction: [N]

## Full Report Paths
- Phase 1 shard reports: {REVIEW_DIR}/SHARD_*.md
- Phase 2 cross-shard: {REVIEW_DIR}/CROSS_SHARD.md
- Phase 3 verified reports: {REVIEW_DIR}/VERIFIED_SHARD_*.md
- SHARD_CONFIG.json: {REVIEW_DIR}/SHARD_CONFIG.json
- Final summary: {REVIEW_DIR}/SUMMARY.md
```

### Step 9: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-test-review
```

### Step 10: Present to User

Show the user:
1. Run info: date, seed, shards, files reviewed
2. Phase 1 claims → Verified/Disputed/Inconclusive counts
3. Verified findings by category table (summary totals)
4. Top 5 highest-impact verified findings
5. P0/P1/P2 counts (verified only)
6. Path to final summary: `{REVIEW_DIR}/SUMMARY.md`
7. Paths to per-shard detail: `{REVIEW_DIR}/SHARD_*.md` and `{REVIEW_DIR}/VERIFIED_SHARD_*.md`

Do NOT start making code changes. This is a read-only audit. All findings in the summary are verified — they can be acted upon.
