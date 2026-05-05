# Decomposition Design: core/protocols.py

**Current size:** 1087 lines
**Target post-split:** every resulting sub-module <500 lines

> **Authored:** 2026-04-27 (PROJ-309 Phase 1 design wave)
> **Status:** Design only — no code changes proposed in this document.

---

## Current responsibilities

`game/core/protocols.py` is a single monolithic module that owns **every** cross-layer Protocol class plus its paired TypeGuard helper. It is the structural-typing seam for the whole codebase — Strategy, Simulation, UI, AI, and persistence all import from it.

Concretely, the file contains:

| # | Symbol | Lines | Domain | Notes |
|---|--------|-------|--------|-------|
| 1 | `IRegistryProvider` | 46–78 | **registry** | Data-registry DI seam (PROJ-27/PROJ-50). |
| 2 | `ILocatable` | 85–91 | **common (base)** | Composable mixin protocol. |
| 3 | `INamed` | 94–100 | **common (base)** | Composable mixin protocol. |
| 4 | `IOwnable` | 103–109 | **common (base)** | Composable mixin protocol. |
| 5 | `IStarSystem` | 116–143 | **strategy.entities** | |
| 6 | `IStar` | 146–172 | **strategy.entities** | |
| 7 | `IPlanet` | 175–276 | **strategy.entities** | |
| 8 | `IOrderable` | 279–305 | **strategy.entities** | PROJ-238 unified order queue. |
| 9 | `IZoneOccupant` | 308–331 | **strategy.entities** | PROJ-139 multi-hex objects. |
| 10 | `IFleet` | 334–406 | **strategy.entities** | |
| 11 | `IWarpPoint` | 409–418 | **strategy.entities** | |
| 12 | `ISectorEnvironment` | 421–436 | **strategy.entities** | |
| 13 | `IStorm` | 439–460 | **strategy.entities** | PROJ-189. |
| 14 | `IEmpire` | 467–528 | **strategy.domain** | PROJ-193. |
| 15 | `IFacility` | 531–567 | **strategy.domain** | PROJ-193. |
| 16 | `IRaceRegistry` | 570–582 | **strategy.domain** | PROJ-287 race-config DI seam. |
| 17 | `IShipInstance` | 585–625 | **strategy.domain** | PROJ-193. |
| 18 | `ICombatant` | 632–647 | **combat** | |
| 19 | `IDamageable` | 650–664 | **combat** | |
| 20 | `ICombatShip` | 667–742 | **combat** | PROJ-193. |
| 21 | `_has_attrs` (private helper) | 761–763 | **internal helper** | Imported by `game/simulation/interfaces/*` and `game/ai/protocols.py` despite leading underscore — see "Risks". |
| 22 | `is_star_system` | 766–768 | **strategy.entities** (TypeGuard) | |
| 23 | `is_star` | 771–773 | **strategy.entities** (TypeGuard) | |
| 24 | `is_planet` | 776–778 | **strategy.entities** (TypeGuard) | |
| 25 | `is_fleet` | 781–783 | **strategy.entities** (TypeGuard) | |
| 26 | `is_warp_point` | 786–788 | **strategy.entities** (TypeGuard) | |
| 27 | `is_sector_environment` | 791–793 | **strategy.entities** (TypeGuard) | |
| 28 | `is_storm` | 796–798 | **strategy.entities** (TypeGuard) | |
| 29 | `is_zone_occupant` | 801–803 | **strategy.entities** (TypeGuard) | |
| 30 | `is_combatant` | 806–808 | **combat** (TypeGuard) | |
| 31 | `is_empire` | 811–813 | **strategy.domain** (TypeGuard) | |
| 32 | `is_facility` | 816–818 | **strategy.domain** (TypeGuard) | |
| 33 | `is_ship_instance` | 821–823 | **strategy.domain** (TypeGuard) | |
| 34 | `is_combat_ship` | 826–828 | **combat** (TypeGuard) | |
| 35 | `IScene` | 835–857 | **ui** | PROJ-65. |
| 36 | `IResourceReader` | 865–882 | **boundary (sim↔strategy)** | PROJ-90. |
| 37 | `IPostBattleShip` | 885–932 | **boundary (sim↔strategy)** | PROJ-90/PROJ-254. |
| 38 | `is_post_battle_ship` | 935–937 | **boundary** (TypeGuard) | |
| 39 | `is_resource_reader` | 940–942 | **boundary** (TypeGuard) | |
| 40 | `IResourceHolder` | 945–969 | **boundary (sim↔strategy)** | |
| 41 | `is_resource_holder` | 971–973 | **boundary** (TypeGuard) | |
| 42 | `ICamera` | 980–1054 | **ui** | PROJ-106 — depended on by `game/ui/research/*` and tests. |
| 43 | `is_camera` | 1057–1059 | **ui** (TypeGuard) | |
| 44 | `ISerializable` | 1066–1087 | **persistence** | PROJ-228. |

**Cross-domain candidates (do NOT fit a single group cleanly):**

- `_has_attrs` — a private helper with **public consumers** in `game.simulation.interfaces.entity_protocols`, `game.simulation.interfaces.ability_protocols`, and `game.ai.protocols`. It is functionally common infrastructure.
- `ILocatable` / `INamed` / `IOwnable` — cross-cutting composable mixins that strategy entities, combat entities, and arguably empires all conform to. They belong in a `common` bucket.
- `IRaceRegistry` — strategy-domain registry, but *registry-shaped* (read-only get-by-id). Could plausibly sit alongside `IRegistryProvider` in a registry module. Recommendation below puts it in `strategy.py` because it serves strategy-domain consumers (UI panels, race library, planet economy) and groups with the other PROJ-193 domain protocols (`IEmpire`, `IFacility`, `IShipInstance`).

---

## Proposed sub-modules (package layout)

The original PROJ-309 sketch (`combat.py`, `strategy.py`, `ai.py`, `ui.py`, `registry.py`) is **mostly correct but incomplete**. Refinements:

1. **No `ai.py` is needed** — there are no AI-specific protocols in `core/protocols.py` today. AI's own protocols live in `game/ai/protocols.py` and are out of scope for this decomposition.
2. **A `boundary.py` module is required** — `IResourceReader`, `IPostBattleShip`, `IResourceHolder` are explicitly the Strategy↔Simulation boundary contracts (PROJ-90). They aren't strategy-only or combat-only; they are the seam.
3. **A `common.py` module is required** — for `ILocatable`, `INamed`, `IOwnable`, and the `_has_attrs` helper. This pulls the cross-cutting and shared-infrastructure pieces out of any one domain.
4. **A `persistence.py` module** — for `ISerializable` (PROJ-228). One small file, but fits no other group.

### Proposed file layout

```
game/core/protocols/
├── __init__.py        # MANDATORY re-export shim. ALL public symbols re-exported.
├── common.py          # _has_attrs, ILocatable, INamed, IOwnable
├── registry.py        # IRegistryProvider
├── strategy_entities.py  # IStarSystem, IStar, IPlanet, IOrderable, IZoneOccupant, IFleet,
│                         # IWarpPoint, ISectorEnvironment, IStorm + their TypeGuards (~340 LOC)
├── strategy_domain.py    # IEmpire, IFacility, IRaceRegistry, IShipInstance + their TypeGuards (~180 LOC)
├── combat.py          # ICombatant, IDamageable, ICombatShip + their TypeGuards
├── boundary.py        # IResourceReader, IPostBattleShip, IResourceHolder + their TypeGuards
├── ui.py              # IScene, ICamera + is_camera
└── persistence.py     # ISerializable
```

**Decision (PROJ-309 Phase 2.11 cross-review):** A single `strategy.py` was estimated at ~520 LOC — over the 500 cap. Rather than land borderline and split later, commit upfront to the two-file split. The natural seam is **entities** (concrete galaxy-map data: stars, planets, fleets, storms, warp points, sector environments) vs **domain** (organisational/empire-scoped: empires, facilities, races, ship instances) — both groups already exist as separate sections in the source file (lines 116–460 vs 467–625). The split follows the seam, not an arbitrary chunk.

### Per-sub-module detail

#### `game/core/protocols/__init__.py`
- **Responsibility:** Re-export shim (Option A). Preserve every existing `from game.core.protocols import X` import call site verbatim.
- **Owns:** Nothing — pure re-export surface.
- **Estimated LOC:** ~80 (one `from .submodule import (...)` block per sub-module + `__all__` listing every public symbol).

#### `game/core/protocols/common.py`
- **Responsibility:** Cross-cutting composable base protocols and the shared duck-typing helper.
- **Owns:** `_has_attrs`, `ILocatable`, `INamed`, `IOwnable`.
- **Estimated LOC:** ~50.
- **Note:** `_has_attrs` is **promoted from private to public** here because three other protocol modules already import it. We do NOT rename it (callers depend on the existing name) but we should add a docstring explaining its public-helper status. Alternatively, keep it private inside `common.py` and re-export it from `__init__.py` so external `from game.core.protocols import _has_attrs` keeps working. Recommendation: keep the leading underscore (to minimise diff) and re-export from `__init__.py`.

#### `game/core/protocols/registry.py`
- **Responsibility:** Data-registry DI protocol.
- **Owns:** `IRegistryProvider`.
- **Estimated LOC:** ~50.

#### `game/core/protocols/strategy_entities.py`
- **Responsibility:** Strategy-layer **entity** protocols (concrete galaxy-map objects) and their TypeGuards.
- **Owns:** `IStarSystem`, `IStar`, `IPlanet`, `IOrderable`, `IZoneOccupant`, `IFleet`, `IWarpPoint`, `ISectorEnvironment`, `IStorm`, plus TypeGuards `is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`, `is_storm`, `is_zone_occupant`.
- **Estimated LOC:** ~340.
- **Imports from:** `common` (for the optional base mixins), `typing`, `game.core.constants` (already in current file).

#### `game/core/protocols/strategy_domain.py`
- **Responsibility:** Strategy-layer **domain** protocols (organisational/empire-scoped types) and their TypeGuards.
- **Owns:** `IEmpire`, `IFacility`, `IRaceRegistry`, `IShipInstance`, plus TypeGuards `is_empire`, `is_facility`, `is_ship_instance`.
- **Estimated LOC:** ~180.
- **Imports from:** `common`, `typing`, possibly `strategy_entities` if any domain protocol references entity types — verify at implementation time, prefer string-literal forward refs to avoid intra-package coupling.

#### `game/core/protocols/combat.py`
- **Responsibility:** Simulation-side combat-entity protocols and TypeGuards.
- **Owns:** `ICombatant`, `IDamageable`, `ICombatShip`, `is_combatant`, `is_combat_ship`.
- **Estimated LOC:** ~135.
- **Imports from:** `common` (for `_has_attrs`), `typing`.

#### `game/core/protocols/boundary.py`
- **Responsibility:** Strategy ↔ Simulation boundary contracts (PROJ-90/PROJ-254). These are the read-only views one layer takes of the other.
- **Owns:** `IResourceReader`, `IPostBattleShip`, `IResourceHolder`, `is_post_battle_ship`, `is_resource_reader`, `is_resource_holder`.
- **Estimated LOC:** ~125.
- **Imports from:** `common` (for `_has_attrs`), `game.core.constants` (`LayerType`).
- **Note:** The original PROJ-309 sketch placed boundary protocols nowhere explicit. Putting them in their own module makes the architectural seam visible and prevents `strategy.py` or `combat.py` from accidentally claiming them.

#### `game/core/protocols/ui.py`
- **Responsibility:** UI-layer protocols.
- **Owns:** `IScene`, `ICamera`, `is_camera`.
- **Estimated LOC:** ~120.
- **Imports from:** `common` (for `_has_attrs`).

#### `game/core/protocols/persistence.py`
- **Responsibility:** Serialization contract.
- **Owns:** `ISerializable`.
- **Estimated LOC:** ~30.

### LOC totals (rough)

| Sub-module | LOC | <500? |
|---|---|---|
| `__init__.py` | 80 | yes |
| `common.py` | 50 | yes |
| `registry.py` | 50 | yes |
| `strategy_entities.py` | 340 | yes |
| `strategy_domain.py` | 180 | yes |
| `combat.py` | 135 | yes |
| `boundary.py` | 125 | yes |
| `ui.py` | 120 | yes |
| `persistence.py` | 30 | yes |

---

## Public API surface

This is the surface that **must remain importable from `game.core.protocols`**. Derived from the live Grep of `from game.core.protocols import …`:

**Protocol classes (interfaces):**
- `IRegistryProvider`
- `ILocatable`, `INamed`, `IOwnable` (currently no external importers found, but they are public protocols and MUST be re-exported)
- `IStarSystem`, `IStar`, `IPlanet`, `IOrderable`, `IZoneOccupant`, `IFleet`, `IWarpPoint`, `ISectorEnvironment`, `IStorm`
- `IEmpire`, `IFacility`, `IRaceRegistry`, `IShipInstance`
- `ICombatant`, `IDamageable`, `ICombatShip`
- `IScene`
- `IResourceReader`, `IPostBattleShip`, `IResourceHolder`
- `ICamera`
- `ISerializable`

**TypeGuard functions:**
- `is_star_system`, `is_star`, `is_planet`, `is_fleet`, `is_warp_point`, `is_sector_environment`, `is_storm`, `is_zone_occupant`
- `is_empire`, `is_facility`, `is_ship_instance`
- `is_combatant`, `is_combat_ship`
- `is_post_battle_ship`, `is_resource_reader`, `is_resource_holder`
- `is_camera`

**Private-but-imported helper:**
- `_has_attrs` — imported by `game.simulation.interfaces.entity_protocols`, `game.simulation.interfaces.ability_protocols`, and `game.ai.protocols`. **Must remain importable from `game.core.protocols`.**

**Exhaustiveness statement:** the `__init__.py` re-export list MUST cover **every public protocol and TypeGuard defined anywhere under `game/core/protocols/`**, plus `_has_attrs`. This is not a curated subset — it is the full surface. The Phase-2 contract test (below) enforces this.

**No `import *` usage detected.** No caller relies on dynamic module attributes (`getattr(protocols, name)`).

---

## Caller-update strategy

**Choice:** Option A (re-export shim from package `__init__.py`). **Mandatory.**

**Justification — by the numbers:**
- **132 import statements** across **80 distinct files** (Grep `from game.core.protocols import` count).
- These span the entire codebase: `game/ui/screens/*`, `game/strategy/engine/*`, `game/strategy/data/*`, `game/strategy/services/*`, `game/strategy/facade/*`, `game/strategy/interfaces/*`, `game/strategy/validation/*`, `game/simulation/*`, `game/ai/*`, `game/ui/research/*`, `game/ui/panels/*`, `game/ui/services/*`, `game/core/__init__.py`, `game/app.py`, plus extensive test coverage in `tests/unit/core/test_protocols.py` (36 imports), `tests/unit/core/test_protocols_boundary.py`, `tests/unit/core/test_registry_provider.py` (9 imports), etc.
- Caller-migration would be the most invasive change in the project's history for the smallest semantic value. Re-export is free.

**Implementation rule:** `from game.core.protocols import X` MUST continue to work for every X currently in use. Phase 2 implementation must NOT touch any external import sites — only the package's own internals.

---

## Test plan

1. **Contract test (new, blocking):** `tests/unit/core/test_protocols_public_api.py`. Asserts every name in a frozen golden list is importable from `game.core.protocols`. Golden list is generated once from the pre-split file (44 symbols enumerated above). Test fails if any symbol is dropped or renamed during decomposition.
2. **Star-import discipline test:** parametrized test that runs `import game.core.protocols as p; getattr(p, name)` for every name in the golden list. Catches re-export holes the static contract test might miss.
3. **Run `tests/unit/core/test_protocols.py`** (existing, 36 imports) — no changes required; re-export must keep all imports passing.
4. **Run `tests/unit/core/test_protocols_boundary.py`** — boundary protocols specifically.
5. **Run `tests/unit/core/test_registry_provider.py`** — IRegistryProvider DI.
6. **Run `tests/unit/core/test_serializable_protocol.py`** — ISerializable.
7. **Run `tests/unit/research/test_research_scene_di.py`** — ICamera.
8. **Run `tests/unit/ui/test_scene_protocol.py`** — IScene.
9. **Targeted integration sweep:** `pytest tests/unit/strategy/`, `tests/unit/simulation/`, `tests/unit/ui/` — all three layers depend on these protocols; if any imports break, those suites will surface it.
10. **Full sharded suite:** `python Tools/test_sharded/test_sharded.py` before Phase 2 closure. Baseline 15405 must hold.

---

## Risks

1. **Import cycles between domain sub-modules.** Currently the file is one module so cycles are impossible. After split:
   - `strategy.py` may want to type-hint a method using `LayerType` (already from `core.constants`, fine).
   - `combat.py` and `boundary.py` both need `LayerType`. Each imports it from `game.core.constants` directly — same as today. No cycle introduced.
   - `common.py` is a leaf (no protocol imports). Every other sub-module imports from it. No cycle.
   - **No protocol currently inherits from another protocol in this file.** This is a major risk-reducer — there are no Protocol-on-Protocol inheritance graphs to thread through sub-modules. Phase 2 implementation must verify this still holds at split time and flag any inheritance for special handling.

2. **`_has_attrs` private-public ambiguity.** The leading-underscore name is imported by three other modules. Recommendation: place it in `common.py`, re-export it from `__init__.py` to preserve the existing import path, and add a docstring noting it is treated as public despite the underscore. **Do NOT rename it** — that would break call sites in `simulation/interfaces/*` and `ai/protocols.py`.

3. **TypeGuard / Protocol pairing must stay co-located.** Every `is_X` TypeGuard MUST live in the same sub-module as its `IX` protocol. Otherwise readers lose the symmetry that makes this pattern legible. Layout above respects this rule for all 17 pairs.

4. **`ILocatable` / `INamed` / `IOwnable` are unused base mixins today.** Grep returned no external importers. Risk: if we silently leave them in `common.py` but no protocol inherits from them, they remain dead weight. Recommendation: keep them — they are documented as "Base Protocols (Composable)" and removing them is out of scope for a decomposition project. Flag for a separate cleanup ticket.

5. **`strategy.py` borderline-LOC risk.** Estimated 520 LOC; the `IPlanet` protocol alone is 100 lines and `IFleet` is 75. If the actual split lands above 500, fall back to the two-file plan in the strategy bullet above (`strategy_entities.py` + `strategy_domain.py`). This is a Phase 2 measurement decision, not a Phase 1 design lock-in.

6. **Mock/duck-typing test compatibility.** All 14 TypeGuards use `_has_attrs` (hasattr-based duck typing). After the split, existing mocks (MagicMock, Mock) must still pass each `is_X` check. Because the implementation does not change — only its file location — this is a non-risk, but call out for the contract test to confirm.

7. **`game/core/__init__.py` re-export.** That file already does `from game.core.protocols import (...)`. After decomposition `game.core.protocols` becomes a package, not a module, but the dotted import path is unchanged. The Python import system treats package-with-`__init__.py` identically to a module for this case. No change required — but Phase 2 must verify `game/core/__init__.py` still resolves.

---

## Open questions

1. **Should `IRaceRegistry` live in `strategy.py` or `registry.py`?** It is registry-shaped but strategy-scoped. Current recommendation: `strategy.py` (groups with PROJ-193 domain protocols). Cross-review please confirm.
2. **Should `_has_attrs` be renamed to `has_attrs` (drop the underscore)?** Doing so signals it is public. Doing so requires touching three other files. Current recommendation: leave it underscored; document as "intentionally public despite naming". Cross-review please confirm.
3. **Strategy.py 500-LOC borderline:** if Phase 2 measurement shows >500 LOC, do we split entities/domain immediately or accept a short overrun? Current recommendation: split immediately if measured >500; the entities-vs-domain seam is natural.
4. **Should the decomposed package live at `game/core/protocols/` (replacing the file) or at `game/core/_protocols/` with `protocols.py` becoming the shim?** Current recommendation: package replaces file. Python does not require an intermediate. The package-with-`__init__.py` *is* the shim.
5. **Should we add a Phase-2 lint rule preventing new symbols from being added directly to `__init__.py`?** Goal: keep the package "difficult to grow back into a mega-file" by forcing every new protocol into a domain sub-module. Cross-review opinion welcome.
6. **`ILocatable` / `INamed` / `IOwnable` cleanup:** out of scope for PROJ-309, but are these mixins worth keeping? Zero external importers today. Defer to a separate dead-code ticket.
