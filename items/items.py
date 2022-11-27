AIR = "air"
PLANT = "double_plant"
TALL_GRASS = "tallgrass"
FLOWER_YELLOW = "yellow_flower"
FLOWER_RED = "red_flower"
WATER = "water"

BEDROCK = "bedrock"
OBSIDIAN = "obsidian"

DIRT = "dirt"
GRASS = "grass"

CLAY = "clay"

SANDSTONE = "sandstone"

LOG = "log"
LOG_2 = "log2"
COAL = "coal"
STONE = "stone"
COBBLESTONE = "cobblestone"
SAND = "sand"
GRAVEL = "gravel"

COAL_ORE = "coal_ore"
IRON_ORE = "iron_ore"
LAPIS_ORE = "lapis_ore"
REDSTONE_ORE = "redstone_ore"
GOLD_ORE = "gold_ore"
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

FENCE = "fence"
ACACIA_FENCE = "acacia_fence"

CRAFTING_TABLE = "crafting_table"
FURNACE = "furnace"

BEEF = "beef"
MUTTON = "mutton"

LEAVES = "leaves"
LEAVES_2 = "leaves2"

MOSSY_COBBLESTONE = "mossy_cobblestone"

MOB_SPAWNER = "mob_spawner"

CHEST = "chest"

BROWN_MUSHROOM = "brown_mushroom"
RED_MUSHROOM = "red_mushroom"

DEAD_BUSH = "deadbush"

FLOWING_WATER = "flowing_water"

LAVA = "lava"
FLOWING_LAVA = "flowing_lava"

FIRE = "fire"

CACTUS = "cactus"

REEDS = "reeds"

XP_ORB = "XPOrb"

pickups = [
    BEEF,
    MUTTON,
    LOG,
    LOG_2,
    COAL,
    IRON_ORE,
    DIAMOND,
    COBBLESTONE,
    FURNACE,
    CRAFTING_TABLE,
    ACACIA_FENCE,
    FENCE
]


def get_variants(item):
    return [item] + VARIANTS.get(item, [])


VARIANTS = {FENCE: [ACACIA_FENCE], LOG: [LOG_2]}

traversable = [AIR, PLANT, TALL_GRASS, FLOWER_YELLOW, FLOWER_RED, WATER]
narrow = get_variants(FENCE)
unclimbable = get_variants(FENCE)
