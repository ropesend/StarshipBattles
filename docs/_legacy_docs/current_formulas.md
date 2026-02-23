# Current Modifier Formulas Documentation

> **Generated**: 2026-01-19
> **Purpose**: Document all current modifier handler formulas before refactoring

This document captures the exact mathematical formulas used by each modifier handler in `modifiers.py`. These formulas must be preserved exactly during the migration to JSON-based formulas.

---

## 1. hardened_mount

**Purpose**: Increases HP as the square of mass multiplier.

**Parameters**:
- `val`: Mass multiplier (1.0 to 10.0)

**Formulas**:
```
mass_mult *= val
hp_mult *= val ^ 2
cost_mult *= val
```

**Examples**:
| val | mass_mult | hp_mult | cost_mult |
|-----|-----------|---------|-----------|
| 1.0 | 1.0 | 1.0 | 1.0 |
| 2.0 | 2.0 | 4.0 | 2.0 |
| 3.0 | 3.0 | 9.0 | 3.0 |
| 5.0 | 5.0 | 25.0 | 5.0 |

---

## 2. range_mount

**Purpose**: Doubles range per level, with 3.5x mass/HP/cost per doubling.

**Parameters**:
- `val`: Level (0 to 3)

**Formulas**:
```
range_mult *= 2.0 ^ val
mass_mult *= 3.5 ^ val
hp_mult *= 3.5 ^ val
cost_mult *= 3.5 ^ val
```

**Examples**:
| level | range_mult | mass_mult | hp_mult | cost_mult |
|-------|------------|-----------|---------|-----------|
| 0 | 1.0 | 1.0 | 1.0 | 1.0 |
| 1 | 2.0 | 3.5 | 3.5 | 3.5 |
| 2 | 4.0 | 12.25 | 12.25 | 12.25 |
| 3 | 8.0 | 42.875 | 42.875 | 42.875 |

---

## 3. turret_mount

**Purpose**: Adds firing arc with logarithmic mass scaling.

**Parameters**:
- `val`: Arc in degrees (0 to 180)

**Formulas**:
```
if val > 0:
    mass_mult *= 1.0 + 0.514 * ln(1.0 + val / 30.0)
    arc_set = val
```

**Examples**:
| arc | mass_mult |
|-----|-----------|
| 0 | 1.0 |
| 30 | ~1.357 |
| 45 | ~1.454 |
| 90 | ~1.676 |
| 180 | ~1.943 |

---

## 4. rapid_fire

**Purpose**: Increases fire rate (reduces reload time) with linear mass scaling.

**Parameters**:
- `val`: Fire rate multiplier (1.0 to 10.0)

**Formulas**:
```
reload_mult *= 1.0 / val
mass_mult += (val - 1.0) * 2.0
cost_mult *= val ^ 0.5
```

**Note**: mass_mult uses ADDITIVE scaling, not multiplicative!

**Examples**:
| rate | reload_mult | mass_mult (additive) | cost_mult |
|------|-------------|---------------------|-----------|
| 1.0 | 1.0 | +0.0 | 1.0 |
| 2.0 | 0.5 | +2.0 | ~1.414 |
| 3.0 | ~0.333 | +4.0 | ~1.732 |
| 5.0 | 0.2 | +8.0 | ~2.236 |

---

## 5. precision_mount

**Purpose**: Increases beam weapon accuracy with mass penalty.

**Parameters**:
- `val`: Level (0 to 5)

**Formulas**:
```
accuracy_add += val * 0.5
mass_mult *= 1.0 + (val * 0.5)
cost_mult *= 1.5 ^ val
```

**Examples**:
| level | accuracy_add | mass_mult | cost_mult |
|-------|--------------|-----------|-----------|
| 0 | +0.0 | 1.0 | 1.0 |
| 1 | +0.5 | 1.5 | 1.5 |
| 2 | +1.0 | 2.0 | 2.25 |
| 3 | +1.5 | 2.5 | 3.375 |
| 5 | +2.5 | 3.5 | 7.594 |

---

## 6. simple_size

**Purpose**: Uniform scaling of all stats.

**Parameters**:
- `val`: Scale multiplier (1 to 1024)

**Formulas**:
```
mass_mult *= val
hp_mult *= val
damage_mult *= val
cost_mult *= val
thrust_mult *= val
turn_mult *= val
strategic_mult *= val
energy_gen_mult *= val
capacity_mult *= val
crew_capacity_mult *= val
life_support_capacity_mult *= val
consumption_mult *= val
```

---

## 7. seeker_endurance

**Purpose**: Increases seeker range/endurance.

**Parameters**:
- `val`: Multiplier (1.0 to 10.0)

**Formulas**:
```
endurance_mult *= val
mass_mult *= 1.0 + (val - 1.0) * 0.5
cost_mult *= val
```

**Examples**:
| mult | endurance_mult | mass_mult | cost_mult |
|------|----------------|-----------|-----------|
| 1.0 | 1.0 | 1.0 | 1.0 |
| 2.0 | 2.0 | 1.5 | 2.0 |
| 5.0 | 5.0 | 3.0 | 5.0 |
| 10.0 | 10.0 | 5.5 | 10.0 |

---

## 8. seeker_damage

**Purpose**: Increases seeker warhead damage.

**Parameters**:
- `val`: Multiplier (1.0 to 1000.0)

**Formulas**:
```
projectile_damage_mult *= val
mass_mult *= 1.0 + (val - 1.0) * 0.75
cost_mult *= val ^ 0.5
```

**Examples**:
| mult | projectile_damage_mult | mass_mult | cost_mult |
|------|------------------------|-----------|-----------|
| 1.0 | 1.0 | 1.0 | 1.0 |
| 2.0 | 2.0 | 1.75 | ~1.414 |
| 10.0 | 10.0 | 7.75 | ~3.162 |
| 100.0 | 100.0 | 75.25 | 10.0 |

---

## 9. seeker_armored

**Purpose**: Increases seeker HP (survivability).

**Parameters**:
- `val`: Multiplier (1.0 to 1000.0)

**Formulas**:
```
projectile_hp_mult *= val
mass_mult *= 1.0 + (val - 1.0) * 0.75
cost_mult *= val ^ 0.5
```

**Note**: Same mass formula as seeker_damage.

---

## 10. seeker_stealth

**Purpose**: Makes seeker harder to hit by PDC.

**Parameters**:
- `val`: Stealth level (0 to 10)

**Formulas**:
```
projectile_stealth_level += val
mass_mult *= 1.0 + val * 2.0
cost_mult *= 2.0 ^ val
```

**Examples**:
| level | stealth_level | mass_mult | cost_mult |
|-------|---------------|-----------|-----------|
| 0 | 0 | 1.0 | 1.0 |
| 1 | 1 | 3.0 | 2.0 |
| 3 | 3 | 7.0 | 8.0 |
| 5 | 5 | 11.0 | 32.0 |
| 10 | 10 | 21.0 | 1024.0 |

---

## 11. automation

**Purpose**: Reduces crew requirement with mass penalty.

**Parameters**:
- `val`: Reduction percentage (0.0 to 0.99)

**Formulas**:
```
crew_req_mult *= (1.0 - val)
mass_mult *= (1.0 + val)
cost_mult *= (1.0 + val)
```

**Examples**:
| reduction | crew_req_mult | mass_mult | cost_mult |
|-----------|---------------|-----------|-----------|
| 0.0 | 1.0 | 1.0 | 1.0 |
| 0.25 | 0.75 | 1.25 | 1.25 |
| 0.5 | 0.5 | 1.5 | 1.5 |
| 0.75 | 0.25 | 1.75 | 1.75 |
| 0.99 | 0.01 | 1.99 | 1.99 |

---

## 12. efficiency_mount

**Purpose**: Reduces resource consumption with exponential mass cost.

**Parameters**:
- `val`: Resource consumption multiplier (0.1 to 1.0)

**Formulas**:
```
consumption_mult *= val
mass_mult *= 1.0 / val
cost_mult *= 1.0 / val
```

**Examples**:
| resource_mult | consumption_mult | mass_mult | cost_mult |
|---------------|------------------|-----------|-----------|
| 1.0 | 1.0 | 1.0 | 1.0 |
| 0.5 | 0.5 | 2.0 | 2.0 |
| 0.25 | 0.25 | 4.0 | 4.0 |
| 0.1 | 0.1 | 10.0 | 10.0 |

---

## 13. facing

**Purpose**: Sets the facing angle property.

**Parameters**:
- `val`: Angle in degrees (0 to 359)

**Formulas**:
```
properties['facing_angle'] = val
```

**Note**: This is a direct property set, not a multiplier.

---

## Summary: Stats Modified by Each Handler

| Handler | mass_mult | hp_mult | cost_mult | Other Stats |
|---------|-----------|---------|-----------|-------------|
| hardened_mount | *= val | *= val^2 | *= val | - |
| range_mount | *= 3.5^val | *= 3.5^val | *= 3.5^val | range_mult *= 2^val |
| turret_mount | *= (1+0.514*ln(1+val/30)) | - | - | arc_set = val |
| rapid_fire | += (val-1)*2 | - | *= val^0.5 | reload_mult *= 1/val |
| precision_mount | *= (1+val*0.5) | - | *= 1.5^val | accuracy_add += val*0.5 |
| simple_size | *= val | *= val | *= val | (many) *= val |
| seeker_endurance | *= (1+(val-1)*0.5) | - | *= val | endurance_mult *= val |
| seeker_damage | *= (1+(val-1)*0.75) | - | *= val^0.5 | projectile_damage_mult *= val |
| seeker_armored | *= (1+(val-1)*0.75) | - | *= val^0.5 | projectile_hp_mult *= val |
| seeker_stealth | *= (1+val*2) | - | *= 2^val | projectile_stealth_level += val |
| automation | *= (1+val) | - | *= (1+val) | crew_req_mult *= (1-val) |
| efficiency_mount | *= 1/val | - | *= 1/val | consumption_mult *= val |
| facing | - | - | - | properties.facing_angle = val |
