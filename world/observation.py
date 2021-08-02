import json

import numpy as np

from items import items
from items.gathering import get_ore
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from mobs.animals import Animal
from utils.vectors import CIRCLE_DEGREES, flat_center_vector, Direction, directionAngle, directionVector, up_vector \
    , rad_to_degrees, center_vector, BlockFace

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
narrow = [items.WOODEN_FENCE]
unclimbable = [items.WOODEN_FENCE]


class Observation:
    GRID_LOCAL = "me"

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

    def __init__(self, observations, mission_data):
        self.mission_data = mission_data

        self.grid_size_local = mission_data.grid_local.get_grid_size()

        self.abs_pos = None
        self.abs_pos_inner = None
        self.abs_pos_discrete = None
        self.animals = None
        self.grid_local = None
        self.grids_global = {}
        self._inventory = None
        self.lower_surroundings = None
        self.los_abs_pos = None
        self.los_pos_discrete = None
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

        info_json = observations[-1].text
        if info_json is None:
            print("Info is null")
            return

        self.info = json.loads(info_json)
        self.inventory = Inventory(self.info)

        self.setup_absolute_position(self.info)
        self.setup_yaw(self.info)
        self.setup_pitch(self.info)
        self.setup_line_of_sight(self.info)
        self.setup_local_grid(self.info)
        self.setup_entities(self.info)

    def get_closest_block(self, block_type):
        if self.grid_local is not None:
            hits = self.get_hits(block_type)
            positions = np.argwhere(hits)
            if len(positions) > 0:
                distances = positions - self.pos
                distances = np.linalg.norm(distances, axis=1)
                min_dist_arg = np.argmin(distances)

                move = positions[min_dist_arg] - self.pos
                exact_move = move.astype("float64") - self.abs_pos_inner

                return exact_move
        return None

    def get_grid_local(self):
        if self.grid_local is not None:
            return self.grid_local
        grid_local_spec = self.mission_data.grid_local
        grid_local = grid_observation_from_list(self.info[grid_local_spec.name], grid_local_spec.get_grid_size())
        self.grid_local = grid_local

    def setup_absolute_position(self, info):
        if Observation.X in info and Observation.Y in info and Observation.Z in info:
            self.abs_pos = np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])
            self.abs_pos_discrete = np.floor(self.abs_pos)
            self.abs_pos_inner = self.abs_pos % 1 - flat_center_vector

    def setup_line_of_sight(self, info):
        if Observation.LOS in info:
            los = info[Observation.LOS]
            if Observation.LOS_X in los and Observation.LOS_Y in los and Observation.LOS_Z in los:
                self.los_abs_pos = np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
                self.los_pos = self.los_abs_pos - self.abs_pos
                self.setup_los_discrete_pos()
            if Observation.LOS_TYPE in los:
                self.los_type = los[Observation.LOS_TYPE]

    def setup_los_discrete_pos(self):
        # Calculate which face of the cube we are looking at. In case of corners it will be prioritized by x, y then z.
        # TODO: Make this work for non-full-size-blocks.
        los_face = BlockFace.NoFace
        if self.los_abs_pos[0] == int(self.los_abs_pos[0]):
            if 0 <= self.yaw <= 180:
                los_face = BlockFace.East
            else:
                los_face = BlockFace.West
        elif self.los_abs_pos[1] == int(self.los_abs_pos[1]):
            if self.pitch > 0:
                los_face = BlockFace.Up
            else:
                los_face = BlockFace.Down
        elif self.los_abs_pos[2] == int(self.los_abs_pos[2]):
            if 90 <= self.yaw <= 270:
                los_face = BlockFace.South
            else:
                los_face = BlockFace.North

        self.los_pos_discrete = np.floor(self.los_abs_pos)
        if los_face == BlockFace.East:
            self.los_pos_discrete[0] -= 1
        elif los_face == BlockFace.Up:
            self.los_pos_discrete[1] -= 1
        elif los_face == BlockFace.South:
            self.los_pos_discrete[2] -= 1

    def setup_yaw(self, info):
        if Observation.YAW in info:
            self.yaw = info[Observation.YAW]
            if self.yaw <= 0:
                self.yaw += CIRCLE_DEGREES

    def setup_pitch(self, info):
        if Observation.PITCH in info:
            self.pitch = info[Observation.PITCH]

    def setup_local_grid(self, info):
        if Observation.GRID_LOCAL in info:
            grid_local_spec = self.mission_data.grid_local
            self.grid_local = grid_observation_from_list(info[grid_local_spec.name], self.grid_size_local)
            self.pos = np.array([int(axis / 2) for axis in self.grid_size_local])

            self.upper_upper_surroundings = {
                direction: self.grid_local[tuple(self.pos + directionVector[direction] + 2 * up_vector)]
                for direction in Direction}
            self.upper_surroundings = {
                direction: self.grid_local[tuple(self.pos + directionVector[direction] + up_vector)]
                for direction in Direction}
            # print("Upper Surroundings", self.upper_surroundings)
            self.lower_surroundings = {direction: self.grid_local[tuple(self.pos + directionVector[direction])] for
                                       direction
                                       in Direction}
            #print("Lower Surroundings", self.lower_surroundings)

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

    def get_grid_global(self, grid_spec):
        if grid_spec.name in self.grids_global:
            return self.grids_global[grid_spec.name]

        grid = grid_observation_from_list(self.info[grid_spec.name], grid_spec.get_grid_size())
        self.grids_global[grid_spec.name] = grid
        return grid

    def get_current_direction(self):
        for key in directionAngle:
            check_angle = directionAngle[key]
            diff = check_angle - self.yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES:
                return key
        return Direction.South

    def is_block_observable(self, block_type):
        hits = None
        if self.grid_local is not None:
            hits = self.get_hits(block_type)
        return hits is not None and np.any(hits)

    def is_animal_observable(self, specie):
        if not self.animals:
            return False
        return any(animal.specie == specie for animal in self.animals)

    def get_hits(self, material):
        if material in self.hits:
            return self.hits[material]

        hits = (self.grid_local == material)
        ore = get_ore(material)
        if ore is not None:
            hits = (hits | (self.grid_local == ore))
        self.hits[material] = hits
        return hits

    def is_stuck(self):
        if self.lower_surroundings is None:
            return False
        position_traversable = self.lower_surroundings[Direction.Zero] in traversable
        position_narrow = self.lower_surroundings[Direction.Zero] in narrow

        return not position_traversable and not position_narrow

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

    # @Deprecated use is_looking_at instead...
    def is_looking_at_distance(self, distance):
        if self.los_abs_pos is None:
            return False

        wanted_pos = self.abs_pos_discrete + round_move(distance)
        return np.all(wanted_pos == self.los_pos_discrete)

    def is_looking_at(self, discrete_position):
        return np.all(discrete_position == self.los_pos_discrete)

    def is_looking_at_type(self, los_type):
        return self.los_type == los_type

    def get_exact_move(self, direction, delta_horizontal):
        move = directionVector[direction]
        exact_move = move.astype("float64") - self.abs_pos_inner
        exact_move[1] += delta_horizontal
        return exact_move

    def get_rounded_distance_to_position(self, position):
        return (position - self.abs_pos_discrete).astype('int64')

    def get_distance_to_position(self, position):
        position_center = position + flat_center_vector
        return position_center - self.abs_pos

    def is_block_at_position(self, position, block):
        if self.is_position_local(position):
            return self.get_block_at_position_from_local(position) == block
        return self.get_block_at_position_from_global(position) == block

    def is_position_local(self, position):
        distance = self.get_rounded_distance_to_position(position)
        grid_pos = self.pos + distance
        return np.all(grid_pos >= 0) and np.all(grid_pos < self.grid_size_local)

    def get_block_at_position_from_local(self, position):
        distance = self.get_rounded_distance_to_position(position)
        return self.grid_local[tuple(self.pos + distance)]

    def get_block_at_position_from_global(self, position):
        grids_global = self.mission_data.grids_global

        for grid_global_spec in grids_global:
            if grid_global_spec.contains_position(position):
                grid_global = self.get_grid_global(grid_global_spec)
                position_in_grid = position - grid_global_spec.grid_range[:, 0]
                return grid_global[tuple(position_in_grid)]

        return None

    def print(self):
        for key in self.info:
            if key != Observation.GRID_LOCAL:
                print(key, self.info[key])


def get_block_center(block_position):
    return np.around(block_position + center_vector) - center_vector


def grid_observation_from_list(grid_observation_list, grid_size):
    grid = np.array(grid_observation_list).reshape((grid_size[1], grid_size[2], grid_size[0]))
    grid = np.transpose(grid, (2, 0, 1))
    return grid


def round_move(move):
    return np.round(move).astype("int32")


def get_horizontal_distance(distance):
    return np.sqrt(distance[0] ** 2 + distance[2] ** 2)


def get_wanted_direction(move):
    if np.abs(move[2]) >= np.abs(move[0]):
        if move[2] > 0:
            wanted_direction = Direction.South
        else:
            wanted_direction = Direction.North
    else:
        if move[0] > 0:
            wanted_direction = Direction.East
        else:
            wanted_direction = Direction.West
    return wanted_direction


def get_yaw_from_direction(direction):
    return directionAngle[direction]


def get_yaw_from_vector(move):
    flat_move = np.copy(move)
    flat_move[1] = 0.0
    normalized_move = flat_move / np.linalg.norm(flat_move)

    south_angle = directionVector[Direction.South]
    dot_product_south = np.dot(normalized_move, south_angle)

    east_angle = directionVector[Direction.East]
    dot_product_east = np.dot(normalized_move, east_angle)

    cos_angle = np.clip(dot_product_south, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    angle = rad_to_degrees(angle)
    if dot_product_east > 0:
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


def get_wanted_pitch(dist_direction, delta_y):
    pitch = -np.arctan(delta_y / dist_direction)
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
