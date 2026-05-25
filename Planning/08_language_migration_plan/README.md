# Stage 8: Language Migration Plan

## Purpose

Plan a later migration of performance-critical or authority-critical systems to a faster language, probably Rust and possibly C++, after interfaces and gameplay rules stabilize.

This is intentionally late-stage planning. The near-term goal is to make the Python code easier to port, not to begin a full rewrite.

## Core Principle

Do not migrate unstable systems. First stabilize the boundaries, DTOs, command schemas, serialization, and tests. Then port isolated subsystems behind those boundaries.

## Preferred Direction

Rust should be the default candidate for the authoritative simulation/server core unless profiling, tooling, library needs, or engine integration point strongly toward C++.

C++ remains plausible for graphics/engine-heavy systems, but Rust is likely better for server-side correctness, concurrency, and long-term maintainability.

## Candidate Migration Areas

| Area | Why It Might Move |
|---|---|
| Tactical combat simulation | Potentially heavy per-tick simulation and many entities. |
| Turn processing | Large galaxies, many empires, many orders, parallel processing. |
| Visibility/fog resolver | Potentially frequent spatial scans over many objects. |
| Pathfinding | Many fleet route calculations and intercept projections. |
| AI planning/search | Potentially expensive scoring and simulation. |
| Server authority core | Security, determinism, concurrency, and deployment. |
| Serialization/validation core | Strong schemas and compatibility. |

## Migration Strategy

1. Keep Python as the fast iteration layer while rules are changing.
2. Define stable DTOs and schemas.
3. Add strong tests around subsystem behavior.
4. Profile before porting.
5. Port one pure subsystem at a time.
6. Keep Python UI/tools initially.
7. Use serialization or FFI boundaries that can be tested independently.
8. Avoid rewriting UI until there is a separate reason to do so.

## Rust Advantages

- Memory safety.
- Strong enums and pattern matching.
- Good serialization ecosystem.
- Good concurrency model.
- Good fit for server-authoritative simulation.
- Fewer accidental data races than C++.

## C++ Advantages

- Familiarity and existing experience.
- Mature game/graphics ecosystem.
- Easier integration with some native engine/tooling options.
- Potentially easier if a future custom engine becomes C++-centric.

## Initial Non-Goals

- Immediate rewrite.
- Porting UI.
- Porting systems without profiling.
- FFI before schemas are stable.
- Maintaining two complete game implementations.

## Design Questions

1. What performance targets should trigger migration?
2. Which subsystem should be the first port candidate?
3. Should the future core be a library loaded by Python, a separate server process, or both?
4. Should serialization be JSON for debugging first, then binary later?
5. Should deterministic simulation be mandatory before migration?
6. Should Rust be treated as default unless C++ has a specific advantage?
7. What tests are required before a subsystem can be ported?
8. How long should Python remain the UI and tooling layer?

## Acceptance Criteria

This stage is ready for implementation projects only when:

- Core gameplay interfaces are stable.
- Candidate subsystem has profiling evidence or a strong architecture reason to move.
- DTOs and serialization are documented.
- Tests are strong enough to prove parity between Python and the new implementation.
- The migration target language has been selected for that subsystem.

## Implementation Project Guidance

Use the existing `Projects/` system for implementation. Suggested future slices:

1. Profile candidate subsystem.
2. Freeze DTO/schema for that subsystem.
3. Add parity tests in Python.
4. Prototype Rust or C++ implementation behind the same boundary.
5. Compare output and performance.
6. Replace Python implementation only after parity is proven.
