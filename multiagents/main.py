from bt.conditions import HasItemEquipped
from goals.agentless_condition import AgentlessCondition
from items.items import DIAMOND_PICKAXE
from malmoutils.agent import MinerAgent
from malmoutils.minecraft import run_minecraft
from multiagentrunner import MultiAgentRunner

N_AGENTS = 2

run_minecraft(N_AGENTS)

goals = [AgentlessCondition(HasItemEquipped, [DIAMOND_PICKAXE])]
agents = [MinerAgent() for _ in range(N_AGENTS)]

runner = MultiAgentRunner(agents, goals)
runner.run_mission()
