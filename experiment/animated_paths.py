import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from experiment import experiments
from experiment.paths import EXPERIMENT_TITLES, get_path_file_name, AGENT_COLORS, plot_target_points, \
    COOPERATIVITY_NAMES, PATH_COOPERATIVITIES, plot_cuboids
from goals.blueprint.blueprint import Blueprint
from world.worldgenerator import CustomWorldGenerator


class PathAnimator:

    def __init__(self, experiment, n_agents, center, width):
        self.center = center
        self.width = width
        self.experiment_id = experiment.id
        self.n_agents = n_agents

        goal_positions = [goal.positions for goal in experiment.goals if isinstance(goal, Blueprint)]
        self.target_points = np.concatenate(goal_positions) if len(goal_positions) > 0 else None

        world_generator = experiment.world_generator
        self.cuboids = world_generator.cuboids if isinstance(world_generator, CustomWorldGenerator) else []

        self.agent_positions = []
        for cooperativity in PATH_COOPERATIVITIES:
            cooperativity_agent_positions = []
            for role in range(n_agents):
                cooperativity_agent_positions.append(
                    np.loadtxt(get_path_file_name(experiment, n_agents, cooperativity, role), delimiter=",")
                )
            self.agent_positions.append(cooperativity_agent_positions)

        self.x = np.arange(0, 2 * np.pi, 0.01)
        self.y = np.sin(self.x)

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots(1, 2, figsize=(8, 4.5))
        plt.subplots_adjust(bottom=0.2)

        # Then setup FuncAnimation.
        self.total_frames = max(
            max(len(self.agent_positions[cooperativity][role]) for role in range(self.n_agents)) for cooperativity in
            range(len(PATH_COOPERATIVITIES)))
        self.resolution = 2  # 5
        self.frames = np.arange(0, self.total_frames, self.resolution)

        ani = animation.FuncAnimation(self.fig, self.update, interval=5, blit=True, save_count=50,
                                      init_func=self.initialize_agent_plot, frames=self.frames)

        writergif = animation.PillowWriter(fps=30)
        ani.save("path.gif", writer=writergif)

    def initialize_agent_plot(self):
        self.agents = []
        for i in range(len(PATH_COOPERATIVITIES)):
            for role in range(self.n_agents):
                color = AGENT_COLORS[role]
                self.agents.append(self.ax[i].plot([], [], color=color, linestyle='dashed', label=f"Agent {role}")[0])

        self.fig.suptitle(f"Paths when {EXPERIMENT_TITLES[self.experiment_id]}", fontsize=16)
        for i, cooperativity in enumerate(PATH_COOPERATIVITIES):
            self.ax[i].set_xlim(self.center[0] - self.width, self.center[0] + self.width)
            self.ax[i].set_ylim(self.center[1] - self.width, self.center[1] + self.width)
            self.ax[i].set_xlabel("X")
            self.ax[i].set_ylabel("Z", labelpad=-4)
            self.ax[i].set_title(COOPERATIVITY_NAMES[cooperativity])
            self.ax[i].set_aspect('equal', adjustable='box')

            for role in range(self.n_agents):
                self.ax[i].scatter(
                    self.agent_positions[i][role][0, 0],
                    self.agent_positions[i][role][0, 2],
                    color=AGENT_COLORS[role],
                    marker='*'
                )
            plot_target_points(self.ax[i], self.target_points)
            plot_cuboids(self.ax[i], self.cuboids)

        handles, labels = self.ax[0].get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.fig.legend(by_label.values(), by_label.keys(), ncol=len(by_label), loc='lower center', fontsize=12,
                        fancybox=True)

        return self.agents

    def update(self, i):
        print(f"Updating frame {i}/{self.total_frames}")
        for cooperativity in range(len(PATH_COOPERATIVITIES)):
            for role in range(self.n_agents):
                index = cooperativity * self.n_agents + role
                self.agents[index].set_xdata(self.agent_positions[cooperativity][role][:i, 0])
                self.agents[index].set_ydata(self.agent_positions[cooperativity][role][:i, 2])
        return self.agents


if __name__ == '__main__':
    # a = PathAnimator(experiments.experiment_flat_world, 3, (130, 10), 40)
    a = PathAnimator(experiments.experiment_get_10_stone_pickaxe_manual, 2, (0, 0), 30)
    plt.show()
