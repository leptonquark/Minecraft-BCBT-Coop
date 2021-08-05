import numpy as np
from py_trees.behaviour import Behaviour
from py_trees.common import Status

from items import items
from items.gathering import get_gathering_tool
from items.inventory import HOTBAR_SIZE
from utils.constants import ATTACK_REACH
from utils.vectors import Direction, directionVector, down_vector
from world.observation import get_horizontal_distance, get_pitch_change, get_wanted_direction, get_wanted_pitch, \
    get_yaw_from_direction, get_yaw_from_vector, get_turn_direction, narrow, get_position_center, round_move, \
    traversable, unclimbable

MAX_DELAY = 60
STOP_TURN_DIRECTION_TOLERANCE = 0.1

DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5

FUEL_HOT_BAR_POSITION = 0
PICKAXE_HOT_BAR_POSITION = 5


class Action(Behaviour):
    def __init__(self, name):
        super(Action, self).__init__(name)


class Craft(Action):
    def __init__(self, agent, item, amount=1):
        super(Craft, self).__init__(f"Craft {item}")
        self.agent = agent
        self.amount = amount
        self.item = item

    def update(self):
        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        self.agent.craft(self.item, self.amount)
        return Status.SUCCESS


class Melt(Action):
    def __init__(self, agent, item, amount=1):
        super(Melt, self).__init__(f"Melt {amount}x {item}")
        self.agent = agent
        self.item = item
        self.amount = amount

    def update(self):
        fuel = self.agent.inventory.get_fuel()
        if fuel is None:
            return Status.FAILURE

        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        fuel_position = self.agent.observation.inventory.find_item(fuel)
        if fuel_position != FUEL_HOT_BAR_POSITION:
            self.agent.swap_items(fuel_position, FUEL_HOT_BAR_POSITION)

        self.agent.craft(self.item, self.amount)
        return Status.SUCCESS


class Equip(Action):
    def __init__(self, agent, item):
        super(Equip, self).__init__(f"Equip {item}")
        self.agent = agent
        self.item = item

    def update(self):
        if self.agent.inventory.has_item(self.item):
            self.equip_item(self.agent.observation, self.item)
            return Status.SUCCESS

        return Status.FAILURE

    def equip_item(self, observation, item):
        position = observation.inventory.find_item(item)
        if position >= HOTBAR_SIZE:
            self.agent.swap_items(position, PICKAXE_HOT_BAR_POSITION)
            position = PICKAXE_HOT_BAR_POSITION

        self.agent.select_on_hotbar(position)


class JumpIfStuck(Action):
    def __init__(self, agent):
        super(JumpIfStuck, self).__init__("JumpIfStuck")
        self.agent = agent

    def update(self):
        if self.agent.observation.is_stuck():
            self.agent.jump(True)
            return Status.RUNNING
        else:
            self.agent.jump(False)
            return Status.SUCCESS

    def terminate(self, new_status):
        self.agent.jump(False)


class GoToObject(Action):
    def __init__(self, agent, name):
        super(GoToObject, self).__init__(name)
        self.agent = agent

    def go_to_position(self, distance):
        flat_distance = np.copy(distance)
        flat_distance[1] = 0

        if np.linalg.norm(flat_distance) <= 1:
            self.mine_downwards()
            return Status.RUNNING


        self.agent.turn_towards(distance)

        turn_direction = self.agent.get_turn_direction(distance)
        current_direction = self.agent.observation.get_current_direction()

        lower_free = self.agent.observation.lower_surroundings[current_direction] in traversable + narrow
        upper_free = self.agent.observation.upper_surroundings[current_direction] in traversable

        if lower_free and upper_free:
            self.agent.move_forward(get_horizontal_distance(distance), turn_direction)

        else:
            wanted_direction = get_wanted_direction(distance)
            if not upper_free:
                self.mine_forward(1, wanted_direction)
            elif not lower_free:
                if self.can_jump(wanted_direction):
                    self.jump_forward(wanted_direction)
                else:
                    self.mine_forward(0, wanted_direction)

    def mine_downwards(self):
        looking_downwards = self.agent.pitch_downwards()
        if not looking_downwards:
            self.agent.attack(False)
            return
        self.agent.attack(True)

    def mine_forward(self, vertical_distance, wanted_direction):
        block_position = self.agent.observation.get_discrete_position(wanted_direction, vertical_distance)

        if not self.agent.observation.is_looking_at_discrete_position(block_position):
            turn_direction = get_turn_direction(self.agent.observation.yaw, get_yaw_from_direction(wanted_direction))
            self.agent.turn(turn_direction)

            wanted_pitch = get_wanted_pitch(1, vertical_distance - 1)
            pitch_req = get_pitch_change(self.agent.observation.pitch, wanted_pitch)
            self.agent.pitch(pitch_req)

            if turn_direction != 0 or pitch_req != 0:
                self.agent.attack(False)
                self.agent.move(0)
                return Status.RUNNING
        self.agent.turn(0)
        self.agent.pitch(0)
        self.agent.move(0)

        self.agent.attack(True)

    def can_jump(self, current_direction):
        climbable_below = self.agent.observation.lower_surroundings[current_direction] not in unclimbable

        free_above = self.agent.observation.upper_upper_surroundings[Direction.Zero] in traversable
        free_above_direction = self.agent.observation.upper_upper_surroundings[current_direction] in traversable

        return climbable_below and free_above and free_above_direction

    def jump_forward(self, wanted_direction):
        turn_direction = get_turn_direction(self.agent.observation.yaw, get_yaw_from_direction(wanted_direction))
        self.agent.turn(turn_direction)

        if turn_direction != 0:
            self.agent.attack(False)
            self.agent.move(0)
            self.agent.pitch(0)
            return Status.RUNNING
        self.agent.move(0)

        self.agent.attack(False)
        self.agent.move(1)
        self.agent.jump(True)

    def terminate(self, new_status):
        self.agent.stop()


class PickupItem(GoToObject):
    def __init__(self, agent, item):
        super(PickupItem, self).__init__(agent, f"Pick up {item}")
        self.item = item

    def update(self):
        self.agent.jump(False)

        distance = self.agent.observation.get_pickup_position(self.item)
        if distance is None:
            return Status.FAILURE

        self.go_to_position(distance)

        if self.agent.observation.get_pickup_position(self.item) is None:
            return Status.SUCCESS
        else:
            return Status.RUNNING


class GoToAnimal(GoToObject):
    def __init__(self, agent, specie=None):
        super(GoToAnimal, self).__init__(agent, f"Go to {specie if specie else 'animal'}")
        self.specie = specie

    def update(self):
        self.agent.jump(False)

        position = self.agent.observation.get_weakest_animal_position(self.specie)
        if position is None:
            return Status.FAILURE

        distance = self.agent.observation.get_distance_to_position(position)
        self.go_to_position(distance)

        if self.agent.observation.is_position_within_reach(position, ATTACK_REACH):
            return Status.SUCCESS
        else:
            return Status.RUNNING


class GoToBlock(GoToObject):
    def __init__(self, agent, block):
        super(GoToBlock, self).__init__(agent, f"Go to {block}")
        self.agent = agent
        self.block = block
        self.tool = get_gathering_tool(block)

    def update(self):
        self.agent.jump(False)
        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        discrete_position = self.agent.observation.get_closest_block(self.block)
        if discrete_position is None:
            return Status.FAILURE

        distance = self.agent.observation.get_distance_to_discrete_position(discrete_position)
        self.go_to_position(distance)

        position_center = get_position_center(discrete_position)
        return Status.SUCCESS if self.agent.observation.is_position_within_reach(position_center) else Status.RUNNING


class GoToPosition(GoToObject):
    def __init__(self, agent, position):
        super(GoToPosition, self).__init__(agent, f"Go to {position}")
        self.agent = agent
        self.position = position

    def update(self):
        distance = self.agent.observation.get_distance_to_discrete_position(self.position)
        self.go_to_position(distance)

        has_arrived = self.agent.observation.is_position_within_reach(self.position, ATTACK_REACH)
        return Status.SUCCESS if has_arrived else Status.RUNNING


class MineMaterial(Action):
    def __init__(self, agent, material):
        super(MineMaterial, self).__init__(f"Mine {material}")
        self.agent = agent
        self.material = material
        self.tool = get_gathering_tool(material)

    def update(self):
        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        discrete_position = self.agent.observation.get_closest_block(self.material)

        if discrete_position is None:
            return Status.FAILURE

        if not self.agent.observation.is_position_within_reach(get_position_center(discrete_position)):
            return Status.FAILURE

        distance = self.agent.observation.get_distance_to_discrete_position(discrete_position)
        if not self.agent.observation.is_looking_at_discrete_position(discrete_position):
            self.agent.attack(False)
            pitching = self.agent.pitch_towards(distance)
            turning = self.agent.turn_towards(distance)

            if pitching or turning:
                return Status.RUNNING
        self.agent.turn(0)
        self.agent.pitch(0)

        self.agent.attack(True)
        target_grid_point = tuple(self.agent.observation.pos + round_move(distance))
        if self.agent.observation.grid_local[target_grid_point] != items.AIR:
            return Status.RUNNING

        self.agent.attack(False)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.agent.stop()


class AttackAnimal(Action):
    def __init__(self, agent, specie=None):
        super(AttackAnimal, self).__init__(f"Attack {specie if specie else 'animal'}")
        self.agent = agent
        self.specie = specie

    def update(self):
        position = self.agent.observation.get_weakest_animal_position(self.specie)
        distance = self.agent.observation.get_distance_to_position(position)

        if not self.agent.observation.is_position_within_reach(position):
            return Status.FAILURE

        if not self.agent.observation.is_looking_at_type(self.specie):
            pitching = self.agent.pitch_towards(distance)
            turning = self.agent.turn_towards(distance)

            if pitching or turning:
                self.agent.attack(False)
                return Status.RUNNING

        self.agent.attack(True)
        if distance is not None:
            return Status.RUNNING

        self.agent.attack(False)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.agent.stop()


class PlaceBlockAtPosition(Action):
    def __init__(self, agent, block, position):
        super(PlaceBlockAtPosition, self).__init__(f"Place {block} at position {position}")
        self.agent = agent
        self.block = block
        self.position = position
        self.position_below = position + down_vector

    def update(self):
        distance = self.agent.observation.get_distance_to_discrete_position(self.position_below)

        if not self.agent.observation.is_position_within_reach(self.position_below, ATTACK_REACH):
            return Status.FAILURE

        # Look at
        self.agent.jump(False)
        self.agent.move(0)

        pitching = self.pitch_towards(distance)
        turning = self.turn_towards(distance)

        if pitching or turning:
            return Status.RUNNING

        if not self.agent.observation.is_looking_at_discrete_position(self.position_below):
            self.agent.attack(True)
            return Status.RUNNING

        self.agent.place_block()

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

    def terminate(self, new_status):
        self.agent.attack(False)


# TODO: Refactor to "LookForMaterial" Which will be an exploratory step when looking for materials
# First it will dig down to a correct height then start digging sideways.
class DigDownwardsToMaterial(Action):
    PITCH_DOWNWARDS = 90

    def __init__(self, agent, material):
        super(DigDownwardsToMaterial, self).__init__(f"Dig downwards to {material}")
        self.agent = agent
        self.material = material

        self.tool = get_gathering_tool(material)

    def update(self):
        if self.tool is not None and not self.agent.inventory.has_item_equipped(self.tool):
            return Status.FAILURE

        position = self.agent.observation.get_closest_block(self.material)

        if position is not None:
            return Status.SUCCESS

        looking_downwards = self.agent.pitch_downwards()
        if not looking_downwards:
            return Status.RUNNING

        self.agent.attack(True)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


# TODO: Refactor to "LookForAnimal" Which will be an exploratory step when looking for animals
class RunForwardTowardsAnimal(GoToObject):
    def __init__(self, agent, specie=None):
        super(RunForwardTowardsAnimal, self).__init__(agent, f"Look for {specie}")
        self.specie = specie

    def update(self):
        self.agent.jump(False)

        distance = directionVector[Direction.North]

        self.go_to_position(distance)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()
