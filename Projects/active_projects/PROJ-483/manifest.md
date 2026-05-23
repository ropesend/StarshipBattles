# PROJ-483 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/simulation/entities/stat_contributors/registry.py | Production | Phase 1: `iter_for` generator annotation |
| game/simulation/systems/attack_processor.py | Production | Phase 2: `_spawn_from_carried_vehicle` |
| game/simulation/systems/fighter_reboard.py | Production | Phase 2: 2 overflow-group narrowings |
| game/core/registry.py | Production | Phase 2: `get_validator` × 2 |
| game/simulation/components/component_stats_calculator.py | Production | Phase 2: `evaluate_recursive` |
| game/ai/interfaces/controllable.py | Production | Phase 3: 3 narrowings |
| game/ai/protocols.py | Production | Phase 3: 2 narrowings |
| game/core/protocols/strategy_entities.py | Production | Phase 3: bulk TYPE_CHECKING narrowings (up to 12) |

> Note: 2026-05-22 post-merge note: PROJ-470 (commit `97b427097`) already narrowed `IAbilitySource.source_kind` from `str` → `SourceKind` (StrEnum) at `game/core/protocols/strategy_entities.py:395`. Item count effectively drops from 12 to ~11. Verify during Phase 3 implementation; don't re-narrow.

| game/core/protocols/ui.py | Production | Phase 3: 3 `ICamera` narrowings |
| game/core/protocols/strategy_domain.py | Production | Phase 3: 2 `IEmpire` narrowings |
| game/core/protocols/strategy_mutators.py | Production | Phase 3: `IPlanetMutator.pop_construction_item` (coordinate w/ PROJ-482) |
| game/simulation/interfaces/entity_protocols.py | Production | Phase 3: up to 7 narrowings (ICombatShip + IProjectile) |
| mypy.ini OR pyproject.toml | Config | Phase 4: per-module strict overrides for research/services/assets/engine/ai/core |
| game/research/ | Production | Phase 4: 0 changes (config-only) |
| game/services/llm/deepseek.py | Production | Phase 4: likely fix for `requests` stub |
| game/assets/ | Production | Phase 4: fix 15 strict errors |
| game/engine/ | Production | Phase 4: fix 14 strict errors |
| game/ai/ | Production | Phase 4: fix remaining strict errors after Phase 3 narrowings |
| game/core/ | Production | Phase 4: fix remaining strict errors after Phase 3 narrowings |
| docs/03_CONVENTIONS.md | Doc | Phase 4 final task — note new strict layers |
