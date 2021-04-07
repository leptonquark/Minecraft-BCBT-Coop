import time

from bt.back_chain_tree import BackChainTree
from observation import Observation
from py_trees.display import ascii_tree
from utils.string import tree_to_string
from utils.time import ms_to_seconds

MAX_DELAY = 60
EXTRA_SLEEP_TIME = 0.1


class Runner:

    def __init__(self, world, agent, goals=None):
        if goals is None:
            goals = []
        self.world = world
        self.agent = agent
        self.last_delta = time.time()

        self.grid_size = world.mission_data.get_grid_size()
        self.night_vision = world.mission_data.night_vision
        self.sleep_time = ms_to_seconds(world.mission_data.ms_per_tick)

        self.tree = BackChainTree(agent, goals)

    def run_mission(self):
        world_state = self.agent.get_world_state()

        self.last_delta = time.time()

        time.sleep(2)

        if self.night_vision:
            self.agent.activate_night_vision()

        # main loop:
        while world_state.is_mission_running:
            # SLEEP
            time.sleep(self.sleep_time + EXTRA_SLEEP_TIME)

            # SEE
            world_state = self.agent.get_world_state()
            observation = Observation(world_state.observations, self.grid_size)
            self.agent.set_observation(observation)
            #observation.print()

            # DO
            self.tree.root.tick_once()
            print(ascii_tree(self.tree.root))
            #print(tree_to_string(self.tree.root))

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
