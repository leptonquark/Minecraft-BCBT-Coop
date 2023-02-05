import math
from typing import Optional, List, Union

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


def backward_chain(agent, condition, collaborative) -> Union[Selector, conditions.Condition]:
    ppa = condition_to_ppa_tree(agent, condition, collaborative)
    if ppa is not None:
        new_pre_conditions = [backward_chain(agent, pc, collaborative) for pc in ppa.pre_conditions]
        ppa.pre_conditions = new_pre_conditions
        tree = ppa.as_tree()
        return tree
    else:
        return condition


def condition_to_ppa_tree(agent, condition, collaborative=False):
    if isinstance(condition, conditions.HasItem):
        return HasItemPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasPickupNearby):
        return HasPickupNearbyPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasItemEquipped):
        return HasItemEquippedPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsBlockWithinReach):
        return IsBlockWithinReachPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsPositionWithinReach):
        return IsPositionWithinReachPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsBlockObservable):
        return IsBlockObservablePPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsAnimalWithinReach):
        return IsAnimalWithinReachPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsEnemyWithinReach):
        return IsEnemyWithinReachPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsEnemyClosestToAgentsWithinReach):
        return IsEnemyClosestToAgentsWithinReachPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsAnimalObservable):
        return IsAnimalObservablePPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasNoEnemyNearby):
        return HasNoEnemyNearbyPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasNoEnemyNearToAgent):
        return HasNoEnemyNearToAgentPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.IsBlockAtPosition):
        return IsBlockAtPositionPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasBestPickaxeByMinimumTierEquipped):
        return HasBestPickaxeByMinimumTierEquippedPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasPickaxeByMinimumTier):
        return HasPickaxeByMinimumTierPPA(agent, condition, collaborative)
    elif isinstance(condition, conditions.HasItemShared):
        return HasItemSharedPPA(agent, condition, collaborative)
    print(f"No PPA found for condition {condition}")
    return None


class PPA:
    name: str
    post_condition: Optional[conditions.Condition]
    pre_conditions: List[Behaviour]
    actions: List[Behaviour]

    def __init__(self, agent, condition, collaborative=False):
        self.agent = agent
        self.collaborative = collaborative
        self.name = condition.name
        self.post_condition = condition
        self.pre_conditions = []
        self.actions = []

    def as_tree(self):

        tree = self.get_pre_condition_sequence()
        tree = self.get_post_condition_fallback(tree)
        tree.name = f"PPA {self.name}"
        return tree

    def get_pre_condition_sequence(self):
        if self.collaborative:
            sender = Sender(self.agent.blackboard, self.name, self.agent.name)
            outer_sequence_children = [sender] + self.pre_conditions + self.actions
        else:
            outer_sequence_children = self.pre_conditions + self.actions
        tree = Sequence(name=f"Precondition Handler {self.name}", children=outer_sequence_children)
        return tree

    def get_post_condition_fallback(self, tree):
        if self.collaborative:
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

    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        recipe = get_recipe(condition.item)
        if recipe is not None:
            craft_amount = math.ceil(condition.amount / recipe.output_amount)
            self.pre_conditions = [conditions.HasItem(agent, recipe.station)] if recipe.station else []
            self.pre_conditions += [get_has_ingredient(agent, craft_amount, i) for i in recipe.ingredients]
            if recipe.recipe_type == RecipeType.Melting:
                self.name = f"Melt {condition.amount}x {condition.item}"
                self.actions = [actions.Melt(agent, condition.item, craft_amount)]
            else:
                self.name = f"Craft {condition.amount}x {condition.item}"
                self.actions = [actions.Craft(agent, condition.item, craft_amount)]
        else:
            self.name = f"Pick up {condition.item}"
            self.pre_conditions = [conditions.HasPickupNearby(agent, condition.item)]
            self.actions = [actions.PickupItem(agent, condition.item)]


class HasPickupNearbyPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        source = get_loot_source(condition.item)
        if source is None:
            self.name = f"Mine {condition.item}"
            tier = get_gathering_tier_by_material(condition.item)
            self.pre_conditions = [] if tier is None else [conditions.HasBestPickaxeByMinimumTierEquipped(agent, tier)]
            self.pre_conditions.append(conditions.IsBlockWithinReach(agent, condition.item))
            self.actions = [actions.MineMaterial(agent, condition.item)]
        else:
            self.name = f"Hunt {source} for {condition.item}"
            tool = get_hunting_tool(source)
            self.pre_conditions = [conditions.HasItemEquipped(agent, tool)] if tool is not None else []
            self.pre_conditions.append(conditions.IsAnimalWithinReach(agent, source))
            self.actions = [actions.AttackAnimal(agent, source)]


class HasItemEquippedPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.Equip(agent, condition.item)]
        self.pre_conditions = [conditions.HasItem(agent, condition.item)]


class IsBlockWithinReachPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.GoToBlock(agent, condition.block_type)]


class IsPositionWithinReachPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.GoToPosition(agent, condition.position)]


class IsBlockObservablePPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        if condition.block == items.items.DIAMOND:
            self.actions = [actions.DigDownwardsToMaterial(agent, condition.block)]
        else:
            self.actions = [actions.ExploreInDirection(agent, Direction.North)]


class IsAnimalWithinReachPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.pre_conditions = [conditions.IsAnimalObservable(agent, condition.specie)]
        self.actions = [actions.GoToAnimal(agent, condition.specie)]


class IsEnemyWithinReachPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.GoToEnemy(agent)]


class IsEnemyClosestToAgentsWithinReachPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.GoToEnemyClosestToAgents(agent)]


class IsAnimalObservablePPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.ExploreInDirection(agent, Direction.North)]


class HasNoEnemyNearbyPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.pre_conditions = [conditions.IsEnemyWithinReach(agent)]
        self.actions = [actions.DefeatClosestEnemy(agent)]


class HasNoEnemyNearToAgentPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.pre_conditions = [conditions.IsEnemyClosestToAgentsWithinReach(agent)]
        self.actions = [actions.DefeatEnemyClosestToAgent(agent)]


class IsBlockAtPositionPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, collaborative)
        self.pre_conditions = [
            conditions.HasItemEquipped(agent, condition.block),
            conditions.IsPositionWithinReach(agent, condition.position)
        ]
        self.actions = [actions.PlaceBlockAtPosition(agent, condition.block, condition.position)]


class HasBestPickaxeByMinimumTierEquippedPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        self.actions = [actions.EquipBestPickAxe(agent, condition.tier)]
        self.pre_conditions = [conditions.HasPickaxeByMinimumTier(agent, condition.tier)]


class HasPickaxeByMinimumTierPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, False)
        minimum_pickaxe = get_pickaxe(condition.tier)
        recipe = get_recipe(minimum_pickaxe)
        self.pre_conditions = [conditions.HasItem(agent, recipe.station)] if recipe.station else []
        self.pre_conditions += [get_has_ingredient(agent, i.amount, i) for i in recipe.ingredients]
        self.actions = [actions.Craft(agent, minimum_pickaxe, 1)]


class HasItemSharedPPA(PPA):
    def __init__(self, agent, condition, collaborative):
        super().__init__(agent, condition, collaborative)

        recipe = get_recipe(condition.item)
        if recipe is not None:
            self.pre_conditions = conditions.HasItem(condition.agent, recipe.station) if recipe.station else []
            self.pre_conditions += [get_has_ingredient(agent, i.amount, i) for i in recipe.ingredients]
            if recipe.recipe_type == RecipeType.Melting:
                self.actions = [actions.Melt(condition.agent, condition.item, condition.amount)]
            else:
                self.actions = [actions.Craft(condition.agent, condition.item, condition.amount)]
        else:
            self.pre_conditions = [conditions.HasPickupNearby(condition.agent, condition.item)]
            self.actions = [actions.PickupItem(condition.agent, condition.item)]

        send_item_action = ItemSender(self.agent, condition.item)
        self.pre_conditions = [send_item_action] + self.pre_conditions
