import math
from typing import Optional, List

from py_trees.behaviour import Behaviour
from py_trees.composites import Selector

import bt.actions as actions
import bt.conditions as conditions
import items.items
from bt.receiver import InverseReceiver
from bt.sender import StopSender, Sender, ItemSender
from bt.sequence import Sequence
from items.gathering import get_gathering_tier_by_material, get_pickaxe
from items.recipes import get_recipe, RecipeType
from mobs.animals import get_loot_source
from mobs.hunting import get_hunting_tool
from utils.vectors import Direction


def back_chain_recursive(agent, condition, collaborative) -> Optional[Sequence]:
    ppa = condition_to_ppa_tree(agent, condition, collaborative)
    if ppa is not None:
        for i in range(len(ppa.pre_conditions)):
            ppa_condition_tree = back_chain_recursive(agent, ppa.pre_conditions[i], collaborative)
            if ppa_condition_tree is not None:
                ppa.pre_conditions[i] = ppa_condition_tree
        return ppa.as_tree()
    return condition


def condition_to_ppa_tree(agent, condition, collaborative=False):
    if isinstance(condition, conditions.HasItem):
        recipe = get_recipe(condition.item)
        if recipe is None:
            return PickupPPA(agent, condition.item, condition.amount, condition.same_variant)
        else:
            if recipe.recipe_type == RecipeType.Melting:
                return MeltPPA(agent, condition.item, condition.amount, condition.same_variant)
            else:
                return SmartCraftPPA(agent, condition.item, condition.amount, condition.same_variant)
    elif isinstance(condition, conditions.HasPickupNearby):
        source = get_loot_source(condition.item)
        return MinePPA(agent, condition.item) if source is None else HuntPPA(agent, condition.item)
    elif isinstance(condition, conditions.HasItemEquipped):
        return EquipPPA(agent, condition.item)
    elif isinstance(condition, conditions.IsBlockWithinReach):
        return GoToBlockPPA(agent, condition.block_type)
    elif isinstance(condition, conditions.IsPositionWithinReach):
        return GoToPositionPPA(agent, condition.position)
    elif isinstance(condition, conditions.IsBlockObservable):
        if condition.block == items.items.DIAMOND:
            return ExploreDownwardsPPA(agent, condition.block)
        else:
            return LookForBlockPPA(agent, condition.block)
    elif isinstance(condition, conditions.IsAnimalWithinReach):
        return GoToAnimalPPA(agent, condition.specie)
    elif isinstance(condition, conditions.IsEnemyWithinReach):
        return GoToEnemyPPA(agent)
    elif isinstance(condition, conditions.IsAnimalObservable):
        return LookForAnimalPPA(agent, condition.specie)
    elif isinstance(condition, conditions.HasNoEnemyNearby):
        return DefeatEnemyPPA(agent)
    elif isinstance(condition, conditions.IsBlockAtPosition):
        if collaborative:
            return PlaceBlockPPACollaborative(agent, condition.block, condition.position)
        else:
            return PlaceBlockPPA(agent, condition.block, condition.position)
    elif isinstance(condition, conditions.HasBestPickaxeByMinimumTierEquipped):
        return EquipPickaxePPA(agent, condition.tier)
    elif isinstance(condition, conditions.HasPickaxeByMinimumTier):
        return CraftPickaxePPA(agent, condition.tier)
    elif isinstance(condition, conditions.HasItemShared):
        if collaborative:
            return HasItemSharedPPACollaborative(agent, condition.item, condition.amount)
        else:
            return HasItemSharedPPA(agent, condition.item, condition.amount)
    return None


class PPA:
    name: str
    post_condition: Optional[conditions.Condition]
    pre_conditions: List[Behaviour]
    actions: List[Behaviour]

    def __init__(self):
        self.name = ""
        self.post_condition = None
        self.pre_conditions = []
        self.actions = []

    def as_tree(self):
        if len(self.actions) == 0:
            return None

        if len(self.pre_conditions) == 0 and len(self.actions) == 1:
            tree = self.actions[0]
        else:
            tree = Sequence(name=f"Precondition Handler {self.name}", children=self.pre_conditions + self.actions)
        if self.post_condition is not None:
            tree = Selector(name=f"Postcondition Handler {self.name}", children=[self.post_condition, tree])
        tree.name = f"PPA {self.name}"
        return tree


class SimpleCraftPPA(PPA):

    def __init__(self, agent, item, amount=1, same_variant=False):
        super().__init__()
        self.name = f"Craft {amount}x {item}"
        self.post_condition = conditions.HasItem(agent, item, amount, same_variant)
        recipe = get_recipe(item)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                has_item = conditions.HasItem(agent, ingredient.item, ingredient.amount, ingredient.same_variant)
                self.pre_conditions.append(has_item)
        self.actions = [actions.Craft(agent, item, 1)]


class SmartCraftPPA(PPA):

    def __init__(self, agent, item, amount=1, same_variant=False):
        super().__init__()
        self.name = f"Craft {amount}x {item}"
        self.post_condition = conditions.HasItem(agent, item, amount, same_variant)
        recipe = get_recipe(item)
        craft_amount = amount
        if recipe is not None:
            craft_amount = math.ceil(amount / recipe.output_amount)
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = craft_amount * ingredient.amount
                has_item = conditions.HasItem(agent, ingredient.item, ingredient_amount, ingredient.same_variant)
                self.pre_conditions.append(has_item)
        self.actions = [actions.Craft(agent, item, craft_amount)]


class MeltPPA(PPA):

    def __init__(self, agent, item, amount=1, same_variant=False):
        super().__init__()
        self.name = f"Melt {amount}x {item}"
        self.post_condition = conditions.HasItem(agent, item, amount, same_variant)
        recipe = get_recipe(item)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = math.ceil(amount / recipe.output_amount) * ingredient.amount
                has_item = conditions.HasItem(agent, ingredient.item, ingredient_amount, ingredient.same_variant)
                self.pre_conditions.append(has_item)
        self.actions = [actions.Melt(agent, item, amount)]


class PickupPPA(PPA):
    def __init__(self, agent, material, amount, same_variant=False):
        super().__init__()
        self.name = f"Pick up {material}"
        self.post_condition = conditions.HasItem(agent, material, amount, same_variant)
        self.pre_conditions = [conditions.HasPickupNearby(agent, material)]
        self.actions = [actions.PickupItem(agent, material)]


class CraftPickaxePPA(PPA):
    def __init__(self, agent, tier):
        super().__init__()
        self.name = f"Craft pickaxe for gathering {tier.name}"
        self.post_condition = conditions.HasPickaxeByMinimumTier(agent, tier)
        minimum_pickaxe = get_pickaxe(tier)
        recipe = get_recipe(minimum_pickaxe)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                self.pre_conditions.append(conditions.HasItem(agent, ingredient.item, ingredient.amount))
        self.actions = [actions.Craft(agent, minimum_pickaxe, 1)]


class ExploreDownwardsPPA(PPA):
    def __init__(self, agent, material):
        super().__init__()
        self.name = f"Look for {material}"
        self.post_condition = conditions.IsBlockObservable(agent, material)
        self.actions = [actions.DigDownwardsToMaterial(agent, material)]


class LookForBlockPPA(PPA):
    def __init__(self, agent, material):
        super().__init__()
        self.name = f"Look for {material}"
        self.post_condition = conditions.IsBlockObservable(agent, material)
        self.actions = [actions.ExploreInDirection(agent, Direction.North)]


class GoToBlockPPA(PPA):
    def __init__(self, agent, material):
        super().__init__()
        self.name = f"Go to {material}"
        self.post_condition = conditions.IsBlockWithinReach(agent, material)
        self.pre_conditions = [conditions.IsBlockObservable(agent, material)]
        self.actions = [actions.GoToBlock(agent, material)]


class MinePPA(PPA):
    def __init__(self, agent, material):
        super().__init__()
        self.name = f"Mine {material}"
        self.post_condition = conditions.HasPickupNearby(agent, material)
        self.pre_conditions = [conditions.IsBlockWithinReach(agent, material)]

        tier = get_gathering_tier_by_material(material)
        if tier is not None:
            self.pre_conditions.insert(0, conditions.HasBestPickaxeByMinimumTierEquipped(agent, tier))
        self.actions = [actions.MineMaterial(agent, material)]


class HuntPPA(PPA):
    def __init__(self, agent, item):
        super().__init__()
        mob = get_loot_source(item)
        self.name = f"Hunt {item} for {mob}"
        self.post_condition = conditions.HasPickupNearby(agent, item)
        self.pre_conditions = [conditions.IsAnimalWithinReach(agent, mob)]
        tool = get_hunting_tool(mob)
        if tool is not None:
            self.pre_conditions.insert(0, conditions.HasItemEquipped(agent, tool))
        self.actions = [actions.AttackAnimal(agent, mob)]


class GoToAnimalPPA(PPA):
    def __init__(self, agent, animal):
        super().__init__()
        self.name = f"Go to {animal}"
        self.post_condition = conditions.IsAnimalWithinReach(agent, animal)
        self.pre_conditions = [conditions.IsAnimalObservable(agent, animal)]
        self.actions = [actions.GoToAnimal(agent, animal)]


class LookForAnimalPPA(PPA):
    def __init__(self, agent, animal):
        super().__init__()
        self.name = f"Look for {animal}"
        self.post_condition = conditions.IsAnimalObservable(agent, animal)
        self.actions = [actions.ExploreInDirection(agent, Direction.North)]


class EquipPPA(PPA):
    def __init__(self, agent, item):
        super().__init__()
        self.name = f"Equip {item}"
        self.agent = agent
        self.post_condition = conditions.HasItemEquipped(agent, item)
        self.actions = [actions.Equip(agent, item)]
        self.pre_conditions = [conditions.HasItem(agent, item)]


class EquipPickaxePPA(PPA):
    def __init__(self, agent, tier):
        super().__init__()
        self.name = f"Equip Pickaxe of tier {tier}"
        self.agent = agent
        self.post_condition = conditions.HasBestPickaxeByMinimumTierEquipped(agent, tier)
        self.actions = [actions.EquipBestPickAxe(agent, tier)]
        self.pre_conditions = [conditions.HasPickaxeByMinimumTier(agent, tier)]


class PlaceBlockPPA(PPA):
    def __init__(self, agent, block, position):
        super().__init__()
        self.name = f"Place Block {block} at position {position}"
        self.agent = agent
        self.post_condition = conditions.IsBlockAtPosition(agent, block, position)
        self.pre_conditions = [
            conditions.HasItemEquipped(agent, block),
            conditions.IsPositionWithinReach(agent, position)
        ]
        self.actions = [actions.PlaceBlockAtPosition(agent, block, position)]


class PlaceBlockPPACollaborative(PPA):
    def __init__(self, agent, block, position):
        super().__init__()
        self.name = f"Place Block {block} at position {position}"
        self.channel = f"Place {block} at {position}"
        self.agent = agent
        self.post_condition = conditions.IsBlockAtPosition(agent, block, position)
        self.pre_conditions = [
            Sender(agent.blackboard, self.channel, self.agent.name),
            conditions.HasItemEquipped(agent, block),
            conditions.IsPositionWithinReach(agent, position),

        ]
        self.actions = [actions.PlaceBlockAtPosition(agent, block, position), ]

    def as_tree(self):
        if len(self.actions) == 0:
            return None

        receiver = InverseReceiver(self.agent.blackboard, self.channel, [False, self.agent.name])

        tree = Sequence(name=f"Precondition Handler {self.name}", children=self.pre_conditions + self.actions)
        if self.post_condition is not None:
            tree = Selector(name=f"Postcondition Handler {self.name}", children=[
                Sequence(children=[self.post_condition, StopSender(self.agent.blackboard, self.channel)]),
                receiver,
                tree])
        tree.name = f"PPA {self.name}"
        return tree


class GoToPositionPPA(PPA):
    def __init__(self, agent, position):
        super().__init__()
        self.name = f"Go to position {position}"
        self.agent = agent
        self.post_condition = conditions.IsPositionWithinReach(agent, position)
        self.actions = [actions.GoToPosition(agent, position)]


class DefeatEnemyPPA(PPA):
    def __init__(self, agent):
        super().__init__()
        self.name = f"Defeat enemy"
        self.post_condition = conditions.HasNoEnemyNearby(agent)
        self.pre_conditions = [conditions.IsEnemyWithinReach(agent)]
        self.actions = [actions.DefeatClosestEnemy(agent)]


class GoToEnemyPPA(PPA):
    def __init__(self, agent):
        super().__init__()
        self.name = f"Go to enemy"
        self.post_condition = conditions.IsEnemyWithinReach(agent)
        self.actions = [actions.GoToEnemy(agent)]


def get_base_ppa(agent, item, amount):
    recipe = get_recipe(item)
    if recipe is None:
        return PickupPPA(agent, item, amount)
    elif recipe.recipe_type == RecipeType.Melting:
        return MeltPPA(agent, item, amount)
    else:
        return SimpleCraftPPA(agent, item, amount)


class HasItemSharedPPA(PPA):
    def __init__(self, agent, item, amount):
        super().__init__()
        self.name = f"Has {item}"
        self.agent = agent
        self.item = item
        self.amount = amount
        self.post_condition = conditions.HasItemShared(agent, item, amount)
        base_ppa = get_base_ppa(agent, item, amount)
        self.actions = base_ppa.actions
        self.pre_conditions = base_ppa.pre_conditions

    def as_tree(self):
        if len(self.actions) == 0:
            return None

        send_item_action = ItemSender(self.agent, self.item)

        tree = Sequence(name=f"Precondition Handler {self.name}", children=self.pre_conditions + self.actions)
        if self.post_condition is not None:
            tree = Selector(name=f"Postcondition Handler {self.name}", children=[
                self.post_condition, send_item_action, tree])
        tree.name = f"PPA {self.name}"
        return tree


class HasItemSharedPPACollaborative(PPA):
    def __init__(self, agent, item, amount):
        super().__init__()
        self.name = f"Has {item}"
        self.agent = agent
        self.channel = f"Has {item}"
        self.item = item
        self.amount = amount
        self.post_condition = conditions.HasItemShared(agent, item, amount)
        base_ppa = get_base_ppa(agent, item, amount)
        sender = Sender(agent.blackboard, self.channel, self.agent.name)
        self.pre_conditions = [sender] + base_ppa.pre_conditions
        self.actions = base_ppa.actions + [StopSender(agent.blackboard, self.channel)]

    def as_tree(self):
        if len(self.actions) == 0:
            return None

        send_item_action = ItemSender(self.agent, self.item)
        receiver = InverseReceiver(self.agent.blackboard, self.channel, [False, self.agent.name])

        tree = Sequence(name=f"Precondition Handler {self.name}", children=self.pre_conditions + self.actions)
        if self.post_condition is not None:
            tree = Selector(name=f"Postcondition Handler {self.name}", children=[
                Sequence(children=[self.post_condition, StopSender(self.agent.blackboard, self.channel)]),
                send_item_action,
                receiver,
                tree])
        tree.name = f"PPA {self.name}"
        return tree
