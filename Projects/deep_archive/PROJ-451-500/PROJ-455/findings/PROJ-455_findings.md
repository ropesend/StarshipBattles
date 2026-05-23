# PROJ-455 Findings (consolidated)

Source: `AgentCoordination/discovered_issues/log.jsonl` (DI-2026-05-18-001 — ActionExecutionEngine half; verbatim below).

File:line references **re-verified against current code on 2026-05-19** before this file was written. The current `_process_planet_action_tick` method spans lines 245-297 of `game/strategy/engine/action_execution_engine.py` (the DI entry was logged when the method was at line 245 — line range unchanged since logging).

The DI log contains **two entries with the same `"id": "DI-2026-05-18-001"`** (the log uses `id` for the original-discovery anchor, not for uniqueness). The first entry (line 1 of `log.jsonl`) is the ActionExecutionEngine half — the one this project closes. The second entry (line 3) is the transfer half — already `"status": "resolved"` per archived PROJ-445 Phase 2. PROJ-455 touches only line 1.

---

## DI-2026-05-18-001 (ActionExecutionEngine half) — Behavioural E2E coverage gap for planet-FMS through `ActionExecutionEngine._process_planet_action_tick`

- **Severity**: medium
- **Category**: test-gap
- **File**: `game/strategy/engine/action_execution_engine.py:245-297` (the `_process_planet_action_tick` method body)
- **Symbol**: `ActionExecutionEngine._process_planet_action_tick`
- **Source task**: PROJ-438 end-of-project Codex consult triage
- **Discovery date**: 2026-05-18T16:55:32Z
- **Description (verbatim from log.jsonl)**: "The engine-mediated dispatch path that runs planet FMS recovery/launch orders through OrderProcessor.get_handler -> handler.execute_for_issuer is currently protected by structural / inspect-based tests (tests/unit/strategy/engine/test_issuer_execution_contract.py) plus unit-level handler tests (tests/integration/test_fms_planet_recovery.py:90), but no behavioral test drives the full engine tick path. Found by PROJ-438 end-of-project Codex consult 2026-05-18 (Finding 6c + Risk 3, response.md at AgentCoordination/Scratchpad/Consult/20260518T153829Z_proj-438-end-of-project/). PROJ-438 ships strict-green at 23,272 passed; this is a coverage hole that was intentionally deferred so PROJ-438 could close. Plausibly 100-200 LOC of integration fixture scaffold."
- **Suggested action (verbatim from log.jsonl)**: "Fixture needs: 1 empire, 1 owned planet with operational facility carrying fighter/satellite bay, queued RECOVER_FIGHTERS or RECOVER_SATELLITES order via typed command path, deployed groups present. Drive one tick of _process_planet_action_tick. Assert order queue advanced, handler invoked with all 5 kwargs of unified execute_for_issuer, deployed group transitioned correctly, no exception propagation."
- **Status as of 2026-05-19**: still open. Archived PROJ-445 Phase 1 closed the **adjacent** half (added `tests/integration/test_fms_planet_lay_mines.py` parametrised across 5 order types, but that test calls `_execute_planet_action` **directly**, bypassing the `_process_planet_action_tick` entry point). The DI log entry's "drive one tick of _process_planet_action_tick" requirement remains unsatisfied.

---

## Context: what archived PROJ-445 Phase 1 closed (and what it did NOT close)

PROJ-445 Phase 1 (2026-05-18 close) added `tests/integration/test_fms_planet_lay_mines.py` — a parametrised test across all 5 planet-FMS order types that:

- Constructs a `_StubPlanet` and `SimpleNamespace` empire.
- For each order type, runs the appropriate scenario builder (`_build_lay_mines_scenario`, `_build_launch_fighters_scenario`, `_build_launch_satellites_scenario`, `_build_recover_fighters_scenario`, `_build_recover_satellites_scenario`).
- Calls `engine._execute_planet_action(planet, empire, component_registry=None)` **directly**.
- Asserts no exception escapes and the order queue is advanced.

**What this test covers:** the `_execute_planet_action` → `_order_processor.get_handler` → `PlanetStagingYardIssuerAdapter` → `handler.execute_for_issuer(..., registries=...)` chain. Specifically catches the F-B-001 drift (any handler with a wrong kwarg signature raises `TypeError` here).

**What this test does NOT cover:**

- `process_action_ticks` outer loop over `empire.colonies` (the loop body at action_execution_engine.py:124-130).
- `_process_planet_action_tick`'s `order_metadata.planet_fms_action_order_types` membership check (line 264).
- `order.execution_progress += 1` increment (line 267).
- `ActionTimeResolver.resolve_action_time(planet, order, component_registry)` resolution (lines 269-276) — neither the injected-resolver branch nor the static-resolver branch.
- The `if order.execution_progress >= action_time:` completion gate (line 278) — both the completion path (calls `_execute_planet_action`) AND the in-progress path (returns an `ActionTickResult` with `action_completed=False`).
- The `ActionTickResult` return-value shape (lines 282-289 for completion; 290-297 for in-progress).

PROJ-455 covers all of the above by parametrising across the same 5 order types but driving through `process_action_ticks` instead of `_execute_planet_action`.

---

## Out-of-scope clarifications (not closed by this project)

- **DI-2026-05-18-001 transfer half** — closed by archived PROJ-445 Phase 2 (recorded as `resolved` in line 3 of log.jsonl).
- **DI-2026-05-18-002 (CommandRegistry.serializer_codec_for)** — closed by archived PROJ-445 Phase 2.
- **DI-2026-05-18-003 / -004 / -005** — owned by PROJ-452.
- **DI-2026-05-18-006 / -007 (production engine semantics)** — partial-resolved by PROJ-444/445; UX gap deferred to a future engine project.
- **F-B-022** (LAY_MINES planet-dispatch test) — closed by PROJ-445 Phase 1 (handler-direct path). PROJ-455 escalates to the engine-mediated path.
- **The fleet branch of `process_action_ticks`** — has separate coverage in `tests/unit/strategy/engine/` (per the inline comment at action_execution_engine.py:106-108 about the "any action order anywhere precheck" that was tried and dropped). Not a PROJ-455 target.

---

## Fixture sizing — what the test needs (canonical reference)

This section captures the fixture spec for Phase 1 in one place so the agent picking up implementation has everything in one read.

### Minimum `_StubPlanet` shape (extend the precedent from `test_fms_planet_lay_mines.py:41-83`)

```python
class _StubPlanet:
    def __init__(self, *, planet_id: int, owner_id: int, location: HexCoord, name: str = "P1") -> None:
        self.id = planet_id
        self.owner_id = owner_id
        self.location = location
        self.global_hex = location
        self.name = name
        self.staging_yard: list = []
        self.max_staging_mass: float = 0.0
        self.orders: list = []
    def get_current_order(self):
        return self.orders[0] if self.orders else None
    def pop_order(self):
        if self.orders:
            return self.orders.pop(0)
        return None
    def add_order(self, order) -> None:
        self.orders.append(order)
    def add_to_staging_yard(self, item) -> bool:
        # ... mass-check as in precedent file lines 74-83
        ...
```

The existing precedent stub is sufficient for direct `_execute_planet_action` calls. End-to-end tests need it unchanged.

### Minimum empire shape

```python
empire = SimpleNamespace(
    id=7,
    name="E",
    fleets=[],                          # process_action_ticks loops over .fleets
    colonies=[planet],                  # process_action_ticks loops over .colonies
    deployed_groups=[],                 # populated for recovery scenarios
)
empire.deployed_groups_of = lambda cls, _e=empire: [
    g for g in _e.deployed_groups if isinstance(g, cls)
]
```

### `ActionTimeResolver` choice

Two options:

1. **Inject a mock resolver** via `ActionExecutionEngine(order_processor=..., action_time_resolver=mock_resolver)`. The mock returns `1` so the test ticks complete the action on the first tick. Preferred — deterministic, no production-code dependency on the planet's component layout.
2. Use the static fallback `ActionTimeResolver.resolve_action_time(planet, order, component_registry=None)`. Currently returns a default constant when no component registry is supplied. Verify the constant is `1` or otherwise low enough that the test reliably completes within one tick.

The recommended path is option 1 for the parametrised test (assert the action completes); option 2 may be useful for a separate "in-progress" test that asserts `execution_progress == 1` and the order is NOT popped.

### Scenario builders (reusable from precedent)

All 5 builders already exist verbatim in `tests/integration/test_fms_planet_lay_mines.py:138-220`. Phase 1 may either:

- Copy them into the new test file (simplest), or
- Extract them into a shared `tests/integration/_planet_fms_fixtures.py` module and import from both the precedent file and the new file (recommended if the implementation discovers >1 shared helper).

### Engine + processor fixture

```python
@pytest.fixture
def engine_and_processor() -> tuple[ActionExecutionEngine, OrderProcessor]:
    processor = OrderProcessor()
    engine = ActionExecutionEngine(order_processor=processor)
    return engine, processor
```

Identical to the precedent at `test_fms_planet_lay_mines.py:223-227`.
