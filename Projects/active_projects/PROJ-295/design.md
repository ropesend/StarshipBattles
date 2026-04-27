# PROJ-295: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Python 3.10 hits end-of-life on **2026-10-04**. Today (2026-04-26) the dev environment is Python 3.10.11. The trigger for this project is two `FutureWarning`s from `google-cloud-speech` and `google-api-core` libraries used by [Tools/qa_observer/processor.py](../../../Tools/qa_observer/processor.py). These libraries will drop 3.10 support in future releases past the EOL date.

The upgrade is purely preventive — no current code path is broken on 3.10 today. The deadline gives ~5 months of runway.

## Swarm Findings Summary

Single Explore agent's findings; full report in [findings/research.md](findings/research.md). Highlights:

### Architecture

- No CI/CD infrastructure detected (no `.github/workflows/`, no Dockerfile, no `tox.ini`)
- No virtual environment configured at root (no `.venv`, `venv`, or `.python-version`)
- No `pyproject.toml`, no `setup.py`, no `setup.cfg` — the project doesn't pin Python version anywhere mechanical
- Pytest infrastructure: `pytest.ini` with `-n 4` parallel default; custom test sharding via `Tools/test_sharded/test_sharded.py`
- 15,109 tests, ~40s parallel runtime — fast enough that a full re-run on the new Python is cheap

### Key Patterns to Reuse

- **`from __future__ import annotations`** — 147 files already use this. PEP 563-compatible; no-ops on 3.11+. Means we don't need to retype any annotations.
- **Test-first regression** per CLAUDE.md Rule 1 — the existing 15K-test suite IS the regression test. No new tests needed; just re-run on the new version.

### Dependencies & Risks

The risk surface is C-extension wheel availability. Pure-Python deps don't care about Python version (within reason). Risk-ranked dependencies:

| Package | Wheel risk | Why |
|---------|-----------|-----|
| `numpy` | Low | First-class wheels for 3.11/3.12/3.13 published quickly |
| `scipy` | Low | Same |
| `opencv-python` | Medium | Often lags 3.13 by 6+ months; usually current on 3.11/3.12 |
| `Pillow` | Low | Wheels current on all maintained versions |
| `pyaudio` | **Medium-High** | Often requires manual compilation on Windows; 3.13 wheels sometimes missing |
| `dearpygui` | Medium | Slower release cadence; verify 3.12+ compat |
| `pygame-ce` 2.5.6 | Low | Active project; supports 3.11/3.12/3.13 |
| `google-cloud-speech` | Low | The source of the FutureWarning; explicitly publishes wheels for 3.11+ |
| `pytest` 8.0+ | Low | Pure Python |
| `pytest-xdist` | Low | Pure Python |
| `pytest-testmon` | Low | Pure Python |

**Risk mitigation:** Phase 1 dry-run install on the target version *before* committing to it. If `pyaudio` blocks, the fallbacks are: (1) pin to a specific PyPI version that has wheels, (2) wheelhouse a precompiled binary, (3) drop pyaudio (only used by [Tools/qa_observer/](../../../Tools/qa_observer/) — could be made optional).

### Opportunities Discovered

- **Opportunity:** create a minimal `pyproject.toml` declaring `requires-python = ">=3.11"` (or whichever target). This is the modern standard and prevents accidental 3.10 installs once the upgrade lands. Out of scope to add full PEP 621 metadata; the single declaration is enough.
- **Opportunity:** add `.python-version` for `pyenv` users. Single-file declaration, no behavior cost.
- **Opportunity:** introduce a `.venv` at repo root with the new Python. Currently no venv → contributors install globally. The upgrade is a natural moment to standardize. Phase 2 includes this as an *optional* task (user discretion).

## Target Version Comparison

| Version | Released | EOL | Recommendation |
|---------|----------|-----|----------------|
| 3.11 | Oct 2022 | Oct 2027 | Conservative — 1.5y of runway, all deps stable |
| 3.12 | Oct 2023 | Oct 2028 | **Sweet spot** — 2.5y runway, mature wheels for all deps |
| 3.13 | Oct 2024 | Oct 2029 | Aggressive — 3.5y runway, but pyaudio/dearpygui wheels may lag |

**Recommendation:** 3.12. It maximizes runway without aggressive bleeding-edge risk. Switch to 3.13 if the user prefers maximum runway and is willing to accept higher chance of dependency wheel friction in Phase 1.

## Phased Approach Rationale

| Phase | Purpose | Why split out |
|-------|---------|---------------|
| 0 | User decision gate | Multiple decisions can't be answered without user input (target version, drop-3.10, timing). Blocking these in Phase 0 prevents wasted work. |
| 1 | Dry-run wheel validation | Done BEFORE installing, so we discover wheel gaps without polluting the working environment. If a wheel is missing, Phase 1 surfaces it cheaply. |
| 2 | Live migration + regression | The high-effort phase. Self-contained: install, run tests, fix anything that breaks. Pure execution. |
| 3 | Documentation | Hygiene step. Records the new baseline for future contributors. |
| 4 | Closeout | A 2-week observation window to catch any subtle issues from the upgrade (e.g. behavior changes in stdlib `asyncio` semantics). Cheap insurance. |

## Design Decisions

See [decisions.md](decisions.md) for full rationale.
