import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch

from utils.plot import save_figure


def visualize_arena_two_dimensionally():
    fig, ax = plt.subplots()

    agents = [[0, 0], [-5, 0], [5, 0]]
    plt.plot(*zip(*agents), marker='*', color='k', ls='', markersize=14)
    ax.add_patch(Rectangle((-5, 20), 10, 5, color='gray'))
    ax.add_patch(Rectangle((-5, -25), 10, 5, color='brown'))

    plt.xlim([-25, 25])
    plt.ylim([-25, 25])
    plt.title("Visual representation of the test arena")

    stone = Patch(color='gray', label='Stone chunk')
    wood = Patch(color='brown', label='Wood chunk')
    agent = Line2D([0], [0], label='Start position', color='k', marker="*", ls='', markersize=14)

    plt.legend(handles=[stone, wood, agent])

    # display plot
    save_figure("arena.png")
    plt.show()


def visualize_arena_three_dimensionally():
    # prepare some coordinates
    x, y, z = np.indices((10, 10, 6))

    # draw cuboids in the top left and bottom right corners, and a link between
    # them
    wood_cube = (x <= 5) & (x > 3) & (y < 1) & (z < 1)
    stone_cube = (x <= 5) & (x > 3) & (y >= 9) & (z < 1)
    both_cubes = wood_cube | stone_cube

    colors = np.empty(both_cubes.shape, dtype=object)
    colors[wood_cube] = 'red'
    colors[stone_cube] = 'green'

    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(both_cubes, facecolors=colors, edgecolor='k')
    ax.set_box_aspect(aspect=(1, 1, 0.5))

    xy_virtual = range(1, 12, 2)
    xy_actual = [5 * x - 25 for x in xy_virtual]

    plt.xticks(xy_virtual, labels=xy_actual)
    plt.yticks(xy_virtual, labels=xy_actual)

    z_actual = range(0, 26, 10)
    z_virtual = range(0, 6, 2)

    agents = np.array([[5, 5, 0], [4, 5, 0], [6, 5, 0]])
    ax.scatter(*agents.T, marker='*', color='blue', s=100)
    for i, a in enumerate(agents):
        ax.text(a[0], a[1] - 0.5, a[2] - 1, str(i), color="black", fontsize=10)

    ax.set_zticks(z_virtual)
    ax.set_zticklabels(z_actual)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_zlim(0, 6)

    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')

    stone = Patch(label='Stone Chunk', facecolor='red', edgecolor='k', linewidth=1)
    wood = Patch(label='Wood Chunk', facecolor='green', edgecolor='k', linewidth=1)
    agent = Line2D([0], [0], label='Start Position', marker='*', linewidth=0, color='blue', markersize=10)
    plt.legend(handles=[stone, wood, agent], bbox_to_anchor=(1.15, 0), fancybox=True, ncol=3)
    plt.title("Test Arena for Stone Pickaxe Scenario")

    plt.show()
    save_figure("arena3d.png")


if __name__ == '__main__':
    visualize_arena_three_dimensionally()
