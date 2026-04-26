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

## Phase 0 Decision Questions (FOR USER)

The following questions must be answered before Phase 1 begins. Update this table as the user answers.

| # | Question | Recommendation | User's answer |
|---|----------|----------------|---------------|
| 1 | Target Python version: 3.11, 3.12, or 3.13? | 3.12 (best runway / risk balance) | _Pending_ |
| 2 | Drop 3.10 support entirely, or maintain multi-version compatibility? | Drop entirely | _Pending_ |
| 3 | Target completion date? | Before 2026-09-01 (1 month buffer before EOL) | _Pending_ |
| 4 | Is `pyaudio` dropping acceptable as a fallback if wheels are missing? It's only used by `Tools/qa_observer/` (not core game). | Yes, fallback acceptable; don't block the upgrade on QA tooling | _Pending_ |
| 5 | Should we introduce `.venv` at repo root and `pyproject.toml` (with just `requires-python` declared) as part of this upgrade? | Yes — minimal, modern, prevents accidental 3.10 installs | _Pending_ |
| 6 | Are there contributors other than the user who'd be affected? | Solo project per project context | _Pending_ |
