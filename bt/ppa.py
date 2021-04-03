from bt.behaviours import Craft, DigDownwardsToMaterial, GoToMaterial, Equip, MineMaterial, PickupItem
from bt.conditions import HasItem, HasItemEquipped
from bt.sequence import Sequence
from items.gathering import get_gathering_tool
from items.recipes import get_ingredients, has_recipe
from py_trees.composites import Selector


def condition_to_ppa_tree(agent, condition):
    if isinstance(condition, HasItem):
        if has_recipe(condition.item):
            ppa = CraftPPA(agent, condition.item, condition.amount)
        else:
            ppa = GatherPPA(agent, condition.item, condition.amount)
        return ppa
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
        ingredients = get_ingredients(item)
        if ingredients is not None:
            for ingredient in ingredients:
                self.pre_conditions.append(HasItem(agent, ingredient.item, ingredient.amount))
        self.action = Craft(agent, item)


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
        tool = get_gathering_tool(material)

        children = []
        children += [
            PickupItem(self.agent, material),
            MineMaterial(self.agent, material),
            GoToMaterial(self.agent, material),
            DigDownwardsToMaterial(self.agent, material)
        ]
        return Selector(
            "Gather " + str(material),
            children=children
        )


class EquipPPA(PPA):
    def __init__(self, agent, item):
        super(EquipPPA, self).__init__()
        self.name = "Equip {0}".format(item)
        self.agent = agent
        self.post_condition = HasItemEquipped(agent, item)
        self.action = Equip(agent, item)
        self.pre_conditions = [HasItem(agent, item)]
