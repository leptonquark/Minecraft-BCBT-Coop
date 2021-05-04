from observation import has_arrived
from py_trees.behaviour import Behaviour
from py_trees.common import Status


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
