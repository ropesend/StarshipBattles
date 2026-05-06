# PROJ-359: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/)
- **Type:** Technical Debt Review
- **Date:** 2026-05-04
- **Report:** [View Full Report](../../../Reviews/results/2026-05-04_211026_tech-debt_realtime-combat-layer-maintainability-extensibilit/report.md)
- **Source finding:** #4 — "Weapon behavior is hardcoded in several systems" (P2 extensibility, largest leverage)

## Initial Analysis

### Bug location (string/class dispatch sprawl)
- `game/simulation/combat/weapon_firing_system.py:198,221,236` — `_create_attack` branches on `comp.has_ability('BeamWeaponAbility')` then on `comp.has_ability('SeekerWeaponAbility')`; emits dict-shaped attack payloads.
- `game/simulation/combat/targeting_system.py:123` — knows about PDC and seeker rules separately.
- `game/engine/collision.py:68` — `process_beam_attack` consumes the dict-shaped attack carrier inside the engine layer (simulation-layer semantics leak).
- `game/simulation/projectile_manager.py:130` — projectile hit application is its own damage path.

### Why it matters
Every new weapon family today requires coordinated edits to all four files plus telemetry and outcome handling. The dict-carriers leak simulation semantics into `game/engine/`, which the layer architecture says should not own combat semantics.

### Architecture
- Layer boundaries (per `docs/01_ARCHITECTURE.md`): Simulation owns combat semantics; Engine owns physics/collision primitives. Today simulation semantics flow into engine via dict carriers — refactor pulls them back behind a typed contract.
- The Ability-Stat Registry pattern (`game/simulation/combat/ability_stat_registry.py`, PROJ-273) is a precedent: a single registry replaces what was previously hardcoded across multiple files. The weapon registry should follow the same shape (one mapping per family, lookup at the dispatch site).

## Key Patterns to Reuse
- **Registry pattern** — `ABILITY_STAT_REGISTRY` shape and `KNOWN_EXTERNAL_STAT_KEYS` allow-list for unknown-family detection.
- **Protocol + TypeGuard** — `is_combat_ship` (per `docs/02_PATTERNS.md` §2) for typing-narrowing the attack source/target.
- **PROJ-273-style glob test** — a glob-driven test that iterates every weapon design and validates its family resolves to a registered handler.

## Phasing rationale
Strict TDD per AGENTS.md. The four phases reflect risk gradient:
- **Phase 1 (golden tests)** locks current observable damage events for Beam / Projectile / Seeker / PDC. Zero behavior change. Lowest risk; highest insurance value for what follows.
- **Phase 2 (typed contract behind dispatch)** introduces `AttackRequest` / `AttackResolution` and the registry skeleton, but *every* dispatch still routes through the legacy string-class branch. Tests still pass on existing code because the contract is unobservable. Allows incremental migration.
- **Phase 3 (migrate one family at a time)** moves Beam, then Projectile, then Seeker, then PDC behind the registry. Each family migration is an independent commit; rollback is one-file. Phase 1's golden tests guard each step.
- **Phase 4 (delete legacy)** removes the now-unused string branches and dict carriers. Pure deletion, locked by the now-extensive test corpus.

## Dependencies & Risks
1. **Cross-cutting refactor** — the largest of the 5 review-derived projects. Mitigation: phasing above; per-family commits in Phase 3.
2. **Engine-layer dict carriers in `collision.py:68`** — pulling these behind a typed boundary may surface other engine consumers we don't expect. Phase 2 should grep for every dict-carrier consumer before introducing the typed contract.
3. **Telemetry / outcome shapes** — `combat/telemetry.py:HitLogRecorder._on_hit_event` (complexity C(17) per the review's Radon notes) consumes attack metadata. Verify Phase 2 contract doesn't break telemetry; if it does, telemetry update is in-scope.
4. **Overlap with PROJ-360** — the ShipStatsCalculator decomposition may want to consume the typed contract once it exists. PROJ-360 sequences after this project deliberately.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
