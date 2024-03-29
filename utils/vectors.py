from enum import Enum

import numpy as np

CIRCLE_DEGREES = 360


class Direction(Enum):
    Zero = 0
    South = 1
    West = 2
    North = 3
    East = 4


class RelativeDirection(Enum):
    Left = 0
    Right = 1


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

up = np.array([0, 1, 0])
down = np.array([0, -1, 0])
flat_center = np.array([0.5, 0, 0.5])
center = np.array([0.5, 0.5, 0.5])

faceDistance = {
    BlockFace.NoFace: directionVector[Direction.Zero],
    BlockFace.Up: 0.5 * up,
    BlockFace.Down: 0.5 * down,
    BlockFace.South: 0.5 * directionVector[Direction.South],
    BlockFace.West: 0.5 * directionVector[Direction.West],
    BlockFace.North: 0.5 * directionVector[Direction.North],
    BlockFace.East: 0.5 * directionVector[Direction.East],
}


def radians_to_degrees(rad):
    half_circle = CIRCLE_DEGREES / 2
    return rad * half_circle / np.pi


# TODO: Make this work for non-full-size-blocks.
# Calculate which face of the cube we are looking at. In case of corners it will be prioritized by x, y then z.
def get_los_face(los_pos, yaw, pitch):
    if los_pos[0] == int(los_pos[0]):
        if 0 <= yaw <= 180:
            return BlockFace.East
        else:
            return BlockFace.West
    elif los_pos[1] == int(los_pos[1]):
        if pitch > 0:
            return BlockFace.Up
        else:
            return BlockFace.Down
    elif los_pos[2] == int(los_pos[2]):
        if 90 <= yaw <= 270:
            return BlockFace.South
        else:
            return BlockFace.North
    return BlockFace.NoFace


def normalize(vector):
    return vector / np.linalg.norm(vector)


def flatten(vector):
    return np.array([vector[0], 0, vector[2]]) if vector is not None else None
