import multiprocessing as mp
import time

from bt.back_chain_tree import BackChainTree
from bt.conditions import HasItemEquipped
from goals.agentless_condition import AgentlessCondition
from items.items import DIAMOND_PICKAXE
from malmoutils.agent import MinerAgent
from malmoutils.world_state import check_timeout
from multiagents.multiagentworld import MultiAgentWorld
from world.observation import Observation


class MultiAgentProcess(mp.Process):

    def __init__(self, agent_names):
        super(mp.Process, self).__init__()
        self.agent_names = agent_names

    def run(self):
        goals = [AgentlessCondition(HasItemEquipped, [DIAMOND_PICKAXE])]

        self.agents = [MinerAgent(name) for name in self.agent_names]
        self.world = MultiAgentWorld(self.agents, goals)
        self.trees = [BackChainTree(agent, goals) for agent in self.agents]

        last_delta = time.time()

        world_states = [agent.get_next_world_state() for agent in self.agents]

        while None not in world_states and all(world_state.is_mission_running for world_state in world_states):
            for i, agent in enumerate(self.agents):
                world_states[i] = agent.get_next_world_state()
                observation = Observation(world_states[i].observations, self.world.mission_data)
                agent.set_observation(observation)
                self.trees[i].root.tick_once()
                self.trees[i].print_tip()
                last_delta = check_timeout(self.world, world_states[i], last_delta)
