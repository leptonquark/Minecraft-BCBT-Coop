from items import items

gathering_tools = {
    items.COBBLESTONE: items.WOODEN_PICKAXE,
    items.STONE: items.WOODEN_PICKAXE,
    items.COAL: items.WOODEN_PICKAXE,
    items.COAL_ORE: items.WOODEN_PICKAXE,
    items.IRON_ORE: items.STONE_PICKAXE,
    items.DIAMOND: items.IRON_PICKAXE,
    items.DIAMOND_ORE: items.IRON_PICKAXE
}


def get_gathering_tool(materials):
    return gathering_tools.get(materials)


ores = {
    items.COBBLESTONE: items.STONE,
    items.COAL: items.COAL_ORE,
    items.DIAMOND: items.DIAMOND_ORE
}


def get_ore(material):
    return ores.get(material)
