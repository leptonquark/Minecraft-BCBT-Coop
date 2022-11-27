from enum import Enum

import numpy as np

from bt.conditions import IsBlockAtPosition
from items import items
from world.grid import GridSpecification


class BlueprintType(Enum):
    Fence = 0
    StraightFence = 1
    PointCross = 2
    PointGrid = 3


DELTA_DEFAULT = 5


class Blueprint:

    def __init__(self, material, positions):
        self.material = material
        self.positions = positions

    def get_required_grid(self, name):
        grid_ranges = np.array([[position.min(), position.max()] for position in self.positions.T])
        return GridSpecification(name, grid_ranges, True)

    def as_conditions(self, agent):
        return [IsBlockAtPosition(agent, self.material, position) for position in self.positions]

    @staticmethod
    def get_blueprint(blueprint_type, start_position, delta=None):
        if blueprint_type == BlueprintType.Fence:
            return Blueprint(
                material=items.FENCE,
                positions=np.array(start_position) + np.array([
                    [0, 0, 0],
                    [0, 0, 1],
                    [0, 0, 2],
                    [0, 0, 3],
                    [1, 0, 3],
                    [2, 0, 3],
                    [3, 0, 3],
                    [3, 0, 2],
                    [3, 0, 1],
                    [3, 0, 0],
                    [2, 0, 0],
                    [1, 0, 0]
                ])
            )
        elif blueprint_type == BlueprintType.StraightFence:
            length = 9
            positions = [[0, 0, i] for i in range(length)]
            return Blueprint(
                material=items.FENCE,
                positions=np.array(start_position) + np.array(positions)
            )
        elif blueprint_type == BlueprintType.PointCross:
            return Blueprint(
                material=items.FENCE,
                positions=np.array(start_position) + np.array([
                    [0, 0, 0],
                    [0, 0, 5],
                    [0, 0, -5],
                    [5, 0, 0],
                    [-5, 0, 0]
                ])
            )
        elif blueprint_type == BlueprintType.PointGrid:
            delta = delta if delta else DELTA_DEFAULT
            return Blueprint(
                material=items.FENCE,
                positions=np.array(start_position) + np.array([
                    [0, 0, 0],
                    [0, 0, delta],
                    [0, 0, -delta],
                    [delta, 0, 0],
                    [delta, 0, delta],
                    [delta, 0, -delta],
                    [-delta, 0, 0],
                    [-delta, 0, delta],
                    [-delta, 0, -delta],
                ])
            )
