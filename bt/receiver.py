from bt.conditions import Condition


class Receiver(Condition):
    def __init__(self, blackboard, channel, value=True):
        super(Receiver, self).__init__(f"Is {channel} fulfilled")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value

    def verify(self):
        return self.blackboard[self.channel] == self.value
