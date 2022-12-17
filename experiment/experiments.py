from dataclasses import dataclass
from typing import List, Union

import bt.conditions as conditions
import items.items as items
from bt.actions import Action
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint, BlueprintType
from mobs import enemies
from mobs.enemies import Enemy
from mobs.entity import Entity


@dataclass
class Experiment:
    id: str
    name: str
    flat_world: bool
    goals: List[Union[Blueprint, Action, conditions.Condition, AgentlessCondition]]
    start_positions: List[List[float]]
    start_entities: List[Entity]
    start_inventory: List[str]


experiment_pickaxe = Experiment(
    id="dp",
    name="Diamond Pickaxe",
    flat_world=False,
    goals=[AgentlessCondition(conditions.HasItemEquipped, [items.DIAMOND_PICKAXE])],
    start_positions=[[131, 72, 17], [117, 72, 13], [120, 72, 24]],
    start_entities=[],
    start_inventory=[]
)

experiment_default_world = Experiment(
    id="dwg",
    name="Fence Grid Default World",
    flat_world=False,
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 11], 7)],
    start_positions=[[131, 72, 17], [132, 72, 4], [140, 72, 24], [125, 72, 50], [140, 72, 34]],
    start_entities=[],
    start_inventory=[]
)

experiment_flat_world = Experiment(
    id="fwg",
    name="Fence Grid Flat World",
    flat_world=True,
    goals=[Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25)],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[],
    start_inventory=[]
)

experiment_flat_world_zombie = Experiment(
    id="fwz",
    name="Fence Grid Flat World Zombie",
    flat_world=True,
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
    flat_world=True,
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.FENCE, 30])
    ],
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]],
    start_entities=[],
    start_inventory=[]
)

experiment_get_10_stone_pickaxe = Experiment(
    id="g10sp",
    name="Get 10 Stone Pick Axe",
    flat_world=False,
    goals=[
        AgentlessCondition(conditions.HasItemShared, [items.STICKS, 20]),
        AgentlessCondition(conditions.HasItemShared, [items.COBBLESTONE, 30]),
    ],
    start_positions=[[131, 72, 17], [132, 72, 4], [140, 72, 24], [125, 72, 50], [140, 72, 34]],
    start_entities=[],
    start_inventory=[]
)

configurations = [
    experiment_pickaxe,
    experiment_default_world,
    experiment_flat_world,
    experiment_flat_world_zombie,
    experiment_get_30_fence,
    experiment_get_10_stone_pickaxe
]
