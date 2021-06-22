from mobs import animals
from items import items

hunting_tools = {
    animals.COW: items.WOODEN_SWORD
}


def get_hunting_tool(animal):
    return hunting_tools.get(animal)
