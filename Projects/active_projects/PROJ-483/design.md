# PROJ-483: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit dir:** `Reviews/results/2026-05-20_210540_type-audit/`
- **Audit verified (5 CRITICAL + 5 MAJOR spot-checks):** zero false positives per `findings/verification.md`
- **Bundle counts:** Audit verified ~31 / This bundle: 31 verified (per-finding) + 6 strict-layer adoption items / 9 user-included (16 Protocol narrowings + 5 AI proto narrowings, treated as previously-UNCERTAIN-then-included) / 5 OOS (json_utils×2, ILocatable, IResourceHolder, sim entity proto subset)
- **Project siblings:** [PROJ-481](../PROJ-481/) (UI), [PROJ-482](../PROJ-482/) (Strategy)
- **Layer coverage:** `core/`, `simulation/`, `ai/`, `engine/`, `services/`, `assets/`, `research/` per-finding + Protocol modules cross-cutting strategy/UI consumers
- **Severity breakdown:** Phase 1: 1 CRITICAL. Phase 2: ~5 MAJOR. Phase 3: ~25 MINOR (incl. user-opted Protocol + AI narrowings). Phase 4: STRATEGIC strict-mode adoption.

## Initial Analysis
Foundation layers are the type-debt foundation, not bulk. Per the heatmap: services/assets/research were reported `READY NOW` (audit estimate 0 errors each); the verifier discovered services=1, assets=15 — small enough to be in scope. Engine, AI, and Core are `READY-1` / `NEAR-READY` per audit (≤30 changes apiece for per-finding cleanup, low-hundreds for strict-mode). The big leverage is in Protocol narrowing: per-finding shard reviewers flagged these as INFO (intentionally duck-typed) but the cross-layer report identified that the type erosion at the Protocol layer **propagates up through every consumer**. User opted to include the bulk Protocol narrowings (Phase 3 Tasks 3.2-3.6).

Heavy strict-mode for simulation/strategy/ui is **deferred**: verifier counts (622/1070/2571 errors) are 2.85×–5.7× the audit's estimates. Adopting strict on those layers is genuinely multi-week work and should be its own project.

## Swarm Findings Summary
Combined analysis from `.agent_reports/2026-05-20_210540_type-audit/`:
- `verification_core_strategy_sim_ai_any.md` — 20 verified per-finding items (the strategy ones live in PROJ-482; Foundation gets the rest); 9 UNCERTAIN items including all AI controllable/protocols + Protocol narrowings
- `verification_missing_returns.md` — 1 Foundation CRITICAL (`iter_for`); other missing returns belong to UI/Strategy
- `verification_strict_migration.md` — measured strict-mode counts per layer (the basis for Phase 4 scoping)

### Architecture
- **Protocol-layer type erosion** is the root cause of `-> Any` returns rippling through the consumer chain. Cross-layer report Tier 2 explicitly recommended bulk Protocol narrowing via TYPE_CHECKING string annotations (zero runtime cost). Phase 3 Tasks 3.2-3.6 implement this.
- **`stat_contributors/registry.py`** is the only CRITICAL — the `iter_for` generator method is called from `simulation/entities/ship_stats.py:307` (cross-module within simulation) so the missing return type is a real cross-module contract violation.
- **`fighter_reboard.py` overflow-group helpers** narrow to `FighterWing | SatelliteConstellation` — both types are imported in the file already.

### Key Patterns to Reuse
- **TYPE_CHECKING-guarded string annotations** (`from typing import TYPE_CHECKING; if TYPE_CHECKING: from x import Y`, then `-> 'Y'`). The Protocol files use this pattern in several existing places — extending is mechanical.
- **`pyproject.toml [tool.mypy]` or `mypy.ini` per-module overrides** for strict adoption: `[mypy-game.research.*]\nstrict = True`. Verifier confirmed no overrides currently exist.

### Dependencies & Risks
1. **Protocol-narrowing breakage** — narrowing `IPlanet.location -> 'HexCoord' | None` requires every Protocol implementer to actually return `HexCoord | None`. If any implementer returns a different type, mypy will surface a `[misc]`/`[override]` error. Phase 3 Task 3.7 explicitly verifies "no Protocol implementer breaks."
2. **`assets` regression vs audit** — audit said 0 strict errors; verifier found 15. Task 4.3 is "investigate first" — count may shift during fix.
3. **`ai` and `core` strict counts depend on Phase 3 landing first** — narrowing the AI/Protocol items at Phase 3 will drop `no-any-return` and `has-type` counts substantially before Phase 4 measures.
4. **`pop_construction_item` cross-project coordination** — narrowing the Protocol here AND the implementation in PROJ-482 must both land for consistency. Phase 3 Task 3.5 calls this out.

### Opportunities Discovered
- Narrowing Protocol returns at the source (core) propagates type precision through every downstream consumer (strategy, UI, AI) — high leverage for low LOC.
- Three layers (research, services, assets) are essentially clean and can become the codebase's first strict-typed islands quickly.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
