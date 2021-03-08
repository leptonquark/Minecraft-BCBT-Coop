import time

from py_trees.display import ascii_tree

from observation import Observation
from tree import BehaviourTree

MAX_DELAY = 60


class Runner:

    def __init__(self, world, agent_host, goals=None):
        if goals is None:
            goals = []
        self.world = world
        self.agent_host = agent_host
        self.last_delta = time.time()

        self.night_vision = world.mission_data.night_vision
        self.grid_size = world.mission_data.get_grid_size()

        self.name = world.mission_data.name

        self.tree = BehaviourTree(agent_host)

    def run_mission(self):
        world_state = self.agent_host.getWorldState()

        self.last_delta = time.time()

        time.sleep(1)

        if self.night_vision:
            self.agent_host.sendCommand("chat /effect @p night_vision 99999 255")

        # main loop:
        while world_state.is_mission_running:
            # SLEEP
            time.sleep(0.5)

            # SEE
            world_state = self.agent_host.getWorldState()
            observation = Observation(world_state.observations, self.grid_size)
            self.agent_host.set_observation(observation)
            # observation.print()

            # DO
            self.tree.root.tick_once()
            print(ascii_tree(self.tree.root))

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
