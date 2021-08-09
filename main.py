from __future__ import print_function

import os

from goals.blueprint import Blueprint, BlueprintType
from malmo import malmoutils
from runner import Runner


def run():
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()
    #goals = [conditions.HasItemEquipped(agent, items.DIAMOND_PICKAXE)]

    #goals = [conditions.HasItem(agent, items.BEEF)]

    goals = Blueprint.get_blueprint(BlueprintType.StraightFence)

    player = Runner(goals)
    player.run_mission()


if __name__ == "__main__":
    run()
