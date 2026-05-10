# PROTOCOL 16: Create Project(s) from Legacy Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-legacy-audit` review, independently re-verify every actionable finding against current source, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **removal cluster** (one project per system being eradicated) rather than severity — containing every item that survives the third pass.

OpenCode's legacy-audit already runs an internal verifier (`findings/verification.md`) over CRITICAL findings. That pass is rigorous but shares blind spots with the Phase-1 reviewers (same prompt, same code-reading angle). **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

**Special framing — delete-or-consolidate, not fix-in-place.** Legacy-audit findings are about *removing* code, not extending or wrapping it. Every project this protocol creates is a removal/consolidation project. Phases are titled `Delete <symbol>` or `Migrate callers of <symbol> then delete` or `Consolidate <system A> with <system B>`. CLAUDE.md Rule 3 ("Root Cause Fixes") is the philosophical backbone — when a system is replaced, remove the old path and update all callers; do not add compatibility shims.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** delete symbols, inline wrappers at call sites, migrate callers, or consolidate systems. Those are implementation work.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/verification.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** treat INFO-severity findings as actionable without explicit user opt-in during Phase D. INFO is "suspected legacy but unclear" per the source skill's severity guide.
- **Do NOT** drop non-INFO findings on the basis of severity. CRITICAL, MAJOR, and MINOR all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** reframe a removal finding as a fix-in-place. If a finding cannot be expressed as a deletion or consolidation, it is probably a wrong-skill finding and belongs to error-audit / state-audit / type-audit. Surface it to the user and exclude it.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume a `*_error-audit/`, `*_type-audit/`, `*_state-audit/`, or `*_docs-audit/` directory. This protocol is legacy-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a legacy-audit directory, e.g. `Reviews/results/2026-05-04_120000_legacy-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_legacy-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent legacy-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_legacy-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_legacy-audit`. If the user passed an `*_error-audit/`, `*_type-audit/`, `*_state-audit/`, or `*_docs-audit/` path, abort with: `Wrong audit type — claude-proj-from-legacy-audit only consumes *_legacy-audit/ directories. Use the matching claude-proj-from-* skill instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `legacy_review_*.md`.
   - `<audit_dir>/raw/manifest.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_120000_legacy-audit` → `2026-05-04`) — it goes into project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities except INFO are kept by default.** INFO items go into a separate "needs user opt-in" bucket and are surfaced during Phase D Step 3. OpenCode's `findings/verification.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Include

- **`report.md` Legacy Inventory by Category** — every entry under each of the 10 detector categories (module_alias, init_reexport_shim, deprecation_marker, wrapper_delegate, name_pair_drift, save_migration_code, superseded_pattern_use, type_checking_only_reexport, partial_protocol_impl, duplicate_system) with a concrete file:line.
- **`report.md` Removal Scorecard** — per-category counts and severity rollups; cross-check against the per-finding detail to catch any item the executive summary skipped.
- **`report.md` Prioritized Removal Plan** — every Critical/Major/Minor row.
- **`findings/legacy_review_NN.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR/INFO item not already captured in the report. Watch for shard reports listing items the executive summary skipped.
- **`findings/legacy_duplicate_systems_cross.md`** — duplicate-system findings with cross-shard context (one finding may span multiple files in different shards).
- **`raw/module_aliases.json`, `raw/init_reexports.json`, `raw/deprecation_markers.json`, `raw/wrapper_delegates.json`, `raw/name_pair_drift.json`, `raw/save_migration_code.json`, `raw/superseded_pattern_uses.json`, `raw/type_checking_only_reexports.json`, `raw/optional_protocol_methods.json`** — concrete file:line lookup, used to hydrate findings missing precise locations and (critically) to compute call-site counts for wrapper-delegate and module-alias items.

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/verification.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- `raw/deprecation_markers.json` entries whose target symbol does not exist in the codebase (orphan markers in deleted modules — already gone).
- `raw/wrapper_delegates.json` entries pointing to canonical adapter patterns the audit explicitly excludes (e.g. boundary adapters between layers).

### Hold for User Opt-In (INFO bucket)

- Every finding marked `INFO` in `report.md` or any `findings/legacy_review_*.md`. Do not auto-include. Surface in Phase D Step 3 with the verifier's note about why classification was uncertain.

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `LEG-01-001`, `LEG-XSYS-002` |
| `category` | `module_alias`, `init_reexport_shim`, `deprecation_marker`, `wrapper_delegate`, `name_pair_drift`, `save_migration_code`, `superseded_pattern_use`, `type_checking_only_reexport`, `partial_protocol_impl`, `duplicate_system` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` / `INFO` |
| `file` | `game/strategy/legacy/foo_manager_alias.py` |
| `line_range` | `1-12` for whole-file deletions, or single line / range for in-file symbols |
| `file_range` | for whole-file deletion candidates: `1-EOF` |
| `symbol` | `LegacyFooManager` (or the alias name, or `null` for whole-file shims) |
| `replaces` | the new symbol that the legacy one delegates to or is superseded by, where known: `game.strategy.foo.FooManager` (or `null` if the legacy is duplicate-system / unknown) |
| `call_site_count` | integer (required for wrapper_delegate and module_alias). `0` flags single-PR deletion |
| `removal_cluster` | the system being eradicated, e.g. `LegacyFooManager`, `save_migration_v3_to_v4`, `duplicate_AmmoTracker_AmmunitionLedger` (assigned in Phase D, blank during Phase B) |
| `recommendation` | one of: `delete`, `inline_at_callers_then_delete`, `consolidate_with`, `migrate_callers_then_delete`, `add_removal_plan_comment` |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `risk` | one-line description of what breaks if not removed (e.g. "drift between alias and canonical implementation as canonical evolves") |
| `policy_violation` | `CLAUDE.md Rule 3 (old saves disposable)` for save_migration_code, else `null` |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — File-deletion candidates.** All `module_alias`, `init_reexport_shim`, `type_checking_only_reexport` items. These are usually whole-file or whole-block deletions; the verification focus is the call-site count.
- **Batch 2 — Wrapper functions.** All `wrapper_delegate`, `name_pair_drift`, `partial_protocol_impl` items. Verification focus: confirm the wrapper genuinely delegates to a canonical, and confirm callers can be cleanly migrated.
- **Batch 3 — Flagged-for-removal.** All `deprecation_marker`, `superseded_pattern_use` items. Verification focus: the marker target / superseded pattern still exists and is used.
- **Batch 4 — Banned-by-policy + duplicates.** All `save_migration_code` and `duplicate_system` items. Verification focus: for save_migration_code, confirm the migration handles a format the codebase no longer supports; for duplicate_system, confirm both implementations exist and that one is genuinely the canonical.

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch, the verifier MUST:

1. Open the cited `file:line` and read enough surrounding code to understand the symbol's role.
2. Open the `replaces` target (where given) and confirm it exists and is the canonical replacement.
3. **Verify the call-site count by grepping** for usages across `game/`, `tests/`, `combat_lab/`, `Tools/`. The audit may have undercounted (missed an import alias) or overcounted (false-positive substring match). The third-pass verifier's job is to be more thorough than the audit.

#### `module_alias` / `init_reexport_shim` / `type_checking_only_reexport`

1. Open the alias file. Confirm it is a re-export shim with no production logic.
2. Grep for the alias module path across the repo. Compare against the audit's `call_site_count`.
3. Decide:
   - Genuine alias with `0` call sites → `VERIFIED` with recommendation `delete` (single-PR deletion, no migration).
   - Genuine alias with `>0` call sites → `VERIFIED` with recommendation `migrate_callers_then_delete`.
   - Alias has been silently extended with new logic since the audit ran → `UNCERTAIN` (no longer a pure shim).
   - Alias does not exist (already deleted) → `REJECTED`.
4. Verdict: `VERIFIED` / `UNCERTAIN` / `REJECTED`.

#### `wrapper_delegate` / `name_pair_drift`

1. Open the wrapper. Confirm it is a thin pass-through to a canonical symbol (allowed: argument forwarding, deprecation logging; not allowed: any business logic, logging-only side-effects with state, parameter transformation that changes behavior).
2. Open the canonical. Confirm it exists and accepts the wrapper's signature (or that callers can be straightforwardly migrated to the canonical's signature).
3. Grep for callers; reconcile with audit's `call_site_count`.
4. Decide:
   - Pure pass-through with replaceable signature → `VERIFIED` with `inline_at_callers_then_delete` (low call count) or `migrate_callers_then_delete` (high call count).
   - Wrapper transforms parameters / adds non-trivial logic → `REJECTED` (it's not a legacy wrapper, it's a real adapter).
   - Canonical does not exist → `REJECTED` (legacy is the only path).
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `deprecation_marker`

1. Open the marker (`@deprecated`, `# DEPRECATED:`, `warnings.warn(DeprecationWarning, ...)`).
2. Confirm the marked symbol still exists and is still imported anywhere.
3. Confirm a replacement exists (named by the marker comment, or by the audit's `replaces` field).
4. Decide:
   - Marker present, symbol used, replacement exists → `VERIFIED` with `migrate_callers_then_delete`.
   - Marker present but symbol has zero call sites → `VERIFIED` with `delete`.
   - Marker is orphan (symbol or replacement gone) → `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED`.

#### `superseded_pattern_use`

1. Read the cited line. Confirm it uses the superseded pattern (e.g. legacy `set_default_*` bridge instead of `ctx.xxx`, or pre-PROJ-258 singleton access).
2. Confirm the modern pattern is documented and applicable in this context.
3. Decide:
   - Superseded pattern present, modern equivalent applies → `VERIFIED` with `migrate_callers_then_delete` for the bridge or `inline_at_callers_then_delete`.
   - Use is intentional (bridge file documented as transitional) → `UNCERTAIN`.
   - Already migrated → `REJECTED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `save_migration_code`

1. Read the cited migration logic. Confirm it migrates from a save-format version that the codebase no longer supports (CLAUDE.md Rule 3: old saves are disposable).
2. Trace the call graph: is the migration code reached during normal save loading? Is it gated on a version field?
3. Decide:
   - Genuine save migration for a defunct format → `VERIFIED` with `delete` and `policy_violation: CLAUDE.md Rule 3`.
   - Logic is general save-loading, not migration → `REJECTED` (audit misclassified).
   - Migration handles a format the user might still have on disk and the user has not confirmed it's safe to drop → `UNCERTAIN` (surface for user decision).
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `partial_protocol_impl`

1. Open the protocol/interface and the partial implementation.
2. Confirm the implementation is genuinely a stub (raises `NotImplementedError`, returns `None` for required methods, etc.) and that no caller relies on the missing method.
3. Decide:
   - Stub with no callers → `VERIFIED` with `delete`.
   - Stub but callers depend on it (would crash if removed) → `UNCERTAIN`.
   - Implementation is complete; audit misread → `REJECTED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `duplicate_system`

1. Open both implementations cited. Read enough of each to understand their public surface.
2. Confirm they solve the same problem with different APIs (e.g. `AmmoTracker` and `AmmunitionLedger`).
3. Determine which is the canonical (newer, better-tested, more callers, or explicitly named by the audit).
4. Decide:
   - Both exist, same problem, one is canonical → `VERIFIED` with `consolidate_with` and the canonical named.
   - One is a thin re-export of the other (it's actually a `module_alias`, miscategorized) → `VERIFIED` but recategorize as `module_alias`.
   - The systems are not actually duplicates (different scopes / domains) → `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (already removed, false-positive scan, audit misread, etc.). Provide file:line of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (canonical adapter pattern, intentional bridge file, etc.). Logged but excluded from project.

Each verdict carries one short evidence line. **No verdict without evidence.**

### Where agents write

Each subagent writes to `.agent_reports/<audit-name>/verification_<batch>.md` and returns a summary in its tool reply. The main session aggregates the batch reports into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocol 14/16 from protocols 11/12: instead of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by `removal_cluster`.
   - A removal cluster is the system being eradicated. Build clusters by:
     a) duplicate_system findings name two systems explicitly — cluster on the one being removed.
     b) wrapper_delegate / module_alias / init_reexport_shim findings cluster around the canonical they delegate to (the canonical is the survivor; the wrappers are the cluster contents).
     c) deprecation_marker findings cluster on the marked symbol.
     d) save_migration_code findings each form their own cluster (one per migration version-pair, e.g. v3→v4).
     e) superseded_pattern_use findings cluster by the pattern being phased out (e.g. all `set_default_*` bridges).
     f) partial_protocol_impl findings cluster on the protocol.
2. One project per cluster by default. Drop clusters with zero VERIFIED items.
3. For each cluster, plan phase ordering by removal-risk:
   - Phase 1 — Critical: save_migration_code (banned by CLAUDE.md) + module_alias / init_reexport_shim with call_site_count == 0 (single-PR deletion, no migration needed).
   - Phase 2 — Major: wrapper_delegate / module_alias with call_site_count > 0; duplicate_system consolidations; partial_protocol_impl with callers.
   - Phase 3 — Minor: orphan deprecation_marker; superseded_pattern_use; type_checking_only_reexport with low risk; stale set_default_* bridges.
   - Drop empty phases.
4. UNCERTAIN and INFO items are queued for Steps 3 and 4.
```

**Note:** A single removal cluster can contain items of multiple severities. Severity drives **which phase** the item lands in inside the project, not which project it lands in.

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                              | Cluster                  | Verified | Uncertain | INFO | Phases             |
|---|----------------------------------------------------|--------------------------|----------|-----------|------|--------------------|
| 1 | Legacy removal — LegacyFooManager                  | LegacyFooManager         |  V1      |  U1       |  I1  | Critical, Major    |
| 2 | Legacy removal — save migration v3→v4              | save_migration_v3_to_v4  |  V2      |  U2       |  I2  | Critical           |
| 3 | Legacy removal — set_default_* bridge               | superseded_set_default   |  V3      |  U3       |  I3  | Minor              |

Totals: VERIFIED V / UNCERTAIN U / INFO I / REJECTED R / OUT_OF_SCOPE O (excluded)
```

Then use `AskUserQuestion` with options:

- **Accept proposal as-is** (Recommended, default).
- **Merge two projects** (user names which two — useful when two clusters touch the same files).
- **Split a project** (user names which one and how to split — useful when a cluster grew unwieldy).
- **Custom — describe the bundling I want** (free-form via "Other").

Iterate. Each adjustment re-runs Step 1's clustering math against the new bundle definitions and re-shows the table. Stop when the user accepts.

### Step 3 — Resolve UNCERTAIN findings

Once the bundling is locked, walk the UNCERTAIN list grouped by their assigned bundle. For each item:

```
[bundle 1, item 2 of 3] LEG-02-007 — wrapper LegacyFooManager.compute_score()
  Cluster: LegacyFooManager | File: game/strategy/legacy/foo_manager.py:412
  Verifier note: wrapper transforms one parameter before delegating; not a pure pass-through.
  Recommendation: include / exclude / defer to a future audit?
```

Ask via `AskUserQuestion`:

- **Include** — add to project plan (with note recording the user's decision).
- **Exclude** — drop, log in `findings/verification_report.md` as user-deferred.
- **Defer** — record in `findings/verification_report.md` for a later audit; not in any project this run.

### Step 4 — Resolve INFO findings (separate pass)

INFO items did not enter the candidate set automatically. Walk them now, grouped by their candidate cluster (best-guess assignment). For each:

```
[INFO item 1 of 5] LEG-XSYS-013 — possible duplicate ResourceTracker / ResourceLedger
  Audit note: classification uncertain — both have small surface, may be intentional separation.
  Verifier note: confirmed both exist; one used in simulation, one in strategy. Could be intentional.
  Include in a project / Exclude?
```

Ask via `AskUserQuestion` (Include / Exclude only — INFO does not get a "Defer" since the audit already deferred it once by classifying it INFO).

Persist all decisions (UNCERTAIN and INFO) to `findings/bundling_decisions.md` (created in Phase E Step 7).

### Step 5 — Final confirmation

Print the locked bundle table again with adjusted counts (UNCERTAIN now resolved into Verified/Excluded/Deferred; INFO into Verified/Excluded). Ask `AskUserQuestion`: "Proceed with project creation?" with options Accept / Adjust further. Accept moves to Phase E.

---

## Phase E: Build the Project(s)

For each finalized bundle:

1. **Create the project skeleton** with the canonical script:
   ```bash
   python Projects/scripts/create_project.py "Legacy removal — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Legacy removal — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, the removal cluster, and any notable risk callouts (e.g. "includes 2 save-migration-code findings banned by CLAUDE.md Rule 3" or "1 module alias with 0 call sites — single-PR deletion").
   - **Goals**: one bullet per phase ("Delete N zero-call-site shims and the v3→v4 save migration", "Migrate M callers of `LegacyFooManager.compute_score` to canonical, then delete wrapper", "Remove K orphan deprecation markers", etc.).
   - **Scope**: `In:` the cluster and categories in this bundle. `Out:` other clusters' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 files touched in this bundle, sorted by item count. For whole-file deletions, mark the row with `[DELETE]`.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** removal-cluster-specific (e.g. "Delete the v3→v4 save migration code identified by audit `<audit-dir-name>`. Saves in v3 format are not supported per CLAUDE.md Rule 3.").
   - **Tasks section:** one `### Task N.M` per file (group multiple symbols in the same file under one task). Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Tests:** <pytest path or "Run \`pytest tests/ --testmon\`">`.
     - One checkbox per finding. Examples:
       - `[ ] Delete `game/strategy/legacy/foo_manager_alias.py` (whole file, 0 call sites)`
       - `[ ] Inline `LegacyFooManager.compute_score` (lines 88-95) at 3 call sites in `strategy_window_manager.py`, `battle_setup.py`, `combat_lab/templates.py`, then delete wrapper`
       - `[ ] Migrate 7 callers of `set_default_widget_factory` to `ctx.widget_factory`, then delete the bridge function (lines 145-152)`
       - `[ ] Remove orphan @deprecated marker on `compute_old_score` (line 220) — symbol unused since 2026-03-01`
       - `[ ] Delete save migration v3→v4 (lines 412-510) [banned by CLAUDE.md Rule 3]`
       - `[ ] Consolidate `AmmunitionLedger` into canonical `AmmoTracker` — migrate 4 call sites in `simulation/ammo/`, then delete `AmmunitionLedger`
     - For save_migration_code findings: include the `[banned by CLAUDE.md Rule 3]` callout in the checkbox text. This is non-negotiable and signals to the implementer that the finding cannot be downgraded to a fix-in-place.
     - For zero-call-site deletions: include `(0 call sites — single-PR deletion)` in the checkbox text. Phase 1 should ideally collect all zero-call-site deletions in one task per directory so they can ship as a single PR.
     - Final checkbox per phase: `[ ] Verify: pytest passes; no remaining imports of deleted symbols (`grep -rn "<deleted_symbol>" .`); no remaining call sites of migrated wrappers`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every file referenced in any `phase_N_checklist.md` must appear here, and every file in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`), `Action` (`Delete` / `Edit` / `Migrate-callers`), `Notes` (one-line action summary).

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <I> INFO (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Cluster identity and severity breakdown.
   - For save_migration_code findings: a one-paragraph "Policy Notes" subsection citing CLAUDE.md Rule 3 and noting that old saves are disposable.
   - For zero-call-site deletions: a one-paragraph "Quick Wins" subsection listing whole-file deletions that can ship in a single PR.
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by removal cluster `<cluster>` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <I> INFO / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, file, symbol, replaces, call_site_count, recommendation, severity, policy_violation).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence file:line, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later via the refinement-feedback channel.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## INFO (resolved)` — table per item: id, the verifier's classification note, and the user's Phase D Step 4 decision (Include / Exclude). Excluded INFO items signal over-eager INFO classification by the source skill — they are fed back via `Projects/protocols/15_refinement_feedback.md`.
   - `## Out of Scope` — table per item: id, why the verifier excluded it (canonical adapter, intentional bridge, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the legacy-audit at:

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
   - Per-INFO-item user decisions from Step 4.

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
- [ ] Every INFO item is either in a checklist (user said Include) or recorded in `verification_report.md` as Excluded.
- [ ] Every `save_migration_code` checkbox carries the `[banned by CLAUDE.md Rule 3]` callout.
- [ ] Every zero-call-site deletion carries the `(0 call sites — single-PR deletion)` callout.
- [ ] No checkbox reframes a removal as a fix-in-place. Every checkbox is `Delete`, `Inline`, `Migrate callers then delete`, `Consolidate`, or `Remove orphan marker`.
- [ ] You have not modified anything outside `Projects/active_projects/PROJ-*/` (except `Projects/projects_index.md`, which `create_project.py` updates).
- [ ] The source audit directory under `Reviews/results/` is unchanged.

If any check fails, fix it before reporting completion.

---

## Phase G: Refinement Feedback

Per `Projects/protocols/15_refinement_feedback.md`, write a refinement proposal back to the originating OpenCode skill. Inputs:

- `audit_dir`: the audit directory consumed.
- `source_skill`: `"ocode-legacy-audit"`.
- `audit_name`: `"legacy"`.
- `rejected_findings`: the REJECTED list with per-item rationale (these are potential bugs in the audit's own verifier).
- `uncertain_findings`: the UNCERTAIN list with the question each raised (these are signals the audit's classification heuristics need sharpening).
- `excluded_info_findings`: INFO items the user excluded during Phase D Step 4 (these signal over-eager INFO classification by the source skill).
- `user_flagged_misses`: any legacy systems the user mentioned during bundling that the audit failed to detect.
- `created_projects`: the list of `PROJ-NNN` IDs created in this run.

Write to `.opencode/skills/ocode-legacy-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both `rejected_findings` and `user_flagged_misses` are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/legacy_audit/`.

---

## Phase H: Hand-off

Print to the user:

```
Created N project(s) from <audit-dir-name>:

  PROJ-NNN — <title>
    Path: Projects/active_projects/PROJ-NNN/
    Cluster: <removal cluster>
    Verified: V / Uncertain (included): U_in / INFO (included): I_in / Rejected: R / Out-of-scope: O
    Phases: <list, e.g. "1 Critical, 2 Major, 3 Minor">
    Save-migration findings (banned by CLAUDE.md Rule 3): <count>
    Zero-call-site deletions (single-PR): <count>

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>

Refinement feedback written to: .opencode/skills/ocode-legacy-audit/refinement_proposals/<today>_<basename>.md

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

If any project contains save_migration_code findings, surface them on a separate line: `⚠ <count> save-migration-code findings across <N> projects — banned by CLAUDE.md Rule 3, recommend prioritizing these in the next implementation pass.`

If any project has a Phase 1 with multiple zero-call-site deletions, surface them: `✓ <count> zero-call-site deletions across <N> projects — these can ship as quick single-PR deletions before tackling caller migrations.`

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
