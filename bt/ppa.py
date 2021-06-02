import math

from py_trees.composites import Selector

import bt.actions as actions
import bt.conditions as conditions
from bt.sequence import Sequence
from items.gathering import get_gathering_tool
from items.recipes import get_recipe, RecipeType
from mobs.animals import get_loot_source
from mobs.hunting import get_hunting_tool


# TODO: This should be done in a more dynamic way
def condition_to_ppa_tree(agent, condition):
    if isinstance(condition, conditions.HasItem):
        recipe = get_recipe(condition.item)
        if recipe is None:
            return PickupPPA(agent, condition.item, condition.amount)
        else:
            if recipe.recipe_type == RecipeType.Melting:
                return MeltPPA(agent, condition.item, condition.amount)
            else:
                return CraftPPA(agent, condition.item, condition.amount)
    elif isinstance(condition, conditions.HasItemEquipped):
        return EquipPPA(agent, condition.item)
    elif isinstance(condition, conditions.HasPickupNearby):
        source = get_loot_source(condition.item)
        if source is None:
            return MinePPA(agent, condition.item)
        else:
            return HuntPPA(agent, condition.item)
    elif isinstance(condition, conditions.IsBlockWithinReach):
        return GoToBlockPPA(agent, condition.block)
    elif isinstance(condition, conditions.IsPositionWithinReach):
        return GoToPositionPPA(agent, condition.position)
    elif isinstance(condition, conditions.IsBlockObservable):
        return ExplorePPA(agent, condition.block)
    elif isinstance(condition, conditions.IsAnimalWithinReach):
        return GoToAnimalPPA(agent, condition.specie)
    elif isinstance(condition, conditions.IsAnimalObservable):
        return LookForAnimalPPA(agent, condition.specie)
    elif isinstance(condition, conditions.IsBlockAtPosition):
        return PlaceBlockPPA(agent, condition.block, condition.position)
    return None


class PPA:

    def __init__(self):
        self.name = ""
        self.post_condition = None
        self.pre_conditions = []
        self.action = None
        self.tree = None

    def create_ppa(self):
        if self.action is None:
            return

        if len(self.pre_conditions) > 0:
            sub_tree = Sequence(
                name=f"Precondition Handler {self.name}",
                children=self.pre_conditions + [self.action]
            )
        else:
            sub_tree = self.action
        if self.post_condition is not None:
            self.tree = Selector(
                name=f"Postcondition Handler {self.name}",
                children=[self.post_condition, sub_tree]
            )
        else:
            self.tree = sub_tree

        self.tree.name = f"PPA {self.name}"
        self.tree.setup_with_descendants()


class CraftPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(CraftPPA, self).__init__()
        self.name = f"Craft {amount}x {item}"
        self.post_condition = conditions.HasItem(agent, item, amount)
        recipe = get_recipe(item)
        craft_amount = amount
        if recipe is not None:
            craft_amount = math.ceil(amount / recipe.output_amount)
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = craft_amount * ingredient.amount
                self.pre_conditions.append(conditions.HasItem(agent, ingredient.item, ingredient_amount))
        self.action = actions.Craft(agent, item, craft_amount)


class MeltPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(MeltPPA, self).__init__()
        self.name = f"Melt {amount}x {item}"
        self.post_condition = conditions.HasItem(agent, item, amount)
        recipe = get_recipe(item)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = math.ceil(amount / recipe.output_amount) * ingredient.amount
                self.pre_conditions.append(conditions.HasItem(agent, ingredient.item, ingredient_amount))
        self.action = actions.Melt(agent, item, amount)


class PickupPPA(PPA):
    def __init__(self, agent, material, amount):
        super(PickupPPA, self).__init__()
        self.name = "Pick up {0}".format(material)
        self.post_condition = conditions.HasItem(agent, material, amount)
        self.pre_conditions = [conditions.HasPickupNearby(agent, material)]
        self.action = actions.PickupItem(agent, material)


class ExplorePPA(PPA):
    def __init__(self, agent, material):
        super(ExplorePPA, self).__init__()
        self.name = "Look for {0}".format(material)
        self.post_condition = conditions.IsBlockObservable(agent, material)
        self.action = actions.DigDownwardsToMaterial(agent, material)


class GoToBlockPPA(PPA):
    def __init__(self, agent, material):
        super(GoToBlockPPA, self).__init__()
        self.name = "Go to {0}".format(material)
        self.post_condition = conditions.IsBlockWithinReach(agent, material)
        self.pre_conditions = [conditions.IsBlockObservable(agent, material)]
        self.action = actions.GoToBlock(agent, material)


class MinePPA(PPA):
    def __init__(self, agent, material):
        super(MinePPA, self).__init__()
        self.name = "Mine {0}".format(material)
        self.post_condition = conditions.HasPickupNearby(agent, material)
        self.pre_conditions = [conditions.IsBlockWithinReach(agent, material)]
        tool = get_gathering_tool(material)
        if tool is not None:
            self.pre_conditions.insert(0, conditions.HasItemEquipped(agent, tool))
        self.action = actions.MineMaterial(agent, material)


class HuntPPA(PPA):
    def __init__(self, agent, item):
        super(HuntPPA, self).__init__()
        mob = get_loot_source(item)
        self.name = f"Hunt {item} for {mob}"
        self.post_condition = conditions.HasPickupNearby(agent, item)
        self.pre_conditions = [conditions.IsAnimalWithinReach(agent, mob)]
        tool = get_hunting_tool(mob)
        if tool is not None:
            self.pre_conditions.insert(0, conditions.HasItemEquipped(agent, tool))
        self.action = actions.AttackAnimal(agent, mob)


class GoToAnimalPPA(PPA):
    def __init__(self, agent, animal):
        super(GoToAnimalPPA, self).__init__()
        self.name = f"Go to {animal}"
        self.post_condition = conditions.IsAnimalWithinReach(agent, animal)
        self.pre_conditions = [conditions.IsAnimalObservable(agent, animal)]
        self.action = actions.GoToAnimal(agent, animal)


class LookForAnimalPPA(PPA):
    def __init__(self, agent, animal):
        super(LookForAnimalPPA, self).__init__()
        self.name = f"Look for {animal}"
        self.post_condition = conditions.IsAnimalObservable(agent, animal)
        self.action = actions.RunForwardTowardsAnimal(agent, animal)


class EquipPPA(PPA):
    def __init__(self, agent, item):
        super(EquipPPA, self).__init__()
        self.name = "Equip {0}".format(item)
        self.agent = agent
        self.post_condition = conditions.HasItemEquipped(agent, item)
        self.action = actions.Equip(agent, item)
        self.pre_conditions = [conditions.HasItem(agent, item)]


class PlaceBlockPPA(PPA):
    def __init__(self, agent, block, position):
        super(PlaceBlockPPA, self).__init__()
        self.name = f"Place Block {block} at position {position}"
        self.agent = agent
        self.post_condition = conditions.IsBlockAtPosition(agent, block, position)
        self.pre_conditions = [
            conditions.HasItemEquipped(agent, block),
            conditions.IsPositionWithinReach(agent, position)
        ]
        self.action = actions.PlaceBlockAtPosition(agent, block, position)


class GoToPositionPPA(PPA):
    def __init__(self, agent, position):
        super(GoToPositionPPA, self).__init__()
        self.name = f"Go to position {position}"
        self.agent = agent
        self.post_condition = conditions.IsPositionWithinReach(agent, position)
        self.action = actions.GoToPosition(agent, position)
