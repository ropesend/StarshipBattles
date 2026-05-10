---
name: ocode-legacy-audit
description: Legacy code, alias, shim, and migration-code audit. Detects module aliases, __init__.py re-export shims, deprecation markers, wrapper delegates, name-pair drift, save-migration code, superseded-pattern uses, TYPE_CHECKING-only re-exports, and partial Protocol implementers. Produces a legacy-removal scorecard with prioritized cleanup plan. Production code only.
argument-hint: "[--skip-phase1 to reuse existing raw results]"
---

## Invocation

- **Slash command (interactive):** `/ocode-legacy-audit`
- **CLI (non-interactive):** `opencode run "Load the ocode-legacy-audit skill and execute it. Args: [optional --skip-phase1]"`

The skill is identical in both modes. CLI mode skips any user-prompt confirmations and defaults to the most conservative option, noting the choice in the report.

# Legacy Code & Shim Audit

Run a comprehensive audit of legacy code, aliases, shims, deprecation markers, and migration code across the production codebase. Detects module aliases, `__init__.py` re-export shims, deprecation markers, wrapper delegates, name-pair drift between two implementations of the same concept, save-migration code (banned by `CLAUDE.md`), superseded-pattern usage, `TYPE_CHECKING`-only re-exports preserving old import paths, and partial Protocol implementers. Produces a legacy-removal scorecard with a prioritized cleanup plan.

The codebase explicitly bans these patterns (see `CLAUDE.md` "no save migrations", "no compatibility shims"; PROJ-58 eradicated shims; PROJ-298 removed 8 module aliases) — so any remaining instances are drift to be cleaned up.

Does NOT change any code. Targets `game/` only (not tests).

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

Ensure the legacy audit scanner exists:

```bash
python -c "import os; assert os.path.exists('Tools/legacy_audit/legacy_audit.py'), 'legacy_audit.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/legacy_audit/legacy_audit.py
```

Capture the output directory path from the last few lines of stdout. It will look like:
```
Output directory: Reviews/results/2026-05-07_120000_legacy-audit
```

Store this as `REVIEW_DIR`.

If the user passed `--skip-phase1`, find the most recent `Reviews/results/*_legacy-audit/` directory (sort by directory name, take the newest) and use that as `REVIEW_DIR`.

The script creates `REVIEW_DIR/raw/` with these outputs against `game/`:

1. `module_aliases.json` — top-level `OldName = NewName` assignments where both are bare names (likely re-export shims)
2. `init_reexports.json` — `__init__.py` star-imports or aliasing imports from non-sibling modules
3. `deprecation_markers.json` — `# DEPRECATED`, `# LEGACY`, `# TODO: remove`, `# kept for backward compat`, `# old`, `@deprecated`, `DeprecationWarning(`
4. `wrapper_delegates.json` — functions whose body is exactly `return other_func(...)` or `return self.other(...)` with same arity
5. `name_pair_drift.json` — classes/functions where `Foo` and `LegacyFoo`/`OldFoo`/`FooV1` both exist; or `XManager` + `XService` pairs with overlapping methods
6. `save_migration_code.json` — functions named `migrate_*`, `_migrate_*`, `convert_legacy_*`, `upgrade_save_*`, or files matching `*_migration.py`; cross-referenced against `data/saves/` schema
7. `superseded_pattern_uses.json` — usages of patterns marked "superseded by #N" in `docs/02_PATTERNS.md`
8. `type_checking_only_reexports.json` — imports inside `if TYPE_CHECKING:` whose only purpose is preserving an old import path
9. `optional_protocol_methods.json` — Protocol classes with methods that exist only on the new implementation (legacy impl missing them)
10. `manifest.json` — 4-shard file assignments for agent distribution

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory:

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists
2. Read `REVIEW_DIR/raw/module_aliases.json`
3. Read `REVIEW_DIR/raw/init_reexports.json`
4. Read `REVIEW_DIR/raw/deprecation_markers.json`
5. Read `REVIEW_DIR/raw/wrapper_delegates.json`
6. Read `REVIEW_DIR/raw/name_pair_drift.json`
7. Read `REVIEW_DIR/raw/save_migration_code.json`
8. Read `REVIEW_DIR/raw/superseded_pattern_uses.json`
9. Read `REVIEW_DIR/raw/type_checking_only_reexports.json`
10. Read `REVIEW_DIR/raw/optional_protocol_methods.json`
11. Read `docs/02_PATTERNS.md` (for superseded-pattern lookups and pattern conventions)
12. Read `CLAUDE.md` Rule 3 (Root Cause Fixes — bans compatibility shims and save migrations)

The Phase 1 tool also writes per-shard filtered copies for each raw JSON: `module_aliases_{shard_id}.json`, `init_reexports_{shard_id}.json`, `deprecation_markers_{shard_id}.json`, `wrapper_delegates_{shard_id}.json`, `name_pair_drift_{shard_id}.json`, `save_migration_code_{shard_id}.json`, `superseded_pattern_uses_{shard_id}.json`, `type_checking_only_reexports_{shard_id}.json`, `optional_protocol_methods_{shard_id}.json`. Agents are passed paths to those filtered files rather than full JSON content.

### Step 3: Launch 5 Agents in Parallel

Create the findings directory:

```bash
mkdir -p REVIEW_DIR/findings
```

Launch **5 OpenCode subagents in parallel**. Each subagent receives the prompt template below with placeholders replaced. Wait for all to complete before proceeding to Step 4.

- **4 in-shard legacy reviewers** (one per shard: 01, 02, 03, 04)
- **1 cross-system duplicate-systems hunter**

**Replace these placeholders in each template before sending:**
- `{REVIEW_DIR}` → the actual review directory
- `{shard_id}` → `"01"`, `"02"`, `"03"`, `"04"`
- `{shard_label}` → from manifest.json `shards.{shard_id}.label`
- `{shard_files}` → the file list from manifest.json `shards.{shard_id}.files`, formatted as a markdown list

Agents read their per-shard filtered JSON files directly from disk — do NOT inline JSON content into prompts.

#### Agents 1a-1d: In-Shard Legacy Reviewers

Launch **4 agents** using the template below — one for each shard.

```
# Legacy Code Audit — Shard {shard_id} Reviewer

You are assigned ONE shard: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/02_PATTERNS.md for current patterns and any "superseded by #N"
markers. Read CLAUDE.md Rule 3 ("Root Cause Fixes") — it explicitly bans
compatibility shims, save migrations, and duplicate logic. Any code that
violates Rule 3 is a finding regardless of how long it has been there.

## Scope
All files listed below MUST be read. If you skip any file, the coverage
guarantee is broken.

Shard file list:
{shard_files}

## Deterministic Scan Results (filtered for your shard)

Read these per-shard filtered JSON files for the deterministic findings
restricted to your shard:

- `{REVIEW_DIR}/raw/module_aliases_{shard_id}.json`
- `{REVIEW_DIR}/raw/init_reexports_{shard_id}.json`
- `{REVIEW_DIR}/raw/deprecation_markers_{shard_id}.json`
- `{REVIEW_DIR}/raw/wrapper_delegates_{shard_id}.json`
- `{REVIEW_DIR}/raw/name_pair_drift_{shard_id}.json`
- `{REVIEW_DIR}/raw/save_migration_code_{shard_id}.json`
- `{REVIEW_DIR}/raw/superseded_pattern_uses_{shard_id}.json`
- `{REVIEW_DIR}/raw/type_checking_only_reexports_{shard_id}.json`
- `{REVIEW_DIR}/raw/optional_protocol_methods_{shard_id}.json`

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Validate deterministic findings within your shard:**
   - For each module alias `OldName = NewName`: search for call sites of
     `OldName` across `game/` (use Grep). If zero production call sites,
     flag the alias as CRITICAL — the file/symbol can be deleted in one PR.
   - For each `__init__.py` re-export: confirm it preserves an old public
     import path. If callers can be updated to import from the new module
     directly, the re-export is a shim and a finding.
   - For each deprecation marker: check whether a removal plan exists (linked
     PROJ ticket, dated TODO). Markers without a removal plan are MINOR
     findings.
   - For each wrapper delegate: confirm the wrapper body is genuinely a
     pass-through. If the underlying callee has non-trivial usage, flag the
     wrapper as MAJOR (call sites need migration). If the wrapper has zero
     production call sites, CRITICAL (delete the wrapper).
   - For each `name_pair_drift` entry: confirm both names refer to the same
     concept. Flag the legacy-named member as MAJOR (or CRITICAL if zero
     production call sites).
   - For each `save_migration_code` entry: CLAUDE.md Rule 3 bans these. Flag
     CRITICAL regardless of usage.
   - For each `superseded_pattern_uses` entry: cross-reference against
     `docs/02_PATTERNS.md` to confirm the supersession is current. Flag MINOR
     in non-critical code; MAJOR if the pattern is in a hot path.
   - For each `type_checking_only_reexport`: confirm the re-export's only
     purpose is preserving an old import path. If so, MINOR.
   - For each `optional_protocol_methods` entry: check if the legacy
     implementation is wired in production. If yes, MAJOR (incomplete
     Protocol). If no production wiring, CRITICAL (delete the legacy impl).

3. **Hunt for additional legacy indicators not caught by Phase 1:**
   - **Shim files:** Does the file exist solely to re-export from another
     file? (E.g., the file body is just `from .new_module import *` plus a
     few aliases.) Flag as CRITICAL if zero call sites against the legacy
     path.
   - **Stale PROJ comments:** Comments referencing deleted PROJ phases or
     completed migrations as if still in progress (e.g., "TODO PROJ-258:
     migrate to ctx" when PROJ-258 is archived). Flag as MINOR — these
     mislead future readers.
   - **Test-only callers:** Functions called only from tests but never from
     production. These are unwired/legacy infrastructure. Flag as MAJOR
     and cross-link to `ocode-audit-shrink` results if present in
     `Reviews/results/*_audit-shrink/`.
   - **Unused `set_default_*` shim functions:** functions whose only caller
     is `ApplicationContext.create_production()`. Flag as MINOR (bridge
     mechanics that should ultimately be removed).

## What NOT to Report
- Module aliases inside `__init__.py` files that are part of a documented
  public API (re-exports for the package's intended import surface).
- Deprecation markers with an active linked PROJ ticket (those are tracked
  removal plans, not drift).
- Wrapper functions that exist for a documented reason (e.g., a thin
  adapter at a boundary documented in `docs/02_PATTERNS.md`).
- Forward-compat extension points (e.g., a Protocol method declared but
  optionally overridden, where the omission is by design — verify against
  the Protocol's docstring).
- TYPE_CHECKING imports that resolve circular-import problems (these are
  not legacy preservation).
- Tests, fixtures, or anything under `tests/` (out of scope).

## Severity Guide
- **CRITICAL**: Module alias / wrapper file with zero call sites in
  production (entire file/symbol can be deleted in one PR); save-migration
  code (banned by CLAUDE.md); shim file existing solely to re-export from
  another file with zero callers against the legacy path.
- **MAJOR**: Wrapper function delegating to one new function with
  non-trivial usage (call sites need migration); duplicate system pair
  where one is clearly legacy; partial Protocol implementer wired in
  production; test-only callers of production functions.
- **MINOR**: Deprecation marker without a removal plan; superseded-pattern
  usage in non-critical code; unused `set_default_*` shim functions; stale
  PROJ comments; TYPE_CHECKING-only re-exports preserving old import paths.
- **INFO**: Suspected legacy but unclear (handoff to skeptical verifier).

## Verification Guidance
Verify ALL CRITICAL findings against the actual source file. For MAJOR
findings, sample-verify at least 30% (every 3rd finding) by re-reading
the file and confirming the call-site count. Report verification coverage
at the bottom of your report: "N/N critical verified, N/N major sampled."

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/legacy_review_{shard_id}.md

Use EXACTLY this structure:

# Legacy Code Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N] | Info: [N]

## Module Alias Findings
#### {SEVERITY}: [Title]
**ID:** LEG-{shard_id}-[NUMBER]
**Location:** file.py:line
**Symbol:** OldName (alias of NewName)
**Production call sites:** N
**Issue:** [description]
**Recommendation:** [delete alias / migrate N callers / leave for documented reason]
**LOC affected:** N

## __init__.py Re-export Shim Findings
...

## Deprecation Marker Findings
...

## Wrapper Delegate Findings
...

## Name-Pair Drift Findings
...

## Save Migration Code Findings
...

## Superseded Pattern Usage Findings
...

## TYPE_CHECKING Re-export Findings
...

## Partial Protocol Implementer Findings
...

## Additional Legacy Indicators (Phase 1 did not catch)
[Shim files, stale PROJ comments, test-only callers, unused set_default_* shims]

## Verification Coverage
- Critical findings verified: N/N
- Major findings sampled: N/N

## File Coverage Verification
| File | Status |
|------|--------|
| [full file list with "Read ✓" for each] |
```

#### Agent 2: Cross-System Duplicate-Systems Hunter

```
# Cross-System Duplicate-Systems Hunter

Hunt for two implementations of the same concept across the codebase.
Phase 1's `name_pair_drift.json` catches AST-detectable cases (e.g., `Foo`
+ `LegacyFoo`); your job is to find narrative pairs the AST cannot detect
(e.g., two distinct fleet-formation systems with different class names but
overlapping responsibilities).

## Documentation Reference
Read docs/01_ARCHITECTURE.md and docs/02_PATTERNS.md.

## Scope
All files under game/ (ui/, simulation/, strategy/, core/, engine/, ai/,
research/, assets/, services/).

## Phase 1 Inputs

Read the full unfiltered files for cross-shard analysis:
- `{REVIEW_DIR}/raw/name_pair_drift.json`
- `{REVIEW_DIR}/raw/optional_protocol_methods.json`

## Methodology

1. **Validate Phase 1 name-pair drift entries:**
   - For each pair, confirm both names refer to the same concept.
   - Identify which is legacy (older first commit, deprecation marker,
     fewer call sites, marked by docs as superseded).
   - Estimate migration effort = number of production call sites against
     the legacy member.

2. **Hunt narrative pairs Phase 1 cannot detect:**
   - Look for two classes/modules with overlapping method sets that
     conceptually do the same thing (e.g., `FleetFormationManager` +
     `SquadronArrangementService`). Use Grep on method names — if two
     classes share ≥3 method names with similar parameter shapes, treat
     as a candidate pair.
   - Look for two registries holding the same kind of data (e.g., two
     ability registries, two design registries) — check `game/core/`,
     `game/strategy/data/`, `game/services/`.
   - Look for two configuration loaders for the same JSON schema.
   - Look for two paths converting between the same two types
     (e.g., two `ShipSpec → BattleSpec` builders).

3. **Classify each pair:**
   - **Clear legacy:** one is documented as superseded; the other is the
     canonical path.
   - **Ambiguous:** both are in active use with no clear winner — flag as
     INFO and recommend an architectural decision.
   - **Intentional split:** the two serve genuinely different use cases
     (e.g., production vs Combat Lab) — NOT a finding.

4. **Estimate consolidation cost:**
   - Number of files importing each member.
   - Cyclomatic divergence: do the two implementations behave identically
     on the same inputs? If they diverge in behaviour, consolidation
     requires a behaviour-reconciliation decision.

## Severity Guide
- **CRITICAL**: Duplicate system pair where the legacy member has zero
  production call sites (delete the legacy member in one PR).
- **MAJOR**: Duplicate system pair where one is clearly legacy with
  non-trivial call sites (call sites need migration).
- **MINOR**: Duplicate system pair where both are in active use but a
  consolidation would simplify the architecture.
- **INFO**: Ambiguous pair — needs an architectural decision.

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/legacy_duplicate_systems_cross.md

# Cross-System Duplicate-Systems Report
## Summary
- Pairs Analyzed: [N]
- Clear Legacy: [N]
- Ambiguous: [N]
- Intentional Split (NOT findings): [N]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N] | Info: [N]

## Phase 1 Name-Pair Drift Validation
[Per-pair analysis with verdict]

## Narrative Pairs (Phase 1 did not catch)
[Per-pair analysis with overlap evidence]

## Prioritized Consolidation Plan
[Ordered by severity × call-site count]

Findings are sorted by `severity_weight × layer_weight × loc_affected`
(using `Tools/_audit_common/layer_weight.py`). All findings still appear
in the per-pair tables above — weighting only affects this top-N ordering.
```

### Step 4: Verify Agent Outputs

After all 5 agents complete, check that these files exist and are non-empty:
- `REVIEW_DIR/findings/legacy_review_01.md`
- `REVIEW_DIR/findings/legacy_review_02.md`
- `REVIEW_DIR/findings/legacy_review_03.md`
- `REVIEW_DIR/findings/legacy_review_04.md`
- `REVIEW_DIR/findings/legacy_duplicate_systems_cross.md`

If any are missing or empty, re-launch the corresponding agent before proceeding.

### Step 5: Launch Verification Agent

Launch **1 verification agent** to skeptically cross-check all CRITICAL findings:

```
# Legacy Audit — Verification Agent

Read ALL legacy review reports and the cross-system duplicate-systems
report. For EVERY finding marked CRITICAL:

1. Read the cited source file at the indicated line/range
2. Verify the code matches the description
3. Confirm the finding is genuinely legacy (not e.g. a forward-compat
   extension point or a documented public API surface)
4. Re-run the call-site count via Grep across `game/` to confirm
   zero/non-trivial usage as claimed
5. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE

For each DISPUTED finding, explain why (e.g., "alias has 4 production call
sites — should be MAJOR not CRITICAL", or "this Protocol method IS
implemented on the legacy class at line N").

For each INCONCLUSIVE finding, identify what additional evidence would
resolve it.

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/verification.md

# Verification Report
## Critical Finding Verification
| Finding ID | Symbol/File | Verdict | Reason |
|------------|-------------|---------|--------|

## Downgraded Findings
[List items that should be MAJOR not CRITICAL with rationale]

## Confirmed Critical
[List verified critical findings — these are safe-to-act-on legacy removals]

## Inconclusive Findings
[List items needing more evidence + what evidence would resolve them]
```

### Step 6: Compile Final Report

Read all agent reports and the verification report. Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Total legacy findings across all categories
- Overall legacy-removal posture (clean / drift / heavy)
- Count of one-PR-deletable items (CRITICAL with zero call sites)

**2. Legacy Inventory by Category**

| Category | Count | Critical | Major | Minor | Info |
|----------|-------|----------|-------|-------|------|
| Module aliases | [N] | | | | |
| `__init__.py` re-export shims | [N] | | | | |
| Deprecation markers | [N] | | | | |
| Wrapper delegates | [N] | | | | |
| Duplicate systems | [N] | | | | |
| Save migration code | [N] | | | | |
| Superseded pattern usage | [N] | | | | |
| TYPE_CHECKING-only re-exports | [N] | | | | |
| Partial Protocol implementers | [N] | | | | |

**3. Legacy Removal Scorecard**

Per-category breakdown with severity counts and total LOC affected. Highlight categories where CLAUDE.md Rule 3 violations exist (save migrations, shims) — these are non-negotiable removals.

**4. Prioritized Removal Plan**

Top 10–20 items ordered by removal impact and effort.

```python
from Tools._audit_common import layer_weight
# severity_weight: CRITICAL=10, MAJOR=5, MINOR=1, INFO=0.25
# Final score = severity_weight × layer_weight × loc_affected
score = severity_weight * layer_weight.weight_for(file_path) * loc_affected
```

All findings still appear in the inventory tables above — weighting only affects this top-N ordering. Sort the table descending by score.

| Rank | Finding ID | Category | Severity | Layer | LOC | Score | Action |
|------|------------|----------|----------|-------|-----|-------|--------|

**5. Trend Comparison**

Use `Tools/_audit_common/run_tracker.py` with `audit_name="legacy"` to load the previous run's totals and render a delta table:

```python
from Tools._audit_common import run_tracker
trend = run_tracker.compute_trend("Reviews/results", "legacy", current_summary)
markdown = run_tracker.render_trend_markdown(trend)
```

Append the rendered markdown:

| Category | Previous Run | This Run | Delta |
|---|---|---|---|
| Critical | [N] | [N] | [+/-N] |
| Major | [N] | [N] | [+/-N] |
| Minor | [N] | [N] | [+/-N] |

After writing the report, append this run's totals via `run_tracker.add_run("Reviews/results", "legacy", current_summary)`.

**6. Refinement Notes**

Placeholder section. Populated when `claude-proj-from-legacy-audit` later writes refinement proposals (false-positive patterns to add to "What NOT to Report", missed checks to add, severity calibration). Leave with the heading and the line:

> No refinements yet. The Claude bridge skill `claude-proj-from-legacy-audit` writes proposals here when it converts this review into projects.

**7. Appendices**
- Path to raw tool outputs: `{REVIEW_DIR}/raw/`
- Paths to agent finding reports: `{REVIEW_DIR}/findings/legacy_review_*.md`, `legacy_duplicate_systems_cross.md`
- Path to verification report: `{REVIEW_DIR}/findings/verification.md`
- Path to manifest: `{REVIEW_DIR}/raw/manifest.json`

### Step 7: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-legacy-audit
```

### Step 8: Present to User

Show the user:
1. Legacy-removal scorecard summary (one line per category)
2. Count of HIGH/MEDIUM/LOW removals (CRITICAL/MAJOR/MINOR)
3. Top 3 removal candidates from the Prioritized Removal Plan (ID, location, action, score)
4. Trend arrow vs the previous run (improving / unchanged / worsening) per category
5. Path to the full report: `{REVIEW_DIR}/report.md`

Do NOT start making code changes. This is a read-only audit. The Claude bridge skill `claude-proj-from-legacy-audit` (separate, manual invocation) converts this review into projects.
