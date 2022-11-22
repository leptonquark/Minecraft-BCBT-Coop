# Start a MultiAgentProcess with various amount of agents
# Store the time?
# Store the path (stretch)
# Being able to choose whether to use cooperative or individualistic agents
import multiprocessing as mp
import time

from goals.blueprint.blueprint import Blueprint, BlueprintType
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.names import get_names
from world.missiondata import MissionData

if __name__ == '__main__':
    reset = True
    n_test_runs = 15
    agents_max = 3

    output = []

    run = 0
    for n_agents in range(1, agents_max + 1):
        for collaborative in [False, True]:
            for i in range(n_test_runs):
                start_time = time.time()
                amount = n_agents
                agent_names = get_names(amount)
                print(f"Starting Minecraft with {amount} clients...")
                goals = Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9])
                running_event = mp.Event()
                running_event.set()
                mission_data = MissionData(goals, collaborative, reset, agent_names)
                process = MultiAgentRunnerProcess(running_event, mission_data)
                process.start()
                value = None
                while process.is_alive():
                    if process.pipe[0].poll():
                        value = process.pipe[0].recv()
                completion_time = value.completion_time if value else -1
                print(f"Total time: {completion_time}")
                output.append(f"{run}, {collaborative}, {n_agents}, {i}, {completion_time}")
                print(output)
                run += 1
    with open('output.txt', 'w') as file:
        file.write('\n'.join(output))
