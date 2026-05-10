# Cross-Doc Consistency Report
## Summary
- Doc files analyzed: 22 (AGENTS.md, CLAUDE.md, CODEX.md, docs/README.md, docs/01-06_*.md, docs/systems/*.md, docs/guides/*.md, docs/known-issues.md)
- Consistency issues found: 9
- Critical: 1 | Major: 4 | Minor: 4

## Terminology Issues
| Term | Doc A Usage | Doc B Usage | Severity | Recommendation |
|------|------------|------------|----------|----------------|
| Python version | **AGENTS.md** (§Critical Conventions): "Python 3.14" | **CLAUDE.md** (§Project Facts): "Python baseline: 3.13+." / **docs/03_CONVENTIONS.md** (§8): "Python 3.13+ baseline (PROJ-295)" / **docs/README.md** (Quick Reference): "Python: 3.x with Pygame" | **CRITICAL** | AGENTS.md is the authoritative agent rulebook. CLAUDE.md and 03_CONVENTIONS.md agree on 3.13+. Resolve: either AGENTS.md should say 3.13+ (matching the two other sources) or the other three should be bumped to 3.14. The README's generic "3.x" is harmless but unhelpful — it should match. |
| Pattern count | **docs/README.md** (§Reading Order, §Directory Structure): "30 design patterns" | **docs/02_PATTERNS.md** (header): "33 patterns" / **docs/README.md** (Last verified): "pattern count is 31" | **MAJOR** | The README advertises 30 patterns in the reading-order table AND the directory-structure listing. The Last verified line (2026-04-28) says 31. The actual count is 33 (Patterns #32 and #33 were added 2026-05-04). All three stale numbers must be updated to 33. |
| Design patterns in README directory structure listing | **docs/README.md** (§Directory Structure): lists "30 design patterns" with parenthetical examples including "Registrar Close-Callback" | **docs/02_PATTERNS.md** (Pattern #30): "Registrar Close-Callback (BUG-121) -- SUPERSEDED" | **MINOR** | The README directory-structure listing highlights a superseded pattern (Registrar Close-Callback) in the summary description. A more current example (e.g. Compositional Construction, UI Widget Test Factory) should replace the superseded one. |

## Contradictory Guidance
| Topic | Doc A Claim | Doc B Claim | Severity | Resolution |
|-------|------------|------------|----------|------------|
| Python version mandate | **AGENTS.md** line 52: "Python 3.14" | **CLAUDE.md** line 94: "Python baseline: 3.13+." | **CRITICAL** | Same as the terminology row above. AGENTS.md sets a specific floor (3.14) that CLAUDE.md and 03_CONVENTIONS.md contradict. If 3.14 is the actual floor, CLAUDE.md and 03_CONVENTIONS.md need updating. If 3.13+ is correct, AGENTS.md needs correction. The README's "3.x" is also inconsistent. |

## Cross-Reference Problems
| Source Doc | Target Ref | Issue | Severity |
|-----------|-----------|-------|----------|
| **docs/03_CONVENTIONS.md** (§10.2, line 617) | `"per §5 / docs/03_CONVENTIONS.md §285–288"` referencing PNG format requirement | **Wrong section.** The PNG-only rule is defined in §3.2 (Image Asset Format Convention), not §5 (JSON Data Conventions). Additionally, `§285–288` appears to reference line numbers rather than section numbers — line numbers drift with edits. | **MAJOR** |
| **docs/README.md** (§Reading Order, line 17 / §Directory Structure, line 68) | `02_PATTERNS.md` — described as "30 design patterns" | **Stale count.** The target doc (02_PATTERNS.md) documents 33 patterns. The cross-reference undersells the doc content by 3 patterns. | **MAJOR** |
| **docs/README.md** (Last verified, line 2) | Claims "pattern count is 31" | **Stale.** Actual count is 33 after PROJ-327 (Pattern #32) and PROJ-322/324/325/328 (Pattern #33) addition on 2026-05-04. | **MAJOR** |
| **docs/03_CONVENTIONS.md** (§6.5, line 511) | Section numbering: `### 6.5 System Migration` duplicates `### 6.5 No Hardcoded Type Lists` (line 495) | **Section 6.5 appears twice.** The second instance should be §6.6. Any cross-reference targeting §6.5 for "System Migration" would be ambiguous. | **MINOR** |

## Duplicate Documentation
| Concept | Doc A | Doc B | Recommendation |
|---------|-------|-------|----------------|
| Design patterns summary | **AGENTS.md** (Quick Reference): "Key patterns: Registry, ApplicationContext DI, Facade/Delegate, CQRS-lite, two-phase ability aggregation, Habitability Factor Registry" | **docs/README.md** (§Directory Structure): lists the first ~7 of 33 patterns parenthetically | The README tries to enumerate patterns in the directory listing. Remove the inline enumeration (it will drift) and instead say "33 design patterns — see full reference" with a link. AGENTS.md's compact list is correct as a quick reference. |
| Agent adapter conventions (Python version, spatial terms, return types, LOC ceiling) | **AGENTS.md** (§Critical Conventions) | **CLAUDE.md** (§Key Conventions) + **CODEX.md** (implied via "Read AGENTS.md first") | CLAUDE.md lines 94-119 intentionally restate AGENTS.md conventions "because Claude Code's context can grow long and the model loses fidelity" (CLAUDE.md line 46). This is marked `<!-- agent-coordination:reinforcement -->` and is NOT a problem. However, CLAUDE.md's "Python baseline: 3.13+" (line 94) contradicts AGENTS.md's "Python 3.14" (line 52) — the reinforcement has diverged from the canonical source. |

## Terminology Normalization Recommendations
| Term | Canonical Definition | Source |
|------|---------------------|--------|
| System | Star system — circular region (~8000 hexes, radius 50) around a star center | AGENTS.md line 57, docs/03_CONVENTIONS.md §1.4 |
| Sector | Single hex coordinate — smallest addressable location on the galaxy map | AGENTS.md line 57, docs/03_CONVENTIONS.md §1.4 |
| Battle | Simulation orchestration: full engagements, state, resolution | docs/03_CONVENTIONS.md §1.1 |
| Combat | Entity-level behavior: per-ship, per-tick mechanics | docs/03_CONVENTIONS.md §1.1 |
| Screen | Major game states (battle, strategy, workshop, setup) | docs/03_CONVENTIONS.md §1.2 |
| Scene | Minor overlays (menus, settings) | docs/03_CONVENTIONS.md §1.2 |
| Builder | Internal panels (reusable UI components) under `game/ui/screens/builder/` | docs/03_CONVENTIONS.md §1.3 |
| Workshop | Top-level screen that composes Builder panels | docs/03_CONVENTIONS.md §1.3 |
| Python version | 3.13+ (per the majority of docs: CLAUDE.md + 03_CONVENTIONS.md) | **NEEDS RESOLUTION** — AGENTS.md says 3.14 |

## Additional Observations

### Terminology Compliance (no issues found)
- "System" vs "Sector": All docs use these terms correctly matching the AGENTS.md definitions. No instance of "System" used to mean "Sector" was found.
- "Battle" vs "Combat": All docs use these correctly matching docs/03_CONVENTIONS.md §1.1 (Battle = orchestration, Combat = per-entity).
- "Screen" vs "Scene": All docs use these correctly matching docs/03_CONVENTIONS.md §1.2.
- "Builder" vs "Workshop": All docs use these correctly matching docs/03_CONVENTIONS.md §1.3.

### Cross-References Verified (no issues found)
- docs/01_ARCHITECTURE.md → docs/02_PATTERNS.md Pattern #31: ✓ (Pattern #31 exists at line 1640)
- docs/01_ARCHITECTURE.md → docs/04_SERVICES.md for public API: ✓ (file exists)
- docs/03_CONVENTIONS.md → docs/05_ERROR_HANDLING.md: ✓ (file exists, section "Intentional Broad Catch Convention" present)
- docs/06_UI_STYLE_GUIDE.md → docs/02_PATTERNS.md Pattern #31: ✓ (Pattern #31 exists)
- docs/README.md → Tools/README.md: ✓ (file exists)
- docs/05_ERROR_HANDLING.md → game/core/exceptions.py, error_codes.py, json_utils.py, event_logging.py: ✓ (all exist)
- AGENTS.md → docs/README.md, 01_ARCHITECTURE.md, 02_PATTERNS.md, 03_CONVENTIONS.md: ✓ (all exist)
- CLAUDE.md → docs/README.md, 01_ARCHITECTURE.md, 02_PATTERNS.md, 03_CONVENTIONS.md: ✓ (all exist)
