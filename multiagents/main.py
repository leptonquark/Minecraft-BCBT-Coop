from bt.conditions import HasItemEquipped, HasItem
from goals.agentless_condition import AgentlessCondition
from items import items
from malmoutils.minecraft import run_minecraft
from multiagentrunner import MultiAgentRunner

if __name__ == "__main__":
    # agent_names = ["SteveBot"]
    agent_names = ["SteveBot", "AlexBot"]
    # run_minecraft(n_clients=len(agent_names))


    # goals = [AgentlessCondition(HasItemEquipped, [items.DIAMOND_PICKAXE])]

    goals = [AgentlessCondition(HasItemEquipped, [items.DIAMOND_PICKAXE])]

    runner = MultiAgentRunner(agent_names, goals)
    runner.run_mission_async()
