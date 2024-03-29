import numpy as np

from items.gathering import get_ore
from items.items import traversable, narrow, get_variants
from utils import vectors
from utils.vectors import get_los_face, up, normalize, flatten
from world.observation import LineOfSightHitType

DELTA_ANGLES = 45
GATHERING_REACH = 3
YAW_TOLERANCE = 8
PITCH_TOLERANCE = 0.5
MAX_PITCH = 0.8
PICKUP_NEARBY_DISTANCE_TOLERANCE = 10
EYE_HEIGHT = 1.62
ENEMY_CLOSE_DISTANCE = 15


def get_position_center(block_position):
    return np.around(block_position) + vectors.center if block_position is not None else None


def get_position_flat_center(block_position):
    return np.around(block_position) + vectors.flat_center if block_position is not None else None


def get_horizontal_distance(distance):
    return np.sqrt(distance[0] ** 2 + distance[2] ** 2)


def get_wanted_direction(move):
    if np.abs(move[2]) >= np.abs(move[0]):
        if move[2] > 0:
            wanted_direction = vectors.Direction.South
        else:
            wanted_direction = vectors.Direction.North
    else:
        if move[0] > 0:
            wanted_direction = vectors.Direction.East
        else:
            wanted_direction = vectors.Direction.West
    return wanted_direction


def get_yaw_from_vector(move):
    normalized_flat_move = normalize(flatten(move))

    south_angle = vectors.directionVector[vectors.Direction.South]
    dot_product_south = np.dot(normalized_flat_move, south_angle)

    east_angle = vectors.directionVector[vectors.Direction.East]
    dot_product_east = np.dot(normalized_flat_move, east_angle)

    cos_angle = np.clip(dot_product_south, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    angle = vectors.radians_to_degrees(angle)
    if dot_product_east > 0:
        angle = vectors.CIRCLE_DEGREES - angle
    return angle


def get_wanted_pitch(dist_direction, delta_y):
    pitch = -np.arctan(delta_y / dist_direction)
    return vectors.radians_to_degrees(pitch)


class Observer:
    def __init__(self, observation=None):
        self.observation = observation
        self.hits = {}

        self.lower_surroundings = self.get_surroundings(self.observation.pos_local_grid)
        self.upper_surroundings = self.get_surroundings(self.observation.pos_local_grid + vectors.up)
        self.upper_upper_surroundings = self.get_surroundings(self.observation.pos_local_grid + 2 * vectors.up)

    def get_surroundings(self, central_position):
        return {
            direction: self.get_grid_local_block(central_position + vectors.directionVector[direction])
            for direction in vectors.Direction
        }

    def get_grid_local_block(self, position):
        return self.observation.grid_local[tuple(position)] if self.observation.grid_local is not None else None

    def get_abs_pos_discrete(self):
        return np.floor(self.observation.abs_pos) if self.observation.abs_pos is not None else None

    def get_closest_block(self, block_type):
        abs_pos_discrete = self.get_abs_pos_discrete()
        if abs_pos_discrete is None:
            return None

        hits = self.get_hits(block_type)
        if hits is None:
            return None

        positions = np.argwhere(hits)
        if positions.size > 0:
            distances_vector = positions - self.observation.pos_local_grid
            distances = np.linalg.norm(distances_vector, axis=1)

            closest_vectors = distances_vector[(distances == min(distances))]
            closest_vectors_same_height = closest_vectors[(closest_vectors[:, 1] == 0)]
            # Prioritize same horizontal level
            closest = closest_vectors_same_height[0] if closest_vectors_same_height.size > 0 else closest_vectors[0]
            return abs_pos_discrete + closest
        else:
            return None

    def is_block_observable(self, block_type):
        hits = self.get_hits(block_type)
        return hits is not None and np.any(hits)

    def get_hits(self, material):
        if material in self.hits:
            return self.hits[material]
        elif self.observation.grid_local is None:
            return None
        else:
            variants = get_variants(material)
            ores = [ore for ore in (get_ore(variant) for variant in variants) if ore is not None]
            targets = variants + ores
            hits = np.isin(self.observation.grid_local, targets)

            self.hits[material] = hits
            return hits

    def get_first_block_downwards(self):
        abs_pos_discrete = self.get_abs_pos_discrete()
        if abs_pos_discrete is not None:
            check_position = np.copy(self.observation.pos_local_grid)
            while check_position[1] >= 0 and self.observation.grid_local[tuple(check_position)] in traversable:
                check_position -= vectors.up
            return abs_pos_discrete - self.observation.pos_local_grid + check_position
        else:
            return None

    def is_position_within_reach(self, position, reach=GATHERING_REACH):
        if position is not None:
            distance = self.get_distance_to_position(position)
            return distance is not None and np.linalg.norm(distance) <= reach
        return False

    def is_block_at_position(self, position, block):
        variants = get_variants(block)
        return self.get_block_at_position_from_global(position) in variants

    def get_block_at_position_from_local(self, position):
        distance = self.get_rounded_distance_to_position(position)
        if distance is not None:
            return self.observation.grid_local[tuple(self.observation.pos_local_grid + distance)]
        else:
            return None

    def get_block_at_position_from_global(self, position):
        grids_global = self.observation.mission_data.grids_global
        position_spec = next((spec for spec in grids_global if spec.contains_position(position)), None)
        if position_spec is not None:
            grid_global = self.observation.get_grid_global(position_spec)
            grid_position = position_spec.get_grid_position(position)
            return grid_global[grid_position] if grid_global is not None else None
        else:
            return None

    def get_rounded_distance_to_position(self, position):
        abs_pos_discrete = self.get_abs_pos_discrete()
        return (position - abs_pos_discrete).astype('int64') if abs_pos_discrete is not None else None

    def get_distance_to_position(self, position):
        abs_pos = self.observation.abs_pos
        return position - (abs_pos + EYE_HEIGHT * up) if abs_pos is not None and position is not None else None

    def is_looking_at_type(self, los_type):
        return self.observation.los_type == los_type

    def is_looking_at_discrete_position(self, discrete_position):
        if self.observation.los_hit_type == LineOfSightHitType.BLOCK:
            los_discrete_position = self.get_los_pos_discrete()
            return los_discrete_position is not None and np.all(discrete_position == los_discrete_position)
        else:
            return False

    def get_los_pos_discrete(self):
        if self.observation.los_pos is None:
            return None

        los_face = get_los_face(self.observation.los_pos, self.observation.yaw, self.observation.pitch)

        los_pos_discrete = np.floor(self.observation.los_pos)
        if los_face == vectors.BlockFace.East:
            los_pos_discrete[0] -= 1
        elif los_face == vectors.BlockFace.Up:
            los_pos_discrete[1] -= 1
        elif los_face == vectors.BlockFace.South:
            los_pos_discrete[2] -= 1
        return los_pos_discrete

    def get_weakest_animal(self, specie=None):
        # Get the weakest entity. If there are several, take the closest of them.
        if self.observation.abs_pos is None:
            return None

        def get_weakest_animal_min_key(animal):
            return not animal.is_specie(specie), animal.health, np.linalg.norm(animal.pos - self.observation.abs_pos)

        weakest_animal = min(self.observation.animals, key=get_weakest_animal_min_key)
        return weakest_animal if weakest_animal.is_specie(specie) else None

    def get_closest_enemy(self):
        return self.get_closest_enemy_to_position(self.observation.abs_pos)

    def get_closest_enemy_to_position(self, position):
        if position is not None and len(self.observation.enemies) != 0:
            return min(self.observation.enemies, key=lambda enemy: np.linalg.norm(enemy.position - position))
        else:
            return None

    def get_closest_enemy_to_agents(self):
        # Get the closest enemy to any agent. Prioritize enemies that are within range to this agent.
        closest_enemy = self.get_closest_enemy()
        if closest_enemy is not None:
            if np.linalg.norm(closest_enemy.position - self.observation.abs_pos) <= ENEMY_CLOSE_DISTANCE:
                return closest_enemy
        closest_enemies = self.get_closest_enemy_agent_positions_to_other_agents()
        if len(closest_enemies) > 0:
            enemy_agent_position = min(closest_enemies, key=lambda ea: np.linalg.norm(ea[0].position - ea[1]))
            if np.linalg.norm(enemy_agent_position[0].position - enemy_agent_position[1]) <= ENEMY_CLOSE_DISTANCE:
                return enemy_agent_position[0]
        return None

    def get_closest_enemy_agent_positions_to_other_agents(self):
        closest = [(self.get_closest_enemy_to_position(a.position), a.position) for a in self.observation.other_agents]
        closest_enemies = [enemy for enemy in closest if enemy is not None]
        return closest_enemies

    def is_enemy_nearby(self):
        closest_enemy = self.get_closest_enemy()
        if closest_enemy is not None:
            closest_distance = np.linalg.norm(closest_enemy.position - self.observation.abs_pos)
            if closest_distance <= ENEMY_CLOSE_DISTANCE:
                return True
        return False

    def is_enemy_near_any_agent(self):
        if self.is_enemy_nearby():
            return True
        else:
            return any(self.is_enemy_near_agent(agent) for agent in self.observation.other_agents)

    def is_enemy_near_agent(self, agent):
        enemy = self.get_closest_enemy_to_position(agent.position)
        return enemy is not None and np.linalg.norm(enemy.position - agent.position) <= ENEMY_CLOSE_DISTANCE

    def has_pickup_nearby(self, wanted):
        if self.observation.abs_pos is not None:
            variants = get_variants(wanted)
            return any(self.is_pickup_nearby(pickup, variants) for pickup in self.observation.pickups)
        else:
            return False

    def is_pickup_nearby(self, pickup, variants):
        if pickup.type in variants:
            return np.linalg.norm(pickup.position - self.observation.abs_pos) < PICKUP_NEARBY_DISTANCE_TOLERANCE
        else:
            return False

    def get_pickup_position(self, wanted):
        variants = get_variants(wanted)
        return next((p.get_centralized_position() for p in self.observation.pickups if p.type in variants), None)

    def is_stuck(self):
        if self.lower_surroundings is not None:
            return not self.lower_surroundings[vectors.Direction.Zero] in traversable + narrow
        else:
            return False

    def is_animal_observable(self, specie):
        return self.observation.animals and any(animal.type == specie for animal in self.observation.animals)

    def get_current_direction(self):
        for key, check_angle in vectors.directionAngle.items():
            diff = check_angle - self.observation.yaw
            if diff <= 0:
                diff += vectors.CIRCLE_DEGREES
            if diff <= DELTA_ANGLES or diff >= vectors.CIRCLE_DEGREES - DELTA_ANGLES:
                return key
        return vectors.Direction.South

    def get_turn_direction(self, distance):
        wanted_angle = get_yaw_from_vector(distance)

        diff = wanted_angle - self.observation.yaw
        if diff <= 0:
            diff += vectors.CIRCLE_DEGREES

        if diff <= YAW_TOLERANCE or diff >= vectors.CIRCLE_DEGREES - YAW_TOLERANCE:
            return 0
        else:
            half_circle = vectors.CIRCLE_DEGREES / 2
            return diff / half_circle if diff <= half_circle else (diff - vectors.CIRCLE_DEGREES) / half_circle

    def get_pitch_change(self, wanted_pitch):
        quarter_circle = vectors.CIRCLE_DEGREES / 4
        diff = self.observation.pitch - wanted_pitch
        return -MAX_PITCH * diff / quarter_circle if np.abs(diff) > PITCH_TOLERANCE else 0

    def get_flat_distance_to_center(self):
        return flatten(self.get_distance_to_position(get_position_flat_center(self.get_abs_pos_discrete())))

    def is_at_position(self, position):
        abs_pos_discrete = self.get_abs_pos_discrete()
        return position is not None and abs_pos_discrete is not None and np.array_equal(position, abs_pos_discrete)
