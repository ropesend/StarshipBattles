# PROJ-447 Phase 3: Pre-PEP-604 annotation sweep (research/assets/engine/simulation loaders)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-447 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** None (independent of other phases)
**Objective:** Mechanical sweep of pre-PEP-604 annotation drift across the lower-layer loaders. Sibling sweep to PROJ-446 Phase 2 Task 2.5 (which covers `game/core/protocols/*.py`). Same recipe; different files. Per CLAUDE.md: "Do not introduce legacy `Optional[int]`, `List[int]`, or `Dict[str, T]` in new code"; existing code is grandfathered but the sweep modernizes the surfaces most-imported by other layers.

**Cross-bucket file-ownership rule:** Only edit `game/research/`, `game/assets/`, `game/engine/` (low-level), `game/simulation/`. Skip files PROJ-444/445/446 own.

**Source-of-truth findings:** [`findings/bucket_d_simulation_ai_research_engine_docs_scan.md`](findings/bucket_d_simulation_ai_research_engine_docs_scan.md) — F-D-013, F-D-014, F-D-015, F-D-016, F-D-017, F-D-018, F-D-019.

**Recipe (apply uniformly):**
- `file_path: str = None` → `file_path: str | None = None`
- `Dict[K, V]` → `dict[K, V]`
- `List[X]` → `list[X]`
- `Optional[X]` → `X | None`
- Public class `__init__(self):` → add `-> None` return annotation
- Public methods missing return annotations → add the right return type
- Drop `from typing import Optional, Dict, List` imports where they become unused
- Add `from __future__ import annotations` only if it's not already present AND forward refs would otherwise need to be string-quoted

---

## Tasks

### Task 3.1: F-D-013 + F-D-014 — game/research/data/tech_tree.py [Simple]
**File:** `game/research/data/tech_tree.py:26, 31`
**Tests:** `pytest tests/unit/research/ tests/integration/research_workflow/ -v`

- [x] Read existing `TechTree.__init__(self):` at line 26 and `load_from_json(cls, file_path: str = None)` at line 31
- [x] **GREEN — F-D-014**: Add `-> None` return to `__init__`
- [x] **GREEN — F-D-013**: Change `file_path: str = None` → `file_path: str | None = None` on `load_from_json`. Add return annotation if absent.
- [x] Sweep sibling sites in the research module flagged by the finding text:
  - `game/research/data/research_tracker.py:56` (`session_seed: int = None`) and `:168` (`tech_levels: Dict[str, int] = None`)
  - `game/research/systems/research_service.py:33` (`tech_levels: Dict[str, int] = None`)
- [x] Apply the same recipe to each
- [x] Run targeted tests.

### Task 3.2: F-D-015 + F-D-016 — game/assets/asset_manager.py [Small]
**File:** `game/assets/asset_manager.py:5, 15, 31, 54, 70, 95, 121`
**Tests:** `pytest tests/unit/assets/ -v` (if a test dir exists; otherwise sharded suite)

- [x] Read the AssetManager class — confirm `from __future__ import annotations` is at line 1 (per the finding)
- [x] **GREEN — F-D-016**: Replace `_default_asset_manager: Optional['AssetManager'] = None` with `_default_asset_manager: "AssetManager | None" = None`. Drop the `from typing import Optional` import if no longer needed.
- [x] **GREEN — F-D-015**: Annotate the 5-method cluster:
  - `__init__(self) -> None:`
  - `load_manifest(self, path: str | None = None) -> None:` (return type may differ — verify)
  - `load_image(self, category: str, key: str) -> pygame.Surface:` (verify the actual return type from the method body)
  - `load_group(self, category: str, group_key: str) -> ...:` (verify)
  - `get_random_from_group(self, category: str, group_key: str, seed_id: str | None = None) -> pygame.Surface:` (verify)
- [x] Run targeted tests (if any) + sharded suite.

### Task 3.3: F-D-017 — game/engine/collision.py + physics.py [Simple]
**Files:** `game/engine/collision.py:68`, `game/engine/physics.py:53`
**Tests:** `pytest tests/unit/engine/ -v` (low-level engine tests)

- [x] Read `CollisionSystem.__init__(self, rng: 'random.Random' = None)` at collision.py:68
- [x] **GREEN**: Drop the string-quoted forward ref. Change to `(self, rng: random.Random | None = None) -> None`. Verify `import random` is at the top of the file; add it if not.
- [x] Read `PhysicsBody.__init__(self, x, y, angle=0)` at physics.py:53
- [x] **GREEN**: Annotate as `(self, x: float, y: float, angle: float = 0.0) -> None`. (Verify the angle's natural unit — likely radians as float.)
- [x] Run targeted tests.

### Task 3.4: F-D-018 — game/simulation/components/component_loader.py [Simple]
**File:** `game/simulation/components/component_loader.py:78, 186`
**Tests:** `pytest tests/unit/simulation/components/ -v`

- [x] Read `load_components_data(file_path: str = None, ...)` at line 78 and `load_modifiers_data(file_path: str = None) -> dict` at line 186
- [x] **GREEN**: Change `file_path: str = None` → `file_path: str | None = None` on both. Verify or add the return type annotations (`-> dict | None` if the function can return None on error).
- [x] Run targeted tests.

### Task 3.5: F-D-019 — game/simulation/entities/ship_loader.py [Simple]
**File:** `game/simulation/entities/ship_loader.py:51, 118`
**Tests:** `pytest tests/unit/simulation/entities/ -v`

- [x] Same recipe as F-D-018 — two public module-level loaders with `file_path: str = None`. Update both.
- [x] Run targeted tests.

---

## Phase Completion Checklist

- [x] All 6 annotation-sweep tasks complete
- [x] No remaining `file_path: str = None` patterns in the touched files (run `rg -n "str\s*=\s*None|Dict\[.*\]\s*=\s*None" game/research/ game/assets/ game/engine/ game/simulation/components/component_loader.py game/simulation/entities/ship_loader.py` — should return 0 hits)
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [x] Run `python Projects/scripts/validate_phase.py PROJ-447 3` — PASSED
- [x] Update status to `Complete`; plan.md phase table + Current State → Phase 4

## Coordination

- **PROJ-446 Phase 2 Task 2.5**: Same recipe, different files (protocol modules in `game/core/protocols/`). No conflict; either project can ship first.

## Notes

- Pure mechanical phase. No behavior change.
- If type-checking surfaces a real type bug while annotating: investigate the root cause; do not silence with a `# type: ignore`.
- F-D-027 (deep-dive DI audit on simulation loaders) is OUT of scope here — that's a follow-up audit ticket, not a Phase 3 task.
