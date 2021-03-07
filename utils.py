import items
import numpy as np
from enum import Enum


class Direction(Enum):
    Zero = 0
    North = 1
    West = 2
    South = 3
    East = 4


directionAngle = {
    Direction.North: 0,
    Direction.East: 90,
    Direction.South: 180,
    Direction.West: 270
}

directionVector = {
    Direction.Zero: np.array([0, 0, 0]),
    Direction.North: np.array([0, 0, 1]),
    Direction.East: np.array([-1, 0, 0]),
    Direction.South: np.array([0, 0, -1]),
    Direction.West: np.array([1, 0, 0])
}

up_vector = np.array([0, 1, 0])
down_vector = np.array([0, -1, 0])

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
