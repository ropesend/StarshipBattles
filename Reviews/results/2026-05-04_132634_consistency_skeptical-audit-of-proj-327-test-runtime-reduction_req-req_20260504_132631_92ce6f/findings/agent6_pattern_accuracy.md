# Pattern Accuracy & Claims Audit — PROJ-327

**Audit type:** Skeptical consistency audit  
**Auditor:** OpenCode (agent 6)  
**Date:** 2026-05-04  
**Scope:** `docs/02_PATTERNS.md` §32, `PROJ-327/decisions.md` lessons-learned scorecard, anti-pattern claims, `docs/known-issues.md` PROJ-327 section.

---

## 1. Pattern Doc Accuracy (§32 "Compositional Construction")

### 1.1 Does the pattern accurately describe `strategy_screen_composition.py`?

**Yes**, mostly. The protocol has exactly 8 `make_*` methods (`strategy_screen_composition.py:56-74`), the factory has 8 corresponding implementations (`strategy_screen_composition.py:85-111`), and `StrategyScreen.__init__` calls them via `comp.make_*()` (`strategy_screen.py:147-155`). The description is mechanically accurate.

**One discrepancy:** The pattern doc says the `Composition` Protocol of `make_<thing>(self, screen)` methods has `screen` as second arg, and the code example shows `comp.make_renderer(self)` (passing screen as self). The actual code has `comp.make_renderer(self)` at `strategy_screen.py:148`, which matches. Accurate.

### 1.2 Does the pattern claim this is reusable or bespoke?

The pattern **claims reusability**:

> **"Same shape across the codebase.** PROJ-325 RaceSetup, PROJ-322 widget factory, and PROJ-327 StrategyScreen all use one Protocol + one default factory + one mock." (§32 "Why", `02_PATTERNS.md:1726`)

**This claim is overstated.** The three cited instances are different shapes:

| Instance | Shape |
|---|---|
| PROJ-327 StrategyScreen | Protocol with 8 `make_*` methods, one factory, one mock composition |
| PROJ-325 RaceSetup delegates | `DefaultRaceSetupDelegateFactory.build(screen) -> RaceSetupDelegates` — a single factory method returning a composite, not a per-slot protocol |
| PROJ-322 widget factory | `make_ui_widget(cls, ...)` — a parameterized generic factory, not a per-class protocol+fingerprint shape |

These share a vague "factory + mock" family resemblance but are NOT the same shape. Calling them "identical" is misleading.

Furthermore, the pattern has **no generic infrastructure** — no abstract base class, no reusable factory base, no composition registry. A developer adopting this pattern for a new class must write an entirely new Protocol + factory + mock from scratch. The pattern is a **convention**, not a reusable abstraction.

### 1.3 Is the "When to Use" guidance actionable?

**Partially.** The criteria are:

1. *"N (≥3) collaborator sub-objects in `__init__` whose own constructors are heavy"* — actionable threshold.
2. *"The collaborators have stable, easily-named roles"* — vague. Most sub-objects have roles; the guidance doesn't help distinguish when to use this vs. dependency injection.
3. *"Preferred over `bypass_init` + manual attribute population for new code"* — **misleading in practice**, because the migrated tests STILL use `__new__` bypass + manual attribute population for the upstream construction (Camera, StrategyUI, asset loading). The composition seam only covers 8 sub-object slots, not the full `__init__`. The pattern doc itself admits this: *"The StrategyScreen upstream construction (Camera, StrategyUI, asset loading) still runs inline — only the 8 sub-object slots are behind the composition seam."* (§32 "Migration notes", `02_PATTERNS.md:1730`)

A developer reading §32 as standalone guidance would think they can avoid bypass-init entirely. They cannot. The pattern is a **partial** seam, and the doc's migration notes are the only place this is clarified.

### 1.4 Is the pattern genuinely reusable?

**No.** It is a bespoke `StrategyScreen` factory convention dressed as a canonical pattern. There is no generic infrastructure to reuse. Each adoption requires writing from scratch:

- A new Protocol with N `make_*` methods
- A new production factory with N constructor calls
- A new mock factory with N MagicMock slots + `populate()` wiring

The one genuinely reusable element — the idea of "Protocol + factory + mock" — is already Pattern #15 (Factory). What §32 adds is the specific naming convention (`make_<thing>`) and the `populate()` helper for bypass-init paths. These are conventions, not a pattern distinct from Factory.

**Verdict: Pattern §32 is a naming convention, not a reusable pattern. It should be merged into §15 (Factory) or reduced to a convention note under §33 (UI Widget Test Factory), not promoted as a standalone canonical pattern.**

---

## 2. Lessons Learned Scorecard Accuracy

### 2.1 The "Highest tech-debt-per-LOC win" label

`decisions.md:32` rates Compositional Construction as:

> **"Highest tech-debt-per-LOC win."** Eliminates the brittle `patch.object(..., '__init__', lambda...)` pattern wholesale.

The scorecard's own columns are: **Wall-clock delta**, **LOC touched**, **Risk**, **Rework**, **Verdict**. By the table's own metrics:

| Technique | Wall-clock delta | LOC touched | Implied ms/LOC |
|---|---|---|---|
| `@patch` sweep | **-3.9 s** | ~700 | **5.6 ms/LOC reclaimed** |
| Compositional Construction | **~no measurable change** | ~+381 LOC added | **0 ms/LOC** |

If "per LOC" is the frame, Compositional Construction is the **worst** ROI by the table's own metric (0 ms runtime improvement per LOC). The "Highest tech-debt-per-LOC win" verdict **switches metric domains mid-table** — from runtime (the column's unit) to tech-debt (a qualitative concept). This is inconsistent and misleading to a reader scanning the Verdict column.

Additionally, the LOC count is **misleading as framed**: the `@patch` sweep "touched" ~700 LOC (removing decorators), while Compositional Construction **added** ~381 LOC (new files + fixture + smoke tests). Counting removals vs. additions as "LOC touched" in the same column conflates opposite directions of code change.

**Verdict: The "Highest tech-debt-per-LOC win" label compares apples to oranges. A reader expecting the Verdict column to summarize runtime ROI (as every other row does) is misled. If the scorecard wants to claim a tech-debt win, it should either: add a separate column for code-quality impact, or use consistent language ("Highest code-quality win; runtime-neutral") that doesn't imply a superlative on the same axis as the `@patch` sweep's 3.9s reclaim.**

### 2.2 Internal consistency

The `bypass_init` flag row ("Necessary but not sufficient") is internally consistent with its measurement (0s delta, 1 line per class). No issue.

The Phase 2 mutable-mock row ("Worth it when audit confirms no mutation") is consistent with its measurement. No issue.

### 2.3 "Bimodal runtime" insight

`decisions.md:36-43` correctly identifies that the ~5-8s "many small tests" cluster is an order of magnitude smaller than the "few heavy tests" cluster. This is well-stated and useful. The 90s target was never reachable from the deferral list alone — the doc is honest about this.

---

## 3. Anti-Pattern Claim Evaluation

### 3.1 The claim

`decisions.md:55`:

> The `patch.object(Cls, '__init__', lambda *args, **kwargs: None)` monkey-patch (used in `test_strategy_screen.py` pre-Phase-4) is **strictly worse than `__new__` bypass-init**: it leaks across tests in the same module if the patch is module-scoped, and it papers over real `__init__` bugs because the test never runs the real constructor.

### 3.2 Cross-test leaking (claim a)

**VALID.** A module-scoped `patch.object(Cls, '__init__', ...)` persists across all tests in the module, which can silently corrupt neighboring tests. `__new__` + manual attribute wiring does not have this problem because it's per-call, not module-scoped. This is a genuine advantage of the `__new__` approach.

### 3.3 Papers over `__init__` bugs (claim b)

**OVERSTATED.** The migrated tests (`test_strategy_screen.py:37`) STILL use `StrategyScreen.__new__(StrategyScreen)` — they do not run the real constructor. The `populate()` method (`strategy_screen_composition.py:102-116`) sets private attributes directly (`screen._renderer = self.renderer`), which is the **same** bypass-init manual wiring pattern.

Both approaches share this fragility:
- `patch.object(__init__, lambda ...)` → never runs `__init__`
- `__new__` + `populate()` → never runs `__init__` either

The composition pattern COULD run real `__init__` by passing `MockStrategyScreenComposition()` as a kwarg — but the migrated tests don't do this because the upstream construction (Camera, StrategyUI, asset loading) is too heavy. The doc admits this: *"Tests can either: pass the composition through a real StrategyScreen(...) call — Currently impractical"* (`strategy_screen_composition.py:18`).

**Thus: far from eliminating the "papers over real `__init__` bugs" problem, the Phase 4 migration preserved it. The composition seam exists in production code but is unused in the bypass-init test path.**

### 3.4 Are they equivalently fragile?

| Dimension | `patch.object(__init__, lambda..)` | `__new__` + `populate()` |
|---|---|---|
| Cross-test leak risk | Higher (module-scoped) | Lower (per-call) |
| Masks `__init__` bugs | Yes | Yes — no change |
| Manual wiring surface | 8 inline MagicMock assignments per test helper | 8 `populate()` assignments, centralized |
| Adding a 9th sub-object | Edit 50+ tests | Edit 1 method in `MockStrategyScreenComposition` |

The `__new__` approach is **better for maintainability** (centralized wiring) and **better for isolation** (no cross-test leak), but **equivalently fragile for init-bug detection**. "Strictly worse" overstates the comparison — "Worse for cross-isolation; equivalent for init-bug masking; better maintainability" is more accurate.

### 3.5 Verdict

The anti-pattern claim is **valid but overstated**. Cross-test leaking is a real concern that `__new__` avoids. But the claimed advantage on init-bug detection is not realized in the migrated tests — they still bypass `__init__` entirely. The Phase 4 migration swapped one bypass-init pattern for another, with the genuine improvement being **centralization** (single edit point for slot changes), not elimination of the bypass-init fragility.

---

## 4. Known-Issues Doc Accuracy

### 4.1 Does it accurately reflect outcomes?

**Yes.** `docs/known-issues.md:128` states:

- Reclaim: **-3.9 s median** (127.8 → 123.9), documented with the reference to `runtime_delta.md`
- **"The 90 s stretch target was NOT hit; ~34 s of gap remains"** — explicit and honest
- Correctly identifies the remaining runtime as integration tests + `test_component_definitions.py` + `test_game_instantiation`
- Correctly states the primary deliverable was disposition + rationale, not raw runtime

This is an honest characterization.

### 4.2 One issue: category confusion

`known-issues.md:130-135` lists Compositional Construction under **"Techniques that yielded measurable wall-clock wins"**, but then immediately says **"~no measurable runtime change"**. A technique with no measurable runtime change does not belong under "measurable wall-clock wins." This is confusing to a reader scanning section headers.

**Recommendation:** Move Compositional Construction to a separate sub-section: **"Techniques that improved code quality without runtime impact"** or rename the existing section to **"Techniques applied and their outcomes."**

### 4.3 Verdict

The known-issues PROJ-327 section is **honest about the failure to hit the 90s target**, honest about the reclaim magnitude, and correctly identifies where the remaining runtime lives. The one issue is a section-header misplacement (technique with no runtime change listed under "measurable wall-clock wins"), which is a presentation problem, not a factual error.

---

## Summary of Flagged Issues

| # | Location | Issue | Severity |
|---|---|---|---|
| 1 | `02_PATTERNS.md:1726` | "Same shape across the codebase" — three cited instances are different shapes; overstated | Medium |
| 2 | `02_PATTERNS.md` §32 | Pattern §32 is a naming convention, not a reusable pattern. No generic infrastructure exists. Should be merged into §15 or downgraded to convention note. | High |
| 3 | `decisions.md:32` | "Highest tech-debt-per-LOC win" compares apples to oranges — switches from runtime metric (column unit) to code-quality metric mid-table | Medium |
| 4 | `decisions.md:32` LOC column | LOC "touched" conflates removals (`@patch` sweep, -700) with additions (Compositional Construction, +381) | Low |
| 5 | `decisions.md:55` | "Strictly worse than `__new__` bypass-init" — overstated for init-bug detection claim, since migrated tests still bypass `__init__` | Medium |
| 6 | `known-issues.md:130-135` | Compositional Construction listed under "measurable wall-clock wins" despite "~no measurable runtime change" | Low |

**Overall assessment:** The documentation is largely honest about PROJ-327's outcomes and runtime limitations. The primary issues are overstatement of Pattern #32's reusability and the scorecard's metric-domain confusion between runtime ROI and code-quality impact. The anti-pattern claim is directionally correct but overstates the init-bug-detection advantage.
