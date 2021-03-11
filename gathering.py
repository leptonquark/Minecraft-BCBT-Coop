import items

gathering_tools = {
    items.STONE: items.WOODEN_PICKAXE,
    items.IRON_ORE: items.STONE_PICKAXE,
    items.DIAMOND_ORE: items.IRON_PICKAXE
}


def get_gathering_tools(materials):
    if isinstance(materials, list):
        tools = [gathering_tools[material] for material in materials if material in gathering_tools]
        tools = list(set(tools))
        if len(tools) == 1:
            return tools[0]
        else:
            return None
    elif isinstance(materials, str):
        return gathering_tools.get(materials)
    else:
        return None
