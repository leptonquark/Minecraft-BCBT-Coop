import random
import time
import json
from enum import Enum
import numpy as np


class Direction(Enum):
    North = 0
    West = 1
    South = 2
    East = 3

MAX_DELAY = 60
YAW_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45


directionAngle = {
    Direction.North : 0,
    Direction.East : 90,
    Direction.South : 180,
    Direction.West : 270
}
directionVector = {
    Direction.North : np.array([0, 0, 1]),
    Direction.East : np.array([-1, 0, 0]),
    Direction.South : np.array([0, 0, -1]),
    Direction.West : np.array([1, 0, 0])
}



class Player():

    def __init__(self, world, agent_host):
        self.world = world
        self.agent_host = agent_host

        self.grid_size = world.mission_data.get_grid_size()

    def run_mission(self):
        agent_host = self.agent_host
        world_state = agent_host.getWorldState()


        # main loop:
        while world_state.is_mission_running:

            #SLEEP
            time.sleep(0.5)

            #SEE (AND DO (FOR NOW)) 
            world_state = agent_host.getWorldState()
            info = world_state.observations[-1].text
            
            if info:
                infoDict = json.loads(info)

                for key in infoDict:
                    if key != "me":
                        print(key, infoDict[key])
                if "LineOfSight" in infoDict:
                    print("los: " + str(infoDict["LineOfSight"]))
                if "entities" in infoDict:
                    print("entities: " + str(infoDict["entities"]))

                yaw = 0
                if "Yaw" in infoDict:
                    yaw = infoDict["Yaw"]
                    if yaw <= 0:
                        yaw += CIRCLE_DEGREES


                if "me" in infoDict:
                    grid = self.gridObservationFromList(infoDict["me"])
                    dx = self.grid_size[0]
                    dy = self.grid_size[1]
                    dz = self.grid_size[2]


                    pos = np.array([int(axis/2) for axis in self.grid_size])

                    surroundings = {direction : grid[tuple(pos + directionVector[direction])] for direction in Direction }
                    print(surroundings)

                    logpos = np.argwhere((grid == "log") | (grid == "log2"))
                    if len(logpos) > 0:

                        logdistances = logpos - pos
                        logdistances[:,1] *= 1000 #Focus on logs on same y position
                        logdistances = np.sum(np.abs(logdistances),axis=1)
                        min_dist_arg = np.argmin(logdistances)
                        min_dist = logdistances[min_dist_arg]
                        print(min_dist)
                        move = logpos[min_dist_arg] - pos
                        wantedDirection = Direction.North
                        if(move[1] > 0):
                            wantedDirection = Direction.North
                        elif(move[1] < 0):
                            wantedDirection = Direction.South
                        elif(move[2] > 0):
                            wantedDirection = Direction.West
                        elif(move[2] < 0):
                            wantedDirection = Direction.East


                        currentDirection = self.getCurrentDirection(yaw)                        
                        print("Current Direction", currentDirection)
                        print("Wanted Direction", wantedDirection)
                        print(move)

                        turn_direction = self.getTurnDirection(yaw, wantedDirection)
                        agent_host.sendCommand( "turn " + str(turn_direction))

                        if turn_direction == 0:
                            if min_dist > 1:
                                agent_host.sendCommand( "move 1")
                            else:
                                agent_host.sendCommand( "move 0")
                            if surroundings[currentDirection] != "air":
                                agent_host.sendCommand( "attack 1")
                            else:
                                agent_host.sendCommand( "attack 0")
                        else:
                            agent_host.sendCommand( "move 0")            
            
            self.checkTimeout(self.world, world_state)




        print("Mission has stopped.")


    def checkTimeout(self, world, world_state):
        if (world_state.number_of_video_frames_since_last_state > 0 or
        world_state.number_of_observations_since_last_state > 0 or
        world_state.number_of_rewards_since_last_state > 0):
            last_delta = time.time()
        else:
            if time.time() - last_delta > MAX_DELAY:
                print("Max delay exceeded for world state change")
                world.restart_minecraft(world_state, "world state change")

    def gridObservationFromList(self, gridobs):
        grid = np.array(gridobs).reshape(self.grid_size[1], self.grid_size[2], self.grid_size[0])
        grid = np.transpose(grid, (2, 0, 1))
        return grid

    def getWantedAngle(self, direction):
        return directionAngle[direction]

    def getTurnDirection(self, yaw, wantedDirection):
        diff = self.getWantedAngle(wantedDirection) - yaw
        if diff <= 0:
            diff += 360

        if diff <= YAW_TOLERANCE or diff >= CIRCLE_DEGREES - YAW_TOLERANCE: 
            return 0
        else:
            half_circle = CIRCLE_DEGREES/2
            if diff <= half_circle:
                return diff/half_circle
            else:
                return -diff/half_circle


    def getCurrentDirection(self, yaw):
        for key in directionAngle:
            checkAngle = directionAngle[key]
            diff = checkAngle - yaw
            if diff <= 0:
                diff += 360

            if diff <= DELTA_ANGLES or diff >= CIRCLE_DEGREES - DELTA_ANGLES: 
                return key
        return Direction.North

