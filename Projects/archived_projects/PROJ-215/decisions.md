# PROJ-215: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Fix Event Log Location Display and Navigation |
| 2026-02-28 | Replace single Location column with System, Planet, Local Hex, Galaxy Hex | User wants granular location data with per-column visibility toggles |
| 2026-02-28 | Add Storm column showing storm names at event hex | User wants environmental context visible in event log |
| 2026-02-28 | Sidebar for column toggles (match FleetReport/PlanetList pattern) | Established UI pattern in codebase; user confirmed sidebar approach |
| 2026-02-28 | All three workstreams in scope (columns, navigation, storm) | User confirmed full solution over incremental approach |
| 2026-02-28 | Enrich events at creation time with system_name, local_hex | Events persist in saves; enriching at creation ensures data is always available without galaxy reference at render time |
| 2026-02-28 | Local Hex and Galaxy Hex columns default to visible=False | Most users want system/planet context; hex coords are power-user info |
| 2026-02-28 | Storm column defaults to visible=False | Most events won't be in storms; avoids visual clutter |
| 2026-02-28 | Phase order: columns → enrichment → sidebar → navigation → storm | Columns first establishes the new schema; enrichment fills data; sidebar adds toggle UI; navigation is independent bug fix; storm builds on column infrastructure |
