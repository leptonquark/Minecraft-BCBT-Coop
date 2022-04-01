import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from utils.visualisation import save_tree_to_log
from world.observation import Observation


class MultiAgentProcess(mp.Process):

    def __init__(self, mission_data, role, goals):
        super(MultiAgentProcess, self).__init__()
        self.mission_data = mission_data
        self.goals = goals
        self.role = role

    def run(self):
        agent_name = self.mission_data.agent_names[self.role]
        agent = MinerAgent(agent_name)

        agent.start_multi_agent_mission(self.mission_data, self.role)
        agent.wait_for_mission()

        if self.mission_data.night_vision:
            agent.activate_night_vision()

        tree = BackChainTree(agent, self.goals)
        save_tree_to_log(tree.root, "steel_pickaxe")

        last_delta = time.time()

        world_state = agent.get_next_world_state()

        while world_state is not None and world_state.is_mission_running:
            world_state = agent.get_next_world_state()
            observation = Observation(world_state.observations, self.mission_data)
            agent.set_observation(observation)
            tree.root.tick_once()
            #print(tree_to_string(tree.root))
            print(tree.root.tip().name)
            last_delta = check_timeout(agent, world_state, last_delta)
