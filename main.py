from __future__ import print_function

import os
import sys

from bt import actions, conditions
from items import items
from malmo import malmoutils
from malmo.agent import MinerAgent
from malmo.world import World
from mobs import animals
from runner import Runner


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

    #goals = [conditions.HasItem(agent, items.BEEF), conditions.HasItemEquipped(agent, items.DIAMOND_PICKAXE)]
    #goals = [conditions.HasItem(agent, items.BEEF)]
    #goals = [conditions.HasItemEquipped(agent, items.DIAMOND_PICKAXE)]
    goals = [conditions.HasItem(agent, items.LOG, 10)]
    player = Runner(world, agent, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
