from py_trees.common import Status

from bt.actions import Action


class Sender(Action):
    def __init__(self, blackboard, channel, value):
        super(Sender, self).__init__(f"Set {channel} is {value}")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value

    def update(self):
        self.blackboard[self.channel] = self.value
        return Status.SUCCESS


class StartSender(Sender):
    def __init__(self, blackboard, channel):
        super(StartSender, self).__init__(blackboard, channel, True)

    def update(self):
        print(f"StartSender ticked: {self.channel}")
        super(StartSender, self).update()
        return Status.SUCCESS


class StopSender(Sender):
    def __init__(self, blackboard, channel):
        super(StopSender, self).__init__(blackboard, channel, False)

    def update(self):
        print(f"StopSender ticked: {self.channel}")
        super(StopSender, self).update()
        return Status.SUCCESS
