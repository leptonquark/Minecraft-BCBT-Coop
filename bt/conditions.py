from observation import has_arrived
from py_trees.behaviour import Behaviour
from py_trees.common import Status
from utils.constants import ATTACK_REACH, PLACING_REACH


class Condition(Behaviour):
    def __init__(self, name):
        super(Condition, self).__init__(name)


class HasItem(Condition):
    def __init__(self, agent, item, amount=1):
        super(HasItem, self).__init__("Has Item {0}x {1}".format(amount, item))
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
        super(HasItemEquipped, self).__init__("Has Item Equipped {0}".format(item))
        self.agent = agent
        self.item = item

    def update(self):
        if self.agent.inventory.has_item_equipped(self.item):
            return Status.SUCCESS
        else:
            return Status.FAILURE


class HasPickupNearby(Condition):
    def __init__(self, agent, item):
        super(HasPickupNearby, self).__init__("Has Pickup Nearby {0}".format(item))
        self.agent = agent
        self.item = item

    def update(self):
        return Status.SUCCESS if self.agent.observation.has_pickup_nearby(self.item) else Status.FAILURE


class IsBlockWithinReach(Condition):

    def __init__(self, agent, block):
        super(IsBlockWithinReach, self).__init__("Is Block {0} Within Reach ".format(block))
        self.agent = agent
        self.block = block

    def update(self):
        distance = self.agent.observation.get_closest_block(self.block)
        return Status.SUCCESS if has_arrived(distance) else Status.FAILURE


class IsBlockObservable(Condition):
    def __init__(self, agent, block):
        super(IsBlockObservable, self).__init__("Is Block {0} Observable ".format(block))
        self.agent = agent
        self.block = block

    def update(self):
        return Status.SUCCESS if self.agent.observation.is_block_observable(self.block) else Status.FAILURE


class IsPositionWithinReach(Condition):

    def __init__(self, agent, position):
        super(IsPositionWithinReach, self).__init__(f"Is Position {position} Within Reach ")
        self.agent = agent
        self.position = position

    def update(self):
        distance = self.agent.observation.get_distance_to_position(self.position)
        return Status.SUCCESS if has_arrived(distance, reach=PLACING_REACH) else Status.FAILURE


class IsAnimalWithinReach(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalWithinReach, self).__init__("Is Animal {0} Within Reach ".format(specie))
        self.agent = agent
        self.specie = specie

    def update(self):
        distance = self.agent.observation.get_weakest_animal(self.specie)
        within_reach = has_arrived(distance, ATTACK_REACH)
        return Status.SUCCESS if within_reach else Status.FAILURE


class IsAnimalObservable(Condition):
    def __init__(self, agent, specie):
        super(IsAnimalObservable, self).__init__("Is Animal {0} Observable ".format(specie))
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
