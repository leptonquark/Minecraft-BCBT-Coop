class AgentlessCondition:

    def __init__(self, condition_class, args):
        self.condition_class = condition_class
        self.args = args

    def as_condition(self, agent):
        params = [agent] + self.args
        return self.condition_class(*params)
