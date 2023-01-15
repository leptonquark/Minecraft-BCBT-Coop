import argparse

import malmo.minecraftbootstrap

# TODO: Remove Hardcoded line and move to a config file
from utils.network import get_ports

INSTALL_DIR = "C:\\Malmo-0.37.0-Windows-64bit_withBoost_Python3.7"


def run_minecraft(n_clients=None):
    malmo.minecraftbootstrap.malmo_install_dir = INSTALL_DIR
    ports = get_ports(n_clients) if n_clients is not None else None
    if ports:
        malmo.minecraftbootstrap.launch_minecraft(ports)
    else:
        malmo.minecraftbootstrap.launch_minecraft()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='A bootstrap for starting Minecraft.')
    parser.add_argument("-c", "--clients", help="How many clients do you want to start?", default=2, type=int)
    args = parser.parse_args()
    run_minecraft(args.clients)
