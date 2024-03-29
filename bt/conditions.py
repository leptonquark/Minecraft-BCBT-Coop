from py_trees.behaviour import Behaviour
from py_trees.common import Status

from items.gathering import get_pickaxe
from utils.constants import ATTACK_REACH, PLACING_REACH
from world.observer import get_position_flat_center


class Condition(Behaviour):
    def __init__(self, name, agent):
        super().__init__(name)
        self.agent = agent

    def update(self):
        return Status.SUCCESS if self.verify() else Status.FAILURE

    def verify(self):
        raise NotImplementedError("Please Implement this method")


class HasItem(Condition):
    def __init__(self, agent, item, amount=1, same_variant=False):
        super().__init__(f"Has Item {amount}x {item}", agent)
        self.item = item
        self.amount = amount
        self.same_variant = same_variant

    def verify(self):
        return self.agent.inventory.has_item(self.item, self.amount, self.same_variant)


class HasItemEquipped(Condition):
    def __init__(self, agent, item):
        super().__init__(f"Has Item Equipped {item}", agent)
        self.item = item

    def verify(self):
        return self.agent.inventory.has_item_equipped(self.item)


class HasPickaxeByMinimumTier(Condition):
    def __init__(self, agent, tier):
        super().__init__(f"Has {get_pickaxe(tier)}", agent)
        self.tier = tier

    def verify(self):
        return self.agent.has_pickaxe_by_minimum_tier(self.tier)


class HasBestPickaxeByMinimumTierEquipped(Condition):
    def __init__(self, agent, tier):
        super().__init__(f"Has {get_pickaxe(tier)} equipped", agent)
        self.tier = tier

    def verify(self):
        return self.agent.has_best_pickaxe_by_minimum_tier_equipped(self.tier)


class HasPickupNearby(Condition):
    def __init__(self, agent, item):
        super().__init__(f"Has Pickup Nearby {item}", agent)
        self.item = item

    def verify(self):
        return self.agent.observer.has_pickup_nearby(self.item)


class HasNoEnemyNearby(Condition):
    def __init__(self, agent):
        super().__init__("Has No Enemy Nearby", agent)

    def verify(self):
        return not self.agent.observer.is_enemy_nearby()


class HasNoEnemyNearToAgent(Condition):
    def __init__(self, agent):
        super().__init__("Has No Enemy Near to Player", agent)

    def verify(self):
        return not self.agent.observer.is_enemy_near_any_agent()


class IsBlockWithinReach(Condition):

    def __init__(self, agent, block_type):
        super().__init__(f"Is Block Within Reach {block_type}", agent)
        self.block_type = block_type

    def verify(self):
        block_center = self.agent.get_closest_block_center(self.block_type)
        return self.agent.is_position_within_reach(block_center)


class IsBlockObservable(Condition):
    def __init__(self, agent, block):
        super().__init__(f"Is Block Observable {block}", agent)
        self.block = block

    def verify(self):
        return self.agent.observer.is_block_observable(self.block)


class IsPositionWithinReach(Condition):

    def __init__(self, agent, position):
        super().__init__(f"Is Position Within Reach {position}", agent)
        self.position = position

    def verify(self):
        position_center = get_position_flat_center(self.position)
        return self.agent.is_position_within_reach(position_center, reach=PLACING_REACH)


class IsAnimalWithinReach(Condition):
    def __init__(self, agent, specie):
        super().__init__(f"Is Animal Within Reach {specie}", agent)
        self.specie = specie

    def verify(self):
        return self.agent.is_entity_within_reach(self.agent.get_weakest_animal(self.specie), ATTACK_REACH)


class IsEnemyWithinReach(Condition):
    def __init__(self, agent):
        super().__init__("Is Enemy Within Reach", agent)

    def verify(self):
        enemy = self.agent.get_closest_enemy(consider_other_agents=False)
        return self.agent.is_entity_within_reach(enemy)


class IsEnemyClosestToAgentsWithinReach(Condition):
    def __init__(self, agent):
        super().__init__("Is Enemy Closest to Agents Within Reach", agent)

    def verify(self):
        enemy = self.agent.get_closest_enemy(consider_other_agents=True)
        return self.agent.is_entity_within_reach(enemy)


class IsAnimalObservable(Condition):
    def __init__(self, agent, specie):
        super().__init__(f"Is Animal Observable {specie}", agent)
        self.specie = specie

    def verify(self):
        return self.agent.observer.is_animal_observable(self.specie)


class IsBlockAtPosition(Condition):
    def __init__(self, agent, block, position):
        super().__init__(f"Is Block {block} at position {position}", agent)
        self.block = block
        self.position = position

    def verify(self):
        return self.agent.observer.is_block_at_position(self.position, self.block)


class HasItemShared(Condition):
    def __init__(self, agent, item, amount=1):
        super().__init__(f"Has Item {amount}x {item}", agent)
        self.item = item
        self.amount = amount

    def verify(self):
        blackboard = self.agent.blackboard.copy()
        amount = sum(n for key, n in blackboard.items() if key.startswith(f"shared_inventory_{self.item}"))
        return amount >= self.amount
