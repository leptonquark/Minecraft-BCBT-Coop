from goals.blueprint.blueprint import Blueprint
from world.observer import Observer


def get_blueprint_validators_from_goals(goals, role):
    return [BlueprintValidator(goal) for goal in goals if isinstance(goal, Blueprint)] if role == 0 else []


class BlueprintValidator:

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def validate(self, observation):
        observer = Observer(observation)
        return [observer.is_block_at_position(pos, self.blueprint.material) for pos in self.blueprint.positions]
