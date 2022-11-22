import malmo.minecraftbootstrap

# TODO: Remove Hardcoded line and move to a config file
from utils.network import get_ports

INSTALL_DIR = "C:\\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7"


def run_minecraft(n_clients=None):
    malmo.minecraftbootstrap.malmo_install_dir = INSTALL_DIR
    if n_clients is None:
        malmo.minecraftbootstrap.launch_minecraft()
    else:
        ports = get_ports(n_clients)
        malmo.minecraftbootstrap.launch_minecraft(ports)


if __name__ == "__main__":
    run_minecraft(3)
