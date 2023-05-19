from py_trees.behaviour import Behaviour
from py_trees.common import Status

from items.gathering import get_pickaxe
from utils.constants import PLACING_REACH
from utils.vectors import down, BlockFace, Direction
from world.observer import get_position_center, get_horizontal_distance, get_position_flat_center


# TODO: Move agent setter to here
class Action(Behaviour):
    def __init__(self, name, agent):
        super().__init__(name)
        self.agent = agent

    def terminate(self, new_status):
        self.agent.stop()


class Craft(Action):
    def __init__(self, agent, item, amount=1):
        super().__init__(f"Craft {item}", agent)
        self.amount = amount
        self.item = item

    def update(self):
        if self.agent.inventory.has_ingredients(self.item):
            self.agent.craft(self.item, self.amount)
            return Status.RUNNING
        else:
            return Status.FAILURE


class Melt(Action):
    def __init__(self, agent, item, amount=1):
        super().__init__(f"Melt {amount}x {item}", agent)
        self.item = item
        self.amount = amount

    def update(self):
        fuel = self.agent.inventory.get_fuel()
        if fuel is not None and self.agent.inventory.has_ingredients(self.item):
            self.agent.melt(self.item, fuel, self.amount)
            return Status.RUNNING
        else:
            return Status.FAILURE


class Equip(Action):
    def __init__(self, agent, item):
        super().__init__(f"Equip {item}", agent)
        self.item = item

    def update(self):
        if self.agent.inventory.has_item(self.item):
            self.agent.equip_item(self.item)
            return Status.SUCCESS
        else:
            return Status.FAILURE


class EquipBestPickAxe(Action):
    def __init__(self, agent, tier):
        super().__init__(f"Equip {get_pickaxe(tier)}", agent)
        self.tier = tier

    def update(self):
        if self.agent.has_pickaxe_by_minimum_tier(self.tier):
            self.agent.equip_best_pickaxe(self.tier)
            return Status.SUCCESS
        else:
            return Status.FAILURE


class JumpIfStuck(Action):
    def __init__(self, agent):
        super().__init__("JumpIfStuck", agent)

    def update(self):
        is_stuck = self.agent.is_stuck()
        self.agent.jump(is_stuck)
        return Status.RUNNING if is_stuck else Status.SUCCESS

    def terminate(self, new_status):
        self.agent.jump(False)


class PickupItem(Action):
    def __init__(self, agent, item):
        super().__init__(f"Pick up {item}", agent)
        self.item = item

    def update(self):
        position = self.agent.get_pickup_position(self.item)
        if position is not None:
            self.agent.go_to_position(position)
            return Status.RUNNING
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.stop()


class GoToAnimal(Action):
    def __init__(self, agent, specie=None):
        super().__init__(f"Go to {specie if specie else 'entity'}", agent)
        self.specie = specie

    def update(self):
        animal = self.agent.get_weakest_animal(self.specie)
        if animal is None:
            return Status.FAILURE
        elif self.agent.is_entity_within_reach(animal):
            return Status.SUCCESS
        else:
            self.agent.go_to_position(animal.position)
            return Status.RUNNING


class GoToEnemy(Action):
    def __init__(self, agent, consider_other_agents=False):
        super().__init__("Go to enemy", agent)
        self.consider_other_agents = consider_other_agents

    def update(self):
        enemy = self.agent.get_closest_enemy(self.consider_other_agents)
        if enemy is None:
            return Status.FAILURE
        elif self.agent.is_entity_within_reach(enemy):
            return Status.SUCCESS
        else:
            self.agent.go_to_position(enemy.position)
            return Status.RUNNING


class GoToBlock(Action):
    def __init__(self, agent, block):
        super().__init__(f"Go to {block}", agent)
        self.agent = agent
        self.block = block

    def update(self):
        block_center = self.agent.get_closest_block_center(self.block)
        if block_center is None:
            return Status.FAILURE
        elif self.agent.is_position_within_reach(block_center):
            return Status.SUCCESS
        else:
            self.agent.go_to_position(block_center)
            return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class GoToPosition(Action):
    def __init__(self, agent, position):
        super().__init__(f"Go to {position}", agent)
        self.position = position

    def update(self):
        position_center = get_position_flat_center(self.position)
        if self.agent.is_position_within_reach(position_center):
            return Status.SUCCESS
        else:
            self.agent.go_to_position(position_center)
            return Status.RUNNING


class MineMaterial(Action):
    def __init__(self, agent, material):
        super().__init__(f"Mine {material}", agent)
        self.material = material

    def update(self):
        discrete_position = self.agent.observer.get_closest_block(self.material)
        position_center = get_position_center(discrete_position)

        if self.agent.is_position_within_reach(position_center):
            done_looking = self.agent.look_at_block(discrete_position, BlockFace.NoFace)
            self.agent.attack(done_looking)
            return Status.RUNNING
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.stop()


class AttackAnimal(Action):
    def __init__(self, agent, specie=None):
        super().__init__(f"Attack {specie if specie else 'entity'}", agent)
        self.specie = specie

    def update(self):
        animal = self.agent.get_weakest_animal(self.specie)
        if self.agent.is_entity_within_reach(animal):
            done_looking = self.agent.look_at_entity(animal)
            self.agent.attack(done_looking)
            return Status.RUNNING
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.stop()


class DefeatEnemy(Action):
    def __init__(self, agent, consider_other_agents=False):
        super().__init__("Defeat closest enemy", agent)
        self.consider_other_agents = consider_other_agents

    def update(self):
        enemy = self.agent.get_closest_enemy(self.consider_other_agents)
        if self.agent.observer.is_position_within_reach(enemy.position):
            done_looking = self.agent.look_at_entity(enemy)
            self.agent.attack(done_looking)
            return Status.RUNNING
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.stop()


class PlaceBlockAtPosition(Action):
    def __init__(self, agent, block, position):
        super().__init__(f"Place {block} at position {position}", agent)
        self.block = block
        self.position = position
        self.position_below = position + down

    def update(self):
        if self.agent.observer.is_block_at_position(self.position, self.block):
            return Status.SUCCESS
        elif not self.agent.is_position_within_reach(get_position_flat_center(self.position), reach=PLACING_REACH):
            self.agent.attack(False)
            return Status.FAILURE
        elif self.agent.is_at_position(self.position):
            self.agent.move_backward()
            self.agent.attack(False)
            return Status.RUNNING
        else:
            self.agent.move(0)
            done_looking = self.agent.look_at_block(self.position_below, BlockFace.Up)
            if done_looking:
                if self.agent.observer.is_looking_at_discrete_position(self.position_below):
                    self.agent.attack(False)
                    self.agent.place_block()
                else:
                    self.agent.attack(True)
            return Status.RUNNING

    def terminate(self, new_status):
        self.agent.attack(False)


# TODO: Refactor to "LookForMaterial" Which will be an exploratory step when looking for materials
# First it will dig down to a correct height then start digging sideways.
class DigDownwardsToMaterial(Action):

    def __init__(self, agent, material):
        super().__init__(f"Dig downwards to {material}", agent)
        self.material = material

    def update(self):
        position_block = self.agent.observer.get_closest_block(self.material)

        if position_block is not None:
            return Status.SUCCESS

        position_downwards = self.agent.observer.get_first_block_downwards()
        if position_downwards is None:
            return Status.FAILURE

        position_center = get_position_center(position_downwards)
        distance = self.agent.observer.get_distance_to_position(position_center)
        if distance is None:
            return Status.FAILURE

        if not self.agent.observer.is_position_within_reach(position_center):
            self.agent.turn_towards(distance)
            turn_direction = self.agent.get_turn_direction(distance)
            self.agent.move_forward(get_horizontal_distance(distance), turn_direction)
            return Status.RUNNING

        done_looking = self.agent.look_at_block(position_downwards, BlockFace.Up)

        if done_looking:
            self.agent.attack(True)
        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class ExploreInDirection(Action):
    def __init__(self, agent, direction=Direction.North):
        super().__init__(f"Explore in direction {direction}", agent)
        self.direction = direction

    def update(self):
        self.agent.explore_in_direction(self.direction)
        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()
