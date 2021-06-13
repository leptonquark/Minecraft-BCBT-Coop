import time

from malmo.MalmoPython import AgentHost
from world.observation import get_horizontal_distance, get_turn_direction, get_wanted_pitch, get_yaw_from_vector, \
    get_pitch_change

CRAFT_SLEEP = 0.25
SWAP_SLEEP = 0.25
HOT_BAR_SLEEP = 0.1

MOVE_THRESHOLD = 5
MIN_MOVE_SPEED = 0.05


def get_move_speed(horizontal_distance):
    if horizontal_distance >= MOVE_THRESHOLD:
        return 1
    else:
        return max(horizontal_distance / MOVE_THRESHOLD, MIN_MOVE_SPEED)


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
        """"Attempt to quit world if running and kill the client"""
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

    def move_forward(self, horizontal_distance):
        self.attack(False)

        move_speed = get_move_speed(horizontal_distance)
        self.move(move_speed)

        pitch_req = get_pitch_change(self.observation.pitch, 0)
        self.pitch(pitch_req)

    def turn(self, speed):
        self.agent_host.sendCommand("turn {0}".format(speed))

    def turn_towards(self, distance):
        wanted_yaw = get_yaw_from_vector(distance)
        current_yaw = self.observation.yaw
        turn_direction = get_turn_direction(current_yaw, wanted_yaw)
        self.turn(turn_direction)
        return turn_direction != 0

    def pitch(self, speed):
        self.agent_host.sendCommand("pitch {0}".format(speed))

    def pitch_towards(self, distance):
        mat_horizontal_distance = get_horizontal_distance(distance)
        wanted_pitch = get_wanted_pitch(mat_horizontal_distance, -1 + distance[1])
        current_pitch = self.observation.pitch
        pitch_req = get_pitch_change(current_pitch, wanted_pitch)
        self.pitch(pitch_req)
        return pitch_req != 0

    def jump(self, active):
        self.agent_host.sendCommand("jump {0:d}".format(active))

    def attack(self, active):
        self.agent_host.sendCommand("attack {0:d}".format(active))

    def place_block(self):
        self.agent_host.sendCommand("use")
        time.sleep(0.25)
#        time.sleep(0.001)
#        self.agent_host.sendCommand("use 0")

    def use(self, active):
        self.agent_host.sendCommand("use {0:d}".format(active))
