from goals.blueprint import Blueprint, BlueprintType
from malmoutils.agent import MinerAgent
from malmoutils.minecraft import run_minecraft
from multiagentrunner import MultiAgentRunner

N_AGENTS = 2

run_minecraft(N_AGENTS)

goals = Blueprint.get_blueprint(BlueprintType.StraightFence)
agents = [MinerAgent() for _ in range(N_AGENTS)]

runner = MultiAgentRunner(agents, goals)
runner.run_mission()
