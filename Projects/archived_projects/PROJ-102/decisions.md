# PROJ-102: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Strategic Superweapons and Special Orders |
| 2026-02-10 | Use Ctrl+ prefix for stellar manipulation keys | User preference; avoids conflicts with existing unmodified key bindings (D=Design, O=Orders, etc.) |
| 2026-02-10 | Stellerate Star uses Ctrl+Shift+S | Ctrl+S is already bound to Save Game; Ctrl+Shift+S is distinct from both Ctrl+S and Shift+S (Zoom System) |
| 2026-02-10 | Open Warp Point uses Ctrl+W (not Ctrl+O) | W for "Warp" is more intuitive; avoids confusion with O (Fleet Orders) even though Ctrl+O is technically distinct |
| 2026-02-10 | Self-Destruct uses X (no modifier) | X is currently unbound; Alt+X (Exit Game) has different modifiers so no conflict |
| 2026-02-10 | Star destruction is suicide: ALL ships die including actor | User preference - "Everything (suicide)" - true superweapon, not a tactical tool |
| 2026-02-10 | No component constraints (mass, cost, ship class) | User: "No constraints right now, I have not yet implemented the research portion of the game, these will be locked behind a large research wall" |
| 2026-02-10 | Self-Destruct uses multi-select ship picker dialog | User: "Ship Picker dialog, but you should be able to pick multiple ships, ships without self destruct devices can't self destruct" |
| 2026-02-10 | Consume entire ship carrying superweapon component (not just the component) | Follows the colonization pattern where the colony ship is removed from the fleet after use |
| 2026-02-10 | Only warp points survive star destruction | Per user spec: "the only thing that should remain are the warp points" |
| 2026-02-10 | Dyson Sphere uses Sphereworld_Portrait.png | User specified asset path; file confirmed to exist at `assets/Images/Stellar Objects/Sphere world/Sphereworld_Portrait.png` |
| 2026-02-10 | Dyson Sphere is 15 hexes diameter, eliminates planets within 9 hexes of star | Per user spec |
| 2026-02-10 | Dyson Sphere treated as colonizable planet with PlanetType.DYSON_SPHERE | Per user spec; needs new PlanetType enum value |
| 2026-02-10 | Open Warp Point far-end placement: direction from ship to target system, at typical orbit distance | Per user spec; near-end location chosen by player, far-end calculated automatically |
| 2026-02-10 | Self-Destruct happens at start of next turn (not end of current turn) | Per user spec: "The ship should destroy itself at the start of the next turn" |
