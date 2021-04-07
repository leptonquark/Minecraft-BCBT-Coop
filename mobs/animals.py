import numpy as np
from items import items

SHEEP = "Sheep"
COW = "Cow"
HORSE = "Horse"
CHICKEN = "Chicken"

species = [CHICKEN, SHEEP, COW, HORSE]

loot = {
    items.BEEF: COW
}


def get_loot_source(item):
    return loot.get(items.BEEF)


class Animal:

    def __init__(self, name, x, y, z):
        self.specie = name
        self.position = np.array([x, y, z])

    def __str__(self):
        return f"Animal: {self.specie} at position {self.position[0]}, {self.position[1]}, {self.position[2]}"

    def __repr__(self):
        return str(self)
