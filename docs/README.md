# Starship Battles Documentation

## Quick Navigation

### I want to understand the codebase architecture
- [ARCHITECTURE.md](architecture/ARCHITECTURE.md) - Layer structure, dependencies, package APIs
- [PATTERNS.md](architecture/PATTERNS.md) - Design patterns (Singleton, MVVM, Event Bus, etc.)
- [SERVICES.md](architecture/SERVICES.md) - Service layer API reference (BattleService, VehicleDesignService, etc.)
- [NAMING_CONVENTIONS.md](architecture/NAMING_CONVENTIONS.md) - Naming patterns for classes, methods, files

### I want to add or modify game features
- [component_system.md](guides/component_system.md) - How the component/ability system works
- [modifier_system.md](guides/modifier_system.md) - How the modifier system works
- [adding_abilities.md](guides/adding_abilities.md) - Step-by-step: add a new component ability
- [adding_modifiers.md](guides/adding_modifiers.md) - Step-by-step: add a new modifier

### I want to write or understand tests
- [simulation_testing.md](guides/simulation_testing.md) - TestScenario pattern, test infrastructure, troubleshooting

### I want to understand specific systems
- [planetary_complex.md](systems/planetary_complex.md) - Planetary complex system design and implementation
- [planetary_complex_testing.md](systems/planetary_complex_testing.md) - Manual testing guide for planetary complexes

### I want to understand error handling or UI styling
- [ERROR_HANDLING.md](architecture/ERROR_HANDLING.md) - Quick reference (logging levels, exception hierarchy)
- [ERROR_HANDLING_GUIDELINES.md](architecture/ERROR_HANDLING_GUIDELINES.md) - Full guide with anti-patterns and decision trees
- [UI_STYLE_GUIDE.md](architecture/UI_STYLE_GUIDE.md) - Color palette, theme configuration, pygame_gui styling

### I want to understand past or planned refactoring
- [REMAINING_WORK.md](refactoring/REMAINING_WORK.md) - Current status of open work items
- [LARGE_FILE_SPLIT_PLAN.md](refactoring/LARGE_FILE_SPLIT_PLAN.md) - Analysis of files needing extraction
- [lessons_learned.md](refactoring/lessons_learned.md) - Bug fixes and prevention patterns
- [REFACTORING_COMPLETE.md](refactoring/completed/REFACTORING_COMPLETE.md) - Design Workshop refactoring summary
- [strategy_scene_split.md](refactoring/completed/strategy_scene_split.md) - Strategy scene extraction (template for future refactoring)
- [resource_system_refactor.md](architecture/resource_system_refactor.md) - Resource system refactoring (model documentation)

---

## Directory Structure

```
docs/
├── README.md                          <- You are here
├── architecture/                      # Codebase architecture and conventions
│   ├── ARCHITECTURE.md                  Layer structure, dependencies, APIs
│   ├── PATTERNS.md                      Design patterns (MVVM, Singleton, etc.)
│   ├── SERVICES.md                      Service layer API reference
│   ├── NAMING_CONVENTIONS.md            Naming conventions
│   ├── ERROR_HANDLING.md                Quick reference for error handling
│   ├── ERROR_HANDLING_GUIDELINES.md     Full error handling guide
│   ├── UI_STYLE_GUIDE.md               Color palette and theme config
│   └── resource_system_refactor.md      Resource system refactor (completed)
│
├── guides/                            # How-to guides for common tasks
│   ├── component_system.md              Component/ability system overview
│   ├── modifier_system.md               Modifier system overview
│   ├── adding_abilities.md              Add a new ability (step-by-step)
│   ├── adding_modifiers.md              Add a new modifier (step-by-step)
│   └── simulation_testing.md            Testing guide and troubleshooting
│
├── systems/                           # Feature-specific documentation
│   ├── planetary_complex.md             Planetary complex system
│   └── planetary_complex_testing.md     Manual testing checklist
│
└── refactoring/                       # Refactoring status and history
    ├── REMAINING_WORK.md                Current open work items
    ├── LARGE_FILE_SPLIT_PLAN.md         Future: large file extraction plan
    ├── lessons_learned.md               Bug fixes and prevention patterns
    └── completed/                       Archived completed projects
        ├── REFACTORING_COMPLETE.md        Design Workshop summary
        ├── strategy_scene_split.md        Strategy scene extraction
        ├── test_baseline.md               Pre-refactoring test baseline
        └── originals/                     Detailed phase reports
```

## For AI Agents: Recommended Reading Order

1. **Start**: [ARCHITECTURE.md](architecture/ARCHITECTURE.md) (10 min) - understand layer structure
2. **Conventions**: [NAMING_CONVENTIONS.md](architecture/NAMING_CONVENTIONS.md) (5 min) - naming patterns
3. **Based on task**:
   - Adding features: [component_system.md](guides/component_system.md) + [adding_abilities.md](guides/adding_abilities.md)
   - Working on services: [SERVICES.md](architecture/SERVICES.md)
   - Working on UI: [PATTERNS.md](architecture/PATTERNS.md) (MVVM section) + [UI_STYLE_GUIDE.md](architecture/UI_STYLE_GUIDE.md)
   - Writing tests: [simulation_testing.md](guides/simulation_testing.md)
   - Refactoring: [REMAINING_WORK.md](refactoring/REMAINING_WORK.md) + [strategy_scene_split.md](refactoring/completed/strategy_scene_split.md) (as template)
