# PROJ-334 — Design / algorithmic context

> Production-side surface to pin. Read before writing tests so the gap audit is grounded.

## `game/strategy/data/pathfinding.py`

### Public surface

| Symbol | Kind | Signature | Purity |
|---|---|---|---|
| `strip_start_hex(current_location, path)` | function | `(HexCoord, Optional[PathT]) -> Optional[PathT]` | Pure |
| `find_path_deep_space(start, end)` | function | `(HexCoord, HexCoord) -> List[HexCoord]` | Pure (delegates to `hex_linedraw`) |
| `find_path_interstellar(start_system, end_system, galaxy)` | function | A* over warp graph | Pure given galaxy |
| `get_system_at_hex(galaxy, hex_c, radius=50)` | function | Spatial lookup, O(1) fast-path then radius search | Pure |
| `find_nearest_system(galaxy, hex_c)` | function | O(n) scan over all systems | Pure |
| `find_hybrid_path(galaxy, start_hex, end_hex, fleet=None, can_warp=None)` | function | Stitches deep-space segments with warp jumps | Pure given inputs |
| `project_fleet_path(fleet, galaxy, max_turns=10)` | function | Delegates to `FleetNavigationService.project_path_as_dicts` | Impure (delegates) |
| `calculate_intercept_point(chaser, target_fleet, galaxy)` | function | A* intercept across hybrid graph | Pure given galaxy |
| `_extract_chaser_info` | private | Tuple destructuring of Fleet/NavigationState | Pure |
| `_ChaserProxy` / `_ChaserProxyCapabilities` | private | Adapter for `find_hybrid_path` | Pure |
| `_evaluate_intercept_candidates` | private | Inner loop of intercept; early-exit logic | Pure given inputs |

### Algorithm shapes

- **A* (interstellar):** Heap-priority queue. G-cost = sum of `hex_distance` along warp lanes. H-cost = `hex_distance` from candidate to goal. Cost stored in `cost_so_far[name]`. Reconstruct via `came_from[name]` walk.
  - **Termination:** When goal popped, breaks.
  - **Failure:** Returns `None` if goal not in `came_from` after queue exhausted (disconnected subgraph).
  - **Same-source-and-target shortcut:** Returns `[start_system]` immediately.
- **Deep-space linedraw:** Pure `hex_linedraw(start, end)` from `game.core.hex_math`. Deterministic.
- **Hybrid path:** Trichotomy — (A) same system → linedraw; (B) cannot warp → linedraw; (C) interstellar with warp → A* over warp graph + linedraw segments + warp-jump appends. Fallback to linedraw if A* returns None.
- **Intercept:** Project target's path 50 turns ahead, hybrid-path the chaser to each candidate, pick earliest where `chaser_turns < target_turn + 1`. Early-exit on perfect synchronization. Fallback to target endpoint or current location.

### Determinism boundaries

- **Pure-deterministic:** `strip_start_hex`, `find_path_deep_space`, `find_path_interstellar`, `find_hybrid_path`, `get_system_at_hex`, `find_nearest_system`.
- **Heuristic ordering:** `find_path_interstellar` tie-breaks by heap insertion order (Python heapq); when two paths have equal `priority`, the first inserted wins. **Stable** for fixed graph traversal.
- **Indirect determinism:** `project_fleet_path` and `calculate_intercept_point` rely on `FleetNavigationService` ordering — outside this project's scope.

### Edge cases (gap-audit will mark covered/uncovered)

1. `find_path_interstellar`: target == source → `[start]`.
2. `find_path_interstellar`: unreachable target (disconnected component) → `None`.
3. `find_path_interstellar`: single-hop (direct warp connection).
4. `find_path_interstellar`: same `hex_distance` ties — heap order determines pick.
5. `find_path_deep_space`: start == end → typically `[start]` (verify what `hex_linedraw` returns).
6. `find_hybrid_path`: `can_warp=False` overrides fleet warp capability.
7. `find_hybrid_path`: `fleet=None, can_warp=None` defaults to `can_use_warp=True`.
8. `find_hybrid_path`: missing reciprocal warp point in `next_sys` → fallback append `next_sys.global_location` (lines 280-285).
9. `find_hybrid_path`: A* returns None mid-stitch → fallback to deep-space linedraw.
10. `get_system_at_hex`: O(1) fast-path on exact match; radius search otherwise.
11. `get_system_at_hex`: `radius=0` (degenerate); `radius` exceeding galaxy diameter (returns nearest).
12. `find_nearest_system`: empty galaxy → `None`.
13. `calculate_intercept_point`: `chaser_speed <= 0` → returns `target.location` (no chase).
14. `calculate_intercept_point`: empty `target_path` → fallback to `[{'hex': target.location, 'turn': 0}]`.
15. `calculate_intercept_point`: no intercept possible → returns endpoint of target's path.
16. `strip_start_hex`: preserves tuple-vs-list type; `path is None` → `None`; `path == []` → `[]`; `path[0] != current` → unchanged.

### Performance-sensitive (note, do NOT test)

- `find_path_interstellar` calls `galaxy.get_system_by_name(current_name)` per pop — O(n) per A* iteration. Acceptable for galaxy sizes <500 systems; flagged for future optimization (NOT this project's job to fix).
- `get_system_at_hex` linear scan when no exact-hex match. Acceptable for small galaxies.

---

## `game/strategy/data/galaxy_system_generator.py`

### Public surface

| Symbol | Kind | Signature | Purity |
|---|---|---|---|
| `GalaxySystemGenerator.__init__` | method | `(star_gen, planet_gen, naming, image_registry, storm_gen=None)` | Pure |
| `GalaxySystemGenerator.generate_planets` | method | `(galaxy, system, rng=None) -> None` | Mutates `system.planets`, calls `galaxy.register_planet` |
| `GalaxySystemGenerator.generate_storms` | method | `(system, blueprint_config, rng) -> None` | Mutates `system.storms`; no-op if `storm_gen is None` |
| `GalaxySystemGenerator.generate_systems` | method | `(galaxy, count, min_dist=10, placement_strategy=None, rng=None, storm_blueprint_config=None) -> List[StarSystem]` | Mutates `galaxy`; main entry point |
| `_load_json_or_empty` | function | Lazy JSON loader; returns `{}` if missing | Pure |
| `_load_planet_types` | function | Lazy load `Paths.PLANET_TYPES_FILE`; cached in module global | Memoised |
| `_apply_intrinsic_abilities` | function | Shared roller; idempotent on non-empty `intrinsic_abilities` | Pure given inputs |
| `_apply_planet_intrinsic_abilities` | function | Wrapper for planets | Pure given inputs |
| `_load_star_types` | function | Memoised | Memoised |
| `_apply_star_intrinsic_abilities` | function | Wrapper for stars | Pure given inputs |
| `_load_system_archetypes` | function | Memoised | Memoised |
| `_apply_system_archetype` | function | ~15% chance archetype roll; idempotent if pre-set; skips `void` key | Pure given inputs |

### Determinism contract

- **Same `rng=Random(seed)` → same system list.** `generate_systems` derives two child seeds from the parent RNG (`storm_seed`, `intrinsic_seed`) via `rng.randint(0, 2**32-1)`, ensuring storm/intrinsic streams don't perturb the placement stream.
- **`rng=None` → unseeded, non-deterministic.** Documented behavior; not a contract to test.
- **Module-level JSON caches (`_PLANET_TYPES_CACHE`, `_STAR_TYPES_CACHE`, `_SYSTEM_ARCHETYPES_CACHE`)** persist across calls and across tests. **Testability concern:** must reset between tests OR accept the cached state. Prefer working WITH the cache (loaded once at import) since the JSON files are committed-data; only reset if a test injects a fake.

### Generation parameters

| Param | Default | Behavior |
|---|---|---|
| `count` | required | Target number of systems. May not be reached if galaxy is saturated. |
| `min_dist` | 10 | Minimum hex distance between systems. |
| `placement_strategy` | `RandomPlacementStrategy` | Lazy-imported default. |
| `rng` | `None` | If None, both storm_rng and intrinsic_rng are unseeded `Random()`. |
| `storm_blueprint_config` | `None` | If None and `storm_gen is not None`, defaults to `{"storms": {"count": {"min": 0, "max": 2}}}`. |

### Validation invariants

1. Every generated system has a non-None `name` (from `naming.get_system_name()`).
2. Every generated system has a `coord` distinct from all existing — placement_strategy.sample_location enforces this via `min_dist`.
3. `len(generated) <= count` (never exceeds; may be less if saturated).
4. `consecutive_failures` resets on every successful placement.
5. Saturation: 10 consecutive failures aborts the loop.
6. Spatial index is built ONCE and incrementally updated (not rebuilt per placement).
7. `storm_rng` and `intrinsic_rng` are independent streams seeded from parent RNG.
8. `_apply_system_archetype` skips `void` archetype key.
9. `_apply_*_intrinsic_abilities` is idempotent — non-empty `intrinsic_abilities` is left alone.

### Edge cases (gap-audit will mark covered/uncovered)

1. `count=0` → returns `[]`, no mutations to galaxy.
2. `count=1` → single placement, no min_dist check.
3. Highly saturated galaxy (`min_dist` >> `radius`) → returns fewer than `count`, exits via failure counter.
4. `seed=0`, `seed=2**32-1` → deterministic boundary seeds.
5. Two calls with same seed → identical generated list (golden test).
6. Two calls with different seeds → different generated list (sanity test).
7. `rng=None` → no determinism contract; just runs without exception.
8. `storm_gen=None` → `generate_storms` is a no-op.
9. `storm_blueprint_config=None and storm_gen is not None` → uses default config.
10. `system.stars` empty → `generate_planets` early-return.
11. `_apply_intrinsic_abilities` with empty `types_data` → no-op (no exception).
12. `_apply_intrinsic_abilities` with entity already having abilities → idempotent skip.
13. `_apply_system_archetype` when `system.archetype is not None` → idempotent skip.
14. `_apply_system_archetype` with `archetypes` dict containing only `'void'` → no-op.
15. `_apply_system_archetype` when `rng.random() > chance` → no-op.

### Testability concerns

- **Module-level JSON caches** — reset via `monkeypatch.setattr` if a test needs a controlled types-table. Default tests should use the real loaded data.
- **`generate_systems` requires Galaxy with `radius`, `systems`, `add_system`, `register_planet`** — use a minimal hand-rolled fake or the existing `tests/fixtures/` Galaxy fixture if one exists (verify in Phase 0).
- **`generate_systems` requires `placement_strategy`, `star_generator`, `planet_generator`, `naming`, `image_registry`** — use minimal hand-rolled fakes that return canned values. Avoid `unittest.mock` for readability.
- **No `random.seed()` mutation** — caller-injected `rng` is the only entry point. Good for testability.
