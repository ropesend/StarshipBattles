# PROJ-181: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Delete deprecated functions entirely (not just deprecate) | CLAUDE.md System Migration Policy: "ERADICATE the old system completely" |
| 2026-02-24 | Full cleanup scope: includes test migration of 24 files | User chose "Full cleanup" option over minimal/phased scope |
| 2026-02-24 | Keep RegistryManager singleton access in tests where it reads data (not `.clear()`) | Out of scope - only `.clear()` boilerplate is targeted; RegistryManager removal is 180+ call sites |
| 2026-02-24 | Composition roots switch to direct RegistryManager usage (no deprecated setter) | DefaultRegistryProvider already wraps RegistryManager; setter was populating a parallel unused variable |
| 2026-02-24 | Phase ordering: delete API first, then migrate callers, then clean boilerplate, then docs | Ensures callers are identified by import errors; boilerplate cleanup is lower risk and can be batched |
| 2026-02-24 | Split .clear() migration into Batch 1 (already using fresh_registries) and Batch 2 (not using it) | Files already using fresh_registries are lowest risk; separating batches limits blast radius |
