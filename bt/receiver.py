from bt.conditions import Condition


class Receiver(Condition):
    def __init__(self, blackboard, channel, value=True):
        super(Receiver, self).__init__(f"Is {channel} fulfilled")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value
        print(f"Receiver {self.channel} {self.value}")

    def verify(self):
        print(f"Receiver {self.channel} {self.value}")
        return self.blackboard.get(self.channel) == self.value
