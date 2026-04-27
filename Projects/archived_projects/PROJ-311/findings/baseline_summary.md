# PROJ-311 Annotation Audit — Baseline Summary

**Generated:** 2026-04-27
**Tool:** `Projects/active_projects/PROJ-311/findings/annotation_audit.py`
**Scope:** `game/**/*.py` (skips `tests/`, `__pycache__/`)

## Top-line numbers

| Metric | Value |
|---|---|
| Total functions / methods | **5349** |
| Dunder methods (excluded from coverage) | 416 |
| Non-dunder functions | **4933** |
| Annotated (non-dunder, `node.returns is not None`) | **3525** |
| Unannotated (non-dunder) | **1408** |
| Coverage % (non-dunder denominator) | **71.46%** |

This reproduces the design.md figure of 1408 unannotated within 0 functions of expected — small drift (4933 vs 4930 non-dunder) is within noise.

## Per-subsystem breakdown

| Subsystem | Total | Non-dunder | Annotated | Unannotated | Coverage % |
|---|---:|---:|---:|---:|---:|
| `game/core/`        |  357 |  325 |  306 |   19 | 94.15% |
| `game/ai/`          |  153 |  141 |  130 |   11 | 92.20% |
| `game/simulation/`  |  959 |  873 |  764 |  109 | 87.51% |
| `game/strategy/`    | 1225 | 1132 | 1075 |   57 | 94.96% |
| `game/ui/`          | 2507 | 2326 | 1172 | 1154 | 50.39% |
| `other` (game/<top>, game/assets/, game/engine/, game/research/, game/services/) | 148 | 136 | 78 | 58 | 57.35% |
| **TOTAL** | **5349** | **4933** | **3525** | **1408** | **71.46%** |

## game/ui/ subdir breakdown (non-dunder)

`game/ui/` is the giant — 1154 of the 1408 unannotated functions live here (82%). Within it:

| Path | Total | Unann | Cov % |
|---|---:|---:|---:|
| `game/ui/screens/`    | 1771 | **966** | 45.5% |
| `game/ui/panels/`     |  288 | **134** | 53.5% |
| `game/ui/research/`   |   31 |   26 | 16.1% |
| `game/ui/assets/`     |   14 |   12 | 14.3% |
| `game/ui/widgets/`    |   32 |   11 | 65.6% |
| `game/ui/renderer/`   |   12 |    2 | 83.3% |
| `game/ui/services/`   |   75 |    2 | 97.3% |
| `game/ui/utils/`      |   19 |    1 | 94.7% |
| `game/ui/components/` |   58 |    0 | 100.0% |
| `game/ui/effects/`    |   10 |    0 | 100.0% |
| `game/ui/filters/`    |    6 |    0 | 100.0% |
| `game/ui/interfaces/` |    6 |    0 | 100.0% |
| `game/ui/<top-level>` |    4 |    0 | 100.0% |

## 'other' bucket detail (non-dunder)

| Path | Total | Unann | Cov % |
|---|---:|---:|---:|
| `game/<top-level>`  |  47 | 42 | 10.6% |
| `game/assets/`      |  18 |  9 | 50.0% |
| `game/engine/`      |  14 |  7 | 50.0% |
| `game/research/`    |  39 |  0 | 100.0% |
| `game/services/`    |  18 |  0 | 100.0% |

`game/<top-level>` (single-file modules at the package root, e.g. `game/app.py`, `game/context.py`) is the worst-covered piece in the 'other' bucket — 42 of 47 functions unannotated.

## Files

- Full inventory CSV: `inventory.csv` (5349 rows)
- Unannotated-only CSV: `unannotated.csv` (1408 rows — Phase 3 backfill targets)
- Helper that produced the UI subdir breakdown: `_breakdown.py`
- Captured console output: `audit_output.txt`

## Notes

- **Coverage by subsystem reveals a clear story:** `core/`, `ai/`, `strategy/` are already in good shape (>92%); `simulation/` is solid (~88%); `ui/` is the problem area (~50%) and dominates the work remaining.
- **`__init__` is excluded from coverage** (it's a dunder) per PEP 484, even though most existing `__init__` methods in the codebase already carry `-> None`. The audit tool intentionally treats them as exempt to match the convention rule.
- **The 'other' bucket** captures `game/app.py`, `game/context.py`, `game/engine/`, `game/assets/`, `game/research/`, and `game/services/`. These are merged into Wave A in the wave order — they are small and orthogonal.
