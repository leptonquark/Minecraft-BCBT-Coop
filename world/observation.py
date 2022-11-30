import json
from enum import Enum

import numpy as np

from items import items
from items.inventory import Inventory
from items.pickup import PickUp
from mobs import animals
from mobs.animals import Animal
from utils.vectors import CIRCLE_DEGREES


def grid_observation_from_list(grid_observation_list, grid_size):
    grid = np.array(grid_observation_list).reshape((grid_size[1], grid_size[2], grid_size[0]))
    grid = np.transpose(grid, (2, 0, 1))
    return grid


def get_absolute_position(info):
    if Observation.X in info and Observation.Y in info and Observation.Z in info:
        return np.array([info[Observation.X], info[Observation.Y], info[Observation.Z]])
    return None


def get_yaw(info):
    if Observation.YAW in info:
        yaw = info[Observation.YAW]
        if yaw <= 0:
            yaw += CIRCLE_DEGREES
        return yaw
    return None


def get_pitch(info):
    return info.get(Observation.PITCH)


def get_line_of_sight_position(info):
    los = info.get(Observation.LOS)
    if los is None:
        return None
    if Observation.LOS_X in los and Observation.LOS_Y in los and Observation.LOS_Z in los:
        return np.array([los[Observation.LOS_X], los[Observation.LOS_Y], los[Observation.LOS_Z]])
    else:
        return None


def get_line_of_sight_type(info):
    los = info.get(Observation.LOS)
    if los is None:
        return None
    return los.get(Observation.LOS_TYPE)


def get_line_of_sight_hit_type(info):
    los = info.get(Observation.LOS)
    if los is None:
        return None
    hit_type = los.get(Observation.LOS_HIT_TYPE)
    if hit_type == Observation.LOS_HIT_TYPE_BLOCK:
        return LineOfSightHitType.BLOCK
    else:
        return LineOfSightHitType.ITEM


class LineOfSightHitType(Enum):
    BLOCK = 0
    ITEM = 1


def get_grid_by_spec(info, spec):
    if Observation.GRID_LOCAL in info:
        grid_observation_list = info.get(spec.name, None)
        if grid_observation_list:
            return grid_observation_from_list(grid_observation_list, spec.get_grid_size())
    return None


def get_life(info):
    return info.get(Observation.LIFE, None)


class Observation:
    GRID_LOCAL = "me"

    X = "XPos"
    Y = "YPos"
    Z = "ZPos"

    LIFE = "Life"

    LOS = "LineOfSight"
    LOS_TYPE = "type"
    LOS_HIT_TYPE = "hitType"
    LOS_HIT_TYPE_ITEM = "item"
    LOS_HIT_TYPE_BLOCK = "block"
    LOS_X = "x"
    LOS_Y = "y"
    LOS_Z = "z"

    YAW = "Yaw"
    PITCH = "Pitch"

    ENTITIES = "entities"
    ENTITY_NAME = "name"
    ENTITY_X = "x"
    ENTITY_Y = "y"
    ENTITY_Z = "z"
    ENTITY_LIFE = "life"

    def __init__(self, observations, mission_data):
        self.mission_data = mission_data

        self.grid_size_local = mission_data.grid_local.get_grid_size()

        self.pos_local_grid = None
        self.info = None

        self.abs_pos = None
        self.pitch = None
        self.yaw = None

        self.grid_local = None
        self.grids_global = {}
        self.inventory = None
        self.los_pos = None
        self.los_type = None
        self.los_hit_type = None

        self.life = None

        self.animals = None
        self.pickups = None

        if observations is None or not observations:
            print("Observations is null or empty")
            return

        info_json = observations[-1].text
        if info_json is None:
            print("Info is null")
            return

        self.info = json.loads(info_json)
        self.inventory = Inventory(self.info)

        self.life = get_life(self.info)

        self.pos_local_grid = np.array([int(axis / 2) for axis in self.grid_size_local])

        self.abs_pos = get_absolute_position(self.info)
        self.yaw = get_yaw(self.info)
        self.pitch = get_pitch(self.info)

        self.los_pos = get_line_of_sight_position(self.info)
        self.los_type = get_line_of_sight_type(self.info)
        self.los_hit_type = get_line_of_sight_hit_type(self.info)

        self.grid_local = get_grid_by_spec(self.info, self.mission_data.grid_local)

        self.setup_entities(self.info)

    def setup_entities(self, info):
        if Observation.ENTITIES in info:
            self.pickups = []
            self.animals = []
            for entity in info[Observation.ENTITIES]:
                entity_name = entity.get(Observation.ENTITY_NAME, None)
                entity_x = entity.get(Observation.ENTITY_X, None)
                entity_y = entity.get(Observation.ENTITY_Y, None)
                entity_z = entity.get(Observation.ENTITY_Z, None)
                if entity_name and entity_x is not None and entity_y is not None and entity_z is not None:
                    if entity_name in items.pickups:
                        self.pickups.append(PickUp(entity_name, entity_x, entity_y, entity_z))
                    elif entity_name in animals.species:
                        animal_life = entity.get(Observation.ENTITY_LIFE, None)
                        self.animals.append(Animal(entity_name, entity_x, entity_y, entity_z, animal_life))

    def get_grid_global(self, grid_spec):
        if grid_spec.name in self.grids_global:
            return self.grids_global[grid_spec.name]

        grid = get_grid_by_spec(self.info, grid_spec)
        self.grids_global[grid_spec.name] = grid
        return grid

    def print(self):
        for key in self.info:
            if key != Observation.GRID_LOCAL:
                print(key, self.info[key])
