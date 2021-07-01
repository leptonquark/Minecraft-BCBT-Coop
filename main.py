from __future__ import print_function

import os
import sys

from goals.blueprint import Blueprint, BlueprintType
from malmo import malmoutils
from malmo.agent import MinerAgent
from runner import Runner
from world.world import World


def run(argv=None):
    if argv is None:
        argv = ['']
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent = MinerAgent()
    #goals = [conditions.HasItemEquipped(agent, items.STONE_PICKAXE)]

    #goals = [conditions.HasItem(agent, items.BEEF)]

    goals = Blueprint.get_blueprint(BlueprintType.Fence)

    world = World(agent, goals)

    player = Runner(world, agent, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
