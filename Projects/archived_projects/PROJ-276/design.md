# PROJ-276: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation.

## Initial Analysis

`ShipInstance` in [game/strategy/data/ship_instance.py:113-124](../../../game/strategy/data/ship_instance.py) carries two component-HP stores:

```python
component_damage: Dict[str, int] = field(default_factory=dict)
# component_id -> current_hp (legacy; single-instance granularity)

components: Dict[str, ComponentState] = field(default_factory=dict)
# PROJ-269 Phase 2: per-component-instance persistent state.
# Key format: "{component_id}#{instance_index}"
```

The docstring at L122-123 admits the transitional bridge:
> `component_damage` above is kept in sync for backwards-compatible stat calculations during the PROJ-269 transition.

**The real bug:** `component_damage` is structurally lossy. A ship with three seeker missile components (same `component_id`) cannot represent "#2 damaged, #1 and #3 intact" — the dict collapses them to one HP value. The post-battle hook rebuilds this lossy form from the per-instance authoritative data.

**Counted occurrences** (read-only sweep 2026-04-16):

| Location | Sites | Role |
|----------|-------|------|
| `game/strategy/data/ship_instance.py` | 8 | Field definition + ctor + docstring |
| `game/strategy/services/ship_stats_calculator.py` | **20** | Reads (stat calc) |
| `game/strategy/data/ship_instance_bridge.py` | 6 | ShipInstance → Ship construction |
| `game/strategy/combat/post_battle_hook.py` | 6 | Post-battle writes (dual) |
| `game/strategy/data/ship_instance_serializer.py` | 3 | Save/load |
| `game/strategy/data/component_state.py` | 2 | New DTO |
| `game/simulation/entities/ship_design_stats.py` | 4 | Design-time stats |
| `tests/fixtures/strategy_entities.py` | 1 | Fixture |
| **Production total** | **~47** | |
| 10 test files | ~29 | Tests |

`ship_stats_calculator.py` has 20 occurrences — the hardest migration. It's a stat calculation hot path.

## Swarm Findings Summary

### Architecture
- `ComponentState` in `game/strategy/data/component_state.py` is the new authoritative DTO (introduced in PROJ-269 Phase 2)
- Key format: `{component_id}#{instance_index}` — `component_state_key(component_id, instance_index)` helper
- Post-battle hook at `game/strategy/combat/post_battle_hook.py:152` is the authoritative writer for `components`
- Post-battle hook at L155-162 is the LEGACY writer for `component_damage` — this is the dual-write that must be deleted

### Key Patterns to Reuse
- **PROJ-269 `ComponentState` DTO** — already defined, already written to by battle outcome extraction
- **`component_state_key(component_id, instance_index)` helper** — use everywhere instead of reconstructing keys
- **Clean-Sheet Rule** (CLAUDE.md) — delete, don't deprecate
- **System Migration Policy** (CLAUDE.md) — no backward compat layers; "Save files are disposable. Old saves are not migrated — they are discarded."

### Dependencies & Risks
1. **Risk: stat calculator hot path.** `ship_stats_calculator.py` with 20 sites is the hardest migration. A bug here affects every strategy-layer HP display and derived stat. Mitigation: TDD per site, parity tests comparing old single-instance computation to new per-instance computation on single-instance ships (should be identical).
2. **Risk: multi-instance ships will CHANGE behavior.** A ship with 3 seekers where #2 was damaged currently has ALL 3 reported at partial HP via the flattened dict. After migration, only #2 is at partial HP. This is a BUG FIX, not a regression — but test baselines may shift. Document this as expected behavior change in decisions.md.
3. **Risk: save compat.** Anyone with an in-flight save loses it. User policy covers this.
4. **Dependency: ShipInstance docstring reads as "PROJ-269 transition."** The transition has been "in progress" for multiple phases. This project is the eradication/closure. Treat it as completing PROJ-269 Phase 2.
5. **Risk: test fixtures at `tests/fixtures/strategy_entities.py`.** Fixture has `component_damage=...` in construction — all downstream tests that rely on this fixture need verification.

### Opportunities Discovered
- Removing the dual-write at L155-162 of post_battle_hook.py is a net LOC reduction and eliminates a known lossy conversion.
- Multi-instance weapons (already-present ships with 2+ seekers) will finally behave correctly after the migration. The seeker Combat Lab scenarios in `memory/MEMORY.md` may surface expected-but-previously-masked behavior.

## Design Decisions

See [decisions.md](decisions.md).

## Migration Strategy — Per-Site TDD

For each of the 47 production call sites:

1. **Classify** the site as READ (reads `component_damage` to make a decision) or WRITE (writes to `component_damage`).
2. **For READ sites**: write a failing test that proves current behavior on a SINGLE-instance ship, then a NEW test asserting correct per-instance behavior on a MULTI-instance ship. Migrate the read to use `components[component_state_key(...)].current_hp`. Both tests pass.
3. **For WRITE sites**: either (a) delete the write entirely if it's the dual-write in post_battle_hook, or (b) redirect to write a `ComponentState` to `components`.
4. **Parity tests** after each migration group — confirm single-instance ships produce identical stats before and after.

## `ComponentState` API Check

Before migrating 20 sites in `ship_stats_calculator`, confirm `ComponentState` exposes everything the old reads needed:

- `current_hp: int` — confirmed
- `is_destroyed: bool` — confirmed (current_hp <= 0)
- `is_operational: bool` — must derive from ability state; verify `ComponentState` surfaces this
- Keyed access via `component_state_key(component_id, instance_index)` — verify helper exists

If `ComponentState` is missing any API, extend it in Phase 1 as a prerequisite for Phase 2.

## Phase Ordering Rationale

Phase 1 (audit) → Phase 2 (stat_calc, the biggest) → Phases 3-4 (smaller files) → Phase 5 (serializer; save format bump) → Phase 6 (field deletion; pass-point where backward compat is severed) → Phase 7 (tests) → Phase 8 (docs).

Phase 6 is the deletion pass — from then on, no `component_damage` exists in the codebase. Earlier phases must leave all production behavior green before that point.
