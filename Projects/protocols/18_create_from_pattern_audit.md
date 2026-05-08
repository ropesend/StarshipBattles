# PROTOCOL 18: Create Project(s) from Pattern Audit
**Role:** Skeptical Verifier → Project Architect

**Goal:** Take a completed `ocode-pattern-audit` review, independently re-verify every actionable finding against current source AND against the cited pattern entry in `docs/02_PATTERNS.md`, and create one or more `Projects/active_projects/PROJ-NNN/` directories — bundled by **layer + pattern-area** rather than severity — containing every item that survives the third pass.

OpenCode's pattern-audit already runs an internal verifier (`findings/verification.md`) over CRITICAL findings. That pass is rigorous but shares blind spots with the Phase-1 reviewers (same prompt, same code-reading angle, same pattern-doc reading angle). **A third independent pass with a different model is what makes this protocol auditable.** Do not skip it for time.

Pattern audits are uniquely sensitive to a two-sided drift: code can change while the doc stays still, OR the doc can change while the code stays still. Every verifier in this protocol must read **both** sides before deciding the gap is real.

---

## ⛔ Forbidden Actions

> [!CAUTION]
> This is a PLANNING protocol. You are the Verifier-then-Architect, NOT the Implementer.

- **Do NOT** edit production code, tests, docs, or data files.
- **Do NOT** rewire imports, insert Facade calls, replace `get_default_registry_provider()` lookups, swap `isinstance()` for `TypeGuard`, or otherwise apply fixes.
- **Do NOT** modify `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`, or `docs/03_CONVENTIONS.md` to reconcile drift — that's an implementation step.
- **Do NOT** modify the source audit report or its `findings/`/`raw/` directories.
- **Do NOT** promote items the audit's own `findings/verification.md` already marked DISPUTED or INCONCLUSIVE — those are out of scope.
- **Do NOT** flag Pattern #30 usage as a violation. The docs mark it superseded by #31; the audit explicitly excludes it.
- **Do NOT** flag TYPE_CHECKING-only imports as layer violations — benign by convention.
- **Do NOT** drop findings on the basis of severity. CRITICAL, MAJOR, MINOR, and STRATEGIC (undocumented-pattern) items all enter the candidate set; severity drives **phase ordering inside a project**, not project boundaries.
- **Do NOT** leave a phase listed in any `plan.md` without a populated `phase_N_checklist.md`. Skipping a category entirely is fine; an empty checklist is not.
- **Do NOT** consume a `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` directory. This protocol is pattern-audit only — abort with a clear error if the resolved directory is the wrong type.

---

## Phase A: Resolve and Validate Inputs

1. **Resolve the audit path.**
   - Argument is a path to a pattern-audit directory, e.g. `Reviews/results/2026-05-04_090501_pattern-audit/`. Accept absolute or relative, with or without trailing slash.
   - **If no argument was given, automatically select the most recent `*_pattern-audit` directory under `Reviews/results/`.** Sort by the timestamp embedded in the directory name; the lexicographic newest is the intended choice. Tie-break on filesystem mtime. Print the chosen path on its own line (`Auto-selected most recent pattern-audit: <path>`) so the user can see which audit is being processed, then continue without prompting.
   - If no `*_pattern-audit` directories exist, stop and tell the user. Do not invent a path or fall back to another audit type.

2. **Validate audit-type.** The directory name MUST end with `_pattern-audit`. If the user passed an `*_error-audit/`, `*_type-audit/`, or `*_docs-audit/` path, abort with: `Wrong audit type — claude-proj-from-pattern-audit only consumes *_pattern-audit/ directories. Use claude-proj-from-error-audit, claude-proj-from-type-audit, or claude-doc-audit-apply instead.`

3. **Validate structure.** Confirm all of:
   - `<audit_dir>/report.md` exists.
   - `<audit_dir>/findings/` exists with at least one `pattern_review_*.md` plus `pattern_hunter_cross_shard.md` and `pattern_docs_validator.md`.
   - `<audit_dir>/raw/manifest.json` exists.
   - `<audit_dir>/raw/patterns_toc.json` exists (the parsed Table of Contents that grounds every pattern-number citation).
   If any are missing, stop and surface the discrepancy. Do not invent findings from a partial report.

4. **Note the audit date.** Extract from the directory name (e.g. `2026-05-04_090501_pattern-audit` → `2026-05-04`) — it goes into project titles in Phase E.

5. **Cache `patterns_toc.json` in working memory.** Every finding cites a pattern by number; the TOC is how the verifier confirms "Pattern #5" actually means StrategySessionFacade and not whichever pattern moved into slot 5 after a recent doc edit.

---

## Phase B: Extract the Candidate Set

Read `report.md` and every file under `findings/` and `raw/`. Build a normalized list of candidate items. **All severities are kept** (including STRATEGIC undocumented-pattern items). OpenCode's `findings/verification.md` is consulted only to mark items it disputed as `OUT_OF_SCOPE` — never to filter on severity.

### Include

- **`report.md` §2 Layer Dependency Violations** — every confirmed cross-layer import (excluding TYPE_CHECKING).
- **`report.md` §3 Pattern Adherence Scorecard** — every pattern row whose status is `MINOR_DRIFT` or `STALE` (a `STRONG` row produces no candidate).
- **`report.md` §4 Architecture Drift Findings** — cross-shard pattern-hunter rows (Facade integrity, registry consistency, event-bus fragmentation, CQRS-lite audit, ability-source drift).
- **`report.md` §5 Documentation Accuracy** — every pattern with rating `MINOR_DIFF`, `STALE`, or `WRONG`. Plus undocumented-patterns and dead-pattern-doc rows.
- **`report.md` §6 Naming Collision Register** — every collision row with concrete file:line on both sides.
- **`report.md` §7 LOC Ceiling Violations** — every file over 500 LOC under `game/`.
- **`report.md` §8 Prioritized Architecture Remediation Plan** — every Critical/Major/Minor/Strategic row.
- **`findings/pattern_review_NN.md`** — full per-finding detail for every CRITICAL/MAJOR/MINOR item not already captured in §2–8. Watch for shard reports listing items the executive summary skipped.
- **`findings/pattern_hunter_cross_shard.md`** — cross-shard pattern-erosion findings.
- **`findings/pattern_docs_validator.md`** — doc-drift entries, undocumented patterns, dead pattern docs.
- **`raw/layer_violations.json`, `raw/layer_violations_NN.json`** — concrete `from_layer → to_layer` import lookup, used to hydrate findings missing precise locations.
- **`raw/protocol_registry.json`** — list of Protocol classes + TypeGuard presence; used to hydrate Protocol-bypass findings.
- **`raw/file_size_violations.txt`** — LOC ceiling concrete file paths.
- **`raw/patterns_toc.json`** — pattern-number → pattern-name map (every finding's `pattern_number` field is grounded against this).

### Exclude (mark OUT_OF_SCOPE)

- Anything `findings/verification.md` marked DISPUTED or INCONCLUSIVE. These were already filtered by OpenCode.
- Pattern #30 (Strategy Modal Window — superseded). Documented superseded by #31; the audit's "What NOT to Report" guide already excludes it.
- Layer-violations whose import sits inside an `if TYPE_CHECKING:` block (benign by convention; the audit's own scanner reports these for transparency but they are not actionable).
- `raw/layer_violations.json` rows where `import_type == "documented_bridge"` — explicit late-import bridges with intentional comments are conventionally allowed.
- Naming-collision rows whose two sides are in the same module/package (false positive — same-name local helpers are fine).
- LOC ceiling rows for files outside `game/` (the 500-LOC ceiling is a `game/`-only convention).
- Pattern doc-drift rows where the verifier reads the doc and the code and concludes both are correct (the audit reviewer simply misread one).

### Normalize

For each kept candidate, capture:

| Field | Example |
|-------|---------|
| `id` | `PAT-01-001`, `PAT-XSHARD-007`, `PAT-DOC-012` |
| `category` | `layer_violation`, `registry_di_bypass`, `facade_bypass`, `cqrs_lite_violation`, `protocol_bypass`, `naming_collision`, `config_deviation`, `pattern_doc_drift`, `undocumented_pattern`, `loc_ceiling` |
| `severity` | `CRITICAL` / `MAJOR` / `MINOR` / `STRATEGIC` |
| `file` | `game/strategy/engine/turn_engine.py` |
| `line_range` | `516-524` or single line |
| `symbol` | `TurnEngine.process_turn` (or `null`) |
| `layer` | `core` / `services` / `simulation` / `strategy` / `ai` / `ui` / `assets` / `engine` / `research` / `unknown` (derived from path prefix) |
| `pattern_number` | `3` (Registry DI) / `5` (Facade) / `6` (CQRS-lite) / `null` for items not tied to one pattern (LOC ceiling, naming collision) |
| `pattern_area` | derived label used for bundling: `registry_di`, `facade`, `protocol_typeguard`, `cqrs_lite`, `command_handler`, `ability_aggregation`, `scope_team_routing`, `ability_stat`, `strategy_modal`, `event_bus`, `config_class`, `layer_table`, `naming`, `loc`, `doc_drift`, `undocumented` |
| `current_state` | one short verb-phrase quoting what the code does (e.g. `direct json.load`, `isinstance check on Concrete`, `simulation imports ui.theme`) |
| `recommended_state` | one short verb-phrase quoting the documented contract (e.g. `json_utils.read_json`, `is_concrete TypeGuard`, `accept dependency via context constructor`) |
| `recommendation` | one short imperative from the audit |
| `effort` | `LOW` / `MEDIUM` / `HIGH` if specified, else `null` |
| `risk` | one-line description of what decays if not fixed (especially for CRITICAL pattern-bypass findings — Registry DI bypass re-introduces the very globals PROJ-306 removed) |
| `source_finding` | which `findings/<file>.md` row it came from |

Save the working list to `.agent_reports/<audit-name>/candidates.json` (per the `Subagent Report Output` convention in `CLAUDE.md`). Disposable.

---

## Phase C: Skeptical Re-Verification (parallel Explore subagents)

Group the candidates from Phase B into ~4 batches by category and dispatch **one `Explore` subagent per non-empty batch in parallel** (single message, multiple Agent tool uses). Suggested grouping:

- **Batch 1 — Layer dependency violations.** All `layer_violation` items.
- **Batch 2 — Pattern bypass (architectural).** All `registry_di_bypass`, `facade_bypass`, `protocol_bypass`, `cqrs_lite_violation` items. **Highest impact — verifier must be especially careful and must read the cited pattern in `docs/02_PATTERNS.md` before reading the code.**
- **Batch 3 — Naming + config + LOC.** All `naming_collision`, `config_deviation`, `loc_ceiling` items.
- **Batch 4 — Doc drift + undocumented patterns.** All `pattern_doc_drift`, `undocumented_pattern` items.

If a batch has zero items, skip it.

### Standing instruction for every Explore agent

> Before opening any code file, read the cited pattern entry in `docs/02_PATTERNS.md` (use the `pattern_number` field plus `raw/patterns_toc.json` to find the right heading). The audit's claim is "code violates pattern X" — you cannot judge that without first knowing what X says. If the pattern entry has been edited since the audit ran and the code now matches the new entry, the finding is `REJECTED` (drift was in the doc, not the code, and the doc has caught up).

### Verification checklist (every Explore agent must apply)

For each item in its batch:

#### `layer_violation`

1. Read `docs/01_ARCHITECTURE.md` layer dependency table. Confirm `(from_layer, to_layer)` is forbidden.
2. Open the cited `file:line`. Confirm the import is present.
3. Determine import type:
   - Inside an `if TYPE_CHECKING:` block → `OUT_OF_SCOPE`.
   - Late import with a `# Intentional bridge:` comment → `UNCERTAIN` (defensible, but worth user judgement on whether the bridge is still needed).
   - Direct import at module scope → `VERIFIED`.
4. Verdict: `VERIFIED` / `OUT_OF_SCOPE` / `UNCERTAIN` / `REJECTED` (if the import has been removed since the scan).

#### `registry_di_bypass` (Pattern #3)

1. Read Pattern #3 in `docs/02_PATTERNS.md`. Confirm the contract: simulation/strategy code receives the registry via DI; `get_default_registry_provider()` is reserved for top-level wiring (app.py, ApplicationContext, Combat Lab bootstrap).
2. Open the cited `file:line`. Confirm a `get_default_registry_provider()` call (or equivalent global lookup) is present in a non-bootstrap location.
3. If the call site is in `game/simulation/` or `game/strategy/` AND not a constructor's default-fallback → `VERIFIED`.
4. If the call site is in `app.py`, `ApplicationContext`, or a Combat Lab `TestRunner.__init__` → `REJECTED` (legitimate top-level wiring).
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `facade_bypass` (Pattern #5)

1. Read Pattern #5 in `docs/02_PATTERNS.md`. Confirm `StrategySessionFacade` is the only UI → Strategy entry.
2. Open the cited UI file. Confirm an import from `game/strategy/data/` or `game/strategy/engine/`.
3. Determine intent:
   - UI imports a typed DTO from `game/strategy/data/` purely for type annotations → `UNCERTAIN` (Pattern #5 doesn't strictly forbid type-only imports; user may want to allow).
   - UI constructs a Strategy data object or invokes engine internals → `VERIFIED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `protocol_bypass` (Pattern #2)

1. Read Pattern #2. Confirm Protocol + TypeGuard is the documented narrowing path.
2. Open the cited `file:line`. Confirm an `isinstance(x, Concrete)` check where a TypeGuard exists in `raw/protocol_registry.json` for the protocol the concrete implements.
3. If a TypeGuard exists and the isinstance is checking the concrete (not the protocol) → `VERIFIED`.
4. If no TypeGuard exists for the relevant protocol → `UNCERTAIN` (the fix may include adding the TypeGuard, which broadens scope; user decides).
5. If the isinstance is against a non-Protocol class hierarchy (e.g. exception types) → `REJECTED`.
6. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `cqrs_lite_violation` (Pattern #6)

1. Read Pattern #6. Confirm the contract: DTOs are immutable, commands return None or an ack, queries return data.
2. Open the cited line. Determine which side is violated:
   - DTO mutation (`dto.field = value` after construction) → `VERIFIED`.
   - Command-handler returning data → `VERIFIED`.
   - Query mutating state → `VERIFIED`.
3. If the "DTO" is actually a working buffer not flowing across a layer boundary → `REJECTED` (CQRS-lite applies to cross-layer flow).
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `naming_collision`

1. Open both cited file:lines. Confirm two distinct definitions share a name across layers.
2. If both are public API → `VERIFIED`.
3. If one is `_private` or `__dunder` → `REJECTED` (collision impossible across import boundaries).
4. If both live inside the same package and the collision is intentional (e.g. a Protocol and its default impl) → `REJECTED`.
5. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `config_deviation` (Pattern #12)

1. Read Pattern #12. Confirm the contract for the relevant config-class flavor (core plain class vs strategy `DEFAULT_*` + `_load_from_json` vs json_utils-loaded).
2. Open the cited config class. Confirm the deviation:
   - `@dataclass` on a class Pattern #12 says is plain → `VERIFIED`.
   - Direct `json.load(open(path))` instead of `json_utils.read_json(path)` → `VERIFIED`.
   - Strategy config without the documented `DEFAULT_*` fallback dict → `VERIFIED`.
3. If the config class is intentionally outside Pattern #12's scope (e.g. a transient runtime cache) → `REJECTED`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `pattern_doc_drift`

1. Read both: the pattern entry in `docs/02_PATTERNS.md` AND every cited implementation file.
2. Decide which side is wrong:
   - Doc describes APIs / file paths / class names that no longer exist → `VERIFIED` (doc-side fix needed).
   - Code disagrees with a doc entry that is itself accurate → `VERIFIED` (code-side fix needed).
   - Doc and code agree, the audit reviewer simply misread one → `REJECTED`.
3. Capture which side fixes resolve to in the candidate's `recommendation` field — this drives whether the project phase touches code or `docs/02_PATTERNS.md`.
4. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `undocumented_pattern`

1. Read every cited usage site. Confirm the pattern recurs in 3+ places (the audit's bar for promoting an undocumented pattern).
2. Read `docs/02_PATTERNS.md` end-to-end. Confirm no existing pattern already covers it (the audit reviewer may have missed an existing entry).
3. If the recurrence is real and uncovered → `VERIFIED` (STRATEGIC severity; doc-add work).
4. If 1–2 usages only → `REJECTED` (not enough to justify a pattern entry).
5. If an existing pattern already covers it → `REJECTED`.
6. Verdict: `VERIFIED` / `REJECTED` / `UNCERTAIN`.

#### `loc_ceiling`

1. Open the cited file. Confirm LOC > 500.
2. If the file is under `game/` and the LOC count is current → `VERIFIED`.
3. If the file is in `tests/`, `Tools/`, or `combat_lab/` → `REJECTED` (ceiling is `game/`-only per `CLAUDE.md`).
4. Verdict: `VERIFIED` / `REJECTED`.

### Verdict per item

Each agent returns one of:

- **`VERIFIED`** — survives re-verification; eligible for project inclusion.
- **`REJECTED`** — counter-evidence found (already fixed, false-positive scan, scope-mismatch). Provide file:line of contrary evidence.
- **`UNCERTAIN`** — ambiguous. Surface for user judgement in Phase D. Provide the question a human needs to answer.
- **`OUT_OF_SCOPE`** — verifier confirmed the item is a non-issue (TYPE_CHECKING import, Pattern #30, in-package naming match). Logged but excluded from project.

Each verdict carries one short evidence line. **No verdict without evidence.**

### Where agents write

Each subagent writes to `.agent_reports/<audit-name>/verification_<batch>.md` and returns a summary in its tool reply. The main session aggregates the batch reports into a working buffer for Phase D.

---

## Phase D: Interactive Bundling

This is what differentiates protocol 18 from protocols 11/12: instead of a fixed project shape, the user shapes the bundling.

### Step 1 — Compute a default bundling proposal

```
1. Group VERIFIED candidates by (`layer`, `pattern_area`).
2. Compute volume per cell: count of items + summed effort (LOW=1, MEDIUM=3, HIGH=8 weighted).
3. Decide breakdown by total VERIFIED count V:
   - V < 30:         ONE project, all (layer, pattern_area) cells in one bundle.
   - 30 <= V <= 100: 2–3 projects. Merge cells by architectural proximity. Suggested merges:
                       Registry DI + Facade in simulation+strategy   (cross-layer architectural)
                       Protocol bypass + naming + config in shared layers (typing + conventions)
                       Doc drift + undocumented patterns + LOC      (documentation + hygiene)
   - V > 100:        One project per (layer, pattern_area) cell with >=10 items.
                     Smaller cells attach to the most architecturally adjacent larger one.
4. For each bundle, plan phase ordering:
   - Phase 1: CRITICAL items (Registry DI bypass, Facade bypass, layer violations not TYPE_CHECKING)
   - Phase 2: MAJOR items (CQRS-lite, Protocol bypass, naming collisions, undocumented patterns recurring 3+ places)
   - Phase 3: MINOR items (config deviations, pattern doc drift, LOC ceiling)
   - Phase 4: STRATEGIC items (undocumented-pattern doc-adds, dead-pattern-doc cleanup)
   - Drop empty phases.
5. UNCERTAIN items are queued for Step 3.
```

**Note 1:** Cross-shard pattern-hunter findings (`facade_bypass`, `event_bus_fragmentation`, etc.) are placed in the bundle owning the **bypass site** (UI for Facade bypass; whichever layer hosts the duplicated event bus, etc.). This keeps the fix conversation local to one layer.

**Note 2:** A `pattern_doc_drift` finding fixes either code or `docs/02_PATTERNS.md`. When the fix is doc-side, prefer placing it in the same bundle as related code-side work for the same pattern — that way the project's design.md can describe the doc + code fix as one coherent reconciliation.

### Step 2 — Present proposal to user

Print one concise table:

```
Proposed projects from <audit-dir>:

| # | Title                                              | Layers/Areas              | Verified | Uncertain | Phases (severities)        |
|---|----------------------------------------------------|---------------------------|----------|-----------|----------------------------|
| 1 | Pattern conformance — Registry DI + Facade in sim  | sim,strategy,ui · DI,Fac. |  V1      |  U1       | Critical, Major            |
| 2 | Pattern conformance — Doc drift + undocumented     | docs · drift,undoc        |  V2      |  U2       | Minor, Strategic           |

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
[bundle 1, item 2 of 3] PAT-02-014 — facade_bypass: UI imports strategy DTO for typing only
  Layer: ui | File: game/ui/screens/strategy/strategy_window_manager.py:42
  Pattern: #5 (StrategySessionFacade)
  Verifier note: type-only import; Pattern #5 doesn't explicitly forbid it.
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
   python Projects/scripts/create_project.py "Pattern conformance — <bundle-summary> (<YYYY-MM-DD of audit>)"
   ```
   This creates `Projects/active_projects/PROJ-NNN/` with `plan.md`, `design.md`, `decisions.md`, `phase_1_checklist.md`, `manifest.md`, and `findings/`. **Do not create these files manually.** Capture the assigned `PROJ-NNN` from stdout.

2. **Rewrite `plan.md`.** Replace the template with:
   - Title `# PROJ-NNN: Pattern conformance — <bundle-summary> (<YYYY-MM-DD>)`.
   - Keep the two `> WORKING / STOPPING` reminder banners.
   - **Quick Status table** with one row per existing phase, linking to its `phase_N_checklist.md`.
   - **Current State** block: active phase = Phase 1, Last Action = `Project created from \`<audit-dir-name>\` after independent verification`, Next Action = `Begin Phase 1 tasks`, Blockers = `None`.
   - **Overview**: one paragraph naming the source audit, the count of verified items in this bundle, the layers + pattern-areas covered, and any notable risk callouts (e.g. "includes 4 CRITICAL Registry DI bypass sites that re-introduce the globals PROJ-306 removed").
   - **Goals**: one bullet per phase ("Eliminate N Registry DI bypass call sites in simulation", "Wrap M UI imports through StrategySessionFacade", "Reconcile K pattern doc-drift entries in docs/02_PATTERNS.md", "Promote 1 undocumented pattern to docs/02_PATTERNS.md", etc.).
   - **Scope**: `In:` the (layer, pattern_area) cells in this bundle. `Out:` other bundles' contents (link by sibling PROJ-NNN if they exist), plus REJECTED and OUT_OF_SCOPE categories ("see `findings/verification_report.md`").
   - **Key Files** table: top ~10 files touched in this bundle, sorted by item count.
   - **Related Documents** links to `design.md`, `decisions.md`, `findings/verification_report.md`, `findings/source_audit.md`, `findings/bundling_decisions.md`, plus a link to the cited entry in `docs/02_PATTERNS.md` for each pattern in scope.
   - Keep the existing `## Verification` checklist.

3. **Create one `phase_N_checklist.md` per listed phase.** Use the `PHASE_TEMPLATE` format from `Projects/scripts/create_project.py:126-158`. For each phase:
   - **Status:** `Not Started`.
   - **Objective:** category-specific (e.g. "Eliminate the N verified Registry DI bypass call sites in simulation/strategy identified by audit `<audit-dir-name>`").
   - **Tasks section:** one `### Task N.M` per file (group multiple symbols in the same file under one task to keep the checklist scannable). Each task has:
     - `**File:** \`<path>\`` (single file per task).
     - `**Pattern:** #<N> (<pattern_name>)` — the pattern entry the fix conforms to.
     - `**Tests:** <pytest path or "Run \`pytest tests/ --testmon\`">`.
     - One checkbox per finding, naming the symbol, line range, current state, and target state. Examples:
       - `[ ] Replace \`get_default_registry_provider()\` (line 47) in \`turn_engine.py\` with constructor-injected \`registry_provider\` per Pattern #3`
       - `[ ] Route \`StrategyWindowManager\` (line 42) to import only via \`StrategySessionFacade\` per Pattern #5`
       - `[ ] Replace \`isinstance(comp, BeamWeapon)\` (line 88) in \`damage_pipeline.py\` with \`is_beam_weapon\` TypeGuard per Pattern #2`
       - `[ ] Convert \`@dataclass\` on \`EconomyConfig\` (lines 12-30) to plain class per Pattern #12`
       - `[ ] Update Pattern #14 entry in \`docs/02_PATTERNS.md\` lines 412-440 to match the live aggregator API in \`game/simulation/abilities/aggregator.py\``
       - `[ ] Promote the recurring \`<undocumented_pattern_name>\` (used in 4 sites) to a new entry in \`docs/02_PATTERNS.md\` after #31`
     - For CRITICAL pattern-bypass findings (Registry DI, Facade, layer violation): include a checkbox for adding a regression test or AST static-guard that prevents re-introduction (PROJ-306's static guard against `get_default_registry_provider` calls in `game/simulation/` is the canonical reference).
     - Final checkbox per phase: `[ ] Verify: pytest passes; relevant pattern-audit static-guard tests added for this phase pass; no new bypass sites re-introduced (re-run \`python Tools/pattern_audit/pattern_audit.py\` and confirm count for this category drops by N)`.
   - **Phase Completion Checklist:** copy the template's standard block verbatim.
   - **Audit-source line at the bottom:** `_Source audit: \`Reviews/results/<audit-dir-name>/\`. See \`findings/source_audit.md\` for the link._`

   **No checklist may be empty or contain placeholder text.** If you find yourself writing "TBD", "fill in", or "[Task Name]", you have a bug — either the phase has no verified items (drop it from `plan.md` too) or you have not finished the work.

4. **Rewrite `manifest.md`.** Replace the template with the file table. Every file referenced in any `phase_N_checklist.md` must appear here, and every file in `manifest.md` must be referenced by at least one checklist. Columns: `File`, `Type` (`Production` / `Test` / `Doc` / `Data`), `Notes` (one-line action summary). `docs/02_PATTERNS.md` appears as a `Doc` row whenever the bundle has any `pattern_doc_drift` or `undocumented_pattern` items.

5. **Update `design.md`.** Add a `## Source Audit` block at the top with:
   - The audit directory path.
   - Bundle counts: `Audit verified: <N> | This bundle: <V> verified, <U> uncertain (resolved), <D> deferred | Project siblings: <list of other PROJ-NNN created in this run>`.
   - Layer + pattern-area coverage and severity breakdown.
   - For CRITICAL pattern-bypass findings: a one-paragraph "Risk Notes" subsection summarizing the architectural-decay path (e.g. "Registry DI bypass at 4 sites means the very globals PROJ-306 removed have re-grown; without an AST static guard the same erosion will recur").
   Keep the rest of the template; populating phases will fill it during implementation.

6. **Append to `decisions.md`** one row:
   ```
   | <YYYY-MM-DD> | Bundled findings from `<audit-dir-name>` by <bundling-rationale, e.g. "layer + pattern-area locality across simulation/strategy"> per user direction | Bundling driven by code relatedness (layer + pattern-area) rather than severity to maximize implementation continuity; full bundling discussion in findings/bundling_decisions.md |
   ```

7. **Write `findings/verification_report.md`.** This is the *full* output of Phase C, organised as:
   - Header: source audit dir, run date, batch summary (`<V> verified / <R> rejected / <U> uncertain / <O> out-of-scope` out of `<N>` candidates).
   - `## Verified` — table of verified items in this bundle (id, file, symbol, pattern_number, current state, recommended state, severity, risk).
   - `## Rejected` — table per item: id, original audit recommendation, contrary-evidence file:line, one-line rationale. **Each row is a potential bug in the audit's own verifier** — keep this section scannable so the user can feed it back later.
   - `## Uncertain (resolved)` — table per item: id, the question the verifier raised, and the user's Phase D Step 3 decision (Include / Exclude / Defer).
   - `## Out of Scope` — table per item: id, why the verifier excluded it (TYPE_CHECKING import, Pattern #30, in-package naming match, etc.).

8. **Write `findings/source_audit.md`.** Pointer file:
   ```markdown
   # Source Audit

   This project was created from the pattern-audit at:

   `Reviews/results/<audit-dir-name>/`
     - [report.md](../../../../Reviews/results/<audit-dir-name>/report.md)
     - [findings/](../../../../Reviews/results/<audit-dir-name>/findings/)
     - [raw/patterns_toc.json](../../../../Reviews/results/<audit-dir-name>/raw/patterns_toc.json)

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
- [ ] No `REJECTED` or `OUT_OF_SCOPE` items leaked into a checklist. No Pattern #30 row is present.
- [ ] Every UNCERTAIN item is either in a checklist (user said Include) or recorded in `verification_report.md` as Excluded/Deferred.
- [ ] Every CRITICAL pattern-bypass finding (Registry DI, Facade, real layer violation) has at least one regression-test or AST static-guard checkbox in its phase.
- [ ] Every checklist task lists the `Pattern: #N` it conforms to (or marks the task as `Pattern: n/a` for naming-collision and LOC items that don't tie to one).
- [ ] You have not modified anything outside `Projects/active_projects/PROJ-*/` (except `Projects/projects_index.md`, which `create_project.py` updates).
- [ ] The source audit directory under `Reviews/results/` is unchanged.
- [ ] `docs/02_PATTERNS.md` is unchanged (doc-drift fixes happen during implementation, not now).

If any check fails, fix it before reporting completion.

---

## Phase G: Hand-off

Print to the user:

```
Created N project(s) from <audit-dir-name>:

  PROJ-NNN — <title>
    Path: Projects/active_projects/PROJ-NNN/
    Verified: V / Uncertain (included): U_in / Rejected: R / Out-of-scope: O
    Phases: <list, e.g. "1 Critical, 2 Major, 3 Minor, 4 Strategic">
    CRITICAL pattern-bypass findings: <count, with architectural-risk callout if > 0>

  PROJ-NNN+1 — <title>
    ...

Bundling rationale: <short summary of how the user chose to slice (layer + pattern-area)>
Total deferred (need future audit): <count>

Next steps (one per project):
  /claude-proj-continue PROJ-NNN
  /claude-proj-continue PROJ-NNN+1
```

If `<R>` is zero, surface that explicitly — the audit's own verifier has produced false positives in past runs, so a downstream skeptical pass that finds none is suspicious, not reassuring.

If any project contains CRITICAL pattern-bypass findings, surface them on a separate line: `⚠ <count> CRITICAL pattern-bypass sites across <N> projects (Registry DI / Facade / layer-violation). Without static-guard tests, these decay silently — recommend prioritizing the Phase 1 work in each project.`

---

## Phase H: Refinement Feedback

Invoke `Projects/protocols/15_refinement_feedback.md` with:

- `audit_dir`: the resolved path from Phase A.
- `source_skill`: `ocode-pattern-audit`.
- `audit_name`: `pattern`.
- `verified_findings`, `rejected_findings`, `uncertain_findings`: the working buffers from Phase C.
- `user_flagged_misses`: any pattern issues the user mentioned during Phase D bundling that weren't in the audit.
- `created_projects`: the list of `PROJ-NNN` IDs from Phase E.

Output goes to `.opencode/skills/ocode-pattern-audit/refinement_proposals/<today>_<basename(audit_dir)>.md`. If both REJECTED and user_flagged_misses are empty, the protocol writes a minimal "no refinements suggested this run" file and exits.

---

## Termination

> [!IMPORTANT]
> ⛔ **STOP HERE** — Do NOT begin implementation in this session.

This protocol session is now COMPLETE. END your response after the hand-off print and refinement-feedback invocation. Implementation happens in `/claude-proj-continue PROJ-NNN`.
