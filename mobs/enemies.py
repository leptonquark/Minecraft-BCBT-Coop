from mobs.entity import Entity

ZOMBIE = "Zombie"


class Enemy(Entity):

    def __init__(self, name, x, y, z):
        super().__init__(name, x, y, z)

    def __str__(self):
        return f"Enemy: {self.specie} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
