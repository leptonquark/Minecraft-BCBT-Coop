import time

from malmoutils.world_state import check_timeout
from multiagents.multiagentprocess import MultiAgentProcess
from world.missiondata import MissionData
from world.observation import Observation

TREE_LOG_FILE_NAME = "../log/tree.txt"


class MultiAgentRunner:

    def __init__(self, agent_names, goals=None):
        if goals is None:
            goals = []

        self.goals = goals
        self.agent_names = agent_names
        # self.agents = [MinerAgent(name) for name in agent_names]
        #
        # self.world = MultiAgentWorld(self.agents, goals)
        #
        # self.night_vision = self.world.mission_data.night_vision
        #
        # self.trees = [BackChainTree(agent, goals) for agent in self.agents]
        # save_tree_to_log(self.trees[0].root, TREE_LOG_FILE_NAME)
        #
        # self.last_delta = time.time()

    def run_mission(self):
        last_delta = time.time()

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
                last_delta = check_timeout(self.world, world_states[i], last_delta)

    def run_mission_async(self):
        last_delta = time.time()

        print("ois")

        #        if self.night_vision:
        #            [agent.activate_night_vision() for agent in self.agents]
        mission_data = MissionData(self.goals, self.agent_names)

        processes = [MultiAgentProcess(mission_data, [self.agent_names[i]], [i]) for i in range(len(self.agent_names))]
        for process in processes:
            process.start()
        for process in processes:
            process.join()
