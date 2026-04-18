# PROJ-255: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Extract-method refactor for AIController.update, not a full class decomposition | The method is ~84 lines with clear responsibility boundaries. Extract-method is sufficient and lower risk than introducing new classes. |
| 2026-04-06 | Type hints on 4 critical files only, not full codebase | Focused effort on the most coupled and performance-sensitive code. Full sweep would be a separate project. |
| 2026-04-06 | Phase 3 (flyweight) is conditional on memory profiling | PROJ-241 already decomposed Component. The deepcopy is intentional for isolation. Only optimize if measured pressure exists. |
