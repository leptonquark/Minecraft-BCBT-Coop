import json
import numpy as np

from items import items
from items.gathering import get_ore
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from utils import center_vector, Direction, directionAngle, directionVector, up_vector, rad_to_degrees

MAX_DELAY = 60
YAW_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MAX_PITCH = 0.2

traversable = [items.AIR, items.PLANT, items.TALL_GRASS, items.FLOWER_YELLOW, items.WATER]


class Observation:
    GRID = "me"

    X = "XPos"
    Y = "YPos"
    Z = "ZPos"

    LOS = "LineOfSight"
    LOS_X = "x"
    LOS_Y = "y"
    LOS_Z = "z"

    YAW = "Yaw"
    PITCH = "Pitch"

    ENTITIES = "entities"
    ENTITY_NAME = "name"
    ENTITY_X = "x"
    ENTITY_Y = "y"
    ENTITY_Z = "z"

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
        if Observation.X in info and Observation.Y in info and Observation.Z in info:
            abs_pos = np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])
        print("Absolute Position", abs_pos)
        self.abs_pos = abs_pos
        self.inner_abs_pos = abs_pos % 1 - center_vector
        print("Inner Absolute Position", self.inner_abs_pos)

        self.los_pos = None
        if Observation.LOS in info:
            los = info[Observation.LOS]
            los_abs_pos = np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
            self.los_pos = los_abs_pos - abs_pos
        print("LOS", self.los_pos)

        yaw = 0
        if Observation.YAW in info:
            yaw = info[Observation.YAW]
            if yaw <= 0:
                yaw += CIRCLE_DEGREES
        self.yaw = yaw
        print("yaw", self.yaw)

        pitch = 0
        if Observation.PITCH in info:
            pitch = info[Observation.PITCH]
        self.pitch = pitch

        if Observation.GRID in info:
            self.grid = self.grid_observation_from_list(info[Observation.GRID])
            self.pos = np.array([int(axis / 2) for axis in self.grid_size])

            self.upper_upper_surroundings = {
                direction: self.grid[tuple(self.pos + directionVector[direction] + 2 * up_vector)]
                for direction in Direction}
            self.upper_surroundings = {direction: self.grid[tuple(self.pos + directionVector[direction] + up_vector)]
                                       for direction in Direction}
            print("Upper Surroundings", self.upper_surroundings)
            self.lower_surroundings = {direction: self.grid[tuple(self.pos + directionVector[direction])] for direction
                                       in Direction}
            print("Lower Surroundings", self.lower_surroundings)

        self.pickups = []
        self.animals = []
        if Observation.ENTITIES in info:
            for entity in info[Observation.ENTITIES]:
                entity_name = entity.get(Observation.ENTITY_NAME, None)
                entity_x = entity.get(Observation.ENTITY_X, None)
                entity_y = entity.get(Observation.ENTITY_Y, None)
                entity_z = entity.get(Observation.ENTITY_Z, None)

                if entity_name and entity_x is not None and entity_y is not None and entity_z is not None:
                    if entity_name in items.pickups:
                        self.pickups.append(PickUp(entity_name, entity_x, entity_y, entity_z))
                    elif entity_name in animals.animals:
                        self.animals.append(entity)

    def grid_observation_from_list(self, grid_observation_list):
        grid = np.array(grid_observation_list).reshape((self.grid_size[1], self.grid_size[2], self.grid_size[0]))
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
            hits = self.get_hits(materials)
            positions = np.argwhere(hits)
            if len(positions) > 0:
                distances = positions - self.pos
                distances = np.sum(np.abs(distances), axis=1)
                min_dist_arg = np.argmin(distances)
                move = positions[min_dist_arg] - self.pos

                exact_move = move.astype("float64") - self.inner_abs_pos
                print(exact_move)

                return exact_move
        return None

    def get_hits(self, material):
        hits = (self.grid == material)
        ore = get_ore(material)
        if ore is not None:
            hits = (hits | (self.grid == ore))
        return hits

    def is_stuck(self):
        return self.lower_surroundings is not None and self.lower_surroundings[Direction.Zero] not in traversable

    def print(self):
        for key in self.info:
            if key != Observation.GRID:
                print(key, self.info[key])

    def get_pickup_position(self, wanted):
        for pickup in self.pickups:
            if pickup.name == wanted:
                return pickup.get_centralized_position() - self.abs_pos
        return None


def round_move(move):
    return np.round(move).astype("int32")


def get_horizontal_distance(distance):
    return np.sqrt(distance[0] ** 2 + distance[2] ** 2)


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


def get_yaw_from_direction(direction):
    return directionAngle[direction]


def get_yaw_from_vector(move):
    flat_move = np.copy(move)
    flat_move[1] = 0.0
    normalized_move = flat_move / np.linalg.norm(flat_move)

    north_angle = directionVector[Direction.North]
    dot_product_north = np.dot(normalized_move, north_angle)

    west_angle = directionVector[Direction.West]
    dot_product_west = np.dot(normalized_move, west_angle)

    cos_angle = np.clip(dot_product_north, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    angle = rad_to_degrees(angle)
    if dot_product_west > 0:
        angle = CIRCLE_DEGREES - angle
    return angle
