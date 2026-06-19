import argparse
import os
from pathlib import Path

import malmo.minecraftbootstrap

# TODO: Remove Hardcoded line and move to a config file
from utils.network import get_ports



def set_mamo_xsd_path():
    xsd_path = os.environ.get("MALMO_XSD_PATH")
    if xsd_path and Path(xsd_path, "Mission.xsd").exists():
        return

    repo_schema_path = Path(__file__).resolve().parent.parent / "bootstrap" / "MalmoPlatform" / "Schemas"
    if Path(repo_schema_path, "Mission.xsd").exists():
        os.environ["MALMO_XSD_PATH"] = str(repo_schema_path)
        print(f"MALMO_XSD_PATH={repo_schema_path}")


def run_minecraft(n_clients=None):
    set_mamo_xsd_path()
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
