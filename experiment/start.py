# Start a MultiAgentProcess with various amount of agents
# Store the time?
# Store the path (stretch)
# Being able to choose whether to use cooperative or individualistic agents
import multiprocessing as mp
import time
from pathlib import Path

import experiment.experiments as experiments
from multiagents.cooperativity import Cooperativity
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.file import create_file_and_write
from utils.names import get_names
from world.missiondata import MissionData

EXPERIMENT_PATH = Path("log/experiments")

if __name__ == '__main__':
    reset = True
    experiment = experiments.experiment_flat_world
    n_test_runs = 15
    agents_max = 3
    cooperativites = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE, Cooperativity.COOPERATIVE_WITH_CATCHUP]

    output = ["collaborative,agents,internal_id,time"]

    run = 0
    start_time = time.time()
    for n_agents in range(1, agents_max + 1):
        for cooperative in cooperativites:
            for i in range(n_test_runs):
                exp_time = time.time()
                amount = n_agents
                agent_names = get_names(amount)
                print(f"Starting Minecraft with {amount} clients...")
                running_event = mp.Event()
                running_event.set()
                mission_data = MissionData(experiment, cooperative, reset, agent_names)
                process = MultiAgentRunnerProcess(running_event, mission_data)
                process.start()
                value = None
                while process.is_alive():
                    if process.pipe[0].poll():
                        value = process.pipe[0].recv()
                completion_time = value.completion_time if value else -1
                print(f"Completion time: {completion_time}. Experiment time: {time.time() - exp_time}")
                if cooperative == Cooperativity.COOPERATIVE:
                    collaborative = True
                elif cooperative == Cooperativity.INDEPENDENT:
                    collaborative = False
                else:
                    collaborative = "Both"
                output.append(f"{run},{collaborative},{n_agents},{i},{completion_time}")
                print(output)
                run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    file_name = f"output_{experiment.id}.csv"
    file_path = EXPERIMENT_PATH / file_name
    create_file_and_write(file_name, lambda file: file.write('\n'.join(output)))
