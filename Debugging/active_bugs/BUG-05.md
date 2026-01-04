---
### 📝 User Update 2026-01-03 15:24
BUG-05

Stats Panel:
Logistics Should have the following entries for all resources that a vehicle consumes/holds/generates
- Max Capacity
- Amount Generated per second (100 game ticks)
- Constant Amount Used per second (100 game ticks) based on the contant usage
- Max Usage per sec (100 game ticks) based on constant usage + all weapons at maximum rate of fire
- Contant Rate Endurance - time that the resource will last at its constant rate of consumption + the amount it generates (this may be infinite if it generates faster than it uses)
- Max Rate Endurance - time that the resource will last at its maximum rate with all at maximum rate of fire.
- If a component is provided that hold, uses, or generates a resource all of the above should be included.  0 values an infinite values are indicated when appropriate.
---
