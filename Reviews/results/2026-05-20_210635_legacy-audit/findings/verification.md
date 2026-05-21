# Verification Report
**Audit:** 2026-05-20 Legacy Audit
**Verification performed:** 2026-05-20

## Methodology
For each CRITICAL finding across all 4 shard reports + cross-system duplicate report:
1. Read the cited source file at the indicated line/range
2. Verified code matches description
3. Confirmed genuinely legacy (not forward-compat extension point or documented public API)
4. Re-ran call-site counts via Grep across `game/` and `tests/`
5. Rated as CONFIRMED, DISPUTED, or INCONCLUSIVE

---

## Critical Finding Verification

| Finding ID | Symbol/File | Verdict | Reason |
|------------|-------------|---------|--------|
| LEG-01-008 | `DamageContext` re-export at `game/simulation/combat/combat_events.py:62` | **CONFIRMED** | Zero production call sites (grep-verified across `game/`). Code at line 62 matches description: `from game.core.combat_types import DamageContext  # noqa: F401` with explicit backward-compat comment. All production consumers (`collision.py:53`, `damage_calculator.py:28`, `projectile_manager.py:148`) import directly from `game.core.combat_types`. One test caller exists (`tests/unit/simulation/combat/test_combat_events.py:14` imports via the legacy path) — test must be updated before deletion. |
| A-01 (Shard 03) | `CombatConstants` re-export at `game/simulation/entities/ship.py:23` | **CONFIRMED** | Zero call sites total (production + test) verified by Grep across entire repo. Code at line 23 matches description: `from game.core.constants import CombatConstants` in a re-export block (lines 21-23) with comment "Re-export for backward compatibility and convenient access." All 12 consumers (`game/ai/interfaces/controllable.py:16`, `game/simulation/entities/ship_combat_engine.py:21`, `game/simulation/entities/stat_contributors/command.py:28`, `game/simulation/components/component.py:64`, `game/ui/panels/ship_detail_panel.py:29`, `game/ui/panels/ship_stats_renderer.py:28`, and all test files) import directly from `game.core.constants`. No file imports `CombatConstants` through the `ship.py` re-export path. This is a clean dead-code delete with zero churn. |

---

## Downgraded Findings

**None.** Both CRITICAL findings are accurately rated. No CRITICAL findings warrant downgrade to MAJOR or MINOR.

---

## Confirmed Critical

These are safe-to-act-on legacy removals:

### CRIT-1: DamageContext re-export (`combat_events.py:62`)
- **File:** `game/simulation/combat/combat_events.py`, line 62
- **Code to remove:** `from game.core.combat_types import DamageContext  # noqa: F401`
- **Pre-cleanup required:** Update `tests/unit/simulation/combat/test_combat_events.py:14` to import `DamageContext` from `game.core.combat_types` instead of `game.simulation.combat.combat_events`
- **Risk:** None. Zero production churn. 1 test file updated.
- **LOC saved:** 1

### CRIT-2: CombatConstants re-export (`ship.py:23`)
- **File:** `game/simulation/entities/ship.py`, line 23
- **Code to remove:** `from game.core.constants import CombatConstants` (line 23 only; line 22 `DEFAULT_MAX_MASS` is a separate MAJOR finding A-02)
- **Pre-cleanup required:** None. Zero total callers (production + test).
- **Risk:** None. Zero churn anywhere.
- **LOC saved:** 1

Note: The adjacent `DEFAULT_MAX_MASS` re-export at `ship.py:22` is a separate MAJOR finding (A-02) with 1 test caller (`tests/unit/entities/test_ship.py:472`). It can be removed in the same PR after that test is updated.

---

## Inconclusive Findings

**None.** Both CRITICAL findings were resolved decisively by direct source verification and exhaustive cross-repo grep.

---

## Notes on Other Findings Reviewed

While verifying CRITICAL findings, the following adjacent observations were made:

- **LEG-01-008 / test_combat_events.py:** The only surviving caller of the `DamageContext` re-export path is the test file that tests `combat_events.py` itself. This is the "dogfooding its own re-export" pattern — the test imports from the module it tests, which happens to re-export the symbol. The fix is trivial: change the test import to the canonical `game.core.combat_types` path and keep importing other symbols from `combat_events`.

- **A-01 / ship.py:21-23:** The re-export block comment "Re-export for backward compatibility and convenient access" applies to both `DEFAULT_MAX_MASS` (line 22, MAJOR finding A-02) and `CombatConstants` (line 23, CRITICAL finding A-01). `DEFAULT_MAX_MASS` has 1 test caller; `CombatConstants` has zero. If both are removed together, line 21's comment should be removed as well.

- **Review 04 MAJOR finding (planetary_facility.py deprecated fuel wrappers):** Verified as actively used in production (`resupply_engine.py:135,208,293`) — this is correctly rated MAJOR (deprecated but can't be removed until consumers migrate to the generic consumable API). The deprecation marker should either be backed by a PROJ ticket with a removal timeline, or the marker should be removed as misleading.
