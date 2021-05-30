import json

import numpy as np

from items import items
from items.gathering import get_ore
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from mobs.animals import Animal
from utils.vectors import CIRCLE_DEGREES, center_vector, Direction, directionAngle, directionVector, up_vector \
    , rad_to_degrees, true_center_vector

MAX_DELAY = 60
YAW_TOLERANCE = 5
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MAX_PITCH = 0.5
PITCH_TOLERANCE = 3
SAME_SPOT_Y_THRESHOLD = 2
EPSILON_ARRIVED_AT_POSITION = 0.045
GATHERING_REACH = 3

traversable = [items.AIR, items.PLANT, items.TALL_GRASS, items.FLOWER_YELLOW, items.FLOWER_RED, items.WATER]


class Observation:
    GRID = "me"

    X = "XPos"
    Y = "YPos"
    Z = "ZPos"

    LOS = "LineOfSight"
    LOS_TYPE = "type"
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
    ENTITY_LIFE = "life"

    def __init__(self, observations, grid_size):
        self.grid_size = grid_size

        self.abs_pos = None
        self.abs_pos_inner = None
        self.animals = None
        self.grid = None
        self._inventory = None
        self.lower_surroundings = None
        self.los_abs_pos = None
        self.los_pos = None
        self.los_type = None

        self.upper_surroundings = None
        self.upper_upper_surroundings = None
        self.pos = None
        self.pickups = None
        self.pitch = None
        self.yaw = None

        self.hits = {}

        if observations is None or len(observations) == 0:
            print("Observations is null or empty")
            return

        infoJSON = observations[-1].text
        if infoJSON is None:
            print("Info is null")
            return

        self.info = json.loads(infoJSON)
        self.inventory = Inventory(self.info)

        self.setup_absolute_position(self.info)
        self.setup_line_of_sight(self.info)
        self.setup_yaw(self.info)
        self.setup_pitch(self.info)
        self.setup_grid(self.info)
        self.setup_entities(self.info)

    def setup_absolute_position(self, info):
        if Observation.X in info and Observation.Y in info and Observation.Z in info:
            self.abs_pos = np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])
            self.abs_pos_inner = self.abs_pos % 1 - center_vector

    def setup_line_of_sight(self, info):
        if Observation.LOS in info:
            print(info[Observation.LOS])
            los = info[Observation.LOS]
            if Observation.LOS_X in los and Observation.LOS_Y in los and Observation.LOS_Z in los:
                self.los_abs_pos = np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
                self.los_pos = self.los_abs_pos - self.abs_pos
            if Observation.LOS_TYPE in los:
                self.los_type = los[Observation.LOS_TYPE]

    def setup_yaw(self, info):
        if Observation.YAW in info:
            self.yaw = info[Observation.YAW]
            if self.yaw <= 0:
                self.yaw += CIRCLE_DEGREES

    def setup_pitch(self, info):
        if Observation.PITCH in info:
            self.pitch = info[Observation.PITCH]

    def setup_grid(self, info):
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

    def setup_entities(self, info):
        if Observation.ENTITIES in info:
            self.pickups = []
            self.animals = []
            for entity in info[Observation.ENTITIES]:
                entity_name = entity.get(Observation.ENTITY_NAME, None)
                entity_x = entity.get(Observation.ENTITY_X, None)
                entity_y = entity.get(Observation.ENTITY_Y, None)
                entity_z = entity.get(Observation.ENTITY_Z, None)
                if entity_name and entity_x is not None and entity_y is not None and entity_z is not None:
                    if entity_name in items.pickups:
                        self.pickups.append(PickUp(entity_name, entity_x, entity_y, entity_z))
                    elif entity_name in animals.species:
                        animal_life = entity.get(Observation.ENTITY_LIFE, None)
                        self.animals.append(Animal(entity_name, entity_x, entity_y, entity_z, animal_life))

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

    def is_block_observable(self, block_type):
        hits = None
        if self.grid is not None:
            hits = self.get_hits(block_type)
        return hits is not None and np.any(hits)

    def is_animal_observable(self, specie):
        if not self.animals:
            return False
        return any(animal.specie == specie for animal in self.animals)

    def get_closest_block(self, block_type):
        if self.grid is not None:
            hits = self.get_hits(block_type)
            positions = np.argwhere(hits)
            if len(positions) > 0:
                distances = positions - self.pos
                distances = np.sum(np.abs(distances), axis=1)
                min_dist_arg = np.argmin(distances)
                move = positions[min_dist_arg] - self.pos

                exact_move = move.astype("float64") - self.abs_pos_inner

                return exact_move
        return None

    def get_hits(self, material):
        if material in self.hits:
            return self.hits[material]

        hits = (self.grid == material)
        ore = get_ore(material)
        if ore is not None:
            hits = (hits | (self.grid == ore))
        self.hits[material] = hits
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

    def has_pickup_nearby(self, wanted):
        return any(pickup.name == wanted for pickup in self.pickups)

    def get_weakest_animal(self, specie=None):
        # Get the weakest animal. If there are several, take the closest of them.
        weakest_animal = None
        for animal in self.animals:
            if specie is None or animal.specie == specie:
                if weakest_animal is None:
                    weakest_animal = animal
                elif animal.life < weakest_animal.life:
                    weakest_animal = animal
                elif animal.life == weakest_animal.life:
                    distance = animal.position - self.abs_pos
                    weakest_distance = weakest_animal.position - self.abs_pos
                    if np.linalg.norm(distance) < np.linalg.norm(weakest_distance):
                        weakest_animal = animal

        if weakest_animal is not None:
            return weakest_animal.position - self.abs_pos
        else:
            return None

    def get_closest_animal(self, specie=None):
        closest_distance = None
        for animal in self.animals:
            if specie is None or animal.specie == specie:
                distance = animal.position - self.abs_pos
                if closest_distance is None or np.linalg.norm(distance) < np.linalg.norm(closest_distance):
                    closest_distance = distance
        return closest_distance

    def is_looking_at(self, distance):
        if self.los_abs_pos is None:
            return False

        exact_center_pos = self.abs_pos + distance
        exact_center_pos[1] += 0.5
        rounded_los_pos = np.around(self.los_abs_pos - true_center_vector) + true_center_vector
        return np.all(rounded_los_pos == exact_center_pos)

    def is_looking_at_type(self, los_type):
        return self.los_type == los_type

    def get_exact_move(self, direction, deltaHorizontal):
        move = directionVector[direction]
        exact_move = move.astype("float64") - self.abs_pos_inner
        exact_move[1] += deltaHorizontal
        print(exact_move)
        return exact_move


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


def get_turn_direction(yaw, wanted_angle):
    diff = wanted_angle - yaw
    if diff <= 0:
        diff += 360

    if diff <= YAW_TOLERANCE or diff >= CIRCLE_DEGREES - YAW_TOLERANCE:
        return 0
    else:
        half_circle = CIRCLE_DEGREES / 2
        if diff <= half_circle:
            return diff / half_circle
        else:
            return (diff - CIRCLE_DEGREES) / half_circle


def get_wanted_pitch(dist_direction, distY):
    pitch = -np.arctan(distY / dist_direction)
    return rad_to_degrees(pitch)


def get_pitch_change(pitch, wanted_pitch):
    quarter_circle = CIRCLE_DEGREES / 4
    diff = pitch - wanted_pitch
    if np.abs(diff) <= PITCH_TOLERANCE:
        return 0
    else:
        return -MAX_PITCH * diff / quarter_circle


def has_arrived(distance, reach=GATHERING_REACH):
    if distance is None:
        return False
    mat_horizontal_distance = get_horizontal_distance(distance)
    y_distance = distance[1]
    return (np.abs(y_distance) <= SAME_SPOT_Y_THRESHOLD and mat_horizontal_distance <= reach) \
           or mat_horizontal_distance <= EPSILON_ARRIVED_AT_POSITION
