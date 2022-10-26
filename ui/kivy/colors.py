COLORS = [
    [1, 0, 1, 1],
    [0, 1, 1, 1],
    [1, 1, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 0, 1],
    [0, 0, 1, 1]
]


def get_color(i):
    if i < len(COLORS):
        return COLORS[i]
    else:
        return COLORS[0]
