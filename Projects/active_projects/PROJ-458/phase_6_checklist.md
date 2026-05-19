# PROJ-458 Phase 6: docs/known-issues.md verification-stamp bump (codex-audit driven)

**Status:** Complete
**Objective:** Bring `docs/known-issues.md` into compliance with the doc-freshness contract at `docs/03_CONVENTIONS.md:502-513` after the Phase 1 / F-C-016 content edits. The end-of-project codex audit (`consults/20260519T145550Z_end-of-project-audit/response.md`) flagged that Phase 1's substantive edits left the `> Last verified: 2026-05-07` stamp unchanged, violating the "bump the date for substantive edits" convention. Pure doc-only cleanup; zero code changes.

**Cross-bucket file-ownership rule:** Touches only `docs/known-issues.md`. No production code, no test files.

**Source:** [`consults/20260519T145550Z_end-of-project-audit/response.md`](consults/20260519T145550Z_end-of-project-audit/response.md) — codex verdict "Extra phases needed... once that doc-freshness issue is fixed, I do not see a remaining production blocker in PROJ-458."

---

## Tasks

### Task 6.1: Update verification stamp [Trivial]

- [x] Bump `> Last verified:` from `2026-05-07` to `2026-05-19`.
- [x] Switch to the canonical convention format (`> **Last verified:** YYYY-MM-DD - <one-sentence summary>`) per `docs/03_CONVENTIONS.md:502`.
- [x] Set the summary to describe Phase 1's substantive change: "SettingsWindow added to the two-stage retrofit list and the stale `tests/fixtures/README.md` warning paragraph removed (PROJ-458 Phase 1 / F-C-016 closure)."

---

## Phase Completion Checklist

- [x] `docs/known-issues.md` header carries the post-Phase-1 verification stamp
- [x] No sharded re-run needed (zero code / test changes)
- [x] No re-audit needed (Phase 6 is 0 LOC of production change per Group C prompt Step 4)

## Notes

- Group C prompt Step 4: "Repeat the codex audit if the new phases are non-trivial (>30 LOC of production change)." Phase 6 is a 2-line doc edit. No re-audit.
- The other 4 candidate verifications codex performed all passed (phase checklist closure; retrofit shape; bypass workaround; F-C-016 content; characterization tests; no production regression; read-only contracts). This is the single verified issue.
