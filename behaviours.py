import numpy as np
from py_trees.behaviour import Behaviour
from py_trees.common import Status

from gathering import get_gathering_tools
from inventory import HOTBAR_SIZE
from observation import get_horizontal_distance, get_wanted_direction, get_yaw_from_direction, traversable, \
    round_move, get_yaw_from_vector
from utils import CIRCLE_DEGREES, Direction, rad_to_degrees

MAX_DELAY = 60
YAW_TOLERANCE = 5
PITCH_TOLERANCE = 3
MAX_PITCH = 0.5
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MOVE_THRESHOLD = 5
SAME_SPOT_Y_THRESHOLD = 2
EPSILON_ARRIVED_AT_POSITION = 0.05
MIN_MOVE_SPEED = 0.05
REACH = 3

FUEL_HOT_BAR_POSITION = 0
PICKAXE_HOT_BAR_POSITION = 5


def get_move_speed(horizontal_distance):
    if horizontal_distance >= MOVE_THRESHOLD:
        return 1
    else:
        return max(horizontal_distance / MOVE_THRESHOLD, MIN_MOVE_SPEED)


def get_pitch_change(pitch, wanted_pitch):
    quarter_circle = CIRCLE_DEGREES / 4
    diff = pitch - wanted_pitch
    print(diff)
    if np.abs(diff) <= PITCH_TOLERANCE:
        return 0
    else:
        return -MAX_PITCH * diff / quarter_circle


def get_wanted_pitch(dist_direction, distY):
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
    def __init__(self, agent, item, amount=1):
        super(Craft, self).__init__("Craft {0}x {1}".format(amount, item))
        self.agent = agent
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS

        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        self.agent.craft(self.item)
        return Status.SUCCESS


class Melt(Behaviour):
    def __init__(self, agent, item, amount=1):
        super(Melt, self).__init__("Melt {0}x {1}".format(amount, item))
        self.agent = agent
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS

        fuel = self.agent.inventory.get_fuel()
        if not fuel:
            return Status.FAILURE

        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        fuel_position = self.agent.observation.inventory.find_item(fuel)
        if fuel_position != FUEL_HOT_BAR_POSITION:
            self.agent.swap_items(fuel_position, FUEL_HOT_BAR_POSITION)
        self.agent.craft(self.item)
        return Status.SUCCESS


class Equip(Behaviour):
    def __init__(self, agent, item):
        super(Equip, self).__init__("Equip " + item)
        self.agent = agent
        self.item = item

    def update(self):
        if self.agent.inventory.has_item(self.item):
            self.find_and_equip_item(self.agent.observation, self.item)
            return Status.SUCCESS

        return Status.FAILURE

    def find_and_equip_item(self, observation, item):
        position = observation.inventory.find_item(item)
        print("pos", position)
        if position >= HOTBAR_SIZE:
            self.agent.swap_items(position, PICKAXE_HOT_BAR_POSITION)
            position = PICKAXE_HOT_BAR_POSITION

        self.agent.select_on_hotbar(position)


class JumpIfStuck(Behaviour):
    def __init__(self, agent):
        super(JumpIfStuck, self).__init__("JumpIfStuck")
        self.agent = agent

    def update(self):
        if self.agent.observation.is_stuck():
            self.agent.jump(True)
        else:
            self.agent.jump(False)
        return Status.SUCCESS


class GoToObject(Behaviour):
    def __init__(self, agent, name):
        super(GoToObject, self).__init__(name)
        self.agent = agent

    def move_forward(self, horizontal_distance):
        self.agent.attack(False)

        move_speed = get_move_speed(horizontal_distance)
        self.agent.move(move_speed)

        pitch_req = get_pitch_change(self.agent.observation.pitch, 0)
        self.agent.pitch(pitch_req)

    def mine_forward(self, vertical_distance):
        self.agent.move(0)

        wantedPitch = get_wanted_pitch(1, vertical_distance - 1)
        pitch_req = get_pitch_change(self.agent.observation.pitch, wantedPitch)
        self.agent.pitch(pitch_req)
        self.agent.attack(pitch_req == 0)

    def can_jump(self, current_direction):
        free_above = self.agent.observation.upper_upper_surroundings[Direction.Zero] in traversable
        free_above_direction = self.agent.observation.upper_upper_surroundings[current_direction] in traversable
        return free_above and free_above_direction

    def jump_forward(self):
        self.agent.attack(False)
        self.agent.move(1)
        self.agent.jump(True)


class PickupItem(GoToObject):
    def __init__(self, agent, item):
        super(PickupItem, self).__init__(agent, "Pick up " + str(item))
        self.item = item

    def update(self):
        distance = self.agent.observation.get_pickup_position(self.item)

        self.agent.jump(False)
        if distance is None:
            return Status.FAILURE

        self.agent.move(0)

        wanted_direction = get_wanted_direction(distance)
        current_direction = self.agent.observation.get_current_direction()
        turn_direction = get_turn_direction(self.agent.observation.yaw, get_yaw_from_direction(wanted_direction))
        self.agent.turn(turn_direction)

        if turn_direction != 0:
            self.agent.attack(False)
            return Status.RUNNING
        # Move towards
        mat_horizontal_distance = get_horizontal_distance(distance)
        if not self.agent.observation.upper_surroundings[current_direction] in traversable:
            self.mine_forward(1)
        elif not self.agent.observation.lower_surroundings[current_direction] in traversable:
            if self.can_jump(current_direction):
                self.jump_forward()
            else:
                self.mine_forward(0)
        else:
            self.move_forward(mat_horizontal_distance)

        if self.agent.observation.get_pickup_position(self.item) is None:
            return Status.SUCCESS
        else:
            return Status.RUNNING


class GoToMaterial(GoToObject):
    def __init__(self, agent, material):
        super(GoToMaterial, self).__init__(agent, "Go to " + str(material))
        self.agent = agent
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):
        distance = self.agent.observation.get_closest(self.material)
        self.agent.jump(False)

        if distance is None:
            return Status.FAILURE

        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        if has_arrived(distance):
            return Status.SUCCESS

        self.agent.move(0)

        wanted_direction = get_wanted_direction(distance)
        current_direction = self.agent.observation.get_current_direction()
        print("cy", self.agent.observation.yaw)
        print("wy", get_yaw_from_direction(wanted_direction))
        turn_direction = get_turn_direction(self.agent.observation.yaw, get_yaw_from_direction(wanted_direction))
        self.agent.turn(turn_direction)

        if turn_direction != 0:
            self.agent.attack(False)
            return Status.RUNNING
        # Move towards
        mat_horizontal_distance = get_horizontal_distance(distance)
        if not has_arrived(distance):
            if not self.agent.observation.upper_surroundings[current_direction] in traversable:
                self.mine_forward(1)
            elif not self.agent.observation.lower_surroundings[current_direction] in traversable:
                if super().can_jump(current_direction):
                    self.jump_forward()
                else:
                    self.mine_forward(0)
            else:
                self.move_forward(mat_horizontal_distance)

            return Status.RUNNING

        return Status.SUCCESS


class MineMaterial(Behaviour):
    def __init__(self, agent, material):
        super(MineMaterial, self).__init__("Mine " + str(material))
        self.agent = agent
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):
        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        distance = self.agent.observation.get_closest(self.material)
        if distance is None:
            return Status.FAILURE

        if not has_arrived(distance):
            return Status.FAILURE

        # Look at
        self.agent.jump(False)
        self.agent.move(0)

        pitching = self.pitch_towards(distance)
        turning = self.turn_towards(distance)

        if pitching or turning:
            self.agent.attack(False)
            return Status.RUNNING

        self.agent.attack(True)
        target_grid_point = tuple(self.agent.observation.pos + round_move(distance))
        if self.agent.observation.grid[target_grid_point] != 'air':
            return Status.RUNNING

        self.agent.attack(False)
        return Status.SUCCESS

    def pitch_towards(self, distance):
        mat_horizontal_distance = get_horizontal_distance(distance)
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + distance[1])
        current_pitch = self.agent.observation.pitch
        pitch_req = get_pitch_change(current_pitch, wanted_pitch)
        self.agent.pitch(pitch_req)
        return pitch_req != 0

    def turn_towards(self, distance):
        wanted_yaw = get_yaw_from_vector(distance)
        current_yaw = self.agent.observation.yaw
        turn_direction = get_turn_direction(current_yaw, wanted_yaw)
        self.agent.turn(turn_direction)
        return turn_direction != 0


# TODO: Refactor to "LookForMaterial" Which will be an exploratory step when looking for materials
# First it will dig down to a correct height then start digging sideways.
class DigDownwardsToMaterial(Behaviour):
    PITCH_DOWNWARDS = 90

    def __init__(self, agent, material):
        super(DigDownwardsToMaterial, self).__init__("Dig downwards to " + str(material))
        self.agent = agent
        self.material = material
        self.tool = get_gathering_tools(material)

    def update(self):
        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        distance = self.agent.observation.get_closest(self.material)

        if distance is not None:
            return Status.SUCCESS

        self.agent.move(0)

        wanted_pitch = DigDownwardsToMaterial.PITCH_DOWNWARDS
        current_pitch = self.agent.observation.pitch
        pitch_req = get_pitch_change(current_pitch, wanted_pitch)
        self.agent.pitch(pitch_req)

        if pitch_req != 0:
            return Status.RUNNING

        self.agent.attack(True)

        return Status.SUCCESS
