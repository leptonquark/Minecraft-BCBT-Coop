from world.observation import get_position_center
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from utils.constants import ATTACK_REACH, PLACING_REACH


class Condition(Behaviour):
    def __init__(self, name):
        super(Condition, self).__init__(name)


class HasItem(Condition):
    def __init__(self, agent, item, amount=1):
        super(HasItem, self).__init__(f"Has Item {amount}x {item}")
        self.agent = agent
        self.item = item
        self.amount = amount

    def update(self):
        if self.agent.inventory.has_item(self.item, self.amount):
            return Status.SUCCESS
        else:
            return Status.FAILURE


class HasItemEquipped(Condition):
    def __init__(self, agent, item):
        super(HasItemEquipped, self).__init__(f"Has Item Equipped {item}")
        self.agent = agent
        self.item = item

    def update(self):
        if self.agent.inventory.has_item_equipped(self.item):
            return Status.SUCCESS
        else:
            return Status.FAILURE


class HasPickupNearby(Condition):
    def __init__(self, agent, item):
        super(HasPickupNearby, self).__init__(f"Has Pickup Nearby {item}")
        self.agent = agent
        self.item = item

    def update(self):
        return Status.SUCCESS if self.agent.observation.has_pickup_nearby(self.item) else Status.FAILURE


class IsBlockWithinReach(Condition):

    def __init__(self, agent, block_type):
        super(IsBlockWithinReach, self).__init__(f"Is Block Within Reach {block_type}")
        self.agent = agent
        self.block_type = block_type

    def update(self):
        discrete_position = self.agent.observation.get_closest_block(self.block_type)
        if discrete_position is None:
            return Status.FAILURE

        position_center = get_position_center(discrete_position)
        return Status.SUCCESS if self.agent.observation.is_position_within_reach(position_center) else Status.FAILURE


class IsBlockObservable(Condition):
    def __init__(self, agent, block):
        super(IsBlockObservable, self).__init__(f"Is Block Observable {block}")
        self.agent = agent
        self.block = block

    def update(self):
        return Status.SUCCESS if self.agent.observation.is_block_observable(self.block) else Status.FAILURE


class IsPositionWithinReach(Condition):

    def __init__(self, agent, position):
        super(IsPositionWithinReach, self).__init__(f"Is Position Within Reach {position}")
        self.agent = agent
        self.position = position

    def update(self):
        position_center = get_position_center(self.position)
        has_arrived = self.agent.observation.is_position_within_reach(position_center, reach=PLACING_REACH)
        return Status.SUCCESS if has_arrived else Status.FAILURE


class IsAnimalWithinReach(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalWithinReach, self).__init__(f"Is Animal Within Reach {specie}")
        self.agent = agent
        self.specie = specie

    def update(self):
        position = self.agent.observation.get_weakest_animal_position(self.specie)
        within_reach = self.agent.observation.is_position_within_reach(position, ATTACK_REACH)
        return Status.SUCCESS if within_reach else Status.FAILURE


class IsAnimalObservable(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalObservable, self).__init__(f"Is Animal Observable {specie}")
        self.agent = agent
        self.specie = specie

    def update(self):
        return Status.SUCCESS if self.agent.observation.is_animal_observable(self.specie) else Status.FAILURE


class IsBlockAtPosition(Condition):
    def __init__(self, agent, block, position):
        super(IsBlockAtPosition, self).__init__(f"Is Block {block} at position {position}")
        self.agent = agent
        self.block = block
        self.position = position

    def update(self):
        is_block_at_position = self.agent.observation.is_block_at_position(self.position, self.block)
        return Status.SUCCESS if is_block_at_position else Status.FAILURE
