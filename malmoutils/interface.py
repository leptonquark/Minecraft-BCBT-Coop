import time

from malmo.MalmoPython import AgentHost, MissionRecordSpec, MissionSpec, ClientPool, ClientInfo

import items.items
from items import variants
from utils.network import get_ports, get_ip

CRAFT_SLEEP = 0.1
DISCRETE_USE_SLEEP = 0.15
HOT_BAR_SLEEP = 0.1

MAX_RETRIES = 15
MAX_RESPONSE_TIME = None


def setup_pool(n_agents):
    ports = get_ports(n_agents)
    ip = get_ip()
    pool = ClientPool()
    for port in ports:
        pool.add(ClientInfo(ip, port))
    return pool


class MissionTimeoutException(Exception):
    pass


class MalmoInterface:

    def __getstate__(self):
        return {}

    def __setstate__(self, state):
        self.agent_host = AgentHost()

    def __init__(self):
        self.agent_host = AgentHost()

    def get_world_state(self):
        return self.agent_host.getWorldState()

    def move(self, speed):
        self.agent_host.sendCommand(f"move {speed}")

    def turn(self, speed):
        self.agent_host.sendCommand(f"turn {speed}")

    def strafe(self, speed):
        self.agent_host.sendCommand(f"strafe {speed}")

    def pitch(self, speed):
        self.agent_host.sendCommand(f"pitch {speed}")

    def jump(self, active):
        self.agent_host.sendCommand(f"jump {active:d}")

    def attack(self, active):
        self.agent_host.sendCommand(f"attack {active:d}")

    def discrete_use(self):
        time.sleep(DISCRETE_USE_SLEEP)
        self.agent_host.sendCommand("use")
        time.sleep(DISCRETE_USE_SLEEP)

    def select_on_hotbar(self, position):
        self.agent_host.sendCommand(f"hotbar.{position + 1} 1")  # press
        self.agent_host.sendCommand(f"hotbar.{position + 1} 0")  # release
        time.sleep(HOT_BAR_SLEEP)

    def craft(self, item, variant=None):
        if variant is None or variant == variants.OAK:
            self.agent_host.sendCommand(f"craft {item}")
        elif item == items.items.FENCE:
            self.agent_host.sendCommand(f"craft {variant}_{item}")
        else:
            self.agent_host.sendCommand(f"craft {item} {variant}")
        time.sleep(CRAFT_SLEEP)

    def swap_items(self, position1, position2):
        self.agent_host.sendCommand("swapInventoryItems {0} {1}".format(position1, position2))

    def activate_effect(self, effect, effect_time, amplifier):
        self.agent_host.sendCommand(f"chat /effect @p {effect} {effect_time} {amplifier}")

    def spawn_zombie(self):
        # self.agent_host.sendCommand("chat /summon zombie 105 10 9 {HandItems:[{Count:1,id:diamond_sword}]}")
        self.agent_host.sendCommand("chat /summon zombie 116 10 9 {HandItems:[{Count:1,id:stone_sword}]}")

    def start_multi_agent_mission(self, mission_data, i):
        mission = MissionSpec(mission_data.get_xml(), True)
        mission_record = MissionRecordSpec()
        pool = setup_pool(mission_data.n_agents)

        for retry in range(MAX_RETRIES):
            try:
                self.agent_host.startMission(mission, pool, mission_record, i, mission_data.experiment_id)
                break
            except RuntimeError as e:
                print("Error starting world:", e)
                if retry == MAX_RETRIES - 1:
                    exit(1)
                else:
                    time.sleep(4)

    def restart_minecraft(self, world_state, client_info, message=""):
        """"Attempt to quit world if running and kill the client"""
        if world_state.is_mission_running:
            self.agent_host.sendCommand("quit")
            time.sleep(10)
        self.agent_host.killClient(client_info)
        raise MissionTimeoutException(message)

    def wait_for_mission(self):
        print("Waiting for the world to start", end=' ')
        start_time = time.time()
        world_state = self.get_world_state()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            if MAX_RESPONSE_TIME is not None and time.time() - start_time > MAX_RESPONSE_TIME:
                print("Max delay exceeded for world to begin")
                self.restart_minecraft(world_state, "begin world")
            world_state = self.get_world_state()
            for error in world_state.errors:
                print("Error:", error.text)
        print()

    def quit(self):
        self.agent_host.sendCommand("quit")
