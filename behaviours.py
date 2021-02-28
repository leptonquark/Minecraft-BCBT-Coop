from py_trees.behaviour import Behaviour
from py_trees.common import Status
import random
import time
import json
from enum import Enum
import numpy as np
from observation import Observation, not_stuck
from inventory import HOTBAR_SIZE
from utils import Direction, directionAngle, directionVector



MAX_DELAY = 60
YAW_TOLERANCE = 5
PITCH_TOLERANCE = 5
CIRCLE_DEGREES = 360
DELTA_ANGLES = 45
LOS_TOLERANCE = 0.5
MOVE_TRESHOLD = 5

PICKAXE_HOTBAR_POSITION = 5


class Craft(Behaviour):
    def __init__(self, agent_host):
        super(Craft, self).__init__("Craft")
        self.agent_host = agent_host

    def update(self):
        if self.agent_host.observation.inventory.hasItem("log"):
            self.agent_host.sendCommand("craft planks")
        if not self.agent_host.observation.inventory.hasItem("crafting_table", 1):
            if self.agent_host.observation.inventory.hasItem("planks", 4):
                self.agent_host.sendCommand("craft crafting_table")
        else:
            if not self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("planks", 2):
                self.agent_host.sendCommand("craft stick")
            if not self.agent_host.observation.inventory.hasItem("wooden_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("planks", 3):
                self.agent_host.sendCommand("craft wooden_pickaxe")
            if not self.agent_host.observation.inventory.hasItem("stone_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("cobblestone", 3):
                self.agent_host.sendCommand("craft stone_pickaxe")


        if self.agent_host.observation.inventory.hasItem("log"):
            self.agent_host.sendCommand("craft planks")
        if not self.agent_host.observation.inventory.hasItem("crafting_table", 1):
            if self.agent_host.observation.inventory.hasItem("planks", 4):
                self.agent_host.sendCommand("craft crafting_table")
        else:
            if not self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("planks", 2):
                self.agent_host.sendCommand("craft stick")
            if not self.agent_host.observation.inventory.hasItem("wooden_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("planks", 3):
                self.agent_host.sendCommand("craft wooden_pickaxe")
            if not self.agent_host.observation.inventory.hasItem("stone_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2) and self.agent_host.observation.inventory.hasItem("cobblestone", 3):
                self.agent_host.sendCommand("craft stone_pickaxe")
        
        return Status.SUCCESS


class Equip(Behaviour):
    def __init__(self, agent_host):
        super(Equip, self).__init__("Equip")
        self.agent_host = agent_host

    def update(self):
        if self.agent_host.observation.inventory.hasItem("stone_pickaxe"):
            self.find_and_equip_item(self.agent_host.observation, "stone_pickaxe")
        elif self.agent_host.observation.inventory.hasItem("wooden_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2):
            self.find_and_equip_item(self.agent_host.observation, "wooden_pickaxe")

        return Status.SUCCESS


    def find_and_equip_item(self, observation, item):
        position = observation.inventory.findItem(item)
        if position > HOTBAR_SIZE:
            self.agent_host.sendCommand("swapInventoryItems " + str(position) + " " + str(PICKAXE_HOTBAR_POSITION))
            position = PICKAXE_HOTBAR_POSITION

            
        self.agent_host.sendCommand("hotbar." + str(position+1) + " 1")  # press
        self.agent_host.sendCommand("hotbar." + str(position+1) + " 0")  # release
        time.sleep(0.1)



class JumpIfStuck(Behaviour):
    def __init__(self, agent_host):
        super(JumpIfStuck, self).__init__("Craft")
        self.agent_host = self.agent_host

    def update(self):
        if self.agent_host.observation.isStuck():
            self.agent_host.sendCommand("jump 1")
        else:
            self.agent_host.sendCommand("jump 0")
        return Status.SUCCESS


class GatherMaterial(Behaviour):
    def __init__(self, agent_host):
        super(GatherMaterial, self).__init__("GatherMaterial")
        self.agent_host = agent_host

    def update(self):
        # Use fallback for this
        if self.agent_host.observation.inventory.hasItem("stone_pickaxe"):
            move = self.agent_host.observation.getClosest(["iron_ore"])
        elif self.agent_host.observation.inventory.hasItem("wooden_pickaxe") and self.agent_host.observation.inventory.hasItem("stick", 2):
            move = self.agent_host.observation.getClosest(["stone"])
        else:
            move = self.agent_host.observation.getClosest(["log", "log2"])

        if move is None:
            return Status.FAILURE


        currentDirection = self.agent_host.observation.getCurrentDirection()                        
        print("Current Direction", currentDirection)

        wantedDirection = self.getWantedDirection(move)
        print("Wanted Direction", wantedDirection)




        if wantedDirection is not None:
            turn_direction = self.getTurnDirection(self.agent_host.observation.yaw, wantedDirection)
        self.agent_host.sendCommand( "turn " + str(turn_direction))

        if turn_direction == 0:
            mat_horizontal_distance = self.getHorizontalDistance(move)
            if mat_horizontal_distance > 1:
                if(not self.agent_host.observation.upper_surroundings[currentDirection] in not_stuck):
                    wantedPitch = self.getWantedPitch(1, 0)
                    self.agent_host.sendCommand( "move 0")
                    pitch_req = self.getPitchChange(self.agent_host.observation.pitch, wantedPitch)
                    self.agent_host.sendCommand("pitch " + str(pitch_req))
                    if(pitch_req == 0):
                        self.agent_host.sendCommand( "attack 1")
                    else:
                        self.agent_host.sendCommand( "attack 0")
                elif(not self.agent_host.observation.lower_surroundings[currentDirection] in not_stuck):
                    wantedPitch = self.getWantedPitch(1, -1)
                    self.agent_host.sendCommand( "move 0")
                    pitch_req = self.getPitchChange(self.agent_host.observation.pitch, wantedPitch)
                    self.agent_host.sendCommand("pitch " + str(pitch_req))
                    if(pitch_req == 0):
                        self.agent_host.sendCommand( "attack 1")
                    else:
                        self.agent_host.sendCommand( "attack 0")                          
                else:                            
                    move_speed = self.getMoveSpeed(mat_horizontal_distance)
                    pitch_req = self.getPitchChange(self.agent_host.observation.pitch, 0)
                    self.agent_host.sendCommand("pitch " + str(pitch_req))
                    self.agent_host.sendCommand( "move " + str(move_speed))
                    self.agent_host.sendCommand( "attack 0")
            else:
                self.agent_host.sendCommand( "move 0")
                wantedPitch = self.getWantedPitch(mat_horizontal_distance, -1+move[1])
                pitch_req = self.getPitchChange(self.agent_host.observation.pitch, wantedPitch)
                self.agent_host.sendCommand("pitch " + str(pitch_req))
                if(pitch_req == 0):
                    self.agent_host.sendCommand( "attack 1")
                else:
                    self.agent_host.sendCommand( "attack 0")
        else:
            self.agent_host.sendCommand( "attack 0")
            self.agent_host.sendCommand( "move 0")  

        return Status.SUCCESS          


    def getWantedDirection(self, move):
        wantedDirection = Direction.North
        if(np.abs(move[2]) >= np.abs(move[0])):
            if(move[2] > 0):
                wantedDirection = Direction.North
            else:
                wantedDirection = Direction.South
        else:
            if(move[0] > 0):
                wantedDirection = Direction.West
            else:
                wantedDirection = Direction.East
        return wantedDirection





    def getWantedAngle(self, direction):
        return directionAngle[direction]

    def getTurnDirection(self, yaw, wantedDirection):
        diff = self.getWantedAngle(wantedDirection) - yaw
        if diff <= 0:
            diff += 360

        if diff <= YAW_TOLERANCE or diff >= CIRCLE_DEGREES - YAW_TOLERANCE: 
            return 0
        else:
            print("diff", diff)
            half_circle = CIRCLE_DEGREES/2
            if diff <= half_circle:
                return diff/half_circle
            else:
                return (diff-CIRCLE_DEGREES)/half_circle

    def getWantedPitch(self, distDirection, distY):
        half_circle = CIRCLE_DEGREES/2

        return -np.arctan(distY/distDirection) * half_circle/np.pi
        

    def getPitchChange(self, pitch, wantedPitch):
        quarter_circle = CIRCLE_DEGREES/4
        diff = pitch - wantedPitch
        print(diff)
        if np.abs(diff) <= PITCH_TOLERANCE:
            return 0
        else:
            return -diff/quarter_circle

    def getHorizontalDistance(self, distance):
        return np.abs(distance[0]) + np.abs(distance[2])

    def getMoveSpeed(self, horizontal_distance):
        if(horizontal_distance >= MOVE_TRESHOLD):
            return 1
        elif(horizontal_distance <= 1):
            return 0
        else:
            return (horizontal_distance-1)/(MOVE_TRESHOLD-1)
            