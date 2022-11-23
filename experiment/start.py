# Start a MultiAgentProcess with various amount of agents
# Store the time?
# Store the path (stretch)
# Being able to choose whether to use cooperative or individualistic agents
import multiprocessing as mp
import time

from experiment.configurations import config_default_world_generator, config_flat_world_generator
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.names import get_names
from world.missiondata import MissionData

if __name__ == '__main__':
    reset = True
    flat_world = True
    n_test_runs = 15
    agents_max = 3

    output = ["collaborative,agents,internal_id,time"]

    run = 0
    start_time = time.time()
    for n_agents in range(3, agents_max + 1):
        for collaborative in [False, True]:
            for i in range(n_test_runs):
                start_time = time.time()
                amount = n_agents
                agent_names = get_names(amount)
                print(f"Starting Minecraft with {amount} clients...")
                if flat_world:
                    config = config_flat_world_generator
                else:
                    config = config_default_world_generator
                running_event = mp.Event()
                running_event.set()
                mission_data = MissionData(config, collaborative, reset, flat_world)
                process = MultiAgentRunnerProcess(running_event, mission_data)
                process.start()
                value = None
                while process.is_alive():
                    if process.pipe[0].poll():
                        value = process.pipe[0].recv()
                completion_time = value.completion_time if value else -1
                print(f"Total time: {completion_time}")
                output.append(f"{run},{collaborative},{n_agents},{i},{completion_time}")
                print(output)
                run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    with open('output.txt', 'w') as file:
        file.write('\n'.join(output))
