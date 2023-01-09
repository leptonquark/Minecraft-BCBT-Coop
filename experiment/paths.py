import numpy as np

from experiment import experiments
from experiment.test import run_test
from multiagents.cooperativity import Cooperativity


def get_path(cooperativity, experiment, n_agents):
    def on_value(value):
        for i, agent_position in enumerate(value.agent_positions):
            if agent_position is not None:
                if len(agent_positions[i]) == 0 or not np.array_equal(agent_position, agent_positions[i][-1]):
                    agent_positions[i].append(agent_position)

    agent_positions = [[] for _ in range(n_agents)]
    run_test(cooperativity, experiment, n_agents, on_value)
    concat_agent_positions = [np.array(agent_position) for agent_position in agent_positions]
    for i, agent_position in enumerate(concat_agent_positions):
        np.savetxt(f"agent_position_{experiment.id}_{i}.csv", agent_position, delimiter=",")


if __name__ == "__main__":
    get_path(Cooperativity.COOPERATIVE, experiments.experiment_flat_world, 3)
