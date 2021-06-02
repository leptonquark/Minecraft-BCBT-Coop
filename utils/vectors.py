from enum import Enum

import numpy as np

CIRCLE_DEGREES = 360


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
flat_center_vector = np.array([0.5, 0, 0.5])
center_vector = np.array([0.5, 0.5, 0.5])


def rad_to_degrees(rad):
    half_circle = CIRCLE_DEGREES / 2
    return rad * half_circle / np.pi
