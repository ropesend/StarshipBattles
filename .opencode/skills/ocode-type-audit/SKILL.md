---
name: ocode-type-audit
description: Type safety & annotation quality audit. Runs mypy strict-mode + AST annotation scanner. Audits -> Any density by layer, missing return types, # type: ignore justifications, cast() proliferation, and TYPE_CHECKING block hygiene. Produces a type safety scorecard and mypy strict-mode readiness assessment. Production code only.
argument-hint: "[--skip-phase1] [--skip-mypy]"
---

## Invocation

- **Slash command (interactive):** `/ocode-type-audit`
- **CLI (non-interactive):** `opencode run "Load the ocode-type-audit skill and execute it. Args: [optional --skip-phase1, --skip-mypy]"`

The skill is identical in both modes. CLI mode skips any user-prompt confirmations.

# Type Safety & Annotation Quality Audit

Run a comprehensive audit of type annotation quality across the production codebase. Two-pass analysis: mypy strict-mode + AST-based annotation scanner. Produces an Any-density heatmap by layer, mypy readiness score, and a prioritized narrowing plan. Measures progress against baseline — the main value is reducing new type debt and picking safe first layers, not fixing every mypy error at once.

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

Ensure the type audit scanner exists:

```bash
python -c "import os; assert os.path.exists('Tools/type_audit/type_audit.py'), 'type_audit.py not found'"
```

Ensure mypy is available (optional — can skip with `--skip-mypy`):

```bash
pip show mypy || pip install mypy
```

Ensure `Reviews/results/` directory exists:

```bash
mkdir -p Reviews/results
```

### Step 1: Run Phase 1 — Deterministic Analysis

**Run the orchestrator script yourself:**

```bash
python Tools/type_audit/type_audit.py
```

If mypy is not available, pass `--skip-mypy`:
```bash
python Tools/type_audit/type_audit.py --skip-mypy
```

Capture `REVIEW_DIR` from stdout.

If the user passed `--skip-phase1`, find the most recent `Reviews/results/*_type-audit/`.

The script creates `REVIEW_DIR/raw/` with these outputs:

1. `mypy_report.json` — mypy strict-mode results (total errors by file)
2. `any_heatmap.json` — `-> Any` and `: Any` density by layer
3. `any_returns.json` — every function returning `-> Any` (file:line:function)
4. `missing_returns.json` — public functions without return type annotation
5. `type_ignore_sites.json` — every `# type: ignore` with context
6. `cast_usage.json` — every `cast()` call site
7. `manifest.json` — 4-shard file assignments

### Step 2: Read Phase 1 Outputs + Reference Docs

Read these files into memory:

1. Read `REVIEW_DIR/raw/manifest.json` — extract ALL 4 shard file lists
2. Read `REVIEW_DIR/raw/any_heatmap.json`
3. Read `REVIEW_DIR/raw/any_returns.json`
4. Read `REVIEW_DIR/raw/missing_returns.json`
5. Read `REVIEW_DIR/raw/type_ignore_sites.json`
6. Read `REVIEW_DIR/raw/cast_usage.json`
7. Read `REVIEW_DIR/raw/mypy_report.json` (if mypy ran)
8. Read `docs/03_CONVENTIONS.md` (type annotation conventions)

### Step 3: Launch 5 Agents in Parallel

Launch **5 agents**:
- **4 in-shard deep review agents** (one per shard: 01, 02, 03, 04)
- **1 cross-layer type flow validator**

**Replace placeholders:**
- `{REVIEW_DIR}` → actual review directory
- `{shard_id}`, `{shard_label}`, `{shard_files}` → from manifest.json
- `{any_returns}` → instruct agent to "Read `{REVIEW_DIR}/raw/any_returns_{shard_id}.json`"
- `{any_heatmap}` → "Read `{REVIEW_DIR}/raw/any_heatmap.json`" (heatmap is global, no per-shard split)
- `{mypy_errors}` → "Read `{REVIEW_DIR}/raw/mypy_report_{shard_id}.json` (or `mypy_report.json` if mypy was skipped)"

#### Agents 1a-1d: In-Shard Type Reviewers

```
# Type Safety Audit — Shard {shard_id} Reviewer

You are assigned ONE shard: **{shard_label}** ({shard_id}).
You MUST exhaustively read EVERY file in this shard.

## Documentation Reference
Read docs/03_CONVENTIONS.md (type annotation conventions).

## Scope
Shard file list:
{shard_files}

## Deterministic Scan Results (filtered for your shard)
Functions returning -> Any:
{any_returns}

Any density heatmap:
{any_heatmap}

Mypy errors (filtered for your shard):
{mypy_errors}

## Methodology
For EACH file in your shard:

1. **Read the file** completely.
2. **Validate -> Any returns:**
   - For each `-> Any` return: can a more specific type be used?
   - Check if the function delegates to a dict/registry lookup (very common
     in UI — these are often unavoidable Any).
   - Flag functions where the return type could easily be narrowed
     (e.g., always returns a specific class or union).
3. **Check missing return annotations:**
   - Every public function (not starting with _) must have a return type
     per AGENTS.md convention.
   - Dunders are exempt.
4. **Validate # type: ignore:**
   - Each ignore must have a clear justification (pygame runtime attr,
     frozen dataclass override, replay store attr-defined, etc.)
   - Flag ignores without obvious justification.
5. **Check cast() usage:**
   - Is the cast genuinely needed or could better typing eliminate it?
   - Each cast is a type-safety bypass — is it worth the risk?
6. **TYPE_CHECKING block hygiene:**
   - Are imports in TYPE_CHECKING blocks only used for type annotations?
   - Flag runtime-usage of TYPE_CHECKING-only imports.
   - **Deferred narrowings:** Check for `# type: ignore[no-any-return]` or
     `-> Any` accompanied by a `# TODO:` comment. These are deliberately
     deferred — they should be tracked as a backlog list. Flag as MINOR;
     aggregate them in a separate '## Deferred Narrowings' section in the
     report.
7. **Protocol conformance in type system:**
   - Does the implementation match the Protocol's type signature?
   - Note any Protocol mismatches the type checker would catch.

## What NOT to Report
- Dunder methods without return types (exempt)
- UI property accessors returning Any from dict lookups (unavoidable)
- pygame interface callbacks (library conventions)
- Private methods (starting with _) without annotations — unless they cross
  layer boundaries or are widely called (10+ call sites); then note as MINOR
- Any from dynamic JSON/pygame/registry boundaries — these are unavoidable
  Any and should be flagged as INFO at most

## Narrowable vs Unavoidable Any
- **Unavoidable Any**: dynamic JSON deserialization, pygame event/mouse APIs,
  registry string-key dispatch, external library callbacks, TYPE_CHECKING
  protocol casts. These are architectural boundaries — note them as INFO.
- **Narrowable Any**: stable app-owned APIs where the return type is always
  one concrete class or a known union. These are MAJOR or CRITICAL.
  - Concrete example from this codebase: `Component.get(name) -> Any`
    patterns where every code path returns `Optional[Component]` — these
    are clear narrowing candidates. Confirm by reading every return
    statement in the function body before proposing the narrowed type.
- **Suggested concrete type**: only propose a specific type when you have
  verified ALL return paths in the function body. If unsure, mark as
  INCONCLUSIVE and request developer review.

## Severity Guide
- CRITICAL: Missing return type on a public API method used across layers
  (AGENTS.md requires return annotations on public functions);
  TYPE_CHECKING import used at runtime
- MAJOR: -> Any that can clearly be narrowed (always returns one type);
  cast() that could be eliminated with better typing; unjustified
  # type: ignore
- MINOR: -> Any in internal helper; cast() that is purely cosmetic;
  TYPE_CHECKING import unused or redundant; private method missing
  return type when crossing layer boundaries

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/type_review_{shard_id}.md

# Type Safety Review: {shard_label}
## Summary
- Shard: {shard_label}
- Files in Scope: [count]
- Files Actually Read: [count]
- Total Findings: [N]
- Critical: [N] | Major: [N] | Minor: [N]

## Narrowable Any Returns
#### {SEVERITY}: [Title]
**ID:** TYP-{shard_id}-[NUMBER]
**Location:** file.py:line
**Function:** function_name
**Current:** -> Any
**Suggested:** -> [concrete type or union]
**Justification:** [why narrowing is safe]
**LOC affected:** N

## Missing Return Types (Public API)
...

## Type Ignore Audit
...

## cast() Usage
...

## TYPE_CHECKING Hygiene
...

## File Coverage Verification
| File | Status |
|------|--------|
| [full file list with "Read ✓"] |
```

#### Agent 2: Cross-Layer Type Flow Validator

```
# Cross-Layer Type Flow Validator

Track types as they cross architectural layer boundaries. Identify where
well-typed returns in lower layers become untyped or Any in higher layers.

## Documentation Reference
Read docs/01_ARCHITECTURE.md, docs/03_CONVENTIONS.md.

## Scope
All files under game/.

## Methodology

1. **Track cross-layer return types:**
   Follow a type from its definition in Core/Simulation through Strategy
   and up to UI. Does it lose specificity? Where?

2. **Identify narrowing-candidates at layer boundaries:**
   Focus on functions called from higher layers that return `-> Any`
   but whose lower-layer source function has a specific return type.

3. **Protocol conformance gaps:**
   Protocols defined in Core are implemented across layers. Do the
   implementations match the Protocol signatures? Flag any mismatch
   that mypy would catch in strict mode.

4. **Propose a mypy strict-mode migration path:**
   Which layer could adopt strict mode first? Compute the recommended
   adoption order from `mypy_report.json` error counts per layer at runtime
   — propose the layer with the lowest error density first. The migration
   table below should be filled in from the actual data, not from a
   hardcoded sequence.
   Estimate error count reduction if each layer went strict.

## Output
You MUST use the Write tool to save your report to:
{REVIEW_DIR}/findings/type_flow_cross_layer.md

# Cross-Layer Type Flow Report
## Summary
- Cross-layer type flows traced: [N]
- Type-loss boundaries found: [N]
- Protocol conformance gaps: [N]

## Type-Loss Analysis
### Flow: simulation -> strategy -> ui
- **Origin type:** SimulationModule.method() -> SpecificType
- **Strategy receives:** StrategyService.method() -> Any
- **UI receives:** ui_renderer.method() -> Any
- **Loss at:** StrategyService line N
- **Fix:** Add return type annotation matching the origin

## Protocol Conformance Gaps
[Per-protocol analysis]

## Mypy Strict-Mode Migration Path
| Layer | Current Errors (est) | Strict Readiness | First to Adopt? |
|-------|---------------------|-----------------|-----------------|
| core | | | ✓ (recommended) |
| services | | | |
| engine | | | |
| ... | | | |

## Prioritized Narrowing Plan
[Ordered by cross-layer impact]
```

### Step 4: Verify Agent Outputs

Check that these files exist:
- `REVIEW_DIR/findings/type_review_01.md`
- `REVIEW_DIR/findings/type_review_02.md`
- `REVIEW_DIR/findings/type_review_03.md`
- `REVIEW_DIR/findings/type_review_04.md`
- `REVIEW_DIR/findings/type_flow_cross_layer.md`

### Step 5: Launch Verification Agent

```
# Type Audit — Verification Agent

Read ALL type review reports and the cross-layer flow report.
For EVERY finding marked CRITICAL:

1. Read the cited source code
2. Verify the finding is accurate and properly categorized
3. For -> Any returns: verify the suggested narrowing is actually safe
4. Rate as CONFIRMED, DISPUTED, or INCONCLUSIVE

Output to: {REVIEW_DIR}/findings/verification.md
```

### Step 6: Compile Final Report

Write `REVIEW_DIR/report.md`:

**1. Executive Summary**
- Date, review directory
- Type safety score by layer
- Mypy strict-mode readiness assessment

**2. Any Density Heatmap**
| Layer | -> Any Count | :Any Count | Missing Returns | Density Score |
|-------|-------------|-----------|-----------------|---------------|
| ui | | | | |
| strategy | | | | |
| ... | | | | |

**3. Narrowing Plan**
Per-layer recommendations with LOC estimates.

**4. Mypy Migration Path**
Step-by-step layer adoption plan.

**5. Prioritized Remediation Plan**

Sorted by `severity_weight × layer_weight × loc_affected` via `Tools/_audit_common/layer_weight.py`. All findings still appear in detail tables; weighting only affects this top-N ordering.

**6. Trend Comparison**

Use `Tools/_audit_common/run_tracker.py` with `audit_name="type"` to compare against prior runs (delta in Any-density, missing returns, mypy error counts, type-ignore counts).

**7. Appendices**

### Step 7: Log Skill Usage

```bash
python Tools/agent_coordination/log_skill_usage.py --agent ocode --skill ocode-type-audit
```

### Step 8: Present to User

Show the user:
1. Type safety scorecard by layer
2. Mypy strict-mode readiness (total errors, recommended first layer)
3. Top 3 most impactful narrowing opportunities
4. Cross-layer type-loss count
5. Path to the full report

Do NOT start making code changes. This is a read-only audit.
