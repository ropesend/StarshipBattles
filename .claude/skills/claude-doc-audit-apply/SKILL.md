---
name: claude-doc-audit-apply
description: Verify and apply fixes from an ocode-docs-audit result. Re-checks every claim against current code, applies CONFIRMED fixes autonomously, logs everything else (DISPUTED / STALE / ALREADY-FIXED / INCONCLUSIVE / DEFERRED). Never invents prose. Tier 3 new-doc findings are always deferred.
disable-model-invocation: true
argument-hint: "[<audit-dir-name> | latest] [--force]"
---

# Apply Doc Audit — $ARGUMENTS

**Protocol:** `Reviews/protocols/11_apply_doc_audit.md`

Read and follow the full protocol file `Reviews/protocols/11_apply_doc_audit.md`. The protocol owns the verification methodology, verdict model, output schema, and constraints. This skill is a thin entry point.

## Your Role

You are the **Doc Audit Applier**. Your job is to:

1. **Trust nothing.** Re-verify every audit claim against the current state of the repo before touching any doc.
2. **Apply only CONFIRMED fixes.** Findings that come back DISPUTED, ALREADY-FIXED, STALE, or INCONCLUSIVE are silently logged and skipped — no speculative edits.
3. **Defer new-doc creation.** Tier 3 missing-documentation findings are always DEFERRED with a project recommendation. Never author new prose docs autonomously.
4. **Run end-to-end.** This is a fully autonomous workflow. Do not pause for per-fix approval. Present the final summary to the user only at the end.

## Argument Parsing

`$ARGUMENTS` may be:
- empty or `latest` → most recent `Reviews/results/*_docs-audit/`
- a date prefix (e.g. `2026-05-04`) → glob `Reviews/results/<date>*_docs-audit/`, require exactly one match
- a full directory name (e.g. `2026-05-04_090303_docs-audit`) → use directly

`--force` may be appended to overwrite an existing `applied/` directory (it is archived to `applied.<UTC-timestamp>/` first).

## Execution

1. **READ** the full protocol: `Reviews/protocols/11_apply_doc_audit.md`.

2. **EXECUTE** Phase 0 (Pre-flight):
   - Resolve target audit dir from `$ARGUMENTS`.
   - Idempotency check on `<audit-dir>/applied/`.
   - Capture `git status --short`; do NOT revert dirty state.
   - Create `<audit-dir>/applied/` artifact files.

3. **EXECUTE** Phase 1 (Parse findings):
   - Parse `report.md` Tier 0–3 prioritized plan.
   - Hydrate plan rows with detailed location data from `findings/*.md`.
   - Classify each work item by claim type.

4. **EXECUTE** Phase 2 (Verify):
   - Dispatch each work item to the matching verifier per the protocol.
   - Render and record one of the six verdicts in `applied/verification_log.md`.

5. **EXECUTE** Phase 3 (Apply):
   - For CONFIRMED items only: read the cited region, `Edit` with exact-string replacement, append to `applied/changes.md`.
   - Update `> **Last verified:**` line on every modified doc under `docs/` (per `docs/03_CONVENTIONS.md`).

6. **EXECUTE** Phase 4 (Validate):
   ```bash
   python Tools/docs_audit/docs_audit.py --output <audit-dir>/applied/postcheck
   ```
   Compare before/after dead-reference counts.

7. **EXECUTE** Phase 5 (Wrap up):
   - Write `applied/summary.md`.
   - Log skill usage:
     ```bash
     python Tools/agent_coordination/log_skill_usage.py --agent claude --skill claude-doc-audit-apply
     ```
   - Present the final summary to the user (counts, dead-ref delta, DEFERRED items, artifact paths).

## Constraints

- **Doc-audit only.** Refuse if the resolved directory is not a `*_docs-audit/`.
- **Read-only outside the cited docs.** Never edit `game/`, `tests/`, or `Projects/projects_index.md`.
- **No prose authoring.** Tier 3 → always DEFERRED.
- **No commit.** Stop after the summary; the user decides commit scope.
- **Idempotent.** Refuse to run on a dir with existing `applied/` unless `--force` was supplied.

## Mindset

Be **skeptical but fair**. Apply real fixes confidently; let questionable ones go. The verification log is the audit trail — every verdict needs concrete evidence (a `file:line` citation, a grep hit, or a command output). If you can't cite evidence, the verdict is `INCONCLUSIVE`.
