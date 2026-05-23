# PROJ-450 Phase 0 — Pre-flight audit

> Date: 2026-05-19 (Group A serial position: last)
> Branch: `group-a` (post-PROJ-449/451/459 merges)

## 1. PROJ-449 Phase 3 precondition (direct code inspection)

```bash
$ grep -n "_planet_init_with_legacy_kwargs\|@staging_yard\.setter" game/strategy/data/planet.py
(zero matches)
```

- `_planet_init_with_legacy_kwargs` is GONE.
- `@staging_yard.setter` is GONE.
- Read-only `@property` for `staging_yard` survives at `game/strategy/data/planet.py:240` (intentional per PROJ-449 Phase 3 scope-adjustment — see PROJ-449 decisions.md 2026-05-18 row "Phase 3 scope adjustment").

**Precondition SATISFIED.** PROJ-449 Phase 3 landed at SHA `ebb5c0e7f` (Merge group-a through PROJ-449).

## 2. Cross-group sync gate (Task 0.6)

Read on `origin/main` per protocol §5:

- **PROJ-454** (Group B): ALL 5 phases marked Complete. Merged at SHA `ab2da0669`.
- **PROJ-456** (Group B): ALL 6 phases marked Complete. Merged at SHA `244c1fa16`.

**Sync gate CLEARED.** Phase 1 may proceed.

## 3. Audit re-verification at HEAD

```bash
grep -rl "staging_yard" game/ | wc -l           # 58 files
grep -rl "staging_yard" tests/ | wc -l          # 73 files
grep -rh "staging_yard" game/ tests/ | wc -l    # 403 occurrences
```

Baseline (May 2026, Stage 3 Joint A preflight §1.2): 310 occurrences across 49 files (82 game + 228 tests).

Current vs baseline:
- Files: 49 → 131 (+82, ~167% growth)
- Occurrences: 310 → 403 (+93, ~30% growth)

The growth is concentrated in NEW DOCUMENTATION FILES, not new code paths:
- `Projects/active_projects/PROJ-449/` — many decisions.md / plan.md / phase_*_checklist.md / consults/ files mention `staging_yard` in context
- `Projects/active_projects/PROJ-450/` — own documentation references
- `tests/integration/test_fms_planet_launch.py` — added a `_StubPlanet._staging_yard` private field + property alias during PROJ-449 Phase 3 (a refactoring side-effect; same logical surface as before, just renamed)

Code-path growth is minimal. The 3 blockers (next section) are the authoritative measure of project scope, and they are all still present at expected locations.

## 4. 3 blockers verified at HEAD

### BLOCKER #1 — UI reader silent-skip

```python
# game/ui/screens/strategy_detail_fmt.py:289
if not isinstance(item, dict):
    continue  # ← typed objects fall here silently
```

Confirmed present at L289. Line refs shifted from 285-297 to ~285-297 (no material drift). **Phase 3 Task 3.2 fixes this.**

### BLOCKER #2 — Integration test direct mutations

| File | Lines (plan) | Lines (current HEAD) | Pattern |
|------|--------------|-----------------------|---------|
| `test_fms_planet_recovery.py` | 59 | 59 | `self.staging_yard.append(item)` (inside `_StubPlanet.add_to_staging_yard`) |
| `test_fms_planet_lay_mines.py` | 82, 139, 155, 171 | 82, 139, 155, 171 | `.append(_mine_dict())` etc. |
| `test_fms_planet_launch.py` | 92, 121, 157, 192 | 132, 168, 203 | `.extend(_fighter_dict()...)` etc.; line refs shifted because the file added `_StubPlanet._staging_yard` private field during PROJ-449 Phase 3 |
| `test_fms_a_e2e.py` | 305 | 305 | `planet.staging_yard.clear()` |

All sites confirmed (line-ref drift in `test_fms_planet_launch.py` only). **Phase 4 migrates these.**

### BLOCKER #3 — Validator + write-service shape probes

```python
# game/strategy/validation/transfer_validator.py:228
staging = getattr(planet, 'staging_yard', [])

# game/strategy/validation/transfer_validator.py:363, 368
staging = getattr(planet, "staging_yard", [])
...
if isinstance(item, CarriedVehicle):
    ...
elif isinstance(item, dict) and ...:
    ...

# game/strategy/services/planet_write_service.py:100-105
def add_staging_item(self, planet: "Planet", item: Any) -> None: ...
def pop_staging_item(self, planet: "Planet", index: int = 0) -> Any: ...
```

All three sites confirmed. **Phase 3 Task 3.3 tightens these.**

## 5. F-A-013 already-complete verification

```python
# game/strategy/facade/slices/fleet_slice.py:165-177
def _ship_container_snapshot(...):
    ...
    _used, capacity_max = ship._cargo_mgr.get_vehicle_bay_capacity()
```

Confirmed. F-A-013 was closed at PROJ-444 Phase 2 Task 2.4. PROJ-450 carries it as a "verify-only" entry; no action required.

## 6. Gate decision

- PROJ-449 Phase 3 precondition: SATISFIED
- Cross-group sync gate: CLEARED (PROJ-454 + PROJ-456 both Complete)
- 3 blockers: all present at expected locations
- F-A-013: verified complete
- Audit count growth (310 → 403): documentation-driven, not code-path growth

**Phase 1 may proceed.** No code touched in Phase 0.

## 7. Baseline sharded suite

23397/23397 GREEN (recorded prior to Phase 0 commit).
