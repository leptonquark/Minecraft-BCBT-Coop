import time

import numpy as np

from items import effects
from items.inventory import HOTBAR_SIZE
from malmoutils.interface import MalmoInterface
from utils.vectors import RelativeDirection
from world.observer import get_horizontal_distance, get_wanted_pitch, Observer, get_position_flat_center

PITCH_UPWARDS = -90
PITCH_DOWNWARDS = 90

BLOCKED_BY_NARROW_THRESHOLD = 0.5
MOVE_THRESHOLD = 5
MIN_MOVE_SPEED = 0.05
NO_MOVE_SPEED_DISTANCE_EPSILON = 1
NO_MOVE_SPEED_TURN_DIRECTION_EPSILON = 0.1
STRAFE_SPEED = 0.3
MOVE_BACKWARD_SPEED = -0.2

FUEL_HOT_BAR_POSITION = 0
PICKAXE_HOT_BAR_POSITION = 5

WORLD_STATE_TIMEOUT = 10


def get_move_speed(horizontal_distance, turn_direction):
    move_speed = horizontal_distance / MOVE_THRESHOLD if horizontal_distance < MOVE_THRESHOLD else 1
    move_speed *= (1 - np.abs(turn_direction)) ** 2
    move_speed = max(move_speed, MIN_MOVE_SPEED)

    is_close_to_target = horizontal_distance < NO_MOVE_SPEED_DISTANCE_EPSILON
    is_large_turn = np.abs(turn_direction) > NO_MOVE_SPEED_TURN_DIRECTION_EPSILON
    if is_large_turn and is_close_to_target:
        move_speed = 0
    return move_speed


class MinerAgent:

    def __init__(self, blackboard, name="SteveBot"):
        self.name = name
        self.blackboard = blackboard
        self.interface = MalmoInterface()
        self.observer = None
        self.inventory = None

    def set_observation(self, observation):
        if observation:
            self.inventory = observation.inventory
            self.observer = Observer(observation)

    def get_world_state(self):
        return self.interface.get_world_state()

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

    def pitch_towards(self, distance):
        mat_horizontal_distance = get_horizontal_distance(distance)
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + distance[1])
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
        flat_center = get_position_flat_center(self.observer.get_abs_pos_discrete())
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
        if direction == RelativeDirection.Right:
            self.interface.strafe(STRAFE_SPEED)
        else:
            self.interface.strafe(-STRAFE_SPEED)

    def activate_night_vision(self):
        self.interface.activate_effect(effects.NIGHT_VISION, effects.MAX_TIME, effects.MAX_AMPLIFIER)

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

    def craft(self, item, amount=1):
        variants = self.inventory.get_variants(item)
        if variants:
            variant = variants[0]
        else:
            variant = None

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

    def start_mission(self, mission, mission_record):
        self.interface.start_mission(mission, mission_record)

    def start_multi_agent_mission(self, mission_data, role):
        self.interface.start_multi_agent_mission(mission_data, role)

    def wait_for_mission(self):
        self.interface.wait_for_mission()

    def quit(self):
        self.interface.quit()

    def get_next_world_state(self):
        observations = None
        world_state = None
        start_time = time.time()
        while observations is None or len(observations) == 0:
            world_state = self.get_world_state()
            observations = world_state.observations
            if time.time() - start_time > WORLD_STATE_TIMEOUT:
                print("Getting World State timed out")
                return None
        return world_state
