AGENT_COLORS = [
    [1, 0, 1, 1],
    [0, 1, 1, 1],
    [1, 1, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 0, 1],
    [0, 0, 1, 1]
]

CUBOID_COLORS = {
    "stone": [1, 0.05, 0.05, 0.05],
    "log_2": [1, 0.75, 0.75, 0.35]
}
CUBOID_COLOR_DEFAULT = [1, 1, 1, 1]


def get_agent_color(i):
    return AGENT_COLORS[i] if i < len(AGENT_COLORS) else AGENT_COLORS[0]


def get_cuboid_color(cuboid_type):
    return CUBOID_COLORS.get(cuboid_type, CUBOID_COLOR_DEFAULT)
