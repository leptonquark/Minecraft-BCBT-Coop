import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from bt.conditions import HasItemEquipped
from goals.agentless_condition import AgentlessCondition
from items.items import DIAMOND_PICKAXE
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from world.missiondata import MissionData
from world.observation import Observation


class MultiAgentProcess(mp.Process):

    def __init__(self, agent_names):
        super(mp.Process, self).__init__()
        self.agent_names = agent_names
        self.goals = [AgentlessCondition(HasItemEquipped, [DIAMOND_PICKAXE])]
        self.mission_data = MissionData(self.goals, self.agent_names)

    def run(self):

        agents = [MinerAgent(name) for name in self.agent_names]

        for i, agent in enumerate(agents):
            agent.start_multi_agent_mission(self.mission_data, i)
        for agent in agents:
            agent.wait_for_mission()

        trees = [BackChainTree(agent, self.goals) for agent in agents]

        last_delta = time.time()

        world_states = [agent.get_next_world_state() for agent in agents]

        while None not in world_states and all(world_state.is_mission_running for world_state in world_states):
            for i, agent in enumerate(agents):
                world_states[i] = agent.get_next_world_state()
                observation = Observation(world_states[i].observations, self.mission_data)
                agent.set_observation(observation)
                trees[i].root.tick_once()
                trees[i].print_tip()
                last_delta = check_timeout(agent, world_states[i], last_delta)
