# Rust/Bevy Migration Feasibility Analysis

**Date:** 2026-02-07
**Type:** General Review - Migration Feasibility
**Scope:** Entire codebase evaluation for Rust + Bevy migration
**Agents Used:** 6 (Core Architecture, Simulation Engine, UI/Rendering, Strategy/AI, Test Suite, Data Model/Serialization)

---

## Executive Summary

**Feasibility: YES - Achievable but substantial effort (12-18 months for a solo developer)**

The codebase is **unusually well-suited** for migration due to:
- Clean layer separation (Core -> Simulation -> Strategy -> AI -> UI, one-way dependencies)
- Existing component/ability system that maps naturally to Bevy's ECS
- Heavy use of type hints, dataclasses, and enums (translate directly to Rust)
- Strict dependency injection (PROJ-50) - no hidden global state
- Data-driven design (JSON component definitions work with serde)
- Good test coverage (6,246 tests provide a behavioral specification)

The main challenges are:
- **UI layer** is deeply coupled to Pygame (~60% of UI code is Pygame-specific)
- **Dynamic dispatch** via duck typing / `isinstance()` needs redesign for Rust's type system
- **Formula evaluation** system uses Python `eval()` - needs an expression parser crate
- **pygame_gui** has 550+ references with no direct Bevy equivalent

---

## Codebase Scale

| Layer | Files | Est. Lines | Migration Difficulty |
|-------|-------|-----------|---------------------|
| Core | ~30 | ~3,000 | Easy |
| Simulation | ~50 | ~8,000 | Moderate-Hard |
| Strategy | ~40 | ~5,000 | Moderate |
| AI | ~15 | ~2,500 | Moderate |
| UI | ~130 | ~15,000 | Hard (Pygame-specific) |
| Tests | ~650+ | ~30,000 | N/A (rewrite in Rust) |
| Data/JSON | ~20 files | N/A | Easy (serde) |
| **Total** | **~300+** | **~50,000+** | |

---

## Architecture Alignment: Python vs Bevy ECS

### What Maps Naturally

| Python Pattern | Bevy Equivalent | Notes |
|---------------|----------------|-------|
| `Ship` class with properties | Entity + Ship component | ECS natural fit |
| `Component` with abilities | Entity + ability components | Better than current OOP |
| `BattleEngine.update()` tick loop | Bevy System schedules | Cleaner separation |
| `GameRegistries` (immutable DI) | `Res<GameRegistries>` | Perfect match |
| `SpatialGrid` hash map | Bevy spatial queries | Built-in support |
| `GameState` enum | Bevy `States<GameState>` | First-class support |
| `IScene` protocol | Bevy plugins per screen | Better isolation |
| Config classes | `Res<PhysicsConfig>` | Same pattern |
| JSON data files | serde_json deserialization | Industry standard |
| `@dataclass(frozen=True)` | `#[derive(Clone)]` struct | Direct mapping |
| Python `Enum` | Rust `enum` | Stronger in Rust |

### What Requires Redesign

| Python Pattern | Challenge | Rust Solution |
|---------------|-----------|---------------|
| `isinstance()` polymorphic dispatch | No runtime type checking | Trait objects or enum dispatch |
| `ABILITY_REGISTRY` string-to-class map | No dynamic class instantiation | Enum-based factory or proc macros |
| `eval()` formula system | No built-in eval | `rhai`, `evalexpr`, or custom parser |
| Duck typing (`hasattr`, `getattr`) | No duck typing | Traits with default impls |
| `copy.deepcopy()` for isolation | Expensive Clone | `Arc<T>` or structural sharing |
| Module-level registry references | No mutable module globals | `Res<T>` / `ResMut<T>` |
| Circular refs (Ship <-> Component) | Borrow checker prevents | Entity IDs + queries |
| pygame_gui (550 references) | No equivalent | `bevy_egui` or Bevy UI |

---

## Staged Migration Strategy

### Recommended Approach: **Strangler Fig Pattern**

Rather than a big-bang rewrite, migrate layer-by-layer from the bottom up, potentially running Python and Rust in parallel during transition (via PyO3 FFI if desired).

### Stage 1: Core Layer (2-4 weeks)
**Difficulty: Easy**

Port the foundation:
- `Vector2` math -> `glam::Vec2` (Bevy's built-in)
- Config classes -> Rust structs with `Default`
- Constants/Enums -> Rust enums (stronger typing)
- `GameRegistries` -> Bevy `Resource`
- JSON loading utilities -> `serde_json`
- Formula system -> `evalexpr` or `rhai` crate
- Logging -> `tracing` crate

**Why first:** Zero dependencies on other layers. Self-contained. Can validate Rust patterns early.

### Stage 2: Simulation Engine (6-10 weeks)
**Difficulty: Moderate-Hard**

The heart of the game:
- `Ship` entity + component data -> Bevy ECS entities
- Ability system (28+ types) -> Trait-based with enum dispatch
- `BattleEngine` tick loop -> Bevy SystemSet with ordering
- `ProjectileManager` -> Bevy entities with velocity
- `SpatialGrid` -> Bevy's spatial queries or custom grid
- Damage pipeline -> Pure functions (excellent Rust fit)
- Stat calculator with modifier stacking -> System with queries

**Key challenge:** The ability system uses ~28 subclasses with polymorphic dispatch. In Rust, this becomes either:
- A large `AbilityKind` enum (simple, performant, but verbose)
- Trait objects `Box<dyn Ability>` (flexible, slight overhead)
- **Recommendation:** Enum dispatch for the ~28 known types. Games don't need open extensibility.

**Key benefit:** The simulation layer is almost entirely **pure computation** with minimal side effects. This is where Rust shines most - expect 5-10x performance improvement for large fleet battles.

### Stage 3: Strategy Layer (4-6 weeks)
**Difficulty: Moderate**

- Galaxy/hex math -> Pure algorithms, straightforward port
- Fleet/order system -> Enum-based orders, entity references
- Empire data -> Simple struct
- Turn engine -> Sequential system pipeline
- Save/load -> `serde` with JSON (already well-structured)
- Galaxy generation (Kruskal's MST, hex placement) -> Standard algorithms

**Key challenge:** Fleet orders use polymorphic targets (HexCoord | Planet | Fleet). In Rust, this becomes a clean enum:
```rust
enum OrderTarget {
    Location(HexCoord),
    Planet(PlanetId),
    Fleet(FleetId),
}
```

### Stage 4: AI System (3-5 weeks)
**Difficulty: Moderate**

- Behavior system (9 types) -> Enum-based state machine
- Target evaluator -> Pure scoring functions
- Strategy manager -> Bevy Resource loaded from JSON
- Formation control -> Vector math (well-suited to Rust)

**Key benefit:** AI hot loop benefits enormously from Rust performance. Complex targeting evaluations across many ships become trivially fast.

### Stage 5: UI Layer (8-14 weeks)
**Difficulty: Hard - This is the biggest challenge**

This is ~60% of the migration effort because:
- 15,000 lines of UI code, 60% Pygame-specific
- 550+ pygame_gui references (no direct Bevy equivalent)
- Custom rendering (Surface blitting, draw calls) -> Bevy sprites/meshes
- Font rendering -> Bevy text system (requires bundled fonts)
- Ship builder is the most complex screen (~7,712 lines)

**UI Library Decision (Critical):**

| Option | Pros | Cons |
|--------|------|------|
| **bevy_egui** (Recommended) | Fast iteration, immediate mode, rich widgets | Not "native" Bevy, less customizable |
| **Bevy UI** | Native ECS integration, full control | Verbose, limited widget library |
| **Custom** | Full control, optimized | Enormous effort |

**Recommendation:** Use `bevy_egui` for complex panels (ship builder, strategy overlay) and native Bevy sprites for the battle view. This hybrid approach minimizes effort while maintaining quality where it matters (combat visuals).

**Sub-phases:**
1. Battle rendering (sprites, beams, projectiles) - Most visual impact
2. Camera system (already well-abstracted, clean port)
3. HUD/panels (battle stats, controls)
4. Main menu + screen transitions
5. Ship builder (heaviest lift - consider last)
6. Strategy map (hex rendering, fleet display)

---

## Detailed Layer Analysis

### Simulation Engine Deep Dive

**Core Classes & Sizes:**
- `BattleEngine` (674 lines) - Central tick-based orchestrator
- `Ship` (870 lines) - Combat entity with layered components
- `Component` (756 lines) - Ship modules with ability instances
- `ProjectileManager` - Projectile lifecycle + collision detection
- `SpatialGrid` - Hash-based spatial indexing

**Tick Loop (each update):**
1. Rebuild spatial grid with alive ships/projectiles
2. Update AI controllers (target selection, behavior)
3. Update ships (movement, weapons, abilities)
4. Process attacks (projectiles, beams, launches)
5. Process ramming collisions
6. Update projectiles (movement, collision detection)
7. Check battle end conditions

**Ability System Architecture:**
- 28+ ability types: WeaponAbility, CombatPropulsion, ShieldProjection, etc.
- Registry pattern: `ABILITY_REGISTRY` maps string names to classes
- Polymorphic dispatch via `isinstance()` + MRO class name fallback
- Two-stage aggregation: collect abilities, then apply modifiers
- Stat bindings: `STAT_BINDINGS` list defines how modifiers affect ability values

**Formula System:**
- Strings starting with `=` (e.g., `"=50 * sqrt(ship_class_mass / 1000)"`)
- Safe `eval()` with restricted namespace (whitelisted math functions)
- AST validation before evaluation
- ~50+ formulas in components.json

**Damage Pipeline:**
1. Emissive Armor (flat reduction per hit)
2. Crystalline Armor (absorbs + recharges shields)
3. Shields (absorption pool)
4. Hull Layers (weighted random component selection)

**Pure Logic vs Side Effects:**
- **Pure (Rust-friendly):** Damage calculations, formula evaluation, stat aggregation, targeting/lead calculation, collision detection, physics movement, modifier stacking
- **Side effects:** File I/O (JSON loading), logging, registry updates, randomness, resource consumption

### UI Layer Deep Dive

**Structure:** 131 Python files, ~15,000 lines
- `game/ui/screens/` - Main screens (battle, strategy, builder, menu)
- `game/ui/renderer/` - Ship drawing, camera, sprites
- `game/ui/panels/` - Battle panels, builder widgets
- `game/ui/services/` - UI-to-domain adapters (DTOs)
- `game/ui/builder/` - Ship designer (7,712 lines across 23 files)

**Pygame Dependency Density:**
| Feature | Count | Migration Path |
|---------|-------|---------------|
| `pygame.draw.*` | ~200+ | Bevy sprite/mesh rendering |
| `pygame.font.render()` | ~50+ | Bevy text or bevy_text crate |
| `pygame.image.load()` | ~30+ | Bevy asset loader |
| `pygame.transform` | ~40+ | Bevy shader pipeline |
| `pygame.Surface` | ~100+ | Bevy RenderTarget/Canvas |
| `pygame.Rect` | ~150+ | Custom rect type |
| `pygame.event` | ~60+ | Bevy input system |
| `pygame_gui.*` | ~550 | bevy_egui or Bevy UI |

**Good patterns that survive migration:**
- DTO pattern (BattleUIService) - clean domain/UI separation
- Camera system - well-abstracted coordinate transforms
- Scene protocol (IScene) - maps to Bevy plugins
- Theme/color centralization - direct port
- Modal input states - maps to Bevy States

**No particle system detected** - makes migration easier.

### Strategy & AI Layer Deep Dive

**Strategy Layer (~4,300 lines):**
- Galaxy: hierarchical data (Galaxy -> StarSystem -> Planet/WarpPoint)
- Hex math: axial coordinates, pure algorithms
- Fleet/orders: polymorphic order targets, queue-based processing
- Turn engine: sequential phases (resources, orders, movement, combat, production)
- Save/load: version 2.0.0, JSON-based, no backward compatibility

**AI System (~2,000 lines):**
- AIController: target acquisition + behavior selection + execution
- 9 behavior types: Kite, AttackRun, Ram, Flee, Formation, Orbit, DoNothing, Stationary, Erratic
- TargetEvaluator: data-driven scoring rules (distance, mass, damage, capability)
- StrategyManager: JSON-loaded strategy definitions
- Performance caching: pre-calculated distances, capability checks

### Data Model & Registry System

**Three-Tier Access Pattern:**
1. Domain Services (computed access, highest level)
2. GameRegistries DI (recommended, PROJ-50)
3. RegistryManager singleton (low-level, special operations)

**Type System Usage:**
- ~80% of public methods have type hints
- Extensive dataclasses (frozen for DTOs, mutable for entities)
- Extensive enums (AttackType, GameState, LayerType, etc.)
- Protocols for cross-layer contracts (IValidationRule, IScene)

---

## Benefits of Migration

### Performance
- **5-10x faster simulation** for large fleet battles (no GC pauses, cache-friendly ECS)
- **Native multithreading** via Bevy's parallel systems (currently limited by Python's GIL)
- **Faster startup** - no interpreter overhead
- **Consistent frame times** - no GC stalls during combat

### Type Safety & Correctness
- **Compile-time guarantees** replace runtime `isinstance()` checks
- **No None/null errors** - `Option<T>` enforces handling
- **Exhaustive matching** on enums prevents missed cases
- **Borrow checker** prevents circular reference bugs

### Developer Experience
- **Bevy ECS** is a natural fit for the existing component/ability architecture
- **cargo test** integrates testing at the language level
- **serde** makes JSON serialization trivial and type-safe
- **Cross-platform** compilation with zero additional effort

### Distribution
- **Single binary** - no Python/Pygame installation required
- **Smaller distribution** - no bundled interpreter
- **WebAssembly** target possible (play in browser via Bevy WASM support)

---

## Risks & Challenges

### High Risk
1. **UI reimplementation effort** - 50% of the work, uncertain timeline
2. **Learning curve** - Rust ownership/lifetimes + Bevy ECS patterns
3. **Feature velocity during migration** - Python features can't easily port mid-flight
4. **pygame_gui replacement** - No perfect equivalent; will look/feel different

### Medium Risk
1. **Formula system** - Python `eval()` is powerful; Rust expression parsers are less flexible
2. **Ability polymorphism** - 28+ types need careful enum/trait design upfront
3. **Test migration** - 6,246 tests need rewriting (but Rust's type system catches many bugs statically)
4. **Save format compatibility** - JSON structure stays, but deserialization logic changes

### Low Risk
1. **Core math/physics** - Pure computation ports trivially
2. **JSON data files** - Same files, different parser
3. **Configuration** - Direct struct mapping
4. **Galaxy generation** - Standard algorithms

---

## Testing Strategy for TDD Transition

### Current State
- 6,246 tests across unit, integration, and simulation test suites
- Good coverage of simulation layer
- pytest-xdist for parallel execution (12 workers)
- conftest.py with registry isolation fixtures
- Simulation test scenarios with StaticTargetScenario pattern
- Session-level caching via SessionRegistryCache (thread-safe singleton)

### Recommendations Before Migration

1. **Document behavioral contracts as specifications**
   - Each test implicitly defines a behavioral contract
   - Write a spec doc extracting: "given X setup, when Y happens, then Z result"
   - This spec becomes the TDD target for Rust reimplementation

2. **Add property-based tests for math/formulas**
   - Current tests are example-based
   - Add `hypothesis` tests for damage calculations, hit chance, physics
   - These translate to `proptest` in Rust
   - Catches edge cases the example tests miss

3. **Increase integration test coverage for AI behaviors**
   - AI behavior correctness is hard to verify after migration
   - Add golden-file tests: record AI decisions for known scenarios
   - Compare Rust AI output against Python golden files

4. **Create end-to-end battle regression tests**
   - Seed deterministic battles, record outcomes (winner, damage dealt, ticks)
   - Use as regression suite: Rust version must produce identical results
   - The simulation_tests framework already does this partially

5. **Test data files are the bridge**
   - Ship JSONs, component JSONs, and battle configs are language-agnostic
   - Same test data files feed both Python and Rust tests
   - This is the strongest guarantee of behavioral equivalence

### Rust Testing Approach
```rust
// cargo test provides built-in test framework
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn damage_pipeline_emissive_armor_reduces_damage() {
        let mut ship = test_ship_with_armor(emissive: 10);
        ship.take_damage(50);
        assert_eq!(ship.current_hp, ship.max_hp - 40); // 50 - 10 armor
    }
}

// proptest for property-based testing
proptest! {
    #[test]
    fn damage_never_negative(damage in 0.0f64..1000.0, armor in 0.0f64..100.0) {
        let result = calculate_damage_after_armor(damage, armor);
        prop_assert!(result >= 0.0);
    }
}
```

---

## Effort Estimates

| Stage | Effort (Solo Dev) | Effort (Small Team) | Confidence |
|-------|-------------------|--------------------|-----------|
| Stage 1: Core | 2-4 weeks | 1-2 weeks | High |
| Stage 2: Simulation | 6-10 weeks | 3-5 weeks | Medium |
| Stage 3: Strategy | 4-6 weeks | 2-3 weeks | Medium |
| Stage 4: AI | 3-5 weeks | 2-3 weeks | Medium |
| Stage 5: UI | 8-14 weeks | 4-7 weeks | Low |
| Testing & Integration | 4-6 weeks | 2-3 weeks | Medium |
| Buffer (unforeseen) | 4-8 weeks | 2-4 weeks | - |
| **Total** | **31-53 weeks** | **16-27 weeks** | |
| | **~8-13 months** | **~4-7 months** | |

---

## Final Recommendations

### Do Migrate If:
- Performance for large battles is a priority
- You want cross-platform distribution (including WASM/web)
- You're comfortable with Rust's learning curve
- You're willing to accept a different (potentially better) UI toolkit
- The game's core mechanics are relatively stable (not rapidly changing)

### Don't Migrate If:
- Rapid feature iteration is the priority right now
- You're unfamiliar with Rust and unwilling to invest in learning
- The current Python performance is acceptable
- You need the game playable continuously during development

### Preparation Steps (Do Now):
1. **Add property-based tests** to formulas/damage/physics
2. **Create golden-file battle regression tests** with deterministic seeds
3. **Document the ability system contracts** as specifications
4. **Prototype one system in Rust** (hex math or damage calculator) to validate the approach
5. **Evaluate `bevy_egui`** with a small UI prototype before committing

### The Architecture is Ready
The most important finding: **this codebase is architecturally well-prepared for migration.** The strict DI (PROJ-50), clean layer separation, data-driven design, component/ability pattern, and comprehensive test suite are exactly the foundations needed. Many Python codebases would require significant refactoring before migration could even begin. Starship Battles is already there.

---

## Agent Reports

This analysis was compiled from 6 specialized exploration agents:

1. **Core Architecture Agent** - Mapped directory structure, layer dependencies, design patterns, state management, external dependencies, entry points
2. **Simulation Engine Agent** - Analyzed combat simulation, component/ability system, formulas, data-driven design, dynamic typing usage
3. **UI/Rendering Agent** - Examined UI structure, Pygame integration depth, input handling, animation, asset management, game state coupling
4. **Strategy/AI Agent** - Explored galaxy map, fleet management, AI decision-making, turn/order system, galaxy generation, save/load
5. **Test Suite Agent** - Analyzed test structure, coverage, patterns, simulation tests, test data, test dependencies
6. **Data Model Agent** - Investigated registry system, DI, JSON data files, validation, component definitions, serialization patterns
