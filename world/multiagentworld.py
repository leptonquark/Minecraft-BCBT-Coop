import time
import uuid

from malmo import malmoutils
from malmo.MalmoPython import MissionSpec, ClientInfo, ClientPool, MissionRecordSpec

from world.missiondata import MissionData

TIME_LIMIT_IN_SECONDS = 1000
VIDEO_SIZE = (800, 600)

RECORDING_NAME = "saved_data"

IP = "127.0.0.1"
BASE_PORT = 10000

MAX_RETRIES = 15
MAX_RESPONSE_TIME = 60


def setup_mission(mission_data):
    mission = MissionSpec(mission_data.get_xml(), True)
    mission.timeLimitInSeconds(TIME_LIMIT_IN_SECONDS)
    mission.requestVideo(*VIDEO_SIZE)
    return mission


def setup_mission_record(agent):
    mission_record = MissionRecordSpec()
    return mission_record


def setup_pool(client_info):
    pool = ClientPool()
    for client in client_info:
        pool.add(client)
    return pool


def setup_experiment_id():
    experiment_id = str(uuid.uuid1())
    print(f"experiment id {experiment_id}")
    return experiment_id


class MultiAgentWorld:

    def __init__(self, agents, goals):

        self.agents = agents

        malmoutils.parse_command_line(self.agents[0].get_agent_host(), [''])

        self.mission_data = MissionData(goals, [agent.name for agent in self.agents])
        self.mission = setup_mission(self.mission_data)
        self.mission_record = setup_mission_record(self.agents[0])

        self.client_info = [ClientInfo(IP, BASE_PORT + i) for i in range(len(agents))]
        self.pool = setup_pool(self.client_info)

        self.experiment_id = setup_experiment_id()

        for i, agent in enumerate(self.agents):
            self.start_world(i)
        self.wait_for_mission()

    def start_world(self, i):
        for retry in range(MAX_RETRIES):
            try:
                self.agents[i].start_multi_agent_mission(self.mission, self.pool, self.mission_record, i,
                                                         self.experiment_id)
                break
            except RuntimeError as e:
                if retry == MAX_RETRIES - 1:
                    print("Error starting world:", e)
                    exit(1)
                else:
                    time.sleep(4)

    def wait_for_mission(self):

        print("Waiting for the world to start", end=' ')
        start_time = time.time()
        world_state = self.agents[0].get_world_state()
        while not world_state.has_mission_begun:
            print(".", end="")
            time.sleep(0.1)
            if time.time() - start_time > MAX_RESPONSE_TIME:
                print("Max delay exceeded for world to begin")
                self.agents[0].restart_minecraft(world_state, "begin world")
            world_state = self.agents[0].get_world_state()
            for error in world_state.errors:
                print("Error:", error.text)
        print()
