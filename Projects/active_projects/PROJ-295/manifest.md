# PROJ-295 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| requirements.txt | Config | Phase 2: bump pin(s) only if Phase 1 surfaced wheel gaps. Otherwise no change. |
| requirements-dev.txt | Config | Phase 2: same — only bump if needed. |
| pyproject.toml | Config (NEW, optional) | Phase 2: create with `requires-python = ">=<TARGET>"` if Phase 0 Q5 = yes. |
| .python-version | Config (NEW, optional) | Phase 3: pyenv-friendly version pin if Phase 0 Q5 = yes. |
| CLAUDE.md | Doc | Phase 3: update Tech Stack section to reflect new Python baseline. |
| README.md | Doc | Phase 3: update if it mentions Python version. |
| Tools/qa_observer/README.md | Doc | Phase 3: remove any references to Google FutureWarning. |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md | Memory (out-of-tree) | Phase 3: append archival entry on closeout. |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\proj_295_python_upgrade.md | Memory (NEW, out-of-tree) | Phase 3: details file linked from MEMORY.md. |

**Production code:** None modified. This is purely an environment + dependency baseline change.

**Test files:** None modified. The existing 15K-test suite IS the regression check.
