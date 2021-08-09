from enum import Enum


class Item(Enum):
    AIR = "air"
    PLANT = "double_plant"
    TALL_GRASS = "tallgrass"
    GRASS = "grass"
    FLOWER_YELLOW = "yellow_flower"
    FLOWER_RED = "red_flower"
    WATER = "water"

    DIRT = "dirt"

    LOG = "log"
    LOG_2 = "log2"
    LEAVES = "leaves"
    COAL = "coal"
    STONE = "stone"
    COBBLESTONE = "cobblestone"
    COAL_ORE = "coal_ore"
    IRON_ORE = "iron_ore"
    DIAMOND_ORE = "diamond_ore"

    IRON_INGOT = "iron_ingot"
    DIAMOND = "diamond"

    STICKS = "stick"
    PLANKS = "planks"

    WOODEN_PICKAXE = "wooden_pickaxe"
    STONE_PICKAXE = "stone_pickaxe"
    IRON_PICKAXE = "iron_pickaxe"
    DIAMOND_PICKAXE = "diamond_pickaxe"

    WOODEN_SWORD = "wooden_sword"

    WOODEN_FENCE = "fence"

    CRAFTING_TABLE = "crafting_table"
    FURNACE = "furnace"

    BEEF = "beef"
    MUTTON = "mutton"

    GRAVEL = "gravel"
    SAND = "sand"


pickups = [
    Item.BEEF,
    Item.MUTTON,
    Item.LOG,
    Item.COAL,
    Item.IRON_ORE,
    Item.DIAMOND_ORE,
    Item.COBBLESTONE,
    Item.FURNACE,
    Item.CRAFTING_TABLE
]

traversable = [Item.AIR, Item.PLANT, Item.TALL_GRASS, Item.FLOWER_YELLOW, Item.FLOWER_RED, Item.WATER]
narrow = [Item.WOODEN_FENCE]
unclimbable = [Item.WOODEN_FENCE]
