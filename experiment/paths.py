import matplotlib.pyplot as plt
import numpy as np

from experiment import experiments
from experiment.test import run_test
from goals.blueprint.blueprint import Blueprint
from items import items
from multiagents.cooperativity import Cooperativity
from world.world_generator import CustomWorldGenerator

AGENT_COLORS = ['r', 'g', 'b']
COOPERATIVITY_NAMES = {
    Cooperativity.INDEPENDENT: "traditional backward chaining",
    Cooperativity.COOPERATIVE: "simple collaboration",
    Cooperativity.COOPERATIVE_WITH_CATCHUP: "proposed approach"
}
CHUNK_COLORS = {
    items.STONE: 'gray',
    items.LOG_2: 'brown'
}
CHUNK_NAMES = {
    items.STONE: "Stone",
    items.LOG_2: "Wood"
}


def get_paths(experiment, n_agents):
    for cooperativity in Cooperativity:
        get_path(cooperativity, experiment, n_agents)


def get_path(cooperativity, experiment, n_agents):
    def on_value(value):
        for j, agent_position in enumerate(value.agent_positions):
            if agent_position is not None:
                if len(agent_positions[j]) == 0 or not np.array_equal(agent_position, agent_positions[j][-1]):
                    agent_positions[j].append(agent_position)

    agent_positions = [[] for _ in range(n_agents)]
    run_test(cooperativity, experiment, n_agents, on_value)
    concat_agent_positions = [np.array(agent_position) for agent_position in agent_positions]
    cooperativity_name = cooperativity.name.lower()
    for i, agent_position in enumerate(concat_agent_positions):
        np.savetxt(f"agent_position_{experiment.id}_{cooperativity_name}_{i}.csv", agent_position, delimiter=",")


def plot_paths(experiment, n_agents, center, width):
    goal_positions = []
    for goal in experiment.goals:
        if isinstance(goal, Blueprint):
            goal_positions.append(goal.positions)
    if goal_positions:
        target_points = np.concatenate(goal_positions)
    else:
        target_points = None
    print(experiment.world_generator)
    if isinstance(experiment.world_generator, CustomWorldGenerator):
        cuboids = experiment.world_generator.cuboids
    else:
        cuboids = []

    for cooperativity in Cooperativity:
        cooperativity_name = cooperativity.name.lower()

        fig, ax = plt.subplots()
        ax.set_aspect('equal', adjustable='box')

        plot_target_points(target_points)
        plot_agents(cooperativity_name, experiment, n_agents)
        plot_cuboids(ax, cuboids)

        lgd = plt.legend(ncol=5, loc='lower center', bbox_to_anchor=(0.5, -0.2), fancybox=True)

        plt.xlim(center[0] - width, center[0] + width)
        plt.ylim(center[1] - width, center[1] + width)
        plt.title(f"Paths placing fence posts with {COOPERATIVITY_NAMES[cooperativity]}", fontsize=11, pad=14)

        plt.savefig(f"path_{experiment.id}_{cooperativity_name}.png", bbox_extra_artists=(lgd,), bbox_inches='tight')
        plt.show(box_extra_artists=(lgd,), bbox_inches='tight')


def plot_target_points(target_points):
    if target_points is not None:
        plt.scatter(target_points[:, 0], target_points[:, 2], c="k", s=60, marker='x', label="Fence posts")


def plot_agents(cooperativity_name, experiment, n_agents):
    for i in range(n_agents):
        agent_position = np.loadtxt(f"agent_position_{experiment.id}_{cooperativity_name}_{i}.csv", delimiter=",")
        if agent_position.ndim == 1:
            agent_position = np.array([agent_position])
        plt.plot(agent_position[:, 0], agent_position[:, 2], color=AGENT_COLORS[i], linestyle='dashed',
                 label=f"Agent {i}")
        plt.scatter(agent_position[0, 0], agent_position[0, 2], color=AGENT_COLORS[i], marker='*')


def plot_cuboids(ax, cuboids):
    for cuboid in cuboids:
        x0 = cuboid.range[0, 0]
        y0 = cuboid.range[0, 2]
        w = cuboid.range[1, 0] - cuboid.range[0, 0]
        h = cuboid.range[1, 2] - cuboid.range[0, 2]
        name = CHUNK_NAMES[cuboid.type]
        color = CHUNK_COLORS[cuboid.type]
        ax.add_patch(plt.Rectangle((x0, y0), w, h, facecolor=color, edgecolor='k', label=name))


if __name__ == "__main__":
    plot_paths(experiments.experiment_flat_world, 3, (130, 10), 40)
    # plot_paths(experiments.experiment_get_10_stone_pickaxe_manual, 3, (0, 0), 30)
