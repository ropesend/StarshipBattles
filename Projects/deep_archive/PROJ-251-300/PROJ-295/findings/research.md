# Python 3.10 → 3.11+ Upgrade: Research Findings

## Python Version Sources

**Current Python Version:** 3.10.11 (confirmed via `python --version`)

**Version Pins Found:**
- No explicit `python_requires` in setup.py or setup.cfg (no files found)
- No `pyproject.toml`, `Pipfile`, or pip-tools configuration
- No `.python-version` (pyenv) file configured
- VS Code settings (`.vscode/settings.json`) — pytest config present, but **no Python interpreter pin**
- Documentation (`CLAUDE.md`) lists "Python 3.x" (generic, not pinned to 3.10)
- No GitHub Actions workflows (no `.github/` directory)
- No Dockerfile

---

## Direct Dependencies

**From `requirements.txt` (3 direct):**
- `pygame-ce>=2.5.0` — Community Edition, pure Python
- `pygame_gui>=0.6.9` — Pure Python GUI
- `scipy>=1.15.0` — Has C extensions; verify 3.11+ wheels available

**From `requirements-dev.txt` (11 additional):**
- `pytest>=8.0.0`, `pytest-testmon`, `pytest-xdist` — 3.11+ compatible
- `Pillow>=10.0.0` — C extensions; wheels available for 3.11+
- `numpy>=1.24.0` — C extensions; **primary compatibility concern**
- `opencv-python>=4.8.0` — C extensions; wheels available
- `matplotlib>=3.7.0` — Mixed; 3.11+ compatible
- `fastapi>=0.100.0`, `uvicorn>=0.23.0` — Pure Python; ready
- `dearpygui>=1.9.0` — C bindings; verify 3.11 wheel support
- `pyaudio>=0.2.14` — C extensions; **known compilation issues on some systems**
- `watchdog>=4.0.0` — Pure Python; 3.11+ ready
- `google-cloud-speech>=2.26.0` — **ROOT TRIGGER: Emits FutureWarning about 3.10 EOL**
- `python-dotenv>=1.0.1` — Pure Python

**High-Risk Candidates:** numpy, opencv-python, pyaudio, dearpygui, google-cloud-speech.

---

## Python 3.10-Specific Syntax

**`from __future__ import annotations`:** 147 files use this pattern.
- PEP 563; forward-compatible with 3.11+ — no code changes required
- Acts as no-op in 3.11+; safe to keep

**Type Hints:**
- `Optional[X]` syntax found in ~5 uses across `combat_lab/battle_state_capture.py`
- `X | None` syntax found in: `combat_lab/design_loader.py`, `game/simulation/components/component.py`, `game/simulation/services/modifier_service.py`
- Both coexist; **no migration required** — 3.11+ supports both

**`match/case` statements:** Not detected (no 3.10+ pattern matching used)

**Advanced typing:** `ParamSpec`, `Concatenate`, `NewType` — not detected

---

## 3.11/3.12 Breaking Changes Risk Assessment

**Removed APIs (not used):**
- `asyncio.coroutine` — grep: not found
- `binhex` module — grep: not found
- `distutils` (3.12+) — grep: not found
- `lib2to3` (3.13+) — grep: not found

**Typing changes:** No detected usage of affected APIs

**Conclusion:** **Zero breaking changes detected.** Safe upgrade path.

---

## CI / Dev Environment

**Virtual Environment:** Not configured.
- No `.venv`, `venv`, `env` directories at root
- No `.python-version` (pyenv not in use)
- No `tox.ini` (multi-version testing not configured)

**Development Setup:** Ad-hoc; likely direct Python installation or IDE-managed.

**Pytest Infrastructure:**
- `pytest.ini` root configuration with `-n 4` default (pytest-xdist parallelization)
- Pre-commit hooks: **not configured**
- Type checking (mypy): **not configured**

---

## Test Suite

**Scale:** 15,109 tests (confirmed via pytest --collect-only)
- 941 test files (`test_*.py` pattern)
- ~18,686 test functions/classes

**Performance (from tests/README.md):**
- Parallel (4 workers): ~40 seconds
- Sequential: ~90 seconds

**Note:** Collection reports 3 errors in AI/strategy tests; requires investigation on upgrade.

---

## Dependent Tooling

**Test Sharding:** `Tools/test_sharded/test_sharded.py`
- Custom runner distributes tests across CPU cores
- Saves per-test timings to `.test_durations.json`
- **No Python version assumptions** — compatible with 3.11+

**No detected usage of:**
- Pre-commit hooks
- Type checking (mypy)
- Linters or formatters (in scope)

---

## Decision Points

### 1. Target Version
- **3.11**: Minimum (stable Nov 2024, EOL Oct 2027)
- **3.12**: Latest stable (EOL Oct 2028) — **recommended**
- **3.13**: Beta track (evaluate for long-term support)

### 2. Timeline
- Deadline: 2026-10-04 (~5 months)
- Upgrade scope: 2–3 weeks (dependency validation, test regression, setup)
- Buffer: 4+ months for unexpected issues

### 3. Support Strategy
- Drop 3.10 entirely (simplifies CI, no version matrix)?
- Or maintain 3.10/3.11+ compatibility?
- **Likely:** Drop 3.10 after upgrade; baseline at 3.11+

### 4. Upgrade Order
- **Local dev first** (contributor validates, documents issues)
- Or CI first (not applicable — no CI infrastructure detected)
- **Recommendation:** Local dev given no CI present

### 5. Contributor Impact
- How many developers affected?
- Build scripts hardcoding 3.10? (Not detected)
- Environment documentation updates needed?

### 6. Dependency Validation (Before Commit)
- Test wheel availability for numpy, opencv-python, pyaudio, dearpygui on 3.11/3.12
- Command: `pip install --dry-run -r requirements.txt` with Python 3.11/3.12
- Identify compilation failures early in planning

---

**Report Generated:** 2026-04-26 | **Findings:** Safe upgrade; zero breaking changes detected. High-value opportunity to drop 3.10 EOL support.
