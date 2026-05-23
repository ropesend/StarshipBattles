# Bundling Decisions — PROJ-466

Source audit: `Reviews/results/2026-05-20_065518_error-audit/` (run 2026-05-20).

## Default proposal

27 VERIFIED items, V < 30 → protocol 14 Phase D Step 1 default = **ONE project, all layers in one bundle**, phases ordered by severity.

| # | Title | Layers | Verified | Uncertain | Phases (severities) |
|---|-------|--------|----------|-----------|---------------------|
| 1 | Error handling cleanup — session-init crash + exception hygiene (2026-05-20) | ui, strategy, simulation, services, core, assets | 27 | 4 (raised) | 1 Critical, 2 Major, 3 Minor |

Totals: VERIFIED 27 / UNCERTAIN 4 (raised) / REJECTED 1 / OUT_OF_SCOPE 4.

## Autonomous-override consult

Per the autonomous-override contract (no human pause), a single Codex consult (planning mode) was run on the bundling and the 4 uncertain decisions. Response: `AgentCoordination/Scratchpad/Consult/20260521T031047Z_err-audit-bundle/response.md`.

- **Codex on bundling:** keep one project — protocol default for V<30, the highest-risk work is code-coupled (the two session-init files), and the rest is low-effort hygiene; splitting adds overhead faster than it reduces risk.
- **Codex on uncertain items:** include 2b (satellite_controller); drop 2a (construction_queue comment-only), 2c (strategy_screen_assets narrow typed catch), 2d (star_list_window defensible UI responsiveness).

## Final decisions (initiator owns the call)

- **Bundling:** ONE project (PROJ-466). Agreed with Codex and protocol default. No siblings this run.
- **Phase ordering:** Phase 1 = CRITICAL session-init boundary + the coupled MAJOR (`new_game_setup_controller.py`); Phase 2 = remaining 10 MAJOR; Phase 3 = 15 MINOR.
- **Cross-layer placement:** the two `cross_layer_boundary` items live in Phase 1 (upstream-end / detecting layer = ui callers of `GameSession`). `XLAYER-MAJ-1` (context merge) sits in Phase 2 with the strategy-layer engine fixes.

### Per-UNCERTAIN-item decisions

| item | decision | rationale |
|------|----------|-----------|
| satellite_controller.py:106-109 (get_position) | **Include** (Phase 3 Task 3.12) | Only one of three AttributeError catches lacking a rationale/diagnostic; pure observability gain, no behavior change; audit flagged the asymmetry. |
| construction_queue.py:186 (_load_design_cost) | **Defer** | Already logs; a bare "add a comment" task is low-leverage and would normalize an ambiguous zero-cost fallback that is really a design question. |
| strategy_screen_assets.py:76 | **Defer** | Already a narrow typed catch with a logger.warning; broad-catch comment rule targets `except Exception`; graceful degradation for optional art is sanctioned by docs/05. |
| star_list_window.py:395 | **Defer** | Audit itself calls it defensible for UI responsiveness; debug logging routine typos is noise. |

Deferred items are recorded in `verification_report.md` under "Uncertain (resolved)" for a future audit pass; they are not in any phase checklist this run.
