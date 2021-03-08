from MalmoPython import AgentHost
from recipes import RecipeBook


class MinerAgent(AgentHost):

    def __init__(self, *args, **kwargs):
        self.observation = None
        self.inventory = None
        super().__init__(*args, **kwargs)

    def set_observation(self, observation):
        self.observation = observation
        if observation:
            self.inventory = observation.inventory

