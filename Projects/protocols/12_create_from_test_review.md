# PROTOCOL 12: Create Projects from OpenCode Test Review
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-test-review` review, independently
re-verify every CONFIRMED claim, and create three sibling
`Projects/active_projects/PROJ-NNN/` directories — one per priority tier
(P0/P1/P2 from `SUMMARY.md`) — containing only the items that survive the
third pass.

OpenCode's test-review skill already runs two passes: shard reviewers find
issues (Phase 1), and an independent verifier reads cited file:line and
emits CONFIRMED / DISPUTED / INCONCLUSIVE verdicts (Phase 3). Confirmation
rate on the 2026-05-02 reference run was ~94% (331 of 351). That second
pass is rigorous, but it can still share blind spots with the Phase-1
reviewer (same prompt, similar reading angle on the same code). **A third
independent pass with a different model is what makes this protocol
auditable.** Do not skip it for time.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the
> Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** delete or rewrite any test identified in the review.
- **Do NOT** modify the source review report or its files.
- **Do NOT** promote DISPUTED or INCONCLUSIVE items from
  `VERIFIED_SHARD_*.md` transparency tables — OpenCode's verifier already
  excluded them. Verify only the CONFIRMED set.
- **Do NOT** leave a phase listed in any `plan.md` without a populated
  `phase_N_checklist.md`. Skipping a category entirely is fine; an empty
  checklist is not.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the review path.**
   - Argument is a path to a test-review directory, e.g.
     `Reviews/results/2026-05-02_204633_test-review/`. Accept absolute or
     relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent
     `*_test-review` directory under `Reviews/results/`.** Sort by the
     timestamp embedded in the directory name; the lexicographic newest
     is the intended choice. If two share the same timestamp, fall back
     to filesystem mtime. Print the chosen path on its own line
     (`Auto-selected most recent test-review: <path>`) so the user can
     see which review is being processed, then continue without
     prompting.
   - If no `*_test-review` directories exist at all, stop and tell the
     user — do not invent a path or fall back to a non-test-review.

2. **Validate the structure.** Confirm all of:
   - `<review_dir>/SUMMARY.md` exists.
   - `<review_dir>/CROSS_SHARD.md` exists.
   - `<review_dir>/VERIFIED_SHARD_01.md` through `VERIFIED_SHARD_12.md` all exist.
   - `<review_dir>/SHARD_CONFIG.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent
   findings from a partial report. (`SHARD_XX.md` files are optional —
   they are superseded by `VERIFIED_SHARD_XX.md`.)

3. **Note the review date.** Extract the date from the directory name
   (e.g. `2026-05-02_204633_test-review` → `2026-05-02`) — it goes into
   each project's title in Phase D.

---

## Phase B: Extract the CONFIRMED Set

Read `SUMMARY.md`, every `VERIFIED_SHARD_XX.md`, and `CROSS_SHARD.md`.
Build a normalized list of candidate items, **keeping only items marked
CONFIRMED** (including severity-downgraded confirmations).

### Include

- **`VERIFIED_SHARD_XX.md` `## Verified Findings (CONFIRMED only)` sections.**
  Every claim listed here, with its category (CAT-1..CAT-12), severity
  (CRITICAL / MAJOR / MINOR — use the verified severity, not the original
  if downgraded), file path, line range, issue description, suggestion,
  and LOC affected.
- **`VERIFIED_SHARD_XX.md` `## Cross-Shard Verified Findings` sections** —
  per-shard CONFIRMED references to APC/DUP/HLP clusters.
- **`CROSS_SHARD.md`** — the master list of APC/DUP/HLP cluster
  definitions (one entry per cluster, with affected files and shards). Use
  this as the source of truth for cluster scope; the per-shard
  cross-shard sections only confirm the cluster includes that shard's
  files.

### Exclude (do NOT verify or include)

- The `## Disputed & Inconclusive Claims` table at the end of each
  `VERIFIED_SHARD_XX.md` — these were already excluded by OpenCode's
  verifier.
- Anything from the unverified `SHARD_XX.md` files that does not also
  appear in the corresponding `VERIFIED_SHARD_XX.md`.
- Top-level summary tallies in `SUMMARY.md` — they are derivable from the
  per-shard data and not finding-level claims themselves.

### Normalize

For each kept item, capture:

| Field | Example |
|-------|---------|
| `id` | `S01-CAT1-001`, `S03-CAT4-002`, `APC-001`, `DUP-002`, `HLP-003` |
| `shard` | `01`..`12`, or `cross_shard` |
| `category` | `CAT-1`..`CAT-12`, or `APC`/`DUP`/`HLP` |
| `priority_tier` | `P0` (CAT-1/2/3), `P1` (CAT-4/5/6/7 + all APC/DUP/HLP), `P2` (CAT-8..12) |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` (verified value) |
| `file` | `tests/unit/ai/test_ai.py` (or list of files for cluster items) |
| `line_range` | `124-136` (or `null` for whole-file or cluster items) |
| `test_name` | `test_navigate_to_rotates_ship` (when available) |
| `issue` | one paragraph of the finding's "Issue:" text |
| `suggestion` | one paragraph of the finding's "Suggestion:" text |
| `loc_affected` | integer |
| `source_file` | which `VERIFIED_SHARD_XX.md` or `CROSS_SHARD.md` it came from |

Save the working list to `.agent_reports/<review-name>/candidates.json`
(per the `Subagent Report Output` convention in the project's
`CLAUDE.md`). It is disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents, 5 waves)

Total verification surface: ~331 confirmed shard claims + ~10 cross-shard
cluster items = ~341 items. Splitting by shard gives natural ~20–50 item
batches that one Explore agent can handle without context overload.

### Wave plan

Dispatch **3 `Explore` subagents in parallel per wave**, single message
with three concurrent Agent tool calls. Five waves total:

| Wave | Agent 1 | Agent 2 | Agent 3 |
|------|---------|---------|---------|
| 1 | Shard 01 verified claims | Shard 02 verified claims | Shard 03 verified claims |
| 2 | Shard 04 verified claims | Shard 05 verified claims | Shard 06 verified claims |
| 3 | Shard 07 verified claims | Shard 08 verified claims | Shard 09 verified claims |
| 4 | Shard 10 verified claims | Shard 11 verified claims | Shard 12 verified claims |
| 5 | CROSS_SHARD APC clusters | CROSS_SHARD DUP+HLP clusters | (idle, or cluster-cross-check audit) |

Wait for each wave to complete before dispatching the next so the
orchestrator can detect agent-level failures early. Within a wave, agents
are independent and run concurrently.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

1. **Open the cited file at the cited line range.** Confirm the test (or
   block of tests) is still there, at the cited lines, with substantively
   the same shape the finding describes. If it has been deleted, renamed,
   or substantially rewritten since the review ran, the finding may be
   stale → mark `OUT_OF_SCOPE` with reason `stale_after_review`.

2. **Judge claim accuracy.** Does the cited code actually exhibit the
   issue the finding describes?
   - For CAT-1 (Trivial Pass): does the test body really lack assertions,
     or contain only `pass`/`assert True`?
   - For CAT-2 (Tests Nothing Real): is the constructor really bypassed
     with `__new__`, or is the code path really not exercising
     production logic? Check whether at least *some* assertions exercise
     real behavior — partial-value tests still earn MAJOR not CRITICAL.
   - For CAT-3 (Dead Test Code): is the file really unused / a leftover
     repro script with no unique coverage? Cross-check that the claimed
     "covered elsewhere" tests actually exercise the same path
     (grep the symbol; do not trust the finding's claim).
   - For CAT-4 (Duplicate Testing): are the two cited tests really
     duplicates, or do they exercise different code paths through the
     same surface? The 2026-05-02 reference run had a DISPUTED finding
     (`test_ship_stats_cargo_storage`) where the "duplicate" tested a
     different pipeline stage — apply the same skepticism.
   - For CAT-5 (Fixture Bloat): is the fixture really expensive and
     re-created per test? Function-scope on a cheap fixture is fine.
   - For CAT-6 (Mocking Brittleness): does the mock really patch a
     private API or assert a specific call chain that would break on
     refactor? `mock.assert_called_with` on a *public* boundary is
     legitimate.
   - For CAT-7 (Sleep/Latency): is `time.sleep` really being used to
     wait for nondeterministic state, or is it a deliberate latency
     simulation in a benchmark? Latency simulation may be `OUT_OF_SCOPE`.
   - For CAT-8/9 (Complexity / Simplification): is the cited complexity
     really avoidable, or does it exist for a reason (e.g., explicit
     setup for a subtle invariant)?
   - For CAT-10 (Parametrize): are the cited tests really structurally
     identical, or do they have meaningful per-test setup that
     parametrize would obscure?
   - For CAT-11 (Fragile Assertion): is the assertion really tautological
     / coupled to magic numbers, or is the magic number a documented
     boundary value?
   - For CAT-12 (Logic-Heavy): does the test really reimplement
     production logic, or does it use a known-good reference value to
     validate the production calculation?

3. **Judge suggestion appropriateness.** Even if the claim is accurate,
   is the proposed action right?
   - "Delete the test" only when there is no unique coverage — verify by
     grepping for any other test that exercises the same symbol /
     behavior.
   - "Convert to `pytest.skip()`" only when the test is plausibly going
     to be implemented later. Otherwise prefer outright deletion.
   - "Parametrize" only when the cluster has ≥3 truly identical members.
     Two tests is rarely worth a parametrize.
   - "Rescope fixture to module/session" only when the fixture is
     read-only or can be safely shared. Mutable fixtures must stay
     function-scope.
   - "Extract helper" only when the duplication is identical or
     near-identical, not when the tests share *theme* but diverge on
     setup.

4. **Cluster-specific checks (APC/DUP/HLP only).**
   - APC-001 (`__new__` bypass): for each file in the cluster, confirm
     that **all** widget-instantiating tests use the `__new__` pattern,
     not just one. If only some do, the cluster's scope for that file is
     `partial` → mark `NEEDS_REWORK` with the partial scope noted.
   - APC-002 (`inspect.getsource`/`inspect.signature`): confirm the test
     really tests source text, not behavior.
   - DUP-NNN: open both cited test files; confirm the tests are
     equivalent in behavior, not merely shaped similarly.
   - HLP-NNN: confirm the helper function is truly duplicated across the
     cited files (allowing for trivial naming differences), and the
     proposed extraction target is in a sensible shared location.

5. **AST-guard / static-analysis tests.** Any test in
   `tests/**/test_*_boundaries.py`, `test_*_ast_*.py`, or that imports
   `ast` at the top level: these intentionally exercise no production
   code. They guard architectural invariants. If the finding is
   `CAT-2: tests nothing real` and the test is an AST guard, mark
   `OUT_OF_SCOPE` with reason `ast_guard_intentional` — the reviewer's
   own SHARD report often acknowledges this with "Suggestion: Keep
   as-is".

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — claim and suggestion both accurate. Carries into the
  project's phase checklist.
- **`NEEDS_REWORK`** — issue is real but the suggestion is wrong,
  incomplete, or risky. Provide an adjusted suggestion. Carries into the
  project's phase checklist with the **adjusted** suggestion.
- **`REJECTED`** — claim is wrong (false positive). Provide concrete
  contrary evidence (file:line, grep result, etc.). **Does not** enter
  the project; recorded in `findings/verification_report.md`.
- **`OUT_OF_SCOPE`** — claim is technically correct but should not be
  acted on (AST guard, intentional smoke test, deliberate latency
  simulation, stale-after-review). Provide rationale. **Does not** enter
  the project; recorded in `findings/verification_report.md`.

Each verdict must include one short evidence line. No verdict without
evidence.

### Where agents write

Each subagent writes its results to
`.agent_reports/<review-name>/verification_<wave>_<agent>.md` and returns
a summary in its tool reply (verdict counts + the
`(id, verdict, evidence, adjusted_suggestion?)` list). The orchestrator
aggregates all 15 reports (5 waves × 3 agents, minus the wave-5 idle
slot) into a single working buffer keyed by `(shard, claim_id)` for
Phase D.

---

## Phase D: Build the Three Projects

### Step 1 — Allocate the verified items to priority tiers

Group all `VERIFIED` and `NEEDS_REWORK` items (NEEDS_REWORK carries the
adjusted suggestion) by priority tier:

| Tier | Categories | Title format |
|------|------------|--------------|
| P0 | CAT-1, CAT-2, CAT-3 | `Test review P0 dead-trivial cleanup <YYYY-MM-DD>` |
| P1 | CAT-4, CAT-5, CAT-6, CAT-7 + all APC/DUP/HLP | `Test review P1 brittle-bloated remediation <YYYY-MM-DD>` |
| P2 | CAT-8, CAT-9, CAT-10, CAT-11, CAT-12 | `Test review P2 opportunistic polish <YYYY-MM-DD>` |

If a tier ends up with zero items after verification, **skip that tier
entirely** — do not create the project. Print which tier(s) you skipped
and why in the Phase F hand-off.

### Step 2 — Create each project skeleton

Call the canonical script three times **in sequence** (not in parallel —
the script reads/writes `projects_index.md`):

```bash
python Projects/scripts/create_project.py "Test review P0 dead-trivial cleanup <YYYY-MM-DD>"
python Projects/scripts/create_project.py "Test review P1 brittle-bloated remediation <YYYY-MM-DD>"
python Projects/scripts/create_project.py "Test review P2 opportunistic polish <YYYY-MM-DD>"
```

Capture each assigned `PROJ-NNN` from stdout. The IDs are typically
consecutive (e.g. PROJ-320, PROJ-321, PROJ-322) but the script's
filesystem-aware allocator handles any gaps.

### Step 3 — Decide phases per project

Group each project's items by category and create a phase **only** when
it has at least one item. Phase ordering inside each project (lowest
risk first):

**P0 project phases:**

| Phase | Category | Why |
|-------|----------|-----|
| 1 | CAT-1 Trivial Pass | Outright deletes / `pytest.skip` conversions |
| 2 | CAT-2 Tests Nothing Real | Larger deletes / rewrites of bypass-init tests |
| 3 | CAT-3 Dead Test Code | Whole-file deletes (repro scripts, empty placeholders) |

**P1 project phases:**

| Phase | Category | Why |
|-------|----------|-----|
| 1 | CAT-4 Duplicate Testing | Per-pair consolidation, easy signal |
| 2 | CAT-5 Fixture Bloat | Fixture rescoping, easy verification |
| 3 | CAT-6 Mocking Brittleness | Per-test mock surface adjustments |
| 4 | CAT-7 Sleep/Latency | Replace `time.sleep` with deterministic waits |
| 5 | APC-001/002/003 cluster remediation | Cross-file structural patterns |
| 6 | DUP/HLP consolidation | Cross-shard helper extraction |

**P2 project phases:**

| Phase | Category | Why |
|-------|----------|-----|
| 1 | CAT-9 Simplification | Smallest deltas first |
| 2 | CAT-8 Needless Complexity | Reduce nesting, flatten patches |
| 3 | CAT-10 Parametrize | Cluster consolidations |
| 4 | CAT-11 Fragile Assertion | Per-assertion fixes |
| 5 | CAT-12 Logic-Heavy | Replace reimplemented logic with reference values |

If a phase has no items, drop it entirely (do not list in `plan.md`, do
not create a checklist file). Phase numbers stay in the order shown above
but skip gaps if needed (e.g. if CAT-7 has no items in P1, the next
phase after CAT-6 is APC, numbered 4 not 5).

### Step 4 — Rewrite each project's `plan.md`

Replace the template with:

- Title `# PROJ-NNN: Test review <P0|P1|P2> <subtitle> <YYYY-MM-DD>`.
- Keep the two `> WORKING / STOPPING` reminder banners.
- **Quick Status table** with one row per existing phase, linking to the
  corresponding `phase_N_checklist.md`.
- **Current State** block initialised: active phase = Phase 1 of the
  listed phases, Last Action = "Project created from
  `<review-dir-name>` after independent verification", Next Action =
  "Begin Phase 1 tasks", Blockers = "None".
- **Overview**: one paragraph naming the source review, the priority
  tier, the count of verified items, and the review's claimed
  reclaimable LOC for those items.
- **Goals**: one bullet per phase ("Delete N CAT-1 trivial-pass tests",
  "Rescope M CAT-5 fixtures", etc.).
- **Scope**:
  - `In:` lists the categories included.
  - `Out:` explicitly lists the other priority tiers' categories
    ("CAT-4..7 categories — see PROJ-NNN+1 (P1 project)" etc.), plus
    "Anything OpenCode tagged DISPUTED or INCONCLUSIVE", plus
    "Anything Claude's verification rejected or marked out-of-scope
    (see `findings/verification_report.md`)".
- **Key Files** table: top ~10 files touched in this project (sorted by
  item count).
- **Related Documents** links to `design.md`, `decisions.md`,
  `findings/verification_report.md`, and `findings/source_review.md`.
- Keep the existing `## Verification` checklist.

### Step 5 — Create one `phase_N_checklist.md` per listed phase

Use the `PHASE_TEMPLATE` format from
`Projects/scripts/create_project.py:126-158` (the same one the initial
`phase_1_checklist.md` already follows). For each phase:

- **Status:** `Not Started`.
- **Objective:** category-specific. Examples:
  - "Delete or convert to `pytest.skip` the N verified CAT-1 trivial-pass
    tests identified by review `<review-dir-name>`."
  - "Rescope the M verified CAT-5 expensive fixtures to module/session
    scope."
  - "Replace `__new__` bypass-init pattern in the K files of APC-001
    with real construction + mocked dependencies."
- **Tasks section:** one `### Task N.M` per file (or per
  duplication-pair / per cluster member). Group multiple findings in the
  same file under one task to keep the checklist scannable. Each task
  has:
  - `**File:** `<path>`` (single file per task; for cluster items the
    cluster ID goes in the task title and one task per file).
  - `**Tests:** <specific pytest path>` — at minimum the file itself
    (e.g. `pytest tests/unit/ai/test_ai.py`); fall back to
    `Run `pytest tests/ --testmon`` only if the change is wider than one
    test file.
  - One checkbox per finding being acted on, naming the test (or test
    class), the line range, and the action. Examples:
    - `[ ] Delete `test_production_progress` (lines 61-76, 16 LOC) — body is comments + `pass`, zero assertions.`
    - `[ ] Convert `test_navigate_to_rotates_ship` (lines 124-136) to `@pytest.mark.skip(reason="Visual verification only")` — no automated regression value.`
    - `[ ] Rewrite `RacePortraitGallery` tests (lines 57-320, ~10 tests) to use real construction with mocked `pygame_gui` — current `__new__` bypass exercises no constructor logic. **APC-001 cluster member.**`
    - `[ ] Parametrize the 5 missing-field default tests (lines 49-77) into one `@pytest.mark.parametrize("key,default", ...)` block.`
    - `[ ] Extract `make_mock_ship()` helper from test_*.py:* into `tests/_helpers/ship_factory.py` and update 5 call sites. **HLP-001 cluster.**`
  - For NEEDS_REWORK items, the checkbox carries Claude's **adjusted**
    suggestion, not OpenCode's original. Add a one-line note immediately
    after the checkbox: `_(verification adjusted from review's
    "<original suggestion summary>" — see verification_report.md)_`.
  - Final checkbox per task: `[ ] Verify: `pytest <test-path>` passes;
    LOC delta ≈ <expected from `loc_affected` sum>`.
- **Phase Completion Checklist:** copy the template's standard block
  verbatim.
- **Review-source line at the bottom:** `_Source review:
  `Reviews/results/<review-dir-name>/`. See `findings/source_review.md`
  for the link._`

**No checklist may be empty or contain placeholder text.** If you find
yourself writing "TBD", "fill in", or "[Task Name]", you have a bug —
either the phase has no verified items (drop it from `plan.md` too) or
you have not finished the work.

### Step 6 — Rewrite each project's `manifest.md`

Replace the template with the file table. Every file referenced in any
`phase_N_checklist.md` must appear here, and every file in `manifest.md`
must be referenced by at least one checklist. Columns: `File`, `Type`
(`Test` for everything in `tests/`, occasionally `Production` if a
finding's adjusted suggestion touches a `game/_helpers/` extraction
target), `Notes` (one-line action summary).

### Step 7 — Update each project's `design.md`

Add a `## Source Test Review` block at the top with:
- The review directory path.
- Item counts: `OpenCode CONFIRMED candidates for this tier: <N> |
  Independently verified: <V> | Needs-rework: <NR> | Rejected: <R> |
  Out-of-scope: <O>`.
- Claimed total LOC vs. verified-only LOC (sum of `loc_affected` across
  V + NR items in this tier).
- One-sentence summary of categories included in this tier.

Keep the rest of the template; the implementing phases will fill it
during `/claude-proj-continue`.

### Step 8 — Append to each project's `decisions.md`

Append one row:

```
| <YYYY-MM-DD> | Acted only on findings that passed independent verification of `<review-dir-name>` (P<X> tier) | OpenCode test-review confirms 94% of Phase-1 claims; a third skeptical pass with a different model catches blind spots the OpenCode verifier may share with its Phase-1 reviewer. P<X> tier verification: <V> verified, <NR> needs-rework, <R> rejected, <O> out-of-scope; rejected and out-of-scope items recorded in `findings/verification_report.md` |
```

### Step 9 — Write each project's `findings/verification_report.md`

This is the *full* output of Phase C for items in this project's tier,
organised as:

- Header: source review dir, run date, priority tier, batch summary
  (`<V> verified / <NR> needs-rework / <R> rejected / <O> out-of-scope`
  out of `<N>` OpenCode CONFIRMED candidates for this tier).
- `## Verified` — table: `id | category | severity | file | test_name | suggestion`. (These are the items in the phase checklists.)
- `## Needs Rework` — table per item: `id | original suggestion |
  Claude's adjusted suggestion | rationale`. (These are also in the
  checklists, but with the adjusted suggestion.)
- `## Rejected` — table per item: `id | original claim | contrary evidence
  (file:line) | rationale`. **Each row is a potential bug in the
  test-review skill** — keep this section scannable so the user can feed
  it back later.
- `## Out of Scope` — table per item: `id | claim | reason for not
  acting (e.g. ast_guard_intentional, deliberate_latency_simulation,
  stale_after_review)`.

### Step 10 — Write each project's `findings/source_review.md`

A short pointer file:

```markdown
# Source Test Review

This project was created from the OpenCode test-review at:

`Reviews/results/<review-dir-name>/`
  - [SUMMARY.md](../../../../Reviews/results/<review-dir-name>/SUMMARY.md)
  - [VERIFIED_SHARD_*.md](../../../../Reviews/results/<review-dir-name>/)
  - [CROSS_SHARD.md](../../../../Reviews/results/<review-dir-name>/CROSS_SHARD.md)

Priority tier for this project: **P<X>** (categories: <list>).

Sibling projects from the same review:
- [PROJ-NNN+0](../../PROJ-NNN+0/plan.md) — P0 dead-trivial cleanup
- [PROJ-NNN+1](../../PROJ-NNN+1/plan.md) — P1 brittle-bloated remediation
- [PROJ-NNN+2](../../PROJ-NNN+2/plan.md) — P2 opportunistic polish

See [verification_report.md](verification_report.md) for the
independent re-verification that filtered OpenCode's CONFIRMED claims
before they entered this project's plan.
```

(Adjust the sibling list to reflect only projects that were actually
created — skip any tier that had zero items.)

---

## Phase E: Self-Check Before Finishing

For **each** created project, verify:

- [ ] Every phase listed in `plan.md`'s Quick Status table has a
      corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in",
      `[Task Name]`, or `[Filled during implementation]` left over from
      the template.
- [ ] Every file path in any checklist appears in `manifest.md`, and vice
      versa.
- [ ] The verified-item count in `decisions.md` / `design.md` matches the
      total finding-level checkbox count across all
      `phase_N_checklist.md` files (within a small margin for grouping
      multiple findings under one task).
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist.
- [ ] `findings/verification_report.md` and `findings/source_review.md`
      both exist and are populated.
- [ ] You have not modified anything outside the three new
      `Projects/active_projects/PROJ-NNN/` directories (except
      `projects_index.md`, which `create_project.py` updates).

If any check fails, fix it before reporting completion.

---

## Phase F: Hand-off

Print to the user:

```
Three projects created from <review-dir-name>:

  PROJ-NNN+0 (P0 dead-trivial cleanup)
    Path:               Projects/active_projects/PROJ-NNN+0/
    OpenCode confirmed: <N0>
    Verified by Claude: <V0>  (entered the project plan)
    Needs rework:       <NR0> (entered with adjusted suggestion)
    Rejected:           <R0>  (false positives — see findings/verification_report.md)
    Out of scope:       <O0>  (intentional patterns — see findings/verification_report.md)
    Phases created:     <list, e.g. "1 CAT-1, 2 CAT-2, 3 CAT-3">

  PROJ-NNN+1 (P1 brittle-bloated remediation)
    Path:               Projects/active_projects/PROJ-NNN+1/
    OpenCode confirmed: <N1>
    Verified by Claude: <V1>
    Needs rework:       <NR1>
    Rejected:           <R1>
    Out of scope:       <O1>
    Phases created:     <list>

  PROJ-NNN+2 (P2 opportunistic polish)
    Path:               Projects/active_projects/PROJ-NNN+2/
    OpenCode confirmed: <N2>
    Verified by Claude: <V2>
    Needs rework:       <NR2>
    Rejected:           <R2>
    Out of scope:       <O2>
    Phases created:     <list>

Next steps:
  /claude-proj-continue PROJ-NNN+0
  /claude-proj-continue PROJ-NNN+1
  /claude-proj-continue PROJ-NNN+2
```

If any tier was skipped (zero verified items), surface that explicitly
with the count breakdown so the user can sanity-check.

If `<R>` across all three tiers sums to zero, surface that explicitly —
it may mean Claude's verifier prompt is too lenient. The OpenCode
verifier itself rejects ~6% of Phase-1 claims, so a downstream pass that
finds zero false positives is suspicious, not reassuring.

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the
hand-off print. Implementation happens in
`/claude-proj-continue PROJ-NNN+X` per project.
