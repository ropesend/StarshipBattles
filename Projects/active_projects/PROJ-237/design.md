# PROJ-237: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
- **No planet energy system exists** — energy only exists on ships (fuel, energy, ammo in `data/resources.json`). Planet resources are mining-only (Metals, Organics, Vapors, Radioactives, Exotics).
- **Planets don't participate in combat** — combat is purely ship-to-ship in the simulation layer. Planets are strategy-layer entities only.
- **Planet destroyers are strategic orders** — `SuperweaponOrderProcessor.process_implode_planet()` simply removes the planet from the galaxy. No combat involved.
- **`PlanetaryFacility` has `resource_levels` dict** used for fuel — this pattern extends to energy tracking.
- **Fleet orders system** is well-established with `FleetOrder`, `OrderType`, `ActionExecutionEngine`, and `FleetOrderProcessor`. Planet orders will mirror this architecture.
- **Starting complexes** are JSON design files in `tests/fixtures/quickstart/designs/`, spawned by `quickstart_builder.py`.

### Architecture Compliance
All new code fits cleanly within the existing layer structure:
- **Simulation layer** (`game/simulation/`): Ability classes (data definitions only, no behavioral coupling)
- **Strategy layer** (`game/strategy/`): Engines, order processors, command handlers, data model changes
- **UI layer** (`game/ui/`): Display formatting only
- No reverse dependencies or layer violations introduced.

## Swarm Findings Summary

### Architecture
- Module placement is correct: abilities in `game/simulation/components/abilities/`, engines in `game/strategy/engine/`
- No layer violations detected across all proposed changes
- TurnEngine integration uses existing lazy-property + DI pattern (2 new injectable engines)
- Two new tick phases: 0c1 (energy, after fuel gen) and 1.6 (planet actions, after fleet actions)

### Key Patterns to Reuse
- **Component scanning**: `iter_components()` + `get_component_abilities()` + registry lookup — `harvesting_engine.py:35-80`
- **Storage recalculation**: `HarvestingEngine.recalculate_storage()` pattern — recalculate capacity each tick for mid-turn changes — `harvesting_engine.py:144-168`
- **Action execution**: `execution_progress` tracking + `ActionTimeResolver` — `action_execution_engine.py:105-183`
- **Command handlers**: `BaseCommandHandler._resolve_planet()` + validator delegation — `superweapon_command_handlers.py`
- **Serialization**: `.get()` with defaults for backward compatibility — `planet.py:338-350`
- **Engine DI**: Lazy properties with runtime import in TurnEngine — `turn_engine.py:229-329`
- **Ability classes**: Marker abilities with `STAT_BINDINGS = []` and data parsing — `harvester.py:11-44`

### Dependencies & Risks
1. **Mid-turn facility destruction** (HIGH) — Generator/battery/shield scuttled by maintenance mid-turn invalidates cached values. **Mitigation**: Recalculate capacity and generation from scratch each tick (like `recalculate_storage()`). If shield facility destroyed, auto-deactivate shield.
2. **Energy underflow** (MEDIUM) — Shield drains more than available energy. **Mitigation**: Check `energy >= drain_rate_per_tick` before draining; auto-deactivate and clamp to 0 if insufficient.
3. **Planet order conflicts** (MEDIUM) — Multiple conflicting orders queued. **Mitigation**: Guard execution with state checks; skip redundant orders (e.g., ACTIVATE when already active).
4. **IPlanet protocol** (LOW) — New fields must be added to protocol for UI binding. Straightforward update.
5. **Save compatibility** (LOW) — Old saves missing new fields. **Mitigation**: All new fields use `.get()` with safe defaults (0.0, False, []).

### Opportunities Discovered
- The planet orders framework provides a clean foundation for future planet-level actions (launching fighters, converting resources, toggling other components)
- Energy system could later power production facilities, defensive turrets, etc.
- Component states tracking (`PlanetaryFacility.component_states`) is a generic mechanism usable for any toggleable component

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
