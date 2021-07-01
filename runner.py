import time

from bt.back_chain_tree import BackChainTree
from utils.visualisation import tree_to_drawio_xml, tree_to_drawio_csv, render_tree
from world.observation import Observation

MAX_DELAY = 60
EXTRA_SLEEP_TIME = 0.1
TREE_LOG_FILE_NAME = "log/tree.txt"


class Runner:

    def __init__(self, world, agent, goals=None):
        if goals is None:
            goals = []
        self.world = world
        self.agent = agent
        self.last_delta = time.time()

        self.night_vision = world.mission_data.night_vision

        self.tree = BackChainTree(agent, goals)

        #with open(TREE_LOG_FILE_NAME, "w") as file:
        #    file.write(tree_to_drawio_csv(self.tree.root))

        world.start_world()

    def run_mission(self):
        world_state = self.agent.get_world_state()

        self.last_delta = time.time()

        time.sleep(2)

        if self.night_vision:
            self.agent.activate_night_vision()

        while world_state.is_mission_running:
            observations = None
            while observations is None or len(observations) == 0:
                world_state = self.agent.get_world_state()
                observations = world_state.observations

            observation = Observation(observations, self.world.mission_data)
            self.agent.set_observation(observation)
            # observation.print()

            self.tree.root.tick_once()
            # print(tree_to_string(self.tree.root))

            self.check_timeout(self.world, world_state)

    def check_timeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
                world_state.number_of_observations_since_last_state > 0 or
                world_state.number_of_rewards_since_last_state > 0):
            self.last_delta = time.time()
        else:
            if time.time() - self.last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")
