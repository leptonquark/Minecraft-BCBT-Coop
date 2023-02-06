import math
from typing import List, Union

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


def backward_chain(agent, condition, collaboration) -> Union[Selector, conditions.Condition]:
    ppa = condition_to_ppa_tree(condition)
    if ppa is not None:
        new_pre_conditions = [backward_chain(agent, pc, collaboration) for pc in ppa.pre_conditions]
        ppa.pre_conditions = new_pre_conditions
        tree = ppa.as_tree(collaboration)
        return tree
    else:
        return condition


class PPA:
    name: str
    post_condition: conditions.Condition
    pre_conditions: List[Behaviour]
    actions: List[actions.Action]
    shareable: bool

    def __init__(self, condition, shareable=False):
        self.shareable = shareable
        self.agent = condition.agent
        self.name = condition.name
        self.post_condition = condition
        self.pre_conditions = []
        self.actions = []

    def as_tree(self, collaboration=False):
        collaborative = collaboration and self.shareable
        tree = self.get_pre_condition_sequence(collaborative)
        tree = self.get_post_condition_fallback(tree, collaborative)
        tree.name = f"PPA {self.name}"
        return tree

    def get_pre_condition_sequence(self, collaborative):
        if collaborative:
            sender = Sender(self.agent.blackboard, self.name, self.agent.name)
            outer_sequence_children = [sender] + self.pre_conditions + self.actions
        else:
            outer_sequence_children = self.pre_conditions + self.actions
        tree = Sequence(name=f"Precondition Handler {self.name}", children=outer_sequence_children)
        return tree

    def get_post_condition_fallback(self, tree, collaborative):
        if collaborative:
            receiver = InverseReceiver(self.agent.blackboard, self.name, [False, self.agent.name])
            post_condition_seq_children = [self.post_condition, StopSender(self.agent.blackboard, self.name)]
            post_condition_sequence = Sequence(children=post_condition_seq_children)
            selector_children = [post_condition_sequence, receiver, tree]
        else:
            selector_children = [self.post_condition, tree]
        tree = Selector(name=f"Postcondition Handler {self.name}", children=selector_children)
        return tree


def get_has_ingredient(agent, amount, ingredient):
    return conditions.HasItem(agent, ingredient.item, amount * ingredient.amount, ingredient.same_variant)


class HasItemPPA(PPA):

    def __init__(self, condition):
        super().__init__(condition, False)
        recipe = get_recipe(condition.item)
        if recipe is not None:
            craft_amount = math.ceil(condition.amount / recipe.output_amount)
            self.pre_conditions = [conditions.HasItem(self.agent, recipe.station)] if recipe.station else []
            self.pre_conditions += [get_has_ingredient(self.agent, craft_amount, i) for i in recipe.ingredients]
            if recipe.recipe_type == RecipeType.Melting:
                self.name = f"Melt {condition.amount}x {condition.item}"
                self.actions = [actions.Melt(self.agent, condition.item, craft_amount)]
            else:
                self.name = f"Craft {condition.amount}x {condition.item}"
                self.actions = [actions.Craft(self.agent, condition.item, craft_amount)]
        else:
            self.name = f"Pick up {condition.item}"
            self.pre_conditions = [conditions.HasPickupNearby(self.agent, condition.item)]
            self.actions = [actions.PickupItem(self.agent, condition.item)]


class HasPickupNearbyPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        source = get_loot_source(condition.item)
        if source is None:
            self.name = f"Mine {condition.item}"
            tier = get_gathering_tier_by_material(condition.item)
            self.pre_conditions = [] if tier is None else [
                conditions.HasBestPickaxeByMinimumTierEquipped(self.agent, tier)]
            self.pre_conditions.append(conditions.IsBlockWithinReach(self.agent, condition.item))
            self.actions = [actions.MineMaterial(self.agent, condition.item)]
        else:
            self.name = f"Hunt {source} for {condition.item}"
            tool = get_hunting_tool(source)
            self.pre_conditions = [conditions.HasItemEquipped(self.agent, tool)] if tool is not None else []
            self.pre_conditions.append(conditions.IsAnimalWithinReach(self.agent, source))
            self.actions = [actions.AttackAnimal(self.agent, source)]


class HasItemEquippedPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.Equip(self.agent, condition.item)]
        self.pre_conditions = [conditions.HasItem(self.agent, condition.item)]


class IsBlockWithinReachPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.GoToBlock(self.agent, condition.block_type)]


class IsPositionWithinReachPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.GoToPosition(self.agent, condition.position)]


class IsBlockObservablePPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        if condition.block == items.items.DIAMOND:
            self.actions = [actions.DigDownwardsToMaterial(self.agent, condition.block)]
        else:
            self.actions = [actions.ExploreInDirection(self.agent, Direction.North)]


class IsAnimalWithinReachPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.pre_conditions = [conditions.IsAnimalObservable(self.agent, condition.specie)]
        self.actions = [actions.GoToAnimal(self.agent, condition.specie)]


class IsEnemyWithinReachPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.GoToEnemy(self.agent)]


class IsEnemyClosestToAgentsWithinReachPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.GoToEnemyClosestToAgents(self.agent)]


class IsAnimalObservablePPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.ExploreInDirection(self.agent, Direction.North)]


class HasNoEnemyNearbyPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.pre_conditions = [conditions.IsEnemyWithinReach(self.agent)]
        self.actions = [actions.DefeatClosestEnemy(self.agent)]


class HasNoEnemyNearToAgentPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.pre_conditions = [conditions.IsEnemyClosestToAgentsWithinReach(self.agent)]
        self.actions = [actions.DefeatEnemyClosestToAgent(self.agent)]


class IsBlockAtPositionPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, True)
        self.pre_conditions = [
            conditions.HasItemEquipped(self.agent, condition.block),
            conditions.IsPositionWithinReach(self.agent, condition.position)
        ]
        self.actions = [actions.PlaceBlockAtPosition(self.agent, condition.block, condition.position)]


class HasBestPickaxeByMinimumTierEquippedPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        self.actions = [actions.EquipBestPickAxe(self.agent, condition.tier)]
        self.pre_conditions = [conditions.HasPickaxeByMinimumTier(self.agent, condition.tier)]


class HasPickaxeByMinimumTierPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, False)
        minimum_pickaxe = get_pickaxe(condition.tier)
        recipe = get_recipe(minimum_pickaxe)
        self.pre_conditions = [conditions.HasItem(self.agent, recipe.station)] if recipe.station else []
        self.pre_conditions += [get_has_ingredient(self.agent, i.amount, i) for i in recipe.ingredients]
        self.actions = [actions.Craft(self.agent, minimum_pickaxe, 1)]


class HasItemSharedPPA(PPA):
    def __init__(self, condition):
        super().__init__(condition, True)
        recipe = get_recipe(condition.item)
        if recipe is not None:
            self.pre_conditions = conditions.HasItem(self.agent, recipe.station) if recipe.station else []
            self.pre_conditions += [get_has_ingredient(self.agent, i.amount, i) for i in recipe.ingredients]
            if recipe.recipe_type == RecipeType.Melting:
                self.actions = [actions.Melt(self.agent, condition.item, condition.amount)]
            else:
                self.actions = [actions.Craft(self.agent, condition.item, condition.amount)]
        else:
            self.pre_conditions = [conditions.HasPickupNearby(self.agent, condition.item)]
            self.actions = [actions.PickupItem(self.agent, condition.item)]

        send_item_action = ItemSender(self.agent, condition.item)
        self.pre_conditions = [send_item_action] + self.pre_conditions


ppas = {
    conditions.HasItem: HasItemPPA,
    conditions.HasPickupNearby: HasPickupNearbyPPA,
    conditions.HasItemEquipped: HasItemEquippedPPA,
    conditions.IsBlockWithinReach: IsBlockWithinReachPPA,
    conditions.IsPositionWithinReach: IsPositionWithinReachPPA,
    conditions.IsBlockObservable: IsBlockObservablePPA,
    conditions.IsAnimalWithinReach: IsAnimalWithinReachPPA,
    conditions.IsEnemyWithinReach: IsEnemyWithinReachPPA,
    conditions.IsEnemyClosestToAgentsWithinReach: IsEnemyClosestToAgentsWithinReachPPA,
    conditions.IsAnimalObservable: IsAnimalObservablePPA,
    conditions.HasNoEnemyNearby: HasNoEnemyNearbyPPA,
    conditions.HasNoEnemyNearToAgent: HasNoEnemyNearToAgentPPA,
    conditions.IsBlockAtPosition: IsBlockAtPositionPPA,
    conditions.HasBestPickaxeByMinimumTierEquipped: HasBestPickaxeByMinimumTierEquippedPPA,
    conditions.HasPickaxeByMinimumTier: HasPickaxeByMinimumTierPPA,
    conditions.HasItemShared: HasItemSharedPPA
}


def condition_to_ppa_tree(condition):
    ppa_class = ppas.get(type(condition))
    if ppa_class is not None:
        return ppa_class(condition)
    else:
        print(f"No PPA found for condition {condition}")
        return None
