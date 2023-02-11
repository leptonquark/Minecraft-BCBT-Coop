import numpy as np
from py_trees.behaviour import Behaviour
from py_trees.common import Status

from items import items
from utils.constants import ATTACK_REACH, PLACING_REACH
from utils.vectors import directionVector, down, BlockFace, Direction
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
        if not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        self.agent.craft(self.item, self.amount)
        return Status.RUNNING


class Melt(Action):
    def __init__(self, agent, item, amount=1):
        super().__init__(f"Melt {amount}x {item}", agent)
        self.item = item
        self.amount = amount

    def update(self):
        fuel = self.agent.inventory.get_fuel()
        if fuel is None or not self.agent.inventory.has_ingredients(self.item):
            return Status.FAILURE

        self.agent.melt(self.item, fuel, self.amount)

        return Status.SUCCESS


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
        super().__init__(f"Equip best pickaxe, {tier} or better", agent)
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
        is_stuck = self.agent.observer.is_stuck()
        self.agent.jump(is_stuck)
        return Status.RUNNING if is_stuck else Status.SUCCESS

    def terminate(self, new_status):
        self.agent.jump(False)


class PickupItem(Action):
    def __init__(self, agent, item):
        super().__init__(f"Pick up {item}", agent)
        self.item = item

    def update(self):
        position = self.agent.observer.get_pickup_position(self.item)
        if position is not None:
            self.agent.go_to_position(position)
            return Status.SUCCESS if self.agent.observer.get_pickup_position(self.item) is None else Status.RUNNING
        else:
            return Status.FAILURE

    def terminate(self, new_status):
        self.agent.stop()


class GoToAnimal(Action):
    def __init__(self, agent, specie=None):
        super().__init__(f"Go to {specie if specie else 'animal'}", agent)
        self.specie = specie

    def update(self):
        self.agent.jump(False)

        animal = self.agent.observer.get_weakest_animal(self.specie)
        if animal is not None:
            self.agent.go_to_position(animal.position)

            within_reach = self.agent.observer.is_position_within_reach(animal.position, ATTACK_REACH)
            return Status.SUCCESS if within_reach else Status.RUNNING
        else:
            return Status.FAILURE


class GoToEnemy(Action):
    def __init__(self, agent, consider_other_agents=False):
        super().__init__("Go to enemy", agent)
        self.consider_other_agents = consider_other_agents

    def update(self):
        self.agent.jump(False)

        if self.consider_other_agents:
            enemy = self.agent.observer.get_closest_enemy_to_agents()
        else:
            enemy = self.agent.observer.get_closest_enemy()

        if enemy is not None:
            self.agent.go_to_position(enemy.position)
            within_reach = self.agent.observer.is_position_within_reach(enemy.position, ATTACK_REACH)
            return Status.SUCCESS if within_reach else Status.RUNNING
        else:
            return Status.FAILURE


class GoToBlock(Action):
    def __init__(self, agent, block):
        super().__init__(f"Go to {block}", agent)
        self.agent = agent
        self.block = block

    def update(self):
        self.agent.jump(False)

        discrete_position = self.agent.observer.get_closest_block(self.block)
        if discrete_position is None:
            return Status.FAILURE

        position_center = get_position_center(discrete_position)
        self.agent.go_to_position(position_center)

        return Status.SUCCESS if self.agent.observer.is_position_within_reach(position_center) else Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class GoToPosition(Action):
    def __init__(self, agent, position):
        super().__init__(f"Go to {position}", agent)
        self.position = position

    def update(self):
        position_center = get_position_flat_center(self.position)
        self.agent.go_to_position(position_center)

        has_arrived = self.agent.observer.is_position_within_reach(position_center, PLACING_REACH)
        return Status.SUCCESS if has_arrived else Status.RUNNING


class MineMaterial(Action):
    def __init__(self, agent, material):
        super().__init__(f"Mine {material}", agent)
        self.material = material

    def update(self):
        discrete_position = self.agent.observer.get_closest_block(self.material)
        position_center = get_position_center(discrete_position)

        if discrete_position is None or not self.agent.observer.is_position_within_reach(position_center):
            return Status.FAILURE

        done_looking = self.agent.look_at_block(discrete_position, BlockFace.NoFace)
        if not done_looking:
            return Status.RUNNING

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
        super().__init__(f"Attack {specie if specie else 'animal'}", agent)
        self.specie = specie

    def update(self):
        animal = self.agent.observer.get_weakest_animal(self.specie)

        if not self.agent.observer.is_position_within_reach(animal.position):
            return Status.FAILURE

        done_looking = self.agent.look_at_entity(animal)
        self.agent.attack(done_looking)
        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()


class DefeatEnemy(Action):
    def __init__(self, agent, consider_other_agents=False):
        super().__init__("Defeat closest enemy", agent)
        self.consider_other_agents = consider_other_agents

    def update(self):
        enemy = self.get_closest_enemy(self.consider_other_agents)
        if self.agent.observer.is_position_within_reach(enemy.position):
            done_looking = self.agent.look_at_entity(enemy)
            self.agent.attack(done_looking)
            return Status.RUNNING
        else:
            return Status.FAILURE

    def get_closest_enemy(self, consider_other_agents):
        if consider_other_agents:
            enemy = self.agent.observer.get_closest_enemy_to_agents()
        else:
            enemy = self.agent.observer.get_closest_enemy()
        return enemy

    def terminate(self, new_status):
        self.agent.stop()


class PlaceBlockAtPosition(Action):
    def __init__(self, agent, block, position):
        super().__init__(f"Place {block} at position {position}", agent)
        self.block = block
        self.position = position
        self.position_below = position + down

    def update(self):
        position_flat_center = get_position_flat_center(self.position)
        has_arrived = self.agent.observer.is_position_within_reach(position_flat_center, reach=PLACING_REACH)

        if not has_arrived:
            self.agent.attack(False)
            return Status.FAILURE

        abs_pos_discrete = self.agent.observer.get_abs_pos_discrete()
        if abs_pos_discrete is None:
            return Status.RUNNING

        if np.array_equal(self.position, abs_pos_discrete):
            self.agent.move_backward()
            self.agent.attack(False)
            return Status.RUNNING

        # Look at
        self.agent.jump(False)
        self.agent.move(0)

        done_looking = self.agent.look_at_block(self.position_below, BlockFace.Up)

        if done_looking:
            if self.agent.observer.is_looking_at_discrete_position(self.position_below):
                self.agent.attack(False)
                self.agent.place_block()
                is_block_at_position = self.agent.observer.is_block_at_position(self.position, self.block)
                return Status.SUCCESS if is_block_at_position else Status.FAILURE
            else:
                self.agent.attack(True)
                return Status.RUNNING
        else:
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


DISTANCE_FAR_AWAY = 100


class ExploreInDirection(Action):
    def __init__(self, agent, direction=Direction.North):
        super().__init__(f"Explore in direction {direction}", agent)
        self.direction = direction

    def update(self):
        self.agent.jump(False)
        abs_pos_discrete = self.agent.observer.get_abs_pos_discrete()
        if abs_pos_discrete is None:
            return Status.RUNNING

        position = abs_pos_discrete + DISTANCE_FAR_AWAY * directionVector[self.direction]

        self.agent.go_to_position(position)

        return Status.RUNNING

    def terminate(self, new_status):
        self.agent.stop()
