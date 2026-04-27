# PROJ-307: Design Document

## Initial Analysis

Doc freshness is a recurring problem in this codebase: code-review agents repeatedly find that `docs/` claims contradict current code. The 2026-04-26 review caught three such drift cases (pattern count, test baseline, deprecated `ship_stats_calculator.py` mention). A "Last verified" timestamp gives readers a fast trust signal: a 30-day-old doc is likely fine; an 18-month-old doc warrants skepticism before relying on it.

[docs/README.md](docs/README.md) already uses the convention. Format observed (line 4):
```
> **Last verified:** 2026-04-13 — PROJ-270 closure complete, PROJ-271 Track B landed. ...
```

The summary text after the date is rich (mentions specific projects/concepts). Backfilling that level of detail across 21 files is high effort. **Decision: backfill with terse summaries** ("current as of <topic> implementation in PROJ-XXX" or just the commit date). Future updates can enrich the summary as the maintainer touches each file.

## Architecture

### Format
```markdown
# Document Title

> **Last verified:** YYYY-MM-DD — <optional one-sentence context>

<rest of doc>
```

Rules:
- Always second line (or third, if there's a blockquote-only intro) — visible without scrolling
- Date is `YYYY-MM-DD` (ISO 8601), no times
- Summary is optional but encouraged; should be one sentence ≤ 200 chars
- "Verified" means: the maintainer read the file and confirmed it matches current behavior, not just that they edited it cosmetically

### Why a blockquote, not a header
- Blockquote (`>`) renders as a styled callout in most Markdown viewers — visually distinct from body text without breaking heading hierarchy
- Doesn't affect H2-derived TOCs

### Why "verified" not "updated"
- "Updated" tempts contributors to bump the date when they fix a typo without re-reading the file. "Verified" puts a stake in the ground: this date represents an intentional accuracy check.

## Dependencies & Risks

1. **Risk: timestamps drift back into staleness immediately.**
   The convention only works if maintainers actually update the date when they verify content. Without enforcement, this becomes ceremony.
   **Mitigation:** Phase 2 adds the rule to CLAUDE.md "Rule 2: Documentation". Every Claude Code session reads CLAUDE.md. The Rule-2 docstring already says "Update those docs in the same commit as your code changes" — adding "and bump the verified date" to that requirement makes the timestamp automatic on every meaningful change.

2. **Risk: stale timestamps misleading because the file looks "verified" but isn't.**
   A maintainer might bump the date without actually re-reading.
   **Mitigation:** Out of scope for this project — purely a process/discipline issue. The convention is a forcing function, not a guarantee.

3. **Risk: backfilled dates are arbitrary.**
   For files that haven't been touched in months, picking the last commit date as "verified" is generous — nobody actually re-verified that day.
   **Mitigation:** Phase 1 uses last-commit-date as the *baseline*; the date represents "as of last meaningful change, this was true." The next maintainer to touch the file does a real verification and bumps appropriately. Imperfect but honest.

## Key Patterns to Reuse

- **Doc convention enforcement via CLAUDE.md** — established pattern. CLAUDE.md "Rule 2: Documentation" is the canonical location for doc-edit guidance. Add the timestamp rule there.
- **`docs/03_CONVENTIONS.md`** — established conventions doc. Add a §"Documentation Freshness" section with the format spec.

## Opportunities Discovered

- A small `Tools/check_doc_freshness.py` script could parse all `docs/**/*.md` and report files where `Last verified` is older than N days (e.g., 90). Useful for scheduled freshness audits. Out of scope for this project — capture as a follow-up if desired.
- Pre-commit hook idea: warn (don't block) when a doc is edited but the `Last verified` date wasn't bumped. Out of scope; capture as follow-up.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
