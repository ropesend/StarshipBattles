# PROTOCOL 11: Create Project from Shrink-Audit Review
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-audit-shrink` review, independently
re-verify the items the audit calls "verified safe to act on", and create a
new `Projects/active_projects/PROJ-NNN/` containing only the items that
survive that second pass.

The audit's own internal verification has caught false positives in past
runs, but it is still fallible — historical findings have referenced symbols
that turned out to be reachable via JSON-driven dispatch (e.g.
`data/targeting_policies.json`) or registry lookup. **Acting on the audit's
recommendations directly is risky; this protocol exists so cleanup work has
an auditable safety floor before any code is removed.**

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the
> Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** delete any code identified in the audit.
- **Do NOT** modify the source audit report or its `findings/` directory.
- **Do NOT** re-evaluate items the audit already excluded as
  `PRODUCT_DECISION`, `UNCERTAIN`, `false_positive`, `downgraded`, or
  `informational`. Those are out of scope. Verify only what the audit calls
  verified-safe.
- **Do NOT** leave a phase listed in `plan.md` without a populated
  `phase_N_checklist.md`. Skipping a category entirely is fine; an empty
  checklist is not.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to an audit-shrink review directory, e.g.
     `Reviews/results/2026-05-02_184210_audit_shrink/`. Accept absolute or
     relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent
     `*_audit_shrink` directory under `Reviews/results/`.** Sort by the
     timestamp embedded in the directory name (e.g.
     `2026-05-02_184210_audit_shrink`); the lexicographic newest is the
     intended choice. If two or more share the same timestamp, fall back
     to filesystem mtime. Print the chosen path on its own line
     (`Auto-selected most recent audit: <path>`) so the user can see
     which audit is being processed, then continue without prompting.
   - If no `*_audit_shrink` directories exist at all, stop and tell the
     user — do not invent a path or fall back to a non-shrink review.

2. **Validate the structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists and contains agent reports.
   - `<audit_dir>/raw/` exists.
   If any are missing, stop and surface the discrepancy. Do not invent
   findings from a partial report.

3. **Note the audit date.** Extract the date from the directory name (or
   from the report's "## YYYY-MM-DD" header) — it goes into the project
   title in Phase D.

---

## Phase B: Extract the Verified-Safe Bucket

Read `report.md` and every file under `findings/`. Build a normalized list of
candidate items, **keeping only items the audit itself classifies as
verified-safe**.

### Include

- **Section 3 ("Dead Code Inventory (Verified Safe)")** — Tier 1 (Dead
  Files), Tier 2 (Dead Classes), Tier 3 (Dead Functions/Methods), and Tier 4
  (Dead Imports, Parameters, and Unreachable Code). All rows except the
  False Positives subsection.
- **Section 4 (Duplication Clusters)** — only `CRITICAL` and `MAJOR` rows
  that name both duplicate sites and a concrete consolidation target. Skip
  `MINOR` and `INFO` rows unless the audit explicitly recommends action.
- The "Safe LOC" rows of the Shrinkage Scorecard, used as a cross-check on
  totals, not as additional findings.

### Exclude (do NOT verify or include)

- Section 3b (`## 3b. Product Decision Required`) and any item tagged
  `PRODUCT_DECISION`.
- The False Positives subsection of Section 3.
- Section 5 (Complexity Hotspots) — these are usually judgement calls, not
  shrinkage actions.
- Anything tagged `UNCERTAIN`, `false_positive`, `downgraded`, or
  `informational` anywhere in the report.
- Any item lacking a concrete file path or line range — without those, no
  verifier can re-check it.

### Normalize

For each kept item, capture:

| Field | Example |
|-------|---------|
| `id` | `DEEP-02-001`, `C2`, `DUP-X-01` |
| `category` | `dead_function`, `dead_class`, `dead_file`, `dead_import`, `dead_param`, `unreachable_code`, `duplication` |
| `file` | `game/simulation/battle_runner.py` |
| `line_range` | `647-671` (or `null` for whole-file / cross-site items) |
| `symbol` | `_extract_weapon_summaries` (or pair of symbols for duplications) |
| `recommendation` | one short verb phrase from the audit |
| `audit_loc` | LOC the audit claimed would be reclaimed |
| `source_finding` | which `findings/<file>.md` it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per
the `Subagent Report Output` convention in the project's `CLAUDE.md`). It is
disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~3 batches by category and dispatch
**one `Explore` subagent per batch in parallel** (single message, multiple
Agent tool uses). Suggested grouping:

- **Batch 1 — Dead imports / params / unreachable code** (the Tier 4 rows
  and `C*` items). Lowest risk, highest volume.
- **Batch 2 — Dead functions / classes / files** (Tier 1–3). Highest risk;
  these are the actual deletions.
- **Batch 3 — Duplications.** Different verification questions: are both
  sites still present, are they really equivalent, is the proposed
  extraction target free?

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

1. **Reference search.** Re-grep for the symbol name AND the file path stem
   across:
   - `tests/**/*.py`
   - `docs/**/*.md`
   - `data/**/*.json`, `data/**/*.yaml`, `data/**/*.toml`
   - any `*.cfg`, `*.ini`, `*.txt` configuration the project uses
   The audit's verifier already grepped these; if you find a hit it missed,
   that is a `REJECTED` (with the file:line of the hit as evidence).

2. **Dynamic-dispatch search.** Look for patterns that defeat static
   analysis:
   - `getattr(`, `setattr(`, `globals()[`, `locals()[`
   - `__subclasses__`, `__init_subclass__`, decorator-based registries
   - `importlib.import_module`, plugin loaders, entry points
   - String keys matching the symbol name (often used as registry keys)
   - `eval(`, `exec(` (rare but fatal if missed)

3. **`TYPE_CHECKING` guards.** Vulture has historically flagged imports
   inside `if TYPE_CHECKING:` blocks as dead. Confirm the symbol is not
   used as a string annotation at any line of the same file (e.g.
   `def f(x: "RegionClassifier") -> None`). If it is, `REJECTED`.

4. **Context-manager / protocol parameters.** Parameters like `exc_type`,
   `exc_val`, `exc_tb` on `__exit__`, or signature-required parameters of
   abstract methods, are not dead. If the parameter belongs to a method
   that overrides a protocol or magic method, `REJECTED`.

5. **For dead classes specifically.** Check whether any base class or
   parent registers subclasses by name, and whether the class is
   instantiated indirectly (e.g. `cls()` from a registry).

6. **For dead files specifically.** Check for module-level side-effects
   (`@register(...)`, top-level calls), `__init_subclass__` registration,
   and `__init__.py` re-exports.

7. **For duplications specifically.** Confirm:
   - Both sites still exist at the file:line ranges claimed.
   - The two blocks are still equivalent (no recent divergence).
   - The proposed extraction target file does not already exist with
     conflicting content.

8. **Recency check.** Run `git log --diff-filter=A --format="%h %s" -- <file>`
   on dead files / dead classes. If the file was added very recently (last
   ~30 days) or its add-commit message mentions "planned", "infra", "stub",
   or "TODO", classify `UNCERTAIN` rather than `VERIFIED`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — no contrary evidence; safe to include in the project.
- **`REJECTED`** — concrete evidence the item is not actually dead /
  duplicate. Provide the file:line of the contrary evidence.
- **`UNCERTAIN`** — ambiguous: dispatch pattern that could go either way,
  recently added, or evidence is borderline. Provide the question a human
  needs to answer.

Each verdict must include one short evidence line. No verdict without
evidence.

### Where agents write

Each subagent writes its results to
`.agent_reports/<audit-name>/verification_<batch>.md` and returns a
summary in its tool reply. You aggregate the three reports into a single
working buffer for Phase D.

---

## Phase D: Build the Project

1. **Create the project skeleton** with the canonical script:
   ```bash
   python Projects/scripts/create_project.py "Audit-shrink cleanup <YYYY-MM-DD of audit>"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`,
   `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and
   `findings/`. **Do not create these files manually.** Capture the
   assigned `PROJ-NNN` from the script's stdout.

2. **Decide which phases exist.** Group `VERIFIED` items by category and
   create a phase **only** if it has at least one verified item. Phase
   ordering (lowest risk first):

   | Phase | Categories | Why |
   |-------|------------|-----|
   | 1 | `dead_import`, `dead_param`, `unreachable_code` | Trivial deletions, fastest signal |
   | 2 | `dead_function` | Per-symbol removals, easy to test |
   | 3 | `dead_class`, `dead_file` | Larger blast radius, may touch `__init__.py` re-exports |
   | 4 | `duplication` | Requires extraction + caller updates |

   If a phase has no verified items, skip it entirely (do not list it in
   `plan.md` and do not create a checklist file).

3. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Audit-shrink cleanup <YYYY-MM-DD>`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to the
     corresponding `phase_N_checklist.md`.
   - **Current State** block initialised: active phase = Phase 1 of the
     listed phases, Last Action = "Project created from
     `<audit-dir-name>` after independent verification", Next Action =
     "Begin Phase 1 tasks".
   - **Overview**: one paragraph naming the source audit, the count of
     verified items, and the audit's claimed reclaimable LOC for those
     items.
   - **Goals**: one bullet per phase ("Remove N dead imports/params",
     "Remove M dead functions", etc.).
   - **Scope**: `In:` lists the categories included; `Out:` explicitly
     lists "Anything the audit tagged PRODUCT_DECISION, UNCERTAIN, or
     false_positive (see `findings/verification_report.md`)" and "Complexity
     hotspots from the source audit".
   - **Key Files** table: the top ~10 files touched (sorted by item count).
   - **Related Documents** links to `design.md`, `decisions.md`, and the
     two findings files created below.
   - Keep the existing `## Verification` checklist.

4. **Create one `phase_N_checklist.md` per listed phase.** Use the
   `PHASE_TEMPLATE` format from
   `Projects/scripts/create_project.py:126-158` (the same one
   `phase_1_checklist.md` already follows). For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Remove the N verified dead
     imports and unused parameters identified by audit
     `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per file (or per
     duplication-pair). Group multiple symbols in the same file under one
     task to keep the checklist scannable. Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Tests:** <specific pytest path or "Run \`pytest tests/ --testmon\`">`.
     - One checkbox per symbol/line being acted on, naming the symbol and
       the line range — the protocol's "Bad / Good Example" rule from
       `01_initialize_project.md` applies. Examples:
       - `[ ] Remove unused import \`MASS_MOON\` (line 23)`
       - `[ ] Remove function \`_extract_weapon_summaries\` (lines 647-671, 25 LOC)`
       - `[ ] Extract duplicated \`_get_race_config\` to \`game/strategy/services/race_resolver.py\` and update both call sites in \`happiness_engine.py:130-159\` and \`population_engine.py:164-193\``
     - For duplications: include a checkbox for the extraction, a checkbox
       per call site update, and a checkbox to delete the original blocks.
     - Final checkbox: `[ ] Verify: pytest passes; LOC delta ≈ <expected>`.
   - **Phase Completion Checklist:** copy the template's standard block
     verbatim.
   - **Audit-source line at the bottom:** `_Source audit:
     `Reviews/results/<audit-dir-name>/`. See
     `findings/source_audit.md` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find
   yourself writing "TBD", "fill in", or "[Task Name]", you have a bug —
   either the phase has no verified items (drop it from `plan.md` too) or
   you have not finished the work.

5. **Rewrite `manifest.md`.** Replace the template with the file table.
   Every file referenced in any `phase_N_checklist.md` must appear here, and
   every file in `manifest.md` must be referenced by at least one checklist.
   Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`),
   `Notes` (one-line action summary).

6. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Item counts: `Audit verified-safe candidates: <N> | Independently
     verified: <V> | Rejected: <R> | Uncertain: <U>`.
   - Claimed total LOC vs. verified-only LOC.
   Keep the rest of the template; the populating phases will fill it during
   implementation.

7. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Acted only on findings that passed independent verification of `<audit-dir-name>` | Audit-shrink reports have produced false positives in past runs (e.g. `_eval_least_armor_rule` reachable via `data/targeting_policies.json`); rejected and uncertain items recorded in `findings/verification_report.md` |
   ```

8. **Write `findings/verification_report.md`.** This is the *full* output
   of Phase C, organised as:
   - Header: source audit dir, run date, batch summary
     (`<V> verified / <R> rejected / <U> uncertain` out of `<N>` audit
     verified-safe candidates).
   - `## Verified` — table of verified items (id, file, symbol, recommendation).
   - `## Rejected` — table per item: id, original audit recommendation,
     contrary-evidence file:line, one-line rationale. **Each row is a
     potential bug in the audit-shrink skill** — keep this section
     scannable so the user can feed it back later.
   - `## Uncertain` — table per item: id, the specific question a human
     needs to answer, and the recommended next step.

9. **Write `findings/source_audit.md`.** A short pointer file:
   ```markdown
   # Source Audit

   This project was created from the audit-shrink review at:

   `Reviews/results/<audit-dir-name>/`
     - [report.md](../../../../Reviews/results/<audit-dir-name>/report.md)
     - [findings/](../../../../Reviews/results/<audit-dir-name>/findings/)

   See [verification_report.md](verification_report.md) for the
   independent re-verification that filtered the audit's claims before
   they entered this project's plan.
   ```

---

## Phase E: Self-Check Before Finishing

Before printing the summary, verify:

- [ ] Every phase listed in `plan.md`'s Quick Status table has a
      corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in",
      `[Task Name]`, or `[Filled during implementation]` left over from the
      template.
- [ ] Every file path in any checklist appears in `manifest.md`, and vice
      versa.
- [ ] The verified-item count in `decisions.md` / `design.md` matches the
      total checkbox count across all `phase_N_checklist.md` files (within
      a small margin for grouping).
- [ ] No `REJECTED` or `UNCERTAIN` items leaked into a checklist.
- [ ] You have not modified anything outside
      `Projects/active_projects/PROJ-NNN/` (except `projects_index.md`,
      which `create_project.py` updates).

If any check fails, fix it before reporting completion.

---

## Phase F: Hand-off

Print to the user:

```
Project PROJ-NNN created from <audit-dir-name>.

  Path:               Projects/active_projects/PROJ-NNN/
  Audit candidates:   <N>  (verified-safe rows from the audit)
  Independently OK:   <V>  (entered the project plan)
  Rejected:           <R>  (false positives — see findings/verification_report.md)
  Uncertain:          <U>  (need human judgement — see findings/verification_report.md)

  Phases created:     <list, e.g. "1 imports/params, 2 functions, 4 duplications">

Next step:
  /claude-proj-continue PROJ-NNN
```

If `<R>` is zero, surface that explicitly — it may mean the verifier prompt
is too lenient (the audit's own internal verifier flagged false positives in
the 2026-05-02 run, so a downstream skeptical pass that finds none is
suspicious, not reassuring).

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off
print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
