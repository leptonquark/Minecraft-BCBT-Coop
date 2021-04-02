from __future__ import print_function

from malmo import malmoutils
import os
import sys
from malmo.agent import MinerAgent
from runner import Runner
from malmo.world import World


def run(argv=None):
    if argv is None:
        argv = ['']
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent = MinerAgent()
    world = World(agent)
    world.start_world()

    goals = ["stone_pickaxe"]

    player = Runner(world, agent, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
