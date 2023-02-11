from items import items
from mobs.entity import Entity

CHICKEN = "Chicken"
PIG = "Pig"
SHEEP = "Sheep"
COW = "Cow"
HORSE = "Horse"

types = [CHICKEN, PIG, SHEEP, COW, HORSE]

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
        self.life = life if life is not None else starting_life.get(name, 0)

    def is_specie(self, specie):
        return specie is None or self.type == specie
