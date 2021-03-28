import time

from MalmoPython import AgentHost

CRAFT_SLEEP = 0.25
SWAP_SLEEP = 0.25
HOT_BAR_SLEEP = 0.1


class MissionTimeoutException(Exception):
    pass


class MinerAgent:

    def __init__(self):
        self.agent_host = AgentHost()
        self.observation = None
        self.inventory = None

    def set_observation(self, observation):
        self.observation = observation
        if observation:
            self.inventory = observation.inventory

    def get_world_state(self):
        return self.agent_host.getWorldState()

    def restart_minecraft(self, world_state, client_info, message=""):
        """"Attempt to quit mission if running and kill the client"""
        if world_state.is_mission_running:
            self.agent_host.sendCommand("quit")
            time.sleep(10)
        self.agent_host.killClient(client_info)
        raise MissionTimeoutException(message)

    def activate_night_vision(self):
        self.agent_host.sendCommand("chat /effect @p night_vision 99999 255")

    def start_mission(self, mission, pool, mission_record, experiment_id):
        self.agent_host.startMission(mission, pool, mission_record, 0, experiment_id)

    def craft(self, item):
        if not self.inventory.has_ingredients(item):
            return False

        self.agent_host.sendCommand("craft " + item)
        time.sleep(CRAFT_SLEEP)
        return True

    def swap_items(self, position1, position2):
        self.agent_host.sendCommand("swapInventoryItems {0} {1}".format(position1, position2))
        time.sleep(SWAP_SLEEP)

    def select_on_hotbar(self, position):
        self.agent_host.sendCommand("hotbar.{0} 1".format(str(position + 1)))  # press
        self.agent_host.sendCommand("hotbar.{0} 0".format(str(position + 1)))  # release
        time.sleep(HOT_BAR_SLEEP)

    def move(self, speed):
        self.agent_host.sendCommand("move {0}".format(speed))

    def turn(self, speed):
        self.agent_host.sendCommand("turn {0}".format(speed))

    def pitch(self, speed):
        self.agent_host.sendCommand("pitch {0}".format(speed))

    def jump(self, active):
        self.agent_host.sendCommand("jump {0:d}".format(active))

    def attack(self, active):
        self.agent_host.sendCommand("attack {0:d}".format(active))





