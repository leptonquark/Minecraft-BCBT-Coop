from items import items

gathering_tools = {
    items.COBBLESTONE: items.WOODEN_PICKAXE,
    items.STONE: items.WOODEN_PICKAXE,
    items.IRON_ORE: items.STONE_PICKAXE,
    items.DIAMOND_ORE: items.IRON_PICKAXE
}


def get_gathering_tool(materials):
    return gathering_tools.get(materials)


veins = {
    "cobblestone": "stone",
    "diamond": "diamond_ore"
}


def get_vein(material):
    return veins.get(material)
