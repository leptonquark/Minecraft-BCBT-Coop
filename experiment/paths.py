from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from experiment import experiments
from experiment.test import run_test
from goals.blueprint.blueprint import Blueprint
from items import items
from multiagents.cooperativity import Cooperativity
from utils.file import get_project_root, create_folders
from utils.plot import save_figure
from world.worldgenerator import CustomWorldGenerator

AGENT_COLORS = ['r', 'g', 'b']
COOPERATIVITY_NAMES = {
    Cooperativity.INDEPENDENT: "Traditional BC",
    Cooperativity.COOPERATIVE: "Collaborative BC",
    Cooperativity.COOPERATIVE_WITH_CATCHUP: "Collaborative BC w. backup"
}
CHUNK_COLORS = {
    items.STONE: 'gray',
    items.LOG_2: 'brown'
}
CHUNK_NAMES = {
    items.STONE: "Stone",
    items.LOG_2: "Wood"
}
EXPERIMENT_TITLES = {
    experiments.experiment_flat_world.id: "placing fence posts in the flat world",
    experiments.experiment_get_10_stone_pickaxe_manual.id: "gathering stone pickaxe materials in the test area",
}
PATHS_FOLDER_NAME = Path("log/paths")
PATH_COOPERATIVITIES = [Cooperativity.INDEPENDENT, Cooperativity.COOPERATIVE]


def get_paths(experiment, n_agents):
    for cooperativity in PATH_COOPERATIVITIES:
        get_path(cooperativity, experiment, n_agents)


def get_path(cooperativity, experiment, n_agents):
    agent_positions = [[] for _ in range(n_agents)]

    def on_value(value):
        for j, agent_position in enumerate(value.agent_positions):
            if agent_position is not None:
                if len(agent_positions[j]) == 0 or not np.array_equal(agent_position, agent_positions[j][-1]):
                    agent_positions[j].append(agent_position)

    run_test(cooperativity, experiment, n_agents, on_value)
    concat_agent_positions = [np.array(agent_position) for agent_position in agent_positions]
    for i, agent_position in enumerate(concat_agent_positions):
        np.savetxt(get_path_file_name(experiment, n_agents, cooperativity, i), agent_position, delimiter=",")


def get_path_file_name(experiment, n_agents, cooperativity, role):
    file_name = f"agent_position_{experiment.id}_{n_agents}_{cooperativity.name.lower()}_{role}.csv"
    file_path = str(PATHS_FOLDER_NAME / file_name)
    create_folders(file_path)
    path = get_project_root() / file_path
    return str(path)


def plot_paths(experiment, n_agents, center, width):
    goal_positions = [goal.positions for goal in experiment.goals if isinstance(goal, Blueprint)]
    target_points = np.concatenate(goal_positions) if len(goal_positions) > 0 else None

    cuboids = experiment.world_generator.cuboids if isinstance(experiment.world_generator, CustomWorldGenerator) else []

    fig, ax = plt.subplots(1, 2, figsize=(8, 4.5))
    for i, cooperativity in enumerate(PATH_COOPERATIVITIES):
        ax[i].set_aspect('equal', adjustable='box')

        plot_target_points(ax[i], target_points)
        plot_agents(ax[i], cooperativity, experiment, n_agents)
        plot_cuboids(ax[i], cuboids)

        ax[i].set_xlim(center[0] - width, center[0] + width)
        ax[i].set_ylim(center[1] - width, center[1] + width)
        ax[i].set_xlabel("X")
        ax[i].set_ylabel("Z", labelpad=-4)
        ax[i].set_title(COOPERATIVITY_NAMES[cooperativity])
    experiment_title = EXPERIMENT_TITLES[experiment.id]

    fig.suptitle(f"Paths when {experiment_title}", fontsize=16)

    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.figlegend(by_label.values(), by_label.keys(), ncol=len(by_label), loc='lower center', fancybox=True)
    save_figure(f"path_{experiment.id}.png")
    plt.show()


def plot_target_points(ax, target_points):
    if target_points is not None:
        ax.scatter(target_points[:, 0], target_points[:, 2], c="k", s=60, marker='x', label="Fence posts")


def plot_agents(ax, cooperativity, experiment, n_agents):
    for role in range(n_agents):
        agent_position = np.loadtxt(get_path_file_name(experiment, n_agents, cooperativity, role), delimiter=",")
        if agent_position.ndim == 1:
            agent_position = np.array([agent_position])
        color = AGENT_COLORS[role]
        ax.plot(agent_position[:, 0], agent_position[:, 2], color=color, linestyle='dashed', label=f"Agent {role}")
        ax.scatter(agent_position[0, 0], agent_position[0, 2], color=color, marker='*')


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
    get_paths(experiments.experiment_flat_world, 3)
    plot_paths(experiments.experiment_flat_world, 3, (130, 10), 40)
    # get_paths(experiments.experiment_get_10_stone_pickaxe_manual, 2)
    # plot_paths(experiments.experiment_get_10_stone_pickaxe_manual, 2, (0, 0), 30)
