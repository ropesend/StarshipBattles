# PROJ-295: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Python 3.11+ Upgrade (Google EOL Track) |
| 2026-04-26 | Phase 0 (decision gate) is blocking — implementation cannot start until user answers | Three decisions affect the whole plan: target version (3.11/3.12/3.13), drop-3.10 vs. multi-version compat, timing window. Locking these in upfront prevents partial work that needs unwinding. |
| 2026-04-26 | Architect's recommended target: Python 3.12 | 2.5y runway (EOL Oct 2028), mature wheel ecosystem, low risk of dependency friction. 3.13 is more runway but higher pyaudio/dearpygui wheel-availability risk. 3.11 is least runway. The user has final say in Phase 0. |
| 2026-04-26 | Architect's recommended drop-3.10 strategy: drop entirely | Maintaining multi-version compat doubles the test matrix forever, and there's no contributor-base reason to keep 3.10 (no CI, no wide audience). Cleanest baseline. |
| 2026-04-26 | Phase 1 uses `pip install --dry-run` to validate wheel availability BEFORE migration | Dry-run surfaces missing wheels without polluting the local environment. Cheap risk-reduction step. |
| 2026-04-26 | Phase 2 is the only phase that touches the actual local Python install | Decoupling reduces the blast radius of any individual phase. If Phase 2 reveals a problem, Phase 1's dry-run records remain valid for fallback decisions. |
| 2026-04-26 | No CI introduction in this project | Adding CI/CD is a separate scope. The 5-month deadline + lack of existing CI infrastructure makes "fix the version, add CI later" the right separation. |
| 2026-04-26 | No syntax modernization in scope | Things like adopting `Self`, `tomllib`, `ExceptionGroup` are post-upgrade improvements. This project is mechanical baseline-bump only. |

---

## Phase 0 Decision Questions (RESOLVED 2026-04-26)

| # | Question | User's answer |
|---|----------|---------------|
| 1 | Target Python version: 3.11, 3.12, or 3.13? | **3.13** (verified via PyPI lookup that all C-ext deps have 3.13-compatible wheels: numpy, scipy, Pillow, opencv-python via abi3, dearpygui, watchdog, pygame-ce, pygame_gui, google-cloud-speech). Only blocker was pyaudio; resolved by migrating to sounddevice. |
| 2 | Drop 3.10 support entirely? | **Yes** — drop, no multi-version compat. |
| 3 | Target completion date? | **Today (2026-04-26).** |
| 4 | pyaudio? | **Migrate to `sounddevice`** rather than drop. Same PortAudio backend (identical audio behavior), `py3-none-win_amd64` wheel covers 3.13 trivially. Folded into PROJ-295 as Phase 1. ~30-40 line refactor across observer.py + audio_monitor.py. |
| 5 | `.venv` at repo root + `pyproject.toml`? | **Yes to both, minimal scope.** `pyproject.toml` carries one declaration: `requires-python = ">=3.13"`. |
| 6 | Contributors? | Solo. |

## Resulting plan revision

Phase 0 closes here. Phase 1 (originally "wheel dry-run") split into:
- **Phase 1: pyaudio→sounddevice migration** — the 3.13 unblocker
- **Phase 2: wheel dry-run on 3.13** — quick sanity check
- **Phase 3: live install + full regression** — venv, install, tests
- **Phase 4: documentation**
- **Phase 5: closeout monitor**

Decision captured: prefer migration over dropping pyaudio because the QA voice-recording loop is a real capability worth preserving, and the migration cost (half a day) is small compared to the long-term benefit of removing the wheel-availability headache.
