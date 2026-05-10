---
name: ocode-error-audit
description: Error handling & robustness audit. Scans all production code for exception hygiene — broad except without Intentional comment, bare except, JSON bypass of json_utils, generic raise Exception, print-debug leakage, resource cleanup, and LLM context security. Produces a prioritized error hygiene scorecard with remediation plan. Production code only.
argument-hint: "[--skip-phase1 to reuse existing raw results]"
---

## Invocation

- **Slash command (interactive):** `/ocode-error-audit`
- **CLI (non-interactive):** `opencode run "Load the ocode-error-audit skill and execute it. Args: [optional --skip-phase1]"`

The skill is identical in both modes. CLI mode skips any user-prompt confirmations.

# Error Handling & Robustness Audit

Run a comprehensive audit of error handling quality across the production codebase. Scans for exception hygiene issues, JSON I/O bypass, resource leaks, and debug-print leakage. Produces a prioritized error hygiene scorecard with remediation estimates.

Does NOT change any code. Targets `game/` only (not tests).

## Pre-Flight Safeguards

Before starting any work:
1. **Run from repo root.** All paths are relative to the repository root.
2. **Check `git status --short`** and do NOT revert unrelated changes.
3. **Never read `docs/_ignore/`.** It is not documentation.
4. **Write only under `Reviews/results/`** and explicitly named `AgentCoordination/` paths.
5. **This is a read-only audit.** Do not edit source code, test code, or docs.

## Scope Exclusions (Pre-Filtered by Phase 1)

The deterministic scanner skips these by design — agents should not see them and should not flag them:

- **In-memory `json.loads(string_arg)` / `json.dumps(obj)` calls** — `json_utils` does not offer in-memory equivalents, so routing through it is impossible. Only file I/O paths are in scope.
- **`except Exception` with a recognized `# Intentional broad catch:` comment on the same line or the line immediately above** — these are explicitly compliant per `docs/05_ERROR_HANDLING.md`.
- **Top-level CLI scripts under `Tools/`** — broader exception types are tolerated at script level.

If you see findings agents have flagged in these categories, treat them as audit defects (file an entry in the report's "Refinement Notes" section) rather than acting on them.

## Execution

This skill is a single-command workflow. The user loads it and you handle everything.

### Step 0: Pre-Flight Checks

Ensure the error audit scanner exists:

```bash
python -c "import os; assert os.path.exists('Tools/error_audit/error_audit.py'), 'error_audit.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/error_audit/error_audit.py
```

Capture the last few lines of stdout. Look for the line that prints the output directory path:
```
Output directory: Reviews/results/2026-05-03_120000_error-audit
```

Store this as `REVIEW_DIR`.

If the user passed `--skip-phase1`, find the most recent review directory:
- Glob: `Reviews/results/*_error-audit/`
- Sort by directory name, take the newest
- Use that as `REVIEW_DIR`

The script creates `REVIEW_DIR/raw/` with these outputs against `game/`:

1. `broad_except_sites.json` — every `except Exception` without `# Intentional` comment
2. `bare_except_sites.json` — bare `except:` clauses (expected zero, guard against regressions)
3. `json_bypass_sites.json` — `json.load`/`json.dump` not routed through `json_utils`
4. `raise_generic_sites.json` — `raise Exception(...)` instead of domain-specific
5. `print_debug_sites.json` — `traceback.print_exc()` or `print()` diagnostic usage
6. `file_inventory.json` — full file inventory
7. `manifest.json` — 4-shard file assignments for agent distribution

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory for use in agent prompts:

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists
2. Read `REVIEW_DIR/raw/broad_except_sites.json` — get the full content
3. Read `REVIEW_DIR/raw/bare_except_sites.json`
4. Read `REVIEW_DIR/raw/json_bypass_sites.json`
5. Read `REVIEW_DIR/raw/raise_generic_sites.json`
6. Read `REVIEW_DIR/raw/print_debug_sites.json`
7. Read `docs/05_ERROR_HANDLING.md`, `docs/03_CONVENTIONS.md`

### Step 3: Launch 6 Agents in Parallel

Create the findings directory:

```bash
mkdir -p REVIEW_DIR/findings
```

Launch **6 agents** in parallel using OpenCode subagents in parallel:
- **4 in-shard deep review agents** (one per shard: 01, 02, 03, 04)
- **1 cross-layer error propagation validator**
- **1 LLM context security validator**

**Replace these placeholders in each template before sending:**
- `{REVIEW_DIR}` → the actual review directory
- `{shard_id}` → `"01"`, `"02"`, `"03"`, `"04"`
- `{shard_label}` → from manifest.json `shards.{shard_id}.label`
- `{shard_files}` → the files list from manifest.json `shards.{shard_id}.files`, formatted as markdown list
- `{broad_excepts}` → the full content of broad_except_sites.json
- `{json_bypasses}` → the full content of json_bypass_sites.json

#### Agents 1a-1d: In-Shard Error Handling Reviewers

Launch **4 agents** using the template below — one for each shard.

```
# Error Handling Audit — Shard {shard_id} Reviewer

You are assigned ONE shard: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/05_ERROR_HANDLING.md and docs/03_CONVENTIONS.md.

## Scope
All files listed below MUST be read. If you skip any file, the coverage
guarantee is broken.

Shard file list:
{shard_files}

## Deterministic Scan Results (filtered for your shard)
Broad except without comment:
{broad_excepts}

JSON bypass sites:
{json_bypasses}

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Validate deterministic findings:**
   - For each broad-except site: read the surrounding 5 lines. Is the catch
     genuinely broad? Could it be narrowed to specific exception types?
   - For each JSON bypass: check if `json_utils` is available and why it
     wasn't used.
3. **Check for additional error handling issues:**
   - Exception swallowing: `except: pass` or bare except with no action
   - Error information loss: catching one exception but raising a new one
     without chaining (`raise NewError from e` or explicit `from None`)
   - **Lost exception chaining:** `raise NewError(...)` inside `except` without
     `from e` (swallows original traceback) or without `from None` rationale
     (must document why the original is intentionally suppressed)
   - Generic exception types where project-specific exceptions exist:
     `raise RuntimeError(...)` or `raise ValueError(...)` where
     `ValidationException` or `EnginePhaseError` would be more specific
   - Inconsistent logging: some errors logged at error level, others at debug
   - Missing error boundaries: TurnEngine callbacks without catch-all wrapper
   - Duplicate error handling code across files in the shard
4. **Check resource cleanup:**
   - File handles opened without `with` context
   - pygame resources without matching cleanup
   - Subprocess launches without wait/timeout
   - Temporary files not removed in finalizers

## What NOT to Report
- Unit tests
- `except Exception` WITH `# Intentional` comment (these are compliant)
- Pygame boilerplate patterns that are idiomatic
- Library-level exception patterns outside your control

## Severity Guide
- CRITICAL: Bare except that swallows all errors silently; resource leak
  that could exhaust file handles or memory
- MAJOR: Broad except without comment where specific types would work;
  JSON bypass where json_utils is clearly available; lost exception chaining
  in production runtime code
- MINOR: Missing error chaining; inconsistent log levels; duplicate
  error-handling patterns across files; generic raise in CLI/tool scripts
  (top-level scripts tolerate broader exception types than runtime code)

## JSON Bypass Exemptions
Production code under `game/` must route JSON I/O through `game.core.json_utils`.
Scripts under `Tools/` are exempt when appropriate. For LLM/security checks,
require direct source evidence before reporting sensitive data leakage — do
not flag based on variable naming alone. Verify by reading the actual data
that flows through the exception handler.

## Verification Guidance
Verify ALL critical findings against the actual source file. For MAJOR
findings, sample-verify at least 30% (every 3rd finding) to catch false
positives. Report verification coverage: "N/N critical verified, N/N major sampled."

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/error_review_{shard_id}.md

Use EXACTLY this structure:
# Error Handling Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Broad Except Findings
#### {SEVERITY}: [Title]
**ID:** ERR-{shard_id}-[NUMBER]
**Location:** file.py:line
**Code:** [the actual line]
**Issue:** [description]
**Suggestion:** [what to change]
**LOC affected:** N

## JSON Bypass Findings
...

## Resource Cleanup Findings
...

## Additional Issues Found
...

## File Coverage Verification
| File | Status |
|------|--------|
| [full file list with "Read ✓" for each] |
```

#### Agent 2: Cross-Layer Error Propagation Validator

```
# Cross-Layer Error Propagation Validator

Trace error propagation paths across architectural layers. Validate that
errors originating in Simulation/Engine propagate correctly to Strategy
and UI layers without information loss.

## Documentation Reference
Read docs/05_ERROR_HANDLING.md and docs/01_ARCHITECTURE.md.

## Scope
All files under game/ (ui/, simulation/, strategy/, core/, engine/, ai/,
research/, assets/, services/).

## Methodology

1. **Map error boundaries:**
   - Identify every `try/except` that wraps a cross-layer call
   - Check that the catching layer doesn't lose diagnostic information
   - Verify that domain-specific exceptions are re-raised with context,
     not replaced with generic `RuntimeError`

2. **Trace critical error paths:**
   - Battle simulation failure → battle outcome → strategy turn processing
   - Galaxy generation error → strategy initialization → UI error display
   - Asset loading failure → AssetManager fallback → UI rendering
   - LLM provider failure → Service layer → UI feedback

3. **Validate error boundary pattern (Pattern #19):**
   - Check TurnEngine callback handlers all have broad-except wrappers
   - Verify snapshot-and-rollback is used where documented
   - Confirm no errors bypass the StrategySessionFacade without conversion

## Severity Guide
- CRITICAL: Error that would crash or corrupt game state with no fallback
- MAJOR: Information loss on error propagation; missing error boundary
- MINOR: Inconsistent error conversion pattern across similar paths

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/error_propagation_cross_layer.md

# Cross-Layer Error Propagation Report
## Summary
- Error Boundaries Mapped: [N]
- Critical Paths Traced: [N]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Error Boundary Audit
[Per-boundary analysis]

## Critical Path Analysis
[Per-path findings]

## Prioritized Recommendations
[Ordered by impact/effort]
```

#### Agent 3: LLM Context Security Validator

```
# LLM Context Security Validator

Audit every site that handles LLM-related exceptions or attaches diagnostic
context to logs. Verify that no API keys, request bodies, or raw provider
response text leaks into logs, error messages, or persisted state.

## Documentation Reference
Read docs/05_ERROR_HANDLING.md.

## Scope
- All files under game/services/llm/ and any caller of those services.
- Search the codebase for variable names: `api_key`, `secret`, `token`, `_request`, `_response`, `prompt`, `messages`.
- Search for any exception handler that builds a `dict()` containing keys
  named `request`, `response`, `body`, `payload`, `prompt`, `messages`.

## Methodology

1. Identify every catch site that produces an exception context dict or
   structured log message.
2. Verify the context never includes:
   - API keys or credentials
   - Full request bodies (truncate or redact)
   - Full provider response bodies (truncate or redact)
   - User-provided prompts that may contain PII
3. Check that all LLM service code lives behind the LLM service interface
   (per docs/05_ERROR_HANDLING.md) and converts provider-specific errors to
   domain-specific ones before propagating up.

## Severity Guide
- CRITICAL: API key, token, or full request body in a log statement that
  could reach disk or telemetry.
- MAJOR: Full provider response body logged at error/warning level.
- MINOR: Excess verbose context that could be trimmed; missing exception
  conversion at the service boundary.

## Output
Save to: {REVIEW_DIR}/findings/llm_context_security.md

# LLM Context Security Report
## Summary
- Sites Audited: [N]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Findings
[Per-site analysis]

## Recommendations
[Prioritized list]
```

### Step 4: Verify Agent Outputs

After all 6 agents complete, check that these files exist and are non-empty:
- `REVIEW_DIR/findings/error_review_01.md`
- `REVIEW_DIR/findings/error_review_02.md`
- `REVIEW_DIR/findings/error_review_03.md`
- `REVIEW_DIR/findings/error_review_04.md`
- `REVIEW_DIR/findings/error_propagation_cross_layer.md`
- `REVIEW_DIR/findings/llm_context_security.md`

### Step 5: Launch Verification Agent

Launch **1 verification agent** to cross-check all CRITICAL findings:

```
# Error Audit — Verification Agent

Read ALL error review reports and the cross-layer report.
For EVERY finding marked CRITICAL:

1. Read the cited line range in the actual source file
2. Verify the code matches the description
3. Check if the finding is justified (e.g., broad-except is truly
   missing a comment, or the comment exists but was missed)
4. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE

Output to: {REVIEW_DIR}/findings/verification.md

# Verification Report
## Critical Finding Verification
| Finding ID | File | Verdict | Reason |
|------------|------|---------|--------|

## Downgraded Findings
[List items that should be MAJOR not CRITICAL]

## Confirmed Critical
[List verified critical findings]
```

### Step 6: Compile Final Report

Read all agent reports and the verification report. Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Total findings across all sources
- Error hygiene score by layer

**2. Coverage Status**
| Shard | Files | LOC | Review File | Status |
|-------|-------|-----|-------------|--------|

**3. Error Hygiene Scorecard**
| Category | Count | Critical | Major | Minor |
|----------|-------|----------|-------|-------|
| Broad except w/o comment | [N] | | | |
| Bare except | [N] | | | |
| JSON bypass | [N] | | | |
| Generic raise Exception | [N] | | | |
| Print/traceback debug | [N] | | | |
| Resource cleanup gaps | [N] | | | |
| LLM context security | [N] | | | |

**4. Cross-Layer Error Propagation Issues**
Summary from the cross-layer validator.

**5. Prioritized Remediation Plan**
Top 10 items ordered by severity then by LOC affected. Sorted by `severity_weight × layer_weight × loc_affected` via `Tools/_audit_common/layer_weight.py`. All findings still appear in detail tables and the scorecard; weighting only affects this top-N ordering.

**6. Trend Comparison**
Use `Tools/_audit_common/run_tracker.py` with `audit_name="error"` to load the previous run's totals and render a delta table:

| Category | Previous Run | This Run | Delta |
|---|---|---|---|
| Critical | [N] | [N] | [+/-N] |
| Major | [N] | [N] | [+/-N] |
| Minor | [N] | [N] | [+/-N] |

After writing the report, append this run's totals via `run_tracker.py`.

**7. Appendices**
Paths to raw tool outputs, agent reports, and verification report.

### Step 7: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-error-audit
```

### Step 8: Present to User

Show the user:
1. Error hygiene scorecard summary
2. Critical findings count (verified)
3. Top 3 most impactful findings
4. Cross-layer propagation health (safe/warning/risky)
5. Path to the full report: `{REVIEW_DIR}/report.md`

Do NOT start making code changes. This is a read-only audit.
