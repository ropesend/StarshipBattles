# Dead Code Validation Report

**Validation Date:** 2026-05-05
**Tooling:** vulture (static analysis) + manual grep verification across game/, tests/, docs/

## Summary
- **Total Candidates Reviewed:** 7
- **Confirmed Dead:** 0
- **Product Decision Required:** 0
- **False Positives:** 7

---

## Confirmed Dead Code

*None.* All 7 vulture candidates were verified as false positives. See below.

---

## False Positives

### 1. `exc_tb`, `exc_type`, `exc_val` — `battle_engine.py:98`
- **Candidate:** unused variable in `__exit__(self, exc_type, exc_val, exc_tb)`
- **Reason:** These are required parameters of the Python context manager `__exit__` protocol. The method body calls `self.close()` and returns `False`. The parameters are unused by design but their presence is mandated by the protocol signature. This is a **well-known vulture false positive** for `__exit__` context managers.

### 2. `IControllableShip` — `ai/controller.py:56` (90% confidence)
- **Candidate:** unused import `from game.simulation.interfaces.ai_controller import IControllableShip`
- **Reason:** The import is guarded by `if TYPE_CHECKING:` (line 54). The symbol is used as a forward-reference string annotation on line 86: `ship: 'IControllableShip'`. The import resolves the annotation for static type checkers (mypy, pyright) while avoiding circular imports at runtime. **Standard TYPE_CHECKING pattern — not dead.**

### 3. `RegionClassifier` — `strategy/data/galaxy.py:30` (90% confidence)
- **Candidate:** unused import `from game.strategy.generation.region_classifier import RegionClassifier`
- **Reason:** The import is guarded by `if TYPE_CHECKING:` (line 28). The symbol is used as a quoted type annotation on line 577: `region_classifier: 'Optional[RegionClassifier]' = None`. The module `region_classifier.py` itself (line 29) defines the class and is heavily tested (43 references in `tests/unit/strategy/generation/test_region_classifier.py`). **TYPE_CHECKING guard — not dead.**

### 4. `RegionClassifier` — `strategy/data/galaxy_warp_generator.py:15` (90% confidence)
- **Candidate:** unused import `from game.strategy.generation.region_classifier import RegionClassifier`
- **Reason:** The import is guarded by `if TYPE_CHECKING:` (line 13). The symbol is used in 6 quoted type annotations across the file (lines 192, 206, 278, 290, 316, 329) in function/method signatures. **TYPE_CHECKING guard — not dead.**

### 5. `BuildContext` — `ui/panels/build_queue_controller.py:18` (90% confidence)
- **Candidate:** unused import `from game.strategy.data.build_context import BuildContext`
- **Reason:** The file has `from __future__ import annotations` (line 10), making all annotations strings at runtime. The import is guarded by `if TYPE_CHECKING:` (line 17). The symbol is used on line 59: `build_context: Union['Planet', 'Fleet', 'BuildContext']`. The `BuildContext` Protocol class (defined in `strategy/data/build_context.py:11`) is tested for protocol compliance in `tests/unit/strategy/data/test_build_context.py` and documented in `docs/systems/strategy_layer.md`. **TYPE_CHECKING guard — not dead.**

---

## Vulture Assessment

**Vulture found 0 genuine dead code candidates across the entire production codebase.**

This is a strong positive signal about code quality. The codebase practices that prevent dead code accumulation:

1. **Consistent `TYPE_CHECKING` guards** for type-only imports — all 4 flagged imports follow this pattern correctly.
2. **TDD-driven development** ensures code is exercised by tests before it exists.
3. **Regular refactoring** (PROJ-63, PROJ-67, PROJ-69 visible in file headers) extracts and cleans up code.
4. **Strict LOC ceilings** (500 lines) force regular file splits, preventing bitrot.

The vulture pass returned only protocol-mandated `__exit__` params and TYPE_CHECKING import guards — both of which are standard Python patterns vulture cannot statically resolve. No actionable dead code was found.

---

## Verification Methodology

| Candidate | game/ grep | tests/ grep | docs/ grep | isinstance check? | Verdict |
|-----------|-----------|-------------|-----------|-------------------|---------|
| `exc_tb/exc_type/exc_val` | 1 match (definition) | — | — | N/A | False positive (`__exit__` protocol) |
| `IControllableShip` | 2 matches (import + annotation) | 0 | 0 | No | False positive (TYPE_CHECKING) |
| `RegionClassifier` (galaxy.py) | 11 matches (definition + annotations + docs) | 43 matches | 2 matches | No | False positive (TYPE_CHECKING) |
| `RegionClassifier` (galaxy_warp_gen.py) | 11 matches (same shared hits) | 43 matches | 2 matches | No | False positive (TYPE_CHECKING) |
| `BuildContext` | 9 matches (definition + annotations + docs) | 15 matches | 0 | No | False positive (TYPE_CHECKING + `__future__`) |
