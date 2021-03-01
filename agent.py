from MalmoPython import AgentHost
from recipes import RecipeBook
import time

class MinerAgent(AgentHost):

    def __init__(self, *args, **kwargs):
        self.recipes = RecipeBook()
        super().__init__(*args, **kwargs)

    def set_observation(self, observation):
        self.observation = observation
        self.inventory = observation.inventory