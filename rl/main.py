import os

from malmo import malmoutils

from goals.blueprint import Blueprint, BlueprintType
from runner import Runner


def run():
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    goals = Blueprint.get_blueprint(BlueprintType.StraightFence)

    player = Runner(goals)
    player.run_mission()


if __name__ == "__main__":
    run()
