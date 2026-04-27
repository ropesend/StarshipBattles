# PROJ-311 File Manifest

## Files

### EDIT (convention)
| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Instructions | Strengthen "Code Quality" with return-annotation requirement |
| `docs/03_CONVENTIONS.md` | Docs | Add §Type Annotations section |

### EDIT (annotations — every file in `game/` with unannotated functions)
| Subsystem | Approximate file count | Wave |
|-----------|-----------------------:|------|
| `game/core/` | TBD (Phase 2 measures) | A |
| `game/simulation/` | TBD | B |
| `game/strategy/` | TBD | C |
| `game/ai/` | TBD | D |
| `game/ui/` | TBD | E |

The exact list of files comes from `findings/unannotated.csv` after Phase 2 audit.

### NEW (project artifacts)
| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-311/findings/annotation_audit.py` | Project artifact | Phase 2 audit tool |
| `Projects/active_projects/PROJ-311/findings/unannotated.csv` | Project artifact | Phase 2 baseline |
| `Projects/active_projects/PROJ-311/findings/baseline_summary.md` | Project artifact | Phase 2 per-subsystem |
| `Projects/active_projects/PROJ-311/findings/wave_order.md` | Project artifact | Phase 2 sequencing |
| `Tools/check_annotation_coverage.py` | Tooling | OPTIONAL — Phase 4 (Option B) |

### EXPLICITLY EXCLUDED
- `tests/` — annotations encouraged but not blocking
- Parameter annotations — separate follow-up project if desired
- `mypy --strict` adoption — much larger separate effort
