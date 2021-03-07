import MalmoPython
import malmoutils
import uuid
import time
from missiondata import MissionData

TIME_LIMIT_IN_SECONDS = 1000
VIDEO_SIZE = (800, 600)

RECORDING_NAME = "saved_data"

IP = "127.0.0.1"
PORT = 10000

MAX_RETRIES = 3
MAX_RESPONSE_TIME = 60


class MissionTimeoutException(Exception):
    pass


def setup_mission(mission_data):
    mission = MalmoPython.MissionSpec(mission_data.get_xml(), True)
    mission.timeLimitInSeconds(TIME_LIMIT_IN_SECONDS)
    mission.requestVideo(*VIDEO_SIZE)
    return mission


def setup_mission_record(agent_host):
    mission_record = malmoutils.get_default_recording_object(agent_host, RECORDING_NAME)
    return mission_record


def setup_pool(client_info):
    pool = MalmoPython.ClientPool()
    pool.add(client_info)
    return pool


def setup_experiment_id():
    experiment_id = str(uuid.uuid1())
    print("experiment id " + experiment_id)
    return experiment_id


class World:

    def __init__(self, agent_host):

        self.agent_host = agent_host

        malmoutils.parse_command_line(agent_host, [''])

        self.mission_data = MissionData()
        self.mission = setup_mission(self.mission_data)
        self.mission_record = setup_mission_record(agent_host)

        self.client_info = MalmoPython.ClientInfo(IP, PORT)
        self.pool = setup_pool(self.client_info)

        self.experiment_id = setup_experiment_id()

    def start_world(self):
        for retry in range(MAX_RETRIES):
            try:
                self.agent_host.startMission(self.mission, self.pool, self.mission_record, 0, self.experiment_id)
                break
            except RuntimeError as e:
                if retry == MAX_RETRIES - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)

        print("Waiting for the mission to start", end=' ')
        start_time = time.time()
        world_state = self.agent_host.getWorldState()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            if time.time() - start_time > MAX_RESPONSE_TIME:
                print("Max delay exceeded for mission to begin")
                self.restart_minecraft(world_state, "begin mission")
            world_state = self.agent_host.getWorldState()
            for error in world_state.errors:
                print("Error:", error.text)
        print()

    def restart_minecraft(self, world_state, message=""):
        """"Attempt to quit mission if running and kill the client"""
        if world_state.is_mission_running:
            self.agent_host.sendCommand("quit")
            time.sleep(10)
        self.agent_host.killClient(self.client_info)
        raise MissionTimeoutException(message)
