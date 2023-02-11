from mobs.entity import Entity

ENEMY_HEIGHT = 0

ZOMBIE = "Zombie"

types = [ZOMBIE]


class Enemy(Entity):

    def __init__(self, name, x, y, z):
        super().__init__(name, x, y, z)