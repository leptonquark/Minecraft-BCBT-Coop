from mobs.entity import Entity


class AgentEntity(Entity):

    def __init__(self, name, x, y, z):
        super().__init__(name, x, y, z)
