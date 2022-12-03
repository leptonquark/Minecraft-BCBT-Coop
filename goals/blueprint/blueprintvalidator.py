from goals.blueprint.blueprint import Blueprint
from world.observer import Observer


def get_blueprint_validators_from_goals(goals, role):
    blueprint_validators = []
    if role == 0:
        for goal in goals:
            if isinstance(goal, Blueprint):
                blueprint_validators.append(BlueprintValidator(goal))
    return blueprint_validators


class BlueprintValidator:

    def __init__(self, blueprint):
        self.blueprint = blueprint

    def validate(self, observation):
        observer = Observer(observation)
        result = [
            observer.is_block_at_position(position, self.blueprint.material)
            for position
            in self.blueprint.positions
        ]
        return result
