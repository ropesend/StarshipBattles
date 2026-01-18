class Empire:
    """
    Represents a player or AI faction.
    """
    def __init__(self, empire_id, name, color, theme_path=None, empire_theme_id="Federation"):
        self.id = empire_id
        self.name = name
        self.color = color
        self.theme_path = theme_path
        self.empire_theme_id = empire_theme_id  # Ship theme for this empire's designs

        self.colonies = [] # List[Planet]
        self.fleets = [] # List[Fleet]

        # Design library tracking (Phase 3)
        self.designed_ships = []  # List[DesignMetadata] - cached design list
        self.built_ship_designs = set()  # Set of design_ids that were ever built

    def add_colony(self, planet):
        if planet not in self.colonies:
            self.colonies.append(planet)
            planet.owner_id = self.id

    def remove_colony(self, planet):
        if planet in self.colonies:
            self.colonies.remove(planet)
            planet.owner_id = None

    def add_fleet(self, fleet):
        self.fleets.append(fleet)
        fleet.owner_id = self.id

    def remove_fleet(self, fleet):
        if fleet in self.fleets:
            self.fleets.remove(fleet)

    def to_dict(self) -> dict:
        """
        Serialize Empire to dict.

        Stores colony IDs only (not full Planet objects) to avoid circular references.
        Planets will be resolved during load via galaxy.get_planet_by_id().
        """
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'theme_path': self.theme_path,
            'empire_theme_id': self.empire_theme_id,
            'colony_ids': [p.id for p in self.colonies],  # Store IDs only
            'fleets': [f.to_dict() for f in self.fleets],
            'built_ship_designs': list(self.built_ship_designs)
        }

    @classmethod
    def from_dict(cls, data: dict, galaxy=None) -> 'Empire':
        """
        Deserialize Empire from dict.

        Args:
            data: Saved empire data
            galaxy: Galaxy instance for resolving planet references (required)

        Returns:
            Reconstructed Empire with colonies resolved
        """
        from game.strategy.data.fleet import Fleet

        empire = cls(
            empire_id=data['id'],
            name=data['name'],
            color=data['color'],
            theme_path=data.get('theme_path'),
            empire_theme_id=data.get('empire_theme_id', 'Federation')
        )

        # Restore built_ship_designs set
        empire.built_ship_designs = set(data.get('built_ship_designs', []))

        # Restore fleets
        empire.fleets = [Fleet.from_dict(f) for f in data.get('fleets', [])]
        for fleet in empire.fleets:
            fleet.owner_id = empire.id

        # Resolve colony references via galaxy
        if galaxy is not None:
            for planet_id in data.get('colony_ids', []):
                planet = galaxy.get_planet_by_id(planet_id)
                if planet:
                    empire.colonies.append(planet)
                    planet.owner_id = empire.id

        return empire
