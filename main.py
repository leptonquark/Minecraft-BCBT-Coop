from __future__ import print_function

from builtins import range
import MalmoPython
import malmoutils
import os
import sys
from agent import MinerAgent
from player import Player
from world import World



def run(argv=['']):
    if "MALMO_XSD_PATH" not in os.environ:
        print("Please set the MALMO_XSD_PATH environment variable.")
        return
    malmoutils.fix_print()

    agent_host = MinerAgent()
    world = World(agent_host)
    world.startWorld()

    #player = Player(world, agent_host)
    player = Player(world, agent_host)
    
    player.run_mission()





if __name__ == "__main__":
    run(sys.argv)
