# PROTOCOL 13: Create Project(s) from Type Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-type-audit` review, independently re-verify every actionable finding against current source, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **code relatedness** rather than severity — containing every item that survives the third pass plus the audit's mypy strict-mode migration plan.

OpenCode's type-audit already runs an internal verifier (`findings/verification.md`) over CRITICAL findings. That pass is rigorous but shares blind spots with the Phase-1 reviewers. **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** run mypy fixes, narrow types, add annotations, or silence warnings.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/verification.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** drop findings on the basis of severity. CRITICAL, MAJOR, MINOR, and STRATEGIC (strict-mode migration) all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume an `*_error-audit/` or `*_docs-audit/` directory. This protocol is type-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a type-audit directory, e.g. `Reviews/results/2026-05-04_090402_type-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_type-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent type-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_type-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_type-audit`. If the user passed an `*_error-audit/` or `*_docs-audit/` path, abort with: `Wrong audit type — claude-proj-from-type-audit only consumes *_type-audit/ directories. Use claude-proj-from-error-audit or claude-doc-audit-apply instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `type_review_*.md`.
   - `<audit_dir>/raw/manifest.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_090402_type-audit` → `2026-05-04`) — it goes into project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities are kept.** OpenCode's `findings/verification.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Include

- **`report.md` §3 Key Findings** — every CRITICAL, MAJOR, MINOR row with `TYP-NN-NNN` IDs.
- **`report.md` §4 Mypy Strict-Mode Migration Path** — one candidate per layer row. Generate the ID as `STRICT-<layer>` (e.g. `STRICT-core`, `STRICT-ui`). Severity = `STRATEGIC`.
- **`findings/type_review_NN.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR item not already captured in §3. Watch for shard reports listing items the executive summary skipped.
- **`findings/type_flow_cross_layer.md`** — cross-layer narrowing candidates.
- **`raw/any_returns.json`, `raw/missing_returns.json`, `raw/type_ignore_sites.json`, `raw/cast_usage.json`** — concrete file:line lookup, used to hydrate findings missing precise locations.

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/verification.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- Anything from `raw/*.json` that the audit's deterministic scanner classified as a known-good pattern (e.g. justified `# type: ignore` sites with comments).

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `TYP-02-001`, `STRICT-core` |
| `category` | `narrowable_any`, `missing_return`, `type_ignore`, `cast`, `wrong_annotation`, `protocol_any_leakage`, `strict_migration` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` / `STRATEGIC` |
| `file` | `game/core/registry.py` (or `null` for layer-scoped strict-migration items) |
| `line_range` | `248,332` or `412-418` (or `null` for whole-layer items) |
| `symbol` | `RegistryManager.get_validator` (or `null`) |
| `layer` | `core` / `services` / `simulation` / `strategy` / `ai` / `ui` / `assets` / `engine` / `research` / `unknown` (derived from path prefix; for `STRICT-*` use the migration row's layer) |
| `current_type` | `-> Any` (or null where not applicable) |
| `suggested_type` | `-> Optional[ShipDesignValidator]` (or null) |
| `recommendation` | one short verb phrase from the audit |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `mypy_error_count` | for `strict_migration` items, the audit's reported error count for that layer |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Narrowable Any returns.** All `narrowable_any` and `protocol_any_leakage` items. Volume can be high; if >40 items, split by layer.
- **Batch 2 — Missing returns + wrong annotations.** All `missing_return` and `wrong_annotation` items.
- **Batch 3 — Type ignores + casts.** All `type_ignore` and `cast` items. Usually small.
- **Batch 4 — Strict-mode migration.** All `strict_migration` items, one per layer.

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

#### `narrowable_any` / `protocol_any_leakage`

1. Open the cited `file:line`. Read the function and trace every return path.
2. Confirm the audit's `current_type` is what the source actually shows. If the function already has a non-`Any` annotation, `REJECTED` (already fixed).
3. Confirm the `suggested_type` is reachable for every return path:
   - Concrete class returns → narrow to that class.
   - Multiple types → consider `T1 | T2`.
   - Genuinely dynamic dispatch (registry, JSON, getattr) → `UNCERTAIN` with a note for the user.
4. For protocol methods: confirm whether all implementers agree on the concrete type. If implementers diverge, `UNCERTAIN`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `missing_return`

1. Open the cited `file:line`. Confirm the function has no return annotation.
2. Confirm it's public (does not start with `_`). If private, downgrade to `UNCERTAIN` — convention exempts internal helpers.
3. Read the function body and infer the return type. Compare to the audit's suggestion. If they match → `VERIFIED`. If body returns `None` everywhere and audit suggested otherwise → `REJECTED` (suggest `-> None` instead, but this still goes in the project as a `VERIFIED` `-> None` annotation).
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `type_ignore`

1. Open the cited line. Confirm the `# type: ignore` is present.
2. Read the surrounding code and any inline justification comment.
3. If the ignore is genuinely necessary (mypy bug, missing stub, dynamic attribute, etc.) → `OUT_OF_SCOPE` (already a non-issue).
4. If the ignore can be removed by adding a proper annotation, narrow type, or stub → `VERIFIED`.
5. Verdict: `VERIFIED` / `REJECTED` / `OUT_OF_SCOPE`.

#### `cast`

1. Open the cited line. Confirm the `cast()` call exists.
2. Determine if a structural narrowing (`isinstance`, `assert`, type-guard function) would replace it. If yes → `VERIFIED`. If the cast is unavoidable (cross-module type erasure) → `OUT_OF_SCOPE`.

#### `wrong_annotation`

1. Open the cited line. Read the function. Compare its actual return type to the declared annotation.
2. If the mismatch holds → `VERIFIED`. If the annotation is correct or the function was rewritten → `REJECTED`.

#### `strict_migration` (one per layer)

1. Run `python -m mypy --strict <layer-path>` (read-only, scoped to that layer's path) to get the current strict-mode error count. **Do not modify any code.**
2. Compare to the audit's reported `mypy_error_count`:
   - Within ±50%: `VERIFIED`. The migration plan is still accurate.
   - More than +50% above: `VERIFIED` but flag note ("layer regressed since audit; effort estimate is low").
   - More than -50% below: `UNCERTAIN`. Layer may have already had work done. Surface for user decision in Phase D.
   - Zero errors now: `OUT_OF_SCOPE`. Migration is complete.
3. Verdict: `VERIFIED` / `OUT_OF_SCOPE` / `UNCERTAIN`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (already fixed, suggested type wrong, etc.). Provide file:line of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (justified ignore, completed migration, etc.). Logged but excluded from project.

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
   - Phase 1: CRITICAL items
   - Phase 2: MAJOR items
   - Phase 3: MINOR items
   - Phase 4+: STRATEGIC items (one phase per layer's strict-mode migration if multiple
               layers in the bundle; one phase otherwise)
   - Drop empty phases.
5. UNCERTAIN items are queued for Step 3.
```

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                   | Layers              | Verified | Uncertain | Phases (severities)                |
|---|-----------------------------------------|---------------------|----------|-----------|------------------------------------|
| 1 | Type cleanup — foundation               | core,services,...   |  V1      |  U1       | Critical, Major, Strict-migration  |
| 2 | Type cleanup — domain                   | strategy,sim,ai     |  V2      |  U2       | Major, Minor, Strict-migration     |
| 3 | Type cleanup — UI                       | ui                  |  V3      |  U3       | Major, Minor, Strict-migration     |

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
[bundle 1, item 3 of 5] TYP-02-005 — RegistryManager.get_handler() -> Any
  Layer: core | File: game/core/registry.py:412
  Verifier note: dispatch via JSON config; could legitimately be Any.
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
   python Projects/scripts/create_project.py "Type cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Type cleanup — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, and the layers covered.
   - **Goals**: one bullet per phase ("Narrow N protocol Any returns in core", "Add return annotations to M public functions", "Migrate core layer to mypy --strict", etc.).
   - **Scope**: `In:` the categories and layers in this bundle. `Out:` other bundles' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 files touched in this bundle, sorted by item count.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Narrow the N verified `-> Any` returns in core protocols identified by audit `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per file (group multiple symbols in the same file under one task to keep the checklist scannable). Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Tests:** <pytest path or "Run \`pytest tests/ --testmon\` and \`mypy <file>\`">`.
     - One checkbox per symbol/line, naming the symbol, line range, current type, and target type. Examples:
       - `[ ] Narrow \`RegistryManager.get_validator\` (line 248) from \`-> Any\` to \`-> Optional[ShipDesignValidator]\``
       - `[ ] Add \`-> None\` to \`_button_handlers\` (line 142) in \`atmosphere_target_editor.py\``
       - `[ ] Replace \`cast(int, x)\` (line 89) with isinstance check`
     - For `strict_migration` phases: one checkbox per major error category in that layer (e.g. `[ ] Resolve 12 implicit-optional errors in math.py`), plus a final `[ ] Add \`--strict\` to layer's mypy config`.
     - Final checkbox per phase: `[ ] Verify: pytest passes; mypy <layer-or-files> shows no new errors`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every file referenced in any `phase_N_checklist.md` must appear here, and every file in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`), `Notes` (one-line action summary).

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Layer coverage and severity breakdown.
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "code locality across core/services/engine"> per user direction | Bundling driven by code relatedness rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, file, symbol, current type, suggested type).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence file:line, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## Out of Scope` — table per item: id, why the verifier excluded it (justified ignore, completed migration, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the type-audit at:

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
    Phases: <list, e.g. "1 Critical, 2 Major, 3 Minor, 4 Strict-migration">

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
