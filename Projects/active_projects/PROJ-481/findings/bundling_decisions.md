# Bundling Decisions (shared across PROJ-481/482/483)

**Source audit:** `Reviews/results/2026-05-20_210540_type-audit/`
**Run date:** 2026-05-22
**Driver:** `/claude-proj-from-type-audit` (Protocol 13 — Skeptical Verifier → Project Architect)

## Default Proposal (V≈109)

Per Protocol 13 Phase D Step 1, with V > 100 the default is one project per layer with ≥10 items, but the verifier observed that the audit's strict-mode estimates for `simulation/strategy/ui` were 2.85×–5.7× higher than reported (622/1070/2571 actual vs ~126/375/452 estimated). The verifier flagged this in `verification_strict_migration.md`. The default proposal therefore decoupled per-finding cleanup from heavy strict-mode adoption:

| # | Title | Layers | Verified | Strict (in scope) | Phases |
|---|-------|--------|----------|-------------------|--------|
| 1 | Type cleanup — UI per-finding | ui | ~79 | none (UI strict deferred — 2,571 errors) | Critical (1), Major (~40), Minor (~38) |
| 2 | Type cleanup — Strategy per-finding | strategy | ~28 | none (Strategy strict deferred — 1,070 errors) | Critical (4), Major (~13), Minor (~11) |
| 3 | Type cleanup — Foundation + strict quick wins | core, simulation, ai, engine, services, assets, research | ~31 | research / engine / ai / core / services / assets (with sim deferred) | Critical (1), Major (~5), Minor (~25), Strict-mode (per-layer) |

## User Adjustments
None — the default proposal was accepted as-is. User answers via `AskUserQuestion`:

1. **Overall shape:** "3 projects: UI / Strategy / Foundation (Recommended)"
2. **Protocol narrowings (16 items):** "Include — use TYPE_CHECKING string annotations (Recommended)" → bundled into PROJ-483 Phase 3
3. **AI `IControllable` / `IGridEntity` / `IProjectile` narrowings (5 items):** "Include (Recommended)" → bundled into PROJ-483 Phase 3
4. **Heavy strict-mode (sim/strategy/ui):** "Defer entirely — note as future work (Recommended)" → documented in each project's `decisions.md`

## UNCERTAIN Item Resolutions (Phase D Step 3)

| Item | Decision |
|------|----------|
| 6 UI items not opened by verifier (TYP-01-045/046/047/048/049/050) | "Quick spot-check now" — all 6 confirmed VERIFIED; two with line drift (process_event 248→277, _get_role_filter_options 388→396) |
| `_with_ship` template-method (workshop_viewmodel.py:129) | INCLUDE → PROJ-481 Phase 3 with `Any` annotation |
| `battle_assembly.py:81` cast alternative | EXCLUDE — defer, not in any project |
| `formula_evaluator._eval_node` narrowing | EXCLUDE — recursive AST evaluator, defer |
| `strategic_ability_scanner.find_*` TypedDict refactor | EXCLUDE — larger refactor, defer |
| `simulation_adapter._build_capture_context` | INCLUDE → PROJ-482 with new `ReplayCaptureContext` type |
| GameSession `# type: ignore` cluster (10 items) | INCLUDE as ONE combined task → PROJ-482 Phase 1 |

## Final Bundle Definitions

### PROJ-481 — Type cleanup — UI per-finding
- ~79 verified items across `game/ui/` only
- 3 phases: Critical (1), Major (~40), Minor + ignore cleanup (~38)
- Excludes `builder/stat_getters.py` (47 INFO data-driven), UI strict adoption (2,571 errors)

### PROJ-482 — Type cleanup — Strategy per-finding
- ~28 verified items across `game/strategy/` and `game/strategy/engine/` (incl. session/commands/superweapon_handlers/handlers/services/adapters/data)
- 3 phases: Critical (4 — GameSession combined cluster + `_registry` + `_get_nav_service` + `primary_star`), Major (~13), Minor (~11)
- Includes one UNCERTAIN item (`_build_capture_context` with new `ReplayCaptureContext` type) per user opt-in
- Excludes Strategy strict adoption (1,070 errors)

### PROJ-483 — Type cleanup — Foundation + strict quick wins
- ~31 verified items: core/registry, sim simulation systems narrowings, evaluate_recursive, planet_write_service.pop_construction_item, AI controllable/protocols cluster (5 items), Protocol narrowings (16 items)
- 1 CRITICAL: `iter_for` in `stat_contributors/registry.py`
- Phases: Critical (1), Major (~5), Minor (~25), Strict-mode (research config + engine/ai/core/services/assets fixes)
- Excludes simulation strict adoption (622 errors) — defer to a future dedicated project

## Why Code Locality, Not Severity
Implementation continuity. A single Edit pass through `strategy_renderer.py` to narrow its 11 properties is mechanical; spreading them across 3 severity-keyed phases would force the implementer to keep re-opening the same file. Severity drives **phase ordering within a project**, not bundle boundaries.

## Strict-Mode Calibration Notes
The verifier's actual mypy `--strict` runs found:
- `research`: 0 (matches audit, config-only enable) → PROJ-483 Strict phase
- `engine`: 14 errors (audit said ~5) — within ±50% → PROJ-483 Strict phase
- `ai`: 60 errors (audit said ~54) — accurate → PROJ-483 Strict phase
- `core`: 116 errors (audit said ~85) — within ~36% → PROJ-483 Strict phase
- `services`: 1 error (likely env stub) → PROJ-483 Strict phase
- `assets`: 15 errors (audit said 0) — regressed → PROJ-483 Strict phase (with investigation note)
- `simulation`: 622 errors (4.9× audit) → DEFERRED
- `strategy`: 1070 errors (2.85× audit) → DEFERRED
- `ui`: 2571 errors (5.7× audit) → DEFERRED
