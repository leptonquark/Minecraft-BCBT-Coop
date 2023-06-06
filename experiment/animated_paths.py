import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from experiment import experiments
from experiment.paths import EXPERIMENT_TITLES, get_path_file_name, AGENT_COLORS, plot_target_points
from goals.blueprint.blueprint import Blueprint
from multiagents.cooperativity import Cooperativity
from world.worldgenerator import CustomWorldGenerator


class PathAnimator:

    def __init__(self, experiment, n_agents, center, width, cooperativity):
        self.center = center
        self.width = width
        self.experiment_id = experiment.id

        goal_positions = [goal.positions for goal in experiment.goals if isinstance(goal, Blueprint)]
        self.target_points = np.concatenate(goal_positions) if len(goal_positions) > 0 else None

        world_generator = experiment.world_generator
        cuboids = world_generator.cuboids if isinstance(world_generator, CustomWorldGenerator) else []

        # plot_agents(ax, cooperativity, experiment, n_agents)
        #        plot_cuboids(ax, cuboids)

        self.agent_positions = [
            np.loadtxt(get_path_file_name(experiment, n_agents, cooperativity, role), delimiter=",")
            for role
            in range(n_agents)
        ]

        print(self.agent_positions[0])
        self.x = np.arange(0, 2 * np.pi, 0.01)
        self.y = np.sin(self.x)

        # Setup the figure and axes...
        self.fig, self.ax = plt.subplots()

        # Then setup FuncAnimation.
        self.total_frames = len(self.agent_positions[0])
        self.resolution = 5
        self.frames = np.arange(0, self.total_frames, self.resolution)

        ani = animation.FuncAnimation(self.fig, self.update, interval=5, blit=True, save_count=50,
                                      init_func=self.initialize_agent_plot, frames=self.frames)

        writergif = animation.PillowWriter(fps=30)
        ani.save("filename.gif", writer=writergif)

    def initialize_agent_plot(self):
        role = 0
        self.agents, = self.ax.plot([], [], color=AGENT_COLORS[role], linestyle='dashed', label=f"Agent {role}")
        self.ax.set_xlim(self.center[0] - self.width, self.center[0] + self.width)
        self.ax.set_ylim(self.center[1] - self.width, self.center[1] + self.width)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Z", labelpad=-4)
        self.ax.set_title(f"Paths when {EXPERIMENT_TITLES[self.experiment_id]}", fontsize=16)

        self.ax.scatter(self.agent_positions[0][0, 0], self.agent_positions[0][0, 2], color=AGENT_COLORS[role],
                        marker='*')
        plot_target_points(self.ax, self.target_points)

        return self.agents,

    def update(self, i):
        """Update the scatter plot."""
        print(f"Updating frame {i}/{self.total_frames}")
        self.agents.set_xdata(self.agent_positions[0][:i, 0])
        self.agents.set_ydata(self.agent_positions[0][:i, 2])
        return self.agents,


if __name__ == '__main__':
    a = PathAnimator(experiments.experiment_flat_world, 3, (130, 10), 40, Cooperativity.INDEPENDENT)
    plt.show()
