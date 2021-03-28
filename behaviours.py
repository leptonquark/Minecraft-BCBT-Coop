import time
import numpy as np

from inventory import HOTBAR_SIZE
from observation import get_horizontal_distance, get_wanted_direction, get_wanted_angle, not_stuck, round_move, \
    get_exact_wanted_angle
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from gathering import get_gathering_tools
from utils import CIRCLE_DEGREES, rad_to_degrees

MAX_DELAY = 60
YAW_TOLERANCE = 5
PITCH_TOLERANCE = 3
MAX_PITCH = 0.5
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MOVE_THRESHOLD = 5
SAME_SPOT_Y_THRESHOLD = 2
EPSILON_ARRIVED_AT_POSITION = 0.05
REACH = 3

FUEL_HOT_BAR_POSITION = 0
PICKAXE_HOT_BAR_POSITION = 5

CRAFT_SLEEP = 0.25


def get_move_speed(horizontal_distance):
    if horizontal_distance >= MOVE_THRESHOLD:
        return 1
    else:
        return horizontal_distance / MOVE_THRESHOLD


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
    pitch = -np.arctan(distY / dist_direction)
    return rad_to_degrees(pitch)


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


def has_arrived(move):
    mat_horizontal_distance = get_horizontal_distance(move)
    y_distance = move[1]
    return (np.abs(y_distance) <= SAME_SPOT_Y_THRESHOLD and mat_horizontal_distance <= REACH) \
           or mat_horizontal_distance <= EPSILON_ARRIVED_AT_POSITION


class Craft(Behaviour):
    def __init__(self, agent_host, item, amount=1):
        super(Craft, self).__init__("Craft {0}x {1}".format(amount, item))
        self.agent_host = agent_host
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent_host.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS

        if self.agent_host.inventory.has_ingredients(self.item):
            self.agent_host.sendCommand("craft " + self.item)
            time.sleep(CRAFT_SLEEP)
            return Status.RUNNING

        return Status.FAILURE


class Melt(Behaviour):
    def __init__(self, agent_host, item, amount=1):
        super(Melt, self).__init__("Melt {0}x {1}".format(amount, item))
        self.agent_host = agent_host
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent_host.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS

        fuel = self.agent_host.inventory.get_fuel()
        if not fuel:
            return Status.FAILURE

        if not self.agent_host.inventory.has_ingredients(self.item):
            return Status.FAILURE

        fuel_position = self.agent_host.observation.inventory.find_item(fuel)
        if fuel_position != FUEL_HOT_BAR_POSITION:
            self.agent_host.sendCommand("swapInventoryItems " + str(fuel_position) + " " + str(FUEL_HOT_BAR_POSITION))
            time.sleep(0.25)
        self.agent_host.sendCommand("craft " + self.item)
        time.sleep(CRAFT_SLEEP)
        return Status.SUCCESS


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
        print("pos", position)
        if position >= HOTBAR_SIZE:
            self.agent_host.sendCommand("swapInventoryItems " + str(position) + " " + str(PICKAXE_HOT_BAR_POSITION))
            position = PICKAXE_HOT_BAR_POSITION
            time.sleep(0.25)

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
        move = self.agent_host.observation.get_closest(self.material)

        if move is None:
            return Status.FAILURE

        if self.tool is not None and not self.agent_host.inventory.has_item(self.tool):
            return Status.FAILURE

        if has_arrived(move):
            return Status.SUCCESS

        wanted_direction = get_wanted_direction(move)
        current_direction = self.agent_host.observation.get_current_direction()
        # Turn correct direction
        turn_direction = get_turn_direction(self.agent_host.observation.yaw, get_wanted_angle(wanted_direction))
        self.agent_host.sendCommand("move 0")
        self.agent_host.sendCommand("turn " + str(turn_direction))

        if turn_direction != 0:
            self.agent_host.sendCommand("attack 0")
            return Status.RUNNING

        # Move towards
        mat_horizontal_distance = get_horizontal_distance(move)
        if not has_arrived(move):
            if not self.agent_host.observation.upper_surroundings[current_direction] in not_stuck:
                self.mine_forward(1)
            elif not self.agent_host.observation.lower_surroundings[current_direction] in not_stuck:
                self.mine_forward(0)
            else:
                self.move_forward(mat_horizontal_distance)

            return Status.RUNNING

        return Status.SUCCESS

    def move_forward(self, horizontal_distance):
        move_speed = get_move_speed(horizontal_distance)
        pitch_req = get_pitch_change(self.agent_host.observation.pitch, 0)
        self.agent_host.sendCommand("pitch " + str(pitch_req))
        self.agent_host.sendCommand("move " + str(move_speed))
        self.agent_host.sendCommand("attack 0")

    def mine_forward(self, vertical_distance):
        wantedPitch = get_wanted_pitch(1, vertical_distance - 1)
        self.agent_host.sendCommand("move 0")
        pitch_req = get_pitch_change(self.agent_host.observation.pitch, wantedPitch)
        self.agent_host.sendCommand("pitch " + str(pitch_req))
        if pitch_req == 0:
            self.agent_host.sendCommand("attack 1")
        else:
            self.agent_host.sendCommand("attack 0")


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
        print("mat horizontal distance", mat_horizontal_distance)

        if not has_arrived(move):
            return Status.FAILURE

        # Look at
        self.agent_host.sendCommand("move 0")
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + move[1])
        print("wanted pitch", wanted_pitch)
        print("current pitch", self.agent_host.observation.pitch)
        pitch_req = get_pitch_change(self.agent_host.observation.pitch, wanted_pitch)
        self.agent_host.sendCommand("pitch " + str(pitch_req))

        wanted_angle = get_exact_wanted_angle(move)
        print("wanted angle", wanted_angle)
        print("current angle", self.agent_host.observation.yaw)
        turn_direction = get_turn_direction(self.agent_host.observation.yaw, wanted_angle)
        self.agent_host.sendCommand("turn " + str(turn_direction))

        if pitch_req != 0 or turn_direction != 0:
            self.agent_host.sendCommand("attack 0")
            return Status.RUNNING

        # Mine
        self.agent_host.sendCommand("attack 1")
        target_grid_point = tuple(self.agent_host.observation.pos + round_move(move))
        if self.agent_host.observation.grid[target_grid_point] != 'air':
            return Status.RUNNING

        self.agent_host.sendCommand("attack 0")
        return Status.SUCCESS


# TODO: Refactor to "LookForMaterial" Which will be an exploratory step when looking for materials
# First it will dig down to a correct height then start digging sideways.
class DigDownwardsToMaterial(Behaviour):
    PITCH_DOWNWARDS = 90

    def __init__(self, agent_host, material):
        super(DigDownwardsToMaterial, self).__init__("Dig downwards to " + str(material))
        self.agent_host = agent_host
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):

        if self.tool is not None and not self.agent_host.inventory.has_item(self.tool):
            return Status.FAILURE

        move = self.agent_host.observation.get_closest(self.material)

        if move is not None:
            return Status.SUCCESS

        self.agent_host.sendCommand("move 0")
        wanted_pitch = DigDownwardsToMaterial.PITCH_DOWNWARDS

        pitch_req = get_pitch_change(self.agent_host.observation.pitch, wanted_pitch)
        self.agent_host.sendCommand("pitch " + str(pitch_req))

        if pitch_req != 0:
            return Status.RUNNING

        # Mine
        self.agent_host.sendCommand("attack 1")

        return Status.SUCCESS


class MineMaterialOld(Behaviour):
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
        print("mat horizontal distance", mat_horizontal_distance)

        if not has_arrived(move):
            return Status.FAILURE

        # Look at
        self.agent_host.sendCommand("move 0")
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + move[1])
        print("wanted pitch", wanted_pitch)
        print("current pitch", self.agent_host.observation.pitch)

        pitch_req = get_pitch_change(self.agent_host.observation.pitch, wanted_pitch)
        self.agent_host.sendCommand("pitch " + str(pitch_req))

        if pitch_req != 0:
            self.agent_host.sendCommand("attack 0")
            return Status.RUNNING

        # Mine
        self.agent_host.sendCommand("attack 1")
        target_grid_point = tuple(self.agent_host.observation.pos + round_move(move))
        if self.agent_host.observation.grid[target_grid_point] != 'air':
            return Status.RUNNING

        self.agent_host.sendCommand("attack 0")
        return Status.SUCCESS
