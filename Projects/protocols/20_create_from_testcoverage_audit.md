# PROTOCOL 20: Create Projects from OpenCode Test Coverage Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-testcoverage-audit` review, independently
re-verify every CONFIRMED gap against current source, and create one or more
`Projects/active_projects/PROJ-NNN/` directories — bundled by **layer +
module cluster** rather than severity — containing every actionable item
that survives the third pass. ADVISORY UI items are recorded as a tracking
section, not promoted into per-symbol unit-test work.

OpenCode's testcoverage-audit already runs an internal Phase-3 verifier (per
shard, in `findings/VERIFIED_SHARD_*.md`) over Phase-2 discovery findings.
That pass is rigorous but shares blind spots with the Phase-2 reviewers
(same prompt, same code-reading angle, same import-graph blind spots in
`coverage_matrix.json`). **A third independent pass with a different model
is what makes this protocol auditable.** Do not skip it for time.

The most common failure mode the third pass catches: **indirect coverage**.
A symbol is reported as Tier 0 / Tier 1 because no test file imports it by
name, but a higher-level test does exercise it through a wrapper, registry
lookup, or two-phase ability aggregation. The Phase-1 deterministic scanner
cannot detect this; the Phase-2 agents sometimes catch it; this protocol's
agents must explicitly look for it.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the
> Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** write any new test files, fixtures, or factories.
- **Do NOT** modify the source audit report or its `findings/`/`raw/`
  directories.
- **Do NOT** promote items the audit's own `VERIFIED_SHARD_*.md` transparency
  tables marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** drop findings on the basis of severity alone. CRITICAL,
  MAJOR, and MINOR all enter the candidate set; severity drives **phase
  ordering inside a project**, not project boundaries.
- **Do NOT** promote ADVISORY items into phase checklists by default. They
  stay in a tracking section unless the user explicitly opts them in during
  Phase D bundling.
- **Do NOT** leave a phase listed in any `plan.md` without a populated
  `phase_N_checklist.md`. Skipping a category entirely is fine; an empty
  checklist is not.
- **Do NOT** consume a `*_test-review/`, `*_error-audit/`, `*_type-audit/`,
  or `*_docs-audit/` directory. This protocol is testcoverage-audit only —
  abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a testcoverage-audit directory, e.g.
     `Reviews/results/2026-05-04_175101_testcoverage-audit/`. Accept
     absolute or relative, with or without a trailing slash.
   - **If no argument was given, automatically select the most recent
     `*_testcoverage-audit` directory under `Reviews/results/`.** Sort by
     the timestamp embedded in the directory name; lexicographic newest
     wins. Tie-break on filesystem mtime. Print the chosen path on its own
     line (`Auto-selected most recent testcoverage-audit: <path>`) so the
     user can see which audit is being processed, then continue without
     prompting.
   - If no `*_testcoverage-audit` directories exist, stop and tell the
     user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with
   `_testcoverage-audit`. If the user passed a `*_test-review/`,
   `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` path, abort with:
   `Wrong audit type — claude-proj-from-testcoverage-audit only consumes
   *_testcoverage-audit/ directories. Use the matching skill instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/SUMMARY.md` exists.
   - `<audit_dir>/SUMMARY.json` exists.
   - `<audit_dir>/findings/` exists with at least one
     `VERIFIED_SHARD_*.md`.
   - `<audit_dir>/raw/manifest.json` exists. Read `shard_count` from it —
     do not assume 18.
   - `<audit_dir>/raw/coverage_matrix.json` exists, with the wrapped
     `{coverage_source, files: {...}}` shape. (Older flat-shape outputs
     should be rerun via `ocode-testcoverage-audit` rather than consumed
     here.)
   - `<audit_dir>/raw/layer_summary.json` exists.
   - `<audit_dir>/raw/file_inventory.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent
   findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g.
   `2026-05-04_175101_testcoverage-audit` → `2026-05-04`) — it goes into
   project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `SUMMARY.json` (the authoritative structured source) and every
`findings/VERIFIED_SHARD_*.md` (the per-shard prose detail). Build a
normalized list of candidate items, **keeping only items marked CONFIRMED**
(including severity-downgraded confirmations).

Use `raw/coverage_matrix.json` (read entries via `data["files"][path]`),
`raw/layer_summary.json`, and `raw/file_inventory.json` to hydrate any
finding missing precise location data, candidate test files, or layer
attribution.

### Include

- **`SUMMARY.json` `findings[]` entries** — every CONFIRMED item with
  category, severity, file, line range, symbol, layer, and suggested test
  description. This is the authoritative structured set.
- **`findings/VERIFIED_SHARD_*.md` `## CONFIRMED Gaps` sections** — full
  prose detail for each entry: production location, key untested symbols,
  risk note, and the suggested test description. Use these to cross-check
  the JSON and to enrich the working list with prose context.
- **Tier 0 and Tier 1 file-level entries** — when an entire module has
  zero unit tests (`tier0_module`) or is imported but exercises no
  symbols (`tier1_module`), the candidate item is the *file* with its
  list of key untested symbols, not one item per symbol. The phase
  checklist will expand to per-symbol checkboxes in Phase E.
- **Per-symbol gap entries** — `missing_error_path`, `missing_boundary`,
  `missing_branch` entries name a single function / method, with cited
  line range and the specific path the test must exercise.

### Exclude (mark OUT_OF_SCOPE)

- Anything in the `## Disputed & Inconclusive Claims` table at the end of
  each `VERIFIED_SHARD_*.md` — these were already filtered by OpenCode's
  Phase-3 verifier.
- Anything from the unverified `findings/SHARD_*.md` files that does not
  also appear in the corresponding `VERIFIED_SHARD_*.md`.
- Top-level summary tallies in `SUMMARY.md` — they are derivable from
  per-shard data and not finding-level claims themselves.
- ADVISORY items — held in a separate buffer, not in the candidate set
  for verification by default. The user may opt them in during Phase D
  bundling; the verifier will then run a lighter check (confirm
  classification rather than confirm absence of coverage).

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `S03-CRIT-002`, `S07-MAJOR-014`, `S12-MINOR-021` |
| `shard` | `01`..`{shard_count:02}` |
| `category` | `tier0_module`, `tier1_module`, `missing_error_path`, `missing_boundary`, `missing_branch`, `ui_advisory` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` / `ADVISORY` (verified value) |
| `production_file` | `game/strategy/treasury/treasury_engine.py` |
| `production_line_range` | `124-186` (file-scope items use the full file range) |
| `production_symbol` | `TreasuryEngine.apply_modifiers` (or `null` for whole-file Tier 0/1 items) |
| `layer` | `core` / `engine` / `services` / `simulation` / `strategy` / `ai` / `research` / `assets` / `ui` (derived from path) |
| `module_cluster` | `core/math`, `strategy/treasury`, `simulation/combat/formation` (derived from path: layer + first 1–2 subdirs) |
| `key_symbols` | list of untested function/method/class names (whole-file items only) |
| `candidate_test_files` | from `coverage_matrix.json` — files that import this module but were judged not to exercise it |
| `suggested_test_description` | one paragraph from the verified shard report's "Suggested test" field |
| `loc_estimate` | rough LOC of the production region needing coverage |
| `source_finding` | which `VERIFIED_SHARD_XX.md` it came from |

Save the working list to
`.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report
Output` convention in the project's `CLAUDE.md`). Disposable.

Hold the ADVISORY buffer separately at
`.agent_reports/<audit-name>/advisory_buffer.json` for the tracking
section in Phase E.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches and dispatch **one
`Explore` subagent per non-empty batch in parallel** (single message,
multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Tier 0 foundation.** All `tier0_module` items in
  `core` / `engine` / `services` / `assets`. Highest-impact zero-coverage
  in the foundation layers.
- **Batch 2 — Tier 0 domain.** All `tier0_module` items in
  `simulation` / `strategy` / `ai` / `research`.
- **Batch 3 — Partial coverage.** All `tier1_module` items plus all
  `missing_error_path`, `missing_boundary`, `missing_branch` items across
  every non-UI layer.
- **Batch 4 — UI advisory (lighter pass).** ADVISORY items, only if the
  user opted them into scope. Verifier confirms the audit's classification
  ("genuine pygame rendering vs testable business logic") and flags any
  items that should have been MAJOR (UI business logic with no
  coverage) — these get promoted into Batch 3's verdict pool.

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

#### `tier0_module`

1. **Confirm zero unit tests exist for the module.**
   - Read `coverage_matrix.json[<file>]` for the audit's
     `candidate_test_files` list. Open every candidate test and grep for
     the module's symbols (not just the module name — symbols may be
     re-exported through `__init__.py`).
   - Search `tests/unit/` for any file that imports the module path or
     any of its `key_symbols`. The Phase-1 scanner uses import-graph +
     name-grep; symbols accessed through registries, factories, or
     two-phase ability aggregation can be exercised without ever
     appearing as a direct import.
   - Read sibling-module tests in the same layer (e.g.
     `tests/unit/core/test_*.py` for a `game/core/*.py` finding) — a
     sibling test may exercise this module's surface through composition.
2. **If any unit test genuinely exercises the module's behavior** →
   `REJECTED` with `file:line` evidence pointing to the test.
3. **If only "import-and-instantiate" tests exist** (no behavioral
   assertions) → `VERIFIED` with note that the existing tests are
   trivial. The new tests in the project still need writing.
4. **If genuinely no coverage** → `VERIFIED`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `tier1_module`

1. The audit reports test files import this module but no test exercises
   any of its symbols. Confirm by reading every candidate test and
   checking whether each `key_symbol` actually appears in an executable
   path (not just in a comment, docstring, or unused import).
2. If at least one symbol IS exercised → narrow the finding: the module
   is partially covered; the remaining untested symbols become individual
   `missing_*` items. Mark verdict `VERIFIED` with a scope adjustment
   note.
3. If no symbol is exercised → `VERIFIED` as a Tier 1 module finding.
4. If indirect coverage is found through a registry / factory / ability
   aggregation path → `REJECTED` with concrete evidence.
5. Verdict: `VERIFIED` (possibly with adjusted scope) / `REJECTED` /
   `UNCERTAIN`.

#### `missing_error_path`

1. Open the cited `production_file` at `production_line_range`. Identify
   the error-raising path the audit claims is untested (the `raise`,
   the `except`, the validation guard, etc.).
2. Read every candidate test that imports the module. For each test that
   touches the symbol, trace whether the error path is actually
   triggered. Look for `pytest.raises`, `assert ... is None`, or any
   assertion shape that would only pass if the error fired.
3. **Also check tests outside the candidate list** — sometimes an
   integration test in `tests/integration/` exercises the error path
   without `tests/unit/` having any direct coverage, which is still a
   real Tier 1 / partial-coverage gap (integration tests don't substitute
   for unit tests at this protocol's scope) but the verdict note should
   record the indirect coverage so the project doesn't double-test it.
4. If the error path is genuinely never triggered by any unit test →
   `VERIFIED`.
5. If an existing unit test does trigger it → `REJECTED` with
   `file:line` of the assertion.
6. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `missing_boundary` / `missing_branch`

1. Open the cited line range. Identify the specific boundary value
   (empty list, `None`, max value, etc.) or branch (`else` arm,
   `elif` ladder member) the audit claims is untested.
2. Read every candidate test parametrize block, fixture, and test body
   for the cited symbol. A `@pytest.mark.parametrize` block can cover
   many boundaries with one test function — check the parameter values,
   not the function count.
3. If the boundary / branch is genuinely never hit by any test input →
   `VERIFIED`.
4. If a parametrize value or a sibling test does hit it → `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `ui_advisory` (only when user opted in)

1. Confirm the cited code is genuinely pygame rendering / event
   handling / layout positioning — not testable business logic.
2. If the cited region contains testable business logic (calculations,
   data transforms, validation) → **upgrade** to `MAJOR` with category
   `missing_error_path` or appropriate finer-grained category. These
   items move to Batch 3's pool.
3. If genuinely UI-only → `VERIFIED` as ADVISORY (still goes into the
   tracking section, not phase work).
4. Verdict: `VERIFIED_ADVISORY` / `UPGRADE_TO_MAJOR` / `REJECTED`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project
  inclusion.
- **`VERIFIED_ADVISORY`** — UI rendering / event item, kept in tracking
  section only.
- **`UPGRADE_TO_MAJOR`** — was ADVISORY, has business logic; promoted
  into the per-symbol candidate pool.
- **`REJECTED`** — counter-evidence found (existing test exercises the
  cited path, indirect coverage via registry, etc.). Provide `file:line`
  of contrary evidence.
- **`UNCERTAIN`** — ambiguous (e.g., unclear whether a registry-driven
  call path exercises the symbol). Surface for user judgment in
  Phase D. Provide the specific question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue
  (stale-after-audit, generated code, `__init__.py` re-export).

Each verdict carries one short evidence line. **No verdict without
evidence.**

### Where agents write

Each subagent writes to
`.agent_reports/<audit-name>/verification_<batch>.md` and returns a
summary in its tool reply. The main session aggregates the batch reports
into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocol 14/20 from protocols 11/12: instead
of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by `module_cluster` (layer + first 1–2 subdirs).
2. Compute volume per cluster: count of items + summed loc_estimate.
3. Decide breakdown by total VERIFIED count V:
   - V < 30:         ONE project, all clusters in one bundle.
   - 30 <= V <= 100: 2–3 projects merged by layer adjacency:
                       core + services + engine + assets       (foundation)
                       simulation + strategy + ai + research   (domain)
                       cross-cutting helpers                   (cross-cut)
   - V > 100:        One project per layer with >=10 items. Smaller layers
                     attach to the most architecturally adjacent larger one.
4. Tier 0 modules with >=10 untested symbols form their own bundle when
   that produces a coherent project (e.g. "Strategy treasury test
   coverage" stands alone if treasury has 12 Tier 0 symbols).
5. For each bundle, plan phase ordering:
   - Phase 1: CRITICAL — tier0_module items
   - Phase 2: MAJOR    — tier1_module + missing_error_path items
   - Phase 3: MINOR    — missing_boundary + missing_branch items
   - Phase 4: ADVISORY tracking (only if user opted ADVISORY into scope)
   - Drop empty phases.
6. UNCERTAIN items are queued for Step 3.
```

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                       | Clusters                  | Verified | Uncertain | Phases (categories)        |
|---|---------------------------------------------|---------------------------|----------|-----------|----------------------------|
| 1 | Test coverage — core math + services       | core/math, services/llm   |  V1      |  U1       | Critical, Major            |
| 2 | Test coverage — strategy treasury + ai     | strategy/treasury, ai/    |  V2      |  U2       | Critical, Major, Minor     |

Totals: VERIFIED V / UNCERTAIN U / REJECTED R / OUT_OF_SCOPE O (excluded)
ADVISORY tracking-only: A items (held aside; will appear as a single
tracking section in the bundle whose layer matches each item).
```

Then use `AskUserQuestion` with options:

- **Accept proposal as-is** (Recommended, default).
- **Merge two projects** (user names which two).
- **Split a project** (user names which one and how to split).
- **Include ADVISORY items as Phase 4 work** (default: No — tracking
  only).
- **Custom — describe the bundling I want** (free-form via "Other").

Iterate. Each adjustment re-runs Step 1's volume + phase math against
the new bundle definitions and re-shows the table. Stop when the user
accepts.

### Step 3 — Resolve UNCERTAIN findings

Once the bundling is locked, walk the UNCERTAIN list grouped by their
assigned bundle. For each item:

```
[bundle 1, item 2 of 3] S07-MAJOR-014 — TreasuryEngine._apply_modifier_dict
  Layer: strategy | File: game/strategy/treasury/treasury_engine.py:124-186
  Verifier note: registry-driven call path; unclear whether
    test_treasury_modifier_application exercises this branch via
    ModifierRegistry.lookup() or only through the explicit-class path.
  Recommendation: include / exclude / defer to a future audit?
```

Ask via `AskUserQuestion`:

- **Include** — add to project plan (with note recording the user's
  decision).
- **Exclude** — drop, log in `findings/verification_report.md` as
  user-deferred.
- **Defer** — record in `findings/verification_report.md` for a later
  audit; not in any project this run.

Persist all decisions to `findings/bundling_decisions.md` (created in
Phase E Step 7).

### Step 4 — Final confirmation

Print the locked bundle table again with adjusted counts (UNCERTAIN now
resolved into Verified / Excluded / Deferred). Ask `AskUserQuestion`:
"Proceed with project creation?" with options Accept / Adjust further.
Accept moves to Phase E.

---

## Phase E: Build the Project(s)

For each finalized bundle:

1. **Create the project skeleton** with the canonical script:
   ```bash
   python Projects/scripts/create_project.py "Test coverage — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`,
   `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`,
   and `findings/`. **Do not create these files manually.** Capture the
   assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Test coverage — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to
     its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action =
     `Project created from \`<audit-dir-name>\` after independent
     verification`, Next Action = `Begin Phase 1 tasks`, Blockers =
     `None`.
   - **Overview**: one paragraph naming the source audit, the count of
     verified items in this bundle, the layers / module clusters
     covered, and the count of Tier 0 modules with their LOC estimate
     (these are the highest-impact items).
   - **Goals**: one bullet per phase ("Add unit tests for N Tier 0
     modules across <clusters>", "Add error-path tests for M MAJOR
     gaps", "Cover K boundary / branch gaps", etc.).
   - **Scope**: `In:` the categories and clusters in this bundle.
     `Out:` other bundles' contents (link by sibling PROJ-NNN if they
     exist), plus REJECTED and OUT_OF_SCOPE categories ("see
     `findings/verification_report.md`"), plus ADVISORY items
     ("recorded in `findings/ui_coverage_advisory.md` — UI rendering
     conventionally tested via integration / manual paths, not unit
     tests").
   - **Key Files** table: top ~10 production files in this bundle by
     untested-symbol count.
   - **Related Documents** links to `design.md`, `decisions.md`,
     `findings/verification_report.md`, `findings/source_audit.md`,
     `findings/bundling_decisions.md`, and (when ADVISORY is in scope
     for this bundle's layer) `findings/ui_coverage_advisory.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the
   `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py`.
   For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific. Examples:
     - "Add unit tests for the N Tier 0 production modules in
       `<cluster>` identified by audit `<audit-dir-name>`."
     - "Add error-path tests for M production functions whose `except`
       / validation paths are untested."
     - "Cover K boundary / branch gaps in already-tested functions."
   - **Tasks section:** one `### Task N.M` per production file (group
     multiple symbols in the same file under one task to keep the
     checklist scannable). Each task has:
     - `**File:** \`<production_file>\`` (single file per task).
     - `**Test file:** \`tests/unit/<mirrored_path>/test_<basename>.py\``
       (canonical convention; the implementing agent creates the file
       if it doesn't exist).
     - `**Pytest invocation:** \`pytest tests/unit/<mirrored_path>/test_<basename>.py\``.
     - One checkbox per untested symbol or path. Examples:
       - `[ ] Add unit test for \`TreasuryEngine.apply_modifiers\` (lines 124-186) — exercise both the registry-driven and explicit-class branches; assert returned modifier dict matches expected math.`
       - `[ ] Add unit test for \`TreasuryEngine._validate_modifier\` error path (lines 198-205) — feed invalid modifier id, assert raises \`InvalidModifierError\`.`
       - `[ ] Add boundary test for \`compute_upkeep\` (line 312) — empty population dict returns 0.0, not raises.`
     - For UNCERTAIN-then-INCLUDED items, the checkbox carries Claude's
       adjusted scope note: `_(verification adjusted from audit's
       original scope — see verification_report.md)_`.
     - Final checkbox per task: `[ ] Verify: \`pytest <test-path>\`
       passes; new test functions run in <5s combined under the
       standard pytest invocation.`
   - **Phase Completion Checklist:** copy the template's standard block
     verbatim.
   - **Audit-source line at the bottom:** `_Source audit:
     \`Reviews/results/<audit-dir-name>/\`. See
     \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you
   find yourself writing "TBD", "fill in", or "[Task Name]", you have
   a bug — either the phase has no verified items (drop it from
   `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table.
   Every production file referenced in any `phase_N_checklist.md` must
   appear here, plus the test files those checklists name (even when
   the test file does not yet exist). Columns: `File`, `Type`
   (`Production` for `game/*` files; `Test (new)` for proposed test
   files), `Notes` (one-line action summary — e.g., "12 untested
   symbols across 3 classes" or "new test file — covers 4 error paths
   in TreasuryEngine").

5. **Update `design.md`.** Add a `## Source Audit` block at the top
   with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified,
     <U> uncertain (resolved), <D> deferred | Project siblings: <list
     of other PROJ-NNN created in this run>`.
   - Layer / cluster coverage and severity breakdown.
   - For Tier 0 modules: a "Tier 0 Modules" subsection listing each
     module with its layer, LOC estimate, and key untested symbols.
     This is the highest-impact section of the project.
   - For ADVISORY tracking: a one-line pointer to
     `findings/ui_coverage_advisory.md` if any ADVISORY items fall
     within this bundle's layer.
   Keep the rest of the template; populating phases will fill it
   during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "module-cluster locality across strategy/treasury and strategy/economy"> per user direction | Bundling driven by code relatedness rather than severity to maximize implementation continuity (test files mirror production layout, so bundling by cluster keeps each session focused on one area); full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full*
   output of Phase C for items in this bundle, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified
     / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>`
     OpenCode CONFIRMED candidates for this bundle).
   - `## Verified` — table of verified items in this bundle: `id |
     category | severity | production_file | symbol |
     suggested_test_description`. (These are the items in the phase
     checklists.)
   - `## Rejected` — table per item: `id | original audit claim |
     contrary evidence (file:line) | rationale`. **Each row is a
     potential bug in the audit's own verifier or in the Phase-1
     coverage matrix's import-graph heuristic** — keep this section
     scannable so the user can feed it back later via Phase 9
     refinement feedback.
   - `## Uncertain (resolved)` — table per item: `id | the question
     the verifier raised | the user's Phase D Step 3 decision (Include
     / Exclude / Defer)`.
   - `## Out of Scope` — table per item: `id | claim | reason for not
     acting (e.g. stale_after_audit, generated_code,
     init_reexport_only)`.

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the testcoverage-audit at:

   `Reviews/results/<audit-dir-name>/`
     - [SUMMARY.md](../../../../Reviews/results/<audit-dir-name>/SUMMARY.md)
     - [SUMMARY.json](../../../../Reviews/results/<audit-dir-name>/SUMMARY.json)
     - [findings/](../../../../Reviews/results/<audit-dir-name>/findings/)
     - [raw/](../../../../Reviews/results/<audit-dir-name>/raw/)

   See [verification_report.md](verification_report.md) for the
   independent re-verification that filtered the audit's CONFIRMED
   claims before they entered this project's plan, and
   [bundling_decisions.md](bundling_decisions.md) for the interactive
   bundling that decided which findings ended up in this project versus
   its siblings.
   ```

9. **Write `findings/bundling_decisions.md`.** Record of Phase D:
   - Default proposal table.
   - User adjustments (each merge / split with rationale).
   - Final bundle definitions.
   - Per-UNCERTAIN-item user decisions from Step 3.
   - The user's Yes / No on opting ADVISORY into scope.

   This file is identical across all sibling projects created in the
   same run (so the user can read it once for the full picture). The
   skill writes it once per project, not just once per run.

10. **Write `findings/ui_coverage_advisory.md` (when applicable).** If
    the audit produced ADVISORY items in this bundle's layer (and the
    user did not opt them into phase scope), write a single tracking
    file listing each advisory item:
    - File path, line range, brief description, audit's classification
      (rendering / event / layout).
    - One-line note: "Conventionally exercised via manual / integration
      paths, not unit tests."
    Skip this file entirely if the bundle's layer has no ADVISORY items
    or the user opted ADVISORY into scope (in which case ADVISORY
    becomes Phase 4 work and lands in `phase_4_checklist.md` instead).

---

## Phase F: Self-Check Before Finishing

For **each** created project, verify:

- [ ] Every phase listed in `plan.md`'s Quick Status table has a
      corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in",
      `[Task Name]`, or `[Filled during implementation]` left over from
      the template.
- [ ] Every production file path in any checklist appears in
      `manifest.md`, and vice versa.
- [ ] Every proposed `tests/unit/...` test file path in any checklist
      appears in `manifest.md` with `Type: Test (new)` (or `Test` if it
      already exists).
- [ ] The verified-item count in `decisions.md` / `design.md` matches
      the total finding-level checkbox count across all
      `phase_N_checklist.md` files (within a small margin for grouping
      multiple symbols under one task).
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist.
- [ ] No ADVISORY items leaked into a checklist unless the user
      explicitly opted them in during Phase D.
- [ ] Every UNCERTAIN item is either in a checklist (user said
      Include) or recorded in `verification_report.md` as
      Excluded / Deferred.
- [ ] When ADVISORY items exist in this bundle's layer and were NOT
      opted into scope: `findings/ui_coverage_advisory.md` exists and
      lists every advisory item.
- [ ] You have not modified anything outside
      `Projects/active_projects/PROJ-*/` (except
      `Projects/projects_index.md`, which `create_project.py` updates).
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
    Tier 0 modules: <count, with module-cluster summary>
    ADVISORY tracking-only items in this bundle: A (see findings/ui_coverage_advisory.md)

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>
ADVISORY items recorded across all bundles: <total A> (no unit-test work scheduled)

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` across all projects sums to zero, surface that explicitly — the
audit's own verifier rejects a non-trivial fraction of Phase-2 claims
through the import-graph + name-grep heuristic, so a downstream
skeptical pass that finds zero false positives is suspicious, not
reassuring. Indirect coverage through registries and ability aggregation
is the most common false-positive source.

If any project contains Tier 0 modules in `core` or `engine`, surface
that on a separate line: `⚠ <count> Tier 0 modules in foundation
layers — recommend prioritizing these before domain-layer work since
foundation regressions have the widest blast radius.`

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the
hand-off print. Implementation happens in
`/claude-proj-continue PROJ-NNN`.
