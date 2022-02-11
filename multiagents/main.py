from bt.conditions import HasItemEquipped
from goals.agentless_condition import AgentlessCondition
from items.items import DIAMOND_PICKAXE
from malmoutils.agent import MinerAgent
from malmoutils.minecraft import run_minecraft
from multiagentrunner import MultiAgentRunner

# agent_names = ["SteveBot"]
agent_names = ["SteveBot", "AlexBot"]
N_AGENTS = len(agent_names)

run_minecraft(N_AGENTS)

goals = [AgentlessCondition(HasItemEquipped, [DIAMOND_PICKAXE])]
agents = [MinerAgent(name) for name in agent_names]

runner = MultiAgentRunner(agents, goals)
runner.run_mission()
