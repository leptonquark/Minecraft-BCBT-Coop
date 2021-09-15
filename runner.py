import codecs
import pathlib
import time

from bt.back_chain_tree import BackChainTree
from malmoutils.agent import MinerAgent
from utils.file import create_file_and_write
from utils.string import tree_to_string
from utils.visualisation import tree_to_drawio_xml, tree_to_drawio_csv, render_tree
from world.observation import Observation
from world.world import World

MAX_DELAY = 60
EXTRA_SLEEP_TIME = 0.1

TREE_LOG_FILE_NAME = "log/tree.txt"


class Runner:

    def __init__(self, agent, goals=None):
        if goals is None:
            goals = []

        self.agent = agent
        self.world = World(self.agent, goals)

        self.night_vision = self.world.mission_data.night_vision

        self.tree = BackChainTree(self.agent, goals)
        create_file_and_write(TREE_LOG_FILE_NAME, lambda file: file.write(tree_to_drawio_csv(self.tree.root)))

        self.last_delta = time.time()
        self.world.start_world()

    def run_mission(self):
        self.last_delta = time.time()

        world_state = self.get_next_world_state()

        if self.night_vision:
            self.agent.activate_night_vision()

        while world_state is not None and world_state.is_mission_running:
            observation = Observation(self.get_next_world_state().observations, self.world.mission_data)
            self.agent.set_observation(observation)
            # observation.print()

            self.tree.root.tick_once()

            # print(tree_to_string(self.tree.root))

            self.check_timeout(self.world, world_state)

    def get_next_world_state(self):
        observations = None
        world_state = None
        while observations is None or len(observations) == 0:
            world_state = self.agent.get_world_state()
            observations = world_state.observations
        return world_state

    def check_timeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
                world_state.number_of_observations_since_last_state > 0 or
                world_state.number_of_rewards_since_last_state > 0):
            self.last_delta = time.time()
        else:
            if time.time() - self.last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")


def save_tree_to_log(tree, file):
    file.write(tree_to_drawio_csv(tree.root))
