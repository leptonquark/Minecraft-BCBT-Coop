from bt.actions import Action, JumpIfStuck
from bt.conditions import Condition
from bt.ppa import PPA, condition_to_ppa_tree
from bt.sequence import Sequence

from py_trees.composites import Selector

import bt.actions as actions
from bt.conditions import HasItem, HasItemEquipped
from bt.sequence import Sequence
from items.gathering import get_gathering_tool
from items.recipes import get_recipe, RecipeType
from mobs.animals import get_loot_source


def tree_to_string(tree, depth=0):
    symbol = "[B]"
    if isinstance(tree, Sequence):
        symbol = "[>]"
    elif isinstance(tree, Selector):
        symbol = "[?]"
    elif isinstance(tree, Condition):
        symbol = "(C)"
    elif isinstance(tree, Action):
        symbol = "[A]"
    indent = "    " * (depth-1)
    arrow = "--> " if depth > 0 else ""
    output = f"{indent}{arrow}{symbol} {tree.name} \n"
    for child in tree.children:
        output += tree_to_string(child, depth+1)
    return output
