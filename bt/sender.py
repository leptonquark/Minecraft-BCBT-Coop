from py_trees.behaviour import Behaviour
from py_trees.common import Status


class Sender(Behaviour):
    def __init__(self, blackboard, channel, value):
        super().__init__(f"Set {channel} is {value}")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value

    def update(self):
        self.blackboard[self.channel] = self.value
        return Status.SUCCESS


class StartSender(Sender):
    def __init__(self, blackboard, channel):
        super().__init__(blackboard, channel, True)

    def update(self):
        super().update()
        return Status.SUCCESS


class StopSender(Sender):
    def __init__(self, blackboard, channel):
        super().__init__(blackboard, channel, False)

    def update(self):
        super().update()
        return Status.SUCCESS


class ItemSender(Behaviour):
    def __init__(self, agent, item):
        self.agent = agent
        self.blackboard = agent.blackboard
        self.channel = f"shared_inventory_{item}_{agent.role}"
        self.item = item
        super().__init__(f"Set {self.channel} to amount of {item} in inventory")

    def update(self):
        amount = self.agent.inventory.get_item_amount(self.item)
        self.blackboard[self.channel] = amount
        return Status.SUCCESS
