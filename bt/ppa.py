import math

from py_trees.composites import Selector

import bt.actions as actions
import bt.conditions as conditions
from bt.sequence import Sequence
from items.gathering import get_gathering_tool
from items.recipes import get_recipe, RecipeType
from mobs.animals import get_loot_source


def condition_to_ppa_tree(agent, condition):
    if isinstance(condition, conditions.HasItem):
        recipe = get_recipe(condition.item)
        if recipe is None:
            source = get_loot_source(condition.item)
            if source is None:
                return GatherPPA(agent, condition.item, condition.amount)
            else:
                return HuntPPA(agent, condition.item, condition.amount)
        else:
            if recipe.recipe_type == RecipeType.Melting:
                return MeltPPA(agent, condition.item, condition.amount)
            else:
                return CraftPPA(agent, condition.item, condition.amount)
    elif isinstance(condition, conditions.HasItemEquipped):
        return EquipPPA(agent, condition.item)
    elif isinstance(condition, condition.IsBlockObservable):
        return ExplorePPA(agent, condition.block)
    elif isinstance(condition, condition.IsBlockWithinReach):
        return GoToBlockPPA(agent, condition.block)
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
                name="Precondition Handler {}".format(self.name),
                children=self.pre_conditions + [self.action]
            )
        else:
            sub_tree = self.action
        if self.post_condition is not None:
            self.tree = Selector(
                name="Postcondition Handler {}".format(self.name),
                children=[self.post_condition, sub_tree]
            )
        else:
            self.tree = sub_tree

        self.tree.name = "PPA {}".format(self.name)
        self.tree.setup_with_descendants()


class CraftPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(CraftPPA, self).__init__()
        self.name = "Craft {1}x {0}".format(item, amount)
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
        self.name = "Melt {1}x {0}".format(item, amount)
        self.post_condition = conditions.HasItem(agent, item, amount)
        recipe = get_recipe(item)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(conditions.HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = math.ceil(amount / recipe.output_amount) * ingredient.amount
                self.pre_conditions.append(conditions.HasItem(agent, ingredient.item, ingredient_amount))
        self.action = actions.Melt(agent, item, amount)


class GatherPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(GatherPPA, self).__init__()
        self.name = "Gather {1}x {0}".format(item, amount)
        self.agent = agent
        self.post_condition = conditions.HasItem(agent, item, amount)

        tool = get_gathering_tool(item)
        if tool is not None:
            self.pre_conditions.append(conditions.HasItemEquipped(agent, tool))
        self.action = self.get_gather_tree(item, amount)

    def get_gather_tree(self, material, amount):
        return Selector(
            "PPA Pickup" + str(material),
            children=[
                conditions.HasItem(self.agent, material, amount),
                Sequence(
                    "Precondition Handler Pickup " + str(material),
                    children=[
                        Selector(
                            "PPA Mine " + str(material),
                            children=[
                                conditions.HasPickupNearby(self.agent, material),
                                Sequence(
                                    "Precondition Handler Mine " + str(material),
                                    children=[
                                        Selector(
                                            "PPA Go to Block",
                                            children=[
                                                conditions.IsBlockWithinReach(self.agent, material),
                                                Sequence(
                                                    "Precondition Handler Go To Block",
                                                    children=[
                                                        Selector(
                                                            name="PPA Dig downwards",
                                                            children=[
                                                                conditions.IsBlockObservable(self.agent, material),
                                                                actions.DigDownwardsToMaterial(self.agent, material)
                                                            ]
                                                        ),
                                                        actions.GoToBlock(self.agent, material)
                                                    ]
                                                )
                                            ]
                                        ),
                                        actions.MineMaterial(self.agent, material)
                                    ]
                                )
                            ]
                        ),
                        actions.PickupItem(self.agent, material),
                    ]
                )
            ]
        )

class PickupPPA(PPA):
    def __init__(self, agent, material):
        super(PickupPPA, self).__init__()
        self.name = "Pick up {0}".format(material)
        self.post_condition = conditions.HasPickupNearby(agent, material)
        self.pre_conditions = [conditions.IsBlockWithinReach(agent, material)]
        self.action = actions.GoToBlock(agent, material)


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
        self.action = actions.GoToBlock(agent, material)


class HuntPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(HuntPPA, self).__init__()

        mob = get_loot_source(item)
        self.name = "Hunt {2} for {1}x {0}".format(item, amount, mob)
        self.agent = agent
        self.post_condition = conditions.HasItem(agent, item, amount)

        self.action = self.get_hunting_tree(item, mob, amount)

    def get_hunting_tree(self, item, mob, amount):
        return Selector(
            "PPA Pickup" + str(item),
            children=[
                conditions.HasItem(self.agent, item, amount),
                Sequence(
                    "Precondition Handler Pickup " + str(item),
                    children=[
                        Selector(
                            "PPA AttackAnimal " + str(item),
                            children=[
                                conditions.HasPickupNearby(self.agent, item),
                                Sequence(
                                    "Precondition Handler Attack Animal" + str(item),
                                    children=[
                                        Selector(
                                            "PPA Go to Animal",
                                            children=[
                                                conditions.IsAnimalWithinReach(self.agent, mob),
                                                Sequence(
                                                    "Precondition Handler Go To Block",
                                                    children=[
                                                        conditions.IsAnimalObservable(self.agent, mob),
                                                        Selector(
                                                            name="PPA Dig downwards",
                                                            children=[
                                                                actions.RunForwardTowardsAnimal(self.agent, mob)
                                                            ]
                                                        ),
                                                        actions.GoToAnimal(self.agent, mob)
                                                    ]
                                                )
                                            ]
                                        ),
                                        actions.AttackAnimal(self.agent, mob)
                                    ]
                                )
                            ]
                        ),
                        actions.PickupItem(self.agent, item),
                    ]
                )
            ]
        )


class EquipPPA(PPA):
    def __init__(self, agent, item):
        super(EquipPPA, self).__init__()
        self.name = "Equip {0}".format(item)
        self.agent = agent
        self.post_condition = conditions.HasItemEquipped(agent, item)
        self.action = actions.Equip(agent, item)
        self.pre_conditions = [conditions.HasItem(agent, item)]
