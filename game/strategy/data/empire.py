class Empire:
    """
    Represents a player or AI faction.
    """
    def __init__(self, empire_id, name, color):
        self.id = empire_id
        self.name = name
        self.color = color
        
        self.colonies = [] # List[Planet]
        self.fleets = [] # List[Fleet]
        
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
