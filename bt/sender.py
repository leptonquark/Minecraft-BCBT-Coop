from bt.actions import Action


class Sender(Action):
    def __init__(self, blackboard, channel, value):
        super(Sender, self).__init__(f"Set {channel} is {value}")
        self.blackboard = blackboard
        self.channel = channel
        self.value = value

    def update(self):
        self.blackboard[self.channel] = self.value


class StartSender(Sender):
    def __init__(self, blackboard, channel):
        super(StartSender, self).__init__(blackboard, channel, True)


class FinishSender(Sender):
    def __init__(self, blackboard, channel):
        super(FinishSender, self).__init__(blackboard, channel, False)
