# PROJ-489: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 1 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-490
- **Cluster identity:** modifier_service_canon — collapse triplicate modifier-validation logic onto `ModifierService` (canonical simulation-layer service)
- **Severity breakdown:** 0 CRITICAL, 1 MAJOR, 0 MINOR

## Initial Analysis
Three classes implement substantially overlapping modifier-allowed-checking logic at different layers:

| Class | Location | Layer | Role |
|-------|----------|-------|------|
| `ModifierService` | `game/simulation/services/modifier_service.py:16` | Simulation | Canonical rule engine |
| `ComponentService.is_modifier_allowed` | `game/ui/services/component_service.py:88` | UI facade | Re-implements the restriction check |
| `ModifierLogicService` | `game/ui/screens/builder/modifier_logic.py:34` | UI/Builder | Re-implements 80%+ of `ModifierService`'s surface |
| `ModifierManager.add_modifier` (inline) | `game/simulation/components/modifier_manager.py:108-117` | Component delegate | Fourth partial implementation, missing `allow_abilities` check |

Method surface overlap confirmed by verifier:

| Method | ModifierService | ModifierLogicService | ComponentService |
|--------|-----------------|----------------------|------------------|
| `is_modifier_allowed` | yes (line 62) | yes (line 66, delegates to ComponentService) | yes (line 88) |
| `get_mandatory_modifiers` | yes (line 108) | yes (line 70) | no |
| `is_modifier_mandatory` | yes (line 127) | yes (line 80) | no |
| `get_initial_value` | yes (line 181) | yes (line 84) | no |
| `get_local_min_max` | yes (line 239) | yes (line 105) | no |
| `ensure_mandatory_modifiers` | yes (line 222) | yes (line 121) | no |

Cyclomatic divergence the verifier noticed:
- `ModifierService.get_initial_value` uses generic `_has_arc_set_effect`; `ModifierLogicService.get_initial_value` hardcodes `turret_mount`.
- `ModifierService` handles `hardened_mount`, `efficiency_mount`; `ModifierLogicService` does not.
- The inline check in `ModifierManager.add_modifier` is missing the `allow_abilities` check.

### Architecture
`ModifierService` (simulation layer) is the canonical home per layered architecture. UI callers receive a `ModifierService` instance via DI; UI ergonomics (e.g. `calculate_snap_value`) remain in the UI layer but delegate validation/initial-value computations to the simulation canonical.

### Key Patterns to Reuse
- **Pattern #5 Facade/Delegate** — `ModifierLogicService` becomes a thin UI facade over `ModifierService` rather than a parallel reimplementation.
- **Pattern #15 Service** — `ModifierService` is the canonical service.

### Dependencies & Risks
1. **Behavioral reconciliation** — `_has_arc_set_effect` vs hardcoded `turret_mount` must be verified equivalent before consolidation. If `_has_arc_set_effect` is *strictly more general*, then consolidation is a quality improvement (covers new arc_set modifiers automatically). Document any cases where the strict superset behavior differs.
2. **Missing `allow_abilities` check in `ModifierManager.add_modifier`** — Adding this check may correctly reject inputs that the buggy implementation previously accepted. Run the test suite carefully and surface any test failures as either (a) legitimate test fixes or (b) flagged for the user before forcing the new behavior.
3. **UI caller injection** — 4 UI files need their construction sites updated. If `ModifierLogicService` keeps its existing constructor signature but gains a `ModifierService` parameter, the migration is mechanical.

### Opportunities Discovered
- This consolidation may surface other modifier-validation drift; if the test suite uncovers any, log them via `/claude-di-log` rather than expanding scope.
- `calculate_snap_value` could move to a free function for purity, but that's a stylistic preference — keep on `ModifierLogicService` unless the user prefers otherwise.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
