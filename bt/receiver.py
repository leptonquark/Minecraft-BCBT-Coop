from py_trees.behaviour import Behaviour
from py_trees.common import Status


class Receiver(Behaviour):
    def __init__(self, blackboard, channel, values=None):
        if values is None:
            values = []
        super().__init__(f"Is {channel} fulfilled")
        self.blackboard = blackboard
        self.channel = channel
        self.values = values

    def update(self):
        return Status.SUCCESS if self.verify() else Status.FAILURE

    def verify(self):
        return self.blackboard.get(self.channel, False) in self.values


class InverseReceiver(Behaviour):
    def __init__(self, blackboard, channel, values=None):
        if values is None:
            values = [False]
        super().__init__(f"Is {channel} not in {values}")
        self.blackboard = blackboard
        self.channel = channel
        self.values = values

    def update(self):
        value = self.blackboard.get(self.channel, False)
        return Status.SUCCESS if value not in self.values else Status.FAILURE
