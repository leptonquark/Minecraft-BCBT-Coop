import math

from py_trees.composites import Selector

import bt.actions as actions
from bt.conditions import HasItem, HasItemEquipped
from bt.sequence import Sequence
from items.gathering import get_gathering_tool
from items.recipes import get_recipe, RecipeType
from mobs.animals import get_loot_source


def condition_to_ppa_tree(agent, condition):
    if isinstance(condition, HasItem):
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

    elif isinstance(condition, HasItemEquipped):
        return EquipPPA(agent, condition.item)
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
        self.post_condition = HasItem(agent, item, amount)
        recipe = get_recipe(item)
        craft_amount = amount
        if recipe is not None:
            craft_amount = math.ceil(amount / recipe.output_amount)
            if recipe.station:
                self.pre_conditions.append(HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = craft_amount * ingredient.amount
                self.pre_conditions.append(HasItem(agent, ingredient.item, ingredient_amount))
        self.action = actions.Craft(agent, item, craft_amount)


class MeltPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(MeltPPA, self).__init__()
        self.name = "Melt {1}x {0}".format(item, amount)
        self.post_condition = HasItem(agent, item, amount)
        recipe = get_recipe(item)
        if recipe is not None:
            if recipe.station:
                self.pre_conditions.append(HasItem(agent, recipe.station))
            for ingredient in recipe.ingredients:
                ingredient_amount = math.ceil(amount / recipe.output_amount) * ingredient.amount
                self.pre_conditions.append(HasItem(agent, ingredient.item, ingredient_amount))
        self.action = actions.Melt(agent, item, amount)


class GatherPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(GatherPPA, self).__init__()
        self.name = "Gather {1}x {0}".format(item, amount)
        self.agent = agent
        self.post_condition = HasItem(agent, item, amount)

        tool = get_gathering_tool(item)
        if tool is not None:
            self.pre_conditions.append(HasItemEquipped(agent, tool))
        self.action = self.get_gather_tree(item)

    def get_gather_tree(self, material):
        return Selector(
            "Gather " + str(material),
            children=[
                actions.PickupItem(self.agent, material),
                actions.MineMaterial(self.agent, material),
                actions.GoToMaterial(self.agent, material),
                actions.DigDownwardsToMaterial(self.agent, material)
            ]
        )


class HuntPPA(PPA):

    def __init__(self, agent, item, amount=1):
        super(HuntPPA, self).__init__()

        mob = get_loot_source(item)
        self.name = "Hunt {2} for {1}x {0}".format(item, amount, mob)
        self.agent = agent
        self.post_condition = HasItem(agent, item, amount)

        self.action = self.get_hunting_tree(item, mob)

    def get_hunting_tree(self, item, mob):
        return Selector(
            f"Hunt {mob} for {item}" + str(mob),
            children=[
                actions.PickupItem(self.agent, item),
                actions.AttackAnimal(self.agent, mob),
                actions.GoToAnimal(self.agent, mob)
            ]
        )


class EquipPPA(PPA):
    def __init__(self, agent, item):
        super(EquipPPA, self).__init__()
        self.name = "Equip {0}".format(item)
        self.agent = agent
        self.post_condition = HasItemEquipped(agent, item)
        self.action = actions.Equip(agent, item)
        self.pre_conditions = [HasItem(agent, item)]
