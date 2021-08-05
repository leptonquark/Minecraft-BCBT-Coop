import numpy as np

from malmoutils.commands import CommandInterface
from items import effects
from world.observation import get_horizontal_distance, get_turn_direction, get_wanted_pitch, get_yaw_from_vector, \
    get_pitch_change

PITCH_DOWNWARDS = 90
MOVE_THRESHOLD = 5
MIN_MOVE_SPEED = 0.05
NO_MOVE_SPEED_DISTANCE_EPSILON = 1
NO_MOVE_SPEED_TURN_DIRECTION_EPSILON = 0.1


def get_move_speed(horizontal_distance, turn_direction):
    move_speed = horizontal_distance / MOVE_THRESHOLD if horizontal_distance < MOVE_THRESHOLD else 1
    move_speed *= (1 - np.abs(turn_direction)) ** 2
    move_speed = max(move_speed, MIN_MOVE_SPEED)
    if np.abs(turn_direction) > NO_MOVE_SPEED_TURN_DIRECTION_EPSILON and horizontal_distance < NO_MOVE_SPEED_DISTANCE_EPSILON:
        move_speed = 0
    return move_speed


class MinerAgent:

    def __init__(self):
        self.interface = CommandInterface()
        self.observation = None
        self.inventory = None

    def get_agent_host(self):
        return self.interface.agent_host

    def set_observation(self, observation):
        self.observation = observation
        if observation:
            self.inventory = observation.inventory

    def get_world_state(self):
        return self.interface.get_world_state()

    def move_forward(self, horizontal_distance, turn_direction):
        self.interface.attack(False)

        move_speed = get_move_speed(horizontal_distance, turn_direction)
        self.interface.move(move_speed)

        pitch_req = get_pitch_change(self.observation.pitch, 0)
        self.interface.pitch(pitch_req)

    def turn_towards(self, distance):
        wanted_yaw = get_yaw_from_vector(distance)
        current_yaw = self.observation.yaw
        turn_direction = get_turn_direction(current_yaw, wanted_yaw)
        self.interface.turn(turn_direction)
        return turn_direction != 0

    def get_turn_direction(self, distance):
        return get_turn_direction(self.observation.yaw, get_yaw_from_vector(distance))

    def pitch_towards(self, distance):
        mat_horizontal_distance = get_horizontal_distance(distance)
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + distance[1])
        current_pitch = self.observation.pitch
        pitch_req = get_pitch_change(current_pitch, wanted_pitch)
        self.interface.pitch(pitch_req)
        return pitch_req != 0

    def pitch_downwards(self):
        wanted_pitch = PITCH_DOWNWARDS
        current_pitch = self.observation.pitch
        pitch_req = get_pitch_change(current_pitch, wanted_pitch)
        self.interface.pitch(pitch_req)
        return pitch_req == 0

    def activate_night_vision(self):
        self.interface.activate_effect(effects.NIGHT_VISION, effects.MAX_TIME, effects.MAX_AMPLIFIER)

    #TODO Jump, Attack, Move, Turn, Select on Hotbar, Swap Items and Pitch should probably be removed
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

    def craft(self, item, amount=1):
        for _ in range(amount):
            self.interface.craft(item)

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

    def start_mission(self, mission, pool, mission_record, experiment_id):
        self.interface.start_mission(mission, pool, mission_record, experiment_id)
