from bt.conditions import HasItemEquipped
from goals.agentless_condition import AgentlessCondition
from items.items import DIAMOND_PICKAXE
from malmoutils.minecraft import run_minecraft
from multiagentrunner import MultiAgentRunner

if __name__ == "__main__":
    # agent_names = ["SteveBot"]
    agent_names = ["SteveBot", "AlexBot"]
    N_AGENTS = len(agent_names)

    run_minecraft(N_AGENTS)

    cat = None

    goals = [AgentlessCondition(HasItemEquipped, [DIAMOND_PICKAXE])]

    runner = MultiAgentRunner(agent_names, goals)
    runner.run_mission_async()
