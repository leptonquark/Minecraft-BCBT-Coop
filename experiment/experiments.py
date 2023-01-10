from dataclasses import dataclass
from typing import List, Union

import numpy as np

import bt.conditions as conditions
import items.items as items
from bt.actions import Action
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint, BlueprintType
from mobs import enemies
from mobs.enemies import Enemy
from mobs.entity import Entity
from world.world_generator import DefaultWorldGenerator, WorldGenerator, FlatWorldGenerator, CustomWorldGenerator, \
    Cuboid


@dataclass
class Experiment:
    id: str
    name: str
    world_generator: WorldGenerator
    goals: List[Union[Blueprint, Action, conditions.Condition, AgentlessCondition]]
    start_positions: List[List[float]]
    start_entities: List[Entity]
    start_inventory: List[str]


experiment_pickaxe = Experiment(
    id="dp",
    name="Diamond Pickaxe",
    world_generator=DefaultWorldGenerator(),
    goals=[AgentlessCondition(conditions.HasItemEquipped, [items.DIAMOND_PICKAXE])],
    start_positions=[[131, 72, 17], [117, 72, 13], [120, 72, 24]],
    start_entities=[],
    start_inventory=[]
)

experiment_default_world = Experiment(
    id="dwg",
    name="Fence Grid Default World",
    world_generator=DefaultWorldGenerator(),
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 11], 7)],
    start_positions=[[131, 72, 17], [132, 72, 4], [140, 72, 24], [125, 72, 50], [140, 72, 34]],
    start_entities=[],
    start_inventory=[]
)

experiment_flat_world = Experiment(
    id="fwg",
    name="Fence Grid Flat World",
    world_generator=FlatWorldGenerator(),
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[],
    start_inventory=[]
)

experiment_flat_world_zombie = Experiment(
    id="fwz",
    name="Fence Grid Flat World Zombie",
    world_generator=FlatWorldGenerator(),
    goals=[
        AgentlessCondition(conditions.HasNoEnemyNearby, []),
        Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)
    ],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[Enemy(enemies.ZOMBIE, 116, 10, 9)],
    start_inventory=[items.IRON_SWORD]
)

experiment_get_30_fence = Experiment(
    id="g30f",
    name="Get 30 Fence Flat World",
    world_generator=FlatWorldGenerator(),
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.FENCE, 30])
    ],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[],
    start_inventory=[]
)

experiment_get_10_stone_pickaxe = Experiment(
    id="g10sp",
    name="Get 10 Pick Axe Default World",
    world_generator=DefaultWorldGenerator(),
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.STICKS, 10]),
        AgentlessCondition(conditions.HasItemShared, [items.STONE, 15]),
    ],
    start_positions=[[131, 72, 17], [132, 72, 4], [140, 72, 24], [125, 72, 50], [140, 72, 34]],
    start_entities=[],
    start_inventory=[]
)

experiment_get_10_stone_pickaxe_manual = Experiment(
    id="g10spmdw",
    name="Get 10 Pick Axe Test Arena",
    world_generator=CustomWorldGenerator(
        [
            Cuboid(items.STONE, np.array([[-5, 9, 20], [5, 11, 25]])),
            Cuboid(items.LOG_2, np.array([[-5, 9, -20], [5, 11, -25]])),
        ]
    ),
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.STICKS, 10]),
        AgentlessCondition(conditions.HasItemShared, [items.STONE, 15]),
    ],
    start_positions=[[0, 9, 0], [-5, 9, 0], [5, 9, 0], [10, 9, 0], [-10, 9, 0]],
    start_entities=[],
    start_inventory=[items.WOODEN_PICKAXE]
)

configurations = [
    experiment_pickaxe,
    experiment_default_world,
    experiment_flat_world,
    experiment_flat_world_zombie,
    experiment_get_30_fence,
    experiment_get_10_stone_pickaxe,
    experiment_get_10_stone_pickaxe_manual
]
