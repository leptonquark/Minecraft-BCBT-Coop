import time

from bt.back_chain_tree import BackChainTree
from utils.visualisation import save_tree_to_log
from world.multiagentworld import MultiAgentWorld
from world.observation import Observation

MAX_DELAY = 60

TREE_LOG_FILE_NAME = "log/tree.txt"


class MultiAgentRunner:

    def __init__(self, agents, goals=None):
        if goals is None:
            goals = []

        self.agents = agents
        self.world = MultiAgentWorld(agents, goals)

        self.night_vision = self.world.mission_data.night_vision

        self.trees = [BackChainTree(agent, goals) for agent in self.agents]
        save_tree_to_log(self.trees[0].root, TREE_LOG_FILE_NAME)

        self.last_delta = time.time()

    def run_mission(self):
        self.last_delta = time.time()

        world_states = [agent.get_next_world_state() for agent in self.agents]

        if self.night_vision:
            [agent.activate_night_vision() for agent in self.agents]

        while None not in world_states and all(world_state.is_mission_running for world_state in world_states):
            for i, agent in enumerate(self.agents):
                world_states[i] = agent.get_next_world_state()
                observation = Observation(world_states[i].observations, self.world.mission_data)
                agent.set_observation(observation)
                self.trees[i].root.tick_once()
                self.trees[i].print_tip()
                self.check_timeout(self.world, world_states[i])

    def check_timeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
                world_state.number_of_observations_since_last_state > 0 or
                world_state.number_of_rewards_since_last_state > 0):
            self.last_delta = time.time()
        else:
            if time.time() - self.last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")
