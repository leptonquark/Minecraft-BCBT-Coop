from bt.conditions import Condition


class Receiver(Condition):
    def __init__(self, blackboard, channel, value=True):
        super(Condition, self).__init__(f"Is {channel} fulfilled")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value

    def verify(self):
        return self.blackboard.get(self.channel) == self.value


class InverseReceiver(Condition):
    def __init__(self, blackboard, channel, values=None):
        if values is None:
            values = [False]
        super(Condition, self).__init__(f"Is {channel} not in {values}")
        self.blackboard = blackboard
        self.channel = channel
        self.values = values

    def verify(self):
        # print(f"Receiver {self.channel} values:  {self.blackboard.get(self.channel)}")
        return self.blackboard.get(self.channel, False) not in self.values
