# PROJ-297: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

A 2026-04-26 comprehensive code review made 15+ priority claims. **Each claim was verified before this project was created** — confirmed claims, refuted claims, and partial claims are listed below. PROJ-297 covers only the **confirmed** small, mechanical fixes.

### Claim Verification Matrix

#### Architecture
| ID | Claim | Status | Evidence |
|----|-------|--------|----------|
| 1.1 | `ship_design_stats.py:14` imports `component_state_key` from Strategy; trivial 2-line formatter | **CONFIRMED** | Function body at `game/strategy/data/component_state.py:19-25` is literally `return f"{component_id}#{instance_index}"` |
| 1.2 | `battle_runner.py:191` + `registry_loader.py:25` call `get_default_registry_provider()` | **CONFIRMED but EXEMPT** | Both call sites confirmed. `battle_runner.py` call is inside `_default_ship_builder_from_context()` — the documented PROJ-274 transitional fallback. Removal must coordinate with PROJ-274 closure, NOT this project. **OUT OF SCOPE.** |
| 1.3 | `protocols.py:38` imports `RaceConfig` under `TYPE_CHECKING` | **CONFIRMED** | LOW priority, acceptable. Source review itself agreed. **NO ACTION.** |
| 1.4a | FleetOrder backward compat aliases — claim "8 sites + 37 test files" | **CONFIRMED, scope worse** | 726 old-name usages across codebase. **SPLIT to PROJ-298** because of breadth. |
| 1.4b | `formula_system.py` shim, claim "26 test files import old path" | **PARTIAL — count wrong, file is dead** | Shim is 20 lines. Zero test files import old path (all migrated). Shim is fully dead — delete. |
| 1.4c | `singleton.py` 97 lines, zero production users | **CONFIRMED** | Verified line count and that no production class inherits `SingletonMeta`. |

#### Code Quality
| ID | Claim | Status | Evidence |
|----|-------|--------|----------|
| 2.5 | `print()` in `battle_resolver.py:56` | **REFUTED** | File exists at `game/strategy/interfaces/battle_resolver.py`. Line 56's `print(...)` is inside a docstring's "Example usage" block. Not production code. **NO ACTION.** |
| 2.6 wildcard | 1 wildcard import in `fleet_orders_window.py` | **CONFIRMED** | Single instance, BC shim flagged with `# noqa`. Removal coordinates with FleetOrder rename. **DEFERRED to PROJ-298.** |
| 2.6 TODO | "5 TODO/FIXME, 2 with `PROJ-XXX` placeholder" | **REFUTED** | Only 2 TODOs in `game/`; both legitimate forward-looking notes; zero placeholders. **NO ACTION.** |
| 2.6 bare except | 2 bare `except:` in tooling | **CONFIRMED** | `Reviews/scripts/calculate_agents.py:94`, `Tools/check_orphans/check_orphans.py:63`. |

#### Tests
| ID | Claim | Status | Evidence |
|----|-------|--------|----------|
| 3.2 | 3 test files fail collection | **CONFIRMED** | Verified by running `pytest --collect-only`: `IFormationMaster` missing from `game.ai.protocols`; `FormationBehavior` missing from `game.ai.behaviors`; `create_auto_load_population_order` missing from `command_handlers`. |
| 3.4 | 273 mock refs in `test_command_handlers.py` | **PARTIAL** | Actual count is 267. Mock-density refactor is its own dedicated project — **OUT OF SCOPE.** |

#### Documentation
| ID | Claim | Status | Evidence |
|----|-------|--------|----------|
| 4.1 patterns | CLAUDE.md says 14, README says 25, real count differs | **CONFIRMED** | `docs/02_PATTERNS.md` header explicitly states "27 patterns" and contains numbered headings ## 1. through ## 27. Both other docs are stale. |
| 4.1 baseline | `CLAUDE.md:312` says "14420 passed" | **CONFIRMED** | Real baseline (per MEMORY) is 15112. |
| 4.2a | `docs/systems/resource_system.md` exists | **CONFIRMED** | 240 lines. |
| 4.2b | Not in README reading table | **CONFIRMED** | Zero matches for "resource_system" in `docs/README.md`. |
| 4.2c | `docs/04_SERVICES.md` mentions deleted `ship_stats_calculator.py` | **CONFIRMED** | Listed at line 43 marked DEPRECATED; the file was deleted. |

#### Tooling
| ID | Claim | Status | Evidence |
|----|-------|--------|----------|
| 5.1 | `radon` + `vulture` not installed | **CONFIRMED** | Absent from `pyproject.toml`, `requirements.txt`, `requirements-dev.txt`. |
| 5.2 | PROJ-296 empty placeholder | **REFUTED** | PROJ-296 is the active LLM-services project (committed today). **NO ACTION.** |

## Architecture

### Pattern: Layer Separation
The Simulation layer must not depend on the Strategy layer. `component_state_key` is a Strategy-located utility used by Simulation today; moving it to Core respects the documented dependency rules with no behavior change.

### Pattern: System Migration Policy ("eradicate, don't graveyard")
The `formula_system.py` shim and `singleton.py` are textbook System Migration Policy candidates: zero current users, kept "just in case." Per CLAUDE.md, both must be deleted, not deprecated.

### Key Patterns to Reuse
- **Re-export pattern (anti-pattern here):** `game/simulation/formula_system.py` re-exports from `game.core.formula_evaluator`. Anti-pattern per Migration Policy — delete, not extend.
- **Module-level docstring conventions:** new `game/core/component_state.py` should follow the same docstring style as siblings in `game/core/`.

### Dependencies & Risks
1. **Risk: `component_state.py` may have other content** — verify it's only the one function before deleting the strategy-layer file. **Mitigation:** read full file in Phase 1 Task 1.1 before action; if other code lives there, leave the strategy file but make Core the canonical source.
2. **Risk: stale tests may have legitimate replacement coverage somewhere else** — deleting them blindly could mask gaps. **Mitigation:** for each, run `git log --all --oneline -- <symbol>` and `grep` the codebase for the missing symbol's last presence; check whether equivalent behavior is tested elsewhere before deletion.
3. **Risk: pattern count of 27 may itself drift** — fixing CLAUDE.md and README to "27" is a snapshot. **Mitigation:** add a brief comment in `02_PATTERNS.md` reminding maintainers to update both call sites when adding patterns.

### Opportunities Discovered
- The `formula_system.py` deletion is risk-free (zero users) and a clean exemplar of Migration Policy enforcement — useful reference for future similar cleanups.
- Adding `radon`/`vulture` to dev deps unlocks ongoing complexity/dead-code scans that would catch future drift early.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
