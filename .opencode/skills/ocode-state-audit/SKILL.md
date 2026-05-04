---
name: ocode-state-audit
description: State management & mutability audit. Scans all production code for module-level mutable state, singleton divergence risk (ctx.xxx vs get_default_xxx()), global keyword abuse, class-level mutable defaults, and random.seed() bypass. Produces a PROJ-258 transition progress report and singleton divergence risk map. Production code only.
argument-hint: "[--skip-phase1 to reuse existing raw results]"
---

# State Management & Mutability Audit

Run a comprehensive audit of state management patterns across the production codebase. Scans for module-level mutable state, singleton divergence risk (PROJ-258 transition), global keyword usage, and unintended caching. Produces a state hygiene scorecard and singleton divergence risk map.

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

Ensure the state audit scanner exists:

```bash
python -c "import os; assert os.path.exists('Tools/state_audit/state_audit.py'), 'state_audit.py not found'"
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself** — do NOT ask the user to run it:

```bash
python Tools/state_audit/state_audit.py
```

Capture the output directory path from the last few lines of stdout.

Store this as `REVIEW_DIR`.

If the user passed `--skip-phase1`, find the most recent `Reviews/results/*_state-audit/`.

The script creates `REVIEW_DIR/raw/` with these outputs:

1. `singleton_sites.json` — every `_default_*`, `_instance`, `_singleton` definition
2. `module_mutables.json` — module-level dict/list/set assignments
3. `global_usages.json` — every `global` keyword with function context
4. `class_mutable_defaults.json` — class-level mutable parameter defaults
5. `random_seed_sites.json` — `random.seed()` outside per-battle RNG pattern
6. `ctx_usage_ratio.json` — `get_default_xxx()` vs `ctx.xxx` access ratio
7. `manifest.json` — 4-shard file assignments

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory:

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists
2. Read `REVIEW_DIR/raw/singleton_sites.json`
3. Read `REVIEW_DIR/raw/module_mutables.json`
4. Read `REVIEW_DIR/raw/global_usages.json`
5. Read `REVIEW_DIR/raw/class_mutable_defaults.json`
6. Read `REVIEW_DIR/raw/random_seed_sites.json`
7. Read `REVIEW_DIR/raw/ctx_usage_ratio.json`
8. Read `docs/02_PATTERNS.md` (Patterns #1, #4, #12 — ApplicationContext, Registry, Configuration)
9. Read `game/context.py` (PROJ-258 bridge mechanics)

### Step 3: Launch 5 Agents in Parallel

Create the findings directory:

```bash
mkdir -p REVIEW_DIR/findings
```

Launch **5 agents** in parallel using the Task tool with `subagent_type: general`:
- **4 in-shard deep review agents** (one per shard: 01, 02, 03, 04)
- **1 cross-shard divergence detector**

**Replace these placeholders:**
- `{REVIEW_DIR}` → actual review directory
- `{shard_id}` → `"01"`, `"02"`, `"03"`, `"04"`
- `{shard_label}` → from manifest.json
- `{shard_files}` → from manifest.json
- `{singleton_sites}` → full singleton_sites.json content
- `{global_usages}` → full global_usages.json content
- `{ctx_ratio}` → full ctx_usage_ratio.json content

#### Agents 1a-1d: In-Shard State Reviewers

```
# State Management Audit — Shard {shard_id} Reviewer

You are assigned ONE shard: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/02_PATTERNS.md Patterns #1 (ApplicationContext), #4 (Registry DI),
and #12 (Configuration Classes). Read game/context.py for PROJ-258 context.

## Scope
All files listed below MUST be read.

Shard file list:
{shard_files}

## Deterministic Scan Results (filtered for your shard)

Singleton definitions in your shard:
{singleton_sites}

Global keyword usages in your shard:
{global_usages}

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Validate singleton patterns:**
   - For each `_default_*` variable: is there a matching `set_default_*()`
     and `get_default_*()` pair? Is `ctx.xxx` also set by create_production()?
   - Is the singleton scoped correctly? (Module-level vs ApplicationContext)
   - Could this be migrated from module-level to ctx-managed?
3. **Check mutation risks:**
   - Module-level dict/list/set that is mutated after initialization
   - Cache invalidation issues — is there a stale cache risk?
   - Multiple accessors mutating the same module-level collection
4. **Global keyword usage:**
   - Verify each `global` is needed (could the value be passed/returned instead?)
   - Check for cross-module state leakage via global mutation
5. **Check class-level mutable defaults:**
   - Flag any parameter defaulting to `[]`, `{}`, or `set()`
6. **Random state hygiene:**
   - Verify `random.seed()` calls are ONLY in per-battle RNG initialization
7. **Track PROJ-258 progress:**
   - Count `get_default_xxx()` calls per file
   - Count `ctx.xxx` accesses per file
   - Flag files where both patterns coexist (divergence risk)

## What NOT to Report
- Module-level constants (ALL_CAPS convention) — these are intentional and immutable
- Module-level registries that are populated once at import and never mutated — these are infrastructure, not state bugs
- Function-scoped mutable defaults that are clearly never mutated
- TYPE_CHECKING blocks
- Lazy-loaded caches with proper invalidation (documented pattern)
- `random.Random(seed)` — this is the preferred per-instance pattern (Pattern #18). Only flag `random.seed()` on the global `random` module as suspect.

## State Classification Guide
- **Approved module-level defaults**: Singletons with `set_/get_` accessor pairs AND wired in `create_production()` — these are documented application bridges, not findings. Flag them only if the wiring is broken or diverging.
- **Unmanaged singleton**: Module-level mutable state with no setter, no ctx wiring, or divergent access patterns — this is a finding.
- **Cache safety**: For any cache, check: invalidation mechanism, lifetime owner, mutation path, and thread-safety. A cache with no invalidation is a finding. A cache with documented TTL or explicit `invalidate()` is fine.

## Severity Guide
- CRITICAL: Singleton with NO setter but MULTIPLE getters (will diverge);
  class-level mutable default that causes shared-state bugs
- MAJOR: Module-level collection mutated across files; high global keyword
  density; file using both ctx.xxx and get_default_xxx() (divergence risk)
- MINOR: Single-use module-level cache that could be local; unnecessary
  global keyword; PROJ-258 transition opportunity

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/state_review_{shard_id}.md

# State Management Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Singleton Findings
#### {SEVERITY}: [Title]
**ID:** ST-{shard_id}-[NUMBER]
**Location:** file.py:line
**Variable:** _default_xxx
**Has setter:** Yes/No
**Has ctx match:** Yes/No
**Call sites:** N (get_default) / N (ctx.xxx)
**Issue:** [description]
**Recommendation:** [migrate to ctx / add setter / leave as-is for documented reason]
**LOC affected:** N

## Module Mutable Collection Findings
...

## Global Keyword Findings
...

## Class Mutable Default Findings
...

## PROJ-258 Transition Progress (this shard)
- get_default_xxx() call sites: [N]
- ctx.xxx accesses: [N]
- Transition percentage: [N]%

## File Coverage Verification
| File | Status |
|------|--------|
| [full file list with "Read ✓"] |
```

#### Agent 2: Cross-Shard Divergence Detector

```
# Cross-Shard Divergence Detector

Detect state accessed differently across architectural layers — the
primary risk of the PROJ-258 transition state where ApplicationContext
and module-level singletons coexist.

## Documentation Reference
Read docs/01_ARCHITECTURE.md and game/context.py.

## Context
PROJ-258 exists as a bridge: ApplicationContext.create_production() calls
every set_default_xxx() to keep module-level singletons in sync with ctx.
But the UI layer still overwhelmingly uses get_default_xxx(). If any code
path sets ctx.xxx without also calling set_default_xxx(), or calls
set_default_xxx() without updating ctx, the instances diverge. The exact
call-site counts are derived from `ctx_usage_ratio.json` at runtime — do
not use hardcoded numbers from this skill text.

## Scope
All files under game/.

## Methodology

1. **Map every singleton to its usage pattern across layers:**
   - Which layers use get_default_xxx()?
   - Which layers use ctx.xxx?
   - Are there layers using both? (HIGH risk)
   - Is there a layer where neither is used? (Module loaded but not consumed)

2. **Check set_default_xxx() coverage:**
   - Does every _default_* variable have a set_default_*() function?
   - Does ApplicationContext.create_production() call ALL of them?
   - Are there direct assignments to _default_* that bypass both?

3. **Divergence risk scoring:**
   For each singleton, calculate risk based on:
   - Number of setter call sites
   - Number of getter call sites using module-level access
   - Number of getter call sites using ctx.xxx
   - Whether the singleton is mutable (dict/list) or immutable (int/str)

4. **Module-level collection analysis:**
   - Which mutable collections are potentially shared?
   - Are there lock/thread-safety mechanisms?
   - Could stale data persist in long-lived caches?

## Severity Guide
- CRITICAL: Singleton mutated via both ctx and set_default in different
  code paths; mutable module-level collection with no invalidation
- MAJOR: Singleton with setter but not wired in create_production();
  layer accessing singleton via both patterns
- MINOR: Unused setter function; cache that could be local

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/state_divergence_cross_shard.md

# Cross-Shard Divergence Report
## Summary
- Singletons Analyzed: [N]
- High Divergence Risk: [N]
- Medium Risk: [N]
- Low Risk: [N]

## Singleton Divergence Risk Map
### HIGH: _default_xxx
- **Module-level call sites:** [N] (layer1: N, layer2: N, ...)
- **ctx.xxx accesses:** [N] (layer1: N, ...)
- **Setter coverage:** create_production() line X
- **Mutable:** Yes/No
- **Risk:** [explanation]
- **Recommendation:** [migrate entirely to ctx / consolidate to single pattern]

### MEDIUM: _default_yyy
...

## PROJ-258 Overall Progress
| Layer | get_default sites | ctx sites | % via ctx | Trend |
|-------|-------------------|-----------|-----------|-------|
| ui | | | | |
| strategy | | | | |
| ... | | | | |

## Module-Level Collection Safety
[Per-collection analysis]

## Prioritized Remediation Plan
[Ordered by risk × call-site count]
```

### Step 4: Verify Agent Outputs

After all 5 agents complete, check that these files exist:
- `REVIEW_DIR/findings/state_review_01.md`
- `REVIEW_DIR/findings/state_review_02.md`
- `REVIEW_DIR/findings/state_review_03.md`
- `REVIEW_DIR/findings/state_review_04.md`
- `REVIEW_DIR/findings/state_divergence_cross_shard.md`

### Step 5: Launch Verification Agent

```
# State Audit — Verification Agent

Read ALL state review reports and the cross-shard divergence report.
For EVERY finding marked CRITICAL:

1. Read the cited source file at the indicated line
2. Verify the finding is accurate
3. Check if the finding's severity is justified
4. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE

Output to: {REVIEW_DIR}/findings/verification.md

# Verification Report
## Critical Finding Verification
| Finding ID | Variable | File | Verdict | Reason |
|------------|----------|------|---------|--------|

## Downgraded Findings
[List items reduced to MAJOR or MINOR]

## Confirmed Critical
[List verified critical findings]
```

### Step 6: Compile Final Report

Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Singleton count, divergence risk assessment
- PROJ-258 transition progress (overall ctx usage %)

**2. State Hygiene Scorecard**
| Category | Count | Critical | Major | Minor |
|----------|-------|----------|-------|-------|
| Singleton divergence risk | [N] | | | |
| Module-level mutable collections | [N] | | | |
| Global keyword usages | [N] | | | |
| Class mutable defaults | [N] | | | |
| random.seed() outside RNG | [N] | | | |

**3. Singleton Divergence Risk Map**
Per-singleton table with risk scores.

**4. PROJ-258 Transition Progress**
Per-layer migration status and overall percentage.

**5. Prioritized Remediation Plan**
Top 10 items.

**6. Appendices**
Paths to all raw and findings files.

### Step 7: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-state-audit
```

### Step 8: Present to User

Show the user:
1. State hygiene scorecard summary
2. Singleton divergence risk count (HIGH/MEDIUM/LOW)
3. PROJ-258 transition progress (% via ctx)
4. Top 3 highest-risk singletons
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
