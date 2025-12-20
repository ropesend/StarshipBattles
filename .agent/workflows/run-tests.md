---
description: run unit tests after code changes
---

# Run All Unit Tests

After making any code changes to the Starship Battles project, run the full test suite:

// turbo
1. Run all unit tests in the tests directory:
```powershell
python -m unittest discover -s tests -v
```

2. Verify all tests pass (should see "OK" at the end)

3. If any tests fail, fix the issues before proceeding

**Test coverage includes:**
- Component loading and creation
- Modifier stacking (multiplicative)  
- Ship physics and damage
- Weapons and firing arcs
- Sprite loading
- AI behavior
- Overlay rendering
