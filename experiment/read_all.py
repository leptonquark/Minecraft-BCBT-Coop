from experiment.read import plot_completion_times
from experiment.read_delta import plot_delta
from experiment.read_monsters import plot_completion_chances
from experiment.read_pickaxes import plot_pickaxe_completion_times


def plot_all():
    plot_completion_chances()
    plot_pickaxe_completion_times()
    plot_delta(3)
    plot_completion_times(True, False)
    plot_completion_times(True, True)
    plot_completion_times(False, False)
    plot_completion_times(False, True)


if __name__ == '__main__':
    plot_all()
