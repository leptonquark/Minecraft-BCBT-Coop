from __future__ import print_function

from builtins import range
import os
import sys
from world import World
from player import Player

import MalmoPython
import malmoutils


def run(argv=['']):
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent_host = MalmoPython.AgentHost()
    
    world = World(agent_host)
    world.startWorld()

    player = Player(world, agent_host)
    player.run_mission()


if __name__ == "__main__":
    run(sys.argv)
