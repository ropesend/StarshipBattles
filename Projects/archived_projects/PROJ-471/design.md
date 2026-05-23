# PROJ-471: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-20_082533_state-audit/`
- **Bundle counts:** Audit verified: 12 (its own verifier) | This bundle: 19 verified, 0 uncertain, 0 deferred | Project siblings: none (single project this run)
- **Singleton/mechanism coverage:** singleton_divergence ×8 (`_default_provider`, `_default_cache_manager`, `_default_policy_manager`, `_default_manager`, `_default_ship_theme_manager`, `_default_asset_manager`, `_default_sprite_manager`, `_default_llm_provider`); stale_bridge / dead-code ×3 (`_default_profiler`, `_default_game_settings`, `_default_image_provider`); module_mutable / class-shared-state / global ×6 (`ShipCombatEngine`, `_next_fleet_id`, `_SERIALIZABLE_REGISTRY`, `_catalog`, `exit_dialog` rects, `CREW_PRIORITY_REGISTRY`); random_seed ×2.
- **Severity breakdown:** 1 CRITICAL, 13 MAJOR, 5 MINOR.

### Risk Notes (CRITICAL / shared-state findings)

`_default_provider` (`game/core/registry.py:466`) is the highest-impact item: `get_default_registry_provider()` auto-creates a `DefaultRegistryProvider` on first access (lines 190-204) with no setter and no `ctx.registry_provider` binding, while `ApplicationContext.create_production()` (`game/context.py:162-190`) only wires `set_default_registry_manager()`. Any consumer (68+ sites across Core/Strategy/UI/App) that calls the provider accessor before `create_production()` hydrates the manager gets a `DefaultRegistryProvider` wrapping a *different*, default-constructed `RegistryManager` — silent singleton divergence with no synchronization path. `ShipCombatEngine` (`ship_combat_engine.py:41-43`) shares its `_targeting_system`/`_damage_calculator`/`_weapon_firing_system` at class level across every ship instance and across tests; `battle_setup.py:49` even overwrites `_damage_calculator` cross-module. Both are gated into Phase 1 with mandatory regression tests because they can silently corrupt state across battles/tests. The shared remediation root is the `create_production()` bridge hub — keeping the singleton family in one project avoids re-deriving that mechanic per finding.

## Initial Analysis
[Findings from Phase A code review - what was discovered about the codebase]

## Swarm Findings Summary
Combined analysis from individual agent reports in `findings/`.

### Architecture
[Key architecture points relevant to implementation]

### Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

### Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

### Opportunities Discovered
- [Opportunity 1]

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
