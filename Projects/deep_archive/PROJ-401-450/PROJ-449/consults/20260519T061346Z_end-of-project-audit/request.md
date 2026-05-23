---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T06:13:46Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-449 — End-of-Project Audit Consult

## Context

PROJ-449 ("Strategy entity wrapper retirement") just closed all 6 phases on the
`group-a` branch. The project retired:

- The `_planet_init_with_legacy_kwargs` constructor wrapper at
  `game/strategy/data/planet.py` (gone — moved private fields are now the only
  accepted kwarg names on the dataclass `__init__`).
- The `_ship_instance_init_with_legacy_kwargs` constructor wrapper at
  `game/strategy/data/ship_instance.py` (gone — same shape).
- The `@setter` halves of the `stockpile` / `max_stockpile` / `staging_yard`
  property/setter cluster on `Planet`.
- The `@setter` halves of the `consumable_levels` / `cargo_contents`
  property/setter cluster on `ShipInstance`.

**Scope adjustment from the original plan** (decisions.md row 2026-05-18 "Phase
3 scope adjustment"): The Phase-0 audit under-counted READ sites (16 production
files + ~50 test files read `planet.stockpile` / `.max_stockpile` /
`.staging_yard` and equivalents on `ShipInstance`). Original plan called for
getter-AND-setter deletion. Final outcome: kept the read-only `@property`
getters as views over the private fields, deleted only the `@setter` halves.
This closes F-A-002/003 fully and substantially closes F-A-004/005 (the
substrate-widening seam that the setter cluster opened is now gone).

Project did NOT do (deliberate):

- `PlanetaryFacility.consumable_levels` kwarg rename — F-A-012 deferred (the
  public dataclass field stays; a future project may take it on).
- `ship_instance.py` LOC reduction — F-A-007 stays at 783 LOC post-Phase-4;
  PROJ-459 Phase 3 will decide the spin-out after measuring post-PROJ-454
  state too.
- `Empire.resource_pool` caching — F-A-011 closed without code change (Phase 6
  profile showed no hot signal at realistic UI workload).

Final sharded baseline: **23375 tests / 23375 passed / 0 failed / 0 errors**.

## Files modified across the 6 phases (high-level)

- `game/strategy/data/planet.py` — wrapper deleted, 3 @setters deleted, 3
  read-only @property getters retained.
- `game/strategy/data/planet_serde.py` — `planet_from_dict_kwargs` emits
  private kwargs; `planet_to_dict` reads private fields directly.
- `game/strategy/data/ship_instance.py` — wrapper deleted, 2 @setters
  deleted, 2 read-only @property getters retained.
- `game/strategy/services/planet_write_service.py` — `set_max_stockpile`
  writes the private field directly.
- `game/strategy/engine/issuer_adapter.py` — recovered-staging-yard rewrite
  writes the private field directly.
- `game/strategy/data/ship_consumable_manager.py` — `replace_levels` writes
  the private field directly.
- `game/core/protocols/strategy_domain.py` — `IShipInstance.cargo_contents`
  docstring rewritten (closes F-C-014).
- `tests/fixtures/strategy_entities.py` — 4 fixture sites migrated to
  private kwargs (line 140 stays public for PlanetaryFacility).
- ~35 other test files modified (constructor-kwarg renames + attribute-setter
  migrations).
- 2 new static guards: `tests/static_guards/test_no_planet_legacy_kwarg_wrapper.py`,
  `tests/static_guards/test_no_ship_instance_legacy_kwarg_wrapper.py`.

## Commit range on `origin/group-a`

```
b3d698f9c PROJ-449 Phase 0: audit complete — clean PROCEED
d531b430a PROJ-449 Phase 1: migrate strategy_entities.py 4 sites to private kwargs
23d87ed84 PROJ-449 Phase 2: sweep test call sites + rewrite planet_from_dict_kwargs
f4503847a PROJ-449 Phase 3: delete Planet legacy-kwarg wrapper + 3 setters
aac714ce4 PROJ-449 Phase 4: delete ShipInstance legacy-kwarg wrapper + 2 setters
a75e4c9ca PROJ-449 Phase 5: drop IShipInstance.cargo_contents 'not read-only' caveat (closes F-C-014)
2a69c7f26 PROJ-449 Phase 6: profile Empire.resource_pool, no hotspot signal (closes F-A-011)
```

## What I want you to do

Audit the closed project end-to-end. The four things I most want a second
opinion on:

### 1. Verify each finding's closure status against current HEAD

For each finding declared closed, confirm by reading the cited code that the
closure claim is accurate:

- **F-A-002 (wrapper)**: confirm `_planet_init_with_legacy_kwargs` is gone
  from `game/strategy/data/planet.py`. Confirm no other module re-assigns
  `Planet.__init__`.
- **F-A-003 (wrapper)**: same for `_ship_instance_init_with_legacy_kwargs`.
- **F-A-004 (Planet setter cluster)**: confirm the 3 @setter blocks on
  `stockpile` / `max_stockpile` / `staging_yard` are gone. Note the read-only
  getters are intentionally retained.
- **F-A-005 (ShipInstance setter cluster)**: confirm the 2 @setter blocks on
  `consumable_levels` / `cargo_contents` are gone.
- **F-C-014 (IShipInstance.cargo_contents docstring caveat)**: confirm the
  "not read-only in absolute terms" caveat is gone from
  `game/core/protocols/strategy_domain.py`.
- **F-A-011 (Empire.resource_pool caching)**: closed-without-code-change.
  Sanity check the profile conclusion against a brief re-reading of
  `game/strategy/data/empire.py`'s `resource_pool` property.

### 2. Sanity-check the Phase-3 scope adjustment

The original plan said "delete property/setter PAIRS". The final outcome
deleted only the setters and kept the getters as read-only views. The
decision rationale (decisions.md 2026-05-18 row "Phase 3 scope adjustment"):

- Audit under-counted read sites; getter deletion would require migrating
  16 production files + ~50 test files
- Setters were the substrate-widening seam (PROJ-450 cares about this)
- Read-only getters don't fight type safety and don't block PROJ-450

Is this the right call, or does keeping the getters leave a meaningful seam
that a future project will have to clean up? Specifically: would a future
codex audit at the next big-rewrite ask "why is there a `@property` getter
when callers could just read `_stockpile` directly?" If yes, suggest the
contour of that follow-up project (read sweep + delete getters).

### 3. Look for residue / missed sites

The Phase-2 sweep was mechanical; the Phase-3/4 setter migration was a
second mechanical sweep delegated to a subagent. Both might have missed
sites that the wrapper translates silently.

- Run a search for `planet.stockpile = ` / `.max_stockpile = ` / 
  `.staging_yard = ` across `game/` and `tests/`. Verify each remaining
  occurrence is targeted at a MagicMock / SimpleNamespace / unrelated
  class (not a real Planet).
- Same for `ship.consumable_levels = ` / `.cargo_contents = ` against
  ShipInstance.
- Same for constructor kwargs: `Planet(stockpile=...)`, `Planet(max_stockpile=...)`,
  `Planet(staging_yard=...)`, `ShipInstance(consumable_levels=...)`,
  `ShipInstance(cargo_contents=...)`. Each remaining match should be
  through a fixture helper that goes through `**defaults` (and the
  private spelling is used in defaults).

Surface any real-target site that was missed.

### 4. Identify newly-discovered nearby residue

Same bucket-scan shape as the original PROJ-444 audit. Things in
`game/strategy/data/` and `game/core/protocols/` (the project's primary
ownership area) that look like residue from previous projects (compat
shims, deprecated kwargs, lying docstrings, dead branches) — anything
that a follow-up project should sweep.

## Output schema

Standard consult/v1 response.md per the harmonized schema:

- `## Findings` — per finding (one block per concern). Each must cite
  `file:line` evidence. Label unverified claims `[unverified]`.
- `## Risks` — anything that might break later (e.g., if PROJ-450 adds
  a typed `staging_yard` getter return type, will the existing read-only
  getter need adjustment?).
- `## Open questions` — anything you couldn't answer from a read-only
  inspection. Don't speculate.
- Set `exit_status: ok` if no blockers; `exit_status: needs-fixes` if
  the audit found a verified issue that requires code change before
  the project closes.

## Constraints

(Inline-include the canonical Constraints block from
`AgentCoordination/protocols/consult_prompt_block.md`.)

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

This consult has `allow_tests: false` and `mode: planning` — read-only inspection only.
