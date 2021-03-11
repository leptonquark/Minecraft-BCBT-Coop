from __future__ import print_function

import malmoutils
import os
import sys
from agent import MinerAgent
from runner import Runner
from world import World


def run(argv=None):
    if argv is None:
        argv = ['']
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent_host = MinerAgent()
    world = World(agent_host)
    world.start_world()

    goals = ["stone_pickaxe"]

    player = Runner(world, agent_host, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
