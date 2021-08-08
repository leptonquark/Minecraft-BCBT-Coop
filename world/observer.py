import numpy as np

from items.gathering import get_ore
from items.items import traversable, narrow
from utils.vectors import center_vector, Direction, directionAngle, directionVector, rad_to_degrees, CIRCLE_DEGREES, \
    up_vector, flat_center_vector, BlockFace

DELTA_ANGLES = 45
GATHERING_REACH = 3
YAW_TOLERANCE = 15
PITCH_TOLERANCE = 3
MAX_PITCH = 0.5


class Observer:
    def __init__(self, observation=None):
        self.observation = observation
        self.hits = {}

        self.lower_surroundings = self.get_surroundings(self.observation.pos_local_grid)
        self.upper_surroundings = self.get_surroundings(self.observation.pos_local_grid + up_vector)
        self.upper_upper_surroundings = self.get_surroundings(self.observation.pos_local_grid + 2 * up_vector)

    def get_surroundings(self, central_position):
        return {
            direction: self.get_grid_local_block(central_position + directionVector[direction])
            for direction in Direction
        }

    def get_grid_local_block(self, position):
        return self.observation.grid_local[tuple(position)]

    def get_abs_pos_discrete(self):
        return np.floor(self.observation.abs_pos)

    def get_closest_block(self, block_type):
        hits = self.get_hits(block_type)
        if hits is None:
            return None

        positions = np.argwhere(hits)
        if len(positions) > 0:
            distances_vector = positions - self.observation.pos_local_grid
            distances = np.linalg.norm(distances_vector, axis=1)
            min_dist_arg = np.argmin(distances)

            return self.get_abs_pos_discrete() + distances_vector[min_dist_arg]

    def is_block_observable(self, block_type):
        hits = self.get_hits(block_type)
        return hits is not None and np.any(hits)

    def get_hits(self, material):
        if material in self.hits:
            return self.hits[material]

        if self.observation.grid_local is None:
            return None

        hits = (self.observation.grid_local == material)
        ore = get_ore(material)
        if ore is not None:
            hits = (hits | (self.observation.grid_local == ore))
        self.hits[material] = hits
        return hits

    def get_first_block_downwards(self):
        check_position = np.copy(self.observation.pos_local_grid)
        while self.observation.grid_local[tuple(check_position)] in traversable:
            check_position -= up_vector
        return self.get_abs_pos_discrete() - self.observation.pos_local_grid + check_position

    def is_position_within_reach(self, position, reach=GATHERING_REACH):
        return position is not None and np.linalg.norm(self.get_distance_to_discrete_position(position)) <= reach

    def is_block_at_position(self, position, block):
        if self.is_position_local(position):
            return self.get_block_at_position_from_local(position) == block
        return self.get_block_at_position_from_global(position) == block

    def is_position_local(self, position):
        grid_pos = self.observation.pos_local_grid + self.get_rounded_distance_to_position(position)
        return np.all(grid_pos >= 0) and np.all(grid_pos < self.observation.grid_size_local)

    def get_block_at_position_from_local(self, position):
        distance = self.get_rounded_distance_to_position(position)
        return self.observation.grid_local[tuple(self.observation.pos_local_grid + distance)]

    def get_block_at_position_from_global(self, position):
        grids_global = self.observation.mission_data.grids_global

        for grid_global_spec in grids_global:
            if grid_global_spec.contains_position(position):
                grid_global = self.observation.get_grid_global(grid_global_spec)
                position_in_grid = position - grid_global_spec.grid_range[:, 0]
                return grid_global[tuple(position_in_grid)]
        return None

    def get_distance_to_discrete_position(self, discrete_position):
        position_center = discrete_position + flat_center_vector
        return position_center - self.observation.abs_pos

    def get_rounded_distance_to_position(self, position):
        return (position - self.get_abs_pos_discrete()).astype('int64')

    def get_distance_to_position(self, position):
        return position - self.observation.abs_pos

    def is_looking_at_type(self, los_type):
        return self.observation.los_type == los_type

    def is_looking_at_discrete_position(self, discrete_position):
        los_discrete_position = self.get_los_pos_discrete()

        return los_discrete_position is not None and np.all(discrete_position == los_discrete_position)

    def get_los_pos_discrete(self):
        if self.observation.los_abs_pos is None:
            return None

        # Calculate which face of the cube we are looking at. In case of corners it will be prioritized by x, y then z.
        # TODO: Make this work for non-full-size-blocks.
        los_face = BlockFace.NoFace
        if self.observation.los_abs_pos[0] == int(self.observation.los_abs_pos[0]):
            if 0 <= self.observation.yaw <= 180:
                los_face = BlockFace.East
            else:
                los_face = BlockFace.West
        elif self.observation.los_abs_pos[1] == int(self.observation.los_abs_pos[1]):
            if self.observation.pitch > 0:
                los_face = BlockFace.Up
            else:
                los_face = BlockFace.Down
        elif self.observation.los_abs_pos[2] == int(self.observation.los_abs_pos[2]):
            if 90 <= self.observation.yaw <= 270:
                los_face = BlockFace.South
            else:
                los_face = BlockFace.North

        los_pos_discrete = np.floor(self.observation.los_abs_pos)
        if los_face == BlockFace.East:
            los_pos_discrete[0] -= 1
        elif los_face == BlockFace.Up:
            los_pos_discrete[1] -= 1
        elif los_face == BlockFace.South:
            los_pos_discrete[2] -= 1
        return los_pos_discrete

    def get_weakest_animal_position(self, specie=None):
        # Get the weakest animal. If there are several, take the closest of them.
        weakest_animal = None
        for animal in self.observation.animals:
            if specie is None or animal.specie == specie:
                if weakest_animal is None:
                    weakest_animal = animal
                elif animal.life < weakest_animal.life:
                    weakest_animal = animal
                elif animal.life == weakest_animal.life:
                    distance = animal.position - self.observation.abs_pos
                    weakest_distance = weakest_animal.position - self.observation.abs_pos
                    if np.linalg.norm(distance) < np.linalg.norm(weakest_distance):
                        weakest_animal = animal

        if weakest_animal is not None:
            return weakest_animal.position
        else:
            return None

    def has_pickup_nearby(self, wanted):
        return any(pickup.name == wanted for pickup in self.observation.pickups)

    def get_pickup_position(self, wanted):
        for pickup in self.observation.pickups:
            if pickup.name == wanted:
                return pickup.get_centralized_position() - self.observation.abs_pos
        return None

    def is_stuck(self):
        if self.lower_surroundings is None:
            return False
        position_traversable = self.lower_surroundings[Direction.Zero] in traversable + narrow
        return not position_traversable

    def is_animal_observable(self, specie):
        return self.observation.animals and any(animal.specie == specie for animal in self.observation.animals)

    def get_current_direction(self):
        for key in directionAngle:
            check_angle = directionAngle[key]
            diff = check_angle - self.observation.yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES:
                return key
        return Direction.South

    def get_turn_direction(self, distance):
        wanted_angle = get_yaw_from_vector(distance)

        diff = wanted_angle - self.observation.yaw
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

    def get_pitch_change(self, wanted_pitch):
        quarter_circle = CIRCLE_DEGREES / 4
        diff = self.observation.pitch - wanted_pitch
        if np.abs(diff) <= PITCH_TOLERANCE:
            return 0
        else:
            return -MAX_PITCH * diff / quarter_circle


def get_position_center(block_position):
    return np.around(block_position + center_vector) - center_vector


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


def get_wanted_pitch(dist_direction, delta_y):
    pitch = -np.arctan(delta_y / dist_direction)
    return rad_to_degrees(pitch)
