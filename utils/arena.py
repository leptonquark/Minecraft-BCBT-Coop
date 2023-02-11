import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Patch

from utils.plot import save_figure

WIDTH = 25
RANGE = [-WIDTH, WIDTH]

CHUNK_WIDTH = 10
CHUNK_DEPTH = 5
CHUNK_HEIGHT = 5
CHUNK_X = -5
STONE_CHUNK_Z = 20
WOOD_CHUNK_Z = -25

AGENTS_START_POSITIONS = np.array([[0, 0, 0], [-5, 0, 0], [5, 0, 0]])

AGENT_LABEL = "Start Position"
WOOD_LABEL = "Wood Chunk"
STONE_LABEL = "Stone Chunk"

AGENT_2D = {"label": AGENT_LABEL, "color": "black"}
WOOD_2D = {"label": WOOD_LABEL, "color": "brown"}
STONE_2D = {"label": STONE_LABEL, "color": "gray"}

AGENT_3D = {"label": AGENT_LABEL, "color": "blue"}
WOOD_3D = {"label": WOOD_LABEL, "color": "green"}
STONE_3D = {"label": STONE_LABEL, "color": "red"}
TEXT_OFFSET = np.array([0, -0.5, -1])

VIRTUAL_WIDTH = 10
VIRTUAL_HEIGHT = 6
DELTA_TICK_XY = 2
DELTA_TICK_Z = 2
BOX_ASPECT_3D = (1, 1, 0.5)


def visualize_arena_two_dimensionally():
    fig, ax = plt.subplots()

    plt.plot(*zip(*AGENTS_START_POSITIONS[:, :2]), marker='*', color=AGENT_2D["color"], ls='', markersize=14)
    ax.add_patch(Rectangle((CHUNK_X, STONE_CHUNK_Z), CHUNK_WIDTH, CHUNK_DEPTH, color=STONE_2D["color"]))
    ax.add_patch(Rectangle((CHUNK_X, WOOD_CHUNK_Z), CHUNK_WIDTH, CHUNK_DEPTH, color=WOOD_2D["color"]))

    plt.xlim(RANGE)
    plt.ylim(RANGE)
    plt.title("Visual representation of the test arena")

    stone = Patch(color=STONE_2D["color"], label=STONE_2D["label"])
    wood = Patch(color=WOOD_2D["color"], label=WOOD_2D["label"])
    agent = Line2D([0], [0], label=AGENT_2D["label"], color=AGENT_2D["color"], marker="*", ls='', markersize=14)

    plt.legend(handles=[stone, wood, agent])

    # display plot
    save_figure("arena.png")
    plt.show()


def visualize_arena_three_dimensionally():
    # prepare some coordinates
    x, y, z = np.indices((VIRTUAL_WIDTH, VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    scale = 2 * WIDTH / VIRTUAL_WIDTH

    # draw cuboids in the top left and bottom right corners, and a link between them
    wood_cube = (x <= VIRTUAL_WIDTH / 2) & (x >= (VIRTUAL_WIDTH / 2) - 1) & (y < 1) & (z < 1)
    stone_cube = (x <= VIRTUAL_WIDTH / 2) & (x >= (VIRTUAL_WIDTH / 2) - 1) & (y >= (VIRTUAL_WIDTH - 1)) & (z < 1)
    both_cubes = wood_cube | stone_cube

    colors = np.empty(both_cubes.shape, dtype=object)
    colors[wood_cube] = WOOD_3D["color"]
    colors[stone_cube] = STONE_3D["color"]

    ax = plt.figure().add_subplot(projection='3d')
    ax.voxels(both_cubes, facecolors=colors, edgecolor='k')
    ax.set_box_aspect(aspect=BOX_ASPECT_3D)

    xy_virtual = range(1, VIRTUAL_WIDTH + DELTA_TICK_XY, DELTA_TICK_XY)
    xy_actual = [scale * x - WIDTH for x in xy_virtual]
    plt.xticks(xy_virtual, labels=xy_actual)
    plt.yticks(xy_virtual, labels=xy_actual)

    z_virtual = range(0, VIRTUAL_HEIGHT, DELTA_TICK_Z)
    z_actual = [scale * x for x in z_virtual]

    agents = np.array([VIRTUAL_WIDTH / 2, VIRTUAL_WIDTH / 2, 0]) + AGENTS_START_POSITIONS / scale
    ax.scatter(*agents.T, marker='*', color=AGENT_3D["color"], s=100)
    for i, a in enumerate(agents):
        text_position = a + TEXT_OFFSET
        ax.text(text_position[0], text_position[1], text_position[2], str(i), color="black", fontsize=10)

    ax.set_zticks(z_virtual)
    ax.set_zticklabels(z_actual)

    ax.set_xlim(0, VIRTUAL_WIDTH)
    ax.set_ylim(0, VIRTUAL_WIDTH)
    ax.set_zlim(0, VIRTUAL_HEIGHT)

    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_zlabel('Y')

    wood = Patch(label=WOOD_3D["label"], facecolor=WOOD_3D["color"], edgecolor='k', linewidth=1)
    stone = Patch(label=STONE_3D["label"], facecolor=STONE_3D["color"], edgecolor='k', linewidth=1)
    agent = Line2D([0], [0], label=AGENT_3D["label"], marker='*', linewidth=0, color=AGENT_3D["color"], markersize=10)
    handles = [wood, stone, agent]
    plt.legend(handles=handles, bbox_to_anchor=(1.15, 0), fancybox=True, ncol=len(handles))
    plt.title("Test Arena for Stone Pickaxe Scenario")

    plt.show()
    save_figure("arena3d.png")


if __name__ == '__main__':
    visualize_arena_three_dimensionally()
