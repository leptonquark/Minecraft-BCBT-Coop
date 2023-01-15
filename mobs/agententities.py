from mobs.entity import Entity


class AgentEntity(Entity):

    def __init__(self, name, x, y, z):
        super().__init__(name, x, y, z)

    def __str__(self):
        return f"Agent Entity: {self.type} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
