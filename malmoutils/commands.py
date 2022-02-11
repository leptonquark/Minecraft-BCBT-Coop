import time

from malmo.MalmoPython import AgentHost

CRAFT_SLEEP = 0.1
DISCRETE_USE_SLEEP = 0.1
HOT_BAR_SLEEP = 0.1


class MissionTimeoutException(Exception):
    pass


class CommandInterface:
    def __init__(self):
        self.agent_host = AgentHost()

    def get_world_state(self):
        return self.agent_host.getWorldState()

    def move(self, speed):
        self.agent_host.sendCommand(f"move {speed}")

    def turn(self, speed):
        self.agent_host.sendCommand(f"turn {speed}")

    def pitch(self, speed):
        self.agent_host.sendCommand(f"pitch {speed}")

    def jump(self, active):
        self.agent_host.sendCommand(f"jump {active:d}")

    def attack(self, active):
        self.agent_host.sendCommand(f"attack {active:d}")

    def discrete_use(self):
        self.agent_host.sendCommand("use")
        time.sleep(DISCRETE_USE_SLEEP)

    def select_on_hotbar(self, position):
        self.agent_host.sendCommand(f"hotbar.{position + 1} 1")  # press
        self.agent_host.sendCommand(f"hotbar.{position + 1} 0")  # release
        time.sleep(HOT_BAR_SLEEP)

    def craft(self, item):
        self.agent_host.sendCommand(f"craft {item}")
        time.sleep(CRAFT_SLEEP)

    def swap_items(self, position1, position2):
        self.agent_host.sendCommand("swapInventoryItems {0} {1}".format(position1, position2))

    def activate_effect(self, effect, effect_time, amplifier):
        self.agent_host.sendCommand(f"chat /effect @p {effect} {effect_time} {amplifier}")

    def start_mission(self, mission, mission_record):
        self.agent_host.startMission(mission, mission_record)

    def start_multi_agent_mission(self, mission, client_pool, mission_record, role, experiment_id):
        self.agent_host.startMission(mission, client_pool, mission_record, role, experiment_id)

    def restart_minecraft(self, world_state, client_info, message=""):
        """"Attempt to quit world if running and kill the client"""
        if world_state.is_mission_running:
            self.agent_host.sendCommand("quit")
            time.sleep(10)
        self.agent_host.killClient(client_info)
        raise MissionTimeoutException(message)

    def quit(self):
        self.agent_host.sendCommand("quit")
