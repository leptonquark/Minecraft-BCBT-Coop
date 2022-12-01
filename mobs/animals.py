from items import items
from mobs.entity import Entity

CHICKEN = "Chicken"
PIG = "Pig"
SHEEP = "Sheep"
COW = "Cow"
HORSE = "Horse"

species = [CHICKEN, PIG, SHEEP, COW, HORSE]

loot = {
    items.BEEF: COW,
    items.MUTTON: SHEEP
}

starting_life = {
    COW: 10,
    SHEEP: 8,
    HORSE: 25
}


def get_loot_source(item):
    return loot.get(item)


class Animal(Entity):

    def __init__(self, name, x, y, z, life=None):
        super().__init__(name, x, y, z)

        self.life = None
        if life:
            self.life = life
        else:
            self.life = starting_life.get(self.specie, 0)

    def __str__(self):
        return f"Animal: {self.specie} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
