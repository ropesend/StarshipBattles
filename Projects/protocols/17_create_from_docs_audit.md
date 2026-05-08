# PROTOCOL 17: Create Project(s) from Docs Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-docs-audit` review, independently re-verify every actionable finding against current docs and source, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **doc-file-cluster** rather than severity — containing every item that survives the third pass.

OpenCode's docs-audit already runs an internal Code-Base Accuracy Validator (`findings/docs_accuracy_code.md`) over its content-accuracy claims. That pass is rigorous but shares blind spots with the Phase-1 reviewers (same prompt, same doc-reading angle). **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit docs, production code, tests, or data files.
- **Do NOT** correct dead references, update PROJ statuses, fix content-accuracy claims, or apply terminology normalizations. The output is a *plan*; the doc edits happen later under `/claude-proj-continue PROJ-NNN`.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/docs_accuracy_code.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** drop findings on the basis of severity. CRITICAL, MAJOR, and MINOR all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume a `*_type-audit/`, `*_error-audit/`, or `*_audit-shrink/` directory. This protocol is docs-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a docs-audit directory, e.g. `Reviews/results/2026-05-04_090436_docs-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_docs-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent docs-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_docs-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_docs-audit`. If the user passed an `*_type-audit/`, `*_error-audit/`, or `*_audit-shrink/` path, abort with: `Wrong audit type — claude-proj-from-docs-audit only consumes *_docs-audit/ directories. Use claude-proj-from-type-audit, claude-proj-from-error-audit, or claude-proj-from-audit-shrink instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `docs_review_G*.md`.
   - `<audit_dir>/findings/docs_consistency_cross.md` exists.
   - `<audit_dir>/findings/docs_accuracy_code.md` exists.
   - `<audit_dir>/raw/` exists with `doc_file_refs.json`, `stale_proj_refs.json`, `doc_staleness.json`, `undocumented_modules.json`, `doc_inventory.json`.
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_090436_docs-audit` → `2026-05-04`) — it goes into project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities are kept.** OpenCode's `findings/docs_accuracy_code.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Include

- **`report.md` §2 Doc Health Scorecard** — group-level totals; used to cross-check that the candidate set covers every group with non-zero findings.
- **`report.md` §3 Dead Reference Register** — every dead `game/*`, `Tools/*`, `Projects/protocols/*`, `Reviews/protocols/*`, `data/*`, `tests/*` reference with `doc_file:line` and the missing `referenced_path`.
- **`report.md` §4 Stale PROJ Reference Register** — PROJ references that describe a feature as "planned" or "in progress" when the PROJ is already completed/archived per `projects_index.md`.
- **`report.md` §5 Doc Staleness Register** — docs past the 60-day `Last verified:` threshold.
- **`report.md` §6 Undocumented Modules** — production modules > 50 LOC with zero doc coverage. The audit pre-filters to public-API / architectural-surface modules; keep that filter.
- **`report.md` §7 Cross-Doc Consistency Issues** — terminology drift, contradictory guidance, broken cross-references, duplicate documentation.
- **`report.md` §8 Prioritized Documentation Update Plan** — every Critical/Major/Minor row.
- **`findings/docs_review_G1.md` through `docs_review_G6.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR item not already captured in §3–7. Watch for group reports listing items the executive summary skipped.
- **`findings/docs_consistency_cross.md`** — cross-doc terminology / contradictory-guidance / cross-reference / duplicate-documentation findings with `DOC-CROSS-NN` style IDs.
- **`findings/docs_accuracy_code.md`** — content-accuracy claims marked CONFIRMED (the doc is wrong against live code).
- **`raw/doc_file_refs.json`, `raw/stale_proj_refs.json`, `raw/doc_staleness.json`, `raw/undocumented_modules.json`** — concrete `doc_file:line` lookup, used to hydrate findings missing precise locations.

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/docs_accuracy_code.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- `raw/stale_proj_refs.json` entries where the surrounding doc text clearly frames the PROJ as historical context or already-implemented — the audit notes these are not stale.
- Findings in the "What NOT to Report" categories from the audit's own SKILL.md: minor typos / grammar (unless they cause factual confusion), formatting preferences, "this doc should be split into multiple files," missing examples for well-documented features.
- Undocumented-module entries the audit's reviewers explicitly classified as implementation-detail rather than public-API / architectural surface.

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `DOC-G1-001`, `DOC-CROSS-002`, `DOC-ACC-007` |
| `category` | `dead_ref`, `stale_proj`, `content_error`, `missing_docs`, `terminology_drift`, `cross_doc_inconsistency`, `doc_staleness`, `code_example_broken` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` |
| `doc_file` | `docs/01_ARCHITECTURE.md` |
| `line_or_section` | `412` or `§3.2 Spatial Terminology` |
| `referenced_path` | `game/strategy/old_module.py` (for dead refs); `null` otherwise |
| `referenced_proj` | `PROJ-298` (for stale_proj); `null` otherwise |
| `doc_group` | `G1` / `G2` / `G3` / `G4` / `G5` / `G6` / `cross` (derived from finding source) |
| `current_text` | one-line excerpt of the offending doc passage (or `null` for missing-docs) |
| `recommended_change` | `update path to game/strategy/new_module.py` / `mark as implemented` / `rewrite §3.2 to use Sector` (or `null`) |
| `recommendation` | one short verb phrase from the audit |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `risk` | one-line description of what misleads the reader if not fixed (especially for CRITICAL dead-refs and content errors) |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Dead refs + Stale PROJs (deterministic).** All `dead_ref` and `stale_proj` items.
- **Batch 2 — Content-accuracy errors.** All `content_error` and `code_example_broken` items. **Highest mislead risk — verifier must read both doc and code.**
- **Batch 3 — Missing docs + staleness.** All `missing_docs` and `doc_staleness` items.
- **Batch 4 — Cross-doc consistency.** All `terminology_drift` and `cross_doc_inconsistency` items.

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch, the agent must read the doc file at the cited line and — for content-accuracy claims — read the corresponding code under `game/` (or wherever the doc claim points) to confirm the doc is genuinely wrong against current code.

#### `dead_ref`

1. Open the cited `doc_file:line`. Confirm the path reference is present and matches `referenced_path`.
2. Stat the `referenced_path`. If it exists → `REJECTED` (false positive; either the doc is fine or the file came back).
3. If it does not exist:
   - Search the repo for a renamed equivalent (same basename, similar module name). If found, the recommendation is "update path to <new path>" — verdict `VERIFIED`.
   - If nothing similar exists, the referenced functionality was likely removed — recommendation is "remove reference / mark as historical" — verdict `VERIFIED`.
4. Verdict: `VERIFIED` / `REJECTED`.

#### `stale_proj`

1. Open the cited `doc_file:line`. Read the surrounding paragraph.
2. Check `Projects/projects_index.md` for the PROJ status.
3. Decide:
   - PROJ is Complete/Archived AND surrounding text says "planned" / "in progress" / "we will" / "to be added" → `VERIFIED`. Recommend updating the doc to reflect implemented status.
   - PROJ is Complete/Archived BUT surrounding text frames it as historical context or already-implemented → `REJECTED` (false positive).
   - PROJ is still Active and the doc says it's planned → `REJECTED` (not stale).
4. Verdict: `VERIFIED` / `REJECTED`.

#### `content_error` / `code_example_broken`

1. Open the cited doc section. Read enough of it to understand the claim being made.
2. **Read the corresponding code** under `game/` (or wherever the doc points). Trace the actual behavior.
3. Decide:
   - Doc claim contradicts current code (function signature, return type, behavior, layer boundary, data shape) → `VERIFIED`. Recommendation states the corrected claim.
   - Code example references a function / class / import that no longer exists → `VERIFIED`.
   - Doc claim is actually correct, the audit reviewer misread the code → `REJECTED`.
   - Code is too complex to determine in a reasonable time → `UNCERTAIN`. Surface the question for the user.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `missing_docs`

1. Open the named module under `game/`. Confirm it is > 50 LOC and is part of the public-API / architectural surface (crosses layer boundaries, is imported widely, is a service / facade / protocol).
2. Decide:
   - Genuinely architectural surface, no doc mention anywhere → `VERIFIED`. Recommendation states which existing doc should host the new section (or proposes a new file under `docs/systems/` or `docs/guides/`).
   - Implementation detail, internal helper, or already mentioned in passing → `REJECTED`.
3. Verdict: `VERIFIED` / `REJECTED`.

#### `doc_staleness`

1. Open the cited doc. Confirm the `> **Last verified:**` date and that it is past the 60-day threshold (`MAJOR` if > 120 days, `MINOR` if 60–120).
2. Spot-check 2–3 claims in the doc against current code. If the doc is materially out-of-date → `VERIFIED` (recommend full re-verification pass). If the doc is still accurate and only the timestamp is stale → `UNCERTAIN` (a stamp refresh might be enough; flag for the user).
3. Verdict: `VERIFIED` / `UNCERTAIN`.

#### `terminology_drift` / `cross_doc_inconsistency`

1. Read both doc files referenced in the finding.
2. Decide:
   - Same concept described two contradictory ways, or "System" used to mean "Sector" (or vice versa), or a cross-reference points to a non-existent section → `VERIFIED`. Recommendation names the canonical term / canonical location.
   - Cross-reference is ambiguous but neither doc is wrong → `UNCERTAIN`.
   - The two docs actually agree once read in context → `REJECTED`.
3. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (file exists, PROJ-text was historical, code matches doc, etc.). Provide `doc_file:line` or code `file:line` of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (typo, formatting, audit-rejected category). Logged but excluded from project.

Each verdict carries one short evidence line. **No verdict without evidence.**

### Where agents write

Each subagent writes to `.agent_reports/<audit-name>/verification_<batch>.md` and returns a summary in its tool reply. The main session aggregates the batch reports into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocol 13/14/17 from protocols 11/12: instead of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by `doc_file` (or doc-file-cluster — adjacent
   files in the same group like all of docs/systems/* form a natural cluster).
2. Compute volume per cluster: count of items + summed effort (LOW=1, MEDIUM=3, HIGH=8 weighted).
3. Decide breakdown by total VERIFIED count V:
   - V < 30:         ONE project, all clusters in one bundle.
   - 30 <= V <= 100: 2–3 projects. Merge clusters by doc tier:
                       root agent docs (AGENTS.md, CLAUDE.md, .agents/CODEX.md) +
                         architecture (docs/0N_*.md)            (foundation)
                       systems (docs/systems/) + guides (docs/guides/)  (reference)
                       protocols (Projects/protocols/, Reviews/protocols/)  (procedural)
   - V > 100:        One project per cluster that has >=10 items. Smaller
                     clusters attach to the most adjacent larger one.
4. Cross-doc consistency findings (terminology_drift, cross_doc_inconsistency)
   ALWAYS form their own bundle, regardless of V. They span many doc files at
   once and benefit from a single reviewer applying a canonical-term decision
   uniformly.
5. For each bundle, plan phase ordering:
   - Phase 1: CRITICAL items (dead refs, content errors that mislead first)
   - Phase 2: MAJOR items (stale PROJ, missing major docs)
   - Phase 3: MINOR items (terminology, doc staleness)
   - Drop empty phases.
6. UNCERTAIN items are queued for Step 3.
```

**Note:** Findings inside `findings/docs_consistency_cross.md` are placed in the dedicated cross-doc bundle. Findings from `findings/docs_review_G*.md` go into the bundle owning their `doc_file`.

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                     | Doc clusters             | Verified | Uncertain | Phases (severities)   |
|---|-------------------------------------------|--------------------------|----------|-----------|-----------------------|
| 1 | Docs cleanup — architecture + root agent  | docs/0N_*, AGENTS.md ... |  V1      |  U1       | Critical, Major       |
| 2 | Docs cleanup — systems + guides           | docs/systems/, guides/   |  V2      |  U2       | Major, Minor          |
| 3 | Docs cleanup — cross-doc consistency      | (multi-file)             |  V3      |  U3       | Critical, Major, Minor|

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
[bundle 2, item 1 of 4] DOC-G2-014 — content_error in docs/systems/combat.md
  Doc: docs/systems/combat.md:212 | Code: game/simulation/combat/damage.py
  Verifier note: damage pipeline order differs from doc, but engine.py also
    contains a fallback path that matches the doc's description. Unclear which
    path is canonical.
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
   python Projects/scripts/create_project.py "Docs cleanup — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Docs cleanup — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, the doc clusters covered, and any notable risk callouts (e.g. "includes 3 CRITICAL content-accuracy errors that actively mislead developers reading current docs").
   - **Goals**: one bullet per phase ("Update N dead file references in <cluster>", "Update M PROJ references whose features are now implemented", "Correct K content-accuracy claims against current code", "Normalize System/Sector terminology across docs/01_ARCHITECTURE.md and docs/systems/", etc.).
   - **Scope**: `In:` the categories and doc clusters in this bundle. `Out:` other bundles' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 doc files touched in this bundle, sorted by item count.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Correct the N verified content-accuracy errors in docs/systems/* against current code, identified by audit `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per doc file (group multiple sections in the same doc under one task to keep the checklist scannable). Each task has:
     - `**File:** \`<doc path>\`` (single doc per task).
     - `**Verification:** "Read the doc end-to-end after edits; check every cited code reference resolves; bump \`Last verified:\` stamp."`
     - One checkbox per finding, naming the line/section, the offending text, and the target replacement. Examples:
       - `[ ] Update dead reference \`game/strategy/old_module.py\` (line 412) to \`game/strategy/new_module.py\` in §3 of \`01_ARCHITECTURE.md\``
       - `[ ] Mark PROJ-298 as Complete in §"Fleet Order System" (line 89) of \`docs/systems/orders.md\` — feature implemented, not "planned"`
       - `[ ] Correct \`compute_beam_hit_chance(...)\` signature in §4.2 of \`docs/systems/combat.md\` (line 212): drop \`attack_bonus\` default-zero claim; current code requires explicit pass`
       - `[ ] Replace "Sector" with "System" in §3.2 spatial terminology block of \`docs/01_ARCHITECTURE.md\` (per AGENTS.md canonical definitions)`
     - For CRITICAL dead-reference and content-error findings: include a verification checkbox confirming the fix lands ("`[ ] Verify: \`grep -rn "<old path>" docs/\` returns nothing in modified files`"; "`[ ] Verify: code claim now matches \`game/<path>\` as of <commit-sha>`").
     - Final checkbox per phase: `[ ] Verify: \`Last verified:\` stamps updated; deterministic scan re-run shows zero dead refs / stale PROJs in modified files`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every doc file referenced in any `phase_N_checklist.md` must appear here, and every doc in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Doc` / `Doc-new` for missing-docs additions), `Notes` (one-line action summary).

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Doc-cluster coverage and severity breakdown.
   - For CRITICAL dead-refs and content errors: a one-paragraph "Mislead Risk Notes" subsection summarizing what current readers are being told incorrectly.
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "doc-cluster locality across architecture and root agent docs"> per user direction | Bundling driven by doc-file-cluster rather than severity to maximize editing continuity (one doc swept end-to-end per task); full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, doc_file, line, category, current text, recommended change, severity, mislead risk).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence `doc_file:line` or code `file:line`, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## Out of Scope` — table per item: id, why the verifier excluded it (typo, formatting, audit-rejected category, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the docs-audit at:

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

10. **Refinement Feedback** — once all sibling projects have been written, follow `Projects/protocols/15_refinement_feedback.md` to write a refinement proposal back to the originating OpenCode skill. Inputs:
    - `audit_dir` — the resolved source audit directory.
    - `source_skill: "ocode-docs-audit"`.
    - `audit_name: "docs"`.
    - REJECTED findings from `findings/verification_report.md` across all sibling projects (with reasons).
    - UNCERTAIN items the user excluded or deferred.
    - Audit-missed issues the user surfaced during Phase D bundling discussion.
    - The list of `PROJ-NNN` IDs created this run.

    Write the proposal to `.opencode/skills/ocode-docs-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user-flagged-misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/docs_audit/`.

---

## Phase F: Self-Check Before Finishing

Before printing the summary, verify:

- [ ] Every phase listed in each `plan.md`'s Quick Status table has a corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in", `[Task Name]`, or `[Filled during implementation]` left over from the template.
- [ ] Every doc file path in any checklist appears in that project's `manifest.md`, and vice versa.
- [ ] The verified-item count in `decisions.md` / `design.md` matches the total checkbox count across all `phase_N_checklist.md` files (within a small margin for grouping).
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist.
- [ ] Every UNCERTAIN item is either in a checklist (user said Include) or recorded in `verification_report.md` as Excluded/Deferred.
- [ ] Every CRITICAL dead-reference or content-error finding has at least one verification checkbox in its phase confirming the fix lands.
- [ ] The refinement-feedback proposal has been written to `.opencode/skills/ocode-docs-audit/refinement_proposals/` (or the minimal "no refinements" file if empty).
- [ ] You have not modified anything outside `Projects/active_projects/PROJ-*/` (except `Projects/projects_index.md`, which `create_project.py` updates, and `.opencode/skills/ocode-docs-audit/refinement_proposals/`).
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
    CRITICAL dead-refs / content errors: <count, with mislead-risk callout if > 0>

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>
Refinement proposal written to: .opencode/skills/ocode-docs-audit/refinement_proposals/<today>_<basename>.md

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

If any project contains CRITICAL dead-references or content errors, surface them on a separate line: `⚠ <count> CRITICAL dead-refs / content errors across <N> projects — these actively mislead developers reading current docs; recommend prioritizing before MAJOR/MINOR work.`

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
