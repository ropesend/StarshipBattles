# PROTOCOL 14: Create Project(s) from Error Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-error-audit` review, independently re-verify every actionable finding against current source, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **code relatedness** rather than severity — containing every item that survives the third pass.

OpenCode's error-audit already runs an internal verifier (`findings/verification.md`) over CRITICAL findings. That pass is rigorous but shares blind spots with the Phase-1 reviewers (same prompt, same code-reading angle). **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** add `# Intentional` comments, wrap exception boundaries, switch JSON calls, or otherwise apply fixes.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/verification.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** drop findings on the basis of severity. CRITICAL, MAJOR, and MINOR all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume a `*_type-audit/` or `*_docs-audit/` directory. This protocol is error-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to an error-audit directory, e.g. `Reviews/results/2026-05-04_090436_error-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_error-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent error-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_error-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_error-audit`. If the user passed an `*_type-audit/` or `*_docs-audit/` path, abort with: `Wrong audit type — claude-proj-from-error-audit only consumes *_error-audit/ directories. Use claude-proj-from-type-audit or claude-doc-audit-apply instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `error_review_*.md`.
   - `<audit_dir>/raw/manifest.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_090436_error-audit` → `2026-05-04`) — it goes into project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities are kept.** OpenCode's `findings/verification.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Include

- **`report.md` §4 Deterministic Scan Results** — every entry under 4.1–4.6 with a concrete file:line. The audit pre-classifies these (compliant / missing-comment / insufficient-justification / functional-inconsistency / false-positive); keep only items NOT marked false-positive.
- **`report.md` §5 Cross-Layer Error Propagation** — §5.1 boundary failures, §5.2 critical findings, §5.3 LLM context security findings.
- **`report.md` §6 Prioritized Remediation Plan** — every Critical/Major/Minor row.
- **`findings/error_review_NN.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR item not already captured in §4–6. Watch for shard reports listing items the executive summary skipped.
- **`findings/error_propagation_cross_layer.md`** — cross-layer boundary findings with `ERR-XLAYER-NN` style IDs.
- **`raw/broad_except_sites.json`, `raw/bare_except_sites.json`, `raw/json_bypass_sites.json`, `raw/raise_generic_sites.json`, `raw/print_debug_sites.json`** — concrete file:line lookup, used to hydrate findings missing precise locations.

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/verification.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- `raw/broad_except_sites.json` entries whose `has_comment` field is true AND the comment is a recognized `# Intentional broad catch:` justification. The audit's report already counts these as compliant.
- `raw/json_bypass_sites.json` entries that are in-memory `json.loads`/`json.dumps` with no file I/O — the audit notes these are low-risk because `json_utils` doesn't offer in-memory equivalents.
- `raw/print_debug_sites.json` entries that the audit explicitly marked as deliberate (e.g. top-level CLI crash diagnostics).

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `ERR-02-001`, `ERR-XLAYER-002` |
| `category` | `broad_except_no_comment`, `bare_except`, `json_bypass`, `generic_raise`, `print_debug`, `cross_layer_boundary`, `llm_context_security`, `resource_cleanup`, `error_chaining`, `logging_consistency` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` |
| `file` | `game/strategy/engine/turn_engine.py` |
| `line_range` | `516-524` or single line |
| `symbol` | `TurnEngine.process_turn` (or `null`) |
| `layer` | `core` / `services` / `simulation` / `strategy` / `ai` / `ui` / `assets` / `engine` / `research` / `unknown` (derived from path prefix) |
| `current_pattern` | `except Exception:` (or null where not applicable) |
| `recommended_pattern` | `except (FileNotFoundError, JSONDecodeError) as e:` or `with json_utils.read_json(...) as ...:` (or null) |
| `recommendation` | one short verb phrase from the audit |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `risk` | one-line description of what breaks if not fixed (especially for CRITICAL boundary findings) |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Exception hygiene (deterministic).** All `broad_except_no_comment`, `bare_except`, `generic_raise`, `print_debug` items.
- **Batch 2 — JSON / IO patterns.** All `json_bypass`, `resource_cleanup` items.
- **Batch 3 — Cross-layer boundaries.** All `cross_layer_boundary` items. **Highest impact — verifier must be especially careful.**
- **Batch 4 — Security + miscellaneous.** All `llm_context_security`, `error_chaining`, `logging_consistency` items.

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

#### `broad_except_no_comment`

1. Open the cited `file:line`. Confirm `except Exception:` (or `except BaseException:`) is present.
2. Look for a `# Intentional broad catch: <reason>` comment on the same line or immediately above. If present → `REJECTED` (already fixed).
3. Read the surrounding code. Decide whether the broad catch is genuinely justified:
   - At a top-level loop / event-loop / RPC handler boundary → `UNCERTAIN` (audit may want a comment, but the pattern is defensible).
   - At an arbitrary mid-function point with no boundary justification → `VERIFIED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `bare_except` (`except:` with no class)

1. Open the cited line. Confirm presence.
2. Existence is a hard regression — `VERIFIED` if present, `REJECTED` if not (the project recently cleaned all bare excepts via PROJ-308).
3. Verdict: `VERIFIED` / `REJECTED`.

#### `json_bypass`

1. Open the cited line. Confirm raw `json.load`/`json.dump`/`json.loads`/`json.dumps` is used.
2. Determine I/O pattern:
   - File I/O (`json.load(open(path))`, `json.dump(obj, open(path, 'w'))`) → `VERIFIED`. Recommend swap to `json_utils.read_json(path)` / `json_utils.write_json(path, obj)`.
   - In-memory (`json.loads(s)`, `json.dumps(obj)`) → `OUT_OF_SCOPE`. `json_utils` doesn't offer in-memory equivalents; the audit's own report agrees these are low-risk.
3. If the file is `game/services/json_utils.py` itself → `OUT_OF_SCOPE` (canonical implementation).
4. Verdict: `VERIFIED` / `OUT_OF_SCOPE`.

#### `generic_raise` (`raise Exception(...)`)

1. Open the cited line. Confirm `raise Exception(...)` (not a domain-specific subclass).
2. Existence is a hard regression — `VERIFIED` if present.
3. Domain-specific subclasses (`raise GameStateError(...)`) → `REJECTED` (already fine).
4. Verdict: `VERIFIED` / `REJECTED`.

#### `print_debug`

1. Open the cited line. Confirm `print()` or `traceback.print_exc()` / `traceback.format_exc()`.
2. Determine context:
   - Diagnostic logging in a top-level crash handler (`game/app.py:498` is the canonical example) → `OUT_OF_SCOPE` if marked deliberate by the audit.
   - Stdout debugging left in production code → `VERIFIED`.
   - CLI script user-facing output → `OUT_OF_SCOPE`.
3. Verdict: `VERIFIED` / `OUT_OF_SCOPE` / `UNCERTAIN`.

#### `cross_layer_boundary`

1. **Re-read the full boundary region**, not just the cited line. These findings are about missing `except` blocks, broken rollback guards, missing per-iteration isolation, and cascade-failure potential. They're high-impact; verifier must read enough surrounding code to understand the boundary.
2. Trace the failure path the audit describes:
   - "Turn-processing crash propagates to top-level" → trace from the cited boundary up to `app.py:494-503` (or equivalent crash handler). Confirm the absence of an intermediate `except`.
   - "Snapshot-capture failure silently disables rollback" → read snapshot capture and the rollback guard. Confirm `snapshot = None` path skips restoration.
   - "No per-combat error isolation" → read the loop, confirm a single iteration crash kills the whole loop.
3. If the gap is real → `VERIFIED`. If the gap has been closed by an interim commit → `REJECTED`. If the boundary is inherently unfixable without architectural change → `UNCERTAIN`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `llm_context_security`

1. Open the cited provider class (e.g. `game/services/llm/deepseek.py`, `game/ui/services/image/openai_provider.py`).
2. Find every `raise ... Error(..., context={...})` site. Read the context dict construction.
3. Confirm the audit's claim about whether secrets leak:
   - If audit says PASS and the dict contains only `model`, `attempt`, `status_code`, `request_duration_ms`, `endpoint` → `OUT_OF_SCOPE` (not actionable, recorded as compliance evidence).
   - If audit says FAIL and the dict contains `api_key`, `request_body`, raw `response.text`, or token data → `VERIFIED`.
4. Verdict: `VERIFIED` / `OUT_OF_SCOPE`.

#### `resource_cleanup`

1. Open the cited line. Confirm whether `with ...:`, `try/finally`, or `__exit__` is in scope.
2. If the resource is properly closed in all return paths → `REJECTED` (false positive).
3. If a leak is real → `VERIFIED`.
4. Verdict: `VERIFIED` / `REJECTED`.

#### `error_chaining` / `logging_consistency`

1. Read the cited region. Confirm the chain or log-level claim.
2. Missing `from e` on a re-raise → `VERIFIED`. Inconsistent log levels (one path logs `WARNING`, another logs `ERROR` for the same condition) → `VERIFIED`.
3. If the chain is intentional or the log levels reflect different severities → `REJECTED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (already fixed, false-positive scan, etc.). Provide file:line of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (in-memory JSON, deliberate diagnostic, compliance evidence). Logged but excluded from project.

Each verdict carries one short evidence line. **No verdict without evidence.**

### Where agents write

Each subagent writes to `.agent_reports/<audit-name>/verification_<batch>.md` and returns a summary in its tool reply. The main session aggregates the batch reports into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocol 13/14 from protocols 11/12: instead of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by `layer`.
2. Compute volume per layer: count of items + summed effort (LOW=1, MEDIUM=3, HIGH=8 weighted).
3. Decide breakdown by total VERIFIED count V:
   - V < 30:         ONE project, all layers in one bundle.
   - 30 <= V <= 100: 2–3 projects. Merge adjacent layers when each is small (<10 items).
                     Suggested merges by architectural proximity:
                       core + services + engine + research + assets   (foundation)
                       simulation + strategy + ai                     (domain)
                       ui                                             (presentation)
   - V > 100:        One project per layer that has >=10 items. Smaller layers
                     attach to the most architecturally adjacent larger one.
4. For each bundle, plan phase ordering:
   - Phase 1: CRITICAL items (boundary failures first — these can crash the game)
   - Phase 2: MAJOR items
   - Phase 3: MINOR items
   - Drop empty phases.
5. UNCERTAIN items are queued for Step 3.
```

**Note:** Cross-layer boundary findings (`cross_layer_boundary` category) are placed in the bundle owning the **upstream end** of the boundary — the layer that detects the error. This keeps the fix conversation local.

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                       | Layers              | Verified | Uncertain | Phases (severities) |
|---|---------------------------------------------|---------------------|----------|-----------|---------------------|
| 1 | Error handling cleanup — strategy/sim       | strategy,sim        |  V1      |  U1       | Critical, Major     |
| 2 | Error handling cleanup — UI + services      | ui,services         |  V2      |  U2       | Major, Minor        |

Totals: VERIFIED V / UNCERTAIN U / REJECTED R / OUT_OF_SCOPE O (excluded)
```

Then use `AskUserQuestion` with options:

- **Accept proposal as-is** (Recommended, default).
- **Merge two projects** (user names which two).
- **Split a project** (user names which one and how to split).
- **Custom — describe the bundling I want** (free-form via "Other").

Iterate. Each adjustment re-runs Step 1's volume + phase math against the new bundle definitions and re-shows the table. Stop when the user accepts.

### Step 3 — Resolve UNCERTAIN findings

Once the bundling is locked, walk the UNCERTAIN list grouped by their assigned bundle. For each item:

```
[bundle 1, item 2 of 3] ERR-02-007 — broad except in TurnEngine._dispatch()
  Layer: strategy | File: game/strategy/engine/turn_engine.py:412
  Verifier note: top-level event-loop catch-all — defensible but no comment present.
  Recommendation: include / exclude / defer to a future audit?
```

Ask via `AskUserQuestion`:

- **Include** — add to project plan (with note recording the user's decision).
- **Exclude** — drop, log in `findings/verification_report.md` as user-deferred.
- **Defer** — record in `findings/verification_report.md` for a later audit; not in any project this run.

Persist all decisions to `findings/bundling_decisions.md` (created in Phase E Step 7).

### Step 4 — Final confirmation

Print the locked bundle table again with adjusted counts (UNCERTAIN now resolved into Verified/Excluded/Deferred). Ask `AskUserQuestion`: "Proceed with project creation?" with options Accept / Adjust further. Accept moves to Phase E.

---

## Phase E: Build the Project(s)

For each finalized bundle:

1. **Create the project skeleton** with the canonical script:
   ```bash
   python Projects/scripts/create_project.py "Error handling cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Error handling cleanup — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, the layers covered, and any notable risk callouts (e.g. "includes 2 CRITICAL boundary failures with crash-and-corruption risk").
   - **Goals**: one bullet per phase ("Wrap N boundary failures with explicit handlers", "Add `# Intentional` comments to M defensible broad excepts", "Swap K JSON file-I/O sites to json_utils", etc.).
   - **Scope**: `In:` the categories and layers in this bundle. `Out:` other bundles' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 files touched in this bundle, sorted by item count.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Close the N verified boundary failures and rollback gaps in strategy/simulation identified by audit `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per file (group multiple symbols in the same file under one task to keep the checklist scannable). Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Tests:** <pytest path or "Run \`pytest tests/ --testmon\`">`.
     - One checkbox per finding, naming the symbol, line range, current pattern, and target pattern. Examples:
       - `[ ] Wrap \`StrategyGameStateManager.process_turn_action\` (lines 122-128) try/finally with explicit \`except EnginePhaseError\` and error dialog`
       - `[ ] Replace \`except Exception:\` (line 412) with \`except (FileNotFoundError, JSONDecodeError) as e:\` in \`asset_loader.py\``
       - `[ ] Add \`# Intentional broad catch: top-level event loop\` to line 412 of \`event_loop.py\``
       - `[ ] Replace \`json.load(open(path))\` (line 89) with \`json_utils.read_json(path)\` in \`save_game_service.py\``
     - For CRITICAL boundary findings: include a checkbox for adding a regression test that exercises the boundary failure path — these are the highest-impact items and need test coverage to prevent regression.
     - Final checkbox per phase: `[ ] Verify: pytest passes; no new \`except Exception\` without \`# Intentional\` comments introduced; \`grep -rn "except:" game/\` returns nothing in modified files`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every file referenced in any `phase_N_checklist.md` must appear here, and every file in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`), `Notes` (one-line action summary).

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Layer coverage and severity breakdown.
   - For CRITICAL boundary findings: a one-paragraph "Risk Notes" subsection summarizing the failure paths.
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "code locality across strategy/simulation"> per user direction | Bundling driven by code relatedness rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, file, symbol, current pattern, recommended pattern, severity, risk).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence file:line, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## Out of Scope` — table per item: id, why the verifier excluded it (in-memory JSON, deliberate diagnostic, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the error-audit at:

   `Reviews/results/<audit-dir-name>/`
     - [report.md](../../../../Reviews/results/<audit-dir-name>/report.md)
     - [findings/](../../../../Reviews/results/<audit-dir-name>/findings/)

   See [verification_report.md](verification_report.md) for the independent re-verification that filtered the audit's claims before they entered this project's plan, and [bundling_decisions.md](bundling_decisions.md) for the interactive bundling that decided which findings ended up in this project versus its siblings.
   ```

9. **Write `findings/bundling_decisions.md`.** Record of Phase D:
   - Default proposal table.
   - User adjustments (each merge/split with rationale).
   - Final bundle definitions.
   - Per-UNCERTAIN-item user decisions from Step 3.

   This file is identical across all sibling projects created in the same run (so the user can read it once for the full picture). The skill writes it once per project, not just once per run.

---

## Phase F: Self-Check Before Finishing

Before printing the summary, verify:

- [ ] Every phase listed in each `plan.md`'s Quick Status table has a corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in", `[Task Name]`, or `[Filled during implementation]` left over from the template.
- [ ] Every file path in any checklist appears in that project's `manifest.md`, and vice versa.
- [ ] The verified-item count in `decisions.md` / `design.md` matches the total checkbox count across all `phase_N_checklist.md` files (within a small margin for grouping).
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist.
- [ ] Every UNCERTAIN item is either in a checklist (user said Include) or recorded in `verification_report.md` as Excluded/Deferred.
- [ ] Every CRITICAL boundary finding has at least one regression-test checkbox in its phase.
- [ ] You have not modified anything outside `Projects/active_projects/PROJ-*/` (except `Projects/projects_index.md`, which `create_project.py` updates).
- [ ] The source audit directory under `Reviews/results/` is unchanged.

If any check fails, fix it before reporting completion.

---

## Phase G: Hand-off

Print to the user:

```
Created N project(s) from <audit-dir-name>:

  PROJ-NNN — <title>
    Path: Projects/active_projects/PROJ-NNN/
    Verified: V / Uncertain (included): U_in / Rejected: R / Out-of-scope: O
    Phases: <list, e.g. "1 Critical, 2 Major, 3 Minor">
    CRITICAL boundary findings: <count, with crash-risk callout if > 0>

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

If any project contains CRITICAL boundary findings, surface them on a separate line: `⚠ <count> CRITICAL boundary failures across <N> projects — recommend prioritizing these before MAJOR/MINOR work.`

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
