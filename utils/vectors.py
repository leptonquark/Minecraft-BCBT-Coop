from enum import Enum

import numpy as np

CIRCLE_DEGREES = 360


class Direction(Enum):
    Zero = 0
    South = 1
    West = 2
    North = 3
    East = 4


class BlockFace(Enum):
    NoFace = 0
    Up = 1
    Down = 2
    South = 3
    West = 4
    North = 5
    East = 6


directionAngle = {
    Direction.South: 0,
    Direction.West: 90,
    Direction.North: 180,
    Direction.East: 270
}

directionVector = {
    Direction.Zero: np.array([0, 0, 0]),
    Direction.North: np.array([0, 0, -1]),
    Direction.East: np.array([1, 0, 0]),
    Direction.South: np.array([0, 0, 1]),
    Direction.West: np.array([-1, 0, 0])
}

up_vector = np.array([0, 1, 0])
down_vector = np.array([0, -1, 0])
flat_center_vector = np.array([0.5, 0, 0.5])
center_vector = np.array([0.5, 0.5, 0.5])


def radians_to_degrees(rad):
    half_circle = CIRCLE_DEGREES / 2
    return rad * half_circle / np.pi


def degrees_to_radians(deg):
    half_circle = CIRCLE_DEGREES / 2
    return deg * np.pi / half_circle
