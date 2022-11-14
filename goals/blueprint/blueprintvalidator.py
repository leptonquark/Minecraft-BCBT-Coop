from world.observer import Observer


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
