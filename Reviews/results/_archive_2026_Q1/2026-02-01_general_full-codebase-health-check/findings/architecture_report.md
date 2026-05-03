### Summary
- Total issues found: 2
- Critical: 0, Major: 1, Minor: 1, Info: 0

### Findings

#### MAJOR: UI/Simulation Coupling
**ID:** AR-01
**Location:** `game/ui/` -> `game/simulation/`
**Issue:** Heavy coupling between UI screens and Simulation internals (e.g. `BattleController`).
**Impact:** Makes it hard to run simulation headless (for testing or server).
**Recommendation:** Introduce a stricter Event Bus or ViewModel layer between UI and Sim.
**Effort:** Complex

#### MINOR: God Object Config
**ID:** AR-02
**Location:** `game/app.py`
**Issue:** `app.py` often becomes a dumping ground for initialization logic.
**Impact:** Startup logic is brittle.
**Recommendation:** Extract `AppConfig` and `ServiceLocator` patterns.
**Effort:** Medium

### Top 5 Priority Issues
1. Decouple UI from Simulation (AR-01)
