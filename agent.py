from MalmoPython import AgentHost
import time

class MinerAgent(AgentHost):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_observation(self, observation):
        self.observation = observation
        self.inventory = observation.inventory