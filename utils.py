import numpy as np
from enum import Enum


class Direction(Enum):
    Zero = 0
    North = 1
    West = 2
    South = 3
    East = 4



directionAngle = {
    Direction.North : 0,
    Direction.East : 90,
    Direction.South : 180,
    Direction.West : 270
}

directionVector = {
    Direction.Zero : np.array([0, 0, 0]),
    Direction.North : np.array([0, 0, 1]),
    Direction.East : np.array([-1, 0, 0]),
    Direction.South : np.array([0, 0, -1]),
    Direction.West : np.array([1, 0, 0])
}


up_vector = np.array([0, 1, 0])
down_vector = np.array([0, -1, 0])
