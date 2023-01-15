import time

import numpy as np

from items import effects
from items.inventory import HOTBAR_SIZE
from items.items import unclimbable, traversable, narrow
from malmoutils.interface import MalmoInterface
from mobs.enemies import ENEMY_HEIGHT
from utils.vectors import RelativeDirection, directionVector, up, Direction, center, faceDistance, BlockFace
from world.observer import get_horizontal_distance, get_wanted_pitch, Observer, get_position_flat_center, \
    get_wanted_direction, get_position_center

PITCH_UPWARDS = -90
PITCH_DOWNWARDS = 90

DIG_VERTICAL_HORIZONTAL_TOLERANCE = 0.2
BLOCKED_BY_NARROW_THRESHOLD = 0.5
MOVE_THRESHOLD = 5
MIN_MOVE_SPEED = 0.05
NO_MOVE_SPEED_DISTANCE_EPSILON = 1
NO_MOVE_SPEED_TURN_DIRECTION_EPSILON = 0.1
STRAFE_SPEED = 0.3
MOVE_BACKWARD_SPEED = -0.2

FUEL_HOT_BAR_POSITION = 0
PICKAXE_HOT_BAR_POSITION = 5

WORLD_STATE_TIMEOUT = 10000


def get_move_speed(horizontal_distance, turn_direction):
    is_close_to_target = horizontal_distance < NO_MOVE_SPEED_DISTANCE_EPSILON
    is_large_turn = np.abs(turn_direction) > NO_MOVE_SPEED_TURN_DIRECTION_EPSILON
    if is_large_turn and is_close_to_target:
        return 0
    else:
        move_speed = horizontal_distance / MOVE_THRESHOLD if horizontal_distance < MOVE_THRESHOLD else 1
        move_speed *= (1 - np.abs(turn_direction)) ** 2
        return max(move_speed, MIN_MOVE_SPEED)


def get_face_position(discrete_position, face):
    return discrete_position + center + faceDistance[face]


class MinerAgent:

    def __init__(self, mission_data, blackboard, role):
        self.mission_data = mission_data
        self.blackboard = blackboard
        self.role = role
        self.name = self.mission_data.agent_names[self.role]
        self.interface = MalmoInterface()
        self.observer = None
        self.inventory = None

    def set_observation(self, observation):
        if observation:
            self.inventory = observation.inventory
            self.observer = Observer(observation)

    def jump(self, active):
        self.interface.jump(active)

    def attack(self, active):
        self.interface.attack(active)

    def move(self, intensity):
        self.interface.move(intensity)

    def pitch(self, intensity):
        self.interface.pitch(intensity)

    def turn(self, intensity):
        self.interface.turn(intensity)

    def strafe(self, intensity):
        self.interface.strafe(intensity)

    def move_forward(self, horizontal_distance, turn_direction):
        self.interface.attack(False)

        move_speed = get_move_speed(horizontal_distance, turn_direction)
        self.interface.move(move_speed)

        pitch_req = self.observer.get_pitch_change(0)
        self.interface.pitch(pitch_req)

    def move_backward(self):
        self.interface.attack(False)
        self.interface.move(MOVE_BACKWARD_SPEED)

    def turn_towards(self, distance):
        turn_direction = self.get_turn_direction(distance)
        self.interface.turn(turn_direction)
        return turn_direction != 0

    def get_turn_direction(self, distance):
        return self.observer.get_turn_direction(distance)

    def go_to_position(self, position):
        distance = self.observer.get_distance_to_position(position)
        if distance is None:
            return

        flat_distance = np.copy(distance)
        flat_distance[1] = 0

        if np.linalg.norm(flat_distance) <= DIG_VERTICAL_HORIZONTAL_TOLERANCE:
            self.mine_vertical(distance[1])
            return

        self.turn_towards(distance)

        self.strafe(0)
        at_narrow = self.observer.lower_surroundings[Direction.Zero] in narrow
        if at_narrow:
            avoiding = self.avoid_narrow(flat_distance)
            if avoiding:
                return

        turn_direction = self.get_turn_direction(distance)
        current_direction = self.observer.get_current_direction()
        lower_free = self.observer.lower_surroundings[current_direction] in traversable + narrow
        upper_free = self.observer.upper_surroundings[current_direction] in traversable
        at_same_discrete_position_horizontally = np.all(np.round(flat_distance) == 0)
        if at_same_discrete_position_horizontally or (lower_free and upper_free):
            self.move_forward(get_horizontal_distance(distance), turn_direction)
            return

        wanted_direction = get_wanted_direction(distance)
        if not upper_free:
            self.mine_forward(1, wanted_direction)
        elif not lower_free:
            if self.can_jump(wanted_direction):
                self.jump_forward(wanted_direction)
            else:
                self.mine_forward(0, wanted_direction)

    def mine_vertical(self, y_distance):
        if y_distance < 0:
            self.mine_downwards()
        else:
            self.mine_upwards()

    def look_at_block(self, discrete_position, face=BlockFace.NoFace):
        position_center = get_face_position(discrete_position, face)
        distance = self.observer.get_distance_to_position(position_center)
        if distance is None:
            return False
        if not self.observer.is_looking_at_discrete_position(discrete_position):
            self.attack(False)
            pitching = self.pitch_towards(distance)
            turning = self.turn_towards(distance)

            if pitching or turning:
                return False

        self.turn(0)
        self.pitch(0)
        return True

    def look_at_entity(self, entity):
        distance = self.observer.get_distance_to_position(entity.position)
        distance[1] += ENEMY_HEIGHT
        if not self.observer.is_looking_at_type(entity.type):
            pitching = self.pitch_towards(distance)
            turning = self.turn_towards(distance)
            if pitching or turning:
                self.attack(False)
                return False
        return True

    def pitch_towards(self, distance):
        horizontal_distance = get_horizontal_distance(distance)
        wanted_pitch = get_wanted_pitch(horizontal_distance, distance[1])
        pitch_req = self.observer.get_pitch_change(wanted_pitch)
        self.interface.pitch(pitch_req)
        return pitch_req != 0

    def pitch_downwards(self):
        pitch_req = self.observer.get_pitch_change(PITCH_DOWNWARDS)
        self.interface.pitch(pitch_req)
        return pitch_req == 0

    def pitch_upwards(self):
        pitch_req = self.observer.get_pitch_change(PITCH_UPWARDS)
        self.interface.pitch(pitch_req)
        return pitch_req == 0

    def avoid_narrow(self, flat_distance):
        abs_pos_discrete = self.observer.get_abs_pos_discrete()
        if abs_pos_discrete is None:
            return False

        flat_center = get_position_flat_center(abs_pos_discrete)
        distance_to_center = self.observer.get_distance_to_position(flat_center)
        flat_distance_to_center = np.copy(distance_to_center)
        flat_distance_to_center[1] = 0
        normalized_flat_distance = flat_distance / np.linalg.norm(flat_distance)
        normalized_flat_distance_to_center = flat_distance_to_center / np.linalg.norm(flat_distance_to_center)
        block_factor = np.dot(normalized_flat_distance_to_center, normalized_flat_distance)
        if block_factor >= BLOCKED_BY_NARROW_THRESHOLD:
            distance_perpendicular = np.array([normalized_flat_distance[2], 0, -normalized_flat_distance[0]])
            go_right = np.dot(distance_perpendicular, normalized_flat_distance_to_center) > 0
            direction = RelativeDirection.Right if go_right else RelativeDirection.Left
            self.strafe_by_direction(direction)
            return True
        else:
            return False

    def strafe_by_direction(self, direction):
        strafe = STRAFE_SPEED if direction == RelativeDirection.Right else -STRAFE_SPEED
        self.interface.strafe(strafe)

    def mine_forward(self, vertical_distance, wanted_direction):
        abs_pos_discrete = self.observer.get_abs_pos_discrete()
        if abs_pos_discrete is None:
            return
        distance_to_block = directionVector[wanted_direction] + vertical_distance * up
        block_position = abs_pos_discrete + distance_to_block
        block_center = get_position_center(block_position)
        distance_to_block = self.observer.get_distance_to_position(block_center)
        self.turn(0)
        self.pitch(0)
        self.move(0)
        if not self.observer.is_looking_at_discrete_position(block_position):
            turning = self.turn_towards(distance_to_block)
            pitching = self.pitch_towards(distance_to_block)

            if turning or pitching:
                self.attack(False)
                self.move(0)
                return

        self.attack(True)

    def mine_upwards(self):
        self.move(0)
        looking_upwards = self.pitch_upwards()
        self.attack(looking_upwards)

    def mine_downwards(self):
        self.move(0)
        looking_downwards = self.pitch_downwards()
        self.attack(looking_downwards)

    def can_jump(self, current_direction):
        climbable_below = self.observer.lower_surroundings[current_direction] not in unclimbable

        free_above = self.observer.upper_upper_surroundings[Direction.Zero] in traversable
        free_above_direction = self.observer.upper_upper_surroundings[current_direction] in traversable

        return climbable_below and free_above and free_above_direction

    def jump_forward(self, wanted_direction):
        self.attack(False)
        self.pitch(0)

        turn_direction = self.get_turn_direction(directionVector[wanted_direction])
        self.turn(turn_direction)
        if turn_direction != 0:
            self.move(0)
        else:
            self.move(1)
            self.jump(True)

    def activate_night_vision(self):
        self.interface.activate_effect(effects.NIGHT_VISION, effects.MAX_TIME, effects.MAX_AMPLIFIER)

    def craft(self, item, amount=1):
        variants = self.inventory.get_variants(item)
        variant = variants[0] if len(variants) > 0 else None
        for _ in range(amount):
            self.interface.craft(item, variant)

    def melt(self, item, fuel, amount=1):
        fuel_position = self.inventory.find_item(fuel)
        if fuel_position != FUEL_HOT_BAR_POSITION:
            self.swap_items(fuel_position, FUEL_HOT_BAR_POSITION)
            time.sleep(0.2)
        self.craft(item, amount)

    def select_on_hotbar(self, position):
        self.interface.select_on_hotbar(position)

    def swap_items(self, position1, position2):
        self.interface.swap_items(position1, position2)

    def place_block(self):
        self.interface.discrete_use()

    def stop(self):
        self.interface.attack(False)
        self.interface.jump(False)
        self.interface.move(0)
        self.interface.pitch(0)
        self.interface.turn(0)

    def equip_item(self, item):
        position = self.inventory.find_item(item)
        if position is not None and position >= HOTBAR_SIZE:
            self.swap_items(position, PICKAXE_HOT_BAR_POSITION)
            position = PICKAXE_HOT_BAR_POSITION

        self.select_on_hotbar(position)

    def equip_best_pickaxe(self, tier):
        pickaxe = self.inventory.get_best_pickaxe(tier)
        self.equip_item(pickaxe)

    def has_pickaxe_by_minimum_tier(self, tier):
        return self.inventory.has_pickaxe_by_minimum_tier(tier)

    def has_best_pickaxe_by_minimum_tier_equipped(self, tier):
        return self.inventory.has_best_pickaxe_by_minimum_tier_equipped(tier)

    def start_mission(self):
        self.interface.start_multi_agent_mission(self.mission_data, self.role)

    def wait_for_mission(self):
        self.interface.wait_for_mission()

    def quit(self):
        self.interface.quit()

    def get_next_world_state(self):
        observations = None
        world_state = None
        start_time = time.time()
        while observations is None or len(observations) == 0:
            world_state = self.interface.get_world_state()
            observations = world_state.observations
            if WORLD_STATE_TIMEOUT is not None and time.time() - start_time > WORLD_STATE_TIMEOUT:
                print("Getting World State timed out")
                return None
        return world_state
