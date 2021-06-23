from __future__ import print_function

import os
import sys

from goals.blueprint import Blueprint, BlueprintType
from bt import conditions
from items import items
from malmo import malmoutils
from malmo.agent import MinerAgent
from world.world import World
from runner import Runner


def run(argv=None):
    if argv is None:
        argv = ['']
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent = MinerAgent()
    goals = [conditions.IsBlockObservable(agent, items.STONE_PICKAXE)]

    #goals = [conditions.HasItemEquipped(agent, items.WOODEN_PICKAXE)]

    #goals = Blueprint.get_blueprint(BlueprintType.Fence)

    world = World(agent, goals)

    player = Runner(world, agent, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
