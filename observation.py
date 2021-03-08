import json

import items
import numpy as np

from inventory import Inventory
from utils import Direction, directionAngle, directionVector, up_vector

MAX_DELAY = 60
YAW_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MAX_PITCH = 0.2

not_stuck = [items.AIR, items.PLANT, items.TALL_GRASS, items.FLOWER_YELLOW, items.WATER]


class Observation:

    def __init__(self, observations, grid_size):

        self.grid_size = grid_size

        if observations is None or len(observations) == 0:
            print("Observations is null or empty")
            self.inventory = None
            return

        infoJSON = observations[-1].text
        if infoJSON is None:
            print("Info is null")
            return

        info = json.loads(infoJSON)
        self.info = info

        self.inventory = Inventory(info)

        los_abs_pos = None

        abs_pos = None
        if "XPos" in info and "YPos" in info and "ZPos" in info:
            abs_pos = np.array([info["XPos"], info["YPos"], info["ZPos"]])
        print("Absolute Position", abs_pos)
        self.inner_abs_pos = abs_pos % 1
        print("Inner Absolute Position", self.inner_abs_pos)

        self.los_pos = None
        if "LineOfSight" in info:
            los = info["LineOfSight"]
            print("los", los)
            los_abs_pos = np.array([los["x"], los["y"], los["z"]])
            self.los_pos = los_abs_pos - abs_pos
        print("LOS", self.los_pos)

        yaw = 0
        if "Yaw" in info:
            yaw = info["Yaw"]
            if yaw <= 0:
                yaw += CIRCLE_DEGREES
        self.yaw = yaw

        pitch = 0
        if "Pitch" in info:
            pitch = info["Pitch"]
        self.pitch = pitch

        if "me" in info:
            self.grid = self.grid_observation_from_list(info["me"])
            self.pos = np.array([int(axis / 2) for axis in self.grid_size])

            self.upper_surroundings = {direction: self.grid[tuple(self.pos + directionVector[direction] + up_vector)]
                                       for direction in Direction}
            print("Upper Surroundings", self.upper_surroundings)
            self.lower_surroundings = {direction: self.grid[tuple(self.pos + directionVector[direction])] for direction
                                       in Direction}
            print("Lower Surroundings", self.lower_surroundings)

    def grid_observation_from_list(self, grid_observation_list):
        grid = np.array(grid_observation_list).reshape(self.grid_size[1], self.grid_size[2], self.grid_size[0])
        grid = np.transpose(grid, (2, 0, 1))
        return grid

    def get_current_direction(self):
        for key in directionAngle:
            checkAngle = directionAngle[key]
            diff = checkAngle - self.yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES:
                return key
        return Direction.North

    def get_closest(self, materials):
        if self.grid is not None:
            hits = (self.grid == materials[0])
            if len(materials) > 1:
                for i in range(1, len(materials)):
                    hits = (hits | (self.grid == materials[i]))
            positions = np.argwhere(hits)
            if len(positions) > 0:
                distances = positions - self.pos
                distances = np.sum(np.abs(distances), axis=1)
                min_dist_arg = np.argmin(distances)
                move = positions[min_dist_arg] - self.pos

                print("move", move)

                return move

        return None

    def is_stuck(self):
        return self.lower_surroundings[Direction.Zero] not in not_stuck

    def print(self):
        for key in self.info:
            if key != "me":
                print(key, self.info[key])


def get_horizontal_distance(distance):
    return np.abs(distance[0]) + np.abs(distance[2])


def get_wanted_direction(move):
    if np.abs(move[2]) >= np.abs(move[0]):
        if move[2] > 0:
            wantedDirection = Direction.North
        else:
            wantedDirection = Direction.South
    else:
        if move[0] > 0:
            wantedDirection = Direction.West
        else:
            wantedDirection = Direction.East
    return wantedDirection


def get_wanted_angle(direction):
    return directionAngle[direction]
