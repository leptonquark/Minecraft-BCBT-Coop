from dataclasses import dataclass
from typing import List, Union

import bt.conditions as conditions
import items.items as items
from bt.actions import Action
from goals.agentlesscondition import AgentlessCondition
from goals.blueprint.blueprint import Blueprint, BlueprintType


@dataclass
class ExperimentConfiguration:
    flat_world: bool
    goals: Union[Blueprint, List[Union[Action, conditions.Condition, AgentlessCondition]]]
    start_positions: List[List[float]]


config_pickaxe = ExperimentConfiguration(
    flat_world=False,
    goals=[AgentlessCondition(conditions.HasItemEquipped, [items.OBSIDIAN])],
    start_positions=[[131, 72, 17], [117, 72, 13], [120, 72, 24]]
)

config_default_world_generator = ExperimentConfiguration(
    flat_world=False,
    goals=Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 71, 9], 5),
    start_positions=[[131, 72, 17], [117, 72, 13], [120, 72, 24], [125, 72, 50], [140, 72, 34]]
)

config_flat_world_generator = ExperimentConfiguration(
    flat_world=True,
    goals=Blueprint.get_blueprint(BlueprintType.PointGrid, [132, 9, 9], 25),
    start_positions=[[101, 10, 9], [132, 10, -21], [162, 10, 9]]
)
