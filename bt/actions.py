from py_trees.behaviour import Behaviour
from py_trees.common import Status

from items import items
from utils.constants import ATTACK_REACH, PLACING_REACH
from utils.vectors import Direction, directionVector, down
from world.observer import get_position_center, get_horizontal_distance, get_position_flat_center


# TODO: Move agent setter to here
class Action(Behaviour):
    def __init__(self, name):
        super().__init__(name)


class Craft(Action):
    def __init__(self, agent, item, amount=1):
        super().__init__(f"Craft {item}")
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
        super().__init__(f"Melt {amount}x {item}")
        self.agent = agent
        self.item = item
        self.amount = amount

    def update(self):
        fuel = self.agent.inventory.get_fuel()
        if fuel is None:
            return Status.FAILURE

        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        self.agent.melt(self.item, fuel, self.amount)

        return Status.SUCCESS


class Equip(Action):
    def __init__(self, agent, item):
        super().__init__(f"Equip {item}")
        self.agent = agent
        self.item = item

    def update(self):
        if self.agent.inventory.has_item(self.item):
            self.agent.equip_item(self.item)
            return Status.SUCCESS

        return Status.FAILURE


class EquipBestPickAxe(Action):
    def __init__(self, agent, tier):
        super().__init__(f"Equip best pickaxe, {tier} or better")
        self.agent = agent
        self.tier = tier

    def update(self):
        if self.agent.has_pickaxe_by_minimum_tier(self.tier):
            self.agent.equip_best_pickaxe(self.tier)
            return Status.SUCCESS
        return Status.FAILURE


class JumpIfStuck(Action):
    def __init__(self, agent):
        super().__init__("JumpIfStuck")
        self.agent = agent

    def update(self):
        if self.agent.observer.is_stuck():
            self.agent.jump(True)
            return Status.RUNNING
        else:
            self.agent.jump(False)
            return Status.SUCCESS

    def terminate(self, new_status):
        self.agent.jump(False)


class GoToObject(Action):
    def __init__(self, agent, name):
        super().__init__(name)
        self.agent = agent

    def go_to_position(self, position):
        self.agent.go_to_position(position)

    def terminate(self, new_status):
        self.agent.stop()


class PickupItem(GoToObject):
    def __init__(self, agent, item):
        super().__init__(agent, f"Pick up {item}")
        self.item = item

    def update(self):
        self.agent.jump(False)

        position = self.agent.observer.get_pickup_position(self.item)
        if position is None:
            return Status.FAILURE

        self.go_to_position(position)

        if self.agent.observer.get_pickup_position(self.item) is None:
            return Status.SUCCESS
        else:
            return Status.RUNNING


class GoToAnimal(GoToObject):
    def __init__(self, agent, specie=None):
        super().__init__(agent, f"Go to {specie if specie else 'animal'}")
        self.specie = specie

    def update(self):
        self.agent.jump(False)

        position = self.agent.observer.get_weakest_animal_position(self.specie)
        if position is None:
            return Status.FAILURE

        self.go_to_position(position)

        if self.agent.observer.is_position_within_reach(position, ATTACK_REACH):
            return Status.SUCCESS
        else:
            return Status.RUNNING


class GoToBlock(GoToObject):
    def __init__(self, agent, block):
        super().__init__(agent, f"Go to {block}")
        self.agent = agent
        self.block = block

    def update(self):
        self.agent.jump(False)

        discrete_position = self.agent.observer.get_closest_block(self.block)
        if discrete_position is None:
            return Status.FAILURE

        position_center = get_position_center(discrete_position)
        self.go_to_position(position_center)

        return Status.SUCCESS if self.agent.observer.is_position_within_reach(position_center) else Status.RUNNING


class GoToPosition(GoToObject):
    def __init__(self, agent, position):
        super().__init__(agent, f"Go to {position}")
        self.agent = agent
        self.position = position

    def update(self):
        position_center = get_position_flat_center(self.position)
        self.go_to_position(position_center)

        has_arrived = self.agent.observer.is_position_within_reach(position_center, PLACING_REACH)
        return Status.SUCCESS if has_arrived else Status.RUNNING


class MineMaterial(Action):
    def __init__(self, agent, material):
        super().__init__(f"Mine {material}")
        self.agent = agent
        self.material = material

    def update(self):
        discrete_position = self.agent.observer.get_closest_block(self.material)
        position_center = get_position_center(discrete_position)

        if discrete_position is None:
            return Status.FAILURE

        if not self.agent.observer.is_position_within_reach(position_center):
            return Status.FAILURE

        distance = self.agent.observer.get_distance_to_position(position_center)
        if not self.agent.observer.is_looking_at_discrete_position(discrete_position):
            self.agent.attack(False)
            pitching = self.agent.pitch_towards(distance)
            turning = self.agent.turn_towards(distance)

            if pitching or turning:
                return Status.RUNNING
        self.agent.turn(0)
        self.agent.pitch(0)

        self.agent.attack(True)

        target_block = self.agent.observer.get_block_at_position_from_local(discrete_position)

        if target_block != items.AIR:
            return Status.RUNNING

        self.agent.attack(False)
        return Status.SUCCESS

    def terminate(self, new_status):
        self.agent.stop()


class AttackAnimal(Action):
    def __init__(self, agent, specie=None):
        super().__init__(f"Attack {specie if specie else 'animal'}")
        self.agent = agent
        self.specie = specie

    def update(self):
        position = self.agent.observer.get_weakest_animal_position(self.specie)
        distance = self.agent.observer.get_distance_to_position(position)

        if not self.agent.observer.is_position_within_reach(position):
            return Status.FAILURE

        if not self.agent.observer.is_looking_at_type(self.specie):
            pitching = self.agent.pitch_towards(distance)
            turning = self.agent.turn_towards(distance)

            if pitching or turning:
                self.agent.attack(False)
                return Status.RUNNING

        self.agent.attack(True)
        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class PlaceBlockAtPosition(Action):
    def __init__(self, agent, block, position):
        super().__init__(f"Place {block} at position {position}")
        self.agent = agent
        self.block = block
        self.position = position
        self.position_below = position + down

    def update(self):
        position_center = get_position_flat_center(self.position)
        has_arrived = self.agent.observer.is_position_within_reach(position_center, reach=PLACING_REACH)

        if not has_arrived:
            self.agent.attack(False)
            return Status.FAILURE

        if all(self.position == self.agent.observer.get_abs_pos_discrete()):
            self.agent.move_backward()
            self.agent.attack(False)
            return Status.RUNNING

        # Look at
        self.agent.jump(False)
        self.agent.move(0)

        distance = self.agent.observer.get_distance_to_position(position_center)
        pitching = self.agent.pitch_towards(distance)
        turning = self.agent.turn_towards(distance)

        if pitching or turning:
            return Status.RUNNING

        if not self.agent.observer.is_looking_at_discrete_position(self.position_below):
            self.agent.attack(True)
            return Status.RUNNING

        self.agent.attack(False)
        self.agent.place_block()

        is_block_at_position = self.agent.observer.is_block_at_position(self.position, self.block)
        if is_block_at_position:
            return Status.SUCCESS
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.attack(False)


# TODO: Refactor to "LookForMaterial" Which will be an exploratory step when looking for materials
# First it will dig down to a correct height then start digging sideways.
class DigDownwardsToMaterial(Action):

    def __init__(self, agent, material):
        super().__init__(f"Dig downwards to {material}")
        self.agent = agent
        self.material = material

    def update(self):
        position_block = self.agent.observer.get_closest_block(self.material)

        if position_block is not None:
            return Status.SUCCESS

        position_downwards = self.agent.observer.get_first_block_downwards()
        distance = self.agent.observer.get_distance_to_discrete_position(position_downwards)

        position_center = get_position_center(position_downwards)
        if not self.agent.observer.is_position_within_reach(position_center):
            self.agent.turn_towards(distance)
            turn_direction = self.agent.get_turn_direction(distance)
            self.agent.move_forward(get_horizontal_distance(distance), turn_direction)
            return Status.RUNNING

        self.agent.move(0)
        self.agent.turn(0)
        self.agent.pitch(0)

        if not self.agent.observer.is_looking_at_discrete_position(position_downwards):
            self.agent.attack(False)
            pitching = self.agent.pitch_towards(distance)
            turning = self.agent.turn_towards(distance)

            if pitching or turning:
                return Status.RUNNING

        self.agent.attack(True)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class DigForwardToMaterial(GoToObject):
    def __init__(self, agent):
        super().__init__(agent, f"Explore")

    def update(self):
        self.agent.jump(False)

        position = self.agent.observer.get_abs_pos_discrete() + directionVector[Direction.North]

        self.go_to_position(position)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


# TODO: Refactor to "LookForAnimal" Which will be an exploratory step when looking for animals
class RunForwardTowardsAnimal(GoToObject):
    def __init__(self, agent, specie=None):
        super().__init__(agent, f"Look for {specie}")
        self.specie = specie

    def update(self):
        self.agent.jump(False)

        position = self.agent.observer.get_abs_pos_discrete() + directionVector[Direction.North]

        self.go_to_position(position)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()
