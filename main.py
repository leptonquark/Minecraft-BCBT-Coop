from __future__ import print_function

import os
import sys

from goals.blueprint import Blueprint, BlueprintType
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
    """
    goals = [
        conditions.HasItem(agent, items.BEEF),
        conditions.HasItemEquipped(agent, items.DIAMOND_PICKAXE)
    ]"""

    goals = Blueprint.get_blueprint(BlueprintType.Fence)

    """
    goals = [
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([209, 65, 238])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([209, 65, 239])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([209, 65, 240])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([209, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([210, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([211, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([212, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([212, 65, 240])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([212, 65, 239])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([212, 65, 238])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([211, 65, 238])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([210, 65, 238])),
    ]"""
    """
    goals = [
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([209, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([210, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([211, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([212, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([213, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([214, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([215, 65, 241])),
        conditions.IsBlockAtPosition(agent, items.WOODEN_FENCE, np.array([216, 65, 241])),

    ]
    """

    world = World(agent, goals)
    world.start_world()

    player = Runner(world, agent, goals)

    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
