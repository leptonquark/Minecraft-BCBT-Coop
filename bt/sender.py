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
        print(f"StartSender ticked: {self.channel}")
        super().update()
        return Status.SUCCESS


class StopSender(Sender):
    def __init__(self, blackboard, channel):
        super().__init__(blackboard, channel, False)

    def update(self):
        super().update()
        return Status.SUCCESS
