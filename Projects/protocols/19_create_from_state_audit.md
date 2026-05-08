# PROTOCOL 19: Create Project(s) from State Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-state-audit` review, independently re-verify every actionable finding against current source, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **singleton-or-mechanism** rather than severity — containing every item that survives the third pass.

OpenCode's state-audit already runs an internal verifier (`findings/verification.md`) over CRITICAL findings. That pass is rigorous but shares blind spots with the Phase-1 reviewers (same prompt, same code-reading angle). **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** consolidate singletons, rewrite class-level defaults, strip `global` keywords, or otherwise apply fixes.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/verification.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** promote items the audit's own scope rules pre-filter out — module-level ALL_CAPS constants, lazy caches with documented invalidation, and `random.Random(seed)` per-instance usage are all infrastructure, not state bugs.
- **Do NOT** drop findings on the basis of severity. CRITICAL, MAJOR, and MINOR all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume an `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` directory. This protocol is state-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a state-audit directory, e.g. `Reviews/results/2026-05-04_113022_state-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_state-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent state-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_state-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_state-audit`. If the user passed an `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` path, abort with: `Wrong audit type — claude-proj-from-state-audit only consumes *_state-audit/ directories. Use the matching skill for that audit type instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `state_review_*.md`.
   - `<audit_dir>/raw/manifest.json` exists.
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_113022_state-audit` → `2026-05-04`) — it goes into project titles in Phase E.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities are kept.** OpenCode's `findings/verification.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Source files to read

- `<audit_dir>/report.md` — executive summary, scorecard, divergence map, remediation plan.
- `<audit_dir>/findings/state_review_01.md` through `state_review_04.md` — per-shard deep reviews.
- `<audit_dir>/findings/state_divergence_cross_shard.md` — cross-layer singleton divergence map.
- `<audit_dir>/findings/verification.md` — audit's own internal verifier output (DISPUTED/INCONCLUSIVE items here go OUT_OF_SCOPE).
- `<audit_dir>/raw/singleton_sites.json` (and per-shard `singleton_sites_{01..04}.json`) — every `_default_*`, `_instance`, `_singleton` definition.
- `<audit_dir>/raw/module_mutables.json` — module-level dict/list/set assignments.
- `<audit_dir>/raw/global_usages.json` (and per-shard `global_usages_{01..04}.json`) — every `global` keyword with function context.
- `<audit_dir>/raw/class_mutable_defaults.json` — class-level mutable parameter defaults.
- `<audit_dir>/raw/random_seed_sites.json` — `random.seed()` calls outside per-battle RNG.
- `<audit_dir>/raw/ctx_usage_ratio.json` (and per-shard `ctx_usage_ratio_{01..04}.json`) — `get_default_xxx()` vs `ctx.xxx` access ratio per file.

### Include

- **`report.md` §2 State Hygiene Scorecard** — every category row with concrete counts and follow-through into the per-shard tables.
- **`report.md` §3 Singleton Divergence Risk Map** — every singleton flagged HIGH/MEDIUM with file:line evidence.
- **`report.md` §4 ApplicationContext Access Pattern Progress** — per-layer access-pattern divergence flags (a layer using both `ctx.X` and `get_default_X()` is a finding).
- **`report.md` §5 Prioritized Remediation Plan** — every Critical/Major/Minor row.
- **`findings/state_review_NN.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR item (`ST-NN-NNN` IDs) not already captured in §2–5. Watch for shard reports listing items the executive summary skipped.
- **`findings/state_divergence_cross_shard.md`** — cross-shard singleton-divergence findings, layer-by-layer divergence summary, and stale `set_default_*` bridge functions whose only caller is `ApplicationContext.create_production()`.
- **`raw/*.json`** — concrete file:line lookup, used to hydrate findings missing precise locations.

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/verification.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- **Module-level ALL_CAPS constants** — the audit's "What NOT to Report" list excludes these as intentional and immutable infrastructure.
- **Lazy-loaded caches with proper invalidation** — the audit's documented pattern; out of scope unless invalidation is missing or broken.
- **`random.Random(seed)` per-instance usage** — the preferred Pattern #18 RNG. Only `random.seed()` on the global `random` module is a finding.
- **Module-level registries populated once at import and never mutated** — infrastructure, not state bugs (per the audit's own scope rules).
- **TYPE_CHECKING blocks** — out of scope per the audit.

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `ST-01-001`, `ST-XSHARD-002` |
| `category` | `singleton_divergence`, `module_mutable`, `global_keyword`, `class_mutable_default`, `random_seed`, `stale_bridge` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` |
| `file` | `game/strategy/services/race_registry.py` |
| `line_range` | `42-58` or single line |
| `symbol` | `_default_race_registry` (or `null`) |
| `layer` | `core` / `services` / `simulation` / `strategy` / `ai` / `ui` / `assets` / `engine` / `research` / `unknown` (derived from path prefix) |
| `setter_present` | `yes` / `no` (whether `set_default_*` exists) |
| `getter_count` | dict broken out by access pattern: `{"get_default": N, "ctx": M}` |
| `mutable` | `yes` / `no` (dict/list/set vs int/str) |
| `current_pattern` | `module-level singleton with both accessors`, `[]/{} as default arg`, `global _cache`, etc. |
| `recommended_pattern` | `migrate consumers to ctx.X`, `replace [] default with None + factory`, `remove unused set_default_xxx`, etc. |
| `recommendation` | one short verb phrase from the audit |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `risk` | one-line description of what breaks if not fixed (especially for CRITICAL singleton-divergence and class-default findings) |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

**Before dispatching agents, read `game/context.py` once yourself.** Every singleton-divergence verdict depends on understanding what `ApplicationContext.create_production()` wires up, which `set_default_*` functions exist, and how `ctx.X` properties resolve. Pass a one-paragraph summary of the bridge mechanics in each agent's prompt so they don't have to re-derive it.

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Singleton divergence.** All `singleton_divergence` items (the highest-impact category — every finding requires reading `game/context.py` plus producing and consuming layers). **Verifier must be especially careful here.**
- **Batch 2 — Module mutables + globals.** All `module_mutable` and `global_keyword` items.
- **Batch 3 — Class defaults + RNG.** All `class_mutable_default` and `random_seed` items.
- **Batch 4 — Stale bridges.** All `stale_bridge` items (`set_default_*` functions whose only caller is `ApplicationContext.create_production()`).

If a batch has zero items, skip it.

### Verification checklist (every Explore agent must apply)

For each item in its batch:

#### `singleton_divergence`

1. Open `game/context.py` and locate the `ctx.X` property and the corresponding `set_default_X()` call inside `create_production()`. Confirm both exist.
2. Open the cited definition file. Confirm the `_default_*` module-level variable + `get_default_*()`/`set_default_*()` accessor pair.
3. Search the consuming layers for actual call sites:
   - Layers using only `ctx.X` → fine.
   - Layers using only `get_default_X()` → fine if intentional, but flag as a transition opportunity.
   - **A layer using BOTH patterns in different files** → `VERIFIED` (this is the canonical divergence risk).
   - **A `_default_*` with multiple getters but no setter** (so the singleton is read but never written from `create_production()`) → `VERIFIED` and elevate to CRITICAL if not already.
   - **A `set_default_*` whose only writer bypasses `create_production()`** → `VERIFIED`.
4. If the audit's claim no longer reproduces (e.g. an interim commit migrated all consumers to `ctx.X`) → `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `module_mutable`

1. Open the cited line. Confirm a module-level `dict`/`list`/`set` assignment.
2. Look for ALL_CAPS naming → `OUT_OF_SCOPE` (constant convention).
3. Look for documented invalidation (`invalidate()` method, TTL, explicit clear-on-reload) → `OUT_OF_SCOPE`.
4. If the collection is mutated across multiple files with no invalidation owner → `VERIFIED`.
5. If the collection is populated once at import and never mutated → `OUT_OF_SCOPE`.
6. Verdict: `VERIFIED` / `OUT_OF_SCOPE` / `UNCERTAIN`.

#### `global_keyword`

1. Open the cited line. Confirm the `global` keyword and read the function it sits in.
2. If the global is updating a documented module-level singleton with proper setter discipline → `UNCERTAIN` (defensible but a transition opportunity).
3. If the global is mutating cross-module state with no setter discipline → `VERIFIED`.
4. If the keyword is unused or vestigial (Python doesn't actually need it for the access pattern in the function) → `VERIFIED` (cleanup).
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `class_mutable_default`

1. Open the cited line. Confirm a parameter defaulting to `[]`, `{}`, or `set()` on a method or class-level attribute.
2. Read the method body to determine whether the default is mutated:
   - Default is mutated (`self.x.append(...)`, `the_arg.add(...)`) → `VERIFIED` and CRITICAL — this is a shared-state bug.
   - Default is read but never mutated → `UNCERTAIN` (still violates convention, but no live bug).
   - Default is replaced inside the method (`if x is None: x = []`) → `REJECTED` (Pythonic guard already in place).
3. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `random_seed`

1. Open the cited line. Confirm `random.seed(...)` on the global `random` module (NOT `random.Random(seed)` per-instance — that is the preferred pattern).
2. If the call is inside a per-battle RNG initialization path → `OUT_OF_SCOPE` (deliberate determinism).
3. If the call is at module import or in a non-test path that mutates the global RNG → `VERIFIED`.
4. If the call is in test code → it should not have appeared in the audit (production-only); flag as audit false-positive and `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED` / `OUT_OF_SCOPE`.

#### `stale_bridge`

1. Open the cited `set_default_*` function in its definition file.
2. Search the codebase for callers. The audit claims the only caller is `ApplicationContext.create_production()`.
3. Confirm via the search results:
   - Only `create_production()` calls it → `VERIFIED` (cleanup opportunity, MINOR).
   - Other callers exist → `REJECTED` (still in active use).
4. Verdict: `VERIFIED` / `REJECTED`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (already migrated, false-positive scan, etc.). Provide file:line of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (ALL_CAPS constant, documented lazy cache, deliberate per-battle seed, etc.). Logged but excluded from project.

Each verdict carries one short evidence line. **No verdict without evidence.**

### Where agents write

Each subagent writes to `.agent_reports/<audit-name>/verification_<batch>.md` and returns a summary in its tool reply. The main session aggregates the batch reports into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocols 14/19 from the auto-bundling protocols: instead of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by singleton-or-mechanism:
   - Each distinct `_default_*` singleton with verified divergence findings
     forms its own group (e.g. all RaceRegistry findings together).
   - Each distinct mechanism family forms a group:
       * "class_mutable_default cleanup" (per layer if volume warrants)
       * "module_mutable consolidation" (per layer)
       * "global keyword removal"
       * "random_seed audit"
       * "stale set_default_* removal"
2. Compute volume per group: count of items + summed effort (LOW=1, MEDIUM=3, HIGH=8 weighted).
3. Decide breakdown by total VERIFIED count V:
   - V < 30:         ONE project, all singletons/mechanisms in one bundle.
   - 30 <= V <= 100: 2–3 projects merged by mechanism family:
                       singleton_divergence consolidation         (foundation)
                       module_mutable + global_keyword cleanup    (collection hygiene)
                       class_mutable_default + random_seed +
                         stale_bridge                             (defaults + cleanup)
   - V > 100:        One project per singleton-or-mechanism with >=10 items.
                     Smaller groups attach to the most architecturally adjacent larger one.
4. For each bundle, plan phase ordering:
   - Phase 1: CRITICAL items (singleton-with-no-setter and class-mutable-defaults causing
              shared-state bugs first — these can silently corrupt state)
   - Phase 2: MAJOR items
   - Phase 3: MINOR items (stale bridges, transition opportunities)
   - Drop empty phases.
5. UNCERTAIN items are queued for Step 3.
```

**Note:** Findings touching the same singleton stay together in the same bundle even when their layers differ — the fix conversation is local to that singleton, and splitting it would force the implementer to re-verify the same bridge mechanics twice.

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                          | Singletons / Mechanisms        | Verified | Uncertain | Phases (severities) |
|---|------------------------------------------------|--------------------------------|----------|-----------|---------------------|
| 1 | State hygiene — Consolidate ContextRegistry    | _default_context_registry      |  V1      |  U1       | Critical, Major     |
| 2 | State hygiene — Class-default cleanup strategy | class_mutable_default×N        |  V2      |  U2       | Major, Minor        |
| 3 | State hygiene — Stale bridge removal           | stale_bridge×M                 |  V3      |   0       | Minor               |

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
[bundle 1, item 2 of 3] ST-02-007 — global keyword in TurnEngine._dispatch()
  Layer: strategy | File: game/strategy/engine/turn_engine.py:412
  Verifier note: defensible — updates a module-level cache with a documented setter,
  but the global keyword itself is unused (Python resolves the access without it).
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
   python Projects/scripts/create_project.py "State hygiene — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: State hygiene — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, the singletons/mechanisms covered, and any notable risk callouts (e.g. "includes 2 CRITICAL singleton-divergence items where consumers will silently see different instances").
   - **Goals**: one bullet per phase ("Migrate N consumers of `_default_X` to `ctx.X`", "Replace M class-level mutable defaults with None + factory", "Remove K stale `set_default_*` bridge functions", etc.).
   - **Scope**: `In:` the singletons/mechanisms in this bundle. `Out:` other bundles' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 files touched in this bundle, sorted by item count.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Consolidate the N verified consumers of `_default_context_registry` onto `ctx.context_registry` identified by audit `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per file (group multiple symbols in the same file under one task to keep the checklist scannable). Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Tests:** <pytest path or "Run \`pytest tests/ --testmon\`">`.
     - One checkbox per finding, naming the symbol, line range, current pattern, and target pattern. Examples:
       - `[ ] Migrate \`StrategyGameStateManager.process_turn_action\` (lines 122-128) from \`get_default_race_registry()\` to \`ctx.race_registry\``
       - `[ ] Replace \`def __init__(self, ships=[])\` (line 42) with \`def __init__(self, ships=None)\` + \`self.ships = list(ships) if ships else []\` in \`Squadron\``
       - `[ ] Remove unused \`global _cache\` keyword (line 89) in \`asset_loader.py\` — Python resolves access without it`
       - `[ ] Delete \`set_default_design_role_registry\` (lines 18-22) — only caller was \`ApplicationContext.create_production()\``
     - For CRITICAL singleton-divergence and class-mutable-default findings: include a checkbox for adding a regression test that exercises the shared-state-bug or divergence path — these are the highest-impact items and need test coverage to prevent regression.
     - Final checkbox per phase: `[ ] Verify: pytest passes; no new \`_default_*\` singletons added without matching \`ctx.X\` wiring; no new mutable parameter defaults introduced`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every file referenced in any `phase_N_checklist.md` must appear here, and every file in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`), `Notes` (one-line action summary).

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Singleton/mechanism coverage and severity breakdown.
   - For CRITICAL singleton-divergence and class-default findings: a one-paragraph "Risk Notes" subsection summarizing the silent-corruption / shared-state-bug paths.
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "singleton locality across consumers"> per user direction | Bundling driven by singleton-or-mechanism rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, file, symbol, current pattern, recommended pattern, severity, risk).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence file:line, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## Out of Scope` — table per item: id, why the verifier excluded it (ALL_CAPS constant, documented lazy cache, deliberate per-battle seed, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the state-audit at:

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

10. **Refinement Feedback.** Per `Projects/protocols/15_refinement_feedback.md`, write a proposal back to the originating OpenCode skill. Inputs: `audit_dir`, `source_skill: "ocode-state-audit"`, `audit_name: "state"`, REJECTED findings (with reasons), UNCERTAIN items, audit-missed issues the user flagged during bundling, and the list of `PROJ-NNN` IDs created. Write to `.opencode/skills/ocode-state-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, write a minimal "no refinements suggested this run" proposal and exit. The proposal is for the user to read manually and decide what to merge into `SKILL.md` or `Tools/state_audit/`.

---

## Phase F: Self-Check Before Finishing

Before printing the summary, verify:

- [ ] Every phase listed in each `plan.md`'s Quick Status table has a corresponding `phase_N_checklist.md` file.
- [ ] No checklist is empty; no checklist contains "TBD", "fill in", `[Task Name]`, or `[Filled during implementation]` left over from the template.
- [ ] Every file path in any checklist appears in that project's `manifest.md`, and vice versa.
- [ ] The verified-item count in `decisions.md` / `design.md` matches the total checkbox count across all `phase_N_checklist.md` files (within a small margin for grouping).
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist.
- [ ] Every UNCERTAIN item is either in a checklist (user said Include) or recorded in `verification_report.md` as Excluded/Deferred.
- [ ] Every CRITICAL singleton-divergence and class-mutable-default finding has at least one regression-test checkbox in its phase.
- [ ] The Refinement Feedback proposal has been written to `.opencode/skills/ocode-state-audit/refinement_proposals/`.
- [ ] You have not modified anything outside `Projects/active_projects/PROJ-*/` (except `Projects/projects_index.md`, which `create_project.py` updates, and the refinement-proposals path).
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
    CRITICAL singleton-divergence / class-default findings: <count, with silent-corruption callout if > 0>

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice>
Total deferred (need future audit): <count>
Refinement feedback: .opencode/skills/ocode-state-audit/refinement_proposals/<today>_<basename>.md

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

If any project contains CRITICAL singleton-divergence or class-mutable-default findings, surface them on a separate line: `⚠ <count> CRITICAL state-corruption risks across <N> projects — recommend prioritizing these before MAJOR/MINOR work.`

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print. Implementation happens in `/claude-proj-continue PROJ-NNN`.
