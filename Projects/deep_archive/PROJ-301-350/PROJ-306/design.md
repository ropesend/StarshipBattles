# PROJ-306: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Verified Findings (2026-04-26)

**Site 1 — `game/simulation/battle_runner.py:198`:**
The call lives inside `_default_ship_builder_from_context()` (lines ~170-220). The function's docstring explicitly says it's a fallback used "when callers drop the `ship_builder` kwarg." Production callers should pass `ship_builder` explicitly (PROJ-274 Phase 6). Combat Lab does this via `DesignOnlyMaterializer`. The fallback exists for non-CL callers that hadn't been migrated.

**Site 2 — `game/simulation/services/registry_loader.py:91`:**
The line-90 comment says `# PROJ-211: Pass registry_provider explicitly (no fallback)` — but the very next line calls `get_default_registry_provider()` directly, contradicting the comment. The function was clearly meant to receive a `registry_provider` parameter; the global lookup is a leftover.

### Why Now
PROJ-274 ("Unified ShipMaterializer Service") was archived. Its closure note in MEMORY.md states all 4 production `_ship_builder` closures were eliminated — but the *fallback for missing kwargs* remained. With PROJ-274 archived and the migration complete, the fallback has lost its rationale. Per System Migration Policy: "When a new system replaces an old one, ERADICATE the old system completely... DO NOT keep backward compatibility layers 'just in case.'"

## Architecture

### Pattern: Layer Separation
Documented rule: Simulation depends only on Core. Calling `get_default_registry_provider()` is fine in Core (it's the registry's own module), but in Simulation it makes the layer reach for global state instead of receiving its dependency. This violates the "Dependency Injection over Singletons" principle (CLAUDE.md §"Long-Term Quality").

### Pattern: System Migration Policy ("eradicate, don't graveyard")
Two transitional fallbacks survived PROJ-274's closure. Per the policy, both are dead code dressed up as safety nets and must be deleted.

### Key Patterns to Reuse
- **`ApplicationContext` DI** ([game/context.py](game/context.py)) — the canonical pattern for service injection. `get_default_ship_materializer()` (called at line 197) already uses this pattern; the registry provider lookup at line 198 should follow suit, OR the caller should pass it.
- **PROJ-258 closure pattern** — when removing transitional fallbacks, migrate every call site to the explicit form, then delete the fallback function. Don't leave the function callable.

### Dependencies & Risks

1. **Risk: hidden callers of `run_battle` / `BattleController.start_from_spec` that omit `ship_builder`.**
   The fallback exists because some callers do this today.
   **Mitigation:** Phase 1 starts with a grep sweep enumerating every call site. Each must either (a) pass `ship_builder` explicitly, or (b) be changed to require its caller to do so. Test failures during the sweep will surface anything the grep misses.

2. **Risk: `registry_loader.load_all_registries()` callers omit `registry_provider`.**
   Same shape of risk as Site 1.
   **Mitigation:** Same approach — grep, migrate, delete fallback. Phase 2 owns this.

3. **Risk: `TYPE_CHECKING` import of `RaceConfig` from Strategy in `game/core/protocols.py:38`.**
   The code review report flagged this as a layer-crossing concern.
   **Mitigation:** Out of scope — the import is `TYPE_CHECKING`-only (no runtime dependency) and required for `IRaceRegistry` return-type hints. Documented in PROJ-297's design.md as an acceptable trade-off. **NO ACTION** in this project.

## Key Patterns to Reuse
- **PROJ-258 / PROJ-274 / PROJ-298 closure pattern:** survey → migrate every caller → delete the transitional code in one phase. Each of those projects executed cleanly using this cadence.

## Opportunities Discovered
- The line-90 comment in `registry_loader.py` ("PROJ-211: Pass registry_provider explicitly (no fallback)") is *aspirational* — the actual code disagrees with it. After Phase 2 the comment becomes truthful. Worth keeping the comment as a reminder.
- If the `ApplicationContext` already has a default registry provider service (analogous to `get_default_ship_materializer`), an alternative to "make the parameter required" is "have callers fetch from the context themselves." Either option is acceptable; final choice in Phase 1 once we see the real call-site distribution.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
