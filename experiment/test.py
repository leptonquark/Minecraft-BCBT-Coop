import time
from pathlib import Path

import experiment.experiments as experiments
from goals.blueprint.blueprint import Blueprint, BlueprintType
from items import items
from multiagents.cooperativity import Cooperativity
from multiagents.multiagentrunnerprocess import MultiAgentRunnerProcess
from utils.file import create_file_and_write
from world.missiondata import MissionData

EXPERIMENT_PATH = Path("log/experiments")

cooperativity_to_collaborative = {
    Cooperativity.INDEPENDENT: False,
    Cooperativity.COOPERATIVE: True,
    Cooperativity.COOPERATIVE_WITH_CATCHUP: "Both"
}


def run_pickaxe_tests():
    experiment = experiments.experiment_get_10_stone_pickaxe
    n_test_runs = 15
    agents_max = 3
    cooperativities = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE, Cooperativity.COOPERATIVE_WITH_CATCHUP]
    pickaxes = [items.DIAMOND_PICKAXE, items.IRON_PICKAXE, items.STONE_PICKAXE, items.WOODEN_PICKAXE, None]
    output = ["collaborative,agents,pickaxe,internal_id,time"]
    run = 0
    start_time = time.time()
    for pickaxe in pickaxes:
        experiment.start_inventory = [pickaxe] if pickaxe else []
        for n_agents in range(1, agents_max + 1):
            for cooperativity in cooperativities:
                for i in range(n_test_runs):
                    completion_time = run_test(cooperativity, experiment, n_agents)
                    collaborative = cooperativity_to_collaborative[cooperativity]
                    output.append(f"{run},{collaborative},{n_agents},{pickaxe},{i},{completion_time}")
                    print(output)
                    run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    file_name = f"output_{experiment.id}.csv"
    create_file_and_write(file_name, lambda file: file.write('\n'.join(output)))


def run_variable_delta_tests():
    experiment = experiments.experiment_flat_world
    n_test_runs = 15
    agents_max = 3
    cooperativities = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE, Cooperativity.COOPERATIVE_WITH_CATCHUP]
    deltas = [5, 10, 15, 20, 25]
    output = ["collaborative,agents,delta,internal_id,time"]
    run = 0
    start_time = time.time()
    for delta in deltas:
        experiment.goals = [Blueprint.get_blueprint(BlueprintType.PointGrid, [130, 9, 9], delta)]
        for n_agents in range(1, agents_max + 1):
            for cooperativity in cooperativities:
                for i in range(n_test_runs):
                    completion_time = run_test(cooperativity, experiment, n_agents)
                    collaborative = cooperativity_to_collaborative[cooperativity]
                    output.append(f"{run},{collaborative},{n_agents},{delta},{i},{completion_time}")
                    print(output)
                    run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    file_name = f"output_{experiment.id}_delta.csv"
    create_file_and_write(file_name, lambda file: file.write('\n'.join(output)))


def run_tests():
    experiment = experiments.experiment_default_world
    n_test_runs = 15
    agents_max = 3
    cooperativities = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE, Cooperativity.COOPERATIVE_WITH_CATCHUP]
    output = ["collaborative,agents,internal_id,time"]
    run = 0
    start_time = time.time()
    for n_agents in range(1, agents_max + 1):
        for cooperativity in cooperativities:
            for i in range(n_test_runs):
                completion_time = run_test(cooperativity, experiment, n_agents)
                collaborative = cooperativity_to_collaborative[cooperativity]
                output.append(f"{run},{collaborative},{n_agents},{i},{completion_time}")
                print(output)
                run += 1
    print(f"Total time all experiments: {time.time() - start_time}")
    file_name = f"output_{experiment.id}.csv"
    create_file_and_write(file_name, lambda file: file.write('\n'.join(output)))


def run_test(cooperativity, experiment, n_agents, on_value=None):
    exp_time = time.time()
    print(f"Starting Minecraft with {n_agents} clients...")
    mission_data = MissionData(experiment, cooperativity, True, n_agents)
    process = MultiAgentRunnerProcess(mission_data)
    process.start()
    value = None
    while process.is_alive():
        if process.pipe[0].poll():
            value = process.pipe[0].recv()
            if on_value is not None:
                on_value(value)
    completion_time = value.completion_time if value else -1
    print(f"Completion time: {completion_time}. Experiment time: {time.time() - exp_time}")
    return completion_time


if __name__ == '__main__':
    run_test(Cooperativity.COOPERATIVE, experiments.experiment_flat_world, 3)
