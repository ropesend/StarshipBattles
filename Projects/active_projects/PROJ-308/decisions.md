# PROJ-308: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | 24 broad `except Exception:` sites in `game/` (most uncommented). User explicitly wants every broad except justified |
| 2026-04-26 | Verified count: 24 across 18 files (not 28 as in original review) | Independent grep confirmed |
| 2026-04-26 | Three triage choices per site: narrow / justify / delete | Mirrors CLAUDE.md "Long-Term Quality" preference order; covers every legitimate disposition |
| 2026-04-26 | Justification format: `except Exception:  # Intentional broad catch: <reason>` | Matches existing convention at `tkinter_utils.py:100` and `workshop_data_reloader.py:23` |
| 2026-04-26 | Reason must be SPECIFIC, not boilerplate | A "broad catch — legacy" comment is worse than none. Implementer must say what kinds of failures are expected and why fire-and-forget is correct |
| 2026-04-26 | `tests/`, `Tools/`, `Reviews/` broad-except OUT OF SCOPE | Production code is the priority; tests can fail loudly; tooling addressed in PROJ-297 |
| 2026-04-26 | When unsure between narrow vs justify, choose JUSTIFY | Mis-narrowing risks crashing on a real production failure mode; comment-justifying is safer |
| 2026-04-26 | DELETE (Choice 3) should be rare | Most catches handle some real failure. Only delete if it's clearly speculative ceremony |
| 2026-04-26 | Convention enforcement via CLAUDE.md + 05_ERROR_HANDLING.md | CLAUDE.md is read every session; 05_ERROR_HANDLING.md is the authoritative error-handling reference for new contributors |
| 2026-04-26 | CI/lint enforcement OUT OF SCOPE | A `check_broad_except.py` script and pylint rule W0703 are sensible follow-ups; not in this project |
