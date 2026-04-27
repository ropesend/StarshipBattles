# PROJ-295: Python 3.11+ Upgrade (Google EOL Track)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-295` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-295 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. User decision gate | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. pyaudio → sounddevice migration | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wheel dry-run on Python 3.13 | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Live install + full regression | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation updates | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Closeout & monitor | Awaiting User Approval | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-26 09:00
**Active Phase:** Phase 5 — Awaiting User Approval to archive
**Last Action:** All 5 phases code-complete. Python 3.13.13 installed via winget; `.venv` created; all 60+ dependencies installed cleanly; pyproject.toml and .python-version added; CLAUDE.md + combat_lab/README.md updated. Three sharded suite runs on 3.13: 15112/15111/15112 (run 2 was a pre-existing order-dependent flake — passes in isolation). Wall time 76s → 52s (31% speedup from 3.13). MEMORY.md topic file written.
**Next Action:** **USER ACTION** — review the changes (`git status` shows the file diff) and authorize archival via `python Projects/scripts/archive_project.py PROJ-295`. Or request specific changes before close.
**Blockers:** Project archival is a destructive operation; awaiting explicit user approval per CLAUDE.md.
**Context for Next Agent:** Project is fully verified end-to-end. Phase 5 stability characterization documented in `findings/watchlist.md`. The known order-dependent flake (`test_warp_distance_scaling`) is pre-existing and was also seen on 3.10 in different forms — not a regression. The audioop-lts dependency could be removed in a future cleanup by reimplementing 3-line numpy RMS in the QA observer; not urgent.

## Overview

Python 3.10 reaches end-of-life on **2026-10-04** (~5 months). Two `FutureWarning`s from `google-cloud-speech` and `google-api-core` (used by [Tools/qa_observer/processor.py](../../../Tools/qa_observer/processor.py)) flag that future releases of those libraries will drop 3.10 support after that date. The upgrade is purely preventive — no current code is broken.

Per research:
- **No breaking-change blockers detected** in our codebase (no usage of removed APIs: `distutils`, `binhex`, `lib2to3`, `asyncio.coroutine`).
- **147 files** already use `from __future__ import annotations` (forward-compatible).
- **Both `Optional[X]` and `X | None` syntax** coexist; both supported in 3.11+.
- **No version pin** is hardcoded in `requirements.txt`, no `pyproject.toml`, no `.python-version`, no CI workflows.

## Goals

- Move the dev environment baseline from Python 3.10.11 to a supported version (3.11, 3.12, or 3.13 per user decision) before 2026-10-04.
- Keep all 15109+ tests passing on the new version.
- Document the new minimum supported Python version in `CLAUDE.md` and `requirements.txt`.
- Eliminate the two Google `FutureWarning`s.

## Scope

**In:**
- Verify wheel availability for `numpy`, `opencv-python`, `pyaudio`, `dearpygui`, `pygame-ce`, `scipy`, `Pillow`, `google-cloud-speech` on the target version
- Set up a local virtual environment on the target Python version
- Install all dependencies and run the full test suite
- Update `requirements.txt` / `requirements-dev.txt` if any dependency version pins need bumping
- Update `CLAUDE.md` to reflect the new minimum Python version
- Add a `python_requires` declaration if creating `pyproject.toml` (decision point)

**Out:**
- Adopting Python 3.11+ specific features (e.g. `tomllib`, `ExceptionGroup`, `Self` type) — mechanical upgrade only, no syntax modernization
- Adding CI/CD infrastructure (no `.github/workflows/` exists today; introducing CI is a separate project)
- Containerizing dev environment (no `Dockerfile` exists today)
- Multi-version compat (Phase 0 decides whether to keep 3.10 support — recommend NO)
- Refactoring `Tools/qa_observer/processor.py` to use a different speech-to-text provider

## Key Files

| Component | File Path |
|-----------|-----------|
| Direct deps | [requirements.txt](../../../requirements.txt) |
| Dev deps | [requirements-dev.txt](../../../requirements-dev.txt) |
| Project context | [CLAUDE.md](../../../CLAUDE.md) |
| QA observer (Google libs) | [Tools/qa_observer/processor.py](../../../Tools/qa_observer/processor.py) |
| Test runner | [Tools/test_sharded/test_sharded.py](../../../Tools/test_sharded/test_sharded.py) |

## Related Documents

- [design.md](design.md) — Risk analysis, target version comparison
- [decisions.md](decisions.md) — Decision log (target version, drop-3.10, etc.)
- [findings/research.md](findings/research.md) — Dependency inventory, breaking-change scan, version sources

## Verification

- [ ] Phase 0: User has answered decision questions
- [ ] Phase 1: Wheel availability confirmed for all C-extension dependencies on target version
- [ ] Phase 2: `python Tools/test_sharded/test_sharded.py` — full suite green on target version (15109+ tests)
- [ ] Phase 2: `python qa_launcher.py` — manual smoke, no Google FutureWarnings
- [ ] Phase 3: `CLAUDE.md` and requirements files updated with new baseline
- [ ] User verified: dev environment works for typical workflows
