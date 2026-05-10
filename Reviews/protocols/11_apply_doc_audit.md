# PROTOCOL 11: Apply Doc Audit
**Role:** Doc Audit Applier
**Extends:** `00_review_core.md`

**Purpose:** Consume the output of an `ocode-docs-audit` run, **independently re-verify every claim against the current state of the repo**, and apply only the fixes that survive verification. Findings that don't survive verification are logged with their verdict and skipped. The skill never invents documentation prose.

This protocol is paired one-to-one with the `claude-doc-audit-apply` skill. It runs only against doc-audit results — type-audit, error-audit, etc. need their own apply protocols.

---

## Scope

**In:** Apply confirmed fixes from a `Reviews/results/<date>_docs-audit/` directory.

**Out:**
- Generic apply across audit types (this protocol is doc-audit specific).
- Authoring new prose docs from scratch (Tier 3 "create new doc" findings always `DEFERRED`).
- Editing `Projects/projects_index.md`, source code under `game/`, or test code.
- Re-running the OpenCode 7-agent swarm (only the deterministic Phase 1 scanner is re-run).
- `docs/_ignore/` (untouched, per `CLAUDE.md`).

---

## Verdict Model

Every finding gets exactly one verdict before any edit is considered:

| Verdict | Meaning | Action |
|---------|---------|--------|
| `CONFIRMED` | Claim still true; doc still wrong. | Apply fix. |
| `ALREADY-FIXED` | Doc has been corrected since the audit ran. | Log, no edit. |
| `DISPUTED` | Audit misread doc or code; doc is correct. | Log, no edit. |
| `STALE` | Code has moved on; the audit's "actual" no longer matches reality. | Log, no edit. |
| `INCONCLUSIVE` | Cannot verify deterministically. | Log, no edit. |
| `DEFERRED` | Verified gap, but fix scope is project-sized (Tier 3 new-doc). | Log + recommend `claude-proj-start`. |

**"Fully autonomous"** = the protocol applies CONFIRMED findings without prompting and silently logs the others. It does not stop mid-run for approval. The user sees the final summary.

---

## Stable Work-Item IDs

The audit's per-finding template defines IDs like `DOC-G1-001`, but `report.md`'s prioritized plan does not carry them through reliably. This protocol generates its own stable IDs from the prioritized plan position:

```
T<tier>-<row>      # e.g. T0-01, T1-04, T3-26
```

Each work item also retains a back-reference to the source line in `report.md` (e.g. `report.md§9.1 row 4`) so the verification log can be cross-checked against the audit.

---

## Verification Methodology (per claim type)

Each work item is dispatched to exactly one verifier based on its claim type. The verifier reads the actual file/code and renders a verdict.

### 1. Dead reference
Audit claim: "doc cites `game/path/file.py` but file no longer exists."

```
1. Glob original cited path. If exists now → DISPUTED.
2. Read the doc at the cited line. If text already shows the corrected
   path → ALREADY-FIXED.
3. Glob the recommended replacement path. If present → CONFIRMED.
4. Otherwise → INCONCLUSIVE.
```

### 2. Content count / accuracy
Audit claim: "doc says N, actual is M" (exception count, exports, pattern count, etc.).

```
1. Read the cited doc line. If text already matches "actual" → ALREADY-FIXED.
2. Re-derive ground truth from source:
   - Count classes:        Grep `^class \w+` in target file.
   - Count exports:        Read `__all__` from the module init.
   - Count patterns:       Count "## Pattern N:" headings in 02_PATTERNS.md.
   - Other counts:         Use the most direct deterministic check.
3. If re-derived value matches the audit's "actual" → CONFIRMED.
4. If re-derived value matches neither doc nor "actual" → STALE.
```

### 3. Cross-doc consistency
Audit claim: "doc A says X, doc B says Y, contradiction."

```
1. Read both cited locations. Confirm contradiction still exists.
2. For "vs actual runtime" claims (e.g. Python version), run:
       python --version
   to ground-truth the runtime.
3. Identify the doc that disagrees with reality → that doc is the fix target.
   The other doc is left alone.
4. If both docs already agree → ALREADY-FIXED.
5. If both docs disagree with reality → CONFIRMED for both, queue both edits.
```

### 4. PROJ status
Audit claim: "doc references PROJ-XXX as planned/in-progress, but it's Complete."

```
1. Read Projects/projects_index.md, find the PROJ row.
2. Read cited doc line. Verify the mismatch:
   - Doc text claims "planned"/"in progress"/"upcoming"?
   - Index shows Complete or Archived?
3. Both true → CONFIRMED.
4. Either side already updated → ALREADY-FIXED or DISPUTED.
```

### 5. Stale class / symbol
Audit claim: "doc lists `FooAbility` as a class but no such class exists."

```
1. Grep for `^class FooAbility\b` across game/.
2. Audit says "class exists" + grep confirms → DISPUTED.
3. Audit says "class does not exist" + grep returns empty → CONFIRMED.
4. Other combinations → STALE or INCONCLUSIVE depending on context.
```

### 6. Code example issues
Audit claim: "code block in doc imports/calls a symbol that doesn't exist."

```
1. Grep target module for the cited symbol.
2. Symbol absent + audit says it's broken → CONFIRMED.
3. Symbol present → DISPUTED.
```

### 7. Missing documentation gap (Tier 3)
Audit claim: "module X is undocumented, needs new doc / new section."

```
1. Confirm module file still exists and exceeds the 50 LOC threshold.
2. Grep all of docs/ for module mentions. If no hits → gap is real.
3. Verdict: DEFERRED. Always. Autonomous prose authoring is high-risk;
   the protocol logs the verified gap with a recommended follow-up
   (claude-proj-start for systematic backfill, or manual section drafting
   by the user). Never write the doc inline.
```

### 8. Heading / section structure
Audit claim: duplicate heading, stale §N cross-reference, wrong section number.

```
1. Read the cited region of the target doc.
2. Confirm the structural defect (count duplicate H3s, resolve §X reference,
   etc.).
3. If still defective → CONFIRMED.
```

### Default
Any claim that doesn't fit one of the above categories (free-form prose advice, "consider rewording", etc.) → `INCONCLUSIVE`. The protocol does not edit speculatively.

---

## Execution Flow

### Phase 0 — Pre-flight

1. **Resolve target audit dir.**
   - If skill argument is `latest` or absent: glob `Reviews/results/*_docs-audit/`, pick the most recent by name (names sort lexicographically by date+time).
   - Otherwise: treat the argument as either a full directory name or a date prefix; glob and require exactly one match.
   - Verify `report.md` and `findings/` both exist. If not, abort with a clear error.

2. **Idempotency guard.**
   - If `<audit-dir>/applied/summary.md` already exists, abort with: `applied/ already present; pass --force to overwrite`.
   - With `--force`: archive the existing `applied/` to `applied.<UTC-timestamp>/` before continuing.

3. **Working tree state.**
   - Run `git status --short`.
   - If clean: proceed.
   - If dirty: record the existing modifications in `applied/preflight.md` and **work around them**. Do NOT revert (per `AGENTS.md` Rule 3 / `CLAUDE.md` Root Cause Fixes).

4. **Create artifact directory.**
   - `<audit-dir>/applied/` with empty `verification_log.md`, `changes.md`, `summary.md`, `preflight.md`.

### Phase 1 — Parse findings

1. **Parse the prioritized plan in `report.md`.**
   - Extract Tier 0–3 tables under "Prioritized Documentation Update Plan".
   - Each row → one work item with stable ID `T<tier>-<row>`, plus the `Issue`, `Docs to Update`, and `Effort` columns.

2. **Parse the per-group findings.**
   - For each `findings/docs_review_G*.md`, `docs_consistency_cross.md`, and `docs_accuracy_code.md`:
     - Extract heading-level findings with their `Location:`, `Reference:`/`Issue:`, `Recommendation:`, and severity.
   - Build an index keyed by `(doc_path, line)` so plan rows can be hydrated with the detailed location info.

3. **Reconcile.**
   - Each plan row maps to one or more findings rows.
   - If a plan row has no matching finding (rare), flag it `INCONCLUSIVE` immediately — the protocol won't act on a plan row without grounded location data.

4. **Classify.**
   - Tag each work item with one of the eight claim types above based on heuristics on the finding text (e.g. "file reference" / "count" / "class doesn't exist" / "duplicate heading").
   - If classification fails → claim type `default` → verdict will be `INCONCLUSIVE`.

### Phase 2 — Verify

For each work item:

1. Dispatch to the matching verifier (claim type → verifier above).
2. Render verdict.
3. Append to `applied/verification_log.md`:

   ```markdown
   ## {ID}: {finding title}

   **Source:** report.md Tier {tier}, row {row} → findings/{file}.md
   **Doc target:** `path/to/doc.md:{line}`
   **Claim type:** dead-reference | content-count | cross-doc | proj-status | stale-symbol | code-example | missing-docs | heading-structure | default
   **Verdict:** CONFIRMED | ALREADY-FIXED | DISPUTED | STALE | INCONCLUSIVE | DEFERRED
   **Evidence:**
   - {bullet — file:line citations, grep hits, command output}
   **Decision:** apply | skip | defer-to-project
   ```

Verification runs sequentially per item but does not pause for any user input.

### Phase 3 — Apply

For each work item with verdict `CONFIRMED`:

1. **Read** the doc at the cited region (small range around the cited line) to capture an exact string for `Edit`.
2. **Edit** with the unique exact-string replacement. If `Edit` reports the `old_string` is not unique, expand the snippet with surrounding context until unique. If the cited region no longer exists, downgrade verdict to `STALE` and skip.
3. **Append** to `applied/changes.md`:

   ```markdown
   ## {ID}: {title}

   **Doc:** `path/to/doc.md`
   **Verification:** see [verification_log.md#{id}](verification_log.md#{id-anchor})

   **Before:**
   ```text
   <old snippet, ~3 lines>
   ```

   **After:**
   ```text
   <new snippet, ~3 lines>
   ```
   ```

4. **Update `Last verified:` line** on every doc that was actually modified in this run. Format per `docs/03_CONVENTIONS.md`:

   ```
   > **Last verified:** YYYY-MM-DD — Applied doc-audit fixes ({count} items, see Reviews/results/<audit-dir>/applied/changes.md).
   ```

   - Use today's UTC date.
   - Only docs under `docs/` carry this line; skip the update for `AGENTS.md` / `CLAUDE.md` / `.agents/CODEX.md` (per the audit's own scope notes).

### Phase 4 — Validate

1. **Re-scan for dead references** using a temporary output directory to avoid polluting `Reviews/results/`:

   ```bash
   python Tools/docs_audit/docs_audit.py --output <audit-dir>/applied/postcheck
   ```

2. **Compare** `<audit-dir>/raw/doc_file_refs.json` (before) with `<audit-dir>/applied/postcheck/raw/doc_file_refs.json` (after). Compute:
   - `dead_refs_before` = count of entries with `exists=false` in before
   - `dead_refs_after` = same in after
   - `dead_refs_resolved` = count of (doc, line, ref) tuples present in before but absent in after with `exists=false`

3. **Sanity check.** `dead_refs_resolved` should equal the count of CONFIRMED dead-reference fixes applied. If it diverges, write a `WARNING` block to `applied/summary.md` — do not abort, but make the discrepancy visible.

4. **Do NOT run the 7-agent Phase 2 swarm.** Phase 1's deterministic scan is the only validation step.

### Phase 5 — Wrap up

1. **Write `applied/summary.md`:**

   ```markdown
   # Apply Doc Audit — Summary

   **Source audit:** `Reviews/results/<audit-dir>/`
   **Applied at (UTC):** {timestamp}
   **Working tree at start:** clean | dirty (see preflight.md)

   ## Counts
   | Verdict | Count |
   |---------|-------|
   | CONFIRMED (applied) | N |
   | ALREADY-FIXED | N |
   | DISPUTED | N |
   | STALE | N |
   | INCONCLUSIVE | N |
   | DEFERRED | N |

   ## Dead-reference scan (deterministic re-check)
   | Metric | Before | After |
   |--------|--------|-------|
   | Dead refs total | N | N |
   | Dead refs resolved by this run | — | N |

   ## Top changes
   1. {ID} — {title} → `doc.md`
   2. ...
   3. ...

   ## DEFERRED items (recommended follow-up)
   | ID | Module | Suggested action |
   |----|--------|------------------|
   | T3-23 | game/simulation/replay/replay_serialization.py | claude-proj-start "Replay system documentation" |

   ## Artifacts
   - [Verification log](verification_log.md)
   - [Changes](changes.md)
   - [Pre-flight notes](preflight.md)
   ```

2. **Log skill usage** (also covered by hook, but explicit call mirrors the OpenCode skill):

   ```bash
   python Tools/agent_coordination/log_skill_usage.py --agent claude --skill claude-doc-audit-apply
   ```

3. **Present summary to user.** Print:
   - Counts table.
   - Dead-ref before/after.
   - DEFERRED items with their recommended next step.
   - Pointer to `applied/summary.md`.
   - Reminder: "Review `git diff --stat` before committing — no `game/` or test files should be touched."

---

## Constraints (recap, for reference during execution)

- **No source-code edits.** Only `docs/`, `AGENTS.md`, `CLAUDE.md`, `.agents/CODEX.md`, `Projects/protocols/*.md`, and `Reviews/protocols/*.md` are eligible for editing — and only when the audit cited those files specifically.
- **No prose authoring.** Tier 3 missing-docs claims are always `DEFERRED`.
- **No `Projects/projects_index.md` edits.** Doc misrepresentation of PROJ status is a doc fix, not an index fix.
- **No reverting unrelated dirty state.** Pre-flight records it; the protocol works around.
- **Runtime root discovery only.** Never hardcode checkout-specific paths; resolve from `git rev-parse --show-toplevel` or runtime caller location.
- **Idempotent.** `applied/` already present → abort unless `--force`.

---

## Quick Reference

### Key commands

| Command | Purpose |
|---------|---------|
| `python Tools/docs_audit/docs_audit.py --output <path>` | Re-run Phase 1 deterministic scan into a custom directory |
| `python Tools/agent_coordination/log_skill_usage.py --agent claude --skill claude-doc-audit-apply` | Usage logging |

### Key files per run

| File | Purpose |
|------|---------|
| `<audit-dir>/applied/verification_log.md` | Per-finding verdict + evidence |
| `<audit-dir>/applied/changes.md` | Per-CONFIRMED-fix before/after diff |
| `<audit-dir>/applied/summary.md` | Top-level counts and pointers |
| `<audit-dir>/applied/preflight.md` | Pre-existing dirty-state record (if any) |
| `<audit-dir>/applied/postcheck/raw/doc_file_refs.json` | Post-fix dead-ref scan output |

### Termination

After presenting the summary, the protocol stops. No automatic commit. The user reviews `git diff` and decides whether to commit, and what scope of commit (single, per-tier, or per-doc).
