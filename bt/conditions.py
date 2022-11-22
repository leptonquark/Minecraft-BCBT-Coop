from py_trees.behaviour import Behaviour
from py_trees.common import Status

from utils.constants import ATTACK_REACH, PLACING_REACH
from world.observer import get_position_center, get_position_flat_center


# TODO: Move agent setter to here
class Condition(Behaviour):
    def __init__(self, name):
        super(Condition, self).__init__(name)

    def update(self):
        return Status.SUCCESS if self.verify() else Status.FAILURE

    def verify(self):
        raise NotImplementedError("Please Implement this method")


class HasItem(Condition):
    def __init__(self, agent, item, amount=1, same_variant=False):
        super(HasItem, self).__init__(f"Has Item {amount}x {item}")
        self.agent = agent
        self.item = item
        self.amount = amount
        self.same_variant = same_variant

    def verify(self):
        return self.agent.inventory.has_item(self.item, self.amount, self.same_variant)


class HasItemEquipped(Condition):
    def __init__(self, agent, item):
        super(HasItemEquipped, self).__init__(f"Has Item Equipped {item}")
        self.agent = agent
        self.item = item

    def verify(self):
        return self.agent.inventory.has_item_equipped(self.item)


class HasPickaxeByMinimumTier(Condition):
    def __init__(self, agent, tier):
        super(HasPickaxeByMinimumTier, self).__init__(f"Has Pickaxe of tier {tier} or better")
        self.agent = agent
        self.tier = tier

    def verify(self):
        return self.agent.has_pickaxe_by_minimum_tier(self.tier)


class HasBestPickaxeByMinimumTierEquipped(Condition):
    def __init__(self, agent, tier):
        super(HasBestPickaxeByMinimumTierEquipped, self).__init__(f"Has Pickaxe of tier {tier} or better equipped")
        self.agent = agent
        self.tier = tier

    def verify(self):
        return self.agent.has_best_pickaxe_by_minimum_tier_equipped(self.tier)


class HasPickupNearby(Condition):
    def __init__(self, agent, item):
        super(HasPickupNearby, self).__init__(f"Has Pickup Nearby {item}")
        self.agent = agent
        self.item = item

    def verify(self):
        return self.agent.observer.has_pickup_nearby(self.item)


class IsBlockWithinReach(Condition):

    def __init__(self, agent, block_type):
        super(IsBlockWithinReach, self).__init__(f"Is Block Within Reach {block_type}")
        self.agent = agent
        self.block_type = block_type

    def update(self):
        discrete_position = self.agent.observer.get_closest_block(self.block_type)
        if discrete_position is None:
            return Status.FAILURE

        position_center = get_position_center(discrete_position)
        return Status.SUCCESS if self.agent.observer.is_position_within_reach(position_center) else Status.FAILURE

    def verify(self):
        discrete_position = self.agent.observer.get_closest_block(self.block_type)
        if discrete_position is None:
            return False

        position_center = get_position_center(discrete_position)
        return self.agent.observer.is_position_within_reach(position_center)


class IsBlockObservable(Condition):

    def __init__(self, agent, block):
        super(IsBlockObservable, self).__init__(f"Is Block Observable {block}")
        self.agent = agent
        self.block = block

    def verify(self):
        return self.agent.observer.is_block_observable(self.block)


class IsPositionWithinReach(Condition):

    def __init__(self, agent, position):
        super(IsPositionWithinReach, self).__init__(f"Is Position Within Reach {position}")
        self.agent = agent
        self.position = position

    def verify(self):
        position_center = get_position_flat_center(self.position)
        has_arrived = self.agent.observer.is_position_within_reach(position_center, reach=PLACING_REACH)
        return has_arrived


class IsAnimalWithinReach(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalWithinReach, self).__init__(f"Is Animal Within Reach {specie}")
        self.agent = agent
        self.specie = specie

    def verify(self):
        position = self.agent.observer.get_weakest_animal_position(self.specie)
        return self.agent.observer.is_position_within_reach(position, ATTACK_REACH)


class IsAnimalObservable(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalObservable, self).__init__(f"Is Animal Observable {specie}")
        self.agent = agent
        self.specie = specie

    def verify(self):
        return self.agent.observer.is_animal_observable(self.specie)


class IsBlockAtPosition(Condition):
    def __init__(self, agent, block, position):
        super(IsBlockAtPosition, self).__init__(f"Is Block {block} at position {position}")
        self.agent = agent
        self.block = block
        self.position = position

    def verify(self):
        return self.agent.observer.is_block_at_position(self.position, self.block)
