# God Class Decomposition Planning Review

## Metadata
- **Date:** 2026-02-23
- **Type:** Technical Debt Review (Focused)
- **Scope:** 16 god classes across UI, Strategy, Simulation, and Core layers
- **Agents Used:** 7 (Tier 1/2/3 Decomposition, Re-Offender, Dependency/Test Impact, Extraction Pattern, Growth Prevention)
- **Prior Art:** PROJ-86/87/88/89, Deliberate Design Debt Audit (2026-02-23)

## Executive Summary

- **Total files analyzed:** 16 (14,223 lines)
- **Verdict: DECOMPOSE:** 9 files
- **Verdict: ACCEPT:** 7 files (with monitoring thresholds)
- **Estimated reduction:** 14,223 → ~8,500 lines in main files (40% reduction)
- **Re-offender root cause:** Extraction without responsibility shift; UI layer left in main class while only data/logic layer extracted
- **Critical insight:** Extraction != Decomposition. Moving code to a file doesn't reduce responsibility. ViewModel/facade patterns that enforce architectural boundaries are required.
- **Key recommendation:** Adopt MVVM as mandatory pattern for UI screens >600 lines

---

## Verdicts Summary

| # | File | Lines | Verdict | Target | Pattern | Priority |
|---|------|-------|---------|--------|---------|----------|
| 1 | test_lab/screen.py | 1,906 | **DECOMPOSE** | ~700 | MVVM + Renderer | P1 - Critical |
| 2 | fleet_report_window.py | 1,108 | **DECOMPOSE** | ~450 | Component extraction | P2 |
| 3 | build_queue_screen.py | 1,084 | **DECOMPOSE** | ~450 | Factory + Renderer | P2 |
| 4 | builder/weapons_panel.py | 1,037 | **DECOMPOSE** | ~350 | Calculator + Renderer | P1 |
| 5 | formation_editor.py | 941 | **DECOMPOSE** (light) | ~550 | Toolbar builder only | P3 - Quick win |
| 6 | race_setup_screen.py | 946 | **ACCEPT** | — | Already decomposed (8 panels) | Monitor at 1000 |
| 7 | galaxy.py | 928 | **DECOMPOSE** | ~210 | GalaxyGenerator extraction | P2 |
| 8 | strategy_input_handler.py | 898 | **DECOMPOSE** | ~240 | FleetCommandRouter + ClickDispatcher | P2 |
| 9 | empire_build_queue_window.py | 863 | **DECOMPOSE** | ~450 | MVVM (RowViewModel) | P1 - Re-offender |
| 10 | strategy_screen.py | 823 | **DECOMPOSE** (light) | ~526 | BuildQueueManager + GameStateManager | P3 |
| 11 | ship.py | 810 | **ACCEPT** | — | Cohesive entity | Monitor at 850 |
| 12 | strategy_renderer.py | 764 | **ACCEPT** | — | Focused renderer | Monitor at 800 |
| 13 | component.py | 723 | **ACCEPT** | — | Already delegated internally | Monitor at 750 |
| 14 | app.py | 705 | **ACCEPT** | — | Appropriate composition root | Monitor at 800 |
| 15 | battle_state_viewer.py | 687 | **DECOMPOSE** | ~150 | JSON diff + tree renderer extraction | P1 - Quick win |
| 16 | battle_controller.py | 659 | **ACCEPT** | — | Well-delegated orchestrator | Monitor at 700 |

---

## RE-OFFENDER ROOT CAUSE ANALYSIS

### The Core Problem: "Extraction Without Responsibility Shift"

All 3 re-offenders share the same systemic failure: **the data/logic layer was extracted, but the UI layer remained in the main class.** When new features arrived, the UI code had nowhere to go except the main class.

### File 1: TestLabScreen (1,837 → 1,906, +69 lines)

**What was extracted (PROJ-86):** data_extractor, validation_manager, panel_manager, test_executor
**What grew back:** Event routing (+69 lines) — dialog events, panel events, scroll handling
**Root cause:** Event handling layer was never extracted. New UI features (battle state viewer, refined scroll) grew directly in screen because no InputHandler or EventRouter delegate existed.
**Prevention:** Extract a `TestLabEventRouter` that owns ALL event dispatch.

### File 2: BuildQueueScreen (1,185 → 1,079, only 9% reduction)

**Why reduction was so modest:** PROJ-86 extracted only utilities (formatters, helpers) not subsystems. The screen still owns panel creation (383 lines), refresh logic (192 lines), and event handling (114 lines).
**Root cause:** Extracted modules are scattered utilities, not cohesive subsystems. Main class still coordinates everything.
**Prevention:** Extract `BuildQueueUIController` that owns panel creation, state management, and refresh.

### File 3: EmpireBuildQueueWindow (698 → 863, +165 lines!)

**What was extracted (PROJ-89):** formatter, filter_manager
**What grew back:** Filter UI building (+195 lines), column management integration, data formatting wrappers
**Root cause:** FilterManager extracted only the DATA layer of filtering. The UI layer (filter buttons, toggle handlers, search entry) remained in window. New features (column toggles, search) landed in window.
**Prevention:** Extract `EmpireBuildQueueSidebar` that owns the ENTIRE sidebar (data + UI).

### Cross-Cutting Pattern: "Layered Extraction Trap"

```
BAD (what happened):    Extract data layer → UI layer stays → UI layer grows
GOOD (what works):      Extract complete subsystem → Main becomes pure dispatcher
```

**Evidence from successful decompositions:**
- StrategyScreen: Pure dispatcher (350 lines), 8 extracted modules — NO regrowth
- Fleet: Clear responsibility split — NO regrowth
- GameSession: Facade pattern enforced — NO regrowth

### Prevention Framework

1. **Extract by subsystem, not by category** — Don't extract "the formatter"; extract "the entire filtering subsystem including its UI"
2. **Main class must become a pure dispatcher** — If it still coordinates, it will accumulate
3. **ViewModel barrier for UI screens** — Forces state ownership into a separate object; screen can't accumulate "just one more field"
4. **Decomposition contracts** — Document which responsibilities belong where; enforce in code review

---

## DETAILED DECOMPOSITION PLANS

### Tier 1 Critical Files

#### 1. TestLabScreen (1,906 lines → ~700)

**Extraction Plan:**

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| TestLabRenderer | Renderer | 19 `_draw_*` methods | ~650 | 1 |
| TestLabInputHandler | Input handler | 12 click/hover handlers | ~280 | 2 |
| TestLabStateManager | State management | 8 selection/hover properties | ~50 | 3 |
| TestLabDialogManager | Dialog management | 5 dialog/popup handlers | ~60 | 4 |

**Risk:** MEDIUM — UI state management requires careful coordination
**Mitigation:** Create TestLabState value object passed between renderer and handler

#### 2. FleetReportWindow (1,108 lines → ~450)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| FleetReportSidebar | Component extraction | `_init_sidebar` (353 lines!) | ~380 | 1 |
| FleetListRenderer | Renderer | Visible rows, row data | ~160 | 2 |
| FleetImageCache | Cache | `_get_ship_image` | ~40 | 3 |
| FleetStatsSummary | Statistics | `_update_summary` (72 lines) | ~75 | 4 |

**Risk:** MEDIUM — `_init_sidebar` at 353 lines (CQ-004) is the priority extraction

#### 3. BuildQueueScreen (1,084 lines → ~450)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| BuildQueuePanelFactory | Factory | 6 `_create_*` methods | ~250 | 1 |
| BuildQueueRenderer | Renderer | `_refresh_items_list`, `_refresh_queue_display` | ~192 | 2 |
| BuildQueueInputHandler | Input handler | button/drag/keyboard handlers | ~99 | 3 |

**Risk:** MEDIUM-HIGH — Complex queue/controller orchestration with 12-param constructor (CQ-012)

#### 4. WeaponsReportPanel (1,037 lines → ~350)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| WeaponCalculator | Calculator | threshold ranges, points of interest, grouping | ~212 | 1 |
| WeaponBarRenderer | Renderer | bar drawing, direction indicators, scale markers | ~222 | 2 |
| WeaponTooltipRenderer | Tooltip | hover detection, tooltip drawing | ~117 | 3 |

**Risk:** MEDIUM — Calculations must match rendering coordinate system; data-driven approach mitigates

#### 5. FormationEditor (941 lines → ~550)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| FormationToolbarBuilder | Builder | `_create_ui` (147 lines) | ~180 | 1 |

**Risk:** LOW — Already well-decomposed (FormationRenderer, FormationInputHandler exist). Only toolbar builder needed.

### Tier 2 Major Files

#### 7. Galaxy (928 lines → ~210)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| GalaxyGenerator | Generator | 10 generation/warp methods | ~371 | 1 |
| GalaxySpatialIndex | Index | planet/zone spatial lookups | ~70 | 2 |
| GalaxyPlanetRegistry | Registry | planet lifecycle management | ~52 | 3 |

**Risk:** MEDIUM — 50 files depend on Galaxy. Keep facade API identical. Internal delegation only.

#### 8. StrategyInputHandler (898 lines → ~240)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| FleetCommandRouter | Router | fleet/superweapon/detail actions | ~125 | 1 |
| PlanetPickingSystem | Hit test | hit test + click resolution | ~136 | 2 |
| ClickDispatcher | Dispatcher | 13 mode-specific click handlers | ~330 | 3 |
| UIActionRouter | Router | zoom, screenshot, cycles | ~57 | 4 |

**Risk:** LOW-MEDIUM — Well-tested (3 dedicated test files, ~50-70 tests)

#### 9. EmpireBuildQueueWindow (863 lines → ~450) — RE-OFFENDER

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| EmpireBuildQueueSidebar | FULL subsystem | sidebar creation + toggle handlers | ~183 | 1 |
| BuildQueueSelection | State | select, toggle, get selected | ~59 | 2 |
| BuildQueueFilter | Logic | filter/sort/refresh | ~45 | 3 |
| BatchQueueOperations | Static | batch add logic | ~27 | 4 |

**Key:** Extract sidebar as COMPLETE subsystem (data + UI), not just data layer

#### 10. StrategyScreen (823 lines → ~526)

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| BuildQueueManager | Manager | 5 build queue lifecycle methods | ~188 | 1 |
| GameStateManager | Manager | turn processing, notifications | ~109 | 2 |

**Risk:** LOW — Already heavily decomposed with 8 extracted modules

### Tier 3 Borderline Files

#### 15. BattleStateViewer (687 lines → ~150) — DECOMPOSE

| Extract To | Pattern | Methods | Est. Lines | Priority |
|------------|---------|---------|------------|----------|
| `game/ui/utils/json_diff.py` | Utility | compute_json_diff, DiffResult | ~80 | 1 |
| `game/ui/renderer/json_tree_renderer.py` | Renderer | syntax highlighting, formatting | ~200 | 2 |
| `game/ui/widgets/scrollable_json_panel.py` | Widget | scroll, viewport, thumb dragging | ~300 | 3 |

**Risk:** LOW — Only 1 file depends on it. Reusable components. Quick win.

#### Files 6, 11-14, 16: ACCEPT with monitoring

| File | Lines | Justification | Ceiling |
|------|-------|---------------|---------|
| RaceSetupScreen | 946 | Already decomposed with 8 extracted panels + asset loader | 1000 |
| Ship | 810 | Cohesive entity, proper delegation to stats/physics/combat | 850 |
| StrategyRenderer | 764 | Focused renderer, inherent domain complexity | 800 |
| Component | 723 | Already delegates to 5 internal managers | 750 |
| app.py | 705 | Appropriate composition root (DD-005 precedent) | 800 |
| BattleController | 659 | Well-delegated to BattleModeHandler, BattleStateManager | 700 |

---

## DEPENDENCY & TEST IMPACT SUMMARY

### Extraction Risk Map

| Risk | Files | Reason |
|------|-------|--------|
| **EXTREME** | Ship (245 deps), Component (153 deps), Galaxy (50 deps) | Core domain; facade-only refactoring |
| **MEDIUM** | BuildQueueScreen (10 deps, 8 test files), StrategyScreen (8 deps, 7 test files), BattleController (16 deps, 8 test files) | Multiple dependents, extensive tests |
| **LOW** | BattleStateViewer (1 dep), WeaponsPanel (4 deps), FormationEditor (3 deps), EmpireBuildQueueWindow (2 deps), FleetReportWindow (3 deps) | Few dependents, isolated UI |

### Recommended Extraction Order (by safety)

1. **BattleStateViewer** — 1 dependent, 3 test files, completely self-contained
2. **FormationEditor** — 3 dependents, already well-decomposed, just toolbar builder
3. **WeaponsPanel** — 4 dependents, isolated UI panel, clean math/render split
4. **EmpireBuildQueueWindow** — 2 dependents, re-offender fix priority
5. **FleetReportWindow** — 3 dependents, good test isolation
6. **TestLabScreen** — 5 dependents, complex but partially extracted
7. **Galaxy** — 50 dependents, internal delegation only (facade preserved)
8. **StrategyInputHandler** — 6 dependents, well-tested
9. **BuildQueueScreen** — 10 dependents, extensive tests protect changes
10. **StrategyScreen** — 8 dependents, already heavily decomposed

---

## EXTRACTION PATTERN ANALYSIS

### Pattern Success Rates in This Codebase

| Pattern | Success Rate | Best For | Evidence |
|---------|-------------|----------|----------|
| **MVVM** | Excellent | UI screens with state | WorkshopScreen stable since PROJ-38 |
| **Facade/Delegate** | Good (when complete) | Domain objects, coordinators | StrategyScreen, Fleet, GameSession all stable |
| **Renderer Extraction** | Moderate | Screens with heavy drawing | StrategyRenderer stable but grew to 764 lines |
| **Input Handler** | Good | Complex event handling | FormationInputHandler, StrategyInputHandler stable |
| **Manager/Controller** | Moderate | Business logic | Works but prone to scope creep |
| **Utility Extraction** | Poor (alone) | Simple helpers | Insufficient on its own (re-offender pattern) |

### Critical Anti-Patterns

1. **Extract Without Discipline:** Moving code to file without eliminating main class need to coordinate it
2. **Bidirectional Coupling:** Renderer knows about main, main queries renderer → both grow
3. **Helper Class Regrowth:** Extracted helper accumulates unrelated logic over time
4. **Fake Modularity:** Many small files that still tightly depend on main class
5. **Over-Extraction of Domain Objects:** Breaking cohesive entities like Ship/Component creates fragmentation

### Recommended Pattern Per File

| File | Pattern | Rationale |
|------|---------|-----------|
| TestLabScreen | MVVM | Must shift state ownership out of screen |
| FleetReportWindow | Component extraction | Already uses ViewModel; extract sidebar subsystem |
| BuildQueueScreen | Factory + Renderer | Panel creation is mechanical; rendering is separable |
| WeaponsPanel | Calculator + Renderer | Clean math/rendering split |
| FormationEditor | Builder (light) | Already well-decomposed; just toolbar |
| Galaxy | Facade/Delegate (internal) | Keep API; delegate to generator/index/registry |
| StrategyInputHandler | Router composition | Multiple distinct routing responsibilities |
| EmpireBuildQueueWindow | MVVM | Re-offender needs architectural barrier |
| StrategyScreen | Manager extraction | Already mostly decomposed; extract remaining managers |
| BattleStateViewer | Component extraction | 3 reusable components (diff, renderer, scroll) |

---

## GROWTH PREVENTION RECOMMENDATIONS

### Tier 1: Implement Immediately

#### 1. Line Count CI Check (600 lines)
- **Tool:** flake8 with flake8-length plugin
- **Threshold:** 600 lines (700 for UI screens with ViewModel)
- **Enforcement:** Hard fail for new violations; allowlist for existing files pending decomposition
- **Effort:** 2 hours

#### 2. Decomposition Contract Template
- **What:** After each extraction, document responsibility boundaries, ceiling line counts, and feature placement rules
- **Why:** EmpireBuildQueueWindow grew back because no one documented "new column features go in Formatter"
- **Template location:** `Projects/templates/decomposition_contract.md`
- **Effort:** 1 hour

#### 3. Line Count Tracking Script
- **What:** `Projects/scripts/report_line_counts.py` — reports files >500 lines, tracks decomposition baselines
- **When:** Pre-commit hook (warning only) + CI reporting
- **Effort:** 3 hours

### Tier 2: Implement After Decomposition

#### 4. Method Count Check (>35 per class)
#### 5. Cyclomatic Complexity (>10 per function via radon)
#### 6. Import Count Warning (>20 imports)
#### 7. Constructor Parameter Limit (>8 params)

### Tier 3: Long-Term

#### 8. Monthly Decomposition Health Dashboard
- Track all previously-decomposed files
- Alert on >10% growth from baseline
- Auto-create PROJ if regrowth detected twice

### Recommended Complexity Thresholds

| Metric | Threshold | Tool | Enforcement |
|--------|-----------|------|-------------|
| Lines per file | 600 | flake8-length | Hard fail |
| Methods per class | 35 | custom script | Warning |
| Cyclomatic complexity | 10 | radon | Warning |
| Nesting depth | 4 | custom script | Warning |
| Import count | 20 | custom script | Warning |
| Constructor params | 8 | custom script | Warning |

---

## PHASED EXECUTION PLAN

### Phase 1: Quick Wins + Re-Offender Fixes (Weeks 1-2)
**Goal:** Establish patterns, fix worst offenders, build confidence

| Order | File | Action | Est. Effort |
|-------|------|--------|-------------|
| 1 | BattleStateViewer | Extract json_diff, json_tree_renderer, scrollable_panel | 1 day |
| 2 | FormationEditor | Extract FormationToolbarBuilder | 0.5 days |
| 3 | EmpireBuildQueueWindow | Extract EmpireBuildQueueSidebar (complete subsystem) | 2 days |
| 4 | WeaponsPanel | Extract WeaponCalculator + WeaponBarRenderer | 2 days |

### Phase 2: Core Decomposition (Weeks 3-5)
**Goal:** Address Tier 1 critical files and Galaxy

| Order | File | Action | Est. Effort |
|-------|------|--------|-------------|
| 5 | FleetReportWindow | Extract FleetReportSidebar + FleetListRenderer | 3 days |
| 6 | Galaxy | Extract GalaxyGenerator + GalaxySpatialIndex | 3 days |
| 7 | TestLabScreen | MVVM: TestLabRenderer + TestLabInputHandler + TestLabStateManager | 5 days |
| 8 | BuildQueueScreen | Extract BuildQueuePanelFactory + BuildQueueRenderer | 3 days |

### Phase 3: Polish + Strategy Cluster (Weeks 6-7)
**Goal:** Complete remaining decompositions

| Order | File | Action | Est. Effort |
|-------|------|--------|-------------|
| 9 | StrategyInputHandler | Extract FleetCommandRouter + PlanetPickingSystem + ClickDispatcher | 3 days |
| 10 | StrategyScreen | Extract BuildQueueManager + GameStateManager | 2 days |

### Phase 4: Guardrails + Documentation (Week 8)
- Implement flake8-length CI check
- Write decomposition contracts for all extracted files
- Create line count tracking script
- Document patterns in architecture guide
- Set monitoring thresholds for all ACCEPT files

### Total Estimated Effort: ~25-30 working days across 8 weeks

---

## ACCEPT File Monitoring Schedule

| File | Lines | Ceiling | Check Frequency | Action if Exceeded |
|------|-------|---------|-----------------|-------------------|
| RaceSetupScreen | 946 | 1000 | Quarterly | Extract ShipPreviewRenderer |
| Ship | 810 | 850 | Quarterly | Internal refactoring only |
| StrategyRenderer | 764 | 800 | Quarterly | Split rendering sections |
| Component | 723 | 750 | Quarterly | Internal refactoring only |
| app.py | 705 | 800 | Quarterly | Extract SceneFactory |
| BattleController | 659 | 700 | Quarterly | Extract BattleSetup/BattlePersistence |

---

## Agent Reports

Individual agent findings are captured in this compiled report. The 7 agents analyzed:
1. **Tier 1 Decomposition Analyst** — Deep analysis of 5 critical files (>1000 lines)
2. **Tier 2 Decomposition Analyst** — Deep analysis of 5 major files (800-999 lines)
3. **Tier 3 Decomposition Analyst** — Accept/decompose verdicts for 6 borderline files
4. **Re-Offender Analyst** — Root cause analysis of 3 files that grew back
5. **Dependency & Test Impact Analyst** — Cross-cutting dependency and test coverage analysis
6. **Extraction Pattern Analyst** — Pattern success/failure assessment, phasing recommendations
7. **Growth Prevention Strategist** — CI guardrails, complexity metrics, monitoring plan
