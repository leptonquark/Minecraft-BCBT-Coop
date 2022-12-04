# Start a MultiAgentProcess with various amount of agents
# Store the time?
# Store the path (stretch)
# Being able to choose whether to use cooperative or individualistic agents
import multiprocessing as mp
import time

import experiment.experiments as experiments
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.file import create_file_and_write
from utils.names import get_names
from world.missiondata import MissionData

if __name__ == '__main__':
    reset = True
    flat_world = False
    n_test_runs = 15
    agents_max = 3

    output = ["collaborative,agents,internal_id,time"]

    run = 0
    start_time = time.time()
    for n_agents in range(1, agents_max + 1):
        for collaborative in [False, True]:
            for i in range(n_test_runs):
                exp_time = time.time()
                amount = n_agents
                agent_names = get_names(amount)
                print(f"Starting Minecraft with {amount} clients...")
                if flat_world:
                    configuration = experiments.experiment_flat_world
                else:
                    configuration = experiments.experiment_default_world
                running_event = mp.Event()
                running_event.set()
                mission_data = MissionData(configuration, collaborative, reset, agent_names)
                process = MultiAgentRunnerProcess(running_event, mission_data)
                process.start()
                value = None
                while process.is_alive():
                    if process.pipe[0].poll():
                        value = process.pipe[0].recv()
                completion_time = value.completion_time if value else -1
                print(f"Completion time: {completion_time}. Experiment time: {time.time() - exp_time}")
                output.append(f"{run},{collaborative},{n_agents},{i},{completion_time}")
                print(output)
                run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    gen = "fwg" if flat_world else "dwg"
    file_name = f"log/experiments/output_{gen}.csv"
    create_file_and_write(file_name, lambda file: file.write('\n'.join(output)))
