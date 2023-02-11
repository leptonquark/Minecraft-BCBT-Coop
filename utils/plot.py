import matplotlib.pyplot as plt

from utils.file import get_project_root, create_folders


def save_figure(filename):
    relative_path = f"log/figures/{filename}"
    create_folders(relative_path)
    plt.savefig(get_project_root() / relative_path)
