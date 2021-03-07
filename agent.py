from MalmoPython import AgentHost
from recipes import RecipeBook


class MinerAgent(AgentHost):

    def __init__(self, *args, **kwargs):
        self.observation = None
        self.inventory = None
        self.recipes = RecipeBook()
        super().__init__(*args, **kwargs)

    def set_observation(self, observation):
        self.observation = observation
        self.inventory = observation.inventory
