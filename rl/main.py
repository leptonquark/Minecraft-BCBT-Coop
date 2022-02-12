import os

from malmo import malmoutils
from stable_baselines3 import A2C

from goals.blueprint import Blueprint, BlueprintType
from malmoutils.agent import MinerAgent
from rl.MineEnvironment import MineEnvironment

TOTAL_TIME_STEPS = 1000000


def run():
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()
    goals = Blueprint.get_blueprint(BlueprintType.StraightFence)

    env = MineEnvironment(MinerAgent())
    model = A2C('MlpPolicy', env, verbose=1)


    model.learn(total_timesteps=TOTAL_TIME_STEPS)


if __name__ == "__main__":
    run()
