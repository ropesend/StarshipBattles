# Agent 3 Report: Task 3.34 Deferral Audit

## 1. Fleet-Not-Found Pattern Analysis

### Handler-by-Handler Comparison

| # | Handler Class (Test Class) | mock_cmd kwargs | Line | Test body differences | Identical to others? |
|---|---|---|---|---|---|
| 1 | ColonizeCommandHandler | `fleet_id=999, planet_id=1` | 93-104 | None | YES (to pattern B) |
| 2 | MoveCommandHandler | `fleet_id=999, target_hex=(0, 0)` | 142-153 | None | YES (to pattern B) |
| 3 | InterceptCommandHandler | `fleet_id=999, target_fleet_id=2` | 209-220 | None | YES (to pattern B) |
| 4 | ColonizeMissionCommandHandler | `fleet_id=999, planet_id=None, target_hex=(0, 0)` | 380-391 | None | YES (to pattern C) |
| 5 | ClearOrdersCommandHandler | `fleet_id=999` | 422-433 | None | YES (to pattern A) |
| 6 | TransferCommandHandler | `fleet_id=999` | 460-471 | None | YES (to pattern A) |
| 7 | SplitFleetCommandHandler | `fleet_id=999, ship_instance_ids=['ship-1']` | 762-773 | None | YES (to pattern B) |
| 8 | DeleteOrderCommandHandler | `fleet_id=999, order_index=0` | 927-938 | None | YES (to pattern B) |
| 9 | ReorderOrderCommandHandler | `fleet_id=999, order_index=0, direction=1` | 1032-1043 | None | YES (to pattern C) |
| 10 | AddToConstructionQueueCommandHandler | `entity_id=999, entity_type="fleet", design_id="scout", category="ship", index=None, target_planet_id=None, queue_id=None` | 1274-1293 | **Different attribute name:** `entity_id` vs `fleet_id` | NO (separate interface) |
| 11 | RemoveFromConstructionQueueCommandHandler | `entity_id=999, entity_type="fleet", item_index=0, queue_id=None` | 1557-1568 | **Different attribute name:** `entity_id` vs `fleet_id` | NO (separate interface) |

### Categorization Summary

All 11 methods share exact same core logic:

```python
handler = <HandlerClass>()
mock_session = Mock()
mock_session.active_empire = Mock(id=0)
mock_session._get_fleet_by_id.return_value = None
mock_cmd = Mock(<handler_specific_kwargs>)
result = handler.execute(mock_session, mock_cmd)
assert not result.is_valid
assert "Fleet not found" in result.message
```

**Pattern A** (minimal, 2 handlers): ClearOrders, Transfer — `Mock(fleet_id=999)`

**Pattern B** (fleet_id + 1 extra, 4 handlers): Colonize, Move, Intercept, SplitFleet — `Mock(fleet_id=999, <extra>)`

**Pattern C** (fleet_id + 2 extra, 2 handlers): ColonizeMission, ReorderOrder — `Mock(fleet_id=999, <extra1>, <extra2>)`

**Pattern D** (construction-queue interface, 2 handlers): AddTo, RemoveFrom — `Mock(entity_id=999, entity_type="fleet", ...)`

**Key observation:** The extra mock_cmd kwargs are functionally dead in the fleet-not-found test context. The handler's `execute()` method calls `_resolve_player_fleet()` or `_get_fleet_by_id()` before reading any command attributes, so the mock_cmd kwargs are only present to prevent `AttributeError` when Mock auto-creates attributes. This means ALL 11 test bodies are **semantically identical** — they differ only in the object shape of the mock command, not in tested behavior.

However, patterns A-D reflect **real interface differences** between the production handlers: standard fleet-command handlers use `cmd.fleet_id`, while construction-queue handlers use `cmd.entity_id` + `cmd.entity_type`. A parametrized test would need to distinguish these two interfaces.

---

## 2. Production Structure Alignment

### How production organizes these handlers

Production handlers were decomposed in PROJ-309 sub-phase 3.5 from a single 1076-line file into the package `game/strategy/engine/handlers/`:

| Production Module | Handlers Owned | Fleet-not-found test count |
|---|---|---|
| `handlers/movement.py` (214 LOC) | Colonize, Move, Intercept, Join | 3 |
| `handlers/order_queue.py` | ColonizeMission, ClearOrders, SplitFleet, DeleteOrder, ReorderOrder | 5 |
| `handlers/transfer.py` | Transfer | 1 |
| `handlers/construction_queue.py` (265 LOC) | AddTo, RemoveFrom, Reorder construction queue | 2 |
| `handlers/build.py` | BuildOrder, RemoveBuildOrder | 0 |
| `handlers/base.py` | BaseCommandHandler | 0 (tested in separate class) |

### How tests mirror this structure

The test file `tests/unit/strategy/test_command_handlers.py` (1899 lines) is a **single monolithic file** containing all 17 test classes in one module. It does NOT mirror the production sub-module structure at all:

- All handler test classes are in one file, regardless of which production sub-module contains the handler
- Test classes are ordered roughly chronologically (original handlers first, then PROJ-208 additions)
- No test-per-module or test-per-functional-domain organization exists

### Would parametrization destroy useful alignment?

**NO.** The "per-class structure" argument is hollow because:

1. The test file already does NOT mirror the production module structure. Production has 5 functional-domain modules; tests have 1 monolithic file.
2. The per-class test organization is an artifact of the original monolithic production file, not a deliberate design choice mirroring the current decomposed structure.
3. If the tests truly mirrored production, each production module would have its own test file (e.g., `test_handlers_movement.py`, `test_handlers_construction_queue.py`), and the fleet-not-found tests would be naturally scattered across those files by domain — making parametrization across domains impossible anyway.
4. Since the tests are already in one file, a parametrized test (or two: one for fleet-command handlers, one for construction-queue handlers) would NOT reduce organizational clarity — it would actually make the shared pattern MORE visible.

---

## 3. Comparison with Successful Parametrization

### Task 3.2 (test_superweapon_handler_validation.py)

**What was done:** 10 near-identical handler tests (5 direct handlers + 5 mission handlers) were collapsed into 3 parametrized tests:
- `test_direct_handler_passes_component_registry` — 5 parametrized cases
- `test_mission_handler_passes_component_registry` — 5 parametrized cases
- `test_mission_handler_rejects_fleet_without_ability` — 5 parametrized cases

**Why it worked:**
- All superweapon handlers live in a single production file (`superweapon_command_handlers.py`)
- The parametrized tests are in a dedicated file (`test_superweapon_handler_validation.py`) focused on ONE validation concern
- Case factory functions (`_direct_handler_cases()`, `_mission_handler_cases()`) return tuples of `(handler_cls, cmd_instance, validator_attr, [ability_name])`
- Parametrize IDs use handler class names via `id=case[0].__name__` for readable test output
- Each of the 3 tests asserts a DIFFERENT thing, so separate test functions are justified
- Estimated savings: ~180 LOC (10 per-handler methods ~15 lines each → 3 parametrized tests + case factories ~50 lines)

### How this case differs

| Aspect | Task 3.2 (Superweapon) | Task 3.34 (Command Handlers fleet-not-found) |
|---|---|---|
| Production handler organization | Single file | 5 sub-module files |
| Test file organization | Dedicated validation test file | Monolithic file (1899 lines) |
| Test behavior diversity | 3 distinct behaviors across 10 handlers | **1 identical behavior across 11 handlers** |
| Handler interface uniformity | All use `fleet_id` + component_registry | 9 use `fleet_id`, 2 use `entity_id`+`entity_type` |
| Number of tests to condense | 10 → 3 parametrized tests | 11 → 1 or 2 parametrized tests |
| Assertion complexity | Different assertions per test (component_registry pass, ability rejection) | All assert identical conditions (`not is_valid`, `"Fleet not found" in message`) |

### Applicable lessons

1. **Parametrization works best when a single concern is tested across handlers.** Task 3.2 proved this with 3 test functions each testing a distinct concern. The fleet-not-found case is an even STRONGER candidate because it's ONE concern, not three.

2. **Case factory functions with `id=handler_cls.__name__` preserve debuggability.** pytest output shows each handler class name in test results, so parametrization doesn't hide which handler failed.

3. **Using real command objects (not raw Mocks) in parametrize cases improves clarity.** Task 3.2 uses actual command class instances (`IssueImplodePlanetCommand(fleet_id=1, planet_id=100)`). This pattern could be applied here.

4. **Separate parametrize groups by interface when handlers differ.** The construction-queue handlers' `entity_id` interface is a natural split point — exactly as Task 3.2 splits direct vs. mission handlers.

---

## 4. Recommendation

### Deferral rationale validity

**PARTIALLY-JUSTIFIED.**

The deferral rationale of "per-class structure aligns with production" is misleading:
- The production structure IS per-module (functional domain), NOT per-class
- The test file does NOT mirror this production structure
- The per-class organization in the test file is an artifact of the old monolithic production design, not a deliberate alignment choice

However, the deferral has one legitimate concern not stated in the rationale: the construction-queue handlers (2 of 11) use a different command interface (`entity_id` + `entity_type` vs `fleet_id`), which means a single parametrized test across all 11 handlers would require conditional mock_cmd construction logic — reducing the elegance of the consolidation.

### If parametrized, estimated LOC savings

| Approach | Current LOC | New LOC | Savings |
|---|---|---|---|
| One parametrized test (all 11) | ~130 | ~45 | **~85 LOC** |
| Two parametrized tests (9 fleet-cmd + 2 construction-queue) | ~130 | ~55 | **~75 LOC** |
| Two parametrized tests as above, but with real command objects | ~130 | ~60 | **~70 LOC** |

The current 11 methods total ~130 lines (including whitespace/docstrings). A two-part parametrization (preferred for interface cleanliness) would be ~55 lines including case factories.

### If left as-is, downside

1. **Duplication burden:** If the fleet-not-found assertion pattern ever changes (e.g., message format changes, ValidationResult API changes, error code added), 11 methods must be updated — a DRY violation.
2. **Noise in monolithic file:** The 1899-line test file has 130 lines of copy-paste that obscure the genuinely unique tests.
3. **Missed pattern visibility:** The uniformity of fleet-not-found handling across handlers is an architectural property worth surfacing, not burying in 11 identical methods.
4. **Inconsistency with Task 3.2 precedent:** The project has already accepted class-level parametrization for handler validation concerns. Keeping this pattern un-parametrized creates an inconsistent standard.

### Recommendation

**PARAMETRIZE-NOW**

The case is straightforward enough to handle in the current project rather than deferring:

1. Split into **two** `@pytest.mark.parametrize` test functions (one for fleet-command handlers, one for construction-queue handlers) to respect the genuine interface difference between `fleet_id` and `entity_id`.

2. Use the Task 3.2 pattern: a case factory function per group, real command object instances (or lightweight dataclass/Mock kwargs dicts) in the parametrize tuples, and `id=handler_cls.__name__` for readable output.

3. This delivers ~75 LOC savings with minimal risk (the assertions are identical, only setup varies).

4. The monolithic test file already doesn't match production structure, so parametrization doesn't degrade organizational clarity — it improves it by grouping the shared concern.

---

## 5. Findings Summary

| ID | Severity | Description |
|---|---|---|
| FND-P3-001 | LOW | 11 `test_fleet_not_found` methods share identical assertion logic; only mock_cmd kwargs differ |
| FND-P3-002 | INFO | All 11 test bodies are semantically identical — handler short-circuits on fleet-not-found before reading command attributes, making extra mock_cmd kwargs dead data |
| FND-P3-003 | LOW | Production handlers are split across 5 sub-module files (`movement.py`, `order_queue.py`, `transfer.py`, `construction_queue.py`, `build.py`), but the test file (`test_command_handlers.py`, 1899 lines) is monolithic — the "per-class structure mirrors production" deferral rationale is factually incorrect |
| FND-P3-004 | INFO | Construction-queue handlers (2 of 11) use `entity_id`+`entity_type` instead of `fleet_id`, representing a genuine interface boundary that warrants a separate parametrize group |
| FND-P3-005 | LOW | Task 3.2 already established the class-level parametrize pattern in the same project phase; keeping fleet-not-found un-parametrized creates inconsistency |
| FND-P3-006 | INFO | Estimated LOC savings: 70-85 lines (from ~130 to 45-55). The existing duplication is a DRY maintenance risk for future ValidationResult API changes |
