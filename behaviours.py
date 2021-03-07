import time
import numpy as np

from inventory import HOTBAR_SIZE
from observation import not_stuck, get_horizontal_distance, get_wanted_direction, get_wanted_angle
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from utils import get_gathering_tools

MAX_DELAY = 60
YAW_TOLERANCE = 5
PITCH_TOLERANCE = 10
MAX_PITCH = 0.5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MOVE_THRESHOLD = 5

PICKAXE_HOT_BAR_POSITION = 5


def get_move_speed(horizontal_distance):
    if horizontal_distance >= MOVE_THRESHOLD:
        return 1
    elif horizontal_distance <= 1:
        return 0
    else:
        return (horizontal_distance - 1) / (MOVE_THRESHOLD - 1)


def get_pitch_change(pitch, wanted_pitch):
    quarter_circle = CIRCLE_DEGREES / 4
    diff = pitch - wanted_pitch
    print(diff)
    if np.abs(diff) <= PITCH_TOLERANCE:
        return 0
    else:
        return -MAX_PITCH * diff / quarter_circle


def get_wanted_pitch(dist_direction, distY):
    half_circle = CIRCLE_DEGREES / 2

    return -np.arctan(distY / dist_direction) * half_circle / np.pi


def get_turn_direction(yaw, wanted_direction):
    diff = get_wanted_angle(wanted_direction) - yaw
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


class Craft(Behaviour):
    def __init__(self, agent_host, item, amount=1):
        super(Craft, self).__init__("Craft " + item)
        self.agent_host = agent_host
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent_host.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS

        if self.has_ingredients():
            self.agent_host.sendCommand("craft " + self.item)
            return Status.SUCCESS

        return Status.FAILURE

    def has_ingredients(self):
        ingredients = self.agent_host.recipes.get_ingredients(self.item)

        for ingredient in ingredients:
            if not self.agent_host.inventory.has_item(ingredient.item, ingredient.amount):
                return False
        return True


class Equip(Behaviour):
    def __init__(self, agent_host, item):
        super(Equip, self).__init__("Equip " + item)
        self.agent_host = agent_host
        self.item = item

    def update(self):
        if self.agent_host.inventory.has_item(self.item):
            self.find_and_equip_item(self.agent_host.observation, self.item)
            return Status.SUCCESS

        return Status.FAILURE

    def find_and_equip_item(self, observation, item):
        position = observation.inventory.find_item(item)
        if position > HOTBAR_SIZE:
            self.agent_host.sendCommand("swapInventoryItems " + str(position) + " " + str(PICKAXE_HOT_BAR_POSITION))
            position = PICKAXE_HOT_BAR_POSITION

        self.agent_host.sendCommand("hotbar.{0} 1".format(str(position + 1)))  # press
        self.agent_host.sendCommand("hotbar.{0} 0".format(str(position + 1)))  # release
        time.sleep(0.1)


class JumpIfStuck(Behaviour):
    def __init__(self, agent_host):
        super(JumpIfStuck, self).__init__("JumpIfStuck")
        self.agent_host = agent_host

    def update(self):
        if self.agent_host.observation.is_stuck():
            self.agent_host.sendCommand("jump 1")
        else:
            self.agent_host.sendCommand("jump 0")
        return Status.SUCCESS


class GoToMaterial(Behaviour):
    def __init__(self, agent_host, material):
        super(GoToMaterial, self).__init__("Go to " + str(material))
        self.agent_host = agent_host
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):
        # Use fallback for this

        move = self.agent_host.observation.get_closest(self.material)

        if move is None:
            return Status.FAILURE

        if self.tool is not None and not self.agent_host.inventory.has_item(self.tool):
            return Status.FAILURE

        wanted_direction = get_wanted_direction(move)
        current_direction = self.agent_host.observation.get_current_direction()

        # Turn correct direction
        turn_direction = get_turn_direction(self.agent_host.observation.yaw, wanted_direction)
        self.agent_host.sendCommand("move 0")
        self.agent_host.sendCommand("turn " + str(turn_direction))

        if turn_direction != 0:
            return Status.RUNNING

        # Move towards
        mat_horizontal_distance = get_horizontal_distance(move)
        if np.abs(move[1]) >= 4 or mat_horizontal_distance > 1:
            if not self.agent_host.observation.upper_surroundings[current_direction] in not_stuck:
                wantedPitch = get_wanted_pitch(1, 0)
                self.agent_host.sendCommand("move 0")
                pitch_req = get_pitch_change(self.agent_host.observation.pitch, wantedPitch)
                self.agent_host.sendCommand("pitch " + str(pitch_req))
                if pitch_req == 0:
                    self.agent_host.sendCommand("attack 1")
                else:
                    self.agent_host.sendCommand("attack 0")
                print("PITCH CHANGE TOP", pitch_req)
            elif not self.agent_host.observation.lower_surroundings[current_direction] in not_stuck:
                wantedPitch = get_wanted_pitch(1, -1)
                self.agent_host.sendCommand("move 0")
                pitch_req = get_pitch_change(self.agent_host.observation.pitch, wantedPitch)
                self.agent_host.sendCommand("pitch " + str(pitch_req))
                if pitch_req == 0:
                    self.agent_host.sendCommand("attack 1")
                else:
                    self.agent_host.sendCommand("attack 0")
                print("PITCH CHANGE BOTTOM", pitch_req)
            else:
                move_speed = get_move_speed(mat_horizontal_distance)
                pitch_req = get_pitch_change(self.agent_host.observation.pitch, 0)
                self.agent_host.sendCommand("pitch " + str(pitch_req))
                self.agent_host.sendCommand("move " + str(move_speed))
                self.agent_host.sendCommand("attack 0")

        if mat_horizontal_distance > 1:
            return Status.RUNNING

        return Status.SUCCESS


class MineMaterial(Behaviour):
    def __init__(self, agent_host, material):
        super(MineMaterial, self).__init__("Mine " + str(material))
        self.agent_host = agent_host
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):
        # Use fallback for this

        move = self.agent_host.observation.get_closest(self.material)

        if move is None:
            return Status.FAILURE

        if self.tool is not None and not self.agent_host.inventory.has_item(self.tool):
            return Status.FAILURE

        mat_horizontal_distance = get_horizontal_distance(move)

        if mat_horizontal_distance > 1:
            return Status.FAILURE

        # Look at
        self.agent_host.sendCommand("move 0")
        wantedPitch = get_wanted_pitch(mat_horizontal_distance, -1 + move[1])
        pitch_req = get_pitch_change(self.agent_host.observation.pitch, wantedPitch)
        self.agent_host.sendCommand("pitch " + str(pitch_req))
        print("PITCH CHANGE", pitch_req)

        if pitch_req != 0:
            return Status.RUNNING

        # Mine
        self.agent_host.sendCommand("attack 1")
        if self.agent_host.observation.grid[tuple(self.agent_host.observation.pos + move)] != 'air':
            return Status.RUNNING

        return Status.SUCCESS
