# PROJ-481: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit dir:** `Reviews/results/2026-05-20_210540_type-audit/`
- **Audit verified (5 CRITICAL + 5 MAJOR spot-checks):** zero false positives per `findings/verification.md`
- **Bundle counts:** Audit verified ~79 / This bundle: 79 verified, 0 uncertain (resolved), 0 deferred
- **Project siblings:** [PROJ-482](../PROJ-482/) (Strategy), [PROJ-483](../PROJ-483/) (Foundation + strict quick wins)
- **Layer coverage:** `game/ui/` only (1 CRITICAL + ~40 MAJOR + ~38 MINOR)
- **Severity breakdown:** Phase 1: 1 CRITICAL. Phase 2: ~40 MAJOR. Phase 3: ~38 MINOR (incl. 3 type-ignore cleanups).

## Initial Analysis
Per the source audit's heatmap, UI accounts for 76.7% of all `-> Any` returns in the codebase (263/343) and 25.6% of all missing return types (11/43). The 47 `-> Any` functions in `builder/stat_getters.py` are intentionally data-driven (JSON-config dispatch) and **excluded** from this project — narrowing them would require refactoring the entire stats registry. All other `-> Any` returns in the UI layer are either delegation properties forwarding to concretely-typed scenes/services, or public-API helpers returning well-known concrete types.

## Swarm Findings Summary
Combined analysis from `.agent_reports/2026-05-20_210540_type-audit/`:
- `verification_ui_any.md` — 43 of 49 UI items personally re-verified; 6 audit-trusted items spot-checked separately during Phase D
- `verification_missing_returns.md` — 1 UI CRITICAL (`strategy_modal_window`) and ~10 UI MINOR closures/helpers
- `verification_type_ignores.md` — 2 unjustified `# type: ignore[assignment]` (defeat_dialog cross-shard consistency includes turn_failed_dialog); 1 unjustified `# type: ignore[index]` (ship_theme_manager)

### Architecture
- **Strategy delegation cluster** (`strategy_renderer.py`, `strategy_screen.py`, `strategy_superweapons.py`, `strategy_fleet_ops.py`): 30+ property accessors forwarding to `self.scene.*`. Narrowing requires TYPE_CHECKING imports from the concrete types (`Camera`, `Galaxy`, `Empire`, etc.) to avoid runtime cycles.
- **List filter modules** (`planet_list_filters.py`, `star_list_filters.py`): module-level public helpers returning typed lists, dicts, and strings. Clear, mechanical narrowings.
- **Workshop ViewModel chain**: `WorkshopViewModel → WorkshopShipOps → VehicleDesignService` — narrow `validate_design` returns from `Any` to `DesignResult` / `ValidationResult | None` at each layer.

### Key Patterns to Reuse
- **TYPE_CHECKING string annotations** (used in many existing files): `from typing import TYPE_CHECKING; if TYPE_CHECKING: from x import Y`, then `-> 'Y'` in signature.
- **`Optional[UIButton]` constructor declaration**: established pattern in other UI dialogs for `pygame_gui` widgets that may be `None` in test-bypass paths.

### Dependencies & Risks
1. **Strategy renderer/screen delegation cluster** — circular import risk if concrete types are imported at runtime. Mitigation: `TYPE_CHECKING` imports only.
2. **gravity_target_editor / water_target_editor `_button_handlers`** — Shard 02 reviewer marked as false-positive (already annotated); Shard 03 missing-returns verifier disagreed. Task 3.12 explicitly says "verify not false positive first" before annotating.
3. **Line drift** — Two findings had line numbers that moved since the audit (TYP-01-049 `fleet_report_window.process_event` from 248 → 277; TYP-01-050 `_get_role_filter_options` from 388 → 396). Phase 3 checklists use updated lines.

### Opportunities Discovered
- All `# type: ignore[no-untyped-def]` cluster on `GameSession` lives in PROJ-482 (Strategy) — coordinated fix removes 10 ignores in one task.
- Once Phase 2 narrowings land, the strategy delegation properties become statically reusable — downstream callers' types auto-tighten.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
