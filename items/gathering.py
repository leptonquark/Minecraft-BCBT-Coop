from items.items import Item

gathering_tools = {
    Item.COBBLESTONE: Item.WOODEN_PICKAXE,
    Item.STONE: Item.WOODEN_PICKAXE,
    Item.COAL: Item.WOODEN_PICKAXE,
    Item.COAL_ORE: Item.WOODEN_PICKAXE,
    Item.IRON_ORE: Item.STONE_PICKAXE,
    Item.DIAMOND: Item.IRON_PICKAXE,
    Item.DIAMOND_ORE: Item.IRON_PICKAXE
}


def get_gathering_tool(blocks):
    return gathering_tools.get(blocks)


ores = {
    Item.COBBLESTONE: Item.STONE,
    Item.COAL: Item.COAL_ORE,
    Item.DIAMOND: Item.DIAMOND_ORE
}


def get_ore(material):
    return ores.get(material)
