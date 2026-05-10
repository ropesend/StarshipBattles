# PROJ-168: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-23 | Project initialized | Starting point for Extract Hex-to-Cartesian Conversion Helper |
| 2026-02-23 | Place function in `game/core/hex_math.py` | Pure geometry, existing hex module, callers already import from it |
| 2026-02-23 | Use `float` param types (not `int`) | Callers pass int, but float signature is more flexible and matches center params |
| 2026-02-23 | Include `center_q`/`center_r` in function signature | 4 of 5 callers compute dq/dr first — eliminates that boilerplate |
| 2026-02-23 | noise.py uses `-offset` as center (not separate function) | Mathematically equivalent; avoids a second function for one call site |
| 2026-02-23 | Skip Phase B swarm review | Small, well-understood scope — deep review already provided complete data |
| 2026-02-23 | Use `math.sqrt(3.0) / 2.0` (not hardcoded constant) | Readable, matches other `hex_math.py` functions; compiler optimizes constant |
