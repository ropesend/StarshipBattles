---
name: ocode-pattern-audit
description: Pattern conformance & architecture drift audit. Validates all 31 documented patterns against live code. Checks layer dependency boundaries, Registry DI compliance, Facade bypass, CQRS-lite adherence, protocol conformance, naming collisions, and LOC ceiling violations. Produces a pattern health scorecard with drift severity map. Production code only.
argument-hint: "[--skip-phase1] [--focus PATTERN_NAME]"
---

# Pattern Conformance & Architecture Drift Audit

Run a comprehensive audit of pattern adherence across the production codebase. Validates the 8-layer dependency table, checks for pattern bypass (Registry DI, Facade, CQRS-lite), detects naming collisions, and scores the 31 documented patterns for conformance against live code.

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

Ensure the pattern audit tools exist:

```bash
python -c "import os; assert os.path.exists('Tools/pattern_audit/pattern_audit.py'), 'pattern_audit.py not found'"
python -c "import os; assert os.path.exists('Tools/pattern_audit/layer_validator.py'), 'layer_validator.py not found'"
python -c "import os; assert os.path.exists('Tools/check_file_size/check_file_size.py'), 'check_file_size.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself:**

```bash
python Tools/pattern_audit/pattern_audit.py
```

Capture `REVIEW_DIR` from stdout.

If the user passed `--skip-phase1`, find the most recent `Reviews/results/*_pattern-audit/`.

The script creates `REVIEW_DIR/raw/` with these outputs:

1. `layer_violations.json` — every import crossing a forbidden layer boundary
2. `loc_baseline.json` — LOC by section
3. `file_size_violations.txt` — files over 500 LOC
4. `protocol_registry.json` — Protocol classes found + TypeGuard presence
5. `manifest.json` — 4-shard file assignments

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory:

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists
2. Read `REVIEW_DIR/raw/layer_violations.json`
3. Read `REVIEW_DIR/raw/file_size_violations.txt`
4. Read `REVIEW_DIR/raw/protocol_registry.json`
5. Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`

The docs document **31 patterns**. Read the Table of Contents in `docs/02_PATTERNS.md` to get the current pattern list at runtime — do NOT use a manually copied enumeration. The canonical ToC headings (as of the doc's last-verified date) define the active pattern set. When evaluating pattern adherence, reference patterns by their doc heading number and name verbatim.

### Step 3: Launch 6 Agents in Parallel

Launch **6 agents**:
- **4 in-shard pattern reviewers** (one per shard: 01, 02, 03, 04)
- **1 cross-shard pattern hunter**
- **1 pattern documentation validator**

**Replace placeholders:**
- `{REVIEW_DIR}` → actual review directory
- `{shard_id}`, `{shard_label}`, `{shard_files}` → from manifest.json
- `{layer_violations}` → layer_violations.json content

#### Agents 1a-1d: In-Shard Pattern Reviewers

```
# Pattern Conformance Audit — Shard {shard_id} Reviewer

You are assigned ONE shard: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/01_ARCHITECTURE.md and docs/02_PATTERNS.md. You must understand
all 31 patterns before reviewing files.

## Scope
Shard file list:
{shard_files}

## Layer Violations (filtered for your shard)
{layer_violations}

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Validate layer dependency violations:**
   - For each violation: is it a TYPE_CHECKING import (benign)?
   - Is it a late import with a documented intentional bridge comment?
   - Is it a genuine violation that needs remediation?
3. **Check for pattern bypass (the most damaging form of drift):**
   - **Registry DI bypass (#3):** Is any simulation/strategy code calling
     get_default_registry_provider()? (This was banned by PROJ-252.)
   - **Facade bypass (#5):** Is UI code directly importing engine/simulation
     internals instead of going through StrategySessionFacade?
   - **CQRS-lite violation (#6):** Are DTOs being mutated? Are commands
     returning data?
   - **Protocol bypass (#2):** Is code using isinstance() checks against
     concrete implementations instead of Protocol TypeGuard functions?
   - **CommandHandlerRegistry bypass (#7):** Are strategy commands dispatched
     via if/elif chains instead of the registry's `dispatch()`? Use the live
     pattern doc's named API surface; current example: `CommandHandlerRegistry.dispatch()`.
   - **Ability aggregation bypass (#14):** Is two-phase aggregation reimplemented
     locally? Use the pattern doc's shared function; current example: `_aggregate_ability_groups()`.
   - **Scope-Driven Team Routing bypass (#25):** Is scope routing duplicated
     locally instead of using the registry? Use the pattern doc's constants
     and helpers; current examples: `OPPONENT_SCOPES`, `_route_team_ids`.
   - **Ability-Stat Registry bypass (#26):** Are `ModifierEntry` objects
     constructed by hand? Use the pattern doc's entry point; current example:
     `emit_entries_for_ability()`.
   - **Strategy Modal Window (#31) vs superseded #30:** New strategy-modal
     windows must subclass `StrategyModalWindow`. Flag windows implementing
     manual close-callback tracking when #31 is the current contract.
   - For ALL bypass checks: the pattern doc's named helpers/APIs are the
     single source of truth. The examples above are current as of the docs'
     last-verified date; always verify against the live doc.
4. **Check naming collisions:**
   - Two distinct classes/functions with the same name in different layers
   - Example: EventBus appears in both game/ui/screens/builder/ and game/core/
5. **Check Configuration class conformance (#12):**
   - Config classes using direct json.load instead of json_utils
   - Config classes incorrectly using @dataclass — core config classes in `game/core/config.py` are plain classes per Pattern #12, not dataclasses
   - JSON-backed strategy configs using the documented `DEFAULT_*` dict + `_load_from_json()` pattern
6. **Check new patterns not yet documented:**
   - If you observe a recurring pattern that isn't in docs/02_PATTERNS.md,
     flag it as "undocumented pattern" so docs can be updated

## What NOT to Report
- Patterns that are documented as superseded (#30 is documented as
  superseded by #31 — do not flag #30 usage as a violation)
- Pattern usage that varies intentionally for valid reasons
- Test files
- Pygame idioms that don't match GoF pattern purity

## Severity Guide
- CRITICAL: Registry DI bypass (simulation calling get_default_registry_provider());
  Facade bypass (UI calling engine internals); Layer dependency violation
  that is NOT TYPE_CHECKING or documented bridge
- MAJOR: CQRS-lite DTO mutation; Protocol bypass with isinstance();
  naming collision between layers; undocumented pattern used in 3+ places
- MINOR: Minor config convention deviation; pattern implementation detail
  that could be tightened; opportunity to adopt a documented pattern where
  ad-hoc code exists

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/pattern_review_{shard_id}.md

# Pattern Conformance Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Layer Dependency Violations
#### {SEVERITY}: [Title]
**ID:** PAT-{shard_id}-[NUMBER]
**Location:** file.py:line
**From Layer:** X | **To Layer:** Y
**Import:** import path
**Type:** TYPE_CHECKING / late-import / direct
**Issue:** [description]
**Recommendation:** [fix]
**LOC affected:** N

## Pattern Bypass Findings
...

## Naming Collisions
...

## Configuration Conventions
...

## Undocumented Patterns Found
...

## File Coverage Verification
| File | Status |
|------|--------|
| [full file list with "Read ✓"] |
```

#### Agent 2: Cross-Shard Pattern Hunter

```
# Cross-Shard Pattern Hunter

Hunt for pattern erosion that spans shard boundaries. The same architectural
pattern may degrade differently across layers — your job is to find the gaps.

## Documentation Reference
Read docs/01_ARCHITECTURE.md and docs/02_PATTERNS.md.

## Scope
All files under game/.

## Methodology

1. **Facade integrity check (#5):**
   - StrategySessionFacade should be the ONLY entry point from UI into
     the Strategy layer.
   - Scan UI screens for imports from game/strategy/data/ or
     game/strategy/engine/ that bypass the Facade.
   - Flag any UI component that constructs Strategy data objects directly.

2. **Registry pattern consistency (#4):**
   - Are registries hydrated consistently across layers?
   - Is the same registry accessed via different patterns in different layers?
   - Check: session_cache usage in tests vs production paths.

3. **Event bus fragmentation (#10):**
   - Two distinct EventBus implementations exist (UI builder and Core).
   - Is either being used where the other is appropriate?
   - Are there places where an event bus SHOULD be used but isn't?

4. **CQRS-lite audit (#6):**
   - Trace command flow: are commands constructed, dispatched, and handlers
     invoked consistently?
   - Are any commands modifying state directly instead of going through
     handlers?

5. **Ability source drift (#29):**
   - The Universal Ability Source pattern has 8 documented adapters.
   - Are new ability sources being added that DON'T use the adapter pattern?

## Severity Guide
- CRITICAL: Facade bypass (UI importing strategy internals); Cross-layer
  pattern fork where same concept implements differently in each layer
- MAJOR: Event bus fragmentation where one bus is used but the other is
  needed; New ability source without adapter
- MINOR: Minor pattern inconsistency across layers

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/pattern_hunter_cross_shard.md

# Cross-Shard Pattern Hunter Report
## Summary
- Pattern Checks Performed: [N]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Facade Integrity
...

## Registry Consistency
...

## Event Bus Fragmentation
...

## CQRS-lite Audit
...

## Ability Source Drift
...

## Prioritized Architectural Recommendations
[Ordered by structural impact]
```

#### Agent 3: Pattern Documentation Validator

```
# Pattern Documentation Validator

Cross-reference the 31 documented patterns in docs/02_PATTERNS.md against
their actual usage in code. Flag patterns that are documented but unused,
patterns that are used but not documented, and documentation that no longer
matches the implementation.

## Documentation Reference
Read docs/02_PATTERNS.md (you must understand all 31 patterns).

## Scope
docs/02_PATTERNS.md + all files under game/.

## Methodology

For EACH of the 31 documented patterns:

1. **Read the pattern's documentation** in docs/02_PATTERNS.md.
2. **Find the pattern's implementation(s)** in game/.
3. **Compare:** Does the code match what the doc describes?
   - Code structure: same classes, methods, decorators?
   - File locations: are the files where the doc says they are?
   - Naming: do the documented names match the actual names?
4. **Rate the doc accuracy:** ACCURATE / MINOR_DIFF / STALE / WRONG

Also hunt for:
- Patterns used in code but NOT in docs/02_PATTERNS.md
- Patterns documented but with zero usage in current code
- Pattern documentation that references deleted PROJ phases

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/pattern_docs_validator.md

# Pattern Documentation Validation Report
## Summary
- Patterns Documented: 31
- Patterns Verified: [N]
- Accurate: [N] | Minor Diff: [N] | Stale: [N] | Wrong: [N]
- Undocumented Patterns Found: [N]

## Pattern Accuracy Assessment
| # | Pattern Name | Accuracy | Issues |
|---|-------------|----------|--------|
| 1 | ApplicationContext | ACCURATE | |
| 2 | Protocol+TypeGuard | MINOR_DIFF | [details] |
| ... | | | |

## Undocumented Patterns
[List recurring patterns in code that have no doc entry]

## Dead Pattern Documentation
[Patterns in docs with zero current usage]

## Documentation Update Recommendations
[Prioritized list of doc changes needed]
```

### Step 4: Verify Agent Outputs

Check that these files exist:
- `REVIEW_DIR/findings/pattern_review_01.md`
- `REVIEW_DIR/findings/pattern_review_02.md`
- `REVIEW_DIR/findings/pattern_review_03.md`
- `REVIEW_DIR/findings/pattern_review_04.md`
- `REVIEW_DIR/findings/pattern_hunter_cross_shard.md`
- `REVIEW_DIR/findings/pattern_docs_validator.md`

### Step 5: Launch Verification Agent

```
# Pattern Audit — Verification Agent

Read ALL pattern review reports.
For EVERY finding marked CRITICAL:

1. Read the cited source code
2. Verify the pattern violation is genuine
3. Check severity is justified
4. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE

Output to: {REVIEW_DIR}/findings/verification.md
```

### Step 6: Compile Final Report

Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Pattern health score (overall % compliance)
- Layer dependency: violations found vs intentional bridges

**2. Layer Dependency Violations**
Confirmed violations only, with remediation plan.

**3. Pattern Adherence Scorecard**
| # | Pattern | Compliance | Status | Notes |
|---|---------|-----------|--------|-------|
| 1 | ApplicationContext | [%] | [STRONG/MINOR_DRIFT/STALE] | |
| ... | | | | |

**4. Architecture Drift Findings**
Cross-shard pattern hunter results.

**5. Documentation Accuracy**
Pattern docs validator results.

**6. Naming Collision Register**

**7. LOC Ceiling Violations**

**8. Prioritized Architecture Remediation Plan**

**9. Appendices**

### Step 7: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-pattern-audit
```

### Step 8: Present to User

Show the user:
1. Pattern health score (overall %)
2. Layer dependency status (violations / intentional bridges)
3. Top 3 pattern drift findings
4. Documentation accuracy breakdown
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
