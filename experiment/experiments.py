from dataclasses import dataclass
from typing import List, Union, Tuple

import numpy as np

import bt.conditions as conditions
import items.items as items
import world.worldgenerator as wg
from bt.actions import Action
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint, BlueprintType
from items.inventory import InventorySlot
from mobs import enemies
from mobs.enemies import Enemy
from mobs.entity import Entity


@dataclass
class Experiment:
    id: str
    name: str
    world_generator: wg.WorldGenerator
    goals: List[Union[Blueprint, Action, conditions.Condition, AgentlessCondition]]
    start_positions: List[List[float]]
    start_entities: List[Entity]
    start_inventory: List[Tuple[str, int]]


experiment_pickaxe = Experiment(
    id="dp",
    name="Diamond Pickaxe",
    world_generator=wg.DefaultWorldGenerator(),
    goals=[AgentlessCondition(conditions.HasItemEquipped, [items.DIAMOND_PICKAXE])],
    start_positions=[[131, 72, 17], [117, 72, 13], [120, 72, 24]],
    start_entities=[],
    start_inventory=[]
)

experiment_default_world = Experiment(
    id="dwg",
    name="Fence Grid Default World",
    world_generator=wg.DefaultWorldGenerator(),
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 11], 7)],
    start_positions=[[131, 72, 17], [132, 72, 4], [140, 72, 24], [125, 72, 50], [140, 72, 34]],
    start_entities=[],
    start_inventory=[]
)

experiment_flat_world = Experiment(
    id="fwg",
    name="Fence Grid Flat World",
    world_generator=wg.FlatWorldGenerator(),
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[],
    start_inventory=[]
)


experiment_flat_world_zombie = Experiment(
    id="fwz",
    name="Fence Grid Flat World Zombie",
    world_generator=wg.FlatWorldGenerator(),
    goals=[
        AgentlessCondition(conditions.HasNoEnemyNearby),
        Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)
    ],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[Enemy(enemies.ZOMBIE, 116, 10, 9)],
    start_inventory=[(items.IRON_HELMET, InventorySlot.HELMET_SLOT)]
)

experiment_flat_world_zombie_help = Experiment(
    id="fwzh",
    name="Fence Flat World Zombie Help",
    world_generator=wg.FlatWorldGenerator(),
    goals=[
        AgentlessCondition(conditions.HasNoEnemyNearToAgent),
        Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)
    ],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[Enemy(enemies.ZOMBIE, 116, 10, 9)],
    start_inventory=[(items.IRON_HELMET, InventorySlot.HELMET_SLOT)]
)

experiment_get_30_fence = Experiment(
    id="g30f",
    name="Get 30 Fence Flat World",
    world_generator=wg.FlatWorldGenerator(),
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
    world_generator=wg.DefaultWorldGenerator(),
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
    world_generator=wg.CustomWorldGenerator(
        [
            wg.Cuboid(items.STONE, np.array([[-5, 9, 20], [5, 11, 25]])),
            wg.Cuboid(items.LOG_2, np.array([[-5, 9, -20], [5, 11, -25]])),
        ]
    ),
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.STICKS, 10]),
        AgentlessCondition(conditions.HasItemShared, [items.STONE, 15]),
    ],
    start_positions=[[0, 9, 0], [-5, 9, 0], [5, 9, 0], [10, 9, 0], [-10, 9, 0]],
    start_entities=[],
    start_inventory=[(items.WOODEN_PICKAXE, 0)]
)

configurations = [
    experiment_pickaxe,
    experiment_default_world,
    experiment_flat_world,
    experiment_flat_world_zombie,
    experiment_flat_world_zombie_help,
    experiment_get_30_fence,
    experiment_get_10_stone_pickaxe,
    experiment_get_10_stone_pickaxe_manual
]
