import numpy as np

from bt.conditions import IsBlockAtPosition
from enum import Enum
from items import items
from world.grid import GridSpecification


class BlueprintType(Enum):
    Fence = 0
    StraightFence = 1


class Blueprint:

    def __init__(self, material, positions):
        self.material = material
        self.positions = positions

    def get_required_grid(self, name):
        grid_ranges = np.array([[position.min(), position.max()] for position in self.positions.T])
        return GridSpecification(name, grid_ranges, True)

    def as_conditions(self, agent):
        return [IsBlockAtPosition(agent, items.WOODEN_FENCE, position) for position in self.positions]

    @staticmethod
    def get_blueprint(blueprint_type):
        if blueprint_type == BlueprintType.Fence:
            return Blueprint(
                material=items.WOODEN_FENCE,
                positions=np.array([
                    [209, 65, 238],
                    [209, 65, 239],
                    [209, 65, 240],
                    [209, 65, 241],
                    [210, 65, 241],
                    [211, 65, 241],
                    [212, 65, 241],
                    [212, 65, 240],
                    [212, 65, 239],
                    [212, 65, 238],
                    [211, 65, 238],
                    [210, 65, 238],
                ])
            )
        elif blueprint_type == BlueprintType.StraightFence:
            return Blueprint(
                material=items.WOODEN_FENCE,
                positions=np.array([
                    [209, 65, 241],
                    [210, 65, 241],
                    [211, 65, 241],
                    [212, 65, 241],
                    [213, 65, 241],
                    [214, 65, 241],
                    [215, 65, 241],
                    [216, 65, 241],
                ])
            )
