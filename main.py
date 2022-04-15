from goals.blueprint import Blueprint, BlueprintType
from malmoutils.minecraft import run_minecraft
from multiagents.multiagentrunner import MultiAgentRunner

if __name__ == "__main__":
    # agent_names = ["SteveBot"]
    agent_names = ["SteveBot", "AlexBot"]
    run_minecraft(n_clients=len(agent_names))

    # goals = [AgentlessCondition(HasItemEquipped, [items.DIAMOND_PICKAXE])]
    # goals = [AgentlessCondition(HasItem, [items.WOODEN_FENCE, 4])]
    goals = Blueprint.get_blueprint(BlueprintType.Points, [136, 71, 11])

    runner = MultiAgentRunner(agent_names, goals)
    runner.run_mission_async()
