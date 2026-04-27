# PROJ-307: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | 21 of 22 docs lack any freshness marker; recurring drift problem flagged by 2026-04-26 review |
| 2026-04-26 | Format: blockquote `> **Last verified:** YYYY-MM-DD — <summary>` placed just under H1 | Matches existing `docs/README.md` convention; visually distinct without breaking heading hierarchy |
| 2026-04-26 | "Verified" not "Updated" | "Verified" implies intentional accuracy check; "Updated" gets bumped on cosmetic edits |
| 2026-04-26 | Backfill date = `git log -1 --format=%cs <file>` | Honest baseline ("as of last meaningful change"); future verifications by real maintainers |
| 2026-04-26 | Summary text is OPTIONAL during backfill | Backfilling rich summaries across 21 files is high effort; let real maintainers enrich on next verification |
| 2026-04-26 | Convention enforcement via CLAUDE.md Rule 2 | CLAUDE.md is read every session by Claude Code; Rule 2 already covers doc-edit requirements |
| 2026-04-26 | `docs/_ignore/` is OUT OF SCOPE | Per CLAUDE.md the folder is the user's scratchpad |
| 2026-04-26 | `Projects/`, `Reviews/`, `Tracking/` markdown files OUT OF SCOPE | Not part of `docs/`; have their own lifecycle |
| 2026-04-26 | Tools (`check_doc_freshness.py`, pre-commit hook) OUT OF SCOPE | Capture as follow-up; this project is the policy + backfill, not the tooling |
