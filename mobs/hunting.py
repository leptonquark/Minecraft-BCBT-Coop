from items.items import Item
from mobs import animals

hunting_tools = {
    animals.COW: Item.WOODEN_SWORD
}


def get_hunting_tool(animal):
    return hunting_tools.get(animal)
