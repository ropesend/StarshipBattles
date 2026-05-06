# PROJ-371: Strategy Command Dispatch Registry (replace hardcoded specs.py table)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-371` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-371 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Introduce `CommandRegistry` + decorator alongside existing tuple (bit-identical) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate consumers to registry; delete `specs.py` tuple; collapse facade forwarders | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Authoring rule doc + AST regression + third-party-command smoke test | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State

**Last Updated:** 2026-05-05
**Active Phase:** 2 (about to start)
**Last Action:** Phase 1 complete. `CommandRegistry`, `@command_spec` decorator
(metadata-only), `seed_default_commands`, `reset_command_registry` shipped
in `game/strategy/engine/commands/registry.py`. All 35 handler classes
decorated and per-module `register(registry)` functions added. Bit-identity
contract test (`tests/unit/strategy/engine/test_command_registry_seeding.py`)
passes with 10 tests including the metadata-only-decorator invariant
(`test_import_handler_module_does_not_register`). `specs.py` re-exports
`CommandSpec`/frozensets/etc. from registry; the literal tuple is unchanged.
Strategy engine + facade + services tests: 2128 passing, 0 regressions.
**Next Action:** Phase 2 — migrate `registry_factory.py`,
`action_time_resolver.py`, `command_dispatch_slice.py` consumers to
`command_registry`; collapse facade `dispatch_*` forwarders to
`__getattr__`; delete `specs.py`.
**Blockers:** None.

## Overview

`game/strategy/engine/commands/specs.py` (661 LOC, 35 `CommandSpec` rows)
consolidates command-routing metadata that was previously scattered across
seven files. PROJ-363 (closed) landed that consolidation — which means the
strategy-layer review's "8 edits across 3-5 files per new command" claim is
already partially out-of-date. **Today's actual state:** adding a 36th command
requires 4 edits (DTO, handler, spec row, facade forwarder) plus 1 conditional
(new OrderType). PROJ-371 takes the consolidation one step further: the spec
table becomes a self-registering `CommandRegistry` populated by a
`@command_spec(...)` decorator on each handler class. After this project,
adding a 36th command requires **one new file** — a handler module that
self-registers.

The project ALSO collapses the 31 hand-written `dispatch_*` forwarders in
`strategy_session_facade.py:186-300` (missed by PROJ-363 Phase 4) into a
single `__getattr__` resolver, mirroring the slice-level resolver landed by
PROJ-363.

## Goals

- **Phase 1:** `game/strategy/engine/commands/registry.py` exists with
  `CommandRegistry` class, global `command_registry` instance, and
  `@command_spec(...)` decorator. The 35 existing handler classes are decorated
  in their domain modules (`engine/handlers/*.py`,
  `engine/planet_command_handlers.py`, `engine/superweapon_command_handlers.py`).
  Both the decorator-driven registry AND the existing `specs.py` tuple
  populate identically; a contract test asserts bit-identity. Zero consumer
  migration; zero behaviour change.
- **Phase 2:** Three production consumers (`registry_factory.py`,
  `action_time_resolver.py`, `command_dispatch_slice.py`) migrate from
  `COMMAND_SPECS` to `command_registry`. The 31 hand-written `dispatch_*`
  forwarders in `strategy_session_facade.py:186-?` collapse into `__getattr__`
  proxying to `self._command_slice.dispatch_*`. The cross-link test
  `tests/unit/strategy/services/test_superweapon_registry_contract.py`
  (PROJ-364) updates to read `command_registry.all()`. `specs.py` is
  **deleted**; `data/order_types.py` frozensets stay (they're pinned to the
  registry by an updated contract test). The redundant local
  `MOVEMENT_ORDER_TYPES` frozenset at `action_time_resolver.py:48` is
  deleted as part of the migration.
- **Phase 3:** AST regression test forbidding any `COMMAND_SPECS = (...)`
  tuple-literal reintroduction. End-to-end smoke test that registers a
  `FakeModCommand` + `FakeModCommandHandler` at test setup, dispatches via
  `facade.handle_command(FakeModCommand(...))`, asserts the handler ran, and
  unregisters cleanly without breaking other tests.
  `docs/systems/strategy_layer.md` gains an authoring-rule section
  ("How to add a new command") with the canonical pattern.

Cross-cutting goal: **zero behaviour change** at every phase boundary. The
sharded suite (currently 15405 passing per memory) must stay green.
Pass count grows with new tests added in Phase 1 (bit-identity contract) and
Phase 3 (AST regression + third-party smoke test).

## Scope

**In:**

- `game/strategy/engine/commands/registry.py` (new) — `CommandSpec` dataclass
  (moved from `specs.py`), `CommandRegistry` class, `command_registry`
  singleton, `@command_spec(...)` decorator, `seed_default_commands()`,
  `reset_command_registry()` (test helper), helper-function instance
  methods (`movement_order_types`, `action_order_types`,
  `planet_action_order_types`, `order_to_ability_map`, `specs_by_command_name`,
  `specs_by_facade_helper`, `order_types_for_category`).
- `game/strategy/engine/handlers/{base,build,construction_queue,movement,
  order_queue,transfer}.py` — Phase 1 adds `@command_spec(...)` decorator
  above each handler class definition.
- `game/strategy/engine/planet_command_handlers.py` — same (7 handlers).
- `game/strategy/engine/superweapon_command_handlers.py` — same (11 handlers).
- `game/strategy/engine/commands/specs.py` — kept in Phase 1 (bit-identical
  redundancy), **deleted** in Phase 2.
- `game/strategy/engine/handlers/registry_factory.py` — Phase 2: read from
  `command_registry` instead of `COMMAND_SPECS`.
- `game/strategy/services/action_time_resolver.py` — Phase 2: read from
  `command_registry.order_to_ability_map()`. Delete the redundant local
  `MOVEMENT_ORDER_TYPES` frozenset at line 48.
- `game/strategy/facade/slices/command_dispatch_slice.py` — Phase 2: read
  from `command_registry.specs_by_facade_helper()`.
- `game/strategy/facade/strategy_session_facade.py` — Phase 2: collapse 31
  hand-written `dispatch_*` forwarders into `__getattr__`.
- `tests/unit/strategy/engine/test_command_specs_contract.py` — Phase 2:
  migrate imports from `commands.specs` to `commands.registry`. Test names
  unchanged; assertions update mechanically.
- `tests/unit/strategy/engine/test_command_registry_contract.py` — already
  exists; no changes (it tests the surface, not the spec module).
- `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` —
  Phase 2: update import; add a `test_facade_dispatch_proxies_to_slice` test
  for the new `strategy_session_facade.__getattr__`.
- `tests/unit/strategy/services/test_superweapon_registry_contract.py` —
  Phase 2: update PROJ-364 cross-link to read `command_registry.all()`.
- `tests/unit/strategy/engine/test_command_registry_seeding.py` (new, Phase 1)
  — bit-identity contract: `set(spec.command_class for spec in COMMAND_SPECS)
  == set(s.command_class for s in command_registry.all())`. Asserts every
  field on every spec matches.
- `tests/unit/strategy/engine/test_command_registry_thirdparty.py` (new,
  Phase 3) — registers a fake mod command, dispatches it, unregisters it.
- `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` (new, Phase 3)
  — AST regression forbidding any `COMMAND_SPECS = (CommandSpec(...), ...)`
  module-level tuple literal in `game/`.
- `docs/systems/strategy_layer.md` — Phase 3: new "Adding a new command"
  authoring-rule section. Update `> **Last verified:**` blockquote.
- `docs/02_PATTERNS.md` — Phase 3: extend the existing "Pattern N: Spec-driven
  registry" section (or add a new one) cross-referencing PROJ-273, PROJ-278,
  PROJ-371.

**Out:**

- Command semantics (DTO field shapes, handler logic) — none change.
- `OrderProcessor` itself (910-LOC monolith) — that's PROJ-368.
- Persistence of commands — commands are NOT persisted (verified). Only
  `Order` objects are persisted.
- New mod-loading machinery — mods register via Python import, same as today.
  No entry-points / dynamic plugin loader.
- `OrderType` enum changes — out of scope; pinned via existing contract tests.
- The data-layer frozensets at `data/order_types.py:58-86` — they stay as
  module-level constants for import-graph reasons (`data/order_types.py` is a
  leaf and cannot import the registry without a cycle). Pinned by the
  Phase 2-updated contract test.

## Key Files

| Component | File Path |
|-----------|-----------|
| New registry module | `game/strategy/engine/commands/registry.py` |
| Existing tuple (deleted Phase 2) | `game/strategy/engine/commands/specs.py` |
| DTO module (untouched) | `game/strategy/engine/commands/__init__.py` |
| Domain handler modules (decorated Phase 1) | `game/strategy/engine/handlers/{build,construction_queue,movement,order_queue,transfer}.py` |
| Planet handler module (decorated Phase 1) | `game/strategy/engine/planet_command_handlers.py` |
| Superweapon handler module (decorated Phase 1) | `game/strategy/engine/superweapon_command_handlers.py` |
| Registry-factory consumer | `game/strategy/engine/handlers/registry_factory.py` |
| Action-time-resolver consumer | `game/strategy/services/action_time_resolver.py` |
| Command-dispatch-slice consumer | `game/strategy/facade/slices/command_dispatch_slice.py` |
| Facade forwarders (collapsed Phase 2) | `game/strategy/facade/strategy_session_facade.py` |
| Order-types frozensets (pinned, untouched) | `game/strategy/data/order_types.py` |
| PROJ-364 cross-link test | `tests/unit/strategy/services/test_superweapon_registry_contract.py` |
| Spec-table contract test | `tests/unit/strategy/engine/test_command_specs_contract.py` |
| Registry contract test (existing) | `tests/unit/strategy/engine/test_command_registry_contract.py` |
| Slice-resolver contract test | `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` |
| Bit-identity contract (new Phase 1) | `tests/unit/strategy/engine/test_command_registry_seeding.py` |
| Third-party smoke (new Phase 3) | `tests/unit/strategy/engine/test_command_registry_thirdparty.py` |
| AST regression (new Phase 3) | `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` |

## Related Documents

- [design.md](design.md) — diagnosis, current vs. target registration, alternatives, risks
- [decisions.md](decisions.md) — design choices and rejected alternatives
- [manifest.md](manifest.md) — file inventory
- [findings/initial_review.md](findings/initial_review.md) — 35-spec inventory + corrected "8 edits" mapping
- Strategy-layer review: `AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md`
- Pattern source 1: `Projects/deep_archive/PROJ-251-300/PROJ-273/` (Ability-Stat Registry)
- Pattern source 2: `Projects/deep_archive/PROJ-251-300/PROJ-278/` (Role Registry)
- Predecessor: `Projects/active_projects/PROJ-363/` (CommandSpec spec table)
- Sibling: `Projects/active_projects/PROJ-368/` (OrderProcessor decomposition — different layer, no file conflicts)
- Sibling: `Projects/active_projects/PROJ-364/` (Superweapon spec table — cross-linked test)

## Today's vs target registration (one-line diff)

**Today** (`game/strategy/engine/commands/specs.py:219-537`):

```python
COMMAND_SPECS: tuple[CommandSpec, ...] = (
    CommandSpec(command_class=IssueMoveCommand, handler_class=MoveCommandHandler, ...),
    CommandSpec(command_class=IssueColonizeCommand, handler_class=ColonizeCommandHandler, ...),
    # ... 33 more rows in a literal tuple ...
)
```

**Target** (after Phase 2):

```python
# game/strategy/engine/handlers/movement.py
@command_spec(command_class=IssueMoveCommand, order_type=OrderType.MOVE,
              category='movement', execution_model='action',
              facade_helper_name='dispatch_issue_move', serializer_codec='hex_coord')
class MoveCommandHandler(BaseCommandHandler):
    def execute(self, session, command): ...
```

The decorator is the registration. `specs.py` no longer exists; `registry.py`
exposes `command_registry` and the decorator.

## Phases

### Phase 1: Introduce `CommandRegistry` alongside existing tuple [Medium]

**Objective:** New `registry.py` module exists with `CommandRegistry` class,
global `command_registry` instance, and `@command_spec(...)` decorator. All 35
handler classes carry the decorator. The literal tuple in `specs.py` is
**kept** unchanged. A new contract test asserts bit-identity between
`COMMAND_SPECS` (tuple) and `command_registry.all()` (registry). Zero consumer
migration; zero behaviour change.

**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Migrate consumers; delete tuple; collapse facade forwarders [Medium]

**Objective:** `registry_factory.py`, `action_time_resolver.py`, and
`command_dispatch_slice.py` read from `command_registry`. The PROJ-364
cross-link test reads `command_registry.all()`. `strategy_session_facade.py`'s
31 hand-written `dispatch_*` forwarders collapse into `__getattr__` proxying
to `self._command_slice.dispatch_*`. `specs.py` is **deleted**. The redundant
`MOVEMENT_ORDER_TYPES` local frozenset at `action_time_resolver.py:48` is
deleted. Three contract tests update imports. Sharded suite green.

**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Authoring rule + AST regression + third-party smoke [Small]

**Objective:** New AST regression test forbids any `COMMAND_SPECS =
(CommandSpec(...), ...)` module-level tuple literal in `game/`. New end-to-end
smoke test registers a `FakeModCommand` + `FakeModCommandHandler` at test
setup, dispatches via the facade, asserts the handler executed, and
unregisters cleanly via a test fixture. `docs/systems/strategy_layer.md` gains
an "Adding a new command" section with the canonical decorator pattern.
`docs/02_PATTERNS.md` cross-references PROJ-273, PROJ-278, PROJ-371 in the
spec-driven registry pattern.

**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)

- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Read `docs/systems/strategy_layer.md`
- [ ] Read PROJ-273 design + plan (pattern source 1)
- [ ] Read PROJ-278 design + plan (pattern source 2)
- [ ] Read PROJ-363 design + plan + Phase 4 checklist (immediate predecessor)
- [ ] Read PROJ-368 plan (sibling project — confirm no file overlap)
- [ ] Read findings/initial_review.md (the 35-spec inventory + line-by-line "8 edits" mapping)
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### After Each Phase

- [ ] Run `pytest tests/unit/strategy/engine/ -v` — engine + registry tests pass
- [ ] Run `pytest tests/unit/strategy/facade/ -v` — facade dispatch tests pass
- [ ] Run `pytest tests/unit/strategy/services/ -v` — services tests (PROJ-364 cross-link) pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Update `Current State` in this plan with handoff context for the next agent

### Final Verification

- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] `game/strategy/engine/commands/specs.py` is deleted (`git ls-files | grep specs.py` returns nothing for that path)
- [ ] `command_registry` is the single source of truth for `CommandSpec` rows
- [ ] All 35 handler classes carry an `@command_spec(...)` decorator
- [ ] `strategy_session_facade.py:186-300` (31 forwarders) is gone — replaced by `__getattr__`
- [ ] Local `MOVEMENT_ORDER_TYPES` at `action_time_resolver.py:48` is gone
- [ ] AST regression test passes — no new `COMMAND_SPECS = (...)` literal can land
- [ ] Third-party smoke test passes — a `FakeModCommand` registers, dispatches, unregisters cleanly
- [ ] `docs/systems/strategy_layer.md` "Adding a new command" section reflects the new pattern
- [ ] `docs/02_PATTERNS.md` cross-references PROJ-273, PROJ-278, PROJ-371

## Audit Log

| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist

- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Audit passed (no significant issues)
- [ ] User verified
