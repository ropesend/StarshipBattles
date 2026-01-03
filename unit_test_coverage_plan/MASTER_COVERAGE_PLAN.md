# Master Test Coverage Plan

## Executive Summary
This document consolidates findings from the comprehensive **Unit Test Coverage Audit** conducted in January 2026. The goal is to achieve 100% line and branch coverage across the Starship Battles V2 codebase.

**Overall System Health:**
*   **Refactored Core:** ✅ High Confidence. The Ability System transition is well-tested.
*   **Validation & Safety:** ⚠️ Moderate Confidence. Core logic is verified, but UI-layer validation and complex rule interactions have gaps.
*   **Edge Case Resilience:** ❌ Needs Improvement. File I/O failure modes, AI edge conditions (zero-targets), and deep UI state synchronization need dedicated tests.

## Domain Audit Summaries

| Domain | Files | Coverage Status | Report Link |
| :--- | :--- | :--- | :--- |
| **1. Core Architecture** | `components.py`, `abilities.py`, `ship.py` | **85-95%** | [View Report](coverage_report_core.md) |
| **2. Simulation Engine** | `ship_physics.py`, `ship_combat.py`, `collision.py` | **80%** | [View Report](coverage_report_simulation.md) |
| **3. AI & Behaviors** | `ai.py`, `ai_behaviors.py` | **60-70%** | [View Report](coverage_report_ai.md) |
| **4. UI & Builder** | `builder_gui.py`, `ui/builder/*.py` | **~70%** | [View Report](coverage_report_ui.md) |
| **5. Data & Infrastructure** | `ship_io.py`, `ship_validator.py` | **~25%** | [View Report](coverage_report_data.md) |

## Implementation Roadmap

The following 3-Phase Plan is recommended to reach 100% coverage efficiently.

### Phase 1: High-Risk Stability Gaps (Immediate Priority)
Targeting areas that cause crashes or data corruption.
1.  **Data Persistence (`ship_io.py`)**: Implement `unit_tests/test_io_interactive.py` to handle save/load errors gracefully.
2.  **Validation Logic (`ship_validator.py`)**: Extend `test_builder_validation.py` to cover `ClassRequirements` and `ResourceDependencies`.
3.  **UI Feedback (`builder_gui.py`)**: Implement tests for I/O error message display in the GUI.

### Phase 2: Logic & Behavior Verification (Medium Priority)
Targeting areas that cause incorrect gameplay or "glitchy" behavior.
1.  **AI Edge Cases (`ai.py`)**: Add tests for AI behavior with 0 targets, 0 speed, or immobilized states.
2.  **Combat Mechanics (`ship_combat.py`)**: Verify precise damage calculation flows and ability interactions.
3.  **Physics (`ship_physics.py`)**: Verify thrust vectoring with `CombatPropulsion` and `ManeuveringThruster` combinations.

### Phase 3: UI Polish & Legacy Cleanup (Low Priority)
Targeting visual correctness and code hygiene.
1.  **Complex Rendering (`detail_panel.py`)**: Verify HTML generation for component stats.
2.  **Layer Panel Sync (`layer_panel.py`)**: Verify reconciliation logic when lists change.
3.  **Visual Feedback (`rendering.py`)**: Verify correct color coding for different component abilities.

## Next Steps
Select **Phase 1: High-Risk Stability Gaps** to begin implementation.
