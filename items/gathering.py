from items import items
from enum import Enum

from utils.dicts import invert_dict


class GatheringTier(Enum):
    BASE = 0
    WOOD = 1
    STONE = 2
    IRON = 3
    DIAMOND = 4


min_gathering_tier = {
    items.COBBLESTONE: GatheringTier.WOOD,
    items.STONE: GatheringTier.WOOD,
    items.COAL: GatheringTier.STONE,
    items.COAL_ORE: GatheringTier.STONE,
    items.IRON_ORE: GatheringTier.STONE,
    items.DIAMOND: GatheringTier.IRON,
    items.DIAMOND_ORE: GatheringTier.IRON,
    items.OBSIDIAN: GatheringTier.DIAMOND
}

pickaxe_gathering_tier = {
    items.WOODEN_PICKAXE: GatheringTier.WOOD,
    items.STONE_PICKAXE: GatheringTier.STONE,
    items.IRON_PICKAXE: GatheringTier.IRON,
    items.DIAMOND_PICKAXE: GatheringTier.DIAMOND
}

gathering_tier_pickaxe = invert_dict(pickaxe_gathering_tier)


def get_sufficient_pickaxes(min_tier):
    return [get_pickaxe(tier) for tier in GatheringTier if tier.value >= min_tier.value]


def get_pickaxe(tier):
    return gathering_tier_pickaxe.get(tier)


def get_gathering_tier_by_pickaxe(pickaxe):
    return pickaxe_gathering_tier.get(pickaxe)


def get_gathering_tier_by_material(material):
    return min_gathering_tier.get(material)


ores = {
    items.COBBLESTONE: items.STONE,
    items.COAL: items.COAL_ORE,
    items.DIAMOND: items.DIAMOND_ORE
}


def get_ore(material):
    return ores.get(material)
